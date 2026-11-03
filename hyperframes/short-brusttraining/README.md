# YouTube Short: „Was passiert im Brustmuskel?“

Animiertes 9:16-Video (1080 × 1920, 38 s) im dunklen Dokumentarstil – erklärt an einer
anatomischen Grafik des großen Brustmuskels (M. pectoralis major).

## Sprechertext

> Du trainierst deine Brust. Aber weißt du eigentlich, was dabei im Muskel passiert?
> Beim Krafttraining entstehen mechanische und metabolische Reize. Besonders die mechanische
> Spannung spielt eine wichtige Rolle bei der Anpassung der Muskulatur.
> Dein Körper reagiert auf diese Belastung mit Anpassungsprozessen, die langfristig zu
> Muskelwachstum führen können.
> Deshalb geht es beim Muskelaufbau nicht einfach darum, möglichst viele Wiederholungen zu
> machen. Entscheidend ist, wie du deinen Trainingsreiz setzt und über die Zeit steigerst.

## Ablauf

| Zeit | Bild |
|---|---|
| 0–2 s | Hook: „DU TRAINIERST DEINE BRUST.“ |
| 2–5,4 s | Scan-Linie über den anatomischen Oberkörper, „Was passiert im Muskel?“ |
| 5,4–9,3 s | Muskelfasern wachsen fächerförmig vom Brustbein zum Oberarm. **Mechanisch** (Spannungspfeile) und **metabolisch** (aufsteigende Stoffwechselprodukte) |
| 9,3–14,9 s | **Mechanische Spannung**: Muskel kontrahiert dreimal, Spannungsbalken füllt sich |
| 14,9–19 s | Zoom: Muskel › Faser › Myofibrille › **Sarkomer**. Last zieht, Filamente gleiten, Signale → Proteinsynthese, neues Filament wird parallel eingebaut |
| 19–22,2 s | Faser-Querschnitt wird dicker: **Hypertrophie**, Zeitachse „Wochen → Monate“ |
| 22,2–27,9 s | Wiederholungszähler rast auf 100 – durchgestrichen: „MEHR ≠ BESSER.“ |
| 27,9–33 s | Diagramm: Trainingsreiz steigt Woche für Woche – **Progressive Overload** |
| 33–38 s | „REIZ SETZEN. REIZ STEIGERN.“ + Call-to-Action |

## Abspielen und rendern

- **Im Browser:** `index.html` öffnen (Ordner `assets/` muss daneben liegen) → ▶ Abspielen.
- **MP4** (Node.js ≥ 22, FFmpeg) – im Hauptverzeichnis des Repos:

  ```bash
  npm install
  npm run brust:render         # → hyperframes/short-brusttraining/renders/brusttraining.mp4
  ```

## Sprecherstimme

Der Sprechertext liegt mit Zeitmarken in `index.html` (`window.__vo`). Ein Befehl erzeugt die
Stimme, passt jede Zeile in ihr Zeitfenster ein, senkt die Musik darunter ab und rendert:

```bash
npm run brust:voice          # Microsoft-Stimme „Conrad“ (edge-tts, kostenlos)
npm run brust:voice-google   # Google Cloud TTS (Schlüssel in GOOGLE_TTS_API_KEY)
```

Weitere Optionen (`--voice`, `--speed`, eigene Aufnahmen mit `--engine files`, Stimmproben mit
`--samples`): siehe `python3 tools/make_voice.py --help` und die README im Ordner
`short-andere-denken`, die Werkzeuge sind identisch.

## Anpassen

- **Untertitel:** `CUES` im Script (`/` trennt Einblendungen, `*…*` = gold).
- **Sprechertext:** `window.__vo` – danach `node tools/export-sfx.cjs` (braucht `npm i -D playwright`).
- **Musik:** `window.__music` (Tempo, Beat-Abschnitte, Riser, Drop) → `python3 tools/make_soundtrack.py`.
- **Anatomie:** SVG `#torso`; die Muskelfasern werden im Script aus `ORIGIN` (Ursprung an
  Schlüsselbein und Brustbein) zum Ansatz am Oberarm berechnet.
