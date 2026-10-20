# Beat original lo-fi / chill (compuesto por código, sin muestras de terceros)
import numpy as np, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 32.0
BPM = 88
beat = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)
out = np.zeros((N, 2))

def env(n, a=.01, r=.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e
def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[:N - i]
    out[i:i+len(sig), 0] += sig * gain * (1 - pan) ** .5 if pan > 0 else sig * gain
    out[i:i+len(sig), 1] += sig * gain * (1 + pan) ** .5 if pan < 0 else sig * gain
def lp(x, f):
    return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f):
    return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)

def note(m): return 440 * 2 ** ((m - 69) / 12)
def kick():
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
def snare():
    n = int(.3 * SR)
    return lp(hp(rng.standard_normal(n), 900), 5000) * env(n, .002, .07) * .6
def hat():
    n = int(.08 * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, .001, .018) * .35
def keys(m, length):
    n = int(length * SR); t = np.arange(n) / SR
    f = note(m); s = 0
    for h, g in [(1, 1), (2, .35), (3, .12), (4, .06)]:
        s = s + g * np.sin(2 * np.pi * f * h * t + .4 * np.sin(2 * np.pi * 5 * t))
    return lp(s * env(n, .015, length * .55), 2400)
def pad(ms, length):
    n = int(length * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * note(m) * t) + .3 * np.sin(2 * np.pi * note(m) * 2.003 * t) for m in ms)
    a = np.minimum(1, t / .6) * np.minimum(1, (length - t) / .6)
    return lp(s * a, 1200) / len(ms)
def bass(m, length):
    n = int(length * SR); t = np.arange(n) / SR
    return np.tanh(1.5 * np.sin(2 * np.pi * note(m) * t)) * env(n, .01, length * .7)

# Am9 – Fmaj7 – Cmaj7 – G6 (cada uno 1 compás)
prog = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 67], [48, 55, 59, 64, 67], [55, 59, 62, 64, 66]]
roots = [45, 41, 48, 43]
bar = 4 * beat
nbars = int(np.ceil(DUR / bar))
for b in range(nbars):
    t0 = b * bar; ch = prog[b % 4]
    add(pad(ch, bar + .4), t0, .18)
    add(bass(roots[b % 4], beat * 1.6), t0, .32)
    add(bass(roots[b % 4], beat * .9), t0 + beat * 2.5, .25)
    # arpegio de piano
    pat = [0, 2, 4, 3, 1, 3, 2, 4]
    for k, idx in enumerate(pat):
        sw = .06 * beat if k % 2 else 0
        add(keys(ch[idx] + 12, beat * .9), t0 + k * beat / 2 + sw, .09, pan=(.3 if k % 2 else -.3))
    if b >= 1:  # la batería entra después del gancho
        for q in range(4):
            if q in (0, 2): add(kick(), t0 + q * beat, .55)
            if q == 2 and b % 2: add(kick(), t0 + q * beat + beat * .75, .35)
            if q in (1, 3): add(snare(), t0 + q * beat, .32)
            for e in range(2):
                add(hat(), t0 + q * beat + e * beat / 2 + (.05 * beat if e else 0), .5 if e == 0 else .3)

# vinilo suave
out += (lp(rng.standard_normal((N, 2)).T, 3000).T) * .004
# fades
fi = int(.3 * SR); fo = int(1.5 * SR)
out[:fi] *= np.linspace(0, 1, fi)[:, None]; out[-fo:] *= np.linspace(1, 0, fo)[:, None]
out /= np.max(np.abs(out)) / .7
wavfile.write(sys.argv[2] if len(sys.argv) > 2 else "music.wav", SR, (out * 32767).astype(np.int16))
