"""lyd.py - eget syntetiseret lydspor (ingen rettighedsproblemer).

Beat + whoosh ved sceneskift, pop naar noget dukker op, chime ved logo.
Laegges lavt under stemmen. Bruges af lav_video.py, men kan koeres alene:
    python3 tools/lyd.py 20 test.wav
"""
import sys
import wave

import numpy as np

SR = 44100


def _env(n, attack, decay):
    a = max(1, int(attack * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    e[a:] = np.exp(-np.arange(n - a) / (decay * SR))
    return e


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * _env(n, 0.002, 0.12)


def hat(rng):
    n = int(0.06 * SR)
    x = rng.standard_normal(n)
    x = np.diff(x, prepend=0)  # simpelt hoejpas
    return x * _env(n, 0.001, 0.015) * 0.25


def bass_note(freq, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
    return x * _env(n, 0.01, length * 0.5) * 0.35


def whoosh(rng):
    n = int(0.45 * SR)
    x = rng.standard_normal(n)
    # glidende lavpas: stigende cutoff via enkel 1-pols filter
    out = np.zeros(n)
    y = 0.0
    for i in range(n):
        c = 0.02 + 0.35 * (i / n)
        y += c * (x[i] - y)
        out[i] = y
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * 0.9


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 40) + 500
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * _env(n, 0.001, 0.025) * 0.6


def chime():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for i, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
        d = int(i * 0.07 * SR)
        seg = np.sin(2 * np.pi * f * t[: n - d]) * np.exp(-t[: n - d] * 3.0)
        x[d:] += seg * (0.5 - i * 0.08)
    return x * 0.5


def _add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def make_track(duration, events, out_wav, voice=None, seed=1, bpm=104):
    """events: liste af (tid_i_sek, 'cut' | 'pop' | 'chime').
    voice: numpy-array (mono, SR) eller None. Musikken duckes under stemmen."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + 1
    music = np.zeros(n)
    beat = 60.0 / bpm
    k, roots = kick(), [110.0, 87.3, 98.0, 82.4]  # A, F, G, E
    b = 0
    t = 0.0
    while t < duration:
        _add(music, k * 0.8, t)
        _add(music, hat(rng), t + beat / 2)
        if b % 4 == 0:
            _add(music, bass_note(roots[(b // 4) % 4], beat * 4), t)
        t += beat
        b += 1
    # fade ind/ud
    fi = int(0.05 * SR)
    music[:fi] *= np.linspace(0.6, 1, fi)  # lyd fra foerste frame
    fo = int(0.8 * SR)
    music[-fo:] *= np.linspace(1, 0, fo)

    fx = np.zeros(n)
    for at, kind in events:
        if kind == "cut":
            _add(fx, whoosh(rng), max(0, at - 0.2))
        elif kind == "pop":
            _add(fx, pop(), at)
        elif kind == "chime":
            _add(fx, chime(), at)

    if voice is not None:
        v = np.zeros(n)
        v[: min(n, len(voice))] = voice[:n]
        # ducking: musik ned hvor der tales
        envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / (0.08 * SR), mode="same")
        duck = 1 - 0.6 * np.clip(envv / (envv.max() + 1e-9) * 4, 0, 1)
        mix = music * 0.16 * duck + fx * 0.22 + v * 0.95
    else:
        mix = music * 0.45 + fx * 0.35

    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.89
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_wav


if __name__ == "__main__":
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 10
    out = sys.argv[2] if len(sys.argv) > 2 else "test.wav"
    make_track(d, [(2, "cut"), (2.1, "pop"), (d - 2.5, "chime")], out)
    print(out)
