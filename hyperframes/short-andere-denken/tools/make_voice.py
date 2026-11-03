#!/usr/bin/env python3
"""Sprecherstimme für das Short erzeugen, einpassen, mischen und (optional) rendern.

Standard (empfohlen) – Microsoft-Neural-Stimme "Conrad" über edge-tts (kostenlos, ohne Key):

    python3 tools/make_voice.py --render

Stimmen vergleichen (schreibt Hörproben nach samples/):

    python3 tools/make_voice.py --samples

Was passiert:
  1. installiert bei Bedarf das Python-Paket edge-tts bzw. piper-tts
  2. spricht jede Zeile aus assets/sfx.json ("vo") und passt sie in ihr Zeitfenster ein
     (bei Bedarf leicht beschleunigt, Tonhöhe bleibt gleich)
  3. schreibt assets/voice.wav und mischt sie mit tools/make_soundtrack.py in
     assets/soundtrack.mp3 (Musik wird unter der Stimme automatisch leiser)
  4. mit --render: rendert renders/niemand-denkt-an-dich.mp4

Engines und Stimmen:
    --engine edge  (Standard)   --voice de-DE-ConradNeural (Standard),
                                de-DE-FlorianMultilingualNeural, de-DE-KillianNeural,
                                de-DE-SeraphinaMultilingualNeural, de-DE-KatjaNeural, …
    --engine piper              offline; --voice de_DE-thorsten-high (Standard),
                                de_DE-thorsten_emotional-medium, de_DE-kerstin-low, …
                                (lädt das Modell einmalig nach tools/models/, ~110 MB)
    --engine files              eigene Aufnahmen aus assets/voice-lines/01.wav, 02.wav, …
                                (Text dazu: voiceover.txt, mit --write-script erzeugen)
    --engine espeak             Roboterstimme ohne Download (nur zum Testen)
    --speed 1.15                Sprechtempo (1.0 = normal)

Voraussetzungen: Python 3.9+, numpy, ffmpeg.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
ASSETS = os.path.join(PROJECT, "assets")
MODELS = os.path.join(HERE, "models")
LINES_DIR = os.path.join(ASSETS, "voice-lines")
MAX_TEMPO = 1.45  # stärker beschleunigen klingt gehetzt


# ---------------------------------------------------------------- Audio-Helfer
def decode(path):
    """Beliebige Audiodatei → mono float32 @ 44.1 kHz (über ffmpeg)."""
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True,
        capture_output=True,
    ).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def write_wav(path, x, sr=SR):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def trim_silence(x, rel=0.02, pad=0.03):
    if len(x) == 0:
        return x
    thr = np.max(np.abs(x)) * rel
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def change_tempo(x, factor, tmp):
    src, dst = os.path.join(tmp, "t_in.wav"), os.path.join(tmp, "t_out.wav")
    write_wav(src, x)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter:a", f"atempo={factor:.4f}", dst], check=True)
    return decode(dst)


# ---------------------------------------------------------------- Stimmen
class PiperEngine:
    def __init__(self, voice, speed):
        try:
            from piper import PiperVoice, SynthesisConfig  # noqa: F401
        except ImportError:
            print("→ Installiere piper-tts …")
            subprocess.run([sys.executable, "-m", "pip", "install", "piper-tts"], check=True)
        from piper import PiperVoice, SynthesisConfig

        model = os.path.join(MODELS, voice + ".onnx")
        if not os.path.exists(model):
            os.makedirs(MODELS, exist_ok=True)
            print(f"→ Lade Stimme {voice} (einmalig) …")
            subprocess.run([sys.executable, "-m", "piper.download_voices", voice, "--download-dir", MODELS], check=True)
        self.voice = PiperVoice.load(model)
        self.cfg = SynthesisConfig(length_scale=1.0 / speed)

    def say(self, text, i, tmp):
        path = os.path.join(tmp, f"line{i:02d}.wav")
        with wave.open(path, "wb") as wf:
            self.voice.synthesize_wav(text, wf, syn_config=self.cfg)
        return decode(path)


class EdgeEngine:
    """Microsofts deutsche Neural-Stimmen über das Paket edge-tts (kostenlos, ohne API-Key, braucht Internet)."""

    def __init__(self, voice, speed):
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            print("→ Installiere edge-tts …")
            subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], check=True)
        import edge_tts

        self.edge_tts = edge_tts
        self.voice = voice
        self.rate = f"{round((speed - 1) * 100):+d}%"

    def say(self, text, i, tmp):
        path = os.path.join(tmp, f"line{i:02d}.mp3")
        self.edge_tts.Communicate(text, self.voice, rate=self.rate).save_sync(path)
        return decode(path)


class EspeakEngine:
    """Notlösung ohne Download (klingt robotisch). Braucht: pip install espeakng-loader"""

    def __init__(self, speed):
        import ctypes

        import espeakng_loader

        self.ct = ctypes
        self.lib = ctypes.CDLL(espeakng_loader.get_library_path())
        self.sr = self.lib.espeak_Initialize(2, 0, espeakng_loader.get_data_path().encode(), 0)
        self.buf = []
        cb_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)

        def cb(wav, n, _ev):
            if wav and n > 0:
                self.buf.append(ctypes.string_at(wav, n * 2))
            return 0

        self.cb = cb_type(cb)
        self.lib.espeak_SetSynthCallback(self.cb)
        self.lib.espeak_SetVoiceByName(b"de")
        self.lib.espeak_SetParameter(1, int(165 * speed), 0)

    def say(self, text, i, tmp):
        self.buf = []
        t = text.encode()
        self.lib.espeak_Synth(t, len(t) + 1, 0, 1, 0, 1, None, None)
        self.lib.espeak_Synchronize()
        path = os.path.join(tmp, f"line{i:02d}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.sr)
            w.writeframes(b"".join(self.buf))
        return decode(path)


class FilesEngine:
    """Eigene Aufnahmen: assets/voice-lines/01.(wav|mp3|m4a|…), 02.…, eine Datei pro Zeile."""

    def say(self, text, i, tmp):
        for name in sorted(os.listdir(LINES_DIR)):
            if os.path.splitext(name)[0] == f"{i + 1:02d}":
                return decode(os.path.join(LINES_DIR, name))
        raise SystemExit(f"Aufnahme für Zeile {i + 1:02d} fehlt in {LINES_DIR} („{text}“)")


# ---------------------------------------------------------------- Ablauf
# Kandidaten für --samples: (Engine, Stimme, Beschreibung)
CANDIDATES = [
    ("edge", "de-DE-ConradNeural", "männlich, tief, souverän – gewählt"),
    ("edge", "de-DE-FlorianMultilingualNeural", "männlich, warm, ausdrucksstark"),
    ("edge", "de-DE-KillianNeural", "männlich, jung, locker"),
    ("edge", "de-DE-SeraphinaMultilingualNeural", "weiblich, warm, natürlich"),
    ("edge", "de-DE-KatjaNeural", "weiblich, klar, sachlich"),
    ("piper", "de_DE-thorsten-high", "männlich, offline, eher Nachrichtensprecher"),
]
SAMPLE_TEXT = (
    "Niemand denkt an dich. Klingt hart? Es ist die beste Nachricht deines Lebens. "
    "Alle anderen stehen in ihrem eigenen Spottlait. Und genau das macht dich frei."
)


def make_samples(speed):
    out_dir = os.path.join(PROJECT, "samples")
    os.makedirs(out_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for i, (eng, voice, desc) in enumerate(CANDIDATES):
            try:
                engine = EdgeEngine(voice, speed or 1.08) if eng == "edge" else PiperEngine(voice, speed or 1.12)
                clip = engine.say(SAMPLE_TEXT, i, tmp)
                path = os.path.join(out_dir, f"{i + 1}-{voice}.mp3")
                write_wav(os.path.join(tmp, "s.wav"), clip / (np.max(np.abs(clip)) + 1e-9) * 0.9)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "s.wav"), "-b:a", "128k", path], check=True)
                print(f"  ✓ {os.path.relpath(path, PROJECT)}   ({desc})")
            except Exception as e:  # eine fehlende Stimme soll die anderen nicht blockieren
                print(f"  ✗ {voice}: {e}")
    print("→ Anhören, Favorit wählen, dann z. B.: python3 tools/make_voice.py --engine edge --voice <Name> --render")


def write_script(vo):
    path = os.path.join(PROJECT, "voiceover.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("Sprechertext – eine Aufnahme pro Zeile, Dateiname = Nummer (01.wav, 02.m4a, …)\n")
        f.write("Ablegen in: assets/voice-lines/   Dann: python3 tools/make_voice.py --engine files --render\n\n")
        for i, (start, text) in enumerate(vo):
            nxt = vo[i + 1][0] if i + 1 < len(vo) else None
            slot = f"{(nxt - start):.1f} s" if nxt else "bis Ende"
            f.write(f"{i + 1:02d}  [{start:5.1f} s, max. {slot}]  {text}\n")
    print("→ voiceover.txt geschrieben")


def build_voice(engine, vo, duration):
    track = np.zeros(int(duration * SR) + SR)
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        prev_end = 0.0
        for i, (start, text) in enumerate(vo):
            end = vo[i + 1][0] if i + 1 < len(vo) else duration
            # Zeile beginnt zu ihrem Zeitpunkt – oder kurz nach der vorherigen, falls diese überhängt
            place = max(start + 0.04, prev_end + 0.08)
            slot = max(end - place - 0.06, 0.4)
            clip = trim_silence(engine.say(text, i, tmp))
            length = len(clip) / SR
            tempo = 1.0
            if length > slot:
                tempo = min(length / slot, MAX_TEMPO)
                clip = change_tempo(clip, tempo, tmp)
                length = len(clip) / SR
            a = int(place * SR)
            track[a : a + len(clip)] += clip[: len(track) - a]
            prev_end = place + length
            late = place - start - 0.04
            notes = []
            if late > 0.02:
                notes.append(f"+{late:.2f}s später")
            if prev_end > end + 0.05:
                notes.append("hängt in nächste Zeile")
            flag = ("  ⚠ " + ", ".join(notes)) if notes else ""
            report.append(f"  {i + 1:02d} {place:5.2f}s  {length:4.2f}s  ×{tempo:.2f}{flag}  {text}")
    print("\n".join(report))
    track = track[: int(duration * SR)]

    # Sprach-Kette: Hochpass, Kompressor, Normalisierung
    with tempfile.TemporaryDirectory() as tmp:
        raw, out = os.path.join(tmp, "raw.wav"), os.path.join(ASSETS, "voice.wav")
        write_wav(raw, track / (np.max(np.abs(track)) + 1e-9) * 0.9)
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                "highpass=f=85,acompressor=threshold=0.12:ratio=3:attack=4:release=90:makeup=1.6,"
                "equalizer=f=3200:t=q:w=1.2:g=2.5,alimiter=limit=0.95",
                out,
            ],
            check=True,
        )
    print("→ assets/voice.wav geschrieben")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["edge", "piper", "files", "espeak"], default="edge")
    ap.add_argument("--voice", help="Stimme (Standard: de-DE-ConradNeural bzw. de_DE-thorsten-high)")
    ap.add_argument("--speed", type=float, help="Sprechtempo (Standard: 1.1 bei edge, 1.12 bei piper)")
    ap.add_argument("--samples", action="store_true", help="Hörproben mehrerer Stimmen nach samples/ schreiben")
    ap.add_argument("--render", action="store_true", help="danach das MP4 rendern")
    ap.add_argument("--write-script", action="store_true", help="nur voiceover.txt schreiben")
    args = ap.parse_args()

    for tool in ("ffmpeg",):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} fehlt – bitte installieren.")

    with open(os.path.join(ASSETS, "sfx.json"), encoding="utf-8") as f:
        data = json.load(f)
    vo = data["vo"]

    if args.write_script:
        write_script(vo)
        return
    if args.samples:
        make_samples(args.speed)
        return

    if args.engine == "edge":
        engine = EdgeEngine(args.voice or "de-DE-ConradNeural", args.speed or 1.1)
    elif args.engine == "piper":
        engine = PiperEngine(args.voice or "de_DE-thorsten-high", args.speed or 1.12)
    elif args.engine == "espeak":
        engine = EspeakEngine(args.speed or 1.0)
    else:
        engine = FilesEngine()

    build_voice(engine, vo, data["duration"])

    sys.path.insert(0, HERE)
    import make_soundtrack

    make_soundtrack.main()

    if args.render:
        npx = shutil.which("npx") or shutil.which("npx.cmd")
        if not npx:
            raise SystemExit("npx (Node.js) fehlt – zum Rendern bitte Node.js ≥ 22 installieren.")
        print("→ Rendere MP4 (dauert einige Minuten) …")
        subprocess.run(
            [npx, "--yes", "hyperframes@0.9.8", "render", "-o", "renders/niemand-denkt-an-dich.mp4"],
            cwd=PROJECT,
            check=True,
        )
        print("✓ Fertig: renders/niemand-denkt-an-dich.mp4")


if __name__ == "__main__":
    main()
