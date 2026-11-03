# YouTube Short: „Niemand denkt an dich.“

**Thema:** Warum denken wir ständig darüber nach, was andere über uns denken?

Animiertes 9:16-Video (1080 × 1920, 53 s, mit Sounddesign) im dunklen Dokumentarstil –
gebaut mit HTML, CSS und JavaScript (GSAP), renderbar mit HyperFrames.

## Was es „viral“ macht

- **Hook in der ersten Sekunde:** „NIEMAND – DENKT – AN DICH.“ knallt Wort für Wort ins Bild
  (Kamera-Shake, Lichtblitz, Bass-Hit). „NIEMAND“ steht schon im ersten Frame (Thumbnail).
- **Schnelle Schnitte:** alle 1–3 Sekunden passiert etwas; Szenenwechsel als Whip-Pan mit
  Bewegungsunschärfe, Lichtstreifen und Whoosh.
- **Untertitel im Shorts-Stil:** groß, in Großbuchstaben, 1–3 Wörter pro Einblendung,
  Wort-für-Wort-Highlight, Schlüsselwörter in Gold.
- **Pattern Interrupts:** Glitches, Zahlen-Counter (50 % → 23 %), ein Spiegel, der zerbricht,
  ein „Plot-Twist“ mit Musik-Drop und Riser davor.
- **Retention-Bar** oben, **Call-to-Action** („Schick das jemandem …“) am Ende.
- **Nahtloser Loop:** das Ende („Niemand denkt an dich.“) führt direkt zurück zum Anfang.

## Ablauf

| Zeit | Szene | Begriff / Visual |
|---|---|---|
| 0–4,6 s | Hook | „Niemand denkt an dich.“ → „Klingt hart? Es ist die beste Nachricht deines Lebens.“ |
| 4,6–12,4 s | Bahn-Szenario | **Spotlight-Effekt** · 22 Augen starren auf „DU“, dann schließen sie sich |
| 12,4–20,4 s | Cornell-Experiment | Counter: geschätzt 50 % → tatsächlich 23 % |
| 20,4–28,2 s | Steinzeit | **Zugehörigkeitsbedürfnis** · Außenseiter wird aus der Gruppe gestoßen |
| 28,2–35,2 s | Gehirn | **Sozialer Schmerz** · Kreise kollidieren, EKG mit Herzschlag |
| 35,2–42,2 s | Spiegel | **Spiegel-Selbst** · Zweifel fliegen herein, der Spiegel zerbricht |
| 42,2–48,4 s | Plot-Twist | Jeder steht in seinem eigenen Spotlight |
| 48,4–53 s | Abschluss | „Niemand denkt an dich. Und genau das macht dich frei.“ + CTA |

Quellen: Gilovich, Medvec & Savitsky (2000); Baumeister & Leary (1995);
Eisenberger, Lieberman & Williams (2003); Cooley (1902).

## Im Browser abspielen

`index.html` doppelklicken (der Ordner `assets/` muss daneben liegen) und auf
**▶ Abspielen** klicken – der Klick ist nötig, weil Browser Ton erst nach einer Interaktion erlauben.
Das Video läuft in Schleife wie auf YouTube Shorts.

- Klick / Leertaste: Pause / Weiter
- R: Neustart · F: Vollbild
- Klick auf die Fortschrittsleiste: springen

## MP4 erstellen

Voraussetzung: Node.js ≥ 22 und FFmpeg.

```bash
# im Hauptverzeichnis des Repos
npm install
npm run short:render
# → hyperframes/short-andere-denken/renders/niemand-denkt-an-dich.mp4
```

Oder direkt in diesem Ordner:

```bash
npx hyperframes render -o renders/niemand-denkt-an-dich.mp4
```

HyperFrames rendert Frame für Frame (30 fps, ruckelfrei) und mischt `assets/soundtrack.mp3`
automatisch ins MP4. Vorschau mit Zeitleiste: `npx hyperframes preview`.

**Ohne HyperFrames:** `index.html` im Browser öffnen, F für Vollbild, mit OBS Studio
aufnehmen und auf 1080 × 1920 zuschneiden. Der HyperFrames-Render ist aber deutlich sauberer.

## Anpassen

- **Untertitel:** Liste `CUES` im Script – `[start, ende, "Chunk 1 / Chunk 2 mit *Gold-Wort*"]`.
  `/` trennt die Einblendungen, `*…*` färbt Wörter gold.
- **Farben:** CSS-Variablen in `:root` (`--gold`, `--gold-soft`, `--ink` …).
- **Animation:** Abschnitte `// ---------- 1 · HOOK ----------` usw. im Script. Bausteine:
  `slam()` (Wort knallt rein), `pop()`, `whip()` (Szenenwechsel), `impact()` (Shake + Blitz + Bass),
  `glitch()`, `counter()`.
- **Ton neu erzeugen** (nach Änderungen am Timing – jeder `slam`/`whip`/… setzt seinen Sound selbst):

  ```bash
  npm i -D playwright            # einmalig
  node tools/export-sfx.cjs      # liest die Sound-Zeitpunkte aus index.html → assets/sfx.json
  python3 tools/make_soundtrack.py   # synthetisiert assets/soundtrack.mp3 (braucht numpy + ffmpeg)
  ```

  Die komplette Tonspur (Bass-Hits, Whooshes, Ticks, Herzschlag, Beat, Pad, Riser) wird
  synthetisch erzeugt – keine fremden Samples, keine Lizenzprobleme.
- **Eigene Musik / Sprecherstimme:** einfach `assets/soundtrack.mp3` ersetzen oder ein weiteres
  `<audio id="voice" src="assets/voice.mp3" data-start="0" data-volume="1">` in `#root` einfügen.
  Für maximale Reichweite: echte Voiceover-Stimme drüberlegen – die Untertitel-Timings
  in `CUES` sind schon auf einen Sprecher ausgelegt.
