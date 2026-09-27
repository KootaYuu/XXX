"""简笔画绘图库：手绘抖动线条、水彩色块、手写字、人物与道具。"""
import math
import os
import random

import numpy as np
import skia

W, H = 1920, 1080
FPS = 24
BOIL = 4  # 每 4 帧重新“描”一次线（6 fps 的手绘抖动）

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.environ.get("STORY_FONT", os.path.join(HERE, "fonts", "LXGWWenKai-Regular.ttf"))

PAL = {
    "ink": (74, 59, 50),
    "paper": (248, 241, 227),
    "coral": (232, 112, 100),
    "pink": (244, 150, 160),
    "blush": (245, 140, 140),
    "blue": (98, 140, 196),
    "sky": (170, 205, 235),
    "yellow": (248, 205, 110),
    "lamp": (255, 214, 130),
    "orange": (232, 145, 75),
    "red": (214, 78, 66),
    "green": (132, 176, 118),
    "grey": (150, 145, 140),
    "lgrey": (205, 200, 192),
    "wood": (196, 150, 104),
    "graphite": (72, 72, 84),
    "white": (255, 252, 246),
    "tear": (120, 170, 230),
    "night": (60, 70, 110),
}


def col(name_or_rgb, a=255):
    r, g, b = PAL[name_or_rgb] if isinstance(name_or_rgb, str) else name_or_rgb
    return skia.ColorSetARGB(int(max(0, min(255, a))), int(r), int(g), int(b))


class G:
    canvas = None
    frame = 0
    t = 0.0        # 全片时间（秒）
    rng = random.Random(0)


def begin(canvas, frame, salt=0):
    G.canvas = canvas
    G.frame = frame
    G.t = frame / FPS
    G.rng = random.Random((frame // BOIL) * 7919 + salt * 104729)


# ---------------------------------------------------------------- 缓动

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    """t 在 [t0,t1] 上的 smoothstep 进度"""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    x = clamp((t - t0) / (t1 - t0))
    return x * x * (3 - 2 * x)


def lin(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def lerp(a, b, p):
    return a + (b - a) * p


def pop(t, t0, dur=0.35):
    """弹出缩放：0 -> 1.15 -> 1"""
    x = clamp((t - t0) / dur)
    if x <= 0:
        return 0.0
    if x < 0.7:
        return 1.15 * (x / 0.7)
    return 1.15 - 0.15 * (x - 0.7) / 0.3


# ---------------------------------------------------------------- 画笔

def _paint(color, width=4.0, fill=False, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=color)
    if fill:
        p.setStyle(skia.Paint.kFill_Style)
    else:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def catmull(pts, closed=False, n=10):
    P = [np.asarray(p, float) for p in pts]
    if len(P) < 3:
        return np.array(P)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            s = k / n
            s2, s3 = s * s, s * s * s
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    out.append(P[-2])
    return np.array(out)


def _wobble(pts, closed, amp):
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P, P[:1]])
    seg = np.diff(P, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(L)])
    total = cum[-1]
    if total < 1e-6 or amp <= 0:
        return P
    n = max(3, int(total / 7) + 1)
    s = np.linspace(0, total, n)
    R = np.stack([np.interp(s, cum, P[:, 0]), np.interp(s, cum, P[:, 1])], 1)
    d = np.gradient(R, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= (np.hypot(nrm[:, 0], nrm[:, 1]) + 1e-9)[:, None]
    knot = 60.0
    nk = int(total / knot) + 2
    vals = np.array([G.rng.uniform(-1, 1) for _ in range(nk + 1)])
    if closed:
        vals[int(total / knot) + 1:] = vals[0]
    u = s / knot
    i = np.floor(u).astype(int)
    f = u - i
    f = (1 - np.cos(np.pi * f)) / 2
    off = vals[i] * (1 - f) + vals[i + 1] * f
    R = R + nrm * (off * amp)[:, None]
    if not closed:
        # 线头轻微出头，像手画的起笔
        ext = G.rng.uniform(0, 2.5)
        if len(R) > 1:
            v = R[0] - R[1]
            R[0] = R[0] + v / (np.hypot(*v) + 1e-9) * ext
    return R


def _path(R, close=False):
    path = skia.Path()
    path.moveTo(float(R[0][0]), float(R[0][1]))
    for x, y in R[1:]:
        path.lineTo(float(x), float(y))
    if close:
        path.close()
    return path


def stroke(pts, w=4.0, c="ink", a=255, closed=False, smooth=False, amp=1.5,
           fill=None, fa=255, wash=None, wa=110, line=True):
    """画一笔：可选纸色/实色填充（fill）与水彩晕染（wash）。"""
    if smooth:
        pts = catmull(pts, closed)
    R = _wobble(pts, closed, amp)
    cv = G.canvas
    if fill is not None:
        cv.drawPath(_path(R, True), _paint(col(fill, fa), fill=True))
    if wash is not None:
        R2 = _wobble(pts, closed, amp * 1.6) + np.array([G.rng.uniform(2, 5), G.rng.uniform(1, 4)])
        cv.drawPath(_path(R2, True), _paint(col(wash, wa), fill=True, blur=2.5))
    if line and w > 0:
        cv.drawPath(_path(R, closed), _paint(col(c, a), w))
    return R


def line(x1, y1, x2, y2, w=4.0, c="ink", a=255, amp=1.2):
    return stroke([(x1, y1), (x2, y2)], w, c, a, amp=amp)


def circle_pts(cx, cy, rx, ry=None, n=None, a0=0.0, a1=2 * math.pi):
    ry = rx if ry is None else ry
    n = n or max(16, int(max(rx, ry) / 2.5))
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1))]


def circle(cx, cy, r, w=4.0, c="ink", a=255, fill=None, fa=255, wash=None, wa=110, ry=None, amp=1.2, line=True):
    return stroke(circle_pts(cx, cy, r, ry), w, c, a, closed=True, fill=fill, fa=fa, wash=wash, wa=wa, amp=amp, line=line)


def arc(cx, cy, r, a0, a1, w=4.0, c="ink", a=255, ry=None, amp=1.0):
    """角度单位：度，0 为右，顺时针（屏幕坐标）"""
    return stroke(circle_pts(cx, cy, r, ry, None, math.radians(a0), math.radians(a1)), w, c, a, amp=amp)


def rect(x, y, w_, h_, w=4.0, c="ink", a=255, fill=None, fa=255, wash=None, wa=110, amp=1.5, line=True):
    pts = [(x, y), (x + w_, y), (x + w_, y + h_), (x, y + h_)]
    return stroke(pts, w, c, a, closed=True, fill=fill, fa=fa, wash=wash, wa=wa, amp=amp, line=line)


def dot(x, y, r=4.0, c="ink", a=255):
    G.canvas.drawCircle(x, y, r, _paint(col(c, a), fill=True))


def blob(x, y, rx, ry, c, a=90, blur=18):
    """柔和光晕/色块"""
    p = _paint(col(c, a), fill=True, blur=blur)
    G.canvas.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), p)


def solid_rect(x, y, w_, h_, c, a=255):
    G.canvas.drawRect(skia.Rect.MakeXYWH(x, y, w_, h_), _paint(col(c, a), fill=True))


# ---------------------------------------------------------------- 变换

class xf:
    """with xf(tx, ty, rot=0, scale=1, alpha=1): 局部坐标系"""

    def __init__(self, tx=0, ty=0, rot=0, scale=1.0, alpha=1.0, sx=None, sy=None, cf=None):
        self.a = (tx, ty, rot, scale, alpha, sx, sy, cf)

    def __enter__(self):
        tx, ty, rot, scale, alpha, sx, sy, cf = self.a
        cv = G.canvas
        if alpha < 0.999 or cf is not None:
            p = skia.Paint()
            if alpha < 0.999:
                p.setAlphaf(max(0.0, alpha))
            if cf is not None:
                p.setColorFilter(cf)
            cv.saveLayer(None, p)
            self.layer = True
        else:
            self.layer = False
        cv.save()
        cv.translate(tx, ty)
        if rot:
            cv.rotate(rot)
        if sx is not None or sy is not None:
            cv.scale(sx if sx is not None else scale, sy if sy is not None else scale)
        elif scale != 1.0:
            cv.scale(scale, scale)
        return self

    def __exit__(self, *exc):
        G.canvas.restore()
        if self.layer:
            G.canvas.restore()


def cam(zoom=1.0, cx=W / 2, cy=H / 2, rot=0):
    """镜头：以 (cx, cy) 为画面中心放大 zoom 倍"""
    class _C:
        def __enter__(self_):
            cv = G.canvas
            cv.save()
            cv.translate(W / 2, H / 2)
            if rot:
                cv.rotate(rot)
            cv.scale(zoom, zoom)
            cv.translate(-cx, -cy)

        def __exit__(self_, *e):
            G.canvas.restore()
    return _C()


def color_matrix(kind, amount=1.0):
    I = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    if kind == "grey":
        M = [0.33, 0.55, 0.12, 0, 0.02, 0.33, 0.55, 0.12, 0, 0.02, 0.33, 0.55, 0.12, 0, 0.03, 0, 0, 0, 1, 0]
    elif kind == "sepia":
        M = [0.42, 0.48, 0.12, 0, 0.0, 0.33, 0.5, 0.125, 0, 0.0, 0.25, 0.42, 0.16, 0, 0.0, 0, 0, 0, 1, 0]
    elif kind == "memory":
        M = [0.55, 0.3, 0.1, 0, -0.02, 0.2, 0.7, 0.12, 0, 0.0, 0.2, 0.35, 0.55, 0, 0.12, 0, 0, 0, 1, 0]
    elif kind == "warm":
        M = [1.05, 0.05, 0, 0, 0.03, 0, 1.0, 0, 0, 0.01, 0, 0, 0.88, 0, 0, 0, 0, 0, 1, 0]
    else:
        M = I
    return skia.ColorFilters.Matrix([lerp(i, m, amount) for i, m in zip(I, M)])


# ---------------------------------------------------------------- 纸张

_PAPER = None


def paper_image():
    global _PAPER
    if _PAPER is None:
        rng = np.random.default_rng(3)
        base = np.array(PAL["paper"], float)
        small = rng.standard_normal((H // 40 + 2, W // 40 + 2))
        big = np.kron(small, np.ones((40, 40)))[:H, :W]
        k = np.ones(41) / 41
        big = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, big)
        big = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 0, big)
        grain = rng.standard_normal((H, W))
        yy, xx = np.mgrid[0:H, 0:W]
        v = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2
        vign = np.clip(v, 0, 1.5) * 16
        shade = big * 5.0 + grain * 3.0 - vign
        img = np.clip(base[None, None, :] + shade[..., None] * np.array([1.0, 0.97, 0.9]), 0, 255).astype(np.uint8)
        rgba = np.dstack([img, np.full((H, W), 255, np.uint8)])
        _PAPER = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _PAPER


def draw_paper():
    G.canvas.drawImage(paper_image(), 0, 0)


# ---------------------------------------------------------------- 文字

_TF = {}


def _typeface():
    if "tf" not in _TF:
        _TF["tf"] = skia.Typeface.MakeFromFile(FONT_PATH)
    return _TF["tf"]


def _font(size, style):
    f = skia.Font(_typeface(), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    if style == "x":          # X 的字：瘦、右斜
        f.setSkewX(-0.28)
        f.setScaleX(0.82)
    elif style == "xu":       # 许知行的字：方正、笨拙、用力
        f.setEmbolden(True)
        f.setScaleX(1.1)
    elif style == "title":
        f.setEmbolden(True)
    return f


def text_width(s, size, style="plain"):
    return _font(size, style).measureText(s)


def write(s, x, y, size=48, style="plain", c="ink", a=255, align="left", reveal=1.0, pencil=False):
    """手写文字；reveal ∈ [0,1] 为已写出的比例（逐字出现）。返回 (笔尖x, 笔尖y)。"""
    f = _font(size, style)
    chars = list(s)
    n = len(chars)
    adv = [f.measureText(ch) for ch in chars]
    if style == "xu":
        adv = [a_ * 1.04 for a_ in adv]
    total = sum(adv)
    if align == "center":
        x0 = x - total / 2
    elif align == "right":
        x0 = x - total
    else:
        x0 = x
    shown = reveal * n
    cx = x0
    tip = (x0, y)
    cv = G.canvas
    rng = random.Random(hash(s) & 0xFFFF)
    for i, ch in enumerate(chars):
        alpha_i = clamp(shown - i)
        jr = rng.uniform(-1, 1)
        jy = rng.uniform(-1, 1)
        if alpha_i > 0:
            p = skia.Paint(AntiAlias=True, Color=col(c, a * alpha_i))
            if style == "xu":
                cv.save()
                cv.translate(cx + adv[i] / 2, y + jy * size * 0.06)
                cv.rotate(jr * 5)
                cv.drawString(ch, -adv[i] / 2 / 1.04, 0, f, p)
                cv.restore()
            else:
                cv.drawString(ch, cx, y + (jy * size * 0.03 if style == "x" else 0), f, p)
            tip = (cx + adv[i] * alpha_i, y)
        cx += adv[i]
    if pencil and 0 < reveal < 1:
        draw_pencil(tip[0] + 6, tip[1] - size * 0.25, size / 48)
    return tip


def draw_pencil(x, y, s=1.0, wig=True):
    """铅笔：笔尖在 (x, y)"""
    ph = G.t * 22
    dx = math.sin(ph) * 4 * s if wig else 0
    dy = math.cos(ph * 1.3) * 3 * s if wig else 0
    with xf(x + dx, y + dy, rot=-35, scale=s):
        stroke([(0, 0), (10, -26), (-10, -26)], 3, closed=True, fill="wood", amp=0.5)
        dot(0, -3, 3.5, "graphite")
        rect(-10, -150, 20, 124, 3, fill="yellow", amp=0.6)
        rect(-10, -172, 20, 22, 3, fill="pink", amp=0.6)


# ---------------------------------------------------------------- 常用图形

def heart_pts(cx, cy, s):
    pts = []
    for k in range(40):
        a = 2 * math.pi * k / 40
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s, cy + y * s))
    return pts


def heart(cx, cy, s=1.0, c="pink", a=255, broken=0.0):
    if s <= 0:
        return
    if broken <= 0:
        stroke(heart_pts(cx, cy, s), 3.5, "ink", a, closed=True, fill=c, fa=a * 0.95, amp=0.8)
        return
    zig = [(0, -8 * s), (-4 * s, -1 * s), (4 * s, 5 * s), (-3 * s, 11 * s), (0, 20 * s)]
    d = broken * 14 * s
    for side in (-1, 1):
        clip = [(0, -40 * s)] + zig + [(0, 40 * s), (side * 40 * s, 40 * s), (side * 40 * s, -40 * s)]
        with xf(cx + side * d, cy + broken * 6 * s, rot=side * broken * 16):
            G.canvas.save()
            G.canvas.clipPath(_path(np.array(clip), True), doAntiAlias=True)
            stroke(heart_pts(0, 0, s), 3.5, "ink", a, closed=True, fill=c, fa=a * 0.95, amp=0.8)
            G.canvas.restore()
            stroke(zig, 3.5, "ink", a, amp=0.3)


def bubble(x, y, w_, h_, tail=None, kind="speech", a=255, s=1.0):
    """对话/思考气泡，中心 (x,y)。tail 为尾巴指向的点。"""
    if s <= 0:
        return
    with xf(x, y, scale=s, alpha=a / 255):
        if kind == "speech":
            pts = circle_pts(0, 0, w_ / 2, h_ / 2, 40)
            if tail is not None:
                tx, ty = (tail[0] - x) / s, (tail[1] - y) / s
                ang = math.atan2(ty, tx)
                i0 = int(((ang - 0.22) % (2 * math.pi)) / (2 * math.pi) * 40)
                i1 = int(((ang + 0.22) % (2 * math.pi)) / (2 * math.pi) * 40)
                if i1 < i0:
                    i1 += 40
                keep = [pts[k % 40] for k in range(i1, i0 + 40 + 1)]
                pts = keep + [(tx, ty)]
            stroke(pts, 4, closed=True, fill="white", amp=1.0)
        else:
            n = 11
            pts = []
            for k in range(n):
                a0 = 2 * math.pi * k / n
                a1 = 2 * math.pi * (k + 1) / n
                cxk = (w_ / 2) * math.cos((a0 + a1) / 2)
                cyk = (h_ / 2) * math.sin((a0 + a1) / 2)
                pts.extend(circle_pts(cxk * 0.92, cyk * 0.92, 0.33 * (w_ + h_) / 2 * 0.62, None, 10,
                                      (a0 + a1) / 2 - 1.3, (a0 + a1) / 2 + 1.3))
            stroke(pts, 4, closed=True, fill="white", amp=0.8)
            if tail is not None:
                tx, ty = (tail[0] - x) / s, (tail[1] - y) / s
                for k, r in ((0.55, 9), (0.8, 6)):
                    bx = lerp(0, tx, k) if abs(tx) > 1 else 0
                    by = lerp(h_ / 2, ty, k)
                    circle(bx, by, r, 3.5, fill="white")


def sparkle(x, y, s=1.0, c="yellow", a=255):
    if s <= 0:
        return
    pts = []
    for k in range(8):
        r = 18 * s if k % 2 == 0 else 6 * s
        ang = math.pi / 4 * k - math.pi / 2
        pts.append((x + r * math.cos(ang), y + r * math.sin(ang)))
    stroke(pts, 3, closed=True, fill=c, a=a, fa=a, amp=0.4)


def sweat(x, y, s=1.0):
    stroke([(x, y - 14 * s), (x - 8 * s, y), (x, y + 7 * s), (x + 8 * s, y)], 3, "ink", closed=True, smooth=True, fill="sky", amp=0.4)


def teardrop(x, y, s=1.0):
    stroke([(x, y - 10 * s), (x - 6 * s, y + 2 * s), (x, y + 8 * s), (x + 6 * s, y + 2 * s)], 2.5, "tear", closed=True,
           smooth=True, fill="tear", fa=200, amp=0.3)


def rain_cloud(x, y, s, t):
    with xf(x, y, scale=s):
        pts = circle_pts(-30, 0, 26, 22, 14, math.pi * 0.5, math.pi * 1.6) + \
            circle_pts(0, -14, 30, 26, 14, math.pi * 1.0, math.pi * 2.0) + \
            circle_pts(32, 0, 24, 20, 14, math.pi * 1.4, math.pi * 2.5)
        stroke(pts, 4, closed=True, fill="lgrey", amp=0.8)
        for k in range(6):
            ph = (t * 1.6 + k * 0.37) % 1.0
            xx = -40 + k * 16
            yy = 26 + ph * 70
            line(xx, yy, xx - 4, yy + 12, 3, "tear", a=255 * (1 - ph))


# ---------------------------------------------------------------- 粒子

def particles(kind, t, n=24, area=(0, 0, W, H), seed=1, a=255, speed=1.0, wind=0.0):
    rng = random.Random(seed)
    x0, y0, aw, ah = area
    for i in range(n):
        px = rng.uniform(0, aw)
        ph = rng.uniform(0, 1)
        sp = rng.uniform(0.7, 1.3) * speed
        size = rng.uniform(0.7, 1.3)
        sway = rng.uniform(20, 50)
        spin = rng.uniform(-1, 1)
        if kind == "rain":
            fall = ((ph + t * 0.9 * sp) % 1.0)
            y = y0 + fall * (ah + 60) - 30
            x = x0 + (px + wind * fall * 200) % aw
            line(x, y, x - 8 - wind * 6, y + 26, 2.5, "blue", a * 0.7, amp=0.2)
            continue
        cycle = 7.0 / sp
        fall = ((ph + t / cycle) % 1.0)
        y = y0 + fall * (ah + 80) - 40
        x = x0 + (px + math.sin(t * 1.2 + i) * sway + wind * fall * 300) % aw
        if kind == "snow":
            circle(x, y, 5 * size, 2.5, "lgrey", a, fill="white", fa=a, amp=0.3)
        elif kind == "leaf":
            c = ["orange", "red", "yellow"][i % 3]
            with xf(x, y, rot=math.degrees(t * spin * 2) + i * 40, scale=size):
                stroke([(-14, 0), (0, -8), (14, 0), (0, 8)], 2.5, "ink", a, closed=True, smooth=True, fill=c, fa=a * 0.9, amp=0.4)
                line(-14, 0, 12, 0, 2, "ink", a * 0.8, amp=0.2)
        elif kind == "petal":
            with xf(x, y, rot=math.degrees(t * spin * 2) + i * 30, scale=size):
                stroke([(-9, 0), (0, -6), (9, 0), (0, 6)], 2, "coral", a * 0.8, closed=True, smooth=True, fill="pink", fa=a * 0.85, amp=0.3)
        elif kind == "dust":
            blob(x, y, 4 * size, 4 * size, "yellow", a * 0.5, blur=3)
        elif kind == "heart":
            heart(x, y, 0.8 * size, "pink", a)


# ---------------------------------------------------------------- 人物

DIMS = {
    "girl": dict(head=31, body=70, thigh=36, shin=36, uarm=29, farm=27),
    "boy": dict(head=31, body=92, thigh=46, shin=46, uarm=36, farm=32),
    "old": dict(head=30, body=68, thigh=36, shin=34, uarm=29, farm=27),
    "kid": dict(head=28, body=62, thigh=32, shin=32, uarm=26, farm=24),
}


def _seg(p, ang_deg, length):
    a = math.radians(ang_deg)
    return (p[0] + math.sin(a) * length, p[1] + math.cos(a) * length)


def person(kind, x, y, s=1.0, face=0, walk=None, arms=None, legs=None, expr="smile", lean=None, tilt=0.0,
           blush=0.0, tears=0.0, sweat_=False, sit=False, look=0.0, scarf_wind=0.0, hair_c=None, alpha=1.0,
           mouth_open=0.0, cane=None, hair=None, badge=None, scarf=None, glasses=None, skirt="coral",
           backpack=False, nod=0.0, flower=False):
    """画一个简笔人物，(x, y) 为脚底（sit=True 时为臀部）。

    face: -1 朝左, 1 朝右, 0 正面。arms/legs: ((角度, 弯曲), (角度, 弯曲))，
    角度从竖直向下起算，正值转向屏幕右侧。返回关键点 dict。
    """
    d = DIMS[kind]
    if lean is None:
        lean = 12 * face if kind == "old" else 0
    if cane is None:
        cane = kind == "old"
    if hair is None:
        hair = {"girl": "ponytail", "boy": "spiky", "old": "side", "kid": "short"}[kind]
    if badge is None:
        badge = kind == "boy"
    if scarf is None:
        scarf = kind == "girl"
    if glasses is None:
        glasses = kind == "old"
    fdir = face if face != 0 else 1
    # --- 腿
    if legs is None:
        if walk is not None:
            sw = math.sin(walk)
            legs = ((-24 * sw * fdir, max(0, -math.cos(walk)) * 30 * fdir if sw * fdir < 0 else 0),
                    (24 * sw * fdir, max(0, math.cos(walk)) * 30 * fdir if sw * fdir > 0 else 0))
            legs = ((-24 * sw, (18 + 14 * max(0, math.cos(walk))) * fdir * (1 if sw * fdir < 0 else 0.3)),
                    (24 * sw, (18 + 14 * max(0, -math.cos(walk))) * fdir * (1 if sw * fdir > 0 else 0.3)))
        elif sit:
            legs = ((90 * fdir, -90 * fdir), (84 * fdir, -84 * fdir))
        else:
            legs = ((-7, 0), (7, 0))
    if arms is None:
        if walk is not None:
            sw = math.sin(walk)
            arms = ((-15 + 22 * sw, 15), (15 - 22 * sw, -15))
        else:
            arms = ((-16, 8), (16, -8))
    L = s
    hip0 = (0.0, 0.0)
    knees, feet = [], []
    for (ang, bend) in legs:
        k = _seg(hip0, ang, d["thigh"] * L)
        f_ = _seg(k, ang - bend, d["shin"] * L)
        knees.append(k)
        feet.append(f_)
    if sit:
        hip = (x, y)
    else:
        lowest = max(f_[1] for f_ in feet)
        hip = (x, y - lowest)
    knees = [(hip[0] + k[0], hip[1] + k[1]) for k in knees]
    feet = [(hip[0] + f_[0], hip[1] + f_[1]) for f_ in feet]
    bob = 0.0
    la = math.radians(lean)
    shoulder = (hip[0] + math.sin(la) * d["body"] * L, hip[1] - math.cos(la) * d["body"] * L + bob)
    neck_len = (d["head"] + 5) * L
    hc = (shoulder[0] + math.sin(la) * neck_len * 0.9, shoulder[1] - math.cos(la) * neck_len)
    arm_root = (lerp(hip[0], shoulder[0], 0.9), lerp(hip[1], shoulder[1], 0.9))
    elbows, hands = [], []
    for (ang, bend) in arms:
        e = _seg(arm_root, ang, d["uarm"] * L)
        h = _seg(e, ang + bend, d["farm"] * L)
        elbows.append(e)
        hands.append(h)
    ink_w = 5.0 * max(0.6, L)

    lay = xf(alpha=alpha) if alpha < 0.999 else None
    if lay:
        lay.__enter__()
    hr = d["head"] * L
    # --- 马尾（在头后面）
    if hair == "ponytail":
        side = -fdir if face != 0 else 1
        base = (hc[0] + side * hr * 0.75, hc[1] - hr * 0.35)
        swing = math.sin(G.t * 3) * 4 + scarf_wind * 10
        tip = (base[0] + side * (hr * 0.9 + swing * 0.3), base[1] + hr * 1.25 + swing)
        stroke([base, (base[0] + side * hr * 0.7, base[1] + hr * 0.2), tip,
                (base[0] + side * hr * 0.25, base[1] + hr * 0.55)], ink_w * 0.8, closed=True, smooth=True,
               fill="ink", fa=235, amp=0.6)
    # --- 腿
    for k, f_ in zip(knees, feet):
        stroke([hip, k, f_], ink_w, amp=1.0)
        line(f_[0], f_[1], f_[0] + 9 * L * fdir, f_[1], ink_w, amp=0.3)
    # --- 身体
    line(hip[0], hip[1], shoulder[0], shoulder[1], ink_w, amp=1.0)
    if backpack:
        mx, my = lerp(hip[0], shoulder[0], 0.62), lerp(hip[1], shoulder[1], 0.62)
        bxx = mx - fdir * 24 * L
        rect(bxx - 17 * L, my - 30 * L, 34 * L, 52 * L, ink_w * 0.8, fill="paper", wash="green", wa=160, amp=0.6)
    if skirt and kind in ("girl", "kid"):
        wx, wy = lerp(hip[0], shoulder[0], 0.3), lerp(hip[1], shoulder[1], 0.3)
        sk = [(wx - 11 * L, wy), (wx + 11 * L, wy), (hip[0] + 26 * L, hip[1] + 22 * L), (hip[0] - 26 * L, hip[1] + 22 * L)]
        stroke(sk, ink_w * 0.8, closed=True, fill="paper", wash=skirt, wa=120, amp=0.8)
    if badge:
        # 工作牌挂绳
        bx, by = lerp(shoulder[0], hip[0], 0.45), lerp(shoulder[1], hip[1], 0.45)
        stroke([(shoulder[0] - 9 * L, shoulder[1] + 2 * L), (bx, by - 8 * L), (shoulder[0] + 9 * L, shoulder[1] + 2 * L)],
               2.5, "blue", amp=0.3)
        rect(bx - 9 * L, by - 8 * L, 18 * L, 22 * L, 3, fill="white", wash="blue", wa=150, amp=0.4)
    # --- 手臂
    for e, h in zip(elbows, hands):
        stroke([arm_root, e, h], ink_w, amp=1.0)
    # --- 拐杖
    if kind == "old" and cane:
        hx, hy = hands[1] if fdir > 0 else hands[0]
        gy = y if not sit else y + 80 * L
        line(hx + 4 * fdir, hy - 2, hx + 10 * fdir * L, gy, ink_w * 0.8, "wood", amp=0.4)
        arc(hx - 4 * fdir, hy - 2, 8 * L, 180, 360, ink_w * 0.8, "wood")
    # --- 头
    circle(hc[0], hc[1], hr, ink_w, fill="paper", amp=1.0)
    tl = math.radians(tilt)

    def fp(dx, dy):
        dx += (look if look else face * 7) * L
        dy += nod
        return (hc[0] + (dx * math.cos(tl) - dy * math.sin(tl)) * L,
                hc[1] + (dx * math.sin(tl) + dy * math.cos(tl)) * L)

    # 头发
    if hair == "long":
        side_pts = [fp(-hr / L * 1.02, -6), fp(-hr / L * 1.2, 30), fp(-hr / L * 0.9, 44), fp(-hr / L * 0.7, 10)]
        stroke(side_pts, ink_w * 0.7, closed=True, smooth=True, fill="ink", fa=235, amp=0.5)
        side_pts = [fp(hr / L * 1.02, -6), fp(hr / L * 1.2, 30), fp(hr / L * 0.9, 44), fp(hr / L * 0.7, 10)]
        stroke(side_pts, ink_w * 0.7, closed=True, smooth=True, fill="ink", fa=235, amp=0.5)
    if hair == "bun":
        p = fp(0, -hr / L - 8)
        circle(p[0], p[1], 13 * L, ink_w * 0.7, fill="ink", fa=235, amp=0.4)
    if hair in ("ponytail", "long", "short", "bun"):
        stroke([fp(-hr / L * 0.95, -4), fp(-20, -24), fp(-2, -31), fp(18, -26), fp(hr / L * 0.95, -6), fp(10, -14),
                fp(-2, -20), fp(-14, -12)], ink_w * 0.7, closed=True, smooth=True, fill="ink", fa=235, amp=0.6)
    elif hair == "spiky":
        for ang in (-50, -25, 0, 25, 50):
            ra = math.radians(ang - 90)
            p0 = (hc[0] + math.cos(ra) * hr * 0.92, hc[1] + math.sin(ra) * hr * 0.92)
            p1 = (hc[0] + math.cos(ra - 0.25) * hr * 1.45, hc[1] + math.sin(ra - 0.25) * hr * 1.45)
            line(p0[0], p0[1], p1[0], p1[1], ink_w * 0.8, amp=0.4)
    elif hair == "neat":
        stroke([fp(-hr / L * 0.97, 0), fp(-18, -26), fp(4, -32), fp(24, -22), fp(hr / L * 0.97, -2), fp(12, -18),
                fp(-6, -16)], ink_w * 0.7, closed=True, smooth=True, fill="ink", fa=235, amp=0.5)
    elif hair == "side":
        for side in (-1, 1):
            cx_ = hc[0] + side * hr * 0.9
            circle(cx_, hc[1] - hr * 0.35, hr * 0.32, 3, "grey", fill="white", amp=0.5)
    # 五官
    ex = 10
    if expr in ("happy", "closed", "cry"):
        for sd in (-1, 1):
            p = fp(sd * ex, -2)
            if expr == "happy":
                arc(p[0], p[1] + 3, 5 * L, 200, 340, 3.5)
            else:
                arc(p[0], p[1] - 3, 5 * L, 20, 160, 3.5)
    else:
        er = 4.2 if expr != "surprise" else 5.5
        for sd in (-1, 1):
            p = fp(sd * ex, -2)
            dot(p[0], p[1], er * L)
    if flower:
        p = fp(hr / L * 0.7, -hr / L * 0.7)
        for k in range(5):
            a_ = k * 2 * math.pi / 5
            circle(p[0] + math.cos(a_) * 6 * L, p[1] + math.sin(a_) * 6 * L, 5 * L, 2, fill="pink", amp=0.2)
        dot(p[0], p[1], 3 * L, "yellow")
    if glasses:
        for sd in (-1, 1):
            p = fp(sd * ex, -2)
            circle(p[0], p[1], 9 * L, 2.5, amp=0.3)
        a_, b_ = fp(-2, -3), fp(2, -3)
        line(a_[0], a_[1], b_[0], b_[1], 2.5, amp=0.1)
    if expr in ("sad", "worried", "cry"):
        for sd in (-1, 1):
            a_, b_ = fp(sd * 5, -12), fp(sd * 15, -15 if expr != "worried" else -10)
            line(a_[0], a_[1], b_[0], b_[1], 3, amp=0.2)
    m = fp(0, 12)
    mo = mouth_open
    if expr in ("smile", "closed"):
        arc(m[0], m[1] - 4 * L, 7 * L, 30, 150, 3.5)
    elif expr == "happy":
        stroke(circle_pts(m[0], m[1] - 3 * L, 9 * L, 7 * L, 12, 0, math.pi), 3.5, fill="coral", fa=200, closed=True, amp=0.3)
    elif expr == "surprise":
        circle(m[0], m[1] + 1, (4 + 3 * mo) * L, 3.5, amp=0.3)
    elif expr in ("sad", "cry"):
        arc(m[0], m[1] + 5 * L, 7 * L, 210, 330, 3.5)
    elif expr == "worried":
        stroke([fp(-7, 13), fp(-3, 10), fp(1, 13), fp(5, 10), fp(8, 12)], 3, amp=0.2)
    else:  # neutral
        a_, b_ = fp(-5, 12), fp(5, 12)
        line(a_[0], a_[1], b_[0], b_[1], 3.5, amp=0.2)
    if blush > 0:
        for sd in (-1, 1):
            p = fp(sd * 17, 7)
            blob(p[0], p[1], 8 * L, 5 * L, "blush", 150 * blush, blur=3)
    if tears > 0:
        for sd in (-1, 1):
            p = fp(sd * ex, 2)
            ph = (G.t * 0.9 + (0.5 if sd > 0 else 0)) % 1.0
            teardrop(p[0], p[1] + ph * 28 * L, L * 0.9 * tears)
    if sweat_:
        p = fp(hr / L * 0.95, -12)
        sweat(p[0] + 6, p[1] + (G.t * 6 % 6), L)
    # 围巾
    if scarf:
        nx, ny = shoulder[0], shoulder[1] - 2 * L
        stroke(circle_pts(nx, ny, 17 * L, 7 * L, 16), ink_w * 0.7, closed=True, fill="coral", amp=0.5)
        side = -fdir if face != 0 else 1
        wv = math.sin(G.t * 4) * 3 + scarf_wind * 18
        tail = [(nx + side * 6 * L, ny + 4 * L), (nx + side * (12 * L + wv), ny + 26 * L),
                (nx + side * (20 * L + wv), ny + 24 * L), (nx + side * 14 * L, ny + 2 * L)]
        stroke(tail, ink_w * 0.6, closed=True, fill="coral", amp=0.4)
    if lay:
        lay.__exit__()
    return dict(head=hc, hr=hr, shoulder=shoulder, hip=hip, hands=hands, feet=feet, elbows=elbows)


# ---------------------------------------------------------------- 道具与场景

BOOK_COLS = ["coral", "blue", "green", "yellow", "orange", "wood", "pink", "sky", "grey"]


def book_closed(x, y, w_=44, h_=60, rot=0, c="green", label=None, a=255):
    with xf(x, y, rot=rot, alpha=a / 255):
        rect(-w_ / 2, -h_ / 2, w_, h_, 3.5, fill="paper", wash=c, wa=200, amp=0.6)
        line(-w_ / 2 + 6, -h_ / 2, -w_ / 2 + 6, h_ / 2, 3, amp=0.3)
        if label:
            write(label, 4, 4, h_ * 0.22, align="center")


def book_open_small(x, y, w_=70, h_=46, rot=0, c="green"):
    with xf(x, y, rot=rot):
        stroke([(-w_ / 2, -h_ / 2 + 4), (0, -h_ / 2), (0, h_ / 2), (-w_ / 2, h_ / 2 + 4)], 3.5, closed=True, fill="white", amp=0.5)
        stroke([(w_ / 2, -h_ / 2 + 4), (0, -h_ / 2), (0, h_ / 2), (w_ / 2, h_ / 2 + 4)], 3.5, closed=True, fill="white", amp=0.5)
        for k in range(3):
            yy = -h_ / 2 + 10 + k * 10
            line(-w_ / 2 + 6, yy + 2, -6, yy, 2, "grey", amp=0.2)
            line(6, yy, w_ / 2 - 6, yy + 2, 2, "grey", amp=0.2)


def shelf(x, y, w_, h_, rows=5, seed=1, label=None, highlight=None, missing=None):
    """书架，左上角 (x,y)。highlight=(row, idx) 标出《霍乱时期的爱情》所在位置。"""
    rect(x, y, w_, h_, 5, fill="paper", wash="wood", wa=90, amp=1.2)
    rng = random.Random(seed)
    rh = h_ / rows
    spots = {}
    for r in range(rows):
        by = y + (r + 1) * rh
        line(x, by, x + w_, by, 4, amp=0.8)
        bx = x + 10
        idx = 0
        while bx < x + w_ - 30:
            bw = rng.uniform(18, 34)
            bh = rng.uniform(0.62, 0.86) * rh
            c = rng.choice(BOOK_COLS)
            is_hl = highlight == (r, idx)
            if missing == (r, idx):
                spots[(r, idx)] = (bx + bw / 2, by - bh / 2, bw, bh)
            else:
                rect(bx, by - bh, bw, bh, 3, fill="paper", wash=c if not is_hl else "coral", wa=170, amp=0.5)
                if rng.random() < 0.4:
                    line(bx + 4, by - bh * 0.7, bx + bw - 4, by - bh * 0.7, 2, amp=0.2)
                spots[(r, idx)] = (bx + bw / 2, by - bh / 2, bw, bh)
            bx += bw + rng.uniform(1, 4)
            idx += 1
    if label:
        rect(x + w_ / 2 - 30, y - 34, 60, 40, 4, fill="white", amp=0.6)
        write(label, x + w_ / 2, y - 2, 32, align="center")
    return spots


def window(x, y, w_, h_, sky="sky", night=False, weather=None, t=0.0, sun=True):
    rect(x, y, w_, h_, 5, fill="night" if night else sky, fa=255 if night else 160, amp=1.0)
    if night:
        circle(x + w_ * 0.72, y + h_ * 0.3, 26, 3, "yellow", fill="yellow", amp=0.4)
    if weather == "snow":
        with xf():
            G.canvas.save()
            G.canvas.clipRect(skia.Rect.MakeXYWH(x, y, w_, h_))
            particles("snow", t, 14, (x, y, w_, h_), seed=5, speed=0.8)
            G.canvas.restore()
    if weather == "rain":
        G.canvas.save()
        G.canvas.clipRect(skia.Rect.MakeXYWH(x, y, w_, h_))
        particles("rain", t, 20, (x, y, w_, h_), seed=6)
        G.canvas.restore()
    line(x + w_ / 2, y, x + w_ / 2, y + h_, 5)
    line(x, y + h_ / 2, x + w_, y + h_ / 2, 5)
    if sun and not night:
        rays = [(x + 10, y + h_), (x + w_ - 10, y + h_), (x + w_ + 260, y + h_ + 520), (x - 60, y + h_ + 520)]
        path = _path(np.array(rays), True)
        G.canvas.drawPath(path, _paint(col("yellow", 45), fill=True, blur=30))


def building(cx, base, s=1.0, lit=0.0, night=False):
    """图书馆外观"""
    with xf(cx, base, scale=s):
        # 台阶
        for k in range(3):
            rect(-330 + k * 20, -30 * (k + 1), 660 - k * 40, 30, 4, fill="paper", wash="lgrey", wa=90, amp=0.8)
        # 主体
        rect(-300, -470, 600, 380, 5, fill="paper", wash="wood" if not night else "night", wa=90 if not night else 60, amp=1.2)
        # 屋顶
        stroke([(-340, -470), (0, -600), (340, -470)], 5, closed=True, fill="paper", wash="coral", wa=140, amp=1.0)
        circle(0, -520, 30, 4, fill="white", amp=0.5)
        line(0, -520, 0, -540, 3)
        line(0, -520, 14, -520, 3)
        # 柱子
        for k in range(5):
            xx = -240 + k * 120
            rect(xx - 14, -450, 28, 360, 4, fill="white", amp=0.8)
        # 窗
        for k in range(4):
            xx = -180 + k * 120
            for yy in (-420, -260):
                rect(xx - 30, yy, 60, 90, 4, fill="white" if lit <= 0 else "lamp", fa=255, amp=0.8)
                if lit > 0:
                    blob(xx, yy + 45, 60, 70, "lamp", 110 * lit, blur=25)
                line(xx, yy, xx, yy + 90, 3, amp=0.4)
        # 门
        stroke([(-50, -90), (-50, -180), (0, -210), (50, -180), (50, -90)], 5, fill="wood", fa=200, amp=0.6)
        rect(-110, -520 + 70, 220, 44, 4, fill="white", amp=0.6)
        write("图书馆", 0, -520 + 104, 32, align="center")


def tree(x, y, s=1.0, season="autumn", sway=0.0):
    c = {"autumn": "orange", "spring": "pink", "summer": "green", "winter": None}[season]
    with xf(x, y, scale=s):
        stroke([(-14, 0), (-8, -160), (8, -160), (14, 0)], 5, closed=True, fill="paper", wash="wood", wa=160, amp=1.0)
        line(-4, -120, -50, -190, 5)
        line(4, -110, 50, -180, 5)
        if c:
            pts = []
            for k in range(9):
                a0 = 2 * math.pi * k / 9
                pts.extend(circle_pts(math.cos(a0) * 90 + sway, -230 + math.sin(a0) * 70, 46, 40, 8, a0 - 1.2, a0 + 1.2))
            stroke(pts, 4, closed=True, fill="paper", wash=c, wa=170, amp=1.0)


def calendar(x, y, s=1.0, top="", big="周三", flip=0.0):
    with xf(x, y, scale=s):
        rect(-110, -130, 220, 260, 5, fill="white", amp=0.8)
        rect(-110, -130, 220, 60, 5, fill="coral", fa=220, amp=0.8)
        for k in (-60, 60):
            circle(k, -130, 10, 4, fill="paper")
        if top:
            write(top, 0, -86, 34, c="white", align="center")
        write(big, 0, 50, 80, align="center")
        if flip > 0:
            # 撕下的一页在翻飞
            with xf(0, -70, rot=-flip * 60, alpha=1 - flip):
                rect(-110, 0, 220, 200, 4, fill="white", amp=0.6)


def clock(x, y, r=70, hh=6.0, mm=0.0):
    circle(x, y, r, 5, fill="white", amp=0.8)
    for k in range(12):
        a_ = math.radians(k * 30)
        line(x + math.sin(a_) * r * 0.82, y - math.cos(a_) * r * 0.82, x + math.sin(a_) * r * 0.92,
             y - math.cos(a_) * r * 0.92, 3, amp=0.1)
    ah = math.radians((hh % 12 + mm / 60) * 30)
    am = math.radians(mm * 6)
    line(x, y, x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5, 6, amp=0.2)
    line(x, y, x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75, 4, "coral", amp=0.2)
    dot(x, y, 6)


def ring_bell(x, y, s=1.0, t=0.0, ringing=True):
    sw = math.sin(t * 18) * 18 if ringing else 0
    with xf(x, y, rot=sw, scale=s):
        stroke([(-40, 30), (-32, -10), (-18, -34), (18, -34), (32, -10), (40, 30)], 5, closed=True, smooth=False,
               fill="yellow", amp=0.8)
        dot(0, 40, 9)
        line(0, -34, 0, -50, 5)
    if ringing:
        for k in (1, 2):
            a_ = 120 * s + k * 18
            arc(x, y, a_ * 0.5, -40, 40, 3.5, a=200)
            arc(x, y, a_ * 0.5, 140, 220, 3.5, a=200)


def cart(x, y, s=1.0, roll=0.0, books=True):
    with xf(x, y, scale=s):
        if books:
            bx = -80
            for k, c in enumerate(["blue", "coral", "green", "yellow", "wood", "pink"]):
                bh = 50 + (k * 13) % 25
                rect(bx, -100 - bh, 24, bh, 3, fill="paper", wash=c, wa=170, amp=0.4)
                bx += 27
        rect(-100, -100, 200, 60, 5, fill="paper", wash="wood", wa=120, amp=0.8)
        line(-100, -100, -130, -170, 5)
        for wx in (-70, 70):
            circle(wx, -20, 20, 5, fill="white", amp=0.4)
            a_ = roll
            line(wx + math.cos(a_) * 16, -20 + math.sin(a_) * 16, wx - math.cos(a_) * 16, -20 - math.sin(a_) * 16, 3, amp=0.1)
            line(wx + math.cos(a_ + 1.57) * 16, -20 + math.sin(a_ + 1.57) * 16, wx - math.cos(a_ + 1.57) * 16,
                 -20 - math.sin(a_ + 1.57) * 16, 3, amp=0.1)
            line(wx, -40, wx, -60, 4)


def umbrella(x, y, s=1.0, rot=0.0, c="blue"):
    """(x,y) 为伞柄末端"""
    with xf(x, y, rot=rot, scale=s):
        line(0, 0, 0, -140, 5)
        arc(10, 0, 10, 0, 180, 5)
        pts = circle_pts(0, -140, 110, 70, 24, math.pi, 2 * math.pi)
        scal = []
        for k in range(4):
            scal.extend(circle_pts(-82.5 + k * 55, -140, 27.5, 10, 6, 0, math.pi)[::-1])
        stroke(pts + scal, 5, closed=True, fill="paper", wash=c, wa=180, amp=0.8)


def ground(y=880, c="ink", a=255):
    line(-20, y, W + 20, y, 5, c, a, amp=2.0)


def floor_boards(y=880):
    ground(y)
    for k in range(10):
        xx = 100 + k * 200
        line(xx, y + 30, xx + 60, y + 30, 3, "wood", 150)
        line(xx + 100, y + 80, xx + 180, y + 80, 3, "wood", 150)


def page_spread(x, y, w_, h_, lines=9, seed=2, flip=0.0):
    """书页特写：左右两页，灰色印刷线条。返回右页区域。"""
    rng = random.Random(seed)
    stroke([(x - w_ / 2, y - h_ / 2 + 10), (x, y - h_ / 2), (x, y + h_ / 2), (x - w_ / 2, y + h_ / 2 + 10)], 5,
           closed=True, fill="white", amp=1.0)
    stroke([(x + w_ / 2, y - h_ / 2 + 10), (x, y - h_ / 2), (x, y + h_ / 2), (x + w_ / 2, y + h_ / 2 + 10)], 5,
           closed=True, fill="white", amp=1.0)
    lh = (h_ - 80) / max(lines, 1)
    for side in (-1, 1):
        for k in range(lines):
            yy = y - h_ / 2 + 50 + k * lh
            l_ = rng.uniform(0.6, 0.95) * (w_ / 2 - 80)
            x0 = x - w_ / 2 + 40 if side < 0 else x + 40
            line(x0, yy, x0 + l_, yy + 2, 4, "lgrey", amp=0.6)
    if flip > 0:
        # 翻页：一页从右向左
        ang = flip * math.pi
        px = x + math.cos(ang) * w_ / 2
        stroke([(x, y - h_ / 2), (px, y - h_ / 2 + 10 - math.sin(ang) * 30), (px, y + h_ / 2 + 10 - math.sin(ang) * 30),
                (x, y + h_ / 2)], 5, closed=True, fill="white", amp=0.8)


def card(x, y, w_=520, h_=320, rot=0.0, lines=True, a=255):
    with xf(x, y, rot=rot, alpha=a / 255):
        rect(-w_ / 2, -h_ / 2, w_, h_, 5, fill="white", wash="yellow", wa=70, amp=0.8)
        if lines:
            for k in range(1, 6):
                yy = -h_ / 2 + k * h_ / 6
                line(-w_ / 2 + 20, yy, w_ / 2 - 20, yy, 2, "sky", 160, amp=0.3)
        line(-w_ / 2 + 60, -h_ / 2, -w_ / 2 + 60, h_ / 2, 2, "pink", 180, amp=0.3)


def train(x, y, s=1.0, t=0.0, rails=True):
    with xf(x, y, scale=s):
        for k in range(3):
            xx = k * 230
            rect(xx, -150, 210, 120, 5, fill="paper", wash="blue" if k else "coral", wa=150, amp=0.8)
            for j in range(3):
                rect(xx + 20 + j * 62, -130, 44, 40, 3, fill="white", amp=0.4)
            for wx in (40, 170):
                circle(xx + wx, -28, 20, 5, fill="white", amp=0.4)
        rect(-20, -210, 40, 60, 5, fill="paper", wash="grey", wa=150, amp=0.5)
        for k in range(4):
            ph = (t * 0.8 + k * 0.25) % 1.0
            circle(-20 + ph * 180, -230 - ph * 120, 18 + ph * 30, 4, "grey", 255 * (1 - ph), fill="white", fa=220 * (1 - ph), amp=0.5)
    if rails:
        line(-40, y + 2, W + 40, y + 2, 5)
        for k in range(24):
            line(k * 90, y + 2, k * 90 + 30, y + 20, 3)


def phone(x, y, s=1.0, off=True):
    with xf(x, y, scale=s):
        rect(-60, -110, 120, 220, 6, fill="graphite", fa=235, amp=0.6)
        rect(-48, -90, 96, 170, 3, fill="night" if off else "sky", fa=200, amp=0.4)
        if off:
            circle(0, -20, 26, 5, "white", amp=0.3)
            line(0, -52, 0, -22, 5, "white", amp=0.1)
            write("关机", 0, 55, 30, c="white", align="center")


def ticket(x, y, s=1.0, rot=0.0, time_="21:00"):
    with xf(x, y, rot=rot, scale=s):
        rect(-120, -60, 240, 120, 4, fill="white", wash="sky", wa=110, amp=0.6)
        line(60, -60, 60, 60, 3, "grey", amp=0.2)
        write("车票", -60, -18, 30, align="center")
        write(time_, -60, 30, 40, style="title", c="coral", align="center")
        for k in range(4):
            dot(90, -40 + k * 26, 4, "grey")
