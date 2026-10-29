# Verificatie — 29 oktober 2026

Geslaagd op Linux met echte whisper.cpp (`e4acdfdf214836d6ce5c7f8ac6b43b9912f361a1`), tiny.en-model en upstream `samples/jfk.wav`:

- Browserupload → FFmpeg-conversie → echte CLI-inferentie → transcript in de interface.
- Betrouwbaarheidskleuren uit ANSI-uitvoer zichtbaar; uitvoer wordt als tekst behandeld, niet als HTML.
- TXT, SRT, VTT, JSON, CSV en LRC gegenereerd; download via HTTP gecontroleerd.
- Meer dan 30 opties uit de geïnstalleerde CLI-help beschikbaar.
- Ongeldige audio geeft een fout en de gebruiker kan opnieuw starten.
- Taak stoppen en daarna opnieuw kunnen starten.
- Verzoeken zonder schrijftoken en met vreemde Host worden geweigerd.
- Chromium op 1440×1000 en 390×844; geen horizontale overflow of JavaScript-fouten. Screenshots in `review/` zijn echte browsercaptures van deze test.
- Python compilecheck, JavaScript syntaxcheck en Tailwind-build geslaagd.

Het mechanische ontwerpcontroleprogramma draaide met beperkte HTML-parserondersteuning. Desktop- en mobiele captures zijn daarnaast visueel bekeken. De ene kleurwaarschuwing betrof regels uit verschillende CSS-selectors; de blauwe knoppen hebben witte tekst.

Nog niet fysiek getest op een Mac: dubbelklikken op Start.command, Finder openen, Safari, Metal-versnelling en het bestaande model van de ontvanger. Nederlandse audio, Engelse vertaling, VAD en sprekerdetectie zijn in deze sessie niet met eigen testaudio doorgelopen. Ze worden doorgegeven aan de bestaande CLI; benodigde modellen moeten aanwezig zijn. De test bewijst geen kwaliteit van transcripties voor andere opnamen.

Herhalen: zie `tests/integration.py`. De Playwright-testomgeving, FFmpeg-testbinary en het testmodel zitten niet in het downloadpakket.
