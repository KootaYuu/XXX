"""《书页里的人》原创配乐合成。

80 BPM，4/4 拍，1 小节 = 3 秒，共 75 小节（225 秒），与分镜时间轴逐小节对齐。
乐器全部用 numpy 合成：八音盒、钢琴、柔和铺底（pad）、铃声。
用法：python3 music.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 80
BEAT = 60.0 / BPM          # 0.75 s
BAR = BEAT * 4             # 3 s
TOTAL_BARS = 75
LENGTH = TOTAL_BARS * BAR + 4.0  # 结尾留出混响余韵

NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    """'C#5' -> 73"""
    pitch = NOTE_NAMES[name[0]]
    rest = name[1:]
    if rest.startswith("#"):
        pitch += 1
        rest = rest[1:]
    elif rest.startswith("b"):
        pitch -= 1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + pitch


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


CHORDS = {
    "C": ["C3", "E3", "G3"], "G": ["G2", "B2", "D3"], "Am": ["A2", "C3", "E3"],
    "F": ["F2", "A2", "C3"], "Dm": ["D3", "F3", "A3"], "E": ["E2", "G#2", "B2"],
    "Em": ["E2", "G2", "B2"], "Gsus": ["G2", "C3", "D3"], "Fmaj7": ["F2", "A2", "C3", "E3"],
    "A7": ["A2", "C#3", "E3", "G3"], "D": ["D3", "F#3", "A3"], "A": ["A2", "C#3", "E3"],
    "Bm": ["B2", "D3", "F#3"], "Dsus": ["D3", "G3", "A3"],
}


# ---------------------------------------------------------------- 乐器

def env_adsr(n, attack, decay_tau, release, sustain_len):
    t = np.arange(n) / SR
    e = np.exp(-t / decay_tau)
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    r0 = int(sustain_len * SR)
    if r0 < n:
        rl = n - r0
        e[r0:] *= np.linspace(1, 0, rl) ** 2
    return e


def music_box(f, dur, vel):
    n = int((dur + 2.2) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for ratio, amp, tau in [(1, 1.0, 1.1), (2.0, 0.28, 0.5), (3.0, 0.1, 0.3), (4.16, 0.08, 0.18), (5.43, 0.04, 0.1)]:
        sig += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / tau)
    a = int(0.003 * SR)
    sig[:a] *= np.linspace(0, 1, a)
    return sig * vel * 0.32


def piano(f, dur, vel):
    n = int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    base_tau = 1.6 * (261.0 / f) ** 0.35
    for k in range(1, 9):
        amp = 1.0 / k ** 1.4
        tau = base_tau / (1 + 0.45 * (k - 1))
        detune = 1 + 0.0004 * k * k
        sig += amp * np.sin(2 * np.pi * f * k * detune * t + k) * np.exp(-t / tau)
    sig *= env_adsr(n, 0.004, 1e9, 0, dur + 0.25)
    # 高音更亮，低音更柔
    return sig * vel * 0.22


def pad(f, dur, vel):
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for d in (-0.004, 0.0, 0.0045):
        ff = f * (1 + d)
        sig += np.sin(2 * np.pi * ff * t) + 0.25 * np.sin(2 * np.pi * 2 * ff * t) + 0.08 * np.sin(2 * np.pi * 3 * ff * t)
    e = np.ones(n)
    a = int(min(1.2, dur * 0.5) * SR)
    e[:a] = np.linspace(0, 1, a) ** 1.5
    r0 = int(dur * SR)
    e[r0:] = np.linspace(1, 0, n - r0) ** 2
    trem = 1 + 0.08 * np.sin(2 * np.pi * 0.25 * t)
    return sig * e * trem * vel * 0.035


def bell(f, dur, vel):
    n = int((dur + 3.5) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for ratio, amp, tau in [(1, 1.0, 2.5), (2.76, 0.5, 1.2), (5.4, 0.3, 0.6), (8.93, 0.15, 0.3), (0.5, 0.3, 3.0)]:
        sig += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / tau)
    return sig * vel * 0.16


INSTR = {"box": music_box, "piano": piano, "pad": pad, "bell": bell}


class Score:
    def __init__(self):
        self.L = np.zeros(int(LENGTH * SR) + SR)
        self.R = np.zeros_like(self.L)

    def note(self, instr, m, start, dur, vel=1.0, pan=0.0):
        if isinstance(m, str):
            m = midi(m)
        sig = INSTR[instr](freq(m), dur, vel)
        i = int(start * SR)
        j = min(len(self.L), i + len(sig))
        sig = sig[: j - i]
        self.L[i:j] += sig * np.sqrt(0.5 * (1 - pan))
        self.R[i:j] += sig * np.sqrt(0.5 * (1 + pan))

    def bar_t(self, bar, beat=0.0):
        return bar * BAR + beat * BEAT


# ---------------------------------------------------------------- 旋律素材
# (音名, 拍数)
THEME_A = [
    [("E5", 1), ("G5", 1), ("C6", 1.5), ("B5", 0.5)],
    [("D6", 1), ("B5", 1), ("G5", 2)],
    [("A5", 1), ("C6", 1), ("E6", 1.5), ("D6", 0.5)],
    [("C6", 1), ("A5", 1), ("F5", 1), ("G5", 1)],
]
THEME_B = [
    [("E5", 1), ("G5", 1), ("C6", 1), ("D6", 1)],
    [("E6", 1.5), ("D6", 0.5), ("B5", 2)],
    [("A5", 1), ("C6", 1), ("F6", 1), ("E6", 1)],
    [("D6", 2), ("B5", 1), ("G5", 1)],
]
SAD = [
    [("E5", 2), ("C5", 1), ("A4", 1)],
    [("F5", 2), ("E5", 1), ("C5", 1)],
    [("D5", 1.5), ("E5", 0.5), ("F5", 2)],
    [("E5", 3), ("G#4", 1)],
]
TENDER = [
    [("A5", 2), ("C6", 2)],
    [("G5", 2), ("E5", 2)],
    [("F5", 1), ("A5", 1), ("D6", 2)],
    [("B5", 3), ("D6", 1)],
]


def transpose(name, semis, octave=0):
    return midi(name) + semis + 12 * octave


def play_phrase(sc, bar, phrase_bar, instr, vel=1.0, semis=0, octave=0, pan=0.0, legato=1.0):
    beat = 0.0
    for name, dur in phrase_bar:
        sc.note(instr, transpose(name, semis, octave), sc.bar_t(bar, beat), dur * BEAT * legato, vel, pan)
        beat += dur


def bass(sc, bar, chord, vel=0.6, pattern="half"):
    root = midi(CHORDS[chord][0]) - 12
    if pattern == "half":
        sc.note("piano", root, sc.bar_t(bar, 0), BEAT * 2, vel, -0.2)
        sc.note("piano", root + 7, sc.bar_t(bar, 2), BEAT * 2, vel * 0.7, -0.2)
    else:
        sc.note("piano", root, sc.bar_t(bar, 0), BEAT * 4, vel, -0.2)


def arpeggio(sc, bar, chord, instr="piano", vel=0.35, octave=1, eighths=8, semis=0):
    tones = [midi(n) + 12 * octave + semis for n in CHORDS[chord]]
    seq = tones + [tones[0] + 12] + tones[::-1][1:]
    for i in range(eighths):
        sc.note(instr, seq[i % len(seq)], sc.bar_t(bar, i * 0.5), BEAT * 0.9, vel * (1.0 if i % 4 == 0 else 0.75), 0.25)


def block(sc, bar, chord, instr="piano", vel=0.3, octave=1, beats=4, semis=0, start_beat=0):
    for n in CHORDS[chord]:
        sc.note(instr, midi(n) + 12 * octave + semis, sc.bar_t(bar, start_beat), BEAT * beats, vel, 0.15)


def padchord(sc, bar, chord, bars=1, vel=1.0, semis=0):
    for n in CHORDS[chord]:
        sc.note("pad", midi(n) + 12 + semis, sc.bar_t(bar), BAR * bars, vel)


def compose():
    sc = Score()
    A_CH = ["C", "G", "Am", "F"]
    B_CH = ["C", "G", "F", "G"]

    # ---- 片头 bars 0-2：八音盒琶音
    for b, ch in zip(range(0, 3), ["C", "F", "Gsus"]):
        arpeggio(sc, b, ch, "box", 0.55, octave=2)
    sc.note("box", "G5", sc.bar_t(2, 3), BEAT, 0.5)

    # ---- 第一章 bars 3-17
    sc.note("box", "C6", sc.bar_t(3), BAR, 0.7)
    arpeggio(sc, 3, "C", "box", 0.3, octave=2)
    for i in range(4):                       # 4-7 主题 A
        play_phrase(sc, 4 + i, THEME_A[i], "box", 0.85)
        bass(sc, 4 + i, A_CH[i], 0.45)
    for i in range(4):                       # 8-11 主题 B
        play_phrase(sc, 8 + i, THEME_B[i], "box", 0.85)
        bass(sc, 8 + i, B_CH[i], 0.45)
    for i in range(4):                       # 12-15 主题 A + 琶音
        play_phrase(sc, 12 + i, THEME_A[i], "box", 0.85)
        arpeggio(sc, 12 + i, A_CH[i], "piano", 0.22, octave=1)
        bass(sc, 12 + i, A_CH[i], 0.4, "whole")
    sc.note("box", "C6", sc.bar_t(16), BAR, 0.8)
    arpeggio(sc, 16, "C", "piano", 0.22)
    bass(sc, 16, "C", 0.4, "whole")
    arpeggio(sc, 17, "F", "box", 0.35, octave=2, eighths=4)
    arpeggio(sc, 17, "G", "box", 0.35, octave=2, eighths=4)

    # ---- 第二章 bars 18-32：加入钢琴与铺底，更甜
    padchord(sc, 18, "C")
    arpeggio(sc, 18, "C", "piano", 0.28)
    bass(sc, 18, "C", 0.45, "whole")
    for i in range(4):                       # 19-22 主题 A
        play_phrase(sc, 19 + i, THEME_A[i], "piano", 0.75, octave=-1, pan=0.1)
        play_phrase(sc, 19 + i, THEME_A[i], "box", 0.4)
        arpeggio(sc, 19 + i, A_CH[i], "piano", 0.2)
        bass(sc, 19 + i, A_CH[i], 0.45)
        padchord(sc, 19 + i, A_CH[i], vel=0.8)
    for i in range(3):                       # 23-25 主题 B 前三小节
        play_phrase(sc, 23 + i, THEME_B[i], "piano", 0.75, octave=-1, pan=0.1)
        play_phrase(sc, 23 + i, THEME_B[i], "box", 0.4)
        arpeggio(sc, 23 + i, B_CH[i], "piano", 0.2)
        bass(sc, 23 + i, B_CH[i], 0.45)
        padchord(sc, 23 + i, B_CH[i], vel=0.8)
    # 26-28 楼梯口：闭馆铃、屏息
    sc.note("bell", "G5", sc.bar_t(26, 0.4), 1.0, 0.9)
    sc.note("bell", "G5", sc.bar_t(26, 1.4), 1.0, 0.6)
    padchord(sc, 26, "Fmaj7", bars=2, vel=0.9)
    sc.note("piano", "E5", sc.bar_t(27, 0), BEAT * 2, 0.35)
    sc.note("piano", "D5", sc.bar_t(27, 2), BEAT * 2, 0.3)
    padchord(sc, 28, "Gsus", vel=0.9)
    sc.note("piano", "C5", sc.bar_t(28, 0), BEAT * 3, 0.3)
    sc.note("piano", "B4", sc.bar_t(28, 3), BEAT, 0.3)
    # 29 点头！
    for k, n in enumerate(["C5", "E5", "G5", "C6", "E6", "G6"]):
        sc.note("box", n, sc.bar_t(29, k * 0.25), BAR, 0.6)
    block(sc, 29, "C", "piano", 0.35)
    padchord(sc, 29, "C")
    bass(sc, 29, "C", 0.5, "whole")
    for i in range(3):                       # 30-32 甜蜜
        play_phrase(sc, 30 + i, THEME_A[i], "piano", 0.8, octave=-1, pan=0.1)
        play_phrase(sc, 30 + i, THEME_A[i], "box", 0.55)
        arpeggio(sc, 30 + i, A_CH[i], "piano", 0.24)
        bass(sc, 30 + i, A_CH[i], 0.5)
        padchord(sc, 30 + i, A_CH[i])

    # ---- 第三章 bars 33-44：音乐骤停，小调
    sc.note("piano", "A1", sc.bar_t(33, 1), BAR * 2, 0.4)
    sc.note("piano", "E2", sc.bar_t(33, 1), BAR * 2, 0.25)
    sad_ch = ["Am", "F", "Dm", "E"]
    for i, b in enumerate(range(34, 38)):    # 稀疏单音
        name, _ = SAD[i][0]
        sc.note("piano", name, sc.bar_t(b), BAR, 0.45)
        sc.note("piano", midi(CHORDS[sad_ch[i]][0]) - 12, sc.bar_t(b), BAR, 0.3)
    for i in range(4):                       # 38-41 完整小调旋律
        play_phrase(sc, 38 + i, SAD[i], "piano", 0.55)
        block(sc, 38 + i, sad_ch[i], "piano", 0.18, octave=0, beats=2)
        block(sc, 38 + i, sad_ch[i], "piano", 0.14, octave=0, beats=2, start_beat=2)
        bass(sc, 38 + i, sad_ch[i], 0.35, "whole")
        padchord(sc, 38 + i, sad_ch[i], vel=0.5)
    for i, (b, ch) in enumerate(zip(range(42, 45), ["Am", "F", "E"])):
        play_phrase(sc, b, SAD[[0, 1, 3][i]][:1], "piano", 0.4 - 0.08 * i)
        bass(sc, b, ch, 0.28 - 0.05 * i, "whole")
        padchord(sc, b, ch, vel=0.4)

    # ---- 第四章 bars 45-59
    padchord(sc, 45, "Am", vel=0.6)
    sc.note("piano", "A4", sc.bar_t(45), BAR, 0.3)
    for b, ch, mel in [(46, "Dm", ["A5", "C6", "D6"]), (47, "F", ["C6", "D6", "F6"])]:
        padchord(sc, b, ch, vel=0.6)
        for k, n in enumerate(mel):
            sc.note("box", n, sc.bar_t(b, k), BEAT * 1.5, 0.5)
    for b, ch in [(48, "Dm"), (49, "E")]:   # 等待：钟摆般的滴答
        padchord(sc, b, ch, vel=0.5)
        for k in range(8):
            sc.note("piano", "A4" if k % 2 == 0 else "E4", sc.bar_t(b, k * 0.5), BEAT * 0.3, 0.16)
    for k, n in enumerate(["F4", "A4", "C5", "F5", "A5", "C6"]):   # 50 揭晓：温暖
        sc.note("box", n, sc.bar_t(50, k * 0.3), BAR, 0.45)
    padchord(sc, 50, "F")
    bass(sc, 50, "F", 0.4, "whole")
    t_ch = ["F", "C", "Dm", "G"]
    for i in range(4):                       # 51-54 回忆：温柔
        play_phrase(sc, 51 + i, TENDER[i], "piano", 0.6, octave=-1)
        arpeggio(sc, 51 + i, t_ch[i], "piano", 0.18)
        bass(sc, 51 + i, t_ch[i], 0.35, "whole")
        padchord(sc, 51 + i, t_ch[i], vel=0.8)
    for i in range(4):                       # 55-58 真相：渐强
        v = 0.6 + 0.1 * i
        play_phrase(sc, 55 + i, TENDER[i], "piano", v, octave=-1)
        play_phrase(sc, 55 + i, TENDER[i], "box", v * 0.6)
        arpeggio(sc, 55 + i, t_ch[i], "piano", 0.2 + 0.03 * i)
        bass(sc, 55 + i, t_ch[i], 0.45)
        padchord(sc, 55 + i, t_ch[i], vel=1.0 + 0.1 * i)
    padchord(sc, 59, "Gsus", vel=1.2)
    block(sc, 59, "Gsus", "piano", 0.3, beats=4)
    sc.note("box", "D6", sc.bar_t(59), BAR, 0.5)

    # ---- 第五章 bars 60-74
    sc.note("piano", "A4", sc.bar_t(60, 1), BAR, 0.3)
    padchord(sc, 60, "Am", vel=0.5)
    for b, ch, n in [(61, "Am", "E5"), (62, "F", "C5"), (63, "G", "D5")]:
        sc.note("piano", n, sc.bar_t(b), BEAT * 2, 0.4)
        sc.note("piano", midi(n) - 2 if ch != "Am" else midi("C5"), sc.bar_t(b, 2), BEAT * 2, 0.3)
        bass(sc, b, ch, 0.3, "whole")
        padchord(sc, b, ch, vel=0.5)
    for i in range(3):                       # 64-66 借书卡：主题单音重现
        beat = 0.0
        for name, dur in THEME_A[i]:
            sc.note("piano", midi(name) - 12, sc.bar_t(64 + i, beat), dur * BEAT, 0.45)
            beat += dur
        bass(sc, 64 + i, A_CH[i], 0.3, "whole")
        padchord(sc, 64 + i, A_CH[i], vel=0.6)
    # 67 还书车轮子：上行，转向 D 大调
    padchord(sc, 67, "A7", vel=0.8)
    for k, n in enumerate(["A3", "C#4", "E4", "G4", "A4", "C#5", "E5", "G5"]):
        sc.note("piano", n, sc.bar_t(67, k * 0.5), BEAT, 0.3 + 0.03 * k)
    d_ch = ["D", "A", "Bm", "G"]
    for i in range(4):                       # 68-71 D 大调全编制高潮
        play_phrase(sc, 68 + i, THEME_A[i], "piano", 0.85, semis=2, octave=-1, pan=0.1)
        play_phrase(sc, 68 + i, THEME_A[i], "box", 0.6, semis=2)
        arpeggio(sc, 68 + i, d_ch[i], "piano", 0.26)
        bass(sc, 68 + i, d_ch[i], 0.55)
        padchord(sc, 68 + i, d_ch[i], vel=1.2)
    sc.note("bell", "A5", sc.bar_t(71, 0), 1.0, 0.7)
    sc.note("bell", "D6", sc.bar_t(71, 2), 1.0, 0.5)
    # 72-74 尾奏：八音盒
    play_phrase(sc, 72, THEME_B[0], "box", 0.7, semis=2)
    padchord(sc, 72, "D", vel=0.8)
    bass(sc, 72, "D", 0.35, "whole")
    play_phrase(sc, 73, [("F#6", 1.5), ("E6", 0.5), ("C#6", 2)], "box", 0.65)
    padchord(sc, 73, "A", vel=0.7)
    bass(sc, 73, "A", 0.3, "whole")
    for k, n in enumerate(["D5", "F#5", "A5", "D6"]):
        sc.note("box", n, sc.bar_t(74, k * 0.5), BAR + 2, 0.55)
    padchord(sc, 74, "D", bars=1.6, vel=0.7)
    sc.note("piano", "D3", sc.bar_t(74), BAR + 2, 0.35)
    return sc


def reverb(x, seconds=2.4, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
    # 柔化高频：简单滑动平均低通
    k = 6
    ir = np.convolve(ir, np.ones(k) / k, mode="same")
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y


def render(path):
    sc = compose()
    out = []
    for ch, seed in ((sc.L, 1), (sc.R, 2)):
        wet = reverb(ch, seed=seed)
        out.append(ch * 0.8 + wet * 0.35)
    stereo = np.stack(out, axis=1)
    n_total = int((TOTAL_BARS * BAR + 3.0) * SR)
    stereo = stereo[:n_total]
    fade = int(3.0 * SR)
    stereo[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    # 淡入
    fi = int(0.05 * SR)
    stereo[:fi] *= np.linspace(0, 1, fi)[:, None]
    peak = np.max(np.abs(stereo))
    stereo = np.tanh(stereo / peak * 1.1) / np.tanh(1.1) * 0.89
    data = (stereo * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "music.wav")
