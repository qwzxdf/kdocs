import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Hex, Lerp, LiveText, NewScene, R, RampFill, Sweep)  # noqa: E402

G = "graphics/skin-hair/"

# d'Eon & Luebke (GPU Gems 3) の 6 ガウス: (分散 mm^2, 重み R, G, B)
GAUSS = [
    (0.0064, (0.233, 0.455, 0.649)),
    (0.0484, (0.100, 0.336, 0.344)),
    (0.187, (0.118, 0.198, 0.0)),
    (0.567, (0.113, 0.007, 0.007)),
    (1.99, (0.358, 0.004, 0.0)),
    (7.41, (0.078, 0.0, 0.0)),
]
CH = [RED, GREEN, BLUE]
CHN = ["赤", "緑", "青"]


def Srgb(r, g, b):
    def f(v):
        v = max(0.0, min(1.0, v))
        return 255 * v ** (1 / 2.2)
    return Hex([f(r), f(g), f(b)])


def PathD(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


def SssSpread():
    name = "sss-spread"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="光が入った点から、どこまでに何 % が出てくるか")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 260, 6.0, 1.0, ylabel="出てきた光の割合（累積）")
    scene.Text(root, ax.x + ax.w, ax.y + ax.h + 38, "入った点からの距離 (mm)", size=12, weight=500, fill=GRAY, anchor="end")
    for v in (1, 2, 3, 4, 5):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    for c in range(3):
        fn = lambda r, c=c: sum(w[c] * (1 - math.exp(-r * r / (2 * v))) for v, w in GAUSS)
        p = ax.Curve(fn, CH[c], width=4, n=80, opacity=0)
        t0 = 1.0 + (2 - c) * 2.5
        p.Show(t0)
        label = scene.Text(root, ax.X(5.9), ax.y + 24 + c * 18, CHN[c], size=13, fill=CH[c], anchor="end", opacity=0)
        label.Show(t0)
    scene.TextStack(root, 390, 372, [(0.0, 1.0, "光が当たった点から、肌の内側に広がる"), (1.0, 3.5, "青: 0.5 mm ほどで、ほぼ出きる（狭い）"), (3.5, 6.0, "緑: 1〜2 mm まで広がる"), (6.0, 20, "赤: 数 mm まで届く。だから、影の縁が赤く染まる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "青 → 緑 → 赤の順に線を引く")
    return dict(name=name, page=G + "skin/subsurface-theory.md", before="## 拡散近似", scene=scene, size=(780, 400), times=[1.5, 4.0, 7.0, 11.0])


def GaussianSum():
    name = "gaussian-sum"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="6 つのガウスを足して、赤の拡散プロファイルを作る")
    root = scene.root
    lo, hi = -1.5, 0.8
    ax = Axes(scene, root, 70, 70, 640, 280, hi, 0.34, xmin=lo, ymin=0.0, ylabel="その距離から出る光の量")
    scene.Text(root, ax.x + ax.w, ax.y + ax.h + 38, "入った点からの距離（対数目盛）", size=12, weight=500, fill=GRAY, anchor="end")
    for val, lab in ((0.03, "0.03"), (0.1, "0.1"), (0.3, "0.3"), (1, "1 mm"), (3, "3 mm")):
        scene.Text(root, ax.X(math.log10(val)), ax.y + ax.h + 18, lab, size=11, weight=500, fill=GRAY, anchor="middle")

    def Part(i):
        v, w = GAUSS[i]
        return lambda lg: w[0] * (10 ** (2 * lg)) / v * math.exp(-(10 ** (2 * lg)) / (2 * v))

    cols = [PURPLE, BLUE, GREEN, AMBER, "#0e9aa7", RED]
    for i in range(6):
        p = ax.Curve(Part(i), cols[i], width=2.5, n=90, opacity=0)
        t0 = 0.8 + i * 1.5
        p.Show(t0, t0 + 3.2 if i < 5 else None)
        scene.Text(root, 90, 100 + i * 17, "ガウス %d  分散 %s mm²  重み %.3f" % (i + 1, GAUSS[i][0], GAUSS[i][1][0]), size=11, weight=500, fill=cols[i], opacity=0).Show(t0)
    cum = []
    total = ax.Curve(lambda lg: sum(Part(i)(lg) for i in range(6)), INK, width=4.5, n=90, opacity=0)
    total.Show(10.0)
    scene.TextStack(root, 390, 405, [(0.0, 0.8, "赤の拡散プロファイルを、ガウスの和で近似する"), (0.8, 10.0, "分散の小さいガウスから順に足す（細い芯 → 広い裾）"), (10.0, 20, "合計（黒）が、赤のプロファイル。裾が長い")], size=14, fill=INK, anchor="middle")
    scene.Note(0.8, name, "ガウスを 1 つずつ表示")
    return dict(name=name, page=G + "skin/diffusion-profile.md", before="## ガウスの和による近似", scene=scene, size=(780, 440), times=[2.0, 6.0, 10.5, 14.0])


def SssBlur():
    name = "sss-blur"
    scene = NewScene(name, 780, 440, duration=11.0, hold=1.5, title="影の縁を、色ごとの幅でぼかすと、縁が赤くなる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 220, 3.0, 1.05, xmin=-3.0, ylabel="明るさ")
    scene.Text(root, ax.x + ax.w, ax.y + ax.h + 18, "影の縁からの距離 (mm)　左: 光　右: 影", size=12, weight=500, fill=GRAY, anchor="end")

    def Edge(c):
        return lambda x: sum(w[c] * 0.5 * math.erfc(x / math.sqrt(2 * v)) for v, w in GAUSS)

    step = ax.Curve(lambda x: 1.0 if x < 0 else 0.0, INK, width=3, n=120, dash="6 4")
    scene.Text(root, ax.X(0.15), ax.Y(0.9), "点線: ぼかす前", size=12, fill=INK)
    for c in (2, 1, 0):
        p = ax.Curve(Edge(c), CH[c], width=4, n=90, opacity=0)
        p.Show(1.5 + (2 - c) * 2.0)
    # 色の帯
    n = 48
    band = root.add("g", opacity=0)
    for i in range(n):
        x = -3.0 + 6.0 * (i + 0.5) / n
        band.add("rect", x=R(ax.X(-3.0 + 6.0 * i / n)), y=320, width=R(640 / n + 0.6), height=34, fill=Srgb(Edge(0)(x), Edge(1)(x), Edge(2)(x)))
    band.Show(8.0)
    scene.Text(root, 70, 372, "見た目の色（拡散光）", size=12, weight=500, fill=GRAY)
    root.add("rect", x=70, y=320, width=640, height=34, fill="none", stroke="#94a3b8", stroke_width=1.5)
    scene.TextStack(root, 390, 420, [(0.0, 1.5, "SSS のぼかし: 影の縁は、ぼけて広がる"), (1.5, 5.5, "青と緑は狭く、赤だけが影の中まで染み出す"), (5.5, 8.0, "赤い光ほど遠くまで届く"), (8.0, 20, "結果: 影の縁が、赤みを帯びる（下の帯）")], size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "青 → 緑 → 赤の順")
    return dict(name=name, page=G + "skin/screen-space-sss.md", before="## カーネルの作り方", scene=scene, size=(780, 440), times=[2.0, 5.0, 8.0, 11.0])


def PreIntegrated():
    name = "preint-lut"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="曲率が大きいほど、影側に赤い光が回り込む")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 260, 1.0, 1.0, xmin=-1.0, xlabel="N·L（−1: 真裏 〜 1: 正面）", ylabel="拡散光")
    lam = ax.Curve(lambda x: max(0.0, x), "#94a3b8", width=3, n=80, dash="6 4")
    scene.Text(root, ax.X(0.55), ax.Y(0.45), "普通のランバート", size=12, fill=GRAY)

    def Diffuse(c, nl, rad):
        th = math.acos(max(-1.0, min(1.0, nl)))
        num = den = 0.0
        steps = 120
        for i in range(steps):
            x = -math.pi + 2 * math.pi * (i + 0.5) / steps
            d = 2 * rad * math.sin(abs(x) / 2)
            prof = sum(w[c] * math.exp(-d * d / (2 * v)) / (2 * math.pi * v) for v, w in GAUSS)
            num += max(0.0, math.cos(th + x)) * prof
            den += prof
        return num / den

    rads = [20.0, 8.0, 3.0, 1.2, 0.6, 0.3]
    xs = [-1.0 + 2.0 * i / 60 for i in range(61)]
    curves = {}
    for c in (0, 2):
        node = root.add("path", d="M0,0", fill="none", stroke=CH[c], stroke_width=4)
        curves[c] = node
    prev_t = 0.0
    nf = len(rads)
    for k, rad in enumerate(rads):
        t = 1.5 + k * 1.6
        for c in (0, 2):
            d = PathD([(ax.X(x), ax.Y(Diffuse(c, x, rad))) for x in xs])
            if k == 0:
                curves[c].Set(0, "d", d)
            else:
                curves[c].Ramp(prev_t, t, "d", d)
        prev_t = t
    LiveText(scene, root, 390, 405, 1.5, 1.5 + (nf - 1) * 1.6 + 0.01, nf - 1, lambda i, f: "球の半径 %.1f mm（%s）" % (rads[i + 1] if False else rads[i], "ほぼ平ら" if i < 2 else "細く丸い") + "  赤: 影側へ回り込む", size=14, fill=INK, anchor="middle")
    scene.Text(root, 700, 100, "赤", size=14, fill=RED, anchor="end")
    scene.Text(root, 700, 120, "青", size=14, fill=BLUE, anchor="end")
    scene.Note(1.5, name, "半径を小さくしていく")
    return dict(name=name, page=G + "skin/pre-integrated.md", before="## LUT の作り方", scene=scene, size=(780, 440), times=[1.5, 4.7, 8.0, 11.0])


def ThinTranslucency():
    name = "thin-transmit"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="肌を通り抜ける光は、厚くなるほど赤だけが残る")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 400, 250, 3.0, 1.0, xlabel="厚み s (mm)", ylabel="透過率 T(s)")
    for c in range(3):
        ax.Curve(lambda s, c=c: sum(w[c] * math.exp(-s * s / v) for v, w in GAUSS), CH[c], width=3.5, n=80)
    mark = root.add("line", x1=ax.X(0), y1=ax.y, x2=ax.X(0), y2=ax.y + ax.h, stroke=INK, stroke_width=2)
    prev = None
    n = 30
    for i in range(n + 1):
        s = 3.0 * i / n
        t = 1.0 + 8.0 * i / n
        if i == 0:
            mark.Set(t, "x1", ax.X(s))
            mark.Set(t, "x2", ax.X(s))
        else:
            mark.Ramp(prev, t, "x1", ax.X(s))
            mark.Ramp(prev, t, "x2", ax.X(s))
        prev = t
    swatch = root.add("rect", x=520, y=110, width=190, height=130, fill=Srgb(1, 1, 1), stroke="#94a3b8", stroke_width=1.5, rx=6)
    prev = None
    for i in range(n + 1):
        s = 3.0 * i / n
        t = 1.0 + 8.0 * i / n
        tv = [sum(w[c] * math.exp(-s * s / v) for v, w in GAUSS) for c in range(3)]
        mx = max(max(tv), 1e-6)
        col = Srgb(*[0.15 + 0.85 * x / mx for x in tv])
        if i == 0:
            swatch.Set(t, "fill", col)
        else:
            swatch.Ramp(prev, t, "fill", col)
        prev = t
    scene.Text(root, 615, 100, "透けて見える光の色（明るさは揃えて表示）", size=13, fill=GRAY, anchor="middle")
    LiveText(scene, root, 615, 270, 1.0, 9.0, 4, lambda i, f: ["薄い（耳たぶ）: ほぼ白く透ける", "少し厚い: 橙に", "さらに厚い: 赤に", "厚い: 光はほぼ届かない（赤だけ）"][i], size=13, fill=INK, anchor="middle")
    scene.Note(1.0, name, "厚み 0 → 6 mm")
    return dict(name=name, page=G + "skin/thin-translucency.md", before="## 厚みから透過光へ", scene=scene, size=(780, 420), times=[1.2, 4.0, 6.5, 9.5])


def SkinSpecular():
    name = "skin-specular"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="肌の鏡面反射: 斜めほど強く、芯と裾の 2 つのローブ")
    root = scene.root
    a1 = Axes(scene, root, 60, 80, 300, 230, 90.0, 1.0, xlabel="見る角度（法線から °）", ylabel="反射率 F")
    f0 = 0.028
    a1.Curve(lambda th: f0 + (1 - f0) * (1 - math.cos(math.radians(th))) ** 5, RED, width=4, n=90)
    dot = root.add("circle", cx=a1.X(0), cy=a1.Y(f0), r=6, fill=INK)
    Sweep(dot, a1, lambda th: f0 + (1 - f0) * (1 - math.cos(math.radians(th))) ** 5, 1.0, 6.0, 0.0, 89.0, n=30)
    scene.Text(root, 60, 345, "正面は約 2.8 %。斜めで急に強くなる", size=12, weight=500, fill=GRAY)
    a2 = Axes(scene, root, 430, 80, 290, 230, 40.0, 1.0, xlabel="ハーフベクトルの角度 (°)", ylabel="ハイライトの強さ（正規化）")

    def Lobe(m):
        return lambda deg: math.exp(-(math.tan(math.radians(deg)) ** 2) / (m * m))

    narrow = a2.Curve(lambda d: 0.55 * Lobe(0.18)(d), BLUE, width=3, n=80, opacity=0)
    wide = a2.Curve(lambda d: 0.45 * Lobe(0.55)(d), GREEN, width=3, n=80, opacity=0)
    both = a2.Curve(lambda d: 0.55 * Lobe(0.18)(d) + 0.45 * Lobe(0.55)(d), RED, width=4.5, n=80, opacity=0)
    narrow.Show(6.5)
    wide.Show(8.0)
    both.Show(9.5)
    scene.Text(root, 430, 345, "青: 皮脂（鋭い） 緑: 凹凸（広い） 赤: 合計", size=12, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 395, [(0.0, 6.5, "フレネル: 輪郭が白く光る理由"), (6.5, 9.5, "鋭いローブと広いローブを足す"), (9.5, 20, "鋭い芯と柔らかい裾。肌の質感になる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "角度を 0 → 90°、ローブを 2 つ足す")
    return dict(name=name, page=G + "skin/specular.md", before="## 粗さと分布", scene=scene, size=(780, 420), times=[2.0, 5.5, 8.5, 11.0])


def EyeRefraction():
    name = "eye-refraction"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="角膜で屈折するので、虹彩は、実際の位置からずれて見える")
    root = scene.root
    cy, depth = 150.0, 120.0
    root.add("rect", x=120, y=cy - 40, width=420, height=40, fill="#bae6fd", fill_opacity=0.55)
    root.add("line", x1=120, y1=cy, x2=540, y2=cy, stroke="#0284c7", stroke_width=3)
    root.add("line", x1=120, y1=cy + depth, x2=540, y2=cy + depth, stroke="#7c3aed", stroke_width=4)
    scene.Text(root, 126, cy - 46, "空気", size=12, fill=GRAY)
    scene.Text(root, 126, cy + 22, "角膜・前房（屈折率 1.376）", size=12, fill="#0284c7")
    scene.Text(root, 126, cy + depth + 22, "虹彩の面", size=12, fill=PURPLE)
    px = 330.0
    n = 16
    straight = root.add("line", x1=px, y1=cy, x2=px, y2=cy + depth, stroke="#94a3b8", stroke_width=3, stroke_dasharray="6 4")
    bent = root.add("line", x1=px, y1=cy, x2=px, y2=cy + depth, stroke=RED, stroke_width=4)
    ray_in = root.add("line", x1=px, y1=cy - 90, x2=px, y2=cy, stroke=INK, stroke_width=3)
    d1 = root.add("circle", cx=px, cy=cy + depth, r=7, fill="#94a3b8")
    d2 = root.add("circle", cx=px, cy=cy + depth, r=7, fill=RED)
    prev = None
    for i in range(n + 1):
        f = i / n
        ang = math.radians(Lerp(0, 50, f) if f <= 0.5 * 2 else 50)
        ang = math.radians(50 * min(1.0, f * 1.0))
        t = 1.0 + 7.0 * f
        th_r = math.asin(math.sin(ang) / 1.376)
        xs = px + depth * math.tan(ang)
        xr = px + depth * math.tan(th_r)
        x0 = px - 90 * math.tan(ang)
        vals = [(straight, "x2", xs), (bent, "x2", xr), (ray_in, "x1", x0), (d1, "cx", xs), (d2, "cx", xr)]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, R(v))
            else:
                node.Ramp(prev, t, attr, R(v))
        prev = t
    scene.Text(root, 570, 200, "灰: 屈折なしで見えるはずの位置", size=12, weight=500, fill=GRAY)
    scene.Text(root, 570, 222, "赤: 屈折した、実際に見える位置", size=12, weight=500, fill=RED)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "正面から見ると、ずれない"), (1.0, 8.0, "斜めから見るほど、虹彩の見える位置がずれる"), (8.0, 20, "パララックス マッピングで、この動きを近似できる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "視線の角度 0 → 50°")
    return dict(name=name, page=G + "skin/eyes.md", before="## 角膜の屈折と虹彩の見え方", scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 8.0])


def KajiyaKay():
    name = "kajiya-lobes"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="髪のハイライトは、光の角度に合わせて動く。接線をずらすと 2 本になる")
    root = scene.root
    ax = Axes(scene, root, 70, 150, 640, 170, 180.0, 1.0, xlabel="視線と髪の軸の角度 β (°)", ylabel="ハイライトの強さ")

    def Spec(alpha, delta, p):
        return lambda b: max(0.0, -math.cos(math.radians(alpha + b - delta))) ** p

    alphas = [110, 90, 70, 90]
    xs = [180.0 * i / 90 for i in range(91)]
    n1 = root.add("path", d="M0,0", fill="none", stroke=BLUE, stroke_width=4)
    n2 = root.add("path", d="M0,0", fill="none", stroke=AMBER, stroke_width=4)
    prev = 0.0
    for k, a in enumerate(alphas):
        t = 1.5 + k * 3.0
        d1 = PathD([(ax.X(b), ax.Y(Spec(a, -6, 80)(b))) for b in xs])
        d2 = PathD([(ax.X(b), ax.Y(0.8 * Spec(a, 12, 20)(b))) for b in xs])
        if k == 0:
            n1.Set(0, "d", d1)
            n2.Set(0, "d", d2)
        else:
            n1.Ramp(prev, t, "d", d1)
            n2.Ramp(prev, t, "d", d2)
        prev = t
    scene.Text(root, 80, 70, "青: 1 本目（鋭い・白）", size=13, fill=BLUE)
    scene.Text(root, 80, 92, "橙: 2 本目（広い・髪の色）。接線を別にずらして計算", size=13, fill=AMBER)
    scene.TextStack(root, 390, 370, [(0.0, 1.5, "光と髪の軸の角度 α = 110°"), (1.5, 4.5, "α が変わると、ハイライトの位置が動く（α + β ≒ 180°）"), (4.5, 7.5, "α = 90°: 視線が髪に垂直のとき最大"), (7.5, 10.5, "α = 70°"), (10.5, 20, "ずらし量が違うので、2 本のピークが分かれる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "α を 110 → 90 → 70 → 90°")
    return dict(name=name, page=G + "hair/kajiya-kay.md", before="## ハイライトの形", scene=scene, size=(780, 420), times=[1.5, 4.5, 7.5, 11.0])


def MarschnerLobes():
    name = "marschner-lobes"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="R・TT・TRT のハイライトは、キューティクルの傾き α で、少しずつずれる")
    root = scene.root
    ax = Axes(scene, root, 70, 160, 640, 160, 30.0, 1.0, xmin=-30.0, xlabel="縦方向の角度 θ_h (°)", ylabel="強さ")
    beta = 5.0

    def G_(b, a):
        return lambda x: math.exp(-0.5 * ((x - a) / b) ** 2)

    alphas = [0.0, 6.0, 10.0, 6.0]
    xs = [-30.0 + 60.0 * i / 100 for i in range(101)]
    spec = [("R", 1.0, 1.0, 0.8, "#475569"), ("TT", -0.5, 0.5, 0.9, BLUE), ("TRT", -1.5, 2.0, 0.6, RED)]
    nodes = []
    for lab, sh, bw, amp, col in spec:
        nodes.append(root.add("path", d="M0,0", fill="none", stroke=col, stroke_width=4))
    prev = 0.0
    for k, a in enumerate(alphas):
        t = 1.5 + k * 3.0
        for node, (lab, sh, bw, amp, col) in zip(nodes, spec):
            d = PathD([(ax.X(x), ax.Y(amp * G_(beta * bw, a * sh)(x))) for x in xs])
            if k == 0:
                node.Set(0, "d", d)
            else:
                node.Ramp(prev, t, "d", d)
        prev = t
    scene.Text(root, 80, 62, "R: 反射（白）", size=13, fill="#475569")
    scene.Text(root, 80, 84, "TT: 通り抜け（鋭い・逆側へ半分ずれる）", size=13, fill=BLUE)
    scene.Text(root, 80, 106, "TRT: 内部反射（広い・髪の色・逆側へ 1.5 倍ずれる）", size=13, fill=RED)
    scene.TextStack(root, 390, 370, [(0.0, 1.5, "α = 0°: 3 つが同じ位置に重なる"), (1.5, 4.5, "α を傾けると、R と TRT が分かれる"), (4.5, 7.5, "α = 10°: 2 本のハイライトがはっきり"), (7.5, 20, "幅の比は R : TT : TRT = 1 : 1/2 : 2")], size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "α を 0 → 6 → 10 → 6°")
    return dict(name=name, page=G + "hair/marschner.md", before="## 縦方向と横方向", scene=scene, size=(780, 420), times=[1.5, 4.5, 7.5, 11.0])


def DeepOpacity():
    name = "deep-opacity"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="層を「髪の最初の面」から切ると、少ない層で足りる")
    root = scene.root
    top, bot = 90, 330
    for x0, ttl in ((50, "固定の層（Opacity Shadow Maps）"), (410, "髪の面から切る層（Deep Opacity Maps）")):
        root.add("rect", x=x0, y=top, width=320, height=bot - top, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, x0 + 160, top - 10, ttl, size=13, fill=GRAY, anchor="middle")
    scene.Text(root, 56, top - 36, "↓ 光の向き", size=12, weight=500, fill=GRAY)
    xs = list(range(0, 321, 8))
    surf = [150 + 28 * math.sin(x / 50.0) for x in xs]
    thick = 36
    layers = [AMBER, "#f59e0b", "#d97706"]
    # 左: 固定の層(水平)
    for i in range(6):
        y = top + 30 + i * 36
        root.add("line", x1=50, y1=y, x2=370, y2=y, stroke=LIGHT, stroke_width=1.5)
    # 髪の領域（両方）
    for x0 in (50, 410):
        pts = [(x0 + x, top + s - 90 + 90) for x, s in zip(xs, surf)]
        d = PathD(pts) + " L%s,%s L%s,%s Z" % (R(x0 + 320), R(top + 190), R(x0), R(top + 190))
        root.add("path", d=d, fill="#7c3aed", fill_opacity=0.28)
        root.add("path", d=PathD(pts), fill="none", stroke=PURPLE, stroke_width=3)
    # 右: 髪の面から切る層
    for i, col in enumerate(layers):
        pts = [(410 + x, top + s - 90 + 90 + i * thick) for x, s in zip(xs, surf)]
        root.add("path", d=PathD(pts), fill="none", stroke=col, stroke_width=3)
    scene.Text(root, 60, bot + 20, "層が、髪のない所にも割り当てられて、無駄が出る", size=12, weight=500, fill=GRAY)
    scene.Text(root, 420, bot + 20, "層の始まりが、画素ごとの髪の最初の面。3〜4 層で足りる", size=12, weight=500, fill=GRAY)
    # 透過率バー
    bar = root.add("rect", x=420, y=370, width=300, height=22, fill="#e2e8f0", stroke="#94a3b8", stroke_width=1.5, rx=3)
    fill = root.add("rect", x=420, y=370, width=300, height=22, fill=BLUE, rx=3)
    sigma = 1.1
    n = 24
    prev = None
    for i in range(n + 1):
        f = i / n
        t = 1.5 + 9.0 * f
        acc = 3.0 * f
        tr = math.exp(-sigma * acc)
        if i == 0:
            fill.Set(t, "width", R(300 * tr))
        else:
            fill.Ramp(prev, t, "width", R(300 * tr))
        prev = t
    LiveText(scene, root, 50, 392, 1.5, 10.5, 6, lambda i, f: "光が通った不透明度の合計 %.1f → 届く光 %d %%" % (3.0 * f, round(100 * math.exp(-sigma * 3.0 * f))), size=14, fill=INK)
    scene.Text(root, 420, 418, "届く光の割合 = exp(−密度 × 合計)", size=12, weight=500, fill=GRAY)
    scene.Note(1.5, name, "髪の奥へ進むほど、光が減る")
    return dict(name=name, page=G + "hair/shadows.md", before="## Deep Opacity Maps", scene=scene, size=(780, 440), times=[1.5, 5.0, 8.5, 11.0])


def HairCoverage():
    name = "hair-coverage"
    scene = NewScene(name, 780, 430, duration=10.0, hold=1.5, title="細い髪は、画素の中心で判定すると途切れる。覆う割合で描くと、滑らか")
    root = scene.root
    cols = 12
    cw = 44
    x0 = 130
    width_px = 0.35
    rows = [(110, "中心で判定（ちらつく）"), (250, "覆う割合をアルファに（滑らか）")]
    for y, lab in rows:
        scene.Text(root, x0, y - 12, lab, size=13, fill=GRAY)
    cells = {}
    for ri, (y, lab) in enumerate(rows):
        for c in range(cols):
            rect = root.add("rect", x=x0 + c * cw, y=y, width=cw, height=cw, fill="#ffffff", stroke="#cbd5e1", stroke_width=1)
            cells[(ri, c)] = rect
    n = 40
    prev = None
    for i in range(n + 1):
        f = i / n
        t = 1.0 + 8.0 * f
        pos = 3.0 + 6.0 * f
        for c in range(cols):
            lo, hi = pos - width_px / 2, pos + width_px / 2
            center = c + 0.5
            hit = 1.0 if abs(center - pos) < width_px / 2 else 0.0
            cov = max(0.0, min(hi, c + 1) - max(lo, c)) / 1.0
            colors = [Hex([255 * (1 - hit * 0.82)] * 3), Hex([255 * (1 - min(0.85, cov * 2.3))] * 3)]
            for ri in (0, 1):
                col = colors[ri]
                if i == 0:
                    cells[(ri, c)].Set(t, "fill", col)
                else:
                    cells[(ri, c)].Steps("fill", [(t, col)]) if False else cells[(ri, c)].Set(t, "fill", col)
        prev = t
    line = root.add("rect", x=x0, y=102, width=3, height=56, fill=RED)
    line2 = root.add("rect", x=x0, y=242, width=3, height=56, fill=RED)
    prev = None
    for i in range(n + 1):
        f = i / n
        t = 1.0 + 8.0 * f
        px = R(x0 + (3.0 + 6.0 * f) * cw - 1.5)
        for node in (line, line2):
            if i == 0:
                node.Set(t, "x", px)
            else:
                node.Ramp(prev, t, "x", px)
        prev = t
    scene.Text(root, 130, 340, "赤: 髪の毛（幅 0.35 画素）", size=13, fill=RED)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "髪が画素の間をゆっくり動く"), (1.0, 9.5, "上: 中心を外すと消える（途切れ・点滅）／ 下: 常に薄く描かれる"), (9.5, 20, "幅を 1 画素に広げ、足りない分をアルファで薄める")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "髪の位置を 3 → 9 画素へ")
    return dict(name=name, page=G + "hair/anti-aliasing.md", before="## カバレッジによる解決", scene=scene, size=(780, 430), times=[1.7, 2.3, 3.4, 6.5])


FIGS = [SssSpread, GaussianSum, SssBlur, PreIntegrated, ThinTranslucency, SkinSpecular, EyeRefraction, KajiyaKay, MarschnerLobes, DeepOpacity, HairCoverage]
