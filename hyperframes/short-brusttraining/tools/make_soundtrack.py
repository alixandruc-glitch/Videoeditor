#!/usr/bin/env python3
"""Synthetisiert die Tonspur (Musikbett + Sound-Effekte) aus assets/sfx.json.

Aufruf:  python3 tools/make_soundtrack.py
Ergebnis: assets/soundtrack.mp3  (benötigt numpy und ffmpeg)

Liegt assets/voice.wav vor (erzeugt von tools/make_voice.py), wird die Sprecherstimme
eingemischt und die Musik darunter automatisch abgesenkt.

Alles wird hier berechnet – keine fremden Audiodateien, keine Lizenzfragen.
"""
import json
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")

# Musikalische Struktur – Standardwerte, werden von "music" in assets/sfx.json überschrieben
# (definiert als window.__music in index.html)
BPM = 100
BEAT = 60 / BPM
KICK_SECTIONS = [(4.6, 42.2), (43.16, 52.6)]
HAT_SECTIONS = [(12.4, 42.0), (44.2, 52.6)]
RISER = (40.4, 42.2)
DROP = (42.2, 43.16)


def apply_music_config(cfg):
    global BPM, BEAT, KICK_SECTIONS, HAT_SECTIONS, RISER, DROP
    if not cfg:
        return
    BPM = cfg.get("bpm", BPM)
    BEAT = 60 / BPM
    KICK_SECTIONS = [tuple(x) for x in cfg.get("kick", KICK_SECTIONS)]
    HAT_SECTIONS = [tuple(x) for x in cfg.get("hats", HAT_SECTIONS)]
    RISER = tuple(cfg.get("riser", RISER))
    DROP = tuple(cfg.get("drop", DROP))


CHORDS = [  # (Grundton-Frequenzen) Am – F – C – Em
    [110.0, 130.81, 164.81],
    [87.31, 110.0, 130.81],
    [130.81, 164.81, 196.0],
    [82.41, 123.47, 164.81],
]

rng = np.random.default_rng(1234)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, cutoff):
    """Einpoliger Tiefpass; cutoff darf ein Array (zeitvariabel) sein."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def sweep_sine(f, t):
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


# ---------------- Sound-Effekte ----------------
def boom():
    t = t_axis(1.6)
    body = sweep_sine(38 + 110 * np.exp(-t * 16), t) * np.exp(-t * 2.6)
    crack = lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 22) * 0.9
    return np.tanh(1.6 * body + crack) * 0.95


def hit():
    t = t_axis(0.6)
    body = sweep_sine(60 + 150 * np.exp(-t * 30), t) * np.exp(-t * 7)
    snap = lowpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 45) * 0.6
    return np.tanh(1.4 * body + snap) * 0.8


def whoosh(d=0.55):
    t = t_axis(d)
    p = t / d
    env = np.sin(np.pi * p ** 1.4) ** 2
    cutoff = 300 + 5200 * np.sin(np.pi * p) ** 2
    n = lowpass(rng.standard_normal(len(t)), cutoff)
    n = n - lowpass(n, 180)
    return n * env * 1.1


def tick():
    t = t_axis(0.07)
    return (np.sin(2 * np.pi * 1900 * t) + 0.4 * np.sin(2 * np.pi * 3800 * t)) * np.exp(-t * 85) * 0.6


def glitch():
    t = t_axis(0.24)
    seg = (t / 0.03).astype(int)
    freqs = np.array([220, 880, 330, 660, 1320, 440, 990, 550])[seg % 8]
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(freqs) / SR))
    crushed = np.round(rng.standard_normal(len(t)) * 3) / 3
    return lowpass((0.5 * sq + 0.35 * crushed) * (seg % 3 != 2), 5500) * 0.7


def heart():
    out = np.zeros(int(0.5 * SR))
    for off, amp in [(0.0, 1.0), (0.19, 0.7)]:
        t = t_axis(0.22)
        thump = sweep_sine(48 + 40 * np.exp(-t * 30), t) * np.exp(-t * 18) * amp
        i = int(off * SR)
        out[i : i + len(thump)] += thump
    return np.tanh(out * 1.8) * 0.9


SFX = {"boom": boom, "hit": hit, "whoosh": whoosh, "tick": tick, "glitch": glitch, "heart": heart}


def place(buf, sig, t, vol):
    i = int(t * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i : i + len(sig)] += sig * vol


# ---------------- Musikbett ----------------
def kick():
    t = t_axis(0.35)
    return np.tanh(2.2 * sweep_sine(45 + 120 * np.exp(-t * 40), t) * np.exp(-t * 9)) * 0.8


def hat():
    t = t_axis(0.05)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 7000)) * np.exp(-t * 90) * 0.5


def bed(duration):
    n = int(duration * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)

    # Drone + Luft
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * 0.12 * t)
    out += (0.5 * np.sin(2 * np.pi * 55 * t) + 0.25 * np.sin(2 * np.pi * 82.41 * t)) * trem * 0.32
    air = lowpass(rng.standard_normal(n), 900)
    out += (air - lowpass(air, 200)) * 0.25

    # Pad-Akkorde, alle 8 Schläge ein Wechsel
    bar = BEAT * 8
    for k in range(int(duration / bar) + 1):
        start = k * bar
        chord = CHORDS[k % len(CHORDS)]
        seg_t = t_axis(min(bar + 0.6, duration - start))
        if len(seg_t) == 0:
            continue
        env = np.minimum(1, seg_t / 0.9) * np.minimum(1, (bar + 0.6 - seg_t) / 0.8)
        pad = np.zeros(len(seg_t))
        for f in chord:
            for h in range(1, 6):
                detune = 1 + 0.002 * (h % 2)
                pad += np.sin(2 * np.pi * f * h * detune * seg_t) / (h * 1.6)
        place(out, pad * env * 0.07, start, 1)

    # Kick & Hi-Hats
    k_sig, h_sig = kick(), hat()
    for a, b in KICK_SECTIONS:
        tt = a
        while tt < b:
            place(out, k_sig, tt, 0.55)
            tt += BEAT
    for a, b in HAT_SECTIONS:
        tt = a + BEAT / 2
        while tt < b:
            place(out, h_sig, tt, 0.35)
            tt += BEAT

    # Riser vor dem Plot-Twist
    a, b = RISER
    rt = t_axis(b - a)
    p = rt / (b - a)
    riser = lowpass(rng.standard_normal(len(rt)), 400 + 7000 * p ** 2) * p ** 2 * 1.4
    riser += np.sin(2 * np.pi * np.cumsum(200 + 900 * p ** 2) / SR) * p ** 3 * 0.25
    place(out, riser, a, 1)

    # Musik im Drop (Plot-Twist) kurz ausdünnen, am Ende ausblenden
    gain = np.ones(n)
    da, db = int(DROP[0] * SR), int(DROP[1] * SR)
    gain[da:db] = 0.25
    fade = int(0.6 * SR)
    gain[-fade:] *= np.linspace(1, 0, fade)
    return out * gain


def load_voice(n):
    """assets/voice.wav (von tools/make_voice.py) laden, falls vorhanden."""
    path = os.path.join(ASSETS, "voice.wav")
    if not os.path.exists(path):
        return None
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True,
        capture_output=True,
    ).stdout
    v = np.frombuffer(out, dtype=np.float32).astype(np.float64)
    v = v[:n] if len(v) >= n else np.concatenate([v, np.zeros(n - len(v))])
    return v / (np.max(np.abs(v)) + 1e-9) * 0.9


def main():
    with open(os.path.join(ASSETS, "sfx.json")) as f:
        data = json.load(f)
    duration = data["duration"]
    apply_music_config(data.get("music"))
    music = bed(duration)
    fx = np.zeros_like(music)
    cache = {}
    for name, t, vol in data["sfx"]:
        if name not in cache:
            cache[name] = SFX[name]()
        place(fx, cache[name], t, vol)
    voice = load_voice(len(music))
    if voice is None:
        mix = 0.75 * music + 0.9 * fx
    else:
        # Ducking: Musik (und etwas die Effekte) unter der Stimme absenken
        env = np.abs(voice)
        env = lowpass(lowpass(env, 6), 6)
        env = np.clip(env / (np.max(env) * 0.25 + 1e-9), 0, 1)
        mix = 0.75 * music * (1 - 0.6 * env) + 0.9 * fx * (1 - 0.3 * env) + 1.15 * voice
        print("→ Sprecherstimme (assets/voice.wav) eingemischt")
    mix = np.tanh(mix * 0.9)
    mix /= np.max(np.abs(mix)) / 0.75

    # leichte Stereo-Breite
    delay = int(0.012 * SR)
    left = mix
    right = np.concatenate([np.zeros(delay), mix[:-delay]]) * 0.6 + mix * 0.4
    stereo = np.stack([left, right], axis=1)
    pcm = (stereo * 32767).astype(np.int16)

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "soundtrack.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        mp3 = os.path.join(ASSETS, "soundtrack.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "192k", mp3], check=True)
    print(f"{len(data['sfx'])} Effekte, {duration}s → assets/soundtrack.mp3")


if __name__ == "__main__":
    main()
