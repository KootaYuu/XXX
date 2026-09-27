"""渲染《书页里的人》。

用法：
  python3 render.py preview 12.5 30 88      # 渲染指定秒数的静帧到 build/preview_*.png
  python3 render.py sheet                   # 每个镜头取 3 帧拼成联系表
  python3 render.py full                    # 渲染完整视频 build/书页里的人.mp4
"""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import skia

import music
from scenes import SHOTS, TOTAL
from sketch import FPS, H, W, begin, draw_paper, xf

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.environ.get("STORY_BUILD", os.path.join(HERE, "build"))
XFADE = 0.5
FONT_URL = "https://github.com/lxgw/LxgwWenKai/releases/download/v1.330/LXGWWenKai-Regular.ttf"


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def ensure_font():
    from sketch import FONT_PATH
    if not os.path.exists(FONT_PATH):
        os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
        subprocess.check_call(["curl", "-sSL", "-o", FONT_PATH, FONT_URL])


STARTS = []
_acc = 0.0
for _name, _d, _f in SHOTS:
    STARTS.append(_acc)
    _acc += _d


def locate(T):
    for i, s in enumerate(STARTS):
        if T < s + SHOTS[i][1]:
            return i, T - s
    return len(SHOTS) - 1, SHOTS[-1][1] - 1e-3


def draw_shot(i, t, frame):
    name, d, f = SHOTS[i]
    begin(G_CANVAS[0], frame, salt=i)
    draw_paper()
    f(max(0.0, min(d, t)), d)


G_CANVAS = [None]


def render_frame(frame, surface=None):
    surface = surface or skia.Surface(W, H)
    canvas = surface.getCanvas()
    G_CANVAS[0] = canvas
    T = frame / FPS
    i, t = locate(T)
    d = SHOTS[i][1]
    half = XFADE / 2
    draw_shot(i, t, frame)
    # 与相邻镜头交叉淡化
    if t > d - half and i + 1 < len(SHOTS):
        a = (t - (d - half)) / XFADE
        with xf(alpha=a * a * (3 - 2 * a)):
            draw_shot(i + 1, 0.0, frame)
    elif t < half and i > 0:
        a = 0.5 + t / XFADE
        a = a * a * (3 - 2 * a)
        # 叠在上一镜头定格之上
        canvas.clear(skia.ColorWHITE)
        draw_shot(i - 1, SHOTS[i - 1][1], frame)
        with xf(alpha=a):
            draw_shot(i, t, frame)
    # 片尾淡出
    if T > TOTAL - 1.2:
        k = (T - (TOTAL - 1.2)) / 1.2
        canvas.drawColor(skia.ColorSetARGB(int(255 * min(1, k) * 0.9), 248, 241, 227))
    return surface


def to_rgba(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


def preview(times):
    os.makedirs(BUILD, exist_ok=True)
    for T in times:
        s = render_frame(int(round(float(T) * FPS)))
        path = os.path.join(BUILD, f"preview_{float(T):07.2f}.png")
        s.makeImageSnapshot().save(path, skia.kPNG)
        print(path)


def sheet(times=None, cols=4, out="sheet.png", scale=0.25):
    os.makedirs(BUILD, exist_ok=True)
    if times is None:
        times = []
        for s, (name, d, f) in zip(STARTS, SHOTS):
            times += [s + d * 0.25, s + d * 0.6, s + d * 0.92]
    tw, th = int(W * scale), int(H * scale)
    rows = (len(times) + cols - 1) // cols
    big = skia.Surface(tw * cols, th * rows)
    bc = big.getCanvas()
    bc.clear(skia.ColorWHITE)
    font = skia.Font(skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", "LXGWWenKai-Regular.ttf")), 18)
    for k, T in enumerate(times):
        s = render_frame(int(round(T * FPS)))
        img = s.makeImageSnapshot()
        x, y = (k % cols) * tw, (k // cols) * th
        bc.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw - 2, th - 2), skia.SamplingOptions(skia.FilterMode.kLinear))
        i, t = locate(T)
        bc.drawString(f"{SHOTS[i][0]}  t={T:.1f}", x + 6, y + 18, font, skia.Paint(Color=skia.ColorRED))
    path = os.path.join(BUILD, out)
    big.makeImageSnapshot().save(path, skia.kPNG)
    print(path)


def _render_segment(args):
    k, f0, f1 = args
    path = os.path.join(BUILD, f"seg_{k:02d}.mp4")
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-tune", "animation", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surface = skia.Surface(W, H)
    for fr in range(f0, f1):
        render_frame(fr, surface)
        p.stdin.write(to_rgba(surface).tobytes())
        if (fr - f0) % 240 == 0:
            print(f"  seg {k}: {fr - f0}/{f1 - f0}", flush=True)
    p.stdin.close()
    p.wait()
    return path


def full(workers=None):
    os.makedirs(BUILD, exist_ok=True)
    wav = os.path.join(BUILD, "music.wav")
    if not os.path.exists(wav):
        print("synthesizing music ...", flush=True)
        music.render(wav)
    nframes = int(round(TOTAL * FPS))
    workers = workers or os.cpu_count() or 2
    nseg = workers * 3
    bounds = np.linspace(0, nframes, nseg + 1).astype(int)
    jobs = [(k, bounds[k], bounds[k + 1]) for k in range(nseg)]
    with Pool(workers) as pool:
        segs = pool.map(_render_segment, jobs, chunksize=1)
    lst = os.path.join(BUILD, "segments.txt")
    with open(lst, "w") as fh:
        for s in segs:
            fh.write(f"file '{os.path.basename(s)}'\n")
    out = os.path.join(BUILD, "书页里的人.mp4")
    subprocess.check_call([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                           "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}",
                           "-movflags", "+faststart", out])
    for s in segs:
        os.remove(s)
    print(out)


if __name__ == "__main__":
    ensure_font()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    if cmd == "preview":
        preview(sys.argv[2:])
    elif cmd == "sheet":
        sheet()
    elif cmd == "full":
        full()
