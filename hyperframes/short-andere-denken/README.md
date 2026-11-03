# YouTube Short: „Warum denken wir ständig darüber nach, was andere über uns denken?“

Animiertes 9:16-Video (1080 × 1920, 56,5 s) im dunklen Dokumentarstil, gebaut mit HTML, CSS und JavaScript (GSAP).

## Ablauf

| Zeit | Szene | Begriff / Visual |
|---|---|---|
| 0–6,5 s | Einstieg: „Alle sehen dich … oder?“ | Großes Auge öffnet sich, Augen ringsum |
| 6,5–15 s | Rampenlicht | **Spotlight-Effekt** · Lichtkegel über einer Menge |
| 15–21,5 s | Das T-Shirt-Experiment | Balken: geschätzt ~50 % vs. tatsächlich ~23 % |
| 21,5–30 s | Herkunft der Angst | **Zugehörigkeitsbedürfnis** · Gruppe am Feuer, Außenseiter driftet weg |
| 30–37,5 s | Gehirn | **Sozialer Schmerz** · Venn-Diagramm: körperlicher Schmerz ∩ Ablehnung |
| 37,5–44,5 s | Selbstbild | **Spiegel-Selbst** · Spiegel mit verzerrtem Abbild und Zweifeln |
| 44,5–51 s | Die Wendung | Jeder steht in seinem eigenen Rampenlicht |
| 51–56,5 s | Abschluss | „Du bist weniger beobachtet, als du glaubst.“ + Quellen |

Quellen: Gilovich, Medvec & Savitsky (2000); Baumeister & Leary (1995); Eisenberger, Lieberman & Williams (2003); Cooley (1902).

## Im Browser abspielen

`index.html` einfach doppelklicken (der Ordner `assets/` muss daneben liegen).
Die Animation startet automatisch und skaliert sich ins Fenster.

- Klick / Leertaste: Pause / Weiter
- R: Neustart
- F: Vollbild
- Klick auf die Fortschrittsleiste: springen

## MP4 erstellen

Voraussetzung: Node.js ≥ 22 und FFmpeg (für HyperFrames).

```bash
# im Hauptverzeichnis des Repos
npm install
npm run short:render
# → hyperframes/short-andere-denken/renders/was-denken-die-anderen.mp4
```

Oder direkt in diesem Ordner:

```bash
npx hyperframes render -o renders/was-denken-die-anderen.mp4
```

Vorschau mit Zeitleiste zum Bearbeiten: `npx hyperframes preview`.

### Alternative ohne HyperFrames: Bildschirmaufnahme

`index.html` im Browser öffnen, F für Vollbild drücken und mit OBS Studio (oder der
Bildschirmaufnahme des Betriebssystems) aufnehmen. Danach auf 1080 × 1920 zuschneiden.
Der HyperFrames-Render ist jedoch Frame-genau und ruckelfrei – er ist der empfohlene Weg.

## Anpassen

- **Texte der Untertitel:** Liste `CUES` im Script (`[start, ende, "Text mit *Gold-Wort*"]`).
- **Farben:** CSS-Variablen in `:root` (`--gold`, `--gold-soft`, `--ink` …).
- **Timing der Szenen:** Abschnitte `// ---------- 1 · Einstieg ----------` usw. im Script.
- **Ton:** Sprachaufnahme oder Musik als `<audio id="voice" src="assets/voice.mp3" data-start="0" data-volume="1">` in `#root` einfügen – HyperFrames mischt sie beim Rendern ins MP4.
