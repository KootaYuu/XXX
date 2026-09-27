"""Synthesize an electronic score for the intro video (numpy + scipy).

Writes music.wav (44.1 kHz stereo). Structure follows index.html:
boot blips -> warp riser + impact (3.4s) -> pulse arp -> groove with kick/hats/sub
-> risers into every scene cut + impacts on the cut -> breakdown (50-56s)
-> final build into the collapse at 59.1s -> ring out.
"""
import pathlib
import sys
import wave

import numpy as np
from scipy import signal

SR = 44100
DURATION = 64.0
N = int(SR * DURATION)
BPM = 120
BEAT = 60 / BPM
CUTS = [8, 16, 26, 35, 43, 50, 56]
WARP = 3.4
COLLAPSE = 59.1
GROOVE = (8.0, 50.0)          # kick + hats
BREAK = (50.0, 56.0)
rng = np.random.default_rng(3)

# A minor: Am - F - C - G, 2 bars (4 s) each
PROG = [(45, [57, 60, 64, 67]), (41, [57, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
FINAL = (45, [57, 64, 67, 71, 72, 76])   # Am(add9) wash


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


def tvec(dur):
    return np.arange(int(dur * SR)) / SR


def saw(freq, dur, cutoff=4000.0, maxh=40, detune=0.0):
    t = tvec(dur)
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


def adsr(n, a, r, curve=1.5):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def sweep_filter(x, f0, f1, btype="lowpass", order=2, chunk=512, shape=2.0):
    """Time-varying Butterworth filter, cutoff moves exponentially from f0 to f1."""
    y = np.zeros_like(x)
    n = len(x)
    zi = None
    for s in range(0, n, chunk):
        k = (s / max(1, n - 1)) ** shape
        fc = f0 * (f1 / f0) ** k
        sos = signal.butter(order, min(fc, SR / 2 * .95) / (SR / 2), btype=btype, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        y[s:s + chunk], zi = signal.sosfilt(sos, x[s:s + chunk], zi=zi)
    return y


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), "highpass", output="sos"), x)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), "lowpass", output="sos"), x)


pad, arp, drums, fx, sub = Bus(), Bus(), Bus(), Bus(), Bus()


def chord_at(t):
    return PROG[int(t // 4) % len(PROG)]


# ---------------- boot: drone + data blips ----------------
drone = saw(hz(33), WARP + .6, cutoff=300, detune=0) + saw(hz(45), WARP + .6, cutoff=500, detune=.003)
drone *= adsr(len(drone), 1.2, .5) * np.linspace(.5, 1, len(drone))
pad.add(drone, 0, gain=.18)
t_b = .3
while t_b < 2.9:
    f = rng.choice([1760, 2093, 2349, 2637, 3136])
    d = .035
    s = np.sin(2 * np.pi * f * tvec(d)) * adsr(int(d * SR), .002, .02)
    fx.add(s, t_b, pan=rng.uniform(-.6, .6), gain=.10)
    t_b += rng.choice([.0625, .125, .125, .25])

# ---------------- risers + impacts ----------------
def riser(end, length, gain=.22):
    d = length
    n = noise(d)
    r = sweep_filter(n, 300, 9000, "lowpass", shape=1.6) * np.linspace(0, 1, int(d * SR)) ** 2.2
    tone = saw(hz(57), d, cutoff=2500, maxh=20)
    ft = np.linspace(0, 1, len(tone)) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(hz(45) * 2 ** (ft * 2)) / SR) * ft * .5
    fx.add((r * .7 + tone * .5), end - d, gain=gain)


def impact(at, gain=.9, size=1.0):
    d = 2.2 * size
    t = tvec(d)
    f = 70 * np.exp(-t * 6) + 34
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8 / size)
    sub.add(boom, at, gain=gain)
    burst = lp(noise(d), 2500) * np.exp(-t * 7)
    fx.add(burst, at, gain=.35 * gain)
    click = hp(noise(.03), 3000) * np.exp(-tvec(.03) * 120)
    fx.add(click, at, gain=.5 * gain)


riser(WARP, 1.6, gain=.28)
impact(WARP, gain=1.0)
for c in CUTS:
    riser(c, 1.1, gain=.16)
    impact(c, gain=.75 if c != 56 else .9)
riser(COLLAPSE, 3.0, gain=.34)
impact(COLLAPSE, gain=1.1, size=1.6)

# ---------------- pads (warp -> collapse) ----------------
t0 = WARP
while t0 < COLLAPSE:
    bar_start = (t0 // 4) * 4
    end = min(bar_start + 4, COLLAPSE)
    dur = end - t0
    root, notes = chord_at(t0 + 1e-3)
    for m in notes:
        for det, pan in ((-.004, -.7), (0, 0), (.004, .7)):
            s = saw(hz(m), dur + 1.0, cutoff=900 if not (BREAK[0] <= t0 < BREAK[1]) else 1600, maxh=16, detune=det)
            pad.add(s * adsr(len(s), .5 if t0 > WARP + .1 else .02, 1.0), t0, pan=pan, gain=.035)
    t0 = end

# final wash
root, notes = FINAL
for m in notes:
    for det, pan in ((-.005, -.8), (.005, .8)):
        s = saw(hz(m), DURATION - COLLAPSE, cutoff=2200, maxh=18, detune=det)
        pad.add(s * adsr(len(s), .02, 3.5, 2), COLLAPSE, pan=pan, gain=.04)
s = np.sin(2 * np.pi * hz(33) * tvec(DURATION - COLLAPSE)) * adsr(int((DURATION - COLLAPSE) * SR), .02, 3.5)
sub.add(s, COLLAPSE, gain=.35)
# sparkle arpeggio on the ending
for k, m in enumerate([69, 72, 76, 79, 81, 84, 88]):
    d = 1.4
    s = saw(hz(m + 12), d, cutoff=6000, maxh=10) * np.exp(-tvec(d) * 3.5)
    arp.add(s, COLLAPSE + .45 + k * .125, pan=-.6 + .2 * k, gain=.05)

# ---------------- pulse arp (16ths) ----------------
PAT = [0, 2, 1, 3, 2, 1, 3, 0, 0, 2, 1, 3, 2, 3, 1, 2]
step = BEAT / 4
t = WARP
k = 0
while t < 58.6:
    root, notes = chord_at(t)
    m = notes[PAT[k % 16]] + 12 + (12 if k % 8 == 6 else 0)
    in_break = BREAK[0] <= t < BREAK[1]
    base_cut = 900 + 2600 * (.5 + .5 * np.sin(t * .35))
    d = .16
    s = saw(hz(m), d, cutoff=base_cut * (1.6 if in_break else 1), maxh=24) * adsr(int(d * SR), .002, .12, 2.2)
    acc = 1.25 if k % 4 == 0 else 1.0
    arp.add(s, t, pan=.45 * np.sin(k * .7), gain=.09 * acc * (.55 if t < 8 else 1))
    t += step
    k += 1

# ---------------- drums + sub bass ----------------
kick_times = []
b = GROOVE[0]
while b < GROOVE[1] - 1e-6:
    kick_times.append(b)
    b += BEAT
b = 56.0
while b < COLLAPSE - 1.0:           # re-entry build: kicks accelerate into the collapse
    kick_times.append(b)
    b += BEAT if b < 57.5 else BEAT / 2


def kick():
    d = .45
    t = tvec(d)
    f = 150 * np.exp(-t * 28) + 46
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = hp(noise(d), 2000) * np.exp(-t * 180) * .4
    return np.tanh((body + click) * 1.6)


K = kick()
for kt in kick_times:
    drums.add(K, kt, gain=.55)
    # offbeat hat
    h = hp(noise(.06), 7000, 4) * np.exp(-tvec(.06) * 70)
    drums.add(h, kt + BEAT / 2, pan=.25, gain=.14)
    if int(round(kt / BEAT)) % 4 == 2:        # clap-ish snare on 2 & 4 feel (every other beat)
        sn = signal.sosfilt(signal.butter(2, [900 / (SR / 2), 5000 / (SR / 2)], "bandpass", output="sos"), noise(.18)) * np.exp(-tvec(.18) * 22)
        drums.add(sn, kt, pan=-.1, gain=.35)
# 16th shaker texture during groove
t = GROOVE[0]
k = 0
while t < GROOVE[1]:
    if k % 4 != 0:
        h = hp(noise(.03), 9000, 4) * np.exp(-tvec(.03) * 140)
        drums.add(h, t, pan=-.35, gain=.05 * (1.4 if k % 2 else 1))
    t += BEAT / 4
    k += 1

# sub bass: 8ths on root during groove, long notes in the break
t = GROOVE[0]
while t < 58.6:
    root, _ = chord_at(t)
    in_break = BREAK[0] <= t < BREAK[1]
    d = BEAT / 2 if not in_break else 2.0
    s = np.sin(2 * np.pi * hz(root - 12) * tvec(d)) + .25 * np.sin(2 * np.pi * hz(root) * tvec(d))
    s *= adsr(len(s), .005, .05 if not in_break else .8)
    sub.add(s, t, gain=.30 if not in_break else .22)
    t += d

# ---------------- sidechain ----------------
duck = np.ones(N)
for kt in kick_times:
    i = int(kt * SR)
    n = int(.3 * SR)
    seg = 1 - .6 * np.exp(-tvec(.3) * 14)
    duck[i:i + n] = np.minimum(duck[i:i + n], seg[: len(duck[i:i + n])])
for bus in (pad, arp, sub):
    bus.x *= duck[:, None]

# ---------------- reverb + mix ----------------
def reverb(x, secs=2.8, decay=2.2, pre=.02):
    n = int(secs * SR)
    t = tvec(secs)
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * decay)
        ir[:int(pre * SR) + ch * 40] = 0
        ir = lp(ir, 6000)
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, ch] = signal.fftconvolve(x[:, ch], ir)[:len(x)]
    return out


wet_src = pad.x * .6 + arp.x * .5 + fx.x * .5
mix = pad.x + arp.x + drums.x + fx.x + sub.x + reverb(wet_src) * .45
# delay on arp (dotted eighth ping-pong)
dly = int(BEAT * .75 * SR)
echo = np.zeros_like(arp.x)
echo[dly:, 0] = arp.x[:-dly, 1] * .35
echo[2 * dly:, 1] = arp.x[:-2 * dly, 0] * .25
mix += echo

fade = np.ones(N)
fi, fo = int(.3 * SR), int(3.5 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
mix *= fade[:, None]
mix = hp(mix.T, 25).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.8) / np.tanh(1.8) * .89

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "music.wav")
with wave.open(str(path), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", path)
