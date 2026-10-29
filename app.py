#!/usr/bin/env python3
"""Local whisper.cpp workbench. Python 3.10+, no Python dependencies."""
import json, os, re, secrets, shutil, signal, subprocess, sys, threading, time, uuid, webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('WHISPER_UI_DATA', str(Path.home()/'.whisper-local'))).expanduser()
DATA.mkdir(parents=True, exist_ok=True)
TOKEN = secrets.token_urlsafe(32)
JOBS = {}; UPLOADS = {}; LOCK = threading.Lock()
BLOCKED = {'--help','--version','--model','--file','--output-file','--language','--translate','--print-colors','--print-progress','--no-prints','--no-timestamps','--detect-language','--output-wts','--font-path','--debug-mode'}
FORMAT = {x:'--output-'+x for x in ['txt','srt','vtt','json','csv','lrc']}

def config():
    try: return json.loads((DATA/'config.json').read_text())
    except (OSError, ValueError):
        binary = shutil.which('whisper-cli') or ''
        for p in [Path.home()/'whisper.cpp/build/bin/whisper-cli',Path('/opt/homebrew/bin/whisper-cli')]:
            if p.is_file(): binary=str(p); break
        models=list((Path.home()/'whisper.cpp/models').glob('ggml-*.bin'))
        return dict(binary=binary,model=str(models[0]) if models else '',output=str(Path.home()/'Documents/Whisper lokaal'))

def capabilities(c):
    binary=str(Path(c.get('binary','')).expanduser())
    if not Path(binary).is_file() or not os.access(binary,os.X_OK): raise ValueError('Kies het uitvoerbare whisper-cli bestand in Installatie.')
    result=subprocess.run([binary,'--help'],capture_output=True,text=True,timeout=10)
    helptext=result.stdout+result.stderr
    if '--model' not in helptext or '--output-srt' not in helptext: raise ValueError('Dit lijkt geen whisper.cpp CLI. Controleer het pad.')
    options=[]
    for line in helptext.splitlines():
        m=re.search(r'(--[\w-]+)([^\[]*)\[([^\]]*)\]\s*(.*)',line)
        if m:
            name,arg,default,description=m.groups()
            if name not in BLOCKED and name not in FORMAT.values(): options.append(dict(name=name,value=bool(arg.strip()),default=default.strip(),description=description))
    return binary,options,helptext

def public(job):
    return {k:v for k,v in job.items() if k not in ('process',)}

def persist(job):
    (Path(job['directory'])/'job.json').write_text(json.dumps(public(job),ensure_ascii=False))

def emit(job,stream,text):
    with LOCK:
        job['events'].append(dict(stream=stream,text=text))
        if len(job['events'])>50000: job['events']=job['events'][-50000:]
        m=re.search(r'progress\s*=\s*(\d+)%',text)
        if m: job['progress']=int(m[1])

def run(job,c,opts,formats,language,translate,colors):
    try:
        binary,supported,_=capabilities(c)
        model=Path(c['model']).expanduser().resolve()
        if not model.is_file(): raise ValueError('Model niet gevonden. Controleer het modelpad in Installatie.')
        job['status']='converting'; persist(job)
        ffmpeg=shutil.which('ffmpeg')
        if not ffmpeg: raise ValueError('FFmpeg ontbreekt. Installeer op de Mac met: brew install ffmpeg')
        converted=Path(job['directory'])/'audio.wav'
        command=[ffmpeg,'-nostdin','-y','-i',job['input'],'-ar','16000','-c:a','pcm_s16le',str(converted)]
        # Stereo retained for --diarize; otherwise mono is faster.
        command[-1:-1]=['-ac','2' if opts.get('--diarize') else '1']
        execute(job,command,conversion=True)
        if job.get('cancelled'): return
        args=[binary,'--model',str(model),'--file',str(converted),'--output-file',str(Path(job['directory'])/'transcript'),'--language',language,'--print-progress']
        if translate: args.append('--translate')
        if colors: args.append('--print-colors')
        args += [FORMAT[f] for f in formats]
        allowed={o['name']:o for o in supported}
        for key,value in opts.items():
            if key not in allowed: raise ValueError('Optie niet ondersteund: '+key)
            if allowed[key]['value']:
                if str(value).strip(): args += [key,str(value)]
            elif value is True: args.append(key)
        import shlex
        job['command']=shlex.join(args); job['status']='running';persist(job)
        execute(job,args)
        if not job.get('cancelled'): job['status']='done';job['progress']=100
    except Exception as e:
        if not job.get('cancelled'): job['status']='error';job['error']=str(e)
    finally:
        if job.get('cancelled'): job['status']='cancelled'
        job.pop('process',None)
        job['files']=[p.name for p in Path(job['directory']).glob('transcript.*') if p.is_file()]
        persist(job)

def execute(job,args,conversion=False):
    with LOCK:
        if job.get('cancelled'): return
        proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        job['process']=proc
    def read(pipe,kind):
        import codecs
        decoder=codecs.getincrementaldecoder('utf-8')('replace')
        while True:
            chunk=os.read(pipe.fileno(),4096)
            if not chunk: break
            emit(job,kind,decoder.decode(chunk))
        tail=decoder.decode(b'',final=True)
        if tail: emit(job,kind,tail)
    threads=[threading.Thread(target=read,args=(proc.stdout,'log' if conversion else 'text')),threading.Thread(target=read,args=(proc.stderr,'log'))]
    for t in threads:t.start()
    code=proc.wait()
    for t in threads:t.join()
    if code and not job.get('cancelled'): raise ValueError(('FFmpeg' if conversion else 'Whisper')+f' stopte met code {code}. Bekijk het verwerkingslog.')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def reply(self,value,status=200):
        data=json.dumps(value,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def validhost(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def do_GET(self):
        if not self.validhost():return self.reply({'error':'Ongeldige host'},403)
        path=unquote(urlparse(self.path).path)
        if path=='/api/state':
            c=config();err='';options=[]
            try: _,options,_=capabilities(c)
            except Exception as e:err=str(e)
            return self.reply(dict(config=c,options=options,error=err,ffmpeg=bool(shutil.which('ffmpeg')),token=TOKEN,jobs=[{k:v for k,v in public(j).items() if k!='events'} for j in JOBS.values()]))
        if path.startswith('/api/job/'):
            j=JOBS.get(path.split('/')[-1]);return self.reply(public(j) if j else {'error':'Taak niet gevonden'},200 if j else 404)
        if path.startswith('/download/'):
            parts=path.split('/')
            if len(parts)!=4:return self.reply({'error':'Niet gevonden'},404)
            j=JOBS.get(parts[2]);name=parts[3]
            if not j or name not in j.get('files',[]):return self.reply({'error':'Niet gevonden'},404)
            return self.file(Path(j['directory'])/name,'application/octet-stream',True)
        names={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if path not in names:return self.reply({'error':'Niet gevonden'},404)
        return self.file(ROOT/'web'/names[path],{'/':'text/html; charset=utf-8','/app.js':'text/javascript','/style.css':'text/css'}[path])
    def file(self,path,mime,attachment=False):
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(path.stat().st_size));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store')
        if attachment:self.send_header('Content-Disposition',f'attachment; filename="{path.name}"')
        self.end_headers()
        with path.open('rb') as f:shutil.copyfileobj(f,self.wfile)
    def do_POST(self):
        if not self.validhost() or self.headers.get('X-Whisper-Token')!=TOKEN:return self.reply({'error':'Herlaad de pagina en probeer opnieuw.'},403)
        try:
            path=urlparse(self.path).path;size=int(self.headers.get('Content-Length','0'))
            if path=='/api/upload':
                if size<=0 or size>8*1024**3:raise ValueError('Kies een bestand van maximaal 8 GB.')
                ident=uuid.uuid4().hex;folder=DATA/'uploads';folder.mkdir(exist_ok=True)
                target=folder/ident;remaining=size
                try:
                    with target.open('wb') as f:
                        while remaining:
                            chunk=self.rfile.read(min(1024*1024,remaining))
                            if not chunk:raise ValueError('Upload afgebroken')
                            f.write(chunk);remaining-=len(chunk)
                except Exception:target.unlink(missing_ok=True);raise
                UPLOADS[ident]=target;return self.reply({'upload':ident})
            if size>1024*1024:raise ValueError('Verzoek te groot')
            body=json.loads(self.rfile.read(size))
            if path=='/api/config':
                c={k:str(body.get(k,'')).strip() for k in ('binary','model','output')}
                if not c['output']:c['output']=str(Path.home()/'Documents/Whisper lokaal')
                _,options,_=capabilities(c)
                if not Path(c['model']).expanduser().is_file():raise ValueError('Modelbestand niet gevonden.')
                (DATA/'config.json').write_text(json.dumps(c));os.chmod(DATA/'config.json',0o600)
                return self.reply({'options':options})
            if path=='/api/start':
                with LOCK:
                    if any(j['status'] in ('queued','converting','running') for j in JOBS.values()):raise ValueError('Er loopt al een taak. Wacht of stop die eerst.')
                    c=config();capabilities(c)
                    source=UPLOADS.get(body.get('upload'))
                    if not source or not source.is_file():raise ValueError('Upload eerst een bestand.')
                    formats=body.get('formats',[])
                    if not formats or any(f not in FORMAT for f in formats):raise ValueError('Kies minstens één uitvoerformaat.')
                    language=body.get('language','auto')
                    if not re.fullmatch('[a-z]{2,3}|auto',language):raise ValueError('Ongeldige taalcode')
                    ident=time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]
                    folder=Path(c['output']).expanduser().resolve()/ident;folder.mkdir(parents=True,mode=0o700)
                    target=folder/'original';shutil.move(source,target);UPLOADS.pop(body['upload'])
                    job=dict(id=ident,name=str(body.get('name','Audio'))[:255],status='queued',progress=0,events=[],files=[],directory=str(folder),input=str(target),command='')
                    JOBS[ident]=job
                threading.Thread(target=run,args=(job,c,body.get('options',{}),formats,language,body.get('translate',False),body.get('colors',True)),daemon=True).start()
                return self.reply({'id':ident})
            job=JOBS.get(body.get('id'))
            if not job:raise ValueError('Taak niet gevonden')
            if path=='/api/cancel':
                with LOCK:
                    if job['status'] not in ('queued','converting','running'):raise ValueError('Taak is al gestopt')
                    job['cancelled']=True
                    proc=job.get('process')
                    if proc and proc.poll() is None:
                        os.killpg(proc.pid,signal.SIGTERM)
                        def kill():
                            try:proc.wait(timeout=3)
                            except subprocess.TimeoutExpired:
                                try:os.killpg(proc.pid,signal.SIGKILL)
                                except ProcessLookupError:pass
                        threading.Thread(target=kill,daemon=True).start()
                return self.reply({'ok':True})
            if path=='/api/reveal':
                if sys.platform=='darwin':subprocess.Popen(['open',job['directory']])
                else:raise ValueError('Open de getoonde map handmatig; Finder openen werkt op macOS.')
                return self.reply({'ok':True})
            self.reply({'error':'Niet gevonden'},404)
        except Exception as e:self.reply({'error':str(e)},400)

def main():
    # Persisted output folders are discovered from current output root.
    for p in Path(config()['output']).expanduser().glob('*/job.json'):
        try:
            j=json.loads(p.read_text())
            if j['status'] in ('queued','converting','running'):j['status']='interrupted'
            JOBS[j['id']]=j
        except (OSError,ValueError,KeyError):pass
    server=ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('PORT','8765'))),Handler)
    url=f'http://127.0.0.1:{server.server_port}'
    print('Whisper lokaal: '+url,flush=True)
    if '--no-browser' not in sys.argv:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:
        for j in JOBS.values():
            proc=j.get('process')
            if proc and proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM)
        server.server_close()
if __name__=='__main__':main()
