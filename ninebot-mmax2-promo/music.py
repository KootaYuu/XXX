"""Synthesize the 128 BPM soundtrack for the MMAX2 promo (numpy + scipy).

Writes music.wav (44.1 kHz stereo). Every hit lands on the section cuts in index.html:
ignition (heartbeat, check blips, motor whine) -> reveal (half-time) -> drop at bar 3
-> full groove with risers + impacts per section, zaps on each feature / colour swap
-> snare-roll build -> finale impact + chord stab -> ring out.
"""
import pathlib
import sys
import wave

import numpy as np
from scipy import signal

SR = 44100
DURATION = 32.0
N = int(SR * DURATION)
BPM = 128
BEAT = 60 / BPM
BAR = 4 * BEAT
bar = lambda n: n * BAR
beat = lambda n: n * BEAT
SEC = dict(reveal=bar(1), range=bar(3), ride=bar(5), safe=bar(7), smart=bar(9), feat=bar(10), build=bar(12), color=bar(13), fin=bar(14))
rng = np.random.default_rng(12)

# E minor: Em - C - D - Bm (one bar each)
PROG = [(40, [64, 67, 71, 74]), (36, [64, 67, 72, 76]), (38, [66, 69, 74, 78]), (35, [66, 71, 74, 78])]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Bus:
    def __init__(self):
        self.x = np.zeros((N, 2))

    def add(self, sig, start, pan=0.0, gain=1.0):
        i = int(round(start * SR))
        if i >= N or i + len(sig) <= 0:
            return
        if i < 0:
            sig, i = sig[-i:], 0
        sig = sig[: N - i] * gain
        self.x[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
        self.x[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)


def tvec(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def adsr(n, a, r, curve=1.5):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def saw(freq, d, cutoff=4000.0, maxh=40, detune=0.0):
    t = tvec(d)
    f = freq * (1 + detune)
    out = np.zeros_like(t)
    for k in range(1, maxh + 1):
        if k * f > 16000:
            break
        a = (1 / k) / (1 + (k * f / cutoff) ** 4)
        if a < 1e-4:
            break
        out += a * np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28))
    return out


def fm_sweep(f0, f1, d, shape=2.0):
    """Saw-ish tone whose pitch glides f0 -> f1 (used for motor whine and zaps)."""
    t = tvec(d)
    f = f0 * (f1 / f0) ** ((t / d) ** shape)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return sum(np.sin(k * ph) / k for k in range(1, 9))


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "bandpass", output="sos"), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), "highpass", output="sos"), x)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), "lowpass", output="sos"), x)


def sweep_filter(x, f0, f1, shape=2.0, chunk=512):
    y, zi, n = np.zeros_like(x), None, len(x)
    for s in range(0, n, chunk):
        fc = f0 * (f1 / f0) ** ((s / max(1, n - 1)) ** shape)
        sos = signal.butter(2, min(fc, SR / 2 * .95) / (SR / 2), "lowpass", output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        y[s:s + chunk], zi = signal.sosfilt(sos, x[s:s + chunk], zi=zi)
    return y


drums, bass, synth, fx, pad = Bus(), Bus(), Bus(), Bus(), Bus()
kick_times = []


def kick(at, gain=.6):
    d = .42
    t = tvec(d)
    f = 160 * np.exp(-t * 30) + 44
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = hp(noise(d), 2500) * np.exp(-t * 200) * .35
    drums.add(np.tanh((body + click) * 1.8), at, gain=gain)
    kick_times.append(at)


def clap(at, gain=.32):
    d = .22
    t = tvec(d)
    env = np.exp(-t * 20)
    for off in (0, .008, .017):   # three quick bursts = clap
        env[int(off * SR):] += np.exp(-(t[: len(t) - int(off * SR)]) * 60) * .6
    drums.add(bp(noise(d), 900, 6000) * env, at, pan=-.05, gain=gain)


def hat(at, open_=False, gain=.1, pan=.2):
    d = .2 if open_ else .05
    drums.add(hp(noise(d), 7500, 4) * np.exp(-tvec(d) * (14 if open_ else 80)), at, pan=pan, gain=gain)


def impact(at, gain=.9, size=1.0):
    d = 2.0 * size
    t = tvec(d)
    f = 80 * np.exp(-t * 7) + 36
    fx.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2 / size), at, gain=gain)
    fx.add(lp(noise(d), 3000) * np.exp(-t * 8), at, gain=.35 * gain)
    fx.add(hp(noise(.04), 3000) * np.exp(-tvec(.04) * 110), at, gain=.5 * gain)


def riser(end, length, gain=.22):
    r = sweep_filter(noise(length), 300, 10000, shape=1.5) * np.linspace(0, 1, int(length * SR)) ** 2.2
    fx.add(r, end - length, gain=gain)


def zap(at, gain=.14, up=False):
    d = .14
    s = fm_sweep(3000, 300, d, 1.0) if not up else fm_sweep(300, 2400, d, 1.0)
    fx.add(s * adsr(len(s), .002, .08), at, pan=rng.uniform(-.4, .4), gain=gain)


def stab(at, notes, gain=.07, d=.35, cutoff=3500):
    for m in notes:
        for det, pan in ((-.006, -.6), (.006, .6)):
            s = saw(hz(m), d, cutoff=cutoff, maxh=26, detune=det)
            synth.add(s * adsr(len(s), .004, d * .8, 2.4), at, pan=pan, gain=gain)


def chord_at(t):
    return PROG[int(t // BAR) % len(PROG)]


# ---------------- ignition: heartbeat, check blips, motor whine ----------------
for b in (0.0, beat(2)):
    kick(b + .2, gain=.35)
    kick(b + .2 + beat(.4), gain=.22)
for k in range(4):
    s = np.sin(2 * np.pi * 2200 * tvec(.05)) * adsr(int(.05 * SR), .002, .03)
    fx.add(s, .28 * (k + 1), pan=-.3 + .2 * k, gain=.12)
whine = fm_sweep(90, 900, 1.0, 1.6) * np.linspace(0, 1, int(SR)) ** 1.5
fx.add(lp(whine, 5000), SEC["reveal"] - 1.0, gain=.16)
riser(SEC["reveal"], .8, gain=.25)
impact(SEC["reveal"], gain=1.0)

# ---------------- reveal: half-time with title hits ----------------
t = SEC["reveal"]
while t < SEC["range"] - 1e-6:
    kick(t, .55)
    clap(t + beat(2))
    for k in range(8):
        hat(t + beat(k / 2 + .5), gain=.07)
    root, _ = chord_at(t)
    for k in range(8):   # filtered 8th bass, opening up
        cut = 300 + 1500 * (t - SEC["reveal"]) / (SEC["range"] - SEC["reveal"])
        s = saw(hz(root - 12), BEAT / 2, cutoff=cut, maxh=20) * adsr(int(BEAT / 2 * SR), .004, .08)
        bass.add(s, t + beat(k / 2), gain=.38)
    t += BAR
# beat 3: line drawing cuts to the real bike; beats 4, 5, 7: title slams
riser(SEC["reveal"] + beat(3), beat(2), gain=.18)
impact(SEC["reveal"] + beat(3), gain=.8, size=.8)
for b in (4, 5, 7):
    impact(SEC["reveal"] + beat(b), gain=.45, size=.5)
    stab(SEC["reveal"] + beat(b), chord_at(SEC["reveal"] + beat(b))[1], gain=.05)
riser(SEC["range"], BAR, gain=.3)
# snare fill into the drop
for k in range(8):
    clap(SEC["range"] - beat(2) + beat(k / 4), gain=.12 + .03 * k)

# ---------------- main groove (drop -> finale) ----------------
def groove(a, b, kick_until=None):
    t = a
    while t < b - 1e-6:
        root, notes = chord_at(t)
        for k in range(4):
            bt = t + beat(k)
            if kick_until is None or bt < kick_until:
                kick(bt, .62)
            if k in (1, 3):
                clap(bt)
            hat(bt + beat(.5), open_=True, gain=.08, pan=.25)
            for q in (.25, .75):
                hat(bt + beat(q), gain=.05, pan=-.25)
            for q in (.5,):   # offbeat rolling bass
                s = saw(hz(root - 12), BEAT * .45, cutoff=900, maxh=24) * adsr(int(BEAT * .45 * SR), .003, .12)
                bass.add(s, bt + beat(q), gain=.45)
            s = np.sin(2 * np.pi * hz(root - 24) * tvec(BEAT * .9)) * adsr(int(BEAT * .9 * SR), .003, .3)
            bass.add(s, bt, gain=.25)
        # 16th arp on the top of the chord
        for k in range(16):
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
            s = saw(hz(m), .1, cutoff=2600 + 1200 * np.sin(t), maxh=18) * adsr(int(.1 * SR), .002, .07, 2.2)
            synth.add(s, t + beat(k / 4), pan=.4 * np.sin(k), gain=.045)
        t += BAR


groove(SEC["range"], SEC["color"])
groove(SEC["color"], SEC["fin"], kick_until=SEC["fin"] - beat(2))
for key in ("range", "ride", "safe", "smart", "build"):
    impact(SEC[key], gain=.85 if key == "range" else .6)
    stab(SEC[key], chord_at(SEC[key])[1], gain=.07)
    if key != "range":
        riser(SEC[key], .9, gain=.16)
# motor whine as the bike starts riding
fx.add(lp(fm_sweep(120, 1400, 1.4, 1.3), 6000) * np.linspace(1, 0, int(1.4 * SR)) ** .5, SEC["ride"], gain=.12)
# statement hits during the ride and safety sections
for k in (1, 2):
    impact(SEC["ride"] + beat(k * 2.667), gain=.35, size=.4)
for k in (1, 2, 3):
    impact(SEC["safe"] + beat(k * 2), gain=.3, size=.4)
# smart: UI cards + features
for k in range(3):
    zap(SEC["smart"] + .3 + beat(k * 1.2), gain=.1, up=True)
for k in range(6):
    zap(SEC["feat"] + beat(k), gain=.15)
# build: colour swaps + snare roll into the finale
for k in range(3):
    zap(SEC["color"] + beat(k * 1.333), gain=.14, up=True)
roll_t, step = SEC["color"] + beat(2), beat(.5)
while roll_t < SEC["fin"] - 1e-6:
    clap(roll_t, gain=.1 + .2 * (roll_t - SEC["color"]) / BAR)
    roll_t += step
    if roll_t > SEC["fin"] - beat(1):
        step = beat(.125)
    elif roll_t > SEC["color"] + beat(3):
        step = beat(.25)
riser(SEC["fin"], BAR, gain=.34)

# ---------------- finale ----------------
impact(SEC["fin"], gain=1.15, size=1.5)
stab(SEC["fin"], [52, 59, 64, 67, 71, 74, 78], gain=.07, d=1.2, cutoff=5000)
groove(SEC["fin"], SEC["fin"] + bar(2))
for k in (1, 2, 4):
    impact(SEC["fin"] + beat(k), gain=.35, size=.5)
end_t = SEC["fin"] + bar(2)
for m in (40, 52, 59, 64, 67, 71, 74):
    for det, pan in ((-.005, -.7), (.005, .7)):
        s = saw(hz(m), DURATION - end_t, cutoff=1800, maxh=16, detune=det)
        pad.add(s * adsr(len(s), .02, 2.2, 2), end_t, pan=pan, gain=.04)
kick(end_t, .7)
impact(end_t, gain=.6, size=1.2)

# ---------------- sidechain, reverb, master ----------------
duck = np.ones(N)
for kt in kick_times:
    i, n = int(kt * SR), int(.25 * SR)
    seg = 1 - .65 * np.exp(-tvec(.25) * 16)
    duck[i:i + n] = np.minimum(duck[i:i + n], seg[: len(duck[i:i + n])])
for b_ in (bass, synth, pad):
    b_.x *= duck[:, None]


def reverb(x, secs=2.2, decay=2.6):
    n, t = int(secs * SR), tvec(secs)
    out = np.zeros_like(x)
    for ch in range(2):
        ir = lp(rng.standard_normal(n) * np.exp(-t * decay), 6000)
        ir[: int(.015 * SR) + ch * 50] = 0
        out[:, ch] = signal.fftconvolve(x[:, ch], ir / np.sqrt(np.sum(ir ** 2)))[: len(x)]
    return out


mix = drums.x + bass.x + synth.x + fx.x + pad.x + reverb(synth.x * .5 + fx.x * .4 + pad.x * .6 + drums.x * .08) * .4
dly = int(BEAT * .75 * SR)
mix[dly:, 0] += synth.x[:-dly, 1] * .28
mix[2 * dly:, 1] += synth.x[:-2 * dly, 0] * .2
fade = np.ones(N)
fade[: int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
fo = int(1.6 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
mix = hp((mix * fade[:, None]).T, 28).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 2.0) / np.tanh(2.0) * .89

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "music.wav")
with wave.open(str(path), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", path)
