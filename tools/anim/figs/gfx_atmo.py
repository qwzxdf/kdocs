import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

G = "graphics/"


def PathD(pts, close=False):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts) + (" Z" if close else "")


def PhasePolar():
    name = "phase-polar"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="位相関数:光が、どの方向へ散るか（光は左から来る）")
    root = scene.root
    cx, cy, R0 = 300, 220, 130
    root.add("circle", cx=cx, cy=cy, r=R0, fill="none", stroke=LIGHT, stroke_width=1.5)
    root.add("circle", cx=cx, cy=cy, r=R0 / 2, fill="none", stroke=LIGHT, stroke_width=1)
    Arrow(scene, root, 60, cy, cx - 16, cy, color=AMBER, width=3)
    scene.Text(root, 60, cy - 14, "太陽の光", size=12, fill=AMBER)
    root.add("circle", cx=cx, cy=cy, r=6, fill=INK)

    def Rayleigh(th):
        return (1 + math.cos(th) ** 2) * 0.75 / 1.5

    def HG(g, th):
        return (1 - g * g) / (1 + g * g - 2 * g * math.cos(th)) ** 1.5

    def D(fn, scale):
        pts = []
        for k in range(121):
            th = math.pi * 2 * k / 120
            r = min(R0 * 1.6, scale * fn(th))
            pts.append((cx + r * math.cos(th), cy - r * math.sin(th)))
        return PathD(pts, True)

    ray = root.add("path", d=D(Rayleigh, R0 * 0.62), fill=BLUE, fill_opacity=0.12, stroke=BLUE, stroke_width=3, stroke_dasharray="6 4")
    gs = [(0.8, 0.0), (3.0, 0.0), (5.0, 0.5), (7.0, 0.5), (9.0, 0.76), (10.5, 0.76), (12.2, 0.9)]
    peak = lambda g: HG(g, 0.0)
    sc = lambda g: R0 * 0.45 if g < 0.01 else R0 * 0.62 / max(1.0, HG(g, 0.0)) ** 0.5 / 1.0
    mie = root.add("path", d=D(lambda t: HG(0.0, t), R0 * 0.45), fill=RED, fill_opacity=0.2, stroke=RED, stroke_width=4)
    for idx in range(1, len(gs)):
        ta, ga = gs[idx - 1]
        tb, gb = gs[idx]
        mie.Ramp(ta, tb, "d", D(lambda t, gb=gb: HG(gb, t) ** 0.7, R0 * 0.55 / (HG(gb, 0.0) ** 0.7) * 1.6 if gb > 0 else R0 * 0.45))
    scene.TextStack(root, 480, 120, [(0.0, 3.0, "g = 0:全方向に均等（等方）"), (3.0, 5.0, "g を上げていくと…"), (5.0, 7.0, "g = 0.5:前方（右）に偏る"), (7.0, 9.0, "さらに上げると…"), (9.0, 10.5, "g = 0.76（霧・ミー散乱の目安）"), (10.5, 20, "g = 0.9:強く前方だけ（太陽の周りが白くにじむ）")], size=16, fill=INK)
    scene.Text(root, 480, 260, "青の点線 = レイリー散乱（空気分子）", size=13, fill=BLUE, weight=500)
    scene.Text(root, 480, 284, "　前後対称で、ほぼ全方向", size=12, fill=GRAY, weight=500)
    scene.Text(root, 480, 316, "赤 = ミー散乱（霧・エアロゾル）", size=13, fill=RED, weight=500)
    scene.Text(root, 480, 340, "　g が大きいほど、前方へ偏る", size=12, fill=GRAY, weight=500)
    scene.Note(0.8, name, "g 0 → 0.9")
    return dict(name=name, page=G + "atmosphere/scattering/phase-function.md", before="## 位相関数", scene=scene, size=(780, 420), times=[1.0, 4.0, 6.0, 9.5])


def FogCurves():
    name = "fog-curves"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="フォグの式:距離が遠いほど、物の色が、フォグの色に近づく")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 360, 230, 100.0, 1.0, "距離", "元の色が残る割合（透過率）")
    dens = [(0.8, 1.0), (3.5, 1.0), (6.0, 2.2), (8.5, 2.2), (11.0, 0.6)]

    def Lin(d):
        return max(0.0, 1 - d / 80)

    def Exp(d, k):
        return math.exp(-k * d / 40)

    def Exp2(d, k):
        return math.exp(-((k * d / 55) ** 2))

    ax.Curve(Lin, GRAY, 3, n=50, dash="5 4")
    pe = root.add("path", d=ax.D(lambda d: Exp(d, 1.0), n=60), fill="none", stroke=BLUE, stroke_width=4)
    p2 = root.add("path", d=ax.D(lambda d: Exp2(d, 1.0), n=60), fill="none", stroke=RED, stroke_width=4)
    for idx in range(1, len(dens)):
        ta, ka = dens[idx - 1]
        tb, kb = dens[idx]
        pe.Ramp(ta, tb, "d", ax.D(lambda d, kb=kb: Exp(d, kb), n=60))
        p2.Ramp(ta, tb, "d", ax.D(lambda d, kb=kb: Exp2(d, kb), n=60))
    scene.Text(root, ax.X(52), ax.Y(0.5), "線形", size=13, fill=GRAY)
    scene.Text(root, ax.X(14), ax.Y(0.28), "指数", size=13, fill=BLUE)
    scene.Text(root, ax.X(60), ax.Y(0.12), "指数二乗", size=13, fill=RED)
    # 右:3 本の木が並ぶ景色
    scene.Text(root, 450, 100, "景色（近い・中間・遠い）", size=13, fill=GRAY)
    for i, d in enumerate((15, 45, 85)):
        x = 480 + i * 90
        tr = root.add("rect", x=x, y=130, width=44, height=110, fill="#166534")
        steps = []
        for t, k in dens:
            steps.append((t, Mix("#cbd5e1", "#166534", Exp(d, k))))
        tr.Steps("fill", steps)
    scene.TextStack(root, 450, 290, [(0.0, 3.5, "指数フォグ（青）:標準。濃さ 1.0"), (3.5, 6.0, "濃さを上げると…"), (6.0, 8.5, "濃さ 2.2:遠くが、すぐ霞む"), (8.5, 11.0, "濃さを下げると…"), (11.0, 20, "濃さ 0.6:遠くまで見える")], size=15, fill=INK)
    scene.Text(root, 450, 330, "最終色 = 物の色 × 透過率 ＋ フォグの色 × (1 − 透過率)", size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "濃さ 1 → 2.2 → 0.6")
    return dict(name=name, page=G + "atmosphere/aerial-fog/fog-equation.md", before="## フォグの式", scene=scene, size=(780, 420), times=[1.0, 4.5, 7.0, 11.5])


def HeightFogRay():
    name = "height-fog-ray"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="高さフォグ:カメラが霧の中にいるか、上にいるかで、遠景の霞み方が変わる")
    root = scene.root
    gy = 330
    # 霧の濃さ(高さで指数減衰)
    for k in range(30):
        h = k * 8
        op = 0.85 * math.exp(-h / 55)
        root.add("rect", x=40, y=gy - h - 8, width=700, height=8.5, fill="#94a3b8", fill_opacity=R(op))
    root.add("rect", x=40, y=gy, width=700, height=20, fill="#a16207", fill_opacity=0.6)
    scene.Text(root, 50, 106, "上へ行くほど、霧が薄い", size=12, fill=GRAY)
    tower = (680, gy - 100)
    tw = root.add("rect", x=670, y=gy - 140, width=24, height=140, fill="#166534")
    cam = root.add("circle", cx=90, cy=gy - 10, r=9, fill=BLUE, stroke="#ffffff", stroke_width=2)
    ray = root.add("line", x1=90, y1=gy - 10, x2=670, y2=gy - 70, stroke=BLUE, stroke_width=2.5)
    sw = root.add("rect", x=610, y=60, width=110, height=30, fill="#166534", stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, 600, 80, "塔の見え方", size=12, fill=GRAY, anchor="end")
    seq = [(0.8, 10), (3.0, 10), (7.0, 230), (9.0, 230), (11.5, 10)]
    H = 55.0

    def OptDepth(cy_):
        # カメラ(高さ cy_)から塔(高さ 70)までの視線上の、霧の濃さの積分
        n = 60
        s = 0.0
        L = 580.0
        for k in range(n):
            f = (k + 0.5) / n
            hh = cy_ + (70 - cy_) * f
            s += math.exp(-hh / H) * (L / n)
        return s * 0.0030

    for idx, (t, hh) in enumerate(seq):
        y = gy - hh
        col = Mix("#cbd5e1", "#166534", math.exp(-OptDepth(hh)))
        vals = [(cam, "cy", y), (ray, "y1", y), (sw, "fill", col)]
        for node, attr, v in vals:
            if idx == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(seq[idx - 1][0], t, attr, v)
    scene.TextStack(root, 40, 396, [(0.0, 3.0, "カメラが地面近く（霧の中）:視線が、濃い霧の中を長く通る → 塔は霞む"), (3.0, 7.0, "カメラを上げていく…"), (7.0, 9.0, "霧の上:視線が薄い霧を通る → 塔がはっきり見える"), (9.0, 20, "下げると、また霞む")], size=14, fill=INK)
    scene.Note(0.8, name, "カメラの高さ")
    return dict(name=name, page=G + "atmosphere/aerial-fog/height-fog.md", before="## 高さフォグ", scene=scene, size=(780, 420), times=[1.5, 4.5, 8.0, 11.0])


def FroxelSlices():
    name = "froxel-slices"
    scene = NewScene(name, 780, 440, duration=11.0, hold=1.5, title="froxel:視錐台を、奥行きに沿って、手前ほど細かく分ける")
    root = scene.root
    cam = (390, 400)
    near_y, far_y = 380, 90
    half_n, half_f = 18, 300
    n = 12

    def HW(f):
        return half_n + (half_f - half_n) * f

    def Y(f):
        return near_y - f * (near_y - far_y)

    root.add("polygon", points="%s,%s %s,%s %s,%s %s,%s" % (cam[0] - half_n, Y(0), cam[0] + half_n, Y(0), cam[0] + half_f, Y(1), cam[0] - half_f, Y(1)), fill="#eff6ff", stroke="#64748b", stroke_width=2)
    root.add("circle", cx=cam[0], cy=cam[1] + 6, r=8, fill=RED)
    scene.Text(root, cam[0] + 14, cam[1] + 12, "カメラ", size=12, fill=GRAY)

    def Pos(i, lam):
        s = i / n
        lin = s
        exp_ = (math.exp(3.4 * s) - 1) / (math.exp(3.4) - 1)
        return lin * (1 - lam) + exp_ * lam

    lines = []
    for i in range(n + 1):
        f = Pos(i, 0.0)
        ln = root.add("line", x1=cam[0] - HW(f), y1=R(Y(f)), x2=cam[0] + HW(f), y2=R(Y(f)), stroke="#64748b", stroke_width=2)
        lines.append((ln, i))
    seq = [(0.8, 0.0), (3.5, 0.0), (6.5, 1.0), (10.5, 1.0)]
    for idx, (t, lam) in enumerate(seq):
        for ln, i in lines:
            f = Pos(i, lam)
            for attr, v in (("x1", cam[0] - HW(f)), ("x2", cam[0] + HW(f)), ("y1", Y(f)), ("y2", Y(f))):
                if idx == 0:
                    ln.Set(t, attr, R(v))
                else:
                    ln.Ramp(seq[idx - 1][0], t, attr, R(v))
    # 縦の分割(横方向 6 本)
    for k in range(1, 6):
        u = -1 + 2 * k / 6
        root.add("line", x1=R(cam[0] + u * half_n), y1=R(Y(0)), x2=R(cam[0] + u * half_f), y2=R(Y(1)), stroke="#cbd5e1", stroke_width=1)
    scene.TextStack(root, 40, 60, [(0.0, 3.5, "奥行きを、等間隔に分けると:手前が粗すぎる"), (3.5, 6.5, "手前を細かく、奥を粗くしていく…"), (6.5, 20, "対数的に分けた froxel:近くが細かい（見た目に効率が良い）")], size=16, fill=INK)
    scene.Text(root, 40, 424, "画面の縦横に分け、奥行きに沿って分割した 3D のグリッド（上から見た断面）。各セルに、密度と光を持つ。", size=12, weight=500, fill=GRAY)
    scene.Note(0.8, name, "等間隔 → 対数")
    return dict(name=name, page=G + "atmosphere/volumetric-fog/froxel.md", before="## froxel", scene=scene, size=(780, 440), times=[1.5, 4.5, 6.0, 9.0])


def LightInjection():
    name = "light-injection"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="光の注入:各セルに、ライトの光 × 影を、書き込む")
    root = scene.root
    cols, rows, cw, ox, oy = 18, 9, 34, 60, 80
    occ = (8, 4)  # 遮蔽物のセル(上から見た)
    cells = {}
    for j in range(rows):
        for i in range(cols):
            cells[(i, j)] = root.add("rect", x=ox + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
    root.add("rect", x=ox + occ[0] * cw, y=oy + occ[1] * cw, width=cw - 1, height=cw - 1, fill="#78716c")
    scene.Text(root, ox + occ[0] * cw + cw / 2, oy + occ[1] * cw + 21, "物", size=14, fill="#ffffff", anchor="middle")
    lights = [(1, 0), (1, 4), (1, 8)]
    t0, dt = 1.0, 3.5

    def Lit(cell, L):
        # 光 L からセルへの線分が、遮蔽物セルを通るか
        x1, y1 = L[0] + 0.5, L[1] + 0.5
        x2, y2 = cell[0] + 0.5, cell[1] + 0.5
        for s in range(41):
            f = s / 40
            x, y = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
            if int(x) == occ[0] and int(y) == occ[1] and (cell != occ):
                return False
        return True

    for key, r in cells.items():
        if key == occ:
            continue
        steps = []
        for k, L in enumerate(lights):
            d = math.hypot(key[0] - L[0], key[1] - L[1])
            val = max(0.0, 1 - d / 17.0) if Lit(key, L) else 0.0
            col = Mix("#1e293b", "#fde68a", val) if val > 0 else "#334155" if True else "#f1f5f9"
            steps.append((t0 + k * dt, col))
        r.Steps("fill", steps)
    lc = root.add("circle", cx=ox + 1.5 * cw, cy=oy + 0.5 * cw, r=11, fill=AMBER, stroke="#ffffff", stroke_width=2)
    lc.Steps("cy", [(t0 + k * dt, R(oy + (L[1] + 0.5) * cw)) for k, L in enumerate(lights)])
    scene.TextStack(root, 60, 56, [(t0 + k * dt, t0 + (k + 1) * dt, "ライトを動かすと、セルの明るさ・影が、書き換わる（光の柱ができる）") for k in range(3)], size=15, fill=INK)
    scene.Text(root, 60, 398, "明るい黄 = ライトの光が届くセル（距離で減衰）。濃い灰 = 物の影になっているセル。影は、シャドウ マップで調べる。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "ライト 3 位置")
    return dict(name=name, page=G + "atmosphere/volumetric-fog/injection.md", before="## ② 光の注入", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 11.0])


def CloudThreshold():
    name = "cloud-coverage"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="雲の量（カバレッジ）:密度が、しきい値を超えた所だけが、雲になる")
    root = scene.root
    x0, x1, base = 60, 720, 300
    rnd = random.Random(15)
    pts = [rnd.random() for _ in range(14)]

    def Dn(x):
        u = (x - x0) / (x1 - x0) * 13
        i = int(u)
        f = u - i
        f = f * f * (3 - 2 * f)
        a, b = pts[i], pts[min(13, i + 1)]
        d = a + (b - a) * f
        u2 = (x - x0) / (x1 - x0) * 31
        j = int(u2)
        g = u2 - j
        g = g * g * (3 - 2 * g)
        p2 = [((j * 7 + 3) % 11) / 11.0, (((j + 1) * 7 + 3) % 11) / 11.0]
        return 0.7 * d + 0.3 * (p2[0] + (p2[1] - p2[0]) * g)

    root.add("rect", x=x0, y=100, width=x1 - x0, height=base - 100, fill="#7dd3fc", fill_opacity=0.55)
    root.add("line", x1=x0, y1=base, x2=x1, y2=base, stroke=LIGHT, stroke_width=1.5)
    dpath = root.add("path", d=PathD([(x, base - 200 * Dn(x)) for x in range(x0, x1 + 1, 4)]), fill="none", stroke="#64748b", stroke_width=2.5)
    scene.Text(root, x0, 90, "灰色の線 = 雲の密度（ノイズ）", size=12, fill=GRAY)
    cloud = root.add("path", d="M0,0", fill="#ffffff", stroke="#e2e8f0", stroke_width=2)
    thr_line = root.add("line", x1=x0, y1=base - 100, x2=x1, y2=base - 100, stroke=RED, stroke_width=2.5, stroke_dasharray="6 4")
    thr = [(0.8, 0.75), (3.5, 0.75), (7.0, 0.35), (9.5, 0.35), (11.5, 0.6)]
    states = []
    for idx in range(len(thr) - 1):
        ta, va = thr[idx]
        tb, vb = thr[idx + 1]
        for i in range(11):
            if idx > 0 and i == 0:
                continue
            f = i / 10
            states.append((Lerp(ta, tb, f), Lerp(va, vb, f)))
    prev = None
    for k, (t, th) in enumerate(states):
        pts_c = []
        for x in range(x0, x1 + 1, 4):
            v = max(0.0, Dn(x) - th)
            pts_c.append((x, base - 200 * (th + v) if v > 0 else base - 200 * th))
        d = "M%s,%s " % (x0, R(base - 200 * th)) + " ".join("L%s,%s" % (R(x), R(y)) for x, y in pts_c) + " L%s,%s Z" % (x1, R(base - 200 * th))
        if k == 0:
            cloud.Set(t, "d", d); thr_line.Set(t, "y1", R(base - 200 * th)); thr_line.Set(t, "y2", R(base - 200 * th))
        else:
            cloud.Ramp(prev, t, "d", d); thr_line.Ramp(prev, t, "y1", R(base - 200 * th)); thr_line.Ramp(prev, t, "y2", R(base - 200 * th))
        prev = t
    scene.TextStack(root, 60, 56, [(0.0, 3.5, "しきい値が高い（赤線）:雲は少ない（晴れ）"), (3.5, 7.0, "しきい値を下げていくと…"), (7.0, 9.5, "しきい値が低い:雲が増える（曇り）"), (9.5, 20, "しきい値を戻すと、雲が減る")], size=16, fill=INK)
    scene.Text(root, 60, 340, "白い部分 = しきい値を超えた密度 = 雲。しきい値 = 1 − カバレッジ。1 つの値で、天気（晴れ・曇り）を制御できる。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "しきい値 0.75 → 0.35 → 0.6")
    return dict(name=name, page=G + "atmosphere/clouds/density-model.md", before="## 密度のモデル", scene=scene, size=(780, 420), times=[1.5, 4.5, 8.0, 11.0])


def RadialStreak():
    name = "radial-streak"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="放射ぼかし:各画素から太陽へ向かい、明るさを集める")
    root = scene.root
    root.add("rect", x=40, y=80, width=700, height=260, fill="#7dd3fc", rx=6)
    sun = (600, 130)
    f1 = Blur(scene, "rs-glow", 14)
    root.add("circle", cx=sun[0], cy=sun[1], r=48, fill="#fff7d6", fill_opacity=0.9, filter=f1)
    root.add("circle", cx=sun[0], cy=sun[1], r=20, fill="#fff7d6")
    # 木のシルエット
    for (x, w, h) in ((300, 40, 180), (370, 22, 130), (460, 36, 200)):
        root.add("rect", x=x, y=340 - h, width=w, height=h, fill="#14532d")
    trees = ((300, 40, 180), (370, 22, 130), (460, 36, 200))

    def InSky(x, y):
        for (xx, w, h) in trees:
            if xx <= x <= xx + w and 340 - h <= y <= 340:
                return False
        return True

    pxs = [(540, 300, "画素 A:太陽との間に、さえぎる物がない"), (250, 310, "画素 B:途中に木が 3 本ある"), (415, 325, "画素 C:木が 1 本だけ手前にある")]
    t0, dt = 1.0, 4.0
    for k, (px, py, label) in enumerate(pxs):
        tk = t0 + k * dt
        g = root.add("g", opacity=0)
        g.Show(tk, tk + dt)
        g.add("circle", cx=px, cy=py, r=8, fill="#ef4444", stroke="#ffffff", stroke_width=2)
        n = 10
        bright = 0
        for s in range(1, n + 1):
            f = s / n
            x, y = px + (sun[0] - px) * f, py + (sun[1] - py) * f
            sky = InSky(x, y)
            if sky:
                bright += 1
            g.add("circle", cx=R(x), cy=R(y), r=4.5, fill="#fde047" if sky else "#0f172a", stroke="#ffffff", stroke_width=1.5)
        g.add("line", x1=px, y1=py, x2=sun[0], y2=sun[1], stroke="#94a3b8", stroke_width=1, stroke_dasharray="3 3")
        scene.Text(g, 40, 372, "%s → 明るいサンプル %d / %d" % (label, bright, n), size=15, fill=INK)
        res = g.add("rect", x=620, y=360, width=80, height=22, fill=Gray(bright / n), stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, 40, 404, "サンプルが、空（明るい）なら +、木（暗い）なら 0。多いほど明るい筋。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "3 つの画素")
    return dict(name=name, page=G + "atmosphere/god-rays/radial-blur.md", before="## 画面空間の放射ぼかし", scene=scene, size=(780, 420), times=[2.0, 5.5, 9.5, 12.5])


def DayNight():
    name = "day-night"
    scene = NewScene(name, 780, 420, duration=16.0, hold=1.5, title="昼夜のサイクル:時刻から、空・太陽・光の色が、いっせいに変わる")
    root = scene.root
    x0, x1, hy = 40, 740, 300
    sky = root.add("rect", x=x0, y=70, width=x1 - x0, height=hy - 70, fill="#0b1224")
    glow = root.add("rect", x=x0, y=190, width=x1 - x0, height=hy - 190, fill="#fb923c", opacity=0)
    stars = [root.add("circle", cx=x0 + 30 + (i * 97) % 640, cy=84 + (i * 53) % 130, r=1.8, fill="#ffffff", opacity=1) for i in range(26)]
    ground = root.add("rect", x=x0, y=hy, width=x1 - x0, height=70, fill="#334155")
    sun = root.add("circle", cx=x0, cy=hy, r=22, fill="#fde68a", opacity=0)
    moon = root.add("circle", cx=x0, cy=hy, r=16, fill="#e2e8f0", opacity=0)
    tm = lambda h: 1.0 + h / 24.0 * 14.0
    # 時刻(h):0..24
    sky_keys = [(0, "#0b1224"), (5, "#0b1224"), (6.5, "#f59e8b"), (8, "#7dd3fc"), (12, "#38bdf8"), (16, "#7dd3fc"), (18, "#fb923c"), (19.5, "#312e81"), (21, "#0b1224"), (24, "#0b1224")]
    sky.Steps("fill", []) if False else None
    prev = None
    for i, (h, col) in enumerate(sky_keys):
        t = tm(h)
        if i == 0:
            sky.Set(0.0 + 0.0001, "fill", col) if False else None
        if i > 0:
            sky.Ramp(tm(sky_keys[i - 1][0]), t, "fill", col)
    glow_keys = [(0, 0), (5, 0), (6.5, 0.7), (8, 0), (16, 0), (18, 0.8), (19.5, 0), (24, 0)]
    for i in range(1, len(glow_keys)):
        glow.Ramp(tm(glow_keys[i - 1][0]), tm(glow_keys[i][0]), "opacity", glow_keys[i][1])
    for st in stars:
        keys = [(0, 1), (5, 1), (7, 0), (18, 0), (20, 1), (24, 1)]
        for i in range(1, len(keys)):
            st.Ramp(tm(keys[i - 1][0]), tm(keys[i][0]), "opacity", keys[i][1])
    # 太陽:6 時に東(左)から、18 時に西(右)へ
    frames = 40
    for body, h0, h1, vis in ((sun, 6, 18, 1), (moon, 18, 30, 1)):
        prevt = None
        for f in range(frames + 1):
            u = f / frames
            hh = h0 + (h1 - h0) * u
            th = math.pi * u
            x = x0 + 30 + (x1 - x0 - 60) * u
            y = hy - 180 * math.sin(th)
            t = tm(hh) if hh <= 24 else tm(hh - 24)
            if hh > 24:
                continue
            if prevt is None:
                body.Set(t, "cx", R(x)); body.Set(t, "cy", R(y)); body.Set(t, "opacity", 1)
            else:
                body.Ramp(prevt, t, "cx", R(x)); body.Ramp(prevt, t, "cy", R(y))
            prevt = t
        if body is sun:
            body.Set(tm(18), "opacity", 0)
            body.Set(0.0001, "opacity", 0) if False else None
    # 月:18 時〜24 時(右から昇る)と、0 時〜6 時(左へ沈む)は、ここでは 18-24 だけ表示
    scene.TextStack(root, 40, 52, [(tm(0), tm(6), "夜（0〜6 時）:月と星"), (tm(6), tm(8), "日の出:空がオレンジに染まる"), (tm(8), tm(16), "昼:青い空。太陽が高い（白い光）"), (tm(16), tm(19.5), "夕方:再びオレンジ、影が長い"), (tm(19.5), 20, "夜:星が出る")], size=15, fill=INK)
    scene.Text(root, 40, 396, "1 つの「時刻」から、太陽の位置・空の色・光の色・星を計算する。環境光（IBL）も、時刻に合わせて更新する。", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "0 時 → 24 時")
    return dict(name=name, page=G + "atmosphere/sky-models/day-night.md", before="## 昼夜のサイクル", scene=scene, size=(780, 420), times=[1.5, 5.5, 9.0, 13.5])


def Rayleigh4():
    name = "rayleigh-wavelength"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="レイリー散乱:波長が短い（青い）光ほど、強く散る（1 / λ⁴）")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 400, 220, 700.0, 1.0, "波長（nm）", "散乱の強さ", xmin=400.0)
    sc = lambda l: (400.0 / l) ** 4
    ax.Curve(lambda l: sc(l), PURPLE, 4, n=60, x0=400, x1=700)
    # スペクトルのバー
    def Wl2rgb(l):
        if l < 440:
            return ((440 - l) / 40, 0, 1)
        if l < 490:
            return (0, (l - 440) / 50, 1)
        if l < 510:
            return (0, 1, (510 - l) / 20)
        if l < 580:
            return ((l - 510) / 70, 1, 0)
        if l < 645:
            return (1, (645 - l) / 65, 0)
        return (1, 0, 0)

    for k in range(60):
        l = 400 + k * 5
        c = Wl2rgb(l)
        root.add("rect", x=ax.X(l), y=ax.y + ax.h + 28, width=R(ax.w / 60 + 0.5), height=14, fill=Hex([v * 255 for v in c]))
    dot = root.add("circle", cx=ax.X(700), cy=ax.Y(sc(700)), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    steps = 28
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(steps + 1):
        l = 700 - 300 * i / steps
        t = Lerp(t0, t1, i / steps)
        if i == 0:
            dot.Set(t, "cx", ax.X(l)); dot.Set(t, "cy", ax.Y(min(1.0, sc(l) / 1.0)))
        else:
            dot.Ramp(prev, t, "cx", ax.X(l)); dot.Ramp(prev, t, "cy", ax.Y(min(1.0, sc(l))))
        prev = t
    LiveText(scene, root, 500, 120, t0, t1, steps, lambda i, f: "波長 %d nm" % (700 - 300 * f), size=20)
    LiveText(scene, root, 500, 154, t0, t1, steps, lambda i, f: "散乱の強さ %.1f 倍（700 nm 比）" % sc(700 - 300 * f) if False else "700 nm の %.1f 倍" % ((700 - 300 * f) ** -4 / 700 ** -4), size=16, fill=PURPLE)
    scene.Text(root, 500, 220, "赤（700 nm）に比べ、青（450 nm）は", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 242, "約 %.1f 倍も強く散る → 空は青い" % ((700 / 450) ** 4), size=14, fill=BLUE)
    scene.Text(root, 500, 280, "夕焼けは、光が長く通って、青が散りきり、", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 302, "赤だけが残る。", size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "波長 700 → 400 nm")
    return dict(name=name, page=G + "atmosphere/scattering/atmosphere-model.md", before="## 大気のモデル", scene=scene, size=(780, 400), times=[1.0, 4.0, 7.0, 9.5])


def SunTransmittance():
    name = "sun-transmittance"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="透過率:太陽が低いほど、光が長く大気を通り、青が先に消える")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 330, 220, 12.0, 1.0, "大気を通る長さ（天頂で 1）", "残る光の割合")
    sig = (0.10, 0.17, 0.33)  # R, G, B の消散(青が大きい)
    for c, col in enumerate((RED, GREEN, BLUE)):
        ax.Curve(lambda L, c=c: math.exp(-sig[c] * L), col, 4, n=50)
    line = root.add("line", x1=ax.X(1), y1=ax.y, x2=ax.X(1), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2.5)
    # 右:太陽
    sky = root.add("rect", x=430, y=90, width=300, height=200, fill="#7dd3fc")
    root.add("rect", x=430, y=250, width=300, height=40, fill="#334155")
    sun = root.add("circle", cx=580, cy=200, r=26, fill="#ffffff")
    steps = 30
    t0, t1 = 0.8, 10.5
    prev = None
    for i in range(steps + 1):
        f = i / steps
        elev = 90 * (1 - f) + 2 * f
        L = 1 / max(0.08, math.sin(math.radians(elev)))
        L = min(12.0, L)
        raw = [math.exp(-sig[c] * L) for c in range(3)]
        mx = max(raw)
        col = [255 * raw[c] / mx * (0.55 + 0.45 * mx) for c in range(3)]
        skycol = Mix("#7dd3fc", "#fb923c", min(1.0, max(0.0, (L - 1.5) / 7)))
        skycol = Mix(skycol, "#1e1b4b", min(1.0, max(0.0, (L - 8) / 4)))
        t = Lerp(t0, t1, f)
        sy = 250 - 150 * math.sin(math.radians(elev)) - 0
        vals = [(line, "x1", ax.X(L)), (line, "x2", ax.X(L)), (sun, "fill", Hex(col)), (sun, "cy", R(sy)), (sky, "fill", skycol)]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    LiveText(scene, root, 50, 346, t0, t1, steps, lambda i, f: "太陽の高さ %d° → 大気を通る長さ %.1f" % (90 * (1 - f) + 2 * f, min(12.0, 1 / max(0.08, math.sin(math.radians(90 * (1 - f) + 2 * f))))), size=15, fill=INK)
    scene.Text(root, 50, 380, "透過率 = exp(−消散係数 × 長さ)。青（消散が大）が先に消え、白 → 黄 → 橙 → 赤と変わる。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "太陽の高さ 90° → 2°")
    return dict(name=name, page=G + "atmosphere/scattering/transmittance.md", before="## 透過率", scene=scene, size=(780, 420), times=[1.0, 4.0, 7.0, 10.0])


FIGS = [PhasePolar, FogCurves, HeightFogRay, FroxelSlices, LightInjection, CloudThreshold, RadialStreak, DayNight, Rayleigh4, SunTransmittance]
