"""stemme.py - dansk voiceover med piper TTS (gratis).

Finder 'piper' + stemmen da_DK-talesyntese-medium.onnx i tools/piper/ eller PATH.
Findes piper ikke, returneres None, og videoen faar kun musik + effekter
(den er aldrig uden lyd).
"""
import os
import random
import shutil
import subprocess
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100


def _find():
    cands = [os.path.join(HERE, "piper", "piper"), shutil.which("piper")]
    exe = next((c for c in cands if c and os.path.exists(c)), None)
    model = None
    for d in [os.path.join(HERE, "piper"), os.path.join(HERE, "..", "assets", "stemme")]:
        p = os.path.join(d, "da_DK-talesyntese-medium.onnx")
        if os.path.exists(p):
            model = p
    return exe, model


def available():
    exe, model = _find()
    return bool(exe and model)


def _read(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x


def say_scenes(texts, seed=7):
    """Returnerer (liste af numpy-arrays i SR, en pr. scene) eller None."""
    exe, model = _find()
    if not (exe and model):
        return None
    rnd = random.Random(seed)
    out = []
    tmp = tempfile.mkdtemp()
    for i, txt in enumerate(texts):
        if not txt:
            out.append(np.zeros(0, dtype=np.float32))
            continue
        raw = os.path.join(tmp, f"r{i}.wav")
        fin = os.path.join(tmp, f"f{i}.wav")
        ls = 0.97 * (1 + rnd.uniform(-0.05, 0.05))
        subprocess.run([exe, "--model", model, "--length_scale", f"{ls:.3f}",
                        "--noise_scale", "0.75", "--noise_w", "0.95",
                        "--sentence_silence", "0.3", "--output_file", raw],
                       input=txt.encode("utf-8"), check=True, capture_output=True)
        # lidt EQ + kompressor, og resample til 44.1 kHz mono
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "highpass=f=80,equalizer=f=3000:t=q:w=1:g=3,"
                        "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"
                        "loudnorm=I=-16:TP=-1.5",
                        "-ar", str(SR), "-ac", "1", fin], check=True)
        out.append(_read(fin))
    return out
