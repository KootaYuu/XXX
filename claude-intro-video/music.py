"""Synthesize a calm, warm background track for the intro video (numpy only).

Writes music.wav (44.1 kHz stereo) with a pad, bass, arpeggio and soft chimes
on each scene change. Length and scene cues match index.html.
"""
import pathlib
import sys
import wave

import numpy as np

SR = 44100
DURATION = 64.0
BAR = 3.0          # 80 BPM, 4/4
STEP = BAR / 8     # eighth notes
SCENE_CUES = [7, 15, 25, 35, 43, 51, 58]

# (bass root, pad voicing) in MIDI note numbers
CHORDS = [
    (48, [60, 64, 67, 71]),  # Cmaj7
    (45, [60, 64, 67, 69]),  # Am7
    (41, [60, 64, 65, 69]),  # Fmaj7
    (43, [59, 62, 67, 69]),  # G6
]
FINAL = (36, [55, 60, 64, 67, 71, 74])  # Cmaj9 ending

rng = np.random.default_rng(7)
N = int(SR * DURATION)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2)
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2)


def tone(freq, dur, partials=(1, .35, .15, .06), detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + detune)
    return sum(a * np.sin(2 * np.pi * f * (k + 1) * t + rng.uniform(0, 6.28)) for k, a in enumerate(partials))


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def pad(notes, start, dur, gain=.05):
    for m in notes:
        for det, pan in ((-.0018, -.6), (.0018, .6)):
            s = tone(hz(m), dur, detune=det)
            add(s * env_adsr(len(s), 1.0, 1.4) * gain, start, pan)


def bass(root, start, dur, gain=.16):
    s = tone(hz(root), dur, partials=(1, .25, .05))
    t = np.arange(len(s)) / SR
    add(s * np.exp(-t * .55) * env_adsr(len(s), .04, .6) * gain, start)


def pluck(m, start, gain=.07, pan=0.0, decay=3.2, dur=1.6):
    s = tone(hz(m), dur, partials=(1, .5, .22, .1, .04))
    t = np.arange(len(s)) / SR
    add(s * np.exp(-t * decay) * env_adsr(len(s), .004, .2) * gain, start, pan)


def chime(m, start, gain=.06):
    s = tone(hz(m), 4.0, partials=(1, 0, .3, 0, .12))
    t = np.arange(len(s)) / SR
    add(s * np.exp(-t * 1.1) * env_adsr(len(s), .005, .5) * gain, start, 0.2)


# --- arrangement -----------------------------------------------------------
ARP = [0, 1, 2, 3, 2, 1, 3, 2]
end_bar = int(58 // BAR)                     # progression runs until the outro
for b in range(end_bar + 1):
    t0 = b * BAR
    root, notes = CHORDS[b % len(CHORDS)]
    pad(notes, t0, BAR + 1.4, gain=.045 if t0 < 6 else .05)
    if t0 >= 6:
        bass(root, t0, BAR + .5)
    if t0 >= 3:
        for k, idx in enumerate(ARP):
            vel = .055 + .02 * (k % 4 == 0) + rng.uniform(-.008, .008)
            pluck(notes[idx] + 12, t0 + k * STEP, gain=vel, pan=-.35 + .1 * k)

# ending: sustained Cmaj9 with a slow arpeggio up
t_end = (end_bar + 1) * BAR
root, notes = FINAL
pad(notes, t_end, DURATION - t_end, gain=.045)
bass(root, t_end, DURATION - t_end, gain=.14)
for k, m in enumerate(notes):
    pluck(m + 12, t_end + .3 + k * .28, gain=.06, pan=-.5 + .2 * k, decay=1.4, dur=3.5)

for i, c in enumerate(SCENE_CUES):
    chime([84, 88, 91, 86][i % 4], c)

# --- reverb (convolution with a decaying-noise impulse) --------------------
ir_len = int(2.6 * SR)
t = np.arange(ir_len) / SR
ir_l = rng.standard_normal(ir_len) * np.exp(-t * 2.6)
ir_r = rng.standard_normal(ir_len) * np.exp(-t * 2.6)
ir_l[:int(.02 * SR)] = 0
ir_r[:int(.023 * SR)] = 0


def conv(x, h):
    n = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[:len(x)]
    return y / np.sqrt(np.sum(h ** 2))


wet = .32
L2 = L * (1 - wet) + conv(L, ir_l) * wet * .9
R2 = R * (1 - wet) + conv(R, ir_r) * wet * .9

# master fades + normalize
fade = np.ones(N)
fi, fo = int(1.2 * SR), int(4.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
out = np.stack([L2 * fade, R2 * fade], axis=1)
out = np.tanh(out / np.max(np.abs(out)) * 1.1) * .72

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "music.wav")
with wave.open(str(path), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("wrote", path)
