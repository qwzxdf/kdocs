import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402

G = "graphics/"
BEFORE = "## よくあるミス"


def XLabel(scene, ax, text):
    scene.Text(scene.root, ax.x + ax.w, ax.y + ax.h + 36, text, size=12, weight=500, fill=GRAY, anchor="end")


def Morph(name, page, title, xlabel, ylabel, xmax, ymax, fns, caps, color=AMBER, ticks=None, ref=None, n=80, xmin=0.0, ymin=0.0):
    """パラメータだけ違う曲線を、順に変形させる。"""
    scene = NewScene(name, 780, 420, duration=1.2 + 2.6 * len(fns) + 0.6, hold=1.5, title=title)
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, xmax, ymax, ylabel=ylabel, xmin=xmin, ymin=ymin)
    XLabel(scene, ax, xlabel)
    for v in ticks or []:
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, ("%g" % v), size=11, weight=500, fill=GRAY, anchor="middle")
    if ref:
        ax.Curve(ref[0], ref[1], width=3, n=n, dash="6 5")
        scene.Text(root, ax.X(ref[3]), ax.Y(ref[0](ref[3])) - 10, ref[2], size=12, weight=500, fill=ref[1])
    line = root.add("path", d="M0,0", fill="none", stroke=color, stroke_width=4)
    prev = 0.0
    for k, fn in enumerate(fns):
        t = 1.2 + k * 2.6
        d = ax.D(fn, n=n)
        if k == 0:
            line.Set(0, "d", d)
        else:
            line.Ramp(prev, t, "d", d)
        prev = t + 0.9
        line.Set(prev, "d", d)
    scene.TextStack(root, 390, 392, [(0.0 if i == 0 else 1.0 + 2.6 * i - 0.2, 1.0 + 2.6 * (i + 1) - 0.2 if i < len(caps) - 1 else 99, c) for i, c in enumerate(caps)], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "パラメータを順に変える")
    times = [1.0 + 2.6 * k + 1.2 for k in range(len(fns))][:4]
    return dict(name=name, page=G + page, before=BEFORE, scene=scene, size=(780, 420), times=times)


def Jacobian():
    ls = [0.5, 1.0, 1.5, 2.0]
    fns = [lambda x, l=l: 1 - l * math.cos(x) for l in ls]
    caps = ["λ = 0.5: J は常に正。波は折り返さない", "λ = 1.0: J がちょうど 0 に触れる。波頭が尖る", "λ = 1.5: J が 0 を下回る。波頭が折り返す → 泡が出る", "λ = 2.0: 折り返す範囲がさらに広がる。泡が増える"]
    assert [round(1 - l, 2) for l in ls] == [0.5, 0.0, -0.5, -1.0]
    return Morph("jacobian-fold", "water/shore-foam/crest-jacobian.md", "ヤコビアン J = 1 − λ·cos x: 0 を下回る所が、波の折り返し(泡)", "波の位置 x (ラジアン)", "J", 2 * math.pi, 3.2, fns, caps, color=RED, ref=(lambda x: 0.0, GRAY, "J = 0（これ以下で泡）", 2.6), ymin=-1.1)


def HeightPow():
    ps = [1.0, 2.0, 3.0]
    fns = [lambda x, p=p: ((x + 1) / 2) ** p for p in ps]
    caps = ["指数 1: ノイズの値が、そのまま高さ。全体が丸く均一", "指数 2: 低い所が広く平らになり、山が際立つ", "指数 3: さらに平野が広がり、山は少数の尖った所だけ"]
    return Morph("height-pow-curve", "terrain/generation/height-conversion.md", "ノイズ(−1〜1)を高さに直す: ((n+1)/2)^p で平野と山の比率が変わる", "ノイズの値 n", "高さ（0〜1）", 1.0, 1.05, fns, caps, color=GREEN, ticks=[-1, -0.5, 0, 0.5, 1], xmin=-1.0)


def TonemapCurves():
    name = "tonemap-aces-curves"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="トーンマップ: 明るさ 0〜8 を、画面に出せる 0〜1 に押し込む")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 8.0, 1.05, ylabel="出力（表示できる明るさ）")
    XLabel(scene, ax, "入力の明るさ（HDR）")
    for v in (0, 2, 4, 6, 8):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    aces = lambda x: (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    rein = lambda x: x / (1 + x)
    lin = lambda x: min(1.0, x)
    ax.Curve(lin, GRAY, width=3, n=100, dash="6 5")
    ax.Curve(rein, BLUE, width=4, n=100)
    ax.Curve(aces, RED, width=4, n=100)
    scene.Text(root, ax.X(4.8), ax.Y(1.0) + 22, "ACES（近似）", size=13, weight=700, fill=RED)
    scene.Text(root, ax.X(4.8), ax.Y(rein(4.8)) + 24, "Reinhard", size=13, weight=700, fill=BLUE)
    scene.Text(root, ax.X(1.6), ax.Y(1.0) - 8, "そのまま（1 で頭打ち）", size=12, weight=500, fill=GRAY)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, aces, 1.0, 10.0, 0.0, 8.0, n=60)
    LiveText(scene, root, 390, 392, 1.0, 10.0, 4, lambda i, f: ["暗い所: ACES は、暗部を少し沈めてコントラストを付ける", "中間: 急に立ち上がる(S 字の中央)", "明るい所: ゆるやかに 1 へ近づく(白飛びしにくい)", "8 でも 1 を超えない。Reinhard は白に届きにくい"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "入力 0 → 8")
    return dict(name=name, page=G + "postprocess/tonemapping/aces.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def NoiseSamples():
    name = "mc-noise-samples"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="ノイズはサンプル数の平方根に反比例: 4 倍の本数で、ノイズは半分")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 10.0, 1.05, ylabel="ノイズの大きさ 1/√N")
    XLabel(scene, ax, "1 ピクセルあたりのサンプル数 N")
    for v in range(0, 11, 2):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(2 ** v), size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda x: 1 / math.sqrt(2 ** x)
    ax.Curve(fn, RED, width=4, n=100)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 10.0, 0.0, 10.0, n=60)
    assert abs(fn(2) - 0.5) < 1e-9 and abs(fn(10) - 1 / 32) < 1e-9
    LiveText(scene, root, 390, 392, 1.0, 10.0, 5, lambda i, f: ["1〜4 本: ノイズ 1 → 0.5", "4〜16 本: 0.5 → 0.25", "16〜64 本: 0.25 → 0.13", "64〜256 本: 0.13 → 0.06", "256〜1024 本: 0.06 → 0.03。ここまで増やしても 1/32"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "N を倍々に")
    return dict(name=name, page=G + "gi/rt-gi/noise.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def Anisotropic():
    name = "aniso-footprint"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="斜めから見ると、1 画素が、地面の細長い楕円を覆う")
    root = scene.root
    angles = [0, 45, 70, 80]
    ratios = [1 / math.cos(math.radians(a)) for a in angles]
    assert [round(r, 1) for r in ratios] == [1.0, 1.4, 2.9, 5.8]
    cx, cy = 390, 185
    root.add("rect", x=cx - 300, y=cy - 150, width=600, height=300, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    e = root.add("ellipse", cx=cx, cy=cy, rx=24, ry=24, fill=AMBER, opacity=0.8, stroke=RED, stroke_width=3)
    e.Set(0, "ry", 24)
    for k in range(1, 4):
        e.Ramp(k * 3.0 - 1.0, k * 3.0, "ry", 24 * ratios[k])
    scene.Text(root, cx - 290, cy - 130, "地面を、真上から見た図（赤い楕円 = 1 画素が覆う範囲）", size=12, weight=500, fill=GRAY)
    caps = [(0.0, 2.8, "視線の角度 0 度（真上）: 円。1 画素 = 正方形の領域"), (2.8, 5.8, "45 度: 縦に 1.4 倍"), (5.8, 8.8, "70 度: 2.9 倍。普通のミップは、長い方に合わせて、ぼやける"), (8.8, 20, "80 度: 5.8 倍。異方性フィルタリングは、細長い範囲を複数のサンプルで平均する")]
    scene.TextStack(root, 390, 385, caps, size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "角度 0 → 80 度")
    return dict(name=name, page=G + "terrain/texturing/anisotropic.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.5, 10.0])


def Stochastic():
    name = "stochastic-alpha"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="確率的透明: アルファを、塗るサンプルの割合に置き換える")
    root = scene.root
    order = [3, 6, 1, 4, 0, 7, 2, 5]
    for r, a in enumerate([0.25, 0.5, 0.75]):
        y = 100 + r * 85
        g = root.add("g", opacity=0)
        cnt = round(a * 8)
        on = set(order[:cnt])
        for i in range(8):
            g.add("rect", x=190 + i * 54, y=y, width=48, height=48, fill=(BLUE if i in on else "#ffffff"), stroke="#94a3b8", stroke_width=1.5)
        scene.Text(g, 170, y + 30, "α = %.2f" % a, size=14, weight=700, fill=INK, anchor="end")
        scene.Text(g, 640, y + 30, "%d / 8" % cnt, size=13, weight=500, fill=GRAY)
        g.Show(1.0 + r * 3.0)
    scene.Text(root, 190, 80, "1 画素の 8 個のサンプル（青 = 描く）", size=13, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 360, [(0.0, 1.0, "半透明の面を、サンプルごとに 描く / 描かない で決める"), (1.0, 4.0, "α = 0.25: 8 個のうち 2 個だけ描く"), (4.0, 7.0, "α = 0.5: 4 個"), (7.0, 20, "α = 0.75: 6 個。平均すると α の割合で塗られる(並べ替え不要、代わりにノイズ)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "α を上げる")
    return dict(name=name, page=G + "translucency/oit/stochastic.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.0, 3.5, 6.5, 9.5])


def Ppll():
    name = "ppll-chain"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="PPLL: 画素ごとに連結リストを作り、最後に深度で並べ替える")
    root = scene.root
    y = 170
    frags = [("F1", 0.7), ("F2", 0.3), ("F3", 0.5)]
    pos_unsorted = {"F1": 560, "F2": 400, "F3": 240}
    pos_sorted = {"F2": 240, "F3": 400, "F1": 560}
    root.add("rect", x=60, y=y, width=90, height=60, fill="#e2e8f0", stroke="#94a3b8", stroke_width=2)
    scene.Text(root, 105, y + 36, "head", size=14, weight=700, fill=INK, anchor="middle")
    for k, (nm, z) in enumerate(frags):
        t = 1.5 + k * 2.2
        g = root.add("g", opacity=0)
        ux, sx = pos_unsorted[nm], pos_sorted[nm]
        r_ = g.add("rect", x=ux, y=y, width=90, height=60, fill=[BLUE, GREEN, AMBER][k], opacity=0.9)
        t1 = scene.Text(g, ux + 45, y + 26, nm, size=15, weight=700, fill="#ffffff", anchor="middle")
        t2 = scene.Text(g, ux + 45, y + 46, "z = %.1f" % z, size=12, weight=500, fill="#ffffff", anchor="middle")
        g.Show(t)
        r_.Ramp(8.0, 9.5, "x", sx)
        t1.Ramp(8.0, 9.5, "x", sx + 45)
        t2.Ramp(8.0, 9.5, "x", sx + 45)
    scene.Text(root, 390, 110, "到着順: F1 → F2 → F3（新しいものが、リストの先頭になる）", size=13, weight=500, fill=GRAY, anchor="middle")
    scene.TextStack(root, 390, 340, [(0.0, 1.5, "最初、リストは空"), (1.5, 3.7, "F1 が到着: head が F1 を指す"), (3.7, 5.9, "F2 が到着: head → F2 → F1"), (5.9, 8.0, "F3 が到着: head → F3 → F2 → F1。深度はバラバラ"), (8.0, 11.0, "深度の小さい順に並べ替え: F2(0.3) → F3(0.5) → F1(0.7)"), (11.0, 20, "奥から手前へ、順に混ぜる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "F1 → F2 → F3 → 並べ替え")
    return dict(name=name, page=G + "translucency/oit/ppll.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 10.5])


def Bilinear():
    name = "bilinear-height"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="好きな位置の高さ: 周りの 4 点を、距離で混ぜる(バイリニア補間)")
    root = scene.root
    h00, h10, h01, h11 = 2.0, 6.0, 4.0, 8.0
    x0, y0, s = 270, 90, 220
    root.add("rect", x=x0, y=y0, width=s, height=s, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    for (u, v, h) in [(0, 0, h00), (1, 0, h10), (0, 1, h01), (1, 1, h11)]:
        px, py = x0 + u * s, y0 + (1 - v) * s
        root.add("circle", cx=px, cy=py, r=5, fill=GRAY)
        scene.Text(root, px + (-12 if u == 0 else 12), py + (22 if v == 0 else -10), "h=%g" % h, size=13, weight=700, fill=GRAY, anchor="end" if u == 0 else "start")
    pts = [(0.2, 0.2), (0.5, 0.5), (0.8, 0.3), (0.25, 0.75)]
    f = lambda u, v: h00 * (1 - u) * (1 - v) + h10 * u * (1 - v) + h01 * (1 - u) * v + h11 * u * v
    assert abs(f(0.5, 0.5) - 5.0) < 1e-9
    dot = root.add("circle", cx=x0 + pts[0][0] * s, cy=y0 + (1 - pts[0][1]) * s, r=9, fill=RED)
    items = []
    for k, (u, v) in enumerate(pts):
        t = 1.0 + k * 3.0
        if k > 0:
            dot.Ramp(t - 1.2, t, "cx", x0 + u * s)
            dot.Ramp(t - 1.2, t, "cy", y0 + (1 - v) * s)
        items.append((t if k else 0.0, t + 3.0 if k < 3 else 99, "u = %.2f, v = %.2f → h = %.2f" % (u, v, f(u, v))))
    scene.TextStack(root, 390, 350, items, size=15, fill=INK, anchor="middle")
    scene.Text(root, 390, 385, "h = h00(1−u)(1−v) + h10·u(1−v) + h01(1−u)v + h11·u·v", size=13, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "点を動かす")
    return dict(name=name, page=G + "terrain/heightmap-mesh/height-query.md", before=BEFORE, scene=scene, size=(780, 440), times=[0.5, 3.5, 6.5, 9.5])


def Instancing():
    name = "instancing-calls"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="同じ草を 24 本描く: 1 本ずつ命令を出す vs 1 回でまとめて描く")
    root = scene.root
    for side, (x0, lab, col) in enumerate([(70, "個別に描く", RED), (430, "インスタンシング", GREEN)]):
        scene.Text(root, x0, 90, lab, size=16, weight=700, fill=col)
        for i in range(24):
            cx, cy = x0 + (i % 6) * 50, 130 + (i // 6) * 50
            sq = root.add("rect", x=cx, y=cy, width=40, height=40, fill=col, opacity=0)
            sq.Show(1.0 + i * 0.28 if side == 0 else 2.0)
    scene.Counter(root, 70, 365, [(1.0 + i * 0.28, i + 1) for i in range(24)], size=26, fill=RED)
    scene.Text(root, 130, 365, "回の描画命令", size=14, weight=500, fill=GRAY)
    one = scene.Text(root, 430, 365, "1", size=26, weight=700, fill=GREEN, opacity=0)
    one.Show(2.0)
    scene.Text(root, 450, 365, "回の描画命令（位置の配列を渡す）", size=14, weight=500, fill=GRAY)
    scene.Note(1.0, name, "命令の数を比べる")
    return dict(name=name, page=G + "terrain/vegetation/instancing.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.0, 5.0, 8.5])


FIGS = [Jacobian, HeightPow, TonemapCurves, NoiseSamples, Anisotropic, Stochastic, Ppll, Bilinear, Instancing]
