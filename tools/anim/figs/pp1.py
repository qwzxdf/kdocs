import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402


def Clamp(x):
    return min(x, 1.0)


def Reinhard(x):
    return x / (1.0 + x)


def Aces(x):
    return max(0.0, min(1.0, (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)))


def Hable(x):
    A, B, C, D, E, F = 0.15, 0.50, 0.10, 0.20, 0.02, 0.30

    def f(v):
        return ((v * (A * v + C * B) + D * E) / (v * (A * v + B) + D * F)) - E / F

    return min(1.0, f(x) / f(11.2))


PAGE = "graphics/postprocess/"


def TonemapCurves():
    name = "tonemap-curves"
    scene = NewScene(name, 780, 380, duration=9.0, hold=1.5, title="入力の明るさ x を増やしていくと、出力がどう変わるか")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 420, 250, 8.0, 1.0, "入力 x（HDR）", "出力（0〜1）")
    fns = [("クランプ", Clamp, GRAY, "5 4"), ("Reinhard", Reinhard, BLUE, None), ("ACES", Aces, RED, None), ("Hable", Hable, GREEN, None)]
    for label, fn, color, dash in fns:
        ax.Curve(fn, color, 3, n=64, dash=dash)
    scene.Text(root, ax.X(5.2), ax.Y(1.0) - 8, "クランプは 1 で頭打ち", size=12, weight=500, fill=GRAY)
    t0, t1, n = 0.8, 8.2, 30
    line = root.add("line", x1=ax.X(0), y1=ax.y, x2=ax.X(0), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2, opacity=1)
    prev = None
    for i in range(n + 1):
        t = Lerp(t0, t1, i / n)
        x = 8.0 * i / n
        if i == 0:
            line.Set(t, "x1", ax.X(x)); line.Set(t, "x2", ax.X(x))
        else:
            line.Ramp(prev, t, "x1", ax.X(x)); line.Ramp(prev, t, "x2", ax.X(x))
        prev = t
    sw = []
    for k, (label, fn, color, dash) in enumerate(fns):
        dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=6, fill=color, stroke="#ffffff", stroke_width=1.5)
        Sweep(dot, ax, fn, t0, t1, 0.0, 8.0, n)
        y = 76 + k * 62
        scene.Text(root, 520, y + 4, label, size=14, fill=color)
        box = root.add("rect", x=620, y=y - 18, width=110, height=44, fill="#000000", stroke="#94a3b8", stroke_width=1.5)
        RampFill(box, "fill", t0, t1, n, lambda f, fn=fn: Gray(fn(8.0 * f)))
    LiveText(scene, root, 520, 340, t0, t1, n, lambda i, f: "入力 x = %.1f" % (8.0 * i / n), size=15)
    scene.Text(root, 520, 360, "右の四角が、その x を表示した色", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "x を 0 → 8 に増やす")
    return dict(name=name, page=PAGE + "tonemapping/index.md", scene=scene, size=(780, 380), times=[0.5, 3.0, 5.5, 8.0])


def TonemapReinhard():
    name = "tonemap-reinhard"
    scene = NewScene(name, 780, 360, duration=9.0, hold=1.5, title="Reinhard:x / (1 + x)。どんなに明るくても 1 を超えない")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 430, 240, 8.0, 1.0, "入力 x", "出力")
    ax.Curve(Clamp, GRAY, 3, n=64, dash="5 4")
    ax.Curve(Reinhard, BLUE, 4, n=64)
    wp = 4.0
    ext = lambda x: min(1.0, x * (1 + x / (wp * wp)) / (1 + x))
    c2 = ax.Curve(ext, PURPLE, 3, n=64, opacity=0)
    c2.Show(5.0)
    lab = scene.Text(root, ax.X(4.6), ax.Y(0.55), "拡張版（白色点 4）:x=4 で 1", size=12, fill=PURPLE, weight=700, opacity=0)
    lab.Show(5.0)
    scene.Text(root, ax.X(4.0), ax.Y(0.38), "Reinhard", size=13, fill=BLUE)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=BLUE, stroke="#ffffff", stroke_width=1.5)
    t0, t1, n = 0.8, 5.0, 24
    Sweep(dot, ax, Reinhard, t0, t1, 0.0, 8.0, n)
    dot2 = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=PURPLE, stroke="#ffffff", stroke_width=1.5, opacity=0)
    dot2.Show(5.0)
    Sweep(dot2, ax, ext, 5.0, 8.6, 0.0, 8.0, 24)
    LiveText(scene, root, 510, 110, t0, t1, n, lambda i, f: "x = %.1f" % (8.0 * i / n), size=18)
    LiveText(scene, root, 510, 146, t0, t1, n, lambda i, f: "出力 = %.2f" % Reinhard(8.0 * i / n), size=18, fill=BLUE)
    scene.TextStack(root, 510, 190, [(1.0, 5.0, "x が 1 のとき 0.50"), (5.0, 20, "白色点を決めると、その明るさで 1 になる")], size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 510, 216, [(1.0, 5.0, "x が 8 でも 0.89（白に潰れない）"), (5.0, 20, "x = 4 以上は 1（白）に張り付く")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 510, 262, "暗い所も持ち上がる ＝ 眠い絵になりやすい", size=13, weight=500, fill=RED)
    scene.Note(t0, name, "x を 0 → 8、続いて拡張版")
    return dict(name=name, page=PAGE + "tonemapping/reinhard.md", scene=scene, size=(780, 360), times=[1.5, 3.5, 6.0, 8.5])


def TonemapHable():
    name = "tonemap-hable"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="フィルミックの S 字:つま先・直線部・肩の 3 つの領域")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 430, 250, 6.0, 1.0, "入力 x", "出力")
    ax.Curve(Reinhard, GRAY, 3, n=64, dash="5 4")
    scene.Text(root, ax.X(3.2), ax.Y(0.62), "Reinhard（比較）", size=12, weight=500, fill=GRAY)
    zones = [("つま先", 0.0, 0.7, PURPLE, "暗部を沈めて、締まった絵に", 0.8), ("直線部", 0.7, 2.6, BLUE, "中間の明るさは、素直に保つ", 3.2), ("肩", 2.6, 6.0, GREEN, "明部をなめらかに圧縮して、白飛びを防ぐ", 5.6)]
    for label, a, b, color, desc, t in zones:
        p = ax.Curve(Hable, color, 5, x0=a, x1=b, n=40, opacity=0)
        p.Show(t)
        tx = 520
        y = 110 + zones.index((label, a, b, color, desc, t)) * 62
        scene.TextStack(root, tx, y, [(t, 20, label)], size=17, fill=color)
        scene.TextStack(root, tx, y + 22, [(t, 20, desc)], size=12, fill=GRAY, weight=500)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK, stroke="#ffffff", stroke_width=1.5, opacity=0)
    dot.Show(8.0)
    Sweep(dot, ax, Hable, 8.0, 10.0, 0.0, 6.0, 16)
    scene.TextStack(root, 50, 352, [(0.0, 8.0, "つま先 → 直線部 → 肩の順に、曲線が現れる"), (8.0, 20, "Reinhard より、暗部が低い（つま先） ＝ コントラストが高い")], size=14, fill=INK, weight=500)
    scene.Note(0.8, name, "つま先 → 直線部 → 肩")
    return dict(name=name, page=PAGE + "tonemapping/filmic-hable.md", scene=scene, size=(780, 380), times=[1.5, 4.0, 7.0, 10.0])


def AutoExposureHistogram():
    name = "auto-exposure-histogram"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="輝度ヒストグラム:外れ値を除いて、平均の明るさを測る")
    root = scene.root
    bins = 16
    data = [2, 4, 9, 18, 30, 44, 52, 46, 30, 16, 8, 5, 3, 2, 3, 9]
    total = sum(data)
    ax = Axes(scene, root, 50, 70, 520, 230, bins, 60, "", "画素数", grid=False)
    scene.Text(root, ax.x + ax.w, ax.y + ax.h + 34, "輝度（log2、右ほど明るい）", size=12, weight=500, fill=GRAY, anchor="end")
    bw = ax.w / bins
    for i, v in enumerate(data):
        h = v / 60 * ax.h
        bar = root.add("rect", x=R(ax.x + i * bw + 2), y=R(ax.y + ax.h - h), width=R(bw - 4), height=R(h), fill=BLUE, opacity=0)
        bar.Show(0.6 + i * 0.12)
        scene.Text(root, ax.x + i * bw + bw / 2, ax.y + ax.h + 16, str(i - 8), size=11, weight=500, fill=GRAY, anchor="middle")
    lo, hi = 3, 13
    cut = root.add("rect", x=R(ax.x + lo * bw), y=ax.y, width=R((hi - lo) * bw), height=ax.h, fill=AMBER, opacity=0)
    cut.Set(3.0, "opacity", 0.18)
    for edge, label in ((lo, "下位 10 % を除く"), (hi, "上位 10 % を除く")):
        ln = root.add("line", x1=R(ax.x + edge * bw), y1=ax.y, x2=R(ax.x + edge * bw), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2.5, opacity=0)
        ln.Show(3.0)
    scene.TextStack(root, ax.x + lo * bw - 6, ax.y + 20, [(3.0, 20, "下位 10 %")], size=12, fill=AMBER, anchor="end")
    scene.TextStack(root, ax.x + hi * bw + 6, ax.y + 20, [(3.0, 20, "上位 10 %")], size=12, fill=AMBER)
    inside = [(i, data[i]) for i in range(lo, hi)]
    mean = sum((i + 0.5) * v for i, v in inside) / sum(v for _, v in inside)
    mx = ax.x + mean * bw
    tri = root.add("polygon", points="%s,%s %s,%s %s,%s" % (R(mx), R(ax.y + ax.h - 4), R(mx - 9), R(ax.y + ax.h + 18), R(mx + 9), R(ax.y + ax.h + 18)), fill=RED, opacity=0)
    tri.Show(5.0)
    ev = mean - 8
    scene.TextStack(root, ax.x + ax.w - 10, ax.y + 52, [(5.0, 20, "▲ 平均 log2 ≒ %.1f" % ev)], size=14, fill=RED, anchor="end")
    exposure = -ev
    scene.TextStack(root, 50, 372, [(0.0, 3.0, "① 画素を明るさの段（log2）ごとに数える"), (3.0, 5.0, "② 暗すぎ・明るすぎる 10 % ずつは除く（ランプ・暗闇に引っ張られない）"), (5.0, 8.0, "③ 残りの平均を求める → 平均 log2 ≒ %.1f" % ev), (8.0, 20, "④ 平均が 0 EV になるよう露出を %+.1f EV 補正する" % exposure)], size=14, fill=INK, weight=500)
    scene.Note(3.0, name, "10 % ずつ除外")
    return dict(name=name, page=PAGE + "tonemapping/auto-exposure.md", scene=scene, size=(780, 400), times=[1.5, 3.5, 6.0, 9.0])


def AutoExposureAdapt():
    name = "auto-exposure-adapt"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="時間で追従:暗い所から明るい所へ出ると、一瞬まぶしい")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 470, 240, 10.0, 1.2, "時間（秒）", "")
    t_change = 2.0
    scene_l = lambda t: 0.25 if t < t_change else 3.0
    rate = 0.9
    adapted = []
    L = 0.25
    dt = 0.1
    steps = int(10.0 / dt)
    samples = []
    for i in range(steps + 1):
        t = i * dt
        samples.append((t, scene_l(t), L))
        L += (scene_l(t) - L) * (1 - math.exp(-rate * dt))
    img = lambda s, a: min(1.0, 0.18 * s / a)
    step_curve = "M" + " L".join("%s,%s" % (ax.X(t), ax.Y(min(1.2, s / 3.0))) for t, s, a in samples)
    img_curve = "M" + " L".join("%s,%s" % (ax.X(t), ax.Y(img(s, a))) for t, s, a in samples)
    root.add("path", d=step_curve, fill="none", stroke=GRAY, stroke_width=3, stroke_dasharray="5 4")
    root.add("path", d=img_curve, fill="none", stroke=BLUE, stroke_width=4)
    scene.Text(root, ax.X(0.2), ax.Y(0.33), "実際の明るさ（点線）", size=12, fill=GRAY, weight=500)
    scene.Text(root, ax.X(2.4), ax.Y(1.0) - 8, "画面の明るさ（青）", size=12, fill=BLUE)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(img(*samples[0][1:])), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    prev = None
    for i, (t, s, a) in enumerate(samples):
        tt = 0.6 + t * 0.9
        if i == 0:
            dot.Set(tt, "cx", ax.X(t)); dot.Set(tt, "cy", ax.Y(img(s, a)))
        else:
            dot.Ramp(prev, tt, "cx", ax.X(t)); dot.Ramp(prev, tt, "cy", ax.Y(img(s, a)))
        prev = tt
    tv = 0.6 + 10.0 * 0.9
    screen = root.add("rect", x=555, y=90, width=170, height=110, fill=Gray(img(*samples[0][1:])), stroke="#94a3b8", stroke_width=2)
    prev = None
    for i, (t, s, a) in enumerate(samples):
        tt = 0.6 + t * 0.9
        if i == 0:
            screen.Set(tt, "fill", Gray(img(s, a)))
        else:
            screen.Ramp(prev, tt, "fill", Gray(img(s, a)))
        prev = tt
    scene.Text(root, 640, 82, "画面", size=13, fill=GRAY, anchor="middle", weight=700)
    tc = 0.6 + t_change * 0.9
    scene.TextStack(root, 555, 232, [(0.0, tc, "暗い部屋の中"), (tc, tc + 1.6, "外へ出た!まぶしい"), (tc + 1.6, 20, "目が慣れて、見やすくなる")], size=14, fill=INK, weight=700)
    scene.TextStack(root, 555, 256, [(tc + 1.6, 20, "露出が少しずつ下がる")], size=12, fill=GRAY, weight=500)
    scene.TextStack(root, 50, 346, [(0.0, 20, "追従の速さ(係数)で、慣れるまでの時間が決まる。明るい所への適応は速く、暗い所へは遅くする。")], size=13, fill=GRAY, weight=500)
    scene.Note(tc, name, "明るさが急変")
    return dict(name=name, page=PAGE + "tonemapping/auto-exposure.md", scene=scene, size=(780, 380), times=[0.8, 2.5, 4.5, 9.0])


def Lamps(scene, g, x, y, bright=1.0, lamp_only=False, glow=None):
    """小さな夜景(建物と街灯)を g の中に描く。"""
    if not lamp_only:
        g.add("rect", x=x, y=y, width=170, height=140, fill="#0f172a")
        g.add("rect", x=x + 14, y=y + 70, width=64, height=70, fill="#334155")
        g.add("rect", x=x + 96, y=y + 96, width=60, height=44, fill="#1e293b")
    else:
        g.add("rect", x=x, y=y, width=170, height=140, fill="#000000")
    for lx, ly, r in ((x + 40, y + 42, 8), (x + 124, y + 58, 7)):
        g.add("circle", cx=lx, cy=ly, r=r, fill="#fff7d6")
    g.add("rect", x=x + 28, y=y + 92, width=22, height=18, fill="#fde68a")


def BloomStages():
    name = "bloom-stages"
    scene = NewScene(name, 780, 330, duration=10.0, hold=1.5, title="ブルームの 4 段階:明るい所を抜き出し、ぼかし、足す")
    root = scene.root
    f_blur = Blur(scene, "bs-blur", 9)
    f_blur2 = Blur(scene, "bs-blur2", 4)
    titles = ["① 元の絵", "② 明るい所だけ", "③ ぼかす", "④ 元に足す"]
    starts = [0.0, 2.2, 4.4, 6.6]
    for i in range(4):
        px = 20 + i * 190
        g = root.add("g", opacity=1 if i == 0 else 0)
        if i:
            g.Show(starts[i])
        py = 80
        if i == 0:
            Lamps(scene, g, px, py)
        elif i == 1:
            Lamps(scene, g, px, py, lamp_only=True)
        elif i == 2:
            g.add("rect", x=px, y=py, width=170, height=140, fill="#000000")
            for lx, ly, r in ((px + 40, py + 42, 8), (px + 124, py + 58, 7)):
                g.add("circle", cx=lx, cy=ly, r=r * 1.4, fill="#fff7d6", filter=f_blur)
            g.add("rect", x=px + 28, y=py + 92, width=22, height=18, fill="#fde68a", filter=f_blur2)
        else:
            Lamps(scene, g, px, py)
            for lx, ly, r in ((px + 40, py + 42, 8), (px + 124, py + 58, 7)):
                g.add("circle", cx=lx, cy=ly, r=r * 1.6, fill="#fff7d6", filter=f_blur, opacity=0.9)
            g.add("rect", x=px + 28, y=py + 92, width=22, height=18, fill="#fde68a", filter=f_blur2, opacity=0.8)
        g.add("rect", x=px, y=py, width=170, height=140, fill="none", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, px + 85, py - 10, titles[i], size=14, fill=INK, anchor="middle")
        if i < 3:
            a = root.add("g", opacity=0)
            a.Show(starts[i + 1] - 0.4)
            Arrow(scene, a, px + 174, py + 70, px + 188, py + 70)
    notes = ["シーンを HDR で描く", "しきい値より明るい画素だけ残す", "残したものを、大きくぼかす", "ぼかした光を、元の絵に足す"]
    scene.TextStack(root, 20, 270, [(starts[i], starts[i + 1] if i < 3 else 20, notes[i]) for i in range(4)], size=16, fill=INK)
    scene.TextStack(root, 20, 298, [(starts[3], 20, "→ 明るい物の周りが、にじんで光って見える")], size=13, fill=GRAY, weight=500)
    scene.Note(0.0, name, "元 → 抽出 → ぼかし → 合成")
    return dict(name=name, page=PAGE + "bloom/index.md", scene=scene, size=(780, 330), times=[1.0, 3.0, 5.5, 8.5])


def BloomMipChain():
    name = "bloom-mip-chain"
    scene = NewScene(name, 780, 440, duration=10.0, hold=1.5, title="ミップ チェーン:半分ずつ小さくして（ダウン）、戻しながら足す（アップ）")
    root = scene.root
    sizes = [(1920, 1080), (960, 540), (480, 270), (240, 135), (120, 68)]
    widths = [220, 110, 56, 28, 14]
    xs = [30, 270, 400, 480, 530]
    top, bot = 70, 235
    for i, (w, h) in enumerate(zip(widths, [int(v * 0.5625) for v in widths])):
        t = 0.8 + i * 1.0
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=xs[i], y=top, width=w, height=h, fill=Mix("#bfdbfe", "#1d4ed8", i / 4), stroke=INK, stroke_width=1.5)
        scene.Text(g, xs[i], top - 8, "%d×%d" % sizes[i], size=11, weight=500, fill=GRAY)
        if i:
            a = root.add("g", opacity=0)
            a.Show(t - 0.3)
            Arrow(scene, a, xs[i - 1] + widths[i - 1] + 4, top + 20, xs[i] - 6, top + 20)
    scene.TextStack(root, 30, 224, [(0.8, 20, "ダウン:各段で 1/2 に縮める（広い範囲が少ない画素に集まる）")], size=14, fill=BLUE)
    for i in reversed(range(4)):
        k = 3 - i
        t = 6.0 + k * 0.9
        w = widths[i]
        h = int(w * 0.5625)
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=xs[i], y=bot + 28, width=w, height=h, fill=Mix("#fed7aa", "#c2410c", (4 - i) / 4 * 0.9), stroke=INK, stroke_width=1.5)
        a = root.add("g", opacity=0)
        a.Show(t - 0.3)
        Arrow(scene, a, xs[i + 1] - 6, bot + 48, xs[i] + widths[i] + 4, bot + 48, color=AMBER)
        scene.Text(g, xs[i] + w / 2, bot + 20, "＋", size=14, fill=AMBER, anchor="middle")
    scene.TextStack(root, 30, 420, [(6.0, 20, "アップ:小さい段から戻しつつ、1 つ大きい段に足していく → 小さな光から大きなにじみまで重なる")], size=14, fill=AMBER)
    scene.Note(0.8, name, "ダウン 5 段 → アップ 4 回")
    return dict(name=name, page=PAGE + "bloom/downsample.md", scene=scene, size=(780, 440), times=[1.5, 4.0, 6.5, 9.0])


def DualFilter():
    name = "dual-filter-passes"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="デュアル フィルタ:ダウンは 5 回、アップは 8 回のサンプルだけ")
    root = scene.root
    cell = 36
    ox, oy = 40, 90
    scene.Text(root, ox, oy - 22, "ダウン:縮小先の 1 画素（2×2）を作る", size=14, fill=BLUE)
    for i in range(7):
        root.add("line", x1=ox + i * cell, y1=oy, x2=ox + i * cell, y2=oy + 6 * cell, stroke=LIGHT, stroke_width=1.5)
        root.add("line", x1=ox, y1=oy + i * cell, x2=ox + 6 * cell, y2=oy + i * cell, stroke=LIGHT, stroke_width=1.5)
    foot = [(0, 0), (2, 0), (2, 2)]
    for k, (cx, cy) in enumerate(foot):
        t = 0.8 + k * 3.0
        g = root.add("g", opacity=0)
        g.Show(t, t + 3.0)
        g.add("rect", x=ox + cx * cell, y=oy + cy * cell, width=2 * cell, height=2 * cell, fill=AMBER, fill_opacity=0.35, stroke=AMBER, stroke_width=3)
        mx, my = ox + (cx + 1) * cell, oy + (cy + 1) * cell
        g.add("circle", cx=mx, cy=my, r=9, fill=BLUE, stroke="#ffffff", stroke_width=2)
        scene.Text(g, mx, my + 4, "4", size=11, fill="#ffffff", anchor="middle")
        for dx, dy in ((0, 0), (2, 0), (0, 2), (2, 2)):
            px, py = ox + (cx + dx) * cell, oy + (cy + dy) * cell
            g.add("circle", cx=px, cy=py, r=7, fill=PURPLE, stroke="#ffffff", stroke_width=2)
            scene.Text(g, px, py + 4, "1", size=10, fill="#ffffff", anchor="middle")
    scene.TextStack(root, ox, oy + 6 * cell + 30, [(0.8, 20, "中心 ×4 ＋ 四隅 ×1 ＝ 重み 8（÷8）。各点は線形補間で 4 画素分")], size=13, fill=GRAY, weight=500)
    ux, uy = 440, 100
    scene.Text(root, ux, uy - 32, "アップ:小さい画像から 1 画素を作る", size=14, fill=GREEN)
    ucell = 56
    for i in range(5):
        root.add("line", x1=ux + i * ucell, y1=uy, x2=ux + i * ucell, y2=uy + 4 * ucell, stroke=LIGHT, stroke_width=1.5)
        root.add("line", x1=ux, y1=uy + i * ucell, x2=ux + 4 * ucell, y2=uy + i * ucell, stroke=LIGHT, stroke_width=1.5)
    cx, cy = ux + 2 * ucell, uy + 2 * ucell
    pts = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-0.5, -0.5, 2), (0.5, -0.5, 2), (-0.5, 0.5, 2), (0.5, 0.5, 2)]
    ctr = root.add("circle", cx=cx, cy=cy, r=6, fill=INK)
    for i, (dx, dy, w) in enumerate(pts):
        t = 1.0 + i * 0.7
        g = root.add("g", opacity=0)
        g.Show(t)
        color = PURPLE if w == 1 else GREEN
        g.add("circle", cx=R(cx + dx * ucell), cy=R(cy + dy * ucell), r=8, fill=color, stroke="#ffffff", stroke_width=2)
        scene.Text(g, R(cx + dx * ucell), R(cy + dy * ucell + 4), str(w), size=11, fill="#ffffff", anchor="middle")
    scene.TextStack(root, ux, uy + 4 * ucell + 30, [(1.0, 20, "縦横 4 点 ×1 ＋ 斜め 4 点 ×2 ＝ 重み 12（÷12）")], size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 40, 382, [(0.8, 20, "ガウスのように横・縦に分けず、各段 1 パスで済む（サンプル数が少なく、ぼけは広い）")], size=13, fill=INK, weight=500)
    scene.Note(0.8, name, "ダウン 5 タップ / アップ 8 タップ")
    return dict(name=name, page=PAGE + "bloom/dual-filter.md", scene=scene, size=(780, 400), times=[1.5, 4.5, 7.0, 9.5])


def GaussianSeparable():
    name = "gaussian-separable"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="ガウスぼかしは「横 → 縦」に分けると、サンプルが激減する")
    root = scene.root
    n, cell, r = 9, 22, 3
    center = n // 2

    def W(d):
        return math.exp(-(d * d) / (2 * 1.4 * 1.4))

    panels = [("そのまま 2D", 40, 1.0), ("① 横にぼかす", 290, 3.2), ("② 縦にぼかす", 540, 5.4)]
    for pi, (title, px, t) in enumerate(panels):
        scene.Text(root, px, 70, title, size=14, fill=INK)
        py = 90
        for j in range(n):
            for i in range(n):
                root.add("rect", x=px + i * cell, y=py + j * cell, width=cell - 1, height=cell - 1, fill="#f1f5f9")
        count = 0
        for j in range(n):
            for i in range(n):
                dx, dy = i - center, j - center
                if abs(dx) > r or abs(dy) > r:
                    continue
                if pi == 1 and dy != 0:
                    continue
                if pi == 2 and dx != 0:
                    continue
                count += 1
                w = W(dx) * W(dy) if pi == 0 else (W(dx) if pi == 1 else W(dy))
                cellrect = root.add("rect", x=px + i * cell, y=py + j * cell, width=cell - 1, height=cell - 1, fill=BLUE if pi == 0 else (GREEN if pi == 1 else PURPLE), opacity=0)
                cellrect.Set(t, "opacity", R(0.2 + 0.8 * w))
        root.add("rect", x=px + center * cell - 1, y=90 + center * cell - 1, width=cell + 1, height=cell + 1, fill="none", stroke=AMBER, stroke_width=3)
        scene.TextStack(root, px, 90 + n * cell + 26, [(t, 20, "サンプル %d 回" % count)], size=16, fill=INK)
    r2 = 8
    scene.TextStack(root, 40, 358, [(0.0, 7.2, "R=%d のとき、そのままだと (2R+1)² = %d 回、分けると 2(2R+1) = %d 回" % (r, (2 * r + 1) ** 2, 2 * (2 * r + 1))), (7.2, 20, "R=%d なら %d 回 → %d 回（約 %d 分の 1）" % (r2, (2 * r2 + 1) ** 2, 2 * (2 * r2 + 1), round((2 * r2 + 1) ** 2 / (2 * (2 * r2 + 1)))))], size=14, fill=RED, weight=700)
    scene.Note(1.0, name, "2D → 横 → 縦")
    return dict(name=name, page=PAGE + "bloom/gaussian.md", scene=scene, size=(780, 380), times=[0.5, 2.0, 4.0, 8.0])


def KarisFireflies():
    name = "karis-fireflies"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="1 画素だけ極端に明るいと、普通の平均は暴れる（ファイアフライ）")
    root = scene.root
    cell, ox, oy = 34, 40, 90
    base, spike = 1.0, 50.0
    frames = [False, True, False, True, False, False]
    plain, karis = [], []
    luma_w = lambda v: 1.0 / (1.0 + v)
    for s in frames:
        vals = [base] * 15 + ([spike] if s else [base])
        plain.append(sum(vals) / 16)
        ws = [luma_w(v) for v in vals]
        karis.append(sum(v * w for v, w in zip(vals, ws)) / sum(ws))
    dur = 1.4
    t0 = 0.8
    scene.Text(root, ox, oy - 14, "4×4 の 1 ブロック", size=13, fill=GRAY)
    for j in range(4):
        for i in range(4):
            root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 2, height=cell - 2, fill="#e2e8f0")
    sp = root.add("rect", x=ox + 2 * cell, y=oy + 1 * cell, width=cell - 2, height=cell - 2, fill="#fef08a", stroke=AMBER, stroke_width=3, opacity=0)
    for k, s in enumerate(frames):
        if s:
            sp.Show(t0 + k * dur, t0 + (k + 1) * dur)
    scene.TextStack(root, ox + 2 * cell + 15, oy + 1 * cell + 21, [(t0 + k * dur, t0 + (k + 1) * dur, "50") for k, s in enumerate(frames) if s], size=13, fill=INK, anchor="middle")
    scene.TextStack(root, ox, oy + 4 * cell + 28, [(t0 + k * dur, t0 + (k + 1) * dur, "フレーム %d:%s" % (k + 1, "明るい画素が入った" if s else "入っていない")) for k, s in enumerate(frames)], size=14, fill=INK)
    gx, gy, gh = 290, 90, 190
    scene.Text(root, gx, gy - 14, "縮小後の画素の明るさ", size=13, fill=GRAY)
    root.add("line", x1=gx, y1=gy + gh, x2=gx + 440, y2=gy + gh, stroke=INK, stroke_width=1.5)
    vmax = 4.5
    for k in range(len(frames)):
        bx = gx + 14 + k * 70
        t = t0 + k * dur
        h1 = plain[k] / vmax * gh
        h2 = karis[k] / vmax * gh
        a = root.add("rect", x=bx, y=R(gy + gh - h1), width=26, height=R(h1), fill=RED, opacity=0)
        a.Show(t)
        b = root.add("rect", x=bx + 28, y=R(gy + gh - h2), width=26, height=R(h2), fill=GREEN, opacity=0)
        b.Show(t)
        scene.Text(root, bx + 27, gy + gh + 16, str(k + 1), size=11, weight=500, fill=GRAY, anchor="middle")
    ly = gy + gh + 44
    root.add("rect", x=gx, y=ly - 11, width=14, height=14, fill=RED)
    scene.Text(root, gx + 20, ly, "普通の平均(%.1f ↔ %.1f とちらつく)" % (plain[0], max(plain)), size=13, fill=INK, weight=500)
    root.add("rect", x=gx + 250, y=ly - 11, width=14, height=14, fill=GREEN)
    scene.Text(root, gx + 270, ly, "Karis 平均(%.2f ↔ %.2f 安定)" % (karis[0], max(karis)), size=13, fill=INK, weight=500)
    scene.Text(root, 40, 356, "Karis 平均:各画素に 1 / (1 + 輝度) の重みを付けて平均 → 極端に明るい画素の影響が小さい", size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "明るい画素が出入りするフレーム列")
    return dict(name=name, page=PAGE + "bloom/karis-average.md", scene=scene, size=(780, 380), times=[1.5, 3.0, 4.5, 8.0])


def BloomIntensity():
    name = "bloom-intensity"
    scene = NewScene(name, 780, 350, duration=10.0, hold=1.5, title="ブルームの強さ:控えめに足すと自然、足しすぎると白くぼやける")
    root = scene.root
    f1, f2 = Blur(scene, "bi-1", 6), Blur(scene, "bi-2", 16)
    px, py = 40, 70
    Lamps(scene, root, px, py)
    glow = root.add("g", opacity=0)
    for lx, ly, r in ((px + 40, py + 42, 8), (px + 124, py + 58, 7)):
        glow.add("circle", cx=lx, cy=ly, r=r * 2.0, fill="#fff7d6", filter=f1)
        glow.add("circle", cx=lx, cy=ly, r=r * 3.2, fill="#fff3c4", filter=f2)
    glow.add("rect", x=px + 28, y=py + 92, width=22, height=18, fill="#fde68a", filter=f1)
    wash = root.add("rect", x=px, y=py, width=170, height=140, fill="#ffffff", opacity=0)
    # スケールして大きく見せる
    ks = [0.0, 0.0, 0.35, 0.35, 0.8, 1.6, 1.6, 0.35]
    ts = [0.0, 0.8, 2.6, 3.6, 5.2, 6.6, 7.6, 9.4]
    glow.Set(0.8, "opacity", 0.0)
    wash.Set(0.8, "opacity", 0.0)
    for i in range(1, len(ks)):
        glow.Ramp(ts[i - 1] if ts[i - 1] > 0.8 else 0.8, ts[i], "opacity", R(min(1.0, ks[i])))
        wash.Ramp(ts[i - 1] if ts[i - 1] > 0.8 else 0.8, ts[i], "opacity", R(max(0.0, (ks[i] - 0.8) * 0.45)))
    bar = root.add("rect", x=260, y=170, width=420, height=10, rx=5, fill=LIGHT)
    root.add("rect", x=260 + 420 * 0.35 / 1.8 - 1, y=162, width=2, height=26, fill=GREEN)
    root.add("rect", x=260 + 420 * 0.8 / 1.8 - 1, y=162, width=2, height=26, fill=RED)
    scene.Text(root, 260 + 420 * 0.35 / 1.8, 156, "おすすめ", size=12, fill=GREEN, anchor="middle")
    scene.Text(root, 260 + 420 * 0.8 / 1.8, 156, "ここから足しすぎ", size=12, fill=RED, anchor="middle")
    knob = root.add("circle", cx=260, cy=175, r=11, fill=BLUE, stroke="#ffffff", stroke_width=2)
    for i in range(1, len(ks)):
        t0_ = ts[i - 1] if ts[i - 1] > 0.8 else 0.8
        knob.Ramp(t0_, ts[i], "cx", R(260 + 420 * ks[i] / 1.8))
    scene.Text(root, 260, 205, "0", size=12, fill=GRAY, weight=500)
    scene.Text(root, 680, 205, "1.8", size=12, fill=GRAY, weight=500, anchor="end")
    scene.Text(root, 260, 120, "ブルームの強さ（intensity）", size=15, fill=INK)
    scene.TextStack(root, 260, 250, [(0.0, 2.6, "強さ 0:ブルームなし。光っているのに、ただの白い点"), (2.6, 5.2, "強さ 0.35 前後:明るい物の周りがほんのり光る（おすすめ）"), (5.2, 6.6, "強さが上がるにつれ、光のにじみが広がる…"), (6.6, 8.0, "強さ 1.6:画面全体が白くかすむ（足しすぎ）"), (8.0, 20, "控えめ（0.2〜0.5）に戻すと、自然な光に")], size=14, fill=INK)
    scene.Note(2.6, name, "強さ 0 → 0.35 → 1.6 → 0.35")
    return dict(name=name, page=PAGE + "bloom/composite.md", scene=scene, size=(780, 350), times=[1.0, 3.0, 5.5, 7.2], )


FIGS = [TonemapCurves, TonemapReinhard, TonemapHable, AutoExposureHistogram, AutoExposureAdapt, BloomStages, BloomMipChain, DualFilter, GaussianSeparable, KarisFireflies, BloomIntensity]
