# Whisper lokaal

Lokale webinterface voor [whisper.cpp](https://github.com/ggml-org/whisper.cpp), met upload, live transcriptie, betrouwbaarheidskleuren, uitvoerbestanden en instellingen uit de eigen CLI-help.

## Op de Mac downloaden en starten

Je hoeft geen code te schrijven. Je bestaande whisper.cpp-installatie en model blijven in gebruik.

### 1. Download de app

1. Open [de nieuwste release](https://github.com/jellewijma/whisper-lokaal/releases/latest).
2. Klik onder **Assets** op **Whisper-lokaal-Mac.zip**. Kies de kant-en-klare ZIP, niet “Source code”.
3. Open de ZIP in Finder. Verplaats de uitgepakte map **Whisper-lokaal** bijvoorbeeld naar **Documenten**.

De app werkt lokaal. Je hebt na het downloaden geen internet nodig om de interface te gebruiken.

### 2. Controleer de benodigdheden

Open **Terminal** op de Mac (via Spotlight: Cmd+spatie, typ Terminal). Voer deze twee opdrachten één voor één uit:

```bash
python3 --version
ffmpeg -version
```

- **Python:** versie 3.10 of hoger is nodig. Ontbreekt Python of is de versie ouder? Installeer de macOS-versie van [python.org](https://www.python.org/downloads/macos/), sluit Terminal en open Terminal opnieuw.
- **FFmpeg:** zie je versie-informatie, dan is dit in orde. Ontbreekt FFmpeg en gebruik je Homebrew? Voer `brew install ffmpeg` uit. Heb je Homebrew nog niet, volg dan eerst de installatie op [brew.sh](https://brew.sh/) en voer daarna die opdracht uit.
- **whisper.cpp:** je bestaande `whisper-cli` en het bijbehorende `.bin`-model moeten op de Mac staan. Deze app installeert of downloadt ze niet. Ze werkt met [whisper.cpp](https://github.com/ggml-org/whisper.cpp), niet met het Python-commando `whisper`.

Node.js en npm zijn niet nodig om de app te gebruiken.

### 3. Start de app

1. Open de uitgepakte map **Whisper-lokaal**.
2. Dubbelklik op **Start.command**.
3. Houd het Terminal-venster dat opent in beeld of geminimaliseerd; sluit het niet zolang je de app gebruikt.
4. De browser opent op **http://127.0.0.1:8765**. Opent hij niet vanzelf? Typ dit adres zelf in de browser.

Blokkeert macOS de dubbelklik of ontbreken uitvoerrechten? Open Terminal, typ `bash` gevolgd door een spatie, sleep **Start.command** vanuit Finder in Terminal en druk op Enter. Het volledige pad wordt zo automatisch ingevuld.

### 4. Koppel jouw bestaande Whisper-installatie

Open bovenaan **Installatie & uitvoermap**. De app probeert bekende locaties automatisch te vinden. Controleer of vul de volgende velden in:

| Veld | Wat vul je in? | Voorbeeld — vervang de gebruikersnaam en modelnaam |
| --- | --- | --- |
| Pad naar whisper-cli | Het volledige pad naar het uitvoerbare CLI-bestand | `/Users/jouwnaam/whisper.cpp/build/bin/whisper-cli` |
| Pad naar model (.bin) | Het volledige pad naar jouw bestaande model | `/Users/jouwnaam/whisper.cpp/models/ggml-large-v3-turbo.bin` |
| Uitvoermap | De map waarin de app de resultaten mag opslaan | `/Users/jouwnaam/Documents/Whisper lokaal` |

Tip: selecteer een bestand in Finder en druk **Option+Cmd+C** om het volledige pad te kopiëren. Plak dat in het bijbehorende veld, zonder extra aanhalingstekens.

Klik **Opslaan & controleren**. Ga pas verder wanneer **Installatie gevonden en opgeslagen** verschijnt. De app onthoudt deze instellingen.

### 5. Maak je eerste ondertiteling

1. Klik bij **Audio of video kiezen** en selecteer je opname.
2. Kies de **Gesproken taal**. Bij een Nederlandse opname kies je **Nederlands**.
3. Kies **Ondertitelen** voor tekst in de gesproken taal, of **Naar Engels** voor een Engelse vertaling. Whisper ondersteunt hier geen andere doeltaal.
4. Laat **TXT** en **SRT** aangevinkt voor gewone tekst en een ondertitelbestand.
5. Laat **Betrouwbaarheid met kleur tonen** aan als je de modelinschatting wilt zien.
6. Eventueel: open **Alle CLI-opties**. Deze lijst komt uit jouw eigen installatie. Laat velden leeg om de standaardwaarden te gebruiken.
7. Klik **Start ondertitelen**. Eerst wordt de audio voorbereid; daarna verschijnt de tekst rechts zodra Whisper segmenten gereed heeft.

### 6. Vind je bestanden terug

Onder **Uitvoerbestanden** staan na afloop de downloads en het exacte mappad. Klik **Open uitvoermap** om die map in Finder te openen.

Standaard staan resultaten in **Documenten → Whisper lokaal → een map per taak**. In die map staan onder andere `transcript.txt` en `transcript.srt`. Via de downloadlinks sla je een extra kopie op in de downloadmap van je browser.

Klaar? Ga naar het Terminal-venster en druk **Ctrl+C** om de app te stoppen. De resultaten blijven bewaard.

### Als iets niet werkt

| Melding of situatie | Wat doe je? |
| --- | --- |
| Geen browservenster | Open `http://127.0.0.1:8765` zelf en houd Terminal open. |
| FFmpeg ontbreekt | Installeer met `brew install ffmpeg`, stop en start de app opnieuw. |
| Model niet gevonden | Controleer het volledige pad naar het bestaande `.bin`-bestand. |
| Dit lijkt geen whisper.cpp CLI | Kies `whisper-cli` uit je whisper.cpp-installatie. Het Python-commando `whisper` werkt hier niet. |
| Address already in use / poort bezet | Er draait mogelijk al een exemplaar: open het browseradres. Stop een eerder exemplaar met Ctrl+C voordat je opnieuw start. |
| Geen tekst tijdens “Audio voorbereiden” | Wacht tot de conversie klaar is. Whisper geeft pas daarna tekst per segment door. |
| Verwerking mislukt | Open **Verwerkingslog & commando** voor de foutmelding. Controleer eerst model, CLI-pad en FFmpeg. |

## Gebruik

- **Ondertitelen** bewaart de gesproken taal. **Naar Engels** vertaalt naar Engels: Whisper ondersteunt geen andere doeltaal.
- Tekst verschijnt zodra Whisper een segment vrijgeeft, dus niet noodzakelijk woord voor woord op het moment dat het gesproken wordt.
- Rood/geel/groen volgt de experimentele modelbetrouwbaarheid van whisper.cpp; dit is geen garantie dat woorden juist zijn.
- TXT: gewone tekst. SRT/VTT: ondertiteling met tijden. JSON/CSV/LRC: verdere verwerking.
- De uitvoermap staat altijd in beeld; **Open uitvoermap** opent Finder op macOS. Downloaden maakt een extra kopie via de browser.
- Standaardmap: `~/Documents/Whisper lokaal/<taak-id>/`. Elke taak heeft een eigen map met origineel, voorbereide WAV, transcriptbestanden en taaklog. Die blijven bewaard; verwijder oude taakmappen handmatig als je ruimte wilt vrijmaken.
- Alle beschikbare extra CLI-opties komen uit de geïnstalleerde `--help`. De app beheert input, model, taal, voortgang en uitvoerpaden zelf; opties die live uitvoer verhinderen zijn afgeschermd. VAD/tinydiarize vereisen de bijbehorende modellen. De volledige geraadpleegde upstream-opties staan in `CLI-REFERENCE.md`.
- FFmpeg zet uploads om naar 16 kHz PCM; stereo blijft behouden bij `--diarize`.
- Eén taak tegelijk; **Stoppen** beëindigt de verwerking. Houd het Terminal-venster open. Sluit met Ctrl+C.

## Privacy en techniek

Luistert alleen op `127.0.0.1`. Geen uploads naar externe diensten en geen CDN's of externe lettertypen. De gekozen bestanden worden lokaal gekopieerd. Configuratie staat in `~/.whisper-local/config.json`. De app gebruikt Host-controle en een willekeurig schrijftoken tegen verzoeken vanaf andere websites. Gebruik de app niet als publieke webserver.

## Ontwikkelen

`python3 app.py --no-browser` start de server. `PORT=8766` kiest een andere poort. `WHISPER_UI_DATA=/pad` isoleert configuratie. Voor CSS: `npm ci` en `npm run build:css`. De gecompileerde Tailwind-CSS zit al in het pakket.

Zie `VALIDATION.md` voor wat wel en niet is getest. Dit project is een onafhankelijke interface en geen officieel OpenAI- of whisper.cpp-product.
