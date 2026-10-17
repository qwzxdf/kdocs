import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

G = "graphics/"


def SsrHizSteps():
    name = "ssr-hiz-steps"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="線形マーチと Hi-Z:同じ当たりを、何ステップで見つけるか")
    root = scene.root
    hit = 562
    x0 = 60
    rows = [("線形マーチ（一定の歩幅）", 110, "lin"), ("Hi-Z トレース（空いていれば大きく、近づけば細かく）", 250, "hiz")]
    for title, y, kind in rows:
        scene.Text(root, 40, y - 44, title, size=14, fill=INK)
        root.add("line", x1=x0, y1=y, x2=720, y2=y, stroke="#cbd5e1", stroke_width=2)
        root.add("rect", x=hit, y=y - 50, width=26, height=50, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
        scene.Text(root, hit + 13, y - 56, "物体", size=11, fill=GRAY, anchor="middle")
    # 線形
    lin = []
    x = x0
    while x < hit and len(lin) < 60:
        x += 18
        lin.append(x)
    t0, dt = 0.8, 0.11
    for i, x in enumerate(lin):
        c = root.add("circle", cx=x, cy=110, r=4.5, fill=GRAY if x < hit else RED, opacity=0)
        c.Show(t0 + i * dt)
    # Hi-Z
    hz = [(92, 32), (156, 64), (284, 128), (412, 128), (540, 64), (604, 32), (572, 16), (556, 8), (564, 8)]
    t1, dt2 = 0.8, 0.55
    for i, (x, size) in enumerate(hz):
        g = root.add("g", opacity=0)
        g.Show(t1 + i * dt2)
        g.add("rect", x=R(x - size / 2), y=R(250 - 14 - size * 0.12), width=size, height=R(28 + size * 0.24), fill=BLUE, fill_opacity=0.15, stroke=BLUE, stroke_width=1.5)
        g.add("circle", cx=x, cy=250, r=5, fill=BLUE if i < len(hz) - 1 else RED)
    n_lin, n_hiz = len(lin), len(hz)
    scene.Counter(root, 620, 80, [(t0 + (i + 1) * dt, i + 1) for i in range(n_lin)], size=22, fill=INK, start_value=0)
    scene.Text(root, 680, 80, "ステップ", size=13, fill=GRAY)
    scene.Counter(root, 620, 220, [(t1 + (i + 1) * dt2, i + 1) for i in range(n_hiz)], size=22, fill=BLUE, start_value=0)
    scene.Text(root, 680, 220, "ステップ", size=13, fill=GRAY)
    end = max(t0 + n_lin * dt, t1 + n_hiz * dt2)
    scene.TextStack(root, 40, 360, [(0.0, end, "歩幅を変えて、同じ物体を探す（左から右へ進む）"), (end, 20, "線形は %d ステップ、Hi-Z は %d ステップ。広い空間ほど、差が大きい" % (n_lin, n_hiz))], size=15, fill=INK)
    scene.TextStack(root, 40, 384, [(0.0, 20, "Hi-Z:深度の最小値のミップを使い、「このブロックの中には何もない」と分かれば、ブロックごと飛ばす。")], size=12, fill=GRAY, weight=500)
    scene.Note(t0, name, "線形 vs Hi-Z")
    return dict(name=name, page=G + "reflections/ssr-hiz.md", before="## 探索アルゴリズム", scene=scene, size=(780, 400), times=[2.0, 4.0, 7.0, 10.5])


def PlanarMirror():
    name = "planar-mirror"
    scene = NewScene(name, 780, 460, duration=12.0, hold=1.5, title="平面反射:鏡の裏側に、鏡映したカメラを置いて、もう一度描く")
    root = scene.root
    yp = 250
    root.add("rect", x=60, y=yp - 4, width=660, height=8, fill="#38bdf8")
    scene.Text(root, 700, yp - 12, "鏡（水面）", size=12, fill="#0284c7", anchor="end")
    root.add("rect", x=60, y=yp + 4, width=660, height=150, fill="#e0f2fe", fill_opacity=0.5)
    O = (520, 170)
    root.add("polygon", points="%s,%s %s,%s %s,%s" % (O[0] - 22, O[1] + 40, O[0] + 22, O[1] + 40, O[0], O[1] - 10), fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    Om = (O[0], 2 * yp - O[1])
    root.add("polygon", points="%s,%s %s,%s %s,%s" % (Om[0] - 22, Om[1] - 40, Om[0] + 22, Om[1] - 40, Om[0], Om[1] + 10), fill="#b8794b", fill_opacity=0.35, stroke="#7a4b2a", stroke_width=1.5, stroke_dasharray="4 3")
    scene.Text(root, Om[0] + 30, Om[1], "鏡像の物体", size=12, fill=GRAY)
    cam = root.add("circle", cx=140, cy=110, r=11, fill=BLUE, stroke="#ffffff", stroke_width=2)
    vcam = root.add("circle", cx=140, cy=2 * yp - 110, r=11, fill=BLUE, fill_opacity=0.35, stroke=BLUE, stroke_width=2, stroke_dasharray="4 3")
    scene.Text(root, 160, 104, "カメラ", size=12, fill=BLUE)
    scene.Text(root, 160, 2 * yp - 104, "鏡映したカメラ", size=12, fill=BLUE)
    ray1 = root.add("line", x1=140, y1=110, x2=300, y2=yp, stroke=BLUE, stroke_width=2.5)
    ray2 = root.add("line", x1=300, y1=yp, x2=O[0], y2=O[1] + 10, stroke=BLUE, stroke_width=2.5)
    ray3 = root.add("line", x1=140, y1=2 * yp - 110, x2=Om[0], y2=Om[1], stroke=BLUE, stroke_width=1.5, stroke_dasharray="5 4")
    seq = [(0.8, 140), (4.0, 300), (7.5, 420), (10.5, 140)]
    for idx, (t, cx) in enumerate(seq):
        cy = 110
        t_ = (yp - cy) / (Om[1] - 10 - (cy)) if False else (yp - cy) / ((Om[1] - 10) - cy)
        px = cx + (O[0] - cx) * t_
        vals = [(cam, "cx", cx), (vcam, "cx", cx), (ray1, "x1", cx), (ray1, "x2", R(px)), (ray2, "x1", R(px)), (ray3, "x1", cx)]
        for node, attr, v in vals:
            if idx == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(seq[idx - 1][0], t, attr, v)
    scene.TextStack(root, 40, 60, [(0.0, 20, "カメラを動かすと、鏡映カメラも、鏡の反対側で同じ動きをする")], size=15, fill=INK)
    scene.TextStack(root, 40, 440, [(0.0, 20, "鏡映カメラで普通にシーンを描く → それがそのまま、鏡に映る絵。実線の経路 = 鏡映カメラの点線の経路（同じ点に当たる）。")], size=12, fill=GRAY, weight=500)
    scene.Note(0.8, name, "カメラ移動")
    return dict(name=name, page=G + "reflections/planar.md", before="## 鏡映の行列", scene=scene, size=(780, 460), times=[1.0, 4.0, 6.5, 9.0])


def RoughnessLobe():
    name = "roughness-lobe"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="粗さが上がると、反射の向きが広がる（GGX の山）")
    root = scene.root
    cx, cy, Rr = 250, 330, 230
    root.add("rect", x=60, y=cy, width=380, height=14, fill="#d6c7a1")
    root.add("line", x1=cx, y1=cy, x2=cx, y2=cy - 250, stroke=LIGHT, stroke_width=2, stroke_dasharray="4 4")
    scene.Text(root, cx + 8, cy - 240, "反射の中心", size=11, fill=GRAY)

    def D(alpha, th):
        a2 = alpha * alpha
        return a2 / (math.pi * ((a2 - 1) * math.cos(th) ** 2 + 1) ** 2)

    def Path(alpha):
        m = D(alpha, 0)
        pts = []
        for k in range(-60, 61):
            th = math.radians(k * 1.5)
            r = Rr * (D(alpha, th) / m) ** 0.5
            pts.append("%s,%s" % (R(cx + r * math.sin(th)), R(cy - r * math.cos(th))))
        return "M" + " L".join(pts) + " Z"

    lobe = root.add("path", d=Path(0.05), fill=BLUE, fill_opacity=0.2, stroke=BLUE, stroke_width=3.5)
    rays = [root.add("line", x1=cx, y1=cy, x2=cx, y2=cy - 150, stroke=RED, stroke_width=2, stroke_dasharray="5 3") for _ in range(7)]
    alphas = [(0.8, 0.05), (2.5, 0.05), (5.0, 0.25), (6.5, 0.25), (9.0, 0.7), (11.0, 0.7)]

    def Angles(alpha):
        out = []
        for i in range(7):
            u = (i + 0.5) / 7
            th = math.atan(alpha * math.sqrt(u / (1 - u)) * 0.9)
            sgn = -1 if i % 2 == 0 else 1
            out.append(sgn * th * (0.4 + 0.6 * (i + 1) / 7))
        return out

    for idx, (t, a) in enumerate(alphas):
        if idx == 0:
            lobe.Set(t, "d", Path(a))
        else:
            lobe.Ramp(alphas[idx - 1][0], t, "d", Path(a))
        for r_, th in zip(rays, Angles(a)):
            x2, y2 = R(cx + 170 * math.sin(th)), R(cy - 170 * math.cos(th))
            if idx == 0:
                r_.Set(t, "x2", x2); r_.Set(t, "y2", y2)
            else:
                r_.Ramp(alphas[idx - 1][0], t, "x2", x2); r_.Ramp(alphas[idx - 1][0], t, "y2", y2)
    scene.TextStack(root, 480, 120, [(0.0, 2.5, "粗さ 0.05（ほぼ鏡）"), (2.5, 5.0, "粗さを上げると…"), (5.0, 6.5, "粗さ 0.25"), (6.5, 9.0, "さらに上げると…"), (9.0, 20, "粗さ 0.7（ざらざら）")], size=20, fill=INK)
    scene.TextStack(root, 480, 156, [(0.0, 2.5, "反射はほぼ 1 方向。レイ 1 本で十分"), (5.0, 6.5, "少し広がる。サンプルがばらつく"), (9.0, 20, "広く散らばる。ノイズが多く、サンプルが要る")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 480, 230, "青い山 = 反射する向きの確率", size=13, fill=BLUE, weight=500)
    scene.Text(root, 480, 254, "赤い線 = ランダムに選ぶ反射レイ", size=13, fill=RED, weight=500)
    scene.Note(0.8, name, "粗さ 0.05 → 0.25 → 0.7")
    return dict(name=name, page=G + "reflections/ssr-stochastic.md", before="## GGX 分布と重要度サンプリング", scene=scene, size=(780, 420), times=[1.5, 4.0, 6.0, 10.0])


def SsrEdgeFade():
    name = "ssr-edge-fade"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="画面の端:反射が当たった位置が端へ近づくほど、SSR を弱める")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 340, 220, 1.0, 1.0, "当たった位置（画面の横、0〜1）", "SSR の信頼度")

    def Conf(u):
        e = min(u, 1 - u)
        if u < 0 or u > 1:
            return 0.0
        v = max(0.0, min(1.0, e / 0.15))
        return v * v * (3 - 2 * v)

    ax.Curve(Conf, BLUE, 4, n=100)
    dot = root.add("circle", cx=ax.X(0.5), cy=ax.Y(1.0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    n = 30
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(n + 1):
        u = i / n
        t = Lerp(t0, t1, u)
        if i == 0:
            dot.Set(t, "cx", ax.X(u)); dot.Set(t, "cy", ax.Y(Conf(u)))
        else:
            dot.Ramp(prev, t, "cx", ax.X(u)); dot.Ramp(prev, t, "cy", ax.Y(Conf(u)))
        prev = t
    # 右:色の混合
    scene.Text(root, 430, 90, "SSR の色（空の青）", size=13, fill=GRAY)
    root.add("rect", x=430, y=100, width=130, height=40, fill="#38bdf8")
    scene.Text(root, 580, 90, "プローブの色（灰）", size=13, fill=GRAY)
    root.add("rect", x=580, y=100, width=130, height=40, fill="#94a3b8")
    mix = root.add("rect", x=505, y=190, width=130, height=60, fill="#94a3b8", stroke="#475569", stroke_width=2)
    scene.Text(root, 570, 180, "最終的な反射の色", size=13, fill=GRAY, anchor="middle")
    RampFill(mix, "fill", t0, t1, n, lambda f: Mix("#94a3b8", "#38bdf8", Conf(f)))
    LiveText(scene, root, 430, 290, t0, t1, n, lambda i, f: "位置 %.2f → 信頼度 %.2f" % (i / n, Conf(i / n)), size=16, fill=INK)
    scene.TextStack(root, 50, 350, [(0.0, 20, "端に近いと、画面の外にあるはずの物が足りない。信頼度で、SSR とフォールバック（プローブ）を混ぜる。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "当たりが画面の端へ")
    return dict(name=name, page=G + "reflections/ssr-fallback.md", before="## 信頼度（Confidence）", scene=scene, size=(780, 400), times=[1.5, 4.0, 7.0, 9.8])


def ParallaxBox():
    name = "parallax-box"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="視差補正:プローブの位置ではなく、反射点から、箱の壁までの交点で引く")
    root = scene.root
    bx0, by0, bx1, by1 = 120, 90, 700, 350
    root.add("rect", x=bx0, y=by0, width=bx1 - bx0, height=by1 - by0, fill="#f8fafc", stroke=INK, stroke_width=4)
    scene.Text(root, bx0 + 8, by0 + 20, "部屋（プローブの影響範囲の箱）", size=12, fill=GRAY, weight=500)
    P = (330, 220)
    root.add("circle", cx=P[0], cy=P[1], r=9, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, P[0] + 12, P[1] + 22, "プローブ", size=12, fill=AMBER)
    Rv = (0.62, -0.78)

    def Hit(px, py, dx, dy):
        best = None
        for (x, y, tx) in ((bx1, None, (bx1 - px) / dx if dx > 0 else None), (bx0, None, (bx0 - px) / dx if dx < 0 else None)):
            pass
        ts = []
        if dx > 0:
            ts.append((bx1 - px) / dx)
        if dx < 0:
            ts.append((bx0 - px) / dx)
        if dy > 0:
            ts.append((by1 - py) / dy)
        if dy < 0:
            ts.append((by0 - py) / dy)
        t = min(t for t in ts if t > 0)
        return px + dx * t, py + dy * t

    X = root.add("circle", cx=200, cy=by1 - 10, r=8, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, 200, by1 + 28, "反射する点", size=12, fill=BLUE, anchor="middle")
    ray = root.add("line", x1=200, y1=by1 - 10, x2=0, y2=0, stroke=BLUE, stroke_width=2.5)
    naive = root.add("line", x1=P[0], y1=P[1], x2=0, y2=0, stroke=RED, stroke_width=2, stroke_dasharray="6 4")
    corr = root.add("line", x1=P[0], y1=P[1], x2=0, y2=0, stroke=GREEN, stroke_width=3)
    hn = root.add("circle", cx=0, cy=0, r=6, fill=RED)
    hc = root.add("circle", cx=0, cy=0, r=6, fill=GREEN)
    seq = [(0.8, 200), (3.5, 330), (6.5, 520), (9.5, 200)]
    for idx, (t, x) in enumerate(seq):
        py_ = by1 - 10
        hx, hy = Hit(x, py_, Rv[0], Rv[1])
        nx, ny = Hit(P[0], P[1], Rv[0], Rv[1])
        vals = [(X, "cx", x), (ray, "x1", x), (ray, "x2", R(hx)), (ray, "y2", R(hy)), (naive, "x2", R(nx)), (naive, "y2", R(ny)), (corr, "x2", R(hx)), (corr, "y2", R(hy)),
                (hn, "cx", R(nx)), (hn, "cy", R(ny)), (hc, "cx", R(hx)), (hc, "cy", R(hy))]
        for node, attr, v in vals:
            if idx == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(seq[idx - 1][0], t, attr, v)
    scene.TextStack(root, 40, 60, [(0.0, 20, "青い線 = 反射レイ。壁に当たる点が、本当に映る場所")], size=15, fill=INK)
    scene.Text(root, 40, 404, "赤（補正なし）:プローブから、反射方向をそのまま引く → 本当の点とずれる。", size=13, fill=RED, weight=500)
    scene.Text(root, 40, 426, "緑（補正あり）:壁の交点を求め、プローブから、その交点への向きで引く → ぴったり合う。", size=13, fill=GREEN, weight=500)
    scene.Note(0.8, name, "反射する点を動かす")
    return dict(name=name, page=G + "reflections/probes/parallax.md", before="### 視差補正：プローブの範囲を", scene=scene, size=(780, 440), times=[1.5, 3.5, 6.5, 9.0])


def PrefilterMips():
    name = "prefilter-mips"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="事前フィルタ:粗さごとに、ぼかしたキューブ マップを用意しておく")
    root = scene.root
    stds = [0, 2, 4, 8, 14]
    boxes = []
    for i, sd in enumerate(stds):
        x = 40 + i * 140
        fid = Blur(scene, "pf-%d" % i, max(sd, 0.01)) if sd else None
        clip = scene.defs.add("clipPath", id="pf-clip-%d" % i)
        clip.add("rect", x=x, y=110, width=120, height=80)
        g = root.add("g", clip_path="url(#pf-clip-%d)" % i)
        g.add("rect", x=x, y=110, width=120, height=80, fill="#0f172a")
        for (dx, dy, r, col) in ((24, 30, 9, "#fde68a"), (80, 52, 12, "#fca5a5"), (60, 18, 6, "#93c5fd"), (100, 24, 8, "#bbf7d0")):
            attrs = dict(cx=x + dx, cy=110 + dy, r=r, fill=col)
            if fid:
                attrs["filter"] = fid
            g.add("circle", **attrs)
        root.add("rect", x=x, y=110, width=120, height=80, fill="none", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, x + 60, 100, "ミップ %d" % i, size=13, fill=INK, anchor="middle")
        scene.Text(root, x + 60, 210, "粗さ %.2f" % (i / 4), size=12, fill=GRAY, anchor="middle")
    sel = root.add("rect", x=36, y=106, width=128, height=88, fill="none", stroke=AMBER, stroke_width=4)
    seq = [(0.8, 0), (3.0, 1), (5.2, 2), (7.4, 3), (9.6, 4)]
    sel.Steps("x", [(t, 36 + i * 140) for t, i in seq])
    texts = [(t, seq[k + 1][0] if k + 1 < len(seq) else 20, "粗さ %.2f → ミップ %d を読む" % (i / 4, i)) for k, (t, i) in enumerate(seq)]
    scene.TextStack(root, 40, 290, texts, size=20, fill=INK)
    scene.TextStack(root, 40, 322, [(0.8, 3.0, "鏡のような面:くっきりしたミップ"), (3.0, 7.4, "少し粗い面:ぼけたミップ"), (7.4, 20, "ざらざらの面:とてもぼけたミップ")], size=14, fill=GRAY, weight=500)
    scene.Text(root, 40, 380, "実行時は、粗さからミップを選んで 1 回読むだけ。ぼかしは事前に計算済み（Split-Sum 近似）。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "粗さ 0 → 1")
    return dict(name=name, page=G + "reflections/probes/prefilter.md", before="### ミップ レベルの選び方", scene=scene, size=(780, 400), times=[1.5, 4.0, 6.5, 11.0])


def RtHybridFlow():
    name = "rt-hybrid-flow"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="ハイブリッド:画素ごとに、使う方式を選ぶ")
    root = scene.root

    def Box(x, y, w, h, text, col):
        root.add("rect", x=x, y=y, width=w, height=h, rx=8, fill=col, fill_opacity=0.18, stroke=col, stroke_width=2.5)
        scene.Text(root, x + w / 2, y + h / 2 + 5, text, size=13, fill=INK, anchor="middle")

    Box(40, 170, 120, 50, "反射が必要な画素", INK)
    Box(210, 170, 150, 50, "SSR が当たった?", BLUE)
    Box(420, 60, 150, 50, "SSR の色を使う", BLUE)
    Box(420, 170, 150, 50, "粗さが高い?", PURPLE)
    Box(620, 120, 130, 50, "プローブを使う", AMBER)
    Box(620, 250, 130, 50, "レイトレを使う", GREEN)
    for (x1, y1, x2, y2) in ((160, 195, 210, 195), (360, 195, 420, 195), (390, 185, 420, 90), (570, 195, 620, 145), (570, 200, 620, 270)):
        Arrow(scene, root, x1, y1, x2, y2, color=GRAY, width=2)
    scene.Text(root, 400, 138, "はい", size=11, fill=BLUE, weight=700)
    scene.Text(root, 372, 215, "いいえ", size=11, fill=GRAY, weight=700)
    scene.Text(root, 586, 148, "はい", size=11, fill=AMBER, weight=700)
    scene.Text(root, 590, 252, "いいえ", size=11, fill=GREEN, weight=700)
    pixels = [("画素 A(鏡面・当たった)", [(100, 195), (285, 195), (495, 85)], "#e5484d"),
              ("画素 B(画面外へ出た・滑らか)", [(100, 195), (285, 195), (495, 195), (685, 275)], "#2563eb"),
              ("画素 C(ざらざら・外れ)", [(100, 195), (285, 195), (495, 195), (685, 145)], "#e5aa28")]
    t0 = 1.0
    for k, (label, path, col) in enumerate(pixels):
        tk = t0 + k * 4.0
        tok = root.add("circle", cx=path[0][0], cy=path[0][1], r=10, fill=col, stroke="#ffffff", stroke_width=2, opacity=0)
        tok.Show(tk, tk + 3.8)
        for i, (x, y) in enumerate(path):
            t = tk + i * 0.9
            if i == 0:
                tok.Set(t, "cx", x); tok.Set(t, "cy", y)
            else:
                tok.Ramp(tk + (i - 1) * 0.9, t, "cx", x); tok.Ramp(tk + (i - 1) * 0.9, t, "cy", y)
        scene.TextStack(root, 40, 350, [(tk, tk + 4.0, label)], size=16, fill=col)
    scene.Text(root, 40, 390, "SSR で当たれば最も安い。外れた画素だけ、レイトレかプローブへ。粗い面は、プローブで十分（ノイズが多く、レイトレの価値が低い）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "画素 A / B / C")
    return dict(name=name, page=G + "reflections/rt-reflections/hybrid.md", before="## ハイブリッド構成", scene=scene, size=(780, 420), times=[2.0, 5.5, 9.0, 12.0])


def PremultFringe():
    name = "premult-fringe"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="縁の黒い線:ストレート アルファは、補間で「透明部分の色」が混ざる")
    root = scene.root
    # 2 テクセル:左=不透明な赤(α=1)、右=透明(RGB は黒、α=0)
    for i, (col, lab) in enumerate((("#e5484d", "テクセル A:赤・不透明（α = 1）"), ("#000000", "テクセル B:透明（α = 0）、色は黒"))):
        x = 60 + i * 300
        root.add("rect", x=x, y=100, width=300, height=70, fill=col if i == 0 else "#ffffff", stroke="#94a3b8", stroke_width=1.5)
        if i == 1:
            root.add("rect", x=x, y=100, width=300, height=70, fill="url(#pf-pat)" if False else "#f1f5f9")
            scene.Text(root, x + 150, 140, "（透明。中の RGB は黒）", size=13, fill=GRAY, anchor="middle")
        scene.Text(root, x + 150, 90, lab, size=13, fill=INK, anchor="middle")
    rows = [("ストレート（補間 → その後でブレンド）", 230, False), ("乗算済み（先に α を掛けて保存 → 補間）", 330, True)]
    n = 24
    for title, y, pre in rows:
        scene.Text(root, 60, y - 16, title, size=13, fill=RED if not pre else GREEN)
        for k in range(n):
            f = (k + 0.5) / n  # 0=A, 1=B
            a = 1 - f
            if not pre:
                # 補間した色 (赤*(1-f) + 黒*f)、補間した α → 背景(白)にブレンド
                rgb = [(0xe5 * (1 - f)), (0x48 * (1 - f)), (0x4d * (1 - f))]
                col = [rgb[i] * a + 255 * (1 - a) for i in range(3)]
            else:
                rgb = [(0xe5 * a), (0x48 * a), (0x4d * a)]  # 乗算済み(先に α を掛けた色)を補間 → そのまま足す
                col = [rgb[i] + 255 * (1 - a) for i in range(3)]
            root.add("rect", x=60 + k * 25, y=y, width=25, height=40, fill=Hex(col))
        root.add("rect", x=60, y=y, width=n * 25, height=40, fill="none", stroke="#94a3b8", stroke_width=1.5)
    probe = root.add("rect", x=60, y=222, width=25, height=156, fill="none", stroke=AMBER, stroke_width=3)
    probe.Steps("x", [(1.0 + k * 0.4, 60 + k * 25) for k in range(n)])
    scene.TextStack(root, 60, 398, [(0.0, 1.0, "A と B の境界を、バイリニア補間で読む"), (1.0, 11.0, "ストレートは、中間で「黒」が混ざって暗い縁（フリンジ）。乗算済みは、混ざらない"), (11.0, 20, "→ 乗算済みアルファなら、縁が自然に薄くなるだけ")], size=14, fill=INK)
    scene.Note(1.0, name, "境界を走査")
    return dict(name=name, page=G + "translucency/blending-sorting/premultiplied.md", before="## 乗算済みアルファ", scene=scene, size=(780, 420), times=[2.0, 4.0, 6.5, 11.0])


def BlendModes():
    name = "blend-modes"
    scene = NewScene(name, 780, 360, duration=10.0, hold=1.5, title="ブレンドの種類:同じ円を、3 つの混ぜ方で重ねる")
    root = scene.root
    panels = [("通常（アルファ）", "normal", 0.6), ("加算（光・炎）", "screen", 1.0), ("乗算（影・色ガラス）", "multiply", 1.0)]
    t0, dt = 0.8, 2.8
    for i, (title, mode, op) in enumerate(panels):
        x = 30 + i * 250
        scene.Text(root, x + 100, 70, title, size=14, fill=INK, anchor="middle")
        for k, col in enumerate(("#e5484d", "#2ea043", "#2563eb", "#fde68a")):
            root.add("rect", x=x + k * 50, y=90, width=50, height=170, fill=col)
        root.add("rect", x=x, y=90, width=200, height=170, fill="none", stroke="#94a3b8", stroke_width=1.5)
        c = root.add("circle", cx=x + 100, cy=175, r=70, fill="#f97316" if mode != "multiply" else "#8ec5ff", opacity=0, style="mix-blend-mode:%s" % mode)
        c.Set(t0 + i * dt, "opacity", op if mode != "normal" else 0.6)
        scene.TextStack(root, x + 100, 292, [(t0 + i * dt, 20, {"normal": "背景と混ざる（α で）", "screen": "明るくなる（足し算）", "multiply": "暗くなる（掛け算）"}[mode])], size=14, fill=INK, anchor="middle")
    scene.Text(root, 30, 336, "通常:SrcAlpha / InvSrcAlpha、加算:One / One、乗算:Zero / SrcColor", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "通常 → 加算 → 乗算")
    return dict(name=name, page=G + "translucency/blending-sorting/blend-state.md", before="### ブレンドの種類", scene=scene, size=(780, 360), times=[1.0, 4.0, 7.0, 10.0])


def SoftParticles():
    name = "soft-particles-depth"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="ソフト パーティクル:地面に近い部分ほど、薄くして、交差の線を消す")
    root = scene.root
    gy = 250
    root.add("rect", x=40, y=gy, width=700, height=14, fill="#d6c7a1")
    # 斜めのパーティクル面
    root.add("polygon", points="260,90 300,90 520,%s 480,%s" % (gy, gy), fill="#94a3b8", fill_opacity=0.25, stroke="#64748b", stroke_width=2, stroke_dasharray="6 4")
    scene.Text(root, 180, 110, "パーティクルの板", size=12, fill=GRAY)
    # 比較バー
    bars = [("硬い（そのまま）", 310, "hard"), ("ソフト（深度差でフェード）", 360, "soft")]
    for title, y, kind in bars:
        scene.Text(root, 40, y - 6, title, size=13, fill=INK)
        n = 40
        for k in range(n):
            x = 260 + k * 5.5
            # k = 0 が板の上のほう、n が地面との交差
            diff = (n - k) / n  # 地面との深度差(大→小)
            a = 1.0 if kind == "hard" else min(1.0, diff / 0.35)
            root.add("rect", x=x, y=y, width=5.6, height=30, fill=Hex([255 - 190 * a] * 3).replace("#", "#") if False else Hex([255 - 150 * a, 255 - 130 * a, 255 - 100 * a]))
    scene.Text(root, 260, 296, "← 板の上側", size=11, fill=GRAY)
    scene.Text(root, 480, 296, "地面との交差 →", size=11, fill=GRAY, anchor="end")
    probe = root.add("rect", x=260, y=300, width=5.6, height=100, fill="none", stroke=AMBER, stroke_width=2.5)
    probe.Steps("x", [(1.0 + k * 0.22, R(260 + k * 5.5)) for k in range(40)])
    LiveText(scene, root, 540, 330, 1.0, 1.0 + 40 * 0.22, 20, lambda i, f: "深度差 %.2f → 不透明度 %.2f" % (1 - f, min(1.0, (1 - f) / 0.35)), size=14, fill=INK)
    scene.TextStack(root, 40, 60, [(0.0, 20, "シーンの深度と、板の深度の差を見て、不透明度を決める")], size=15, fill=INK)
    scene.Text(root, 540, 360, "硬い:交差で不透明のまま → 線が見える", size=12, fill=RED, weight=500)
    scene.Text(root, 540, 382, "ソフト:交差に向けて 0 → 線が消える", size=12, fill=GREEN, weight=500)
    scene.Note(1.0, name, "交差へ向けて走査")
    return dict(name=name, page=G + "translucency/blending-sorting/soft-particles.md", before="## 深度の読み取り", scene=scene, size=(780, 420), times=[1.5, 4.0, 6.5, 9.5])


def A2cCoverage():
    name = "a2c-coverage"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="Alpha to Coverage:アルファを、MSAA のサンプルの数に置き換える")
    root = scene.root
    cx, cy, s = 160, 210, 190
    root.add("rect", x=cx - s / 2, y=cy - s / 2, width=s, height=s, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    spots = [(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)]
    order = [0, 3, 1, 2]
    dots = []
    for (dx, dy) in spots:
        dots.append(root.add("circle", cx=cx + dx * s, cy=cy + dy * s, r=14, fill="#ffffff", stroke=INK, stroke_width=2.5))
    seq = [(1.0, 0.0), (2.6, 0.25), (4.2, 0.5), (5.8, 0.75), (7.4, 1.0), (9.0, 0.5)]
    for k, d in enumerate(dots):
        steps = []
        for t, a in seq:
            covered = order.index(k) < round(a * 4)
            steps.append((t, "#e5484d" if covered else "#ffffff"))
        d.Steps("fill", steps)
    res = root.add("rect", x=420, y=120, width=170, height=100, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
    steps = []
    for t, a in seq:
        steps.append((t, Hex([255 - (255 - 0xe5) * (round(a * 4) / 4), 255 - (255 - 0x48) * (round(a * 4) / 4), 255 - (255 - 0x4d) * (round(a * 4) / 4)])))
    res.Steps("fill", steps)
    scene.Text(root, 505, 110, "解像した結果（4 サンプルの平均）", size=12, fill=GRAY, anchor="middle")
    scene.TextStack(root, 420, 260, [(t, seq[k + 1][0] if k + 1 < len(seq) else 20, "アルファ %.2f → 覆うサンプル %d / 4" % (a, round(a * 4))) for k, (t, a) in enumerate(seq)], size=18, fill=INK)
    scene.TextStack(root, 420, 292, [(1.0, 20, "覆ったサンプルだけに、色を書く")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 60, 340, "1 画素の中の 4 つのサンプル。アルファに応じた数のサンプルだけを「覆う」。ソート不要で、縁がなめらかになる。", size=12, weight=500, fill=GRAY)
    scene.Text(root, 60, 362, "MSAA 4x なら 5 段階（0〜4）。段数が少ないので、縞が出やすい（ハッシュドや TAA と併用する）。", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "アルファ 0 → 1")
    return dict(name=name, page=G + "translucency/alpha-test/alpha-to-coverage.md", before="## Alpha to Coverage", scene=scene, size=(780, 400), times=[1.5, 3.5, 6.5, 8.5])


def HashedAlpha():
    name = "hashed-alpha-sweep"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="ハッシュド アルファ:画素ごとにしきい値を変えると、アルファが「密度」になる")
    root = scene.root
    rnd = random.Random(12)
    cols, rows, cw = 12, 7, 17
    thr = {(i, j): rnd.random() for i in range(cols) for j in range(rows)}
    alphas = [0.1, 0.3, 0.5, 0.7, 0.9]
    t0, dt = 1.0, 2.2
    panels = [(30, "通常の clip（しきい値 0.5）", "clip"), (270, "ハッシュド（画素ごとに変える）", "hash"), (510, "平均（TAA で重ねた結果）", "avg")]
    for px, title, kind in panels:
        scene.Text(root, px, 90, title, size=12, fill=INK)
        for j in range(rows):
            for i in range(cols):
                r = root.add("rect", x=px + i * cw, y=110 + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
                steps = []
                for k, a in enumerate(alphas):
                    if kind == "clip":
                        vis = a > 0.5
                        steps.append((t0 + k * dt, "#e5484d" if vis else "#f1f5f9"))
                    elif kind == "hash":
                        vis = a > thr[(i, j)]
                        steps.append((t0 + k * dt, "#e5484d" if vis else "#f1f5f9"))
                    else:
                        steps.append((t0 + k * dt, Hex([255 - (255 - 0xe5) * a, 255 - (255 - 0x48) * a, 255 - (255 - 0x4d) * a])))
                r.Steps("fill", steps)
    scene.TextStack(root, 30, 290, [(t0 + k * dt, t0 + (k + 1) * dt if k < len(alphas) - 1 else 20, "アルファ %.1f" % a) for k, a in enumerate(alphas)], size=22, fill=INK)
    scene.TextStack(root, 30, 330, [(t0, 20, "左:しきい値 0.5 を境に、全部出る / 全部消える（半透明にならない）")], size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 30, 354, [(t0, 20, "中:アルファが高いほど、出る画素が増える（密度 ＝ アルファ）。縁がざらざらする")], size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 30, 378, [(t0, 20, "右:フレームごとにしきい値を変えて平均すると、アルファどおりの色になる（TAA）")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "アルファ 0.1 → 0.9")
    return dict(name=name, page=G + "translucency/alpha-test/hashed-alpha.md", before="## ハッシュド アルファ", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def WboitLayers():
    name = "wboit-layers"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="WBOIT:ソートなしの重み付き平均は、正しいブレンドに近い")
    root = scene.root
    layers = [("#e5484d", 0.5, 0.2), ("#2ea043", 0.5, 0.5), ("#2563eb", 0.5, 0.8)]
    bg = (255, 255, 255)

    def Hx(c):
        c = c.lstrip("#")
        return [int(c[i:i + 2], 16) for i in (0, 2, 4)]

    def Exact(n):
        col = list(bg)
        for k in range(n - 1, -1, -1):  # 奥から手前へ(z 大 → 小)
            lc, a, z = layers[k]
            c = Hx(lc)
            col = [c[i] * a + col[i] * (1 - a) for i in range(3)]
        return col

    def Weight(z):
        return max(0.01, min(3000.0, 10.0 / (1e-5 + (z / 5.0) ** 3 + (z / 200.0) ** 6)))

    def Wb(n):
        acc = [0.0, 0.0, 0.0]
        wsum = 0.0
        rev = 1.0
        for k in range(n):
            lc, a, z = layers[k]
            c = Hx(lc)
            w = a * Weight(z + 0.1)
            for i in range(3):
                acc[i] += c[i] * w
            wsum += w
            rev *= (1 - a)
        avg = [acc[i] / wsum for i in range(3)]
        return [avg[i] * (1 - rev) + bg[i] * rev for i in range(3)]

    for k, (lc, a, z) in enumerate(layers):
        t = 1.0 + k * 3.0
        g = root.add("g", opacity=0)
        g.Show(t)
        y = 100 + (len(layers) - 1 - k) * 0 + k * 0
        g.add("rect", x=60 + k * 60, y=100 + k * 40, width=200, height=90, fill=lc, fill_opacity=0.5, stroke=lc, stroke_width=2)
        scene.Text(g, 60 + k * 60 + 8, 100 + k * 40 + 20, "層 %d（α 0.5、深さ %.1f）" % (k + 1, z), size=12, fill=INK)
    res_x = 450
    scene.Text(root, res_x, 90, "正しい結果（ソート）", size=13, fill=GRAY)
    scene.Text(root, res_x + 170, 90, "WBOIT（順序なし）", size=13, fill=GRAY)
    ex = root.add("rect", x=res_x, y=100, width=140, height=80, fill=Hex(bg), stroke="#94a3b8", stroke_width=2)
    wb = root.add("rect", x=res_x + 170, y=100, width=140, height=80, fill=Hex(bg), stroke="#94a3b8", stroke_width=2)
    ex.Steps("fill", [(1.0 + k * 3.0, Hex(Exact(k + 1))) for k in range(3)])
    wb.Steps("fill", [(1.0 + k * 3.0, Hex(Wb(k + 1))) for k in range(3)])
    errs = [sum(abs(a - b) for a, b in zip(Exact(k + 1), Wb(k + 1))) / 3 for k in range(3)]
    scene.TextStack(root, res_x, 220, [(1.0 + k * 3.0, 1.0 + (k + 1) * 3.0 if k < 2 else 20, "層 %d まで重ねた結果の差:%.0f / 255" % (k + 1, errs[k])) for k in range(3)], size=14, fill=INK)
    scene.TextStack(root, res_x, 250, [(1.0, 20, "手前ほど重みを大きく（深さの関数）して平均する")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 60, 340, "式:色 = Σ(色 × α × w(z)) / Σ(α × w(z))、残りの透過率 = Π(1 − α)。", size=13, fill=INK, weight=500)
    scene.Text(root, 60, 366, "色は少しずれるが、1 パス・ソートなしで、ほとんどの半透明で十分に見える（重なりが多いほど、誤差は増える）。", size=12, fill=GRAY, weight=500)
    scene.Note(1.0, name, "層を 1 枚ずつ追加")
    return dict(name=name, page=G + "translucency/oit/wboit.md", before="### 考え方", scene=scene, size=(780, 420), times=[2.0, 4.5, 8.0, 11.5])


def DepthPeeling():
    name = "depth-peeling-passes"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="Depth Peeling:手前の層から、1 パスに 1 枚ずつ剥いでいく")
    root = scene.root
    layers = [("#e5484d", 80), ("#2ea043", 150), ("#2563eb", 220), ("#e5aa28", 290)]
    root.add("line", x1=60, y1=60, x2=60, y2=340, stroke=INK, stroke_width=2)
    scene.Text(root, 60, 52, "視点（上から見下ろす）", size=11, fill=GRAY)
    for k, (col, y) in enumerate(layers):
        root.add("rect", x=140, y=y, width=300, height=22, fill=col, fill_opacity=0.35, stroke=col, stroke_width=2)
        scene.Text(root, 150, y + 16, "層 %d" % (k + 1), size=12, fill=INK)
    ray = root.add("line", x1=90, y1=60, x2=90, y2=340, stroke=GRAY, stroke_width=2, stroke_dasharray="4 4")
    t0, dt = 1.2, 2.8
    for k, (col, y) in enumerate(layers):
        t = t0 + k * dt
        g = root.add("g", opacity=0)
        g.Show(t, t + dt)
        g.add("circle", cx=90, cy=y + 11, r=8, fill=col, stroke="#ffffff", stroke_width=2)
        g.add("line", x1=60, y1=y + 11, x2=140, y2=y + 11, stroke=col, stroke_width=2.5)
        # しきい値線(これより奥だけ描く)
        if k > 0:
            g.add("line", x1=60, y1=layers[k - 1][1] + 24, x2=460, y2=layers[k - 1][1] + 24, stroke=RED, stroke_width=2, stroke_dasharray="6 3")
    scene.TextStack(root, 40, 380, [(t0 + k * dt, t0 + (k + 1) * dt, "パス %d:しきい値より奥で、最も手前の層（層 %d）を取り出す" % (k + 1, k + 1)) for k in range(4)], size=15, fill=INK)
    # 右:各パスの結果を、奥から重ねる
    scene.Text(root, 520, 80, "各パスの結果（層ごとの画像）", size=13, fill=GRAY)
    for k, (col, y) in enumerate(layers):
        t = t0 + k * dt + dt * 0.8
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=520, y=96 + k * 56, width=120, height=44, fill=col, fill_opacity=0.5, stroke=col, stroke_width=2)
        scene.Text(g, 580, 96 + k * 56 + 27, "層 %d の画像" % (k + 1), size=12, fill=INK, anchor="middle")
    final = root.add("g", opacity=0)
    final.Show(t0 + 4 * dt)
    Arrow(scene, final, 650, 190, 700, 190, color=INK)
    final.add("rect", x=700, y=150, width=60, height=80, fill="#9ca3af", stroke=INK, stroke_width=2)
    scene.Text(final, 730, 246, "奥から合成", size=11, fill=INK, anchor="middle")
    scene.TextStack(root, 40, 404, [(t0 + 4 * dt, 20, "層の数だけパスが必要（4 層なら 4 パス）。正確だが、重い。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "層を 1 枚ずつ剥ぐ")
    return dict(name=name, page=G + "translucency/oit/depth-peeling.md", before="## Depth Peeling", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 12.0])


def SnellLaw():
    name = "snell-refraction"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="スネルの法則:境界で光が曲がる（空気 → ガラス、ガラス → 空気）")
    root = scene.root
    n1, n2 = 1.0, 1.5
    panels = [(190, "空気（n = 1.0）→ ガラス（n = 1.5）", False), (590, "ガラス → 空気:一定の角度から、全反射", True)]
    for cx, title, rev in panels:
        scene.Text(root, cx, 70, title, size=13, fill=INK, anchor="middle")
        root.add("rect", x=cx - 170, y=100, width=340, height=130, fill="#f8fafc" if not rev else "#e0f2fe")
        root.add("rect", x=cx - 170, y=230, width=340, height=130, fill="#e0f2fe" if not rev else "#f8fafc")
        root.add("line", x1=cx - 170, y1=230, x2=cx + 170, y2=230, stroke=INK, stroke_width=3)
        root.add("line", x1=cx, y1=100, x2=cx, y2=360, stroke=LIGHT, stroke_width=2, stroke_dasharray="4 4")
        a_n, b_n = (n1, n2) if not rev else (n2, n1)
        inc = root.add("line", x1=cx, y1=230, x2=cx, y2=100, stroke=AMBER, stroke_width=4)
        trans = root.add("line", x1=cx, y1=230, x2=cx, y2=360, stroke=BLUE, stroke_width=4)
        refl = root.add("line", x1=cx, y1=230, x2=cx, y2=100, stroke=RED, stroke_width=3, opacity=0)
        steps = 26
        t0, t1 = 0.8, 12.0
        prev = None
        for i in range(steps + 1):
            f = i / steps
            th1 = math.radians(80 * f)
            s2 = a_n * math.sin(th1) / b_n
            tir = s2 > 1.0
            L = 130
            ix, iy = cx - L * math.sin(th1), 230 - L * math.cos(th1)
            if tir:
                th2 = th1
                tx, ty = cx, 230
                rx, ry = cx + L * math.sin(th1), 230 - L * math.cos(th1)
            else:
                th2 = math.asin(s2)
                tx, ty = cx + L * math.sin(th2), 230 + L * math.cos(th2)
                rx, ry = cx + L * 0.35 * math.sin(th1), 230 - L * 0.35 * math.cos(th1)
            t = Lerp(t0, t1, f)
            vals = [(inc, "x2", R(ix)), (inc, "y2", R(iy)), (trans, "x2", R(tx)), (trans, "y2", R(ty)), (refl, "x2", R(rx)), (refl, "y2", R(ry)), (refl, "opacity", 1 if tir else 0.25)]
            for node, attr, v in vals:
                if i == 0:
                    node.Set(t, attr, v)
                else:
                    node.Ramp(prev, t, attr, v)
            prev = t
        LiveText(scene, root, cx - 160, 390, t0, t1, steps, lambda i, f, a_n=a_n, b_n=b_n: ("入射 %d° → 屈折 %s" % (round(80 * f), ("%d°" % round(math.degrees(math.asin(a_n * math.sin(math.radians(80 * f)) / b_n)))) if a_n * math.sin(math.radians(80 * f)) / b_n <= 1 else "なし（全反射）")), size=14, fill=INK)
    scene.Text(root, 40, 412, "n₁ sin θ₁ = n₂ sin θ₂。ガラス → 空気は、臨界角（約 42°）を超えると、全反射（赤）になる。", size=12, weight=500, fill=GRAY)
    scene.Note(0.8, name, "入射角 0 → 80°")
    return dict(name=name, page=G + "translucency/refraction/index.md", before="## 屈折の原理", scene=scene, size=(780, 420), times=[1.5, 5.0, 8.5, 11.5])


def BeerThickness():
    name = "beer-thickness"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ビア＝ランバート:光が通る厚みが増えると、色が指数で濃くなる")
    root = scene.root
    sigma = (0.9, 0.35, 0.12)  # 赤が吸われやすい(水色のガラス)
    x0, x1, base, top = 60, 480, 300, 120
    # 楔形のガラス:左が薄く、右が厚い
    n = 42
    for k in range(n):
        f = (k + 0.5) / n
        d = f * 4.0
        col = [255 * math.exp(-s * d) for s in sigma]
        h = 20 + f * (base - top - 20)
        root.add("rect", x=x0 + k * (x1 - x0) / n, y=base - h, width=(x1 - x0) / n + 0.6, height=h, fill=Hex(col))
    root.add("polygon", points="%s,%s %s,%s %s,%s" % (x0, base, x1, base, x1, top), fill="none", stroke=INK, stroke_width=2)
    scene.Text(root, x0, base + 20, "薄い", size=12, fill=GRAY)
    scene.Text(root, x1, base + 20, "厚い", size=12, fill=GRAY, anchor="end")
    ax = Axes(scene, root, 540, 100, 200, 160, 4.0, 1.0, "厚み", "透過率")
    for c, col in enumerate((RED, GREEN, BLUE)):
        ax.Curve(lambda d, c=c: math.exp(-sigma[c] * d), col, 3, n=40)
    ray = root.add("line", x1=x0, y1=60, x2=x0, y2=base + 4, stroke=AMBER, stroke_width=3)
    probe = root.add("circle", cx=ax.X(0), cy=ax.Y(1), r=5, fill=INK)
    out = root.add("rect", x=540, y=300, width=200, height=36, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
    steps = 28
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(steps + 1):
        f = i / steps
        d = f * 4.0
        t = Lerp(t0, t1, f)
        x = x0 + f * (x1 - x0)
        col = Hex([255 * math.exp(-s * d) for s in sigma])
        vals = [(ray, "x1", R(x)), (ray, "x2", R(x)), (probe, "cx", ax.X(d)), (probe, "cy", ax.Y(math.exp(-sigma[0] * d))), (out, "fill", col)]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    scene.Text(root, 640, 290, "通り抜けた後の色", size=12, fill=GRAY, anchor="middle")
    LiveText(scene, root, 60, 352, t0, t1, steps, lambda i, f: "厚み %.1f:赤の透過率 %.2f、緑 %.2f、青 %.2f" % (4 * f, math.exp(-sigma[0] * 4 * f), math.exp(-sigma[1] * 4 * f), math.exp(-sigma[2] * 4 * f)), size=14, fill=INK)
    scene.Text(root, 60, 380, "透過率 = exp(−吸収係数 × 厚み)。色ごとに吸収が違うので、厚いほど色が付く（赤から先に消える ＝ 青緑）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "厚みを 0 → 4")
    return dict(name=name, page=G + "translucency/refraction/thickness-color.md", before="## 厚みと色", scene=scene, size=(780, 400), times=[1.5, 4.0, 7.0, 9.8])


FIGS = [SsrHizSteps, PlanarMirror, RoughnessLobe, SsrEdgeFade, ParallaxBox, PrefilterMips, RtHybridFlow, PremultFringe, BlendModes, SoftParticles, A2cCoverage, HashedAlpha, WboitLayers, DepthPeeling, SnellLaw, BeerThickness]
