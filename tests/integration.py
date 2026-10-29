"""End-to-end check with a real whisper.cpp build and tiny.en model.
Usage: WHISPER_TEST_ENGINE=/path/to/whisper.cpp python tests/integration.py
Requires Playwright in the test environment; not needed by app users.
"""
import json, os, subprocess, tempfile, time, urllib.request, urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
engine=Path(os.environ['WHISPER_TEST_ENGINE'])
tmp=Path(tempfile.mkdtemp(prefix='whisper-local-test-'))
(tmp/'config.json').write_text(json.dumps(dict(binary=str(engine/'build/bin/whisper-cli'),model=str(engine/'models/ggml-tiny.en.bin'),output=str(tmp/'output'))))
env={**os.environ,'WHISPER_UI_DATA':str(tmp),'PORT':'8876'}
proc=subprocess.Popen(['python3',str(ROOT/'app.py'),'--no-browser'],env=env,stdout=subprocess.PIPE)
base='http://127.0.0.1:8876'
try:
    for _ in range(100):
        try:
            with urllib.request.urlopen(base+'/api/state') as r:s=json.load(r)
            break
        except urllib.error.URLError:time.sleep(.1)
    assert not s['error'],s
    assert len(s['options'])>30,len(s['options'])
    bad=urllib.request.Request(base+'/api/config',data=b'{}',headers={'Content-Type':'application/json'})
    try:urllib.request.urlopen(bad);raise AssertionError('Missing token accepted')
    except urllib.error.HTTPError as e:assert e.code==403
    evil=urllib.request.Request(base+'/api/state',headers={'Host':'evil.example'})
    try:urllib.request.urlopen(evil);raise AssertionError('Invalid Host accepted')
    except urllib.error.HTTPError as e:assert e.code==403
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base);page.wait_for_function("document.getElementById('options').children.length > 30")
        page.locator('#file').set_input_files(str(engine/'samples/jfk.wav'))
        page.locator('#language').select_option('en')
        page.locator('#formats input[value=vtt]').check()
        page.locator('#formats input[value=json]').check()
        page.locator('#formats input[value=csv]').check()
        page.locator('#formats input[value=lrc]').check()
        page.locator('#start').click()
        page.wait_for_function("document.getElementById('status').textContent.includes('Voltooid') || document.getElementById('status').textContent.includes('Mislukt')",timeout=180000)
        assert 'Voltooid' in page.locator('#status').inner_text(),page.locator('#status').inner_text()+page.locator('#logs').inner_text()
        assert 'country' in page.locator('#transcript').inner_text().lower()
        assert page.locator('#transcript span[style]').count()>0,'No confidence colors'
        assert page.locator('#downloads a').count()==6,page.locator('#downloads').inner_text()
        href=page.locator('#downloads a').first.get_attribute('href')
        with urllib.request.urlopen(base+href) as r:assert len(r.read())>10
        page.screenshot(path=str(tmp/'desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(tmp/'mobile.png'),full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'Horizontal overflow'
        page.locator('#file').set_input_files({'name':'broken.wav','mimeType':'audio/wav','buffer':b'not audio'})
        page.locator('#start').click()
        page.wait_for_function("document.getElementById('status').textContent.includes('Mislukt')",timeout=15000)
        assert not page.locator('#start').is_disabled(),'Failed job cannot retry'
        page.locator('#file').set_input_files(str(engine/'samples/jfk.wav'))
        page.locator('#start').click()
        page.locator('#cancel').wait_for(state='visible')
        page.locator('#cancel').click()
        page.wait_for_function("document.getElementById('status').textContent.includes('Gestopt')",timeout=15000)
        assert not page.locator('#start').is_disabled()
        assert not errors,errors
        browser.close()
    print('PASS: real audio upload, conversion, inference, ANSI colors, six downloads, browser desktop/mobile, failure/retry, cancellation, Host and CSRF checks')
    print('Artifacts:',tmp)
finally:
    proc.terminate();proc.wait(timeout=10)
