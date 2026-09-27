"""《书页里的人》各分镜镜头。每个镜头函数签名为 f(t, d)：t 为镜头内时间（秒），d 为镜头时长。"""
import math

from sketch import *  # noqa: F401,F403

GROUND = 900
LIN_C = (168, 72, 82)      # 林晚的铅笔（粉色铅笔写出的深玫瑰色）
X_C = "graphite"           # X 的铅笔


# ---------------------------------------------------------------- 通用

def paper_layer(alpha):
    """在新图层上先铺纸，再画内容（用于镜头内切换）"""
    return _PaperLayer(alpha)


class _PaperLayer:
    def __init__(self, alpha, cf=None):
        self.alpha = alpha
        self.cf = cf

    def __enter__(self):
        self.x = xf(alpha=self.alpha, cf=self.cf)
        self.x.__enter__()
        draw_paper()

    def __exit__(self, *e):
        self.x.__exit__()


def memory_layer(kind, alpha=1.0):
    return _PaperLayer(alpha, color_matrix(kind))


def vignette_frame(c="paper", a=255):
    """回忆画面的柔边框"""
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(180)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 40))
    G.canvas.drawRoundRect(skia.Rect.MakeXYWH(40, 40, W - 80, H - 80), 120, 120, p)


def caption(s, t, t0=0.2, x=90, y=120, size=54, dur=0.8):
    write(s, x, y, size, c="ink", reveal=lin(t, t0, t0 + dur))
    if t > t0 + dur * 0.6:
        line(x, y + 18, x + text_width(s, size) * prog(t, t0 + dur * 0.6, t0 + dur + 0.3), y + 20, 3, "coral", amp=0.6)


def interior(t, light="sun", shelf_spots=None, highlight=(1, 3), missing=None, side_shelves=True, lamp_glow=0.0):
    """图书馆三楼：窗、第七排书架、地板。返回第七排书架上各本书的位置。"""
    if light == "dusk":
        solid_rect(0, 0, W, H, "orange", 26)
    if light == "evening":
        solid_rect(0, 0, W, H, "night", 22)
    weather = {"snow": "snow", "rain": "rain"}.get(light)
    window(150, 170, 330, 400, sky="orange" if light == "dusk" else "sky", night=light == "evening", weather=weather,
           t=t, sun=light in ("sun", "spring"))
    if light == "spring":
        G.canvas.save()
        G.canvas.clipRect(skia.Rect.MakeXYWH(150, 170, 330, 400))
        particles("petal", t, 10, (150, 170, 330, 400), seed=9)
        G.canvas.restore()
    floor_boards(GROUND)
    spots = shelf(760, 330, 400, GROUND - 330, rows=5, seed=7, label="7", highlight=highlight, missing=missing)
    if side_shelves:
        shelf(1400, 330, 400, GROUND - 330, rows=5, seed=8, label="8")
    if lamp_glow > 0:
        for lx in (620, 1300):
            line(lx, 0, lx, 70, 3)
            stroke([(lx - 40, 110), (lx - 20, 70), (lx + 20, 70), (lx + 40, 110)], 4, closed=True, fill="lamp", amp=0.5)
            blob(lx, 200, 260, 220, "lamp", 70 * lamp_glow, blur=60)
    return spots


def book_cover(x, y, s=1.0, rot=0.0):
    """《霍乱时期的爱情》封面"""
    with xf(x, y, rot=rot, scale=s):
        rect(-60, -85, 120, 170, 4, fill="paper", wash="coral", wa=210, amp=0.6)
        line(-48, -85, -48, 85, 3, amp=0.3)
        write("霍乱时期", 6, -30, 22, align="center")
        write("的爱情", 6, -2, 22, align="center")
        heart(6, 40, 0.8, "white")


def chapter_card(title, icon):
    def f(t, d):
        with xf(W / 2, H / 2 - 30, scale=1 + 0.03 * t):
            write(title, 0, 0, 96, style="title", align="center", reveal=lin(t, 0.15, 1.3))
            tw = text_width(title, 96, "title")
            line(-tw / 2, 40, -tw / 2 + tw * prog(t, 0.9, 1.8), 44, 4, "coral", amp=1.0)
            a = pop(t, 1.5, 0.4)
            if a > 0:
                with xf(0, -215, scale=a):
                    icon(t)
    return f


# ---------------------------------------------------------------- 片头

def opening_book(cx, cy, bw, bh, p):
    """p=0 合上（只见封面），p=1 完全摊开"""
    cos_ = math.cos(p * math.pi)
    if cos_ > 0:
        # 封面还在右侧：底下只露出右页
        rect(cx, cy - bh / 2 + 6, bw / 2 + 8, bh, 5, fill="white", amp=1.0)
        with xf(cx, cy, sx=cos_, sy=1.0):
            rect(0, -bh / 2, bw / 2, bh, 6, fill="paper", wash="coral", wa=200, amp=1.2)
            rect(40, -bh / 2 + 40, bw / 2 - 80, bh - 80, 3, "white", amp=0.8)
            heart(bw / 4, 0, bh / 230, "white")
    else:
        page_spread(cx, cy, bw, bh, lines=0)
        if cos_ > -0.999:
            with xf(cx, cy, sx=cos_, sy=1.0):
                rect(0, -bh / 2, bw / 2, bh, 6, fill="white", amp=1.2)


def s_title(t, d):
    bw, bh = 1300, 700
    p = prog(t, 0.6, 2.4)
    cx, cy = lerp(W / 2 - bw / 4, W / 2, p), H / 2 + 20
    particles("dust", t, 30, (0, 0, W, H), seed=3, speed=0.3)
    opening_book(cx, cy, bw, bh, p)
    if p >= 1:
        tip = write("书页里的人", cx, cy + 10, 150, style="title", align="center", reveal=lin(t, 2.9, 6.0))
        if t < 6.2:
            draw_pencil(tip[0] + 10, tip[1] - 30, 1.1)
        sub = "一个关于字迹与等待的故事"
        write(sub, cx, cy + 150, 42, c="grey", align="center", a=255 * prog(t, 6.3, 7.3))
        for k in range(3):
            heart(cx - 260 + k * 260, cy - 190, 0.9 * pop(t, 6.6 + k * 0.2), "pink")


# ---------------------------------------------------------------- 第一章

def icon_pencil(t):
    with xf(-20, 60, rot=0):
        draw_pencil(0, 0, 0.9, wig=False)


def s1_1(t, d):
    """图书馆外观，秋天"""
    z = 1.0 + 0.05 * t / d
    with cam(z, W / 2, H / 2 + 60):
        ground(950)
        tree(250, 950, 1.3, "autumn", sway=math.sin(t) * 4)
        tree(1680, 950, 1.2, "autumn", sway=math.sin(t + 1) * 4)
        building(W / 2 + 40, 950, 1.0)
        x = lerp(330, 870, lin(t, 0.3, 5.8))
        person("girl", x, 950, 1.0, face=1, walk=t * 7, expr="smile",
               arms=((-20, 10), (40, 80)))
        book_closed(x + 32, 950 - 108, 26, 34, c="blue")
    particles("leaf", t, 16, (0, -60, W, H), seed=2, speed=0.8, wind=0.2)
    caption("大二 · 秋天", t, 0.4)


def s1_2(t, d):
    """林晚在第七排抽出那本书"""
    z = lerp(1.0, 1.35, prog(t, 5.8, 8.6))
    with cam(z, lerp(W / 2, 760, prog(t, 5.8, 8.6)), lerp(H / 2, 560, prog(t, 5.8, 8.6))):
        taken = t > 4.9
        spots = interior(t, "sun", missing=(1, 3) if taken else None)
        bx, by, bw, bh = spots[(1, 3)]
        x = lerp(-60, 700, prog(t, 0.0, 3.0))
        walking = t < 3.0
        if 3.2 < t < 5.4:
            reach = prog(t, 3.2, 4.0)
            arms = ((-20, 10), (lerp(30, 150, reach), lerp(20, -30, reach)))
        else:
            arms = ((-20, 10), (40, 80)) if taken else None
        pp = person("girl", x, GROUND, 1.8, face=1, walk=t * 8 if walking else None, arms=arms,
                    expr="happy" if t > 6.2 else "smile", blush=prog(t, 6.2, 7.0))
        if taken:
            hx, hy = pp["hands"][1]
            if t < 5.8:
                k = prog(t, 4.9, 5.8)
                book_closed(lerp(bx, hx + 10, k), lerp(by, hy - 20, k), bw, bh, c="coral")
            else:
                book_cover(hx + 16, hy - 50, 0.75 * lerp(0.8, 1.0, prog(t, 5.8, 6.4)))
        if t > 6.8:
            sparkle(pp["head"][0] + 80, pp["head"][1] - 50, pop(t, 6.8) * 1.2)
            sparkle(pp["head"][0] + 130, pp["head"][1] + 10, pop(t, 7.1) * 0.8)
    if t < 3.2:
        caption("第七排", t, 0.6, x=W - 360)


def s1_3(t, d):
    """书页特写：X 的批注与林晚的回复"""
    z = 1.0 + 0.03 * t / d
    with cam(z):
        page_spread(W / 2, H / 2 + 20, 1640, 860, lines=10, seed=4)
        write("“……爱情，离死亡越近越浓郁。”", 170, 230, 40, c="grey")
        # 高亮这句
        if t > 0.6:
            stroke([(160, 245), (160 + 620 * prog(t, 0.6, 1.4), 248)], 10, "yellow", 150, amp=0.8)
        a = prog(t, 1.4, 2.4)
        write("可惜大多数人，", 1000, 300, 58, style="x", c=X_C, a=255 * a)
        write("都等不到那么近。", 1000, 380, 58, style="x", c=X_C, a=255 * a)
        if t > 2.2:
            circle(1260, 340, 290 * pop(t, 2.2, 0.5), 3, "coral", 180, ry=110, amp=2.0)
        tip = write("那就别等。", 1080, 590, 66, c=LIN_C, reveal=lin(t, 4.6, 7.0))
        if 4.0 < t < 7.6:
            draw_pencil(tip[0] + 10, tip[1] - 16, 1.0)


def s1_4(t, d):
    """日历翻到周三 → 新的回信"""
    if t < 2.6:
        calendar(W / 2, H / 2, 1.6, top="九月", big="周一" if t < 0.7 else "周三", flip=lin(t, 0.7, 1.6))
        for k in range(3):
            sparkle(W / 2 + 230 + k * 50, H / 2 - 220 + k * 70, pop(t, 1.5 + k * 0.15) * 0.8)
    a = prog(t, 2.3, 2.9)
    if a > 0:
        with paper_layer(a):
            with cam(1.04):
                page_spread(W / 2, H / 2 + 20, 1640, 860, lines=10, seed=4)
                write("可惜大多数人，", 1000, 300, 58, style="x", c=X_C)
                write("都等不到那么近。", 1000, 380, 58, style="x", c=X_C)
                write("那就别等。", 1080, 520, 66, c=LIN_C)
                write("我们，算是认识了吗？", 1000, 680, 58, style="x", c=X_C, reveal=lin(t, 3.2, 5.0))
                write("——X", 1450, 770, 58, style="x", c=X_C, a=255 * prog(t, 5.0, 5.5))


EXCHANGES = [
    (("你最喜欢马尔克斯的哪一本？", "x"), ("当然是这一本。", "lin"), "book"),
    (("食堂新出的麻辣香锅，", "lin"), ("辣哭了。", "lin"), "bowl"),
    (("失眠的夜里，你听什么歌？", "x"), ("听雨声。你呢？", "lin"), "moon"),
]


def doodle(kind, x, y, s=1.0):
    with xf(x, y, scale=s):
        if kind == "book":
            book_cover(0, 0, 0.6)
            heart(46, -50, 0.7)
        elif kind == "bowl":
            stroke(circle_pts(0, 0, 70, 50, 20, 0, math.pi), 4, closed=True, fill="white", wash="red", wa=110)
            line(-80, 0, 80, 0, 4)
            for k in (-30, 0, 30):
                ph = G.t * 2 + k
                stroke([(k, -20), (k + 8 * math.sin(ph), -45), (k, -70)], 3, "grey", smooth=True, amp=0.3)
            stroke([(50, -10), (70, -30), (60, 5)], 3, closed=True, fill="red", amp=0.3)
        elif kind == "moon":
            stroke(circle_pts(0, 0, 50, None, 20, math.pi * 0.35, math.pi * 1.65) +
                   circle_pts(-26, 0, 42, None, 20, math.pi * 1.6, math.pi * 0.4 - 0.01)[::-1] if False else
                   circle_pts(0, 0, 50, None, 24), 4, closed=True, fill="yellow", amp=0.5)
            circle(22, -8, 44, 0, fill="white", line=False)
            for k in range(3):
                sparkle(70 + k * 30, -60 + k * 40, 0.5)
            arc(-10, 90, 40, 180, 360, 5)
            rect(-58, 80, 18, 34, 4, fill="coral", amp=0.3)
            rect(22, 80, 18, 34, 4, fill="coral", amp=0.3)


def s1_5(t, d):
    """蒙太奇：书页上的聊天"""
    seg = 3.0
    if t < 9.0:
        i = min(2, int(t / seg))
        lt = t - i * seg
        page_spread(W / 2, H / 2 + 20, 1640, 860, lines=10, seed=10 + i, flip=lin(lt, 0, 0.45) if i > 0 else 0)
        (q, qs), (a_, as_), dk = EXCHANGES[i]
        qx, ax = 190, 1000
        qc = X_C if qs == "x" else LIN_C
        write(q, qx, 330, 54, style="x" if qs == "x" else "plain", c=qc, reveal=lin(lt, 0.3, 1.3))
        if i == 1:
            write(a_, qx + 60, 420, 54, c=LIN_C, reveal=lin(lt, 1.2, 1.6))
            write("下次加一份冰粉。", ax, 330, 54, style="x", c=X_C, reveal=lin(lt, 1.6, 2.5))
            write("——X", ax + 330, 410, 50, style="x", c=X_C, reveal=lin(lt, 2.4, 2.7))
        else:
            write(a_, ax if qs == "x" else qx, 330 if qs == "x" else 420, 54, style="plain" if as_ == "lin" else "x",
                  c=LIN_C if as_ == "lin" else X_C, reveal=lin(lt, 1.3, 2.2))
        s = pop(lt, 1.0, 0.4)
        if s > 0:
            doodle(dk, 480 if i != 1 else 1300, 700 if i != 1 else 680, s * 1.3)
        if i == 2 and lt > 2.2:
            write("我也是。——X", 1000, 440, 54, style="x", c=X_C, reveal=lin(lt, 2.2, 2.9))
    a = prog(t, 8.8, 9.3)
    if a > 0:
        with paper_layer(a):
            interior(t, "sun", missing=(1, 3))
            pp = person("girl", 700, GROUND, 1.9, face=0, expr="happy", blush=1.0,
                        arms=((-30, 100), (30, -100)), tilt=math.sin(t * 2) * 6)
            hx = (pp["hands"][0][0] + pp["hands"][1][0]) / 2
            hy = (pp["hands"][0][1] + pp["hands"][1][1]) / 2
            book_cover(hx, hy - 10, 0.7)
            for k in range(4):
                ph = ((t - 9.2) * 0.45 + k * 0.25) % 1.0
                if t > 9.2 + k * 0.3:
                    heart(hx + math.sin(ph * 6 + k) * 60 + (k - 1.5) * 50, hy - 150 - ph * 300, 1.0 * (1 - ph * 0.5),
                          "pink", 255 * (1 - ph))


# ---------------------------------------------------------------- 第二章

def icon_question(t):
    bubble(0, 0, 150, 110, tail=(-60, 90), kind="thought")
    write("X?", 0, 20, 56, style="title", align="center")


def s2_1(t, d):
    """许知行推车来到第七排，拿起那本书；林晚躲在书架后偷看"""
    spots = interior(t, "sun", side_shelves=False, missing=(1, 3) if 3.8 < t else None)
    bx, by, bw, bh = spots[(1, 3)]
    # 许知行
    x = lerp(W + 150, 1300, prog(t, 0.0, 3.4))
    walking = t < 3.4
    if t < 3.6:
        arms = ((-60, -20), (-40, -30))
        pp = person("boy", x, GROUND, 1.8, face=-1, walk=t * 7 if walking else None, arms=arms, expr="neutral")
        cart(x - 230, GROUND, 1.0, roll=-t * 5)
    else:
        cart(1070, GROUND, 1.0, roll=0)
        reach = prog(t, 3.6, 4.2)
        if t < 5.2:
            arms = ((lerp(-20, -150, reach), lerp(-10, 30, reach)), (15, -8))
        else:
            arms = ((-40, -80), (20, -10))
        pp = person("boy", 1300, GROUND, 1.8, face=-1, arms=arms, expr="smile" if t > 5.4 else "neutral",
                    look=-4)
        if t > 3.8:
            hx, hy = pp["hands"][0]
            k = prog(t, 3.8, 5.0)
            if t < 5.2:
                book_closed(lerp(bx, hx - 10, k), lerp(by, hy - 10, k), bw, bh, c="coral")
            else:
                book_cover(hx - 10, hy - 40, 0.7)
    # 林晚在左边书架后
    shelf_x = 180
    peek = prog(t, 1.2, 2.2)
    person("girl", shelf_x + 330 + 40 * peek, GROUND, 1.8, face=1, expr="surprise" if t > 5.4 else "smile",
           blush=prog(t, 6.0, 7.0), tilt=12 * peek, arms=((-10, 10), (20, 110)))
    shelf(shelf_x, 330, 330, GROUND - 330, rows=5, seed=11, label="6")
    if t > 5.8:
        s = pop(t, 5.8, 0.4)
        bubble(760, 300, 200, 150, tail=(600, 470), kind="thought", s=s)
        if s > 0:
            write("X?", 760, 322, 70 * s, style="title", align="center")
        sparkle(880, 220, pop(t, 6.4) * 1.1)
        sparkle(900, 360, pop(t, 6.7) * 0.7)


def panel(x, y, w_, h_, a=1.0):
    class _P:
        def __enter__(self_):
            self_.x = xf(alpha=a)
            self_.x.__enter__()
            G.canvas.save()
            G.canvas.clipRect(skia.Rect.MakeXYWH(x, y, w_, h_))
            draw_paper()
            return self_

        def __exit__(self_, *e):
            G.canvas.restore()
            rect(x, y, w_, h_, 6, amp=1.2)
            self_.x.__exit__()
    return _P()


def door_frame(x, base, w_=300, h_=460):
    stroke([(x - w_ / 2, base), (x - w_ / 2, base - h_), (x + w_ / 2, base - h_), (x + w_ / 2, base)], 6, amp=1.0)
    rect(x - w_ / 2 - 30, base - h_ - 60, w_ + 60, 60, 5, fill="paper", wash="coral", wa=140, amp=0.8)


def s2_2(t, d):
    """蒙太奇：递伞 / 闭馆后等她"""
    # 左格：下雨天递伞
    with panel(60, 150, 880, 780, a=prog(t, 0, 0.4)):
        G.canvas.save()
        G.canvas.clipRect(skia.Rect.MakeXYWH(60, 150, 880, 780))
        particles("rain", t, 40, (60, 150, 880, 780), seed=4, wind=0.3)
        G.canvas.restore()
        door_frame(360, 830, 330, 500)
        line(60, 830, 940, 830, 5)
        lx = 360
        got = t > 3.0
        person("girl", lx, 830, 1.35, face=1, expr="smile" if got else "sad", blush=prog(t, 3.4, 4.2),
               arms=((-20, 10), (100, 40)) if got else ((-20, 10), (20, -10)))
        bx = lerp(980, 600, prog(t, 0.6, 2.4))
        pp = person("boy", bx, 830, 1.35, face=-1, walk=t * 7 if t < 2.4 else None, expr="smile",
                    arms=((-150, 20), (20, -10)) if not got else ((-20, -10), (20, -10)))
        if not got:
            hx, hy = pp["hands"][0]
            umbrella(hx, hy, 0.8, rot=lerp(0, -40, prog(t, 2.4, 3.0)))
        else:
            umbrella(lx + 70, 830 - 145, 0.9, rot=-5, c="blue")
        if t > 3.3:
            heart(lx + 110, 830 - 380, pop(t, 3.4) * 1.1)
    # 右格：闭馆后，他拿着钥匙等她
    if t > 5.6:
        rt = t - 5.6
        with panel(980, 150, 880, 780, a=prog(rt, 0, 0.4)):
            line(980, 830, 1860, 830, 5)
            clock(1420, 300, 80, hh=9, mm=lerp(0, 20, lin(rt, 0, 5)))
            write("闭馆", 1420, 440, 40, c="coral", align="center")
            # 桌子
            person("girl", 1200, 830, 1.35, face=1, expr="happy" if rt > 3 else "worried",
                   arms=((-40, 60), (60, 60)) if rt < 3 else ((-20, 10), (20, -10)), backpack=rt > 3)
            rect(1110, 700, 250, 20, 4, fill="paper", wash="wood", wa=160)
            line(1130, 720, 1130, 830, 4)
            line(1340, 720, 1340, 830, 4)
            for k in range(3 if rt < 3 else 0):
                book_closed(1160 + k * 50, 675, 36, 30, c=["blue", "green", "coral"][k])
            pp = person("boy", 1640, 830, 1.35, face=-1, expr="smile", arms=((-60, -10), (20, -10)))
            hx, hy = pp["hands"][0]
            sw = math.sin(G.t * 6) * 10
            circle(hx, hy + 18, 14, 3.5, "yellow", amp=0.3)
            line(hx + sw * 0.3, hy + 30, hx + sw, hy + 55, 4, "yellow")
            if rt > 3.4:
                heart(1420, 560, pop(rt, 3.5) * 1.1)


def s2_3(t, d):
    """楼梯口：“X?” —— 点头"""
    snow = True
    # 窗与雪
    window(1300, 150, 360, 380, weather="snow", t=t, sun=False)
    # 楼梯（右侧向上）
    base = GROUND
    for k in range(7):
        x0 = 1000 + k * 80
        y0 = base - k * 50
        stroke([(x0, y0), (x0, y0 - 50), (x0 + 80, y0 - 50)], 5, amp=0.8)
    line(1000, base, 1000 + 560, base - 350, 3, "wood")
    line(-10, base, 1000, base, 5, amp=1.5)
    # 灯（闪烁）
    flick = 1.0
    if 4.8 < t < 8.2:
        flick = 0.25 if int(t * 7) % 3 == 0 else 1.0
    line(760, 0, 760, 90, 3)
    stroke([(710, 140), (735, 90), (785, 90), (810, 140)], 4, closed=True, fill="lamp", amp=0.5)
    blob(760, 300, 330, 300, "lamp", 60 * flick, blur=60)
    # 铃
    ring_bell(260, 230, 0.9, t, ringing=0.3 < t < 2.4)
    # 许知行下楼
    fx = lerp(1450, 1060, prog(t, 0.6, 2.8))
    fy = base - max(0, (fx - 1000)) * 50 / 80
    nod = 0.0
    if 8.4 < t < 9.6:
        nod = math.sin((t - 8.4) / 1.2 * math.pi * 2) * 7
    expr = "neutral"
    if 4.2 < t < 8.4:
        expr = "surprise"
    elif t >= 8.4:
        expr = "happy"
    person("boy", fx, fy, 1.8, face=-1, walk=t * 7 if t < 2.8 else None, expr=expr, sweat_=4.6 < t < 8.4,
           blush=prog(t, 8.6, 9.4), nod=nod, arms=((-30, -20), (20, -10)) if t < 10 else ((-60, -30), (20, -10)))
    # 林晚
    point = prog(t, 3.2, 3.7)
    lin_arms = ((-20, 10), (lerp(20, 80, point), lerp(-10, 0, point))) if t < 10 else ((-20, 10), (60, 10))
    person("girl", 720, base, 1.8, face=1, expr="smile" if t < 8.6 else "happy", blush=prog(t, 3.0, 4.0),
           arms=lin_arms)
    if 3.6 < t < 8.4:
        bubble(640, 350, 190, 140, tail=(700, 560), s=pop(t, 3.6), a=255 * (1 - prog(t, 8.0, 8.4)))
        if t > 3.8:
            write("X?", 640, 372, 70, style="title", align="center", a=255 * (1 - prog(t, 8.0, 8.4)))
    if 5.8 < t < 8.4:
        bubble(1160, 360, 170, 120, tail=(1100, 520), s=pop(t, 5.8), a=255 * (1 - prog(t, 8.0, 8.4)))
        n_dots = min(3, int((t - 6.0) / 0.5) + 1)
        for k in range(n_dots):
            dot(1125 + k * 35, 365, 8)
    if t > 9.0:
        heart(900, 440 - (t - 9.0) * 8, pop(t, 9.0, 0.45) * 3.2)
        for k in range(4):
            sparkle(900 + math.cos(k * 1.6) * 170, 440 + math.sin(k * 1.6) * 130, pop(t, 9.3 + k * 0.12))
    caption("十二月", t, 0.3, x=90, y=110)


def s2_4(t, d):
    """甜蜜三连格"""
    pw = 560
    xs = [60, 60 + pw + 40, 60 + 2 * (pw + 40)]
    # ① 香菜
    with panel(xs[0], 190, pw, 700, a=prog(t, 0, 0.3)):
        x0 = xs[0]
        person("girl", x0 + 170, 820, 1.25, face=1, expr="happy" if t > 1.9 else "worried", blush=0.6)
        person("boy", x0 + 400, 820, 1.25, face=-1, expr="smile", arms=((-110, -20), (20, -10)))
        rect(x0 + 20, 640, pw - 40, 22, 4, fill="paper", wash="wood", wa=160)
        for bx_ in (x0 + 190, x0 + 380):
            stroke(circle_pts(bx_, 620, 60, 40, 16, 0, math.pi), 4, closed=True, fill="white", wash="yellow", wa=90)
            line(bx_ - 66, 620, bx_ + 66, 620, 4)
        k = prog(t, 0.6, 1.8)
        cx_, cy_ = lerp(x0 + 190, x0 + 380, k), 600 - math.sin(k * math.pi) * 90
        line(cx_ + 20, cy_ - 60, cx_ + 4, cy_ - 2, 3, "wood")
        line(cx_ + 34, cy_ - 58, cx_ + 10, cy_ + 2, 3, "wood")
        for j in range(3):
            circle(cx_ + (j - 1) * 10, cy_ + 2, 7, 2.5, "green", fill="green", fa=220, amp=0.3)
        write("香菜", x0 + 190, 700, 30, c="green", align="center", a=255 * (1 - k))
    # ② 热水袋
    if t > 2.8:
        lt = t - 2.8
        with panel(xs[1], 190, pw, 700, a=prog(lt, 0, 0.3)):
            x0 = xs[1]
            person("girl", x0 + 170, 820, 1.25, face=-1, expr="smile" if lt < 1.8 else "surprise", backpack=True,
                   blush=prog(lt, 1.8, 2.4), look=-7 if lt < 1.6 else 7)
            pp = person("boy", x0 + 430, 820, 1.25, face=-1, expr="smile", arms=((-80, 0), (20, -10)))
            k = prog(lt, 0.4, 1.4)
            hx, hy = lerp(pp["hands"][0][0], x0 + 210, k), lerp(pp["hands"][0][1], 640, k)
            stroke([(hx - 26, hy - 26), (hx + 26, hy - 26), (hx + 32, hy + 30), (hx - 32, hy + 30)], 4, closed=True,
                   smooth=True, fill="pink", amp=0.4)
            rect(hx - 10, hy - 42, 20, 16, 3, fill="coral", amp=0.2)
            if lt > 1.8:
                for j in range(3):
                    ph = ((lt - 1.8) * 0.8 + j * 0.33) % 1
                    stroke([(x0 + 200 + (j - 1) * 20, 600 - ph * 60), (x0 + 210 + (j - 1) * 20, 580 - ph * 60),
                            (x0 + 200 + (j - 1) * 20, 560 - ph * 60)], 3, "coral", 255 * (1 - ph), smooth=True)
    # ③ 操场夜走
    if t > 5.6:
        lt = t - 5.6
        with panel(xs[2], 190, pw, 700, a=prog(lt, 0, 0.3)):
            x0 = xs[2]
            solid_rect(x0, 190, pw, 700, "night", 60)
            circle(x0 + 430, 300, 50, 4, fill="yellow", amp=0.5)
            for j in range(5):
                sparkle(x0 + 60 + j * 90, 260 + (j % 2) * 60, 0.5, "white")
            stroke(circle_pts(x0 + pw / 2, 660, 240, 110, 40), 6, closed=True, c="coral", amp=1.0)
            stroke(circle_pts(x0 + pw / 2, 660, 190, 75, 40), 4, closed=True, c="white", amp=1.0)
            ang = lt * 0.9
            for j, kind in enumerate(("girl", "boy")):
                a_ = ang + j * 0.14
                px = x0 + pw / 2 + math.cos(a_) * 215
                py = 660 + math.sin(a_) * 92
                person(kind, px, py + 60, 0.55, face=-1 if math.sin(a_) > 0 else 1, walk=lt * 8, expr="happy",
                       arms=((-20, 10), (60, 10)) if kind == "girl" else ((-60, -10), (20, -10)))
            heart(x0 + pw / 2, 480, pop(lt, 1.0) * 1.3)


# ---------------------------------------------------------------- 第三章

def icon_neq(t):
    write("≠", 0, 40, 150, style="title", c="red", align="center")


def s3_1(t, d):
    """三月：新的回信"""
    if t < 2.3:
        interior(t, "spring", missing=(1, 3))
        pp = person("girl", 700, GROUND, 1.9, face=1, expr="smile", arms=((-20, 10), (40, 80)))
        hx, hy = pp["hands"][1]
        book_open_small(hx + 20, hy - 20, 110, 72)
        caption("三月", t, 0.2)
    a = prog(t, 2.0, 2.6)
    if a > 0:
        with paper_layer(a):
            with cam(1.0 + 0.04 * (t - 2) / 4):
                page_spread(W / 2, H / 2 + 20, 1640, 860, lines=10, seed=21)
                write("很久没见你回信了。", 1000, 360, 60, style="x", c=X_C, reveal=lin(t, 2.6, 4.0))
                write("希望你一切都好。", 1000, 460, 60, style="x", c=X_C, reveal=lin(t, 4.0, 5.2))
                write("——X", 1440, 560, 60, style="x", c=X_C, reveal=lin(t, 5.2, 5.6))


def s3_2(t, d):
    """分屏：同一个下午，他在考场"""
    with panel(60, 170, 880, 760):
        line(60, 840, 940, 840, 5)
        clock(500, 290, 70, hh=3, mm=0)
        for k, dx in enumerate((200, 700)):
            rect(dx - 110, 690, 220, 18, 4, fill="paper", wash="wood", wa=160)
            line(dx - 90, 708, dx - 90, 840, 4)
            line(dx + 90, 708, dx + 90, 840, 4)
        person("kid", 700, 840, 1.1, face=-1, expr="neutral", arms=((-70, -30), (20, -10)), hair="short", skirt=None)
        pp = person("boy", 230, 840, 1.25, face=1, expr="neutral", arms=((-20, 10), (70, 40)), tilt=10, nod=4)
        hx, hy = pp["hands"][1]
        rect(hx - 20, 670, 120, 20, 3, fill="white")
        draw_pencil(hx + 20, 670, 0.4)
        write("考试中", 500, 430, 40, c="coral", align="center")
    with panel(980, 170, 880, 760):
        line(980, 840, 1860, 840, 5)
        pp = person("girl", 1420, 840, 1.4, face=0, expr="surprise" if t > 2.4 else "neutral",
                    arms=((-30, 100), (30, -100)))
        hx = (pp["hands"][0][0] + pp["hands"][1][0]) / 2
        book_open_small(hx, pp["hands"][0][1] - 10, 100, 64)
        if t > 2.4:
            bubble(1620, 380, 180, 130, tail=(1500, 480), s=pop(t, 2.4))
            write("?!", 1620, 405, 70, style="title", c="red", align="center")
    write("同一个下午", W / 2, 120, 54, align="center", reveal=lin(t, 0.2, 1.0))


def s3_3(t, d):
    """笔迹对比：≠"""
    # 左：书页
    with xf(0, 0, rot=-2):
        rect(170, 240, 700, 560, 5, fill="white", amp=1.0)
        for k in range(8):
            line(210, 290 + k * 62, 820, 292 + k * 62, 3, "lgrey", amp=0.4)
        write("希望你", 260, 470, 90, style="x", c=X_C)
        write("一切都好。", 300, 590, 90, style="x", c=X_C)
        write("书页", 520, 760, 36, c="grey", align="center")
    # 右：笔记本
    with xf(0, 0, rot=2):
        rect(1050, 240, 700, 560, 5, fill="paper", wash="blue", wa=120, amp=1.0)
        rect(1090, 280, 620, 480, 4, fill="white", amp=0.8)
        for k in range(7):
            line(1110, 330 + k * 62, 1690, 332 + k * 62, 3, "sky", amp=0.4)
        write("许知行", 1140, 440, 90, style="xu")
        write("高数笔记", 1180, 570, 80, style="xu")
        write("∫ f(x) dx", 1200, 690, 50, c="grey")
    # 放大镜
    mp = prog(t, 0.6, 3.6)
    mx = lerp(420, 1400, mp)
    my = 500 + math.sin(mp * math.pi) * -80
    if t < 4.2:
        circle(mx, my, 110, 7, fill="sky", fa=40, amp=0.5)
        line(mx + 80, my + 80, mx + 170, my + 170, 14, "wood", amp=0.3)
    # ≠
    if t > 4.2:
        s = pop(t, 4.2, 0.4)
        with xf(W / 2, 540, scale=s):
            line(-70, -25, 70, -25, 16, "red", amp=1.0)
            line(-70, 25, 70, 25, 16, "red", amp=1.0)
            line(40, -80, -40, 80, 16, "red", amp=1.0)


def s3_4(t, d):
    """对峙、心碎、转身离开"""
    grey = prog(t, 7.0, 10.5)
    z = lerp(1.0, 1.25, prog(t, 8.0, 12.0))
    cx = lerp(W / 2, 1180, prog(t, 8.0, 12.0))
    with cam(z, cx, lerp(H / 2, 520, prog(t, 8.0, 12.0))):
        with xf(cf=color_matrix("grey", grey)):
            draw_paper()
            interior(t, "spring" if t < 7 else "sun", side_shelves=False, missing=(1, 3))
            # 林晚
            if t < 5.8:
                raise_ = prog(t, 0.2, 0.9)
                pp = person("girl", 700, GROUND, 1.8, face=1, expr="sad",
                            arms=((lerp(-20, -120, raise_), 20), (lerp(20, 120, raise_), -20)))
                book_open_small(pp["hands"][0][0] - 10, pp["hands"][0][1] - 20, 90, 60)
                rect(pp["hands"][1][0] - 30, pp["hands"][1][1] - 55, 60, 80, 4, fill="paper", wash="blue", wa=150, amp=0.4)
            else:
                lx = lerp(700, -150, prog(t, 6.2, 9.8))
                person("girl", lx, GROUND, 1.8, face=-1 if t > 6.0 else 1, walk=(t - 6.2) * 8 if t > 6.2 else None,
                       expr="cry", tears=1.0, scarf_wind=0.8)
            # 许知行
            head_down = prog(t, 1.4, 2.4)
            pp = person("boy", 1220, GROUND, 1.8, face=-1, expr="sad" if t < 7 else "cry",
                        tilt=-14 * head_down, nod=6 * head_down, sweat_=1.6 < t < 5.8,
                        arms=((-20, -10), (160, 60)) if 2.2 < t < 4.4 else ((-15, -8), (15, 8)),
                        tears=0.6 if t > 8.5 else 0)
            if 2.4 < t < 5.0:
                bubble(1330, 360, 160, 110, tail=(1270, 500), s=pop(t, 2.4),
                       a=255 * (1 - prog(t, 4.6, 5.0)))
                for k in range(3):
                    dot(1297 + k * 33, 365, 7)
            if t > 4.3:
                br = prog(t, 5.0, 6.2)
                heart(960, 470 + br * 60, pop(t, 4.3, 0.4) * 3.0, "pink", 255 * (1 - prog(t, 7.5, 8.5)), broken=br)
            if t > 8.0:
                rain_cloud(1225, 330, 1.2 * prog(t, 8.0, 8.8), t)
    particles("petal", t, 18, (0, 0, W, H), seed=12, a=255 * (1 - grey * 0.7), wind=-0.6 if t > 6 else 0)


# ---------------------------------------------------------------- 第四章

def icon_x(t):
    circle(0, 10, 80, 5, fill="white", amp=1.0)
    write("X", 0, 45, 100, style="x", c=X_C, align="center")


def s4_1(t, d):
    """林晚写下邀约"""
    with cam(1.0 + 0.03 * t / d):
        page_spread(W / 2, H / 2 + 20, 1640, 860, lines=10, seed=31)
        write("很久没见你回信了。", 190, 300, 44, style="x", c=X_C, a=150)
        write("希望你一切都好。——X", 190, 370, 44, style="x", c=X_C, a=150)
        tip = write("我想见你。", 1000, 360, 72, c=LIN_C, reveal=lin(t, 0.5, 2.0))
        if t > 2.0:
            tip = write("周三，闭馆前，第七排。", 1000, 480, 60, c=LIN_C, reveal=lin(t, 2.2, 4.4))
        if 0.3 < t < 4.8:
            draw_pencil(tip[0] + 10, tip[1] - 16, 1.0)
        if t > 4.8:
            with xf(1640, 640, scale=pop(t, 4.8)):
                clock(0, 0, 60, hh=9, mm=0)


def s4_2(t, d):
    """等待，黄昏；尽头出现的人影"""
    interior(t, "dusk", side_shelves=False, missing=(1, 3), highlight=None)
    clock(1600, 240, 80, hh=8 + lerp(40, 60, lin(t, 0, 4.5)) / 60, mm=lerp(40, 60, lin(t, 0, 4.5)))
    wait_look = -1 if t > 3.8 else (1 if int(t / 1.3) % 2 == 0 else -1)
    person("girl", 1330, GROUND, 1.8, face=wait_look, expr="surprise" if t > 6.0 else "worried",
           arms=((-30, 100), (30, -100)) if t < 6.0 else ((-110, -20), (20, -10)))
    if t < 6.0:
        book_cover(1330, GROUND - 190, 0.55)
    # 人影 → 周老师
    ox = lerp(-120, 480, prog(t, 3.8, 6.2))
    rev = prog(t, 5.8, 7.0)
    if t > 3.8:
        with xf(alpha=1.0 - rev):
            with xf(cf=skia.ColorFilters.Blend(col("graphite", 255), skia.BlendMode.kSrcIn)):
                person("old", ox, GROUND, 1.8, face=1, walk=(t - 3.8) * 4 if t < 6.2 else None, expr="smile")
        with xf(alpha=rev):
            person("old", ox, GROUND, 1.8, face=1, walk=(t - 3.8) * 4 if t < 6.2 else None,
                   expr="happy" if t > 7.2 else "smile", lean=lerp(12, 22, prog(t, 7.4, 8.2)))
    if t > 6.0:
        bubble(1450, 360, 150, 130, tail=(1390, 520), s=pop(t, 6.0))
        write("!", 1450, 392, 80, style="title", c="red", align="center")
    if 7.3 < t:
        sparkle(560, 440, pop(t, 7.4) * 0.9)
        sparkle(420, 400, pop(t, 7.6) * 0.7)


def bench(x, base, w_=380):
    rect(x - w_ / 2, base - 120, w_, 18, 4, fill="paper", wash="wood", wa=160)
    rect(x - w_ / 2, base - 210, w_, 16, 4, fill="paper", wash="wood", wa=160)
    for dx in (-w_ / 2 + 30, w_ / 2 - 30):
        line(x + dx, base - 102, x + dx, base, 4)


def s4_3(t, d):
    """回忆：他和老伴一起读书 → 一个人写字"""
    mem = prog(t, 0.8, 1.6) * (1 - prog(t, 6.6, 7.4))
    # 现实
    person("old", 560, GROUND, 1.8, face=1, expr="closed" if t > 7.6 else "smile",
           lean=lerp(12, 28, prog(t, 8.2, 9.2)) if t < 10.8 else lerp(28, 12, prog(t, 10.8, 11.6)),
           arms=((-20, -10), (20, 110)) if t > 7.8 else None)
    ground(GROUND)
    person("girl", 1150, GROUND, 1.8, face=-1, expr="sad" if t > 7.6 else "neutral", tears=prog(t, 8.5, 9.5),
           arms=((-30, 100), (30, -100)))
    book_cover(1150, GROUND - 190, 0.55)
    if t > 9.2:
        ph = (t - 9.2) / 2.8
        heart(700, 400 - ph * 150, 1.5 * pop(t, 9.2), "pink", 255 * (1 - ph * 0.6))
    if mem > 0:
        with memory_layer("sepia", mem):
            ground(840)
            tree(1400, 840, 1.4, "summer")
            bench(900, 840)
            if t < 4.4:
                # 年轻的他和她并肩读一本书
                person("boy", 820, 716, 1.5, face=1, sit=True, badge=False, glasses=True, hair="neat", expr="happy",
                       arms=((-20, 10), (60, 70)))
                person("girl", 990, 716, 1.5, face=-1, sit=True, scarf=False, hair="long", flower=True,
                       expr="happy", skirt="pink", arms=((-60, -70), (20, -10)))
                book_open_small(905, 610, 110, 70)
                heart(905, 440, pop(t, 1.8) * 1.2)
            else:
                # 空了一半的长椅
                person("old", 820, 716, 1.5, face=1, sit=True, cane=False, expr="smile", lean=10,
                       arms=((-20, 10), (60, 70)))
                book_open_small(905, 640, 110, 70)
                draw_pencil(935, 630, 0.35)
                write("?", 1000, 640, 40, style="x", c=X_C, a=0)
                particles("leaf", t, 10, (500, 200, 1000, 640), seed=21, speed=0.6)
                if t > 5.2:
                    stroke(heart_pts(1000, 620, 1.6), 3, "ink", 200, closed=True, amp=0.6)
            vignette_frame()
            write("很多年以前", 160, 150, 48, c="ink", a=255 * prog(t, 1.4, 2.2) * (1 - prog(t, 4.0, 4.4)))
            write("后来", 160, 150, 48, c="ink", a=255 * prog(t, 4.6, 5.2))


def s4_4(t, d):
    """真相：他一直在守着这本书"""
    mem = prog(t, 1.6, 2.4) * (1 - prog(t, 12.6, 13.3))
    # 现实
    point = prog(t, 0.2, 0.9)
    person("old", 560, GROUND, 1.8, face=1, expr="smile", arms=((-20, -10), (lerp(20, 100, point), -10)))
    ground(GROUND)
    surprise = t > 13.0
    person("girl", 1150, GROUND, 1.8, face=-1 if t < 13.0 else 0, expr="cry" if surprise else "neutral",
           tears=1.0 if surprise else 0, arms=((-160, 40), (160, -40)) if surprise else ((-30, 100), (30, -100)),
           blush=prog(t, 13.4, 14.0))
    if not surprise:
        book_cover(1150, GROUND - 190, 0.55)
    if t > 13.6:
        for k in range(5):
            sparkle(1150 + math.cos(k * 1.3) * 180, 470 + math.sin(k * 1.3) * 120, pop(t, 13.6 + k * 0.1))
    if mem <= 0:
        return
    with memory_layer("memory", mem):
        lt = t
        if lt < 6.6:
            # a. 从“剔旧”箱里把书捞回来
            ground(GROUND)
            rect(260, GROUND - 170, 320, 170, 5, fill="paper", wash="wood", wa=190, amp=1.0)
            line(260, GROUND - 170, 220, GROUND - 230, 5)
            line(580, GROUND - 170, 620, GROUND - 230, 5)
            write("剔旧", 420, GROUND - 70, 60, style="title", c="red", align="center")
            for k in range(4):
                book_closed(310 + k * 60, GROUND - 190, 40, 60, rot=(k - 1.5) * 12,
                            c=["grey", "blue", "coral", "green"][k] if not (k == 2 and lt > 3.0) else "grey",
                            a=0 if (k == 2 and lt > 3.0) else 255)
            shelf(1180, 330, 400, GROUND - 330, rows=5, seed=7, label="7", missing=(1, 3) if lt < 5.4 else None,
                  highlight=(1, 3))
            if lt < 4.2:
                bx = lerp(760, 640, prog(lt, 2.0, 3.0))
                grab = prog(lt, 2.6, 3.0)
                pp = person("boy", bx, GROUND, 1.8, face=-1, expr="worried" if lt < 3.0 else "smile",
                            arms=((lerp(-20, -60, grab), lerp(-10, -60, grab)) if lt < 3.0 else (-60, -80), (20, -10)),
                            lean=lerp(0, -20, grab) if lt < 3.2 else 0)
                if lt > 3.0:
                    book_cover(pp["hands"][0][0], pp["hands"][0][1] - 50, 0.55)
            else:
                bx = lerp(640, 1080, prog(lt, 4.2, 5.4))
                pp = person("boy", bx, GROUND, 1.8, face=1, walk=lt * 7 if lt < 5.4 else None, expr="smile",
                            arms=((-20, 10), (40, 80) if lt < 5.2 else (120, -20)))
                if lt < 5.2:
                    book_cover(pp["hands"][1][0] + 10, pp["hands"][1][1] - 50, 0.55)
                if lt > 5.6:
                    sparkle(1330, 520, pop(lt, 5.6))
        elif lt < 10.6:
            # b. 每周三，他先上来确认书还在；她来了就躲起来
            lt2 = lt - 6.6
            interior(lt, "sun", side_shelves=False, highlight=(1, 3))
            calendar(1680, 260, 0.7, top="每周", big="周三")
            hide = prog(lt2, 1.8, 2.6)
            bx = lerp(1250, 1560, hide)
            person("boy", bx, GROUND, 1.8, face=-1 if lt2 < 1.8 else 1, walk=lt * 8 if 1.8 < lt2 < 2.6 else None,
                   expr="happy" if lt2 < 1.4 else ("surprise" if lt2 < 2.6 else "smile"),
                   arms=((-120, 0), (20, -10)) if lt2 < 1.4 else None, look=-8 if lt2 > 2.6 else None)
            if lt2 < 1.4:
                with xf():
                    pass
            if lt2 > 2.6:
                # 他躲到另一个书架后
                shelf(1440, 330, 400, GROUND - 330, rows=5, seed=8, label="8")
                gx = lerp(-80, 640, prog(lt2, 1.8, 3.4))
                person("girl", gx, GROUND, 1.8, face=1, walk=lt * 8 if lt2 < 3.4 else None, expr="happy")
                heart(1500, 390, pop(lt2, 3.2) * 1.0)
            else:
                gx = lerp(-80, 640, prog(lt2, 1.8, 3.4))
                person("girl", gx, GROUND, 1.8, face=1, walk=lt * 8, expr="happy")
        else:
            # c. 他在第二章拿起书的那一刻
            lt3 = lt - 10.6
            interior(lt, "sun", side_shelves=False, missing=(1, 3))
            pp = person("boy", 1300, GROUND, 1.8, face=-1, arms=((-40, -80), (20, -10)), expr="closed", blush=0.8)
            hx, hy = pp["hands"][0]
            book_cover(hx - 10, hy - 40, 0.7)
            write("有个女孩在等这本书里的人。", W / 2, 180, 54, align="center", reveal=lin(lt3, 0.2, 1.6))
            for k in range(3):
                heart(1300 + (k - 1) * 70, 300 - k * 30, pop(lt3, 0.8 + k * 0.2) * 0.9)
        vignette_frame()


# ---------------------------------------------------------------- 第五章

def icon_heart(t):
    heart(0, 20, 3.2, "pink")


def s5_1(t, d):
    """奔跑 / 关机 / 火车开走"""
    if t < 3.0:
        ground(GROUND)
        tree(200, GROUND, 1.0, "spring")
        tree(1250, GROUND, 0.9, "spring")
        x = lerp(200, 900, prog(t, 0, 3.0))
        pp = person("girl", x, GROUND, 1.8, face=1, walk=t * 15, lean=12, expr="worried",
                    arms=((-60, -40), (150, 60)), scarf_wind=1.0)
        for k in range(3):
            line(x - 140 - k * 30, GROUND - 180 + k * 50, x - 90 - k * 30, GROUND - 180 + k * 50, 4, a=180)
        if t > 1.0:
            phone(1500, 480, 1.6 * pop(t, 1.0))
        particles("petal", t, 14, (0, 0, W, H), seed=33, wind=-0.8)
    elif t < 6.0:
        lt = t - 3.0
        ground(GROUND)
        rect(1100, 300, 360, GROUND - 300, 6, fill="paper", wash="wood", wa=150, amp=1.0)
        dot(1400, 620, 9)
        rect(1210, 330, 140, 60, 4, fill="white", amp=0.5)
        write("302", 1280, 375, 40, align="center")
        person("girl", 1260, GROUND, 1.7, face=-1, hair="short", scarf=False, skirt="green", expr="sad",
               arms=((-90, -20), (20, -10)))
        person("girl", 620, GROUND, 1.8, face=1, expr="surprise" if lt > 1.2 else "worried")
        bubble(960, 330, 300, 200, tail=(1180, 520), s=pop(lt, 0.5))
        if lt > 0.7:
            with xf(900, 360, scale=0.35):
                train(0, 0, 1.0, t, rails=False)
            write("下午", 1040, 300, 36, c="coral", align="center")
    else:
        lt = t - 6.0
        with cam(1.0):
            tx = lerp(700, 2100, prog(lt, 0.0, 3.0) ** 1.4)
            train(tx, 800, 1.2, t)
            person("girl", 380, 800, 1.6, face=1, expr="cry", tears=0.8, scarf_wind=1.0,
                   arms=((-20, 10), (lerp(20, 100, prog(lt, 0.5, 1.2)), 0)))
            particles("petal", t, 20, (0, 0, W, H), seed=34, wind=0.8)


def s5_2(t, d):
    """借书卡"""
    if t < 2.0:
        with cam(1.25, 900, 560):
            interior(t, "evening", missing=(1, 3), side_shelves=False, lamp_glow=1.0)
            pp = person("girl", 700, GROUND, 1.8, face=1, expr="sad", arms=((-20, 10), (40, 80)))
            hx, hy = pp["hands"][1]
            book_cover(hx + 16, hy - 50, 0.75)
            k = prog(t, 0.6, 1.8)
            with xf(hx + 30 + k * 60, hy + k * 200, rot=k * 200):
                card(0, 0, 90, 56, lines=False)
    a = prog(t, 1.6, 2.2)
    if a > 0:
        with paper_layer(a):
            with cam(1.0 + 0.02 * t):
                card(W / 2, H / 2, 1560, 800, rot=-1)
                lines = ["我字写得丑，也不会说漂亮话。", "骗你是我不对，但有一句是真的——", "我喜欢你，", "从你第一次站在这排书架前面开始。"]
                starts = [2.2, 3.9, 5.6, 6.3]
                ends = [3.8, 5.5, 6.2, 7.8]
                for k, (s, t0, t1) in enumerate(zip(lines, starts, ends)):
                    write(s, 300, 330 + k * 120, 62 if k != 2 else 70, style="xu", reveal=lin(t, t0, t1))
                if t > 8.0:
                    k = prog(t, 8.0, 8.6)
                    teardrop(1300, 620 + k * 100, 2.0 * (1 - prog(t, 8.5, 8.8)))
                    if t > 8.6:
                        blob(1300, 740, 30, 20, "tear", 140, blur=6)


def s5_3(t, d):
    """重逢：那就别等。"""
    glow = prog(t, 12.4, 14.0)
    interior(t, "evening", missing=(1, 3), side_shelves=False, lamp_glow=0.6 + glow)
    # 还书车 + 许知行
    cart_x = lerp(W + 260, 1560, prog(t, 0.8, 2.8))
    cart(cart_x, GROUND, 1.0, roll=-t * 5 if t < 2.8 else -14)
    boy_x = cart_x + 260
    if t < 2.8:
        pass
    boy_x = lerp(W + 520, 1680, prog(t, 0.8, 2.8)) if t < 7.2 else lerp(1680, 1260, prog(t, 7.2, 8.6))
    boy_arms = ((-60, -30), (20, -10))
    if 3.0 < t < 6.8:
        boy_arms = ((-60, -20), (160, 60))
    if t > 11.0:
        boy_arms = ((-70, -10), (20, -10))
    pp = person("boy", boy_x, GROUND, 1.8, face=-1, walk=t * 7 if (t < 2.8 or 7.2 < t < 8.6) else None,
                expr="worried" if t < 10.2 else "happy", blush=prog(t, 3.2, 4.0) + prog(t, 10.0, 10.6),
                arms=boy_arms, backpack=True)
    # 林晚
    lin_x = lerp(620, 960, prog(t, 7.0, 8.6))
    lin_face = -1 if t < 2.4 else 1
    lin_expr = "closed" if t < 2.4 else ("surprise" if t < 5.0 else "happy")
    arms = ((-30, 100), (30, -100)) if t < 2.4 else ((-20, 10), (20, -10))
    if 8.6 < t < 11.0:
        arms = ((-20, 10), (110, -10))
    if t > 11.0:
        arms = ((-20, 10), (70, 10))
    person("girl", lin_x, GROUND, 1.8, face=lin_face, walk=(t - 7.0) * 8 if 7.0 < t < 8.6 else None, expr=lin_expr,
           tears=0.8 if t < 2.4 else 0, blush=prog(t, 9.0, 10.0))
    if t < 2.4:
        card(lin_x, GROUND - 200, 70, 44, lines=False)
    # 火车票
    if 3.6 < t < 7.0:
        ticket(1560, 360, 1.3 * pop(t, 3.6), rot=-6, time_="21:00")
    # 借书卡：那就别等。
    if 8.6 < t < 11.4:
        s = pop(t, 8.6, 0.4) * (1 - prog(t, 11.0, 11.4))
        with xf(W / 2, 330, scale=max(0.01, s)):
            card(0, 0, 700, 300, rot=2)
            tip = write("那就别等。", -230, 30, 100, c=LIN_C, reveal=lin(t, 9.0, 10.4))
            if t < 10.6:
                draw_pencil(tip[0] + 16, tip[1] - 26, 1.2)
    # 牵手、爱心、铃声
    if t > 11.0:
        heart((lin_x + boy_x) / 2, 450, pop(t, 11.1, 0.45) * 3.0)
        for k in range(5):
            sparkle((lin_x + boy_x) / 2 + math.cos(k * 1.26) * 220, 450 + math.sin(k * 1.26) * 150,
                    pop(t, 11.3 + k * 0.1) * 0.9)
    if t > 11.8:
        ring_bell(1760, 230, 0.8, t, ringing=11.8 < t < 13.8)
    if glow > 0:
        blob(W / 2, H / 2, 900, 520, "lamp", 60 * glow, blur=120)
        particles("heart", t, 10, (0, 0, W, H), seed=51, a=200 * glow, speed=0.4)


def s5_4(t, d):
    """春夜的图书馆，拉远，完"""
    z = lerp(1.18, 1.0, prog(t, 0, 6))
    close = prog(t, 5.2, 6.4)
    with xf(alpha=1 - close):
        with cam(z, W / 2, H / 2 + 60):
            solid_rect(-400, -400, W + 800, 1350, "night", 55)
            for k in range(14):
                sparkle((k * 157) % W, 60 + (k * 97) % 300, 0.4 + 0.2 * math.sin(t * 2 + k), "white")
            ground(950)
            tree(250, 950, 1.3, "spring")
            tree(1680, 950, 1.2, "spring")
            building(W / 2 + 40, 950, 1.0, lit=1.0, night=True)
            x = lerp(870, 1180, prog(t, 0.3, 5.0))
            person("girl", x, 950, 0.9, face=1, walk=t * 7, expr="happy", arms=((-20, 10), (60, 10)))
            person("boy", x + 70, 950, 0.9, face=1, walk=t * 7 + 1, expr="happy", arms=((-60, -10), (20, -10)),
                   backpack=True)
            heart(x + 35, 950 - 250, 0.8)
        particles("petal", t, 22, (0, 0, W, H), seed=61, speed=0.6)
    if close > 0:
        with xf(alpha=close):
            p = prog(t, 5.6, 7.0)
            bw, bh = 1000, 560
            cx, cy = lerp(W / 2, W / 2 - bw / 4, p), H / 2 - 20
            opening_book(cx, cy, bw, bh, 1 - p)
            if t > 7.0:
                write("（完）", W / 2, H - 150, 64, style="title", align="center", reveal=lin(t, 7.0, 7.8))


SHOTS = [
    ("0 片头", 9, s_title),
    ("1-0", 3, chapter_card("一 · 铅笔字", icon_pencil)),
    ("1-1", 6, s1_1),
    ("1-2", 9, s1_2),
    ("1-3", 9, s1_3),
    ("1-4", 6, s1_4),
    ("1-5", 12, s1_5),
    ("2-0", 3, chapter_card("二 · 认错的人", icon_question)),
    ("2-1", 9, s2_1),
    ("2-2", 12, s2_2),
    ("2-3", 12, s2_3),
    ("2-4", 9, s2_4),
    ("3-0", 3, chapter_card("三 · 对不上的笔迹", icon_neq)),
    ("3-1", 6, s3_1),
    ("3-2", 6, s3_2),
    ("3-3", 9, s3_3),
    ("3-4", 12, s3_4),
    ("4-0", 3, chapter_card("四 · 真正的 X", icon_x)),
    ("4-1", 6, s4_1),
    ("4-2", 9, s4_2),
    ("4-3", 12, s4_3),
    ("4-4", 15, s4_4),
    ("5-0", 3, chapter_card("五 · 尾声", icon_heart)),
    ("5-1", 9, s5_1),
    ("5-2", 9, s5_2),
    ("5-3", 15, s5_3),
    ("5-4", 9, s5_4),
]

TOTAL = sum(s[1] for s in SHOTS)
