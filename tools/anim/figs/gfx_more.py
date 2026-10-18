import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Lerp, LiveText, NewScene, R, Sweep)  # noqa: E402

G = "graphics/"


def PathD(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


def Smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def XLabel(scene, ax, text):
    scene.Text(scene.root, ax.x + ax.w, ax.y + ax.h + 36, text, size=12, weight=500, fill=GRAY, anchor="end")


def HaloRange():
    name = "halo-range"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="範囲チェック: 深度差が半径を超えるほど、遮蔽として数えない")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 4.0, 1.05, ylabel="遮蔽の重み")
    XLabel(scene, ax, "深度差 Δz ÷ 半径 R")
    for v in (1, 2, 3):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "%d R" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda d: Smooth01(1.0 / max(d, 1e-3))
    ax.Curve(fn, RED, width=4, n=120)
    dot = root.add("circle", cx=ax.X(0.05), cy=ax.Y(1.0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 9.0, 0.05, 4.0, n=50)
    LiveText(scene, root, 390, 355, 1.0, 9.0, 6, lambda i, f: ["Δz が R 以内: 重み 1（近い遮蔽物は、そのまま数える）", "R の少し外: 重みが下がり始める", "2 R: 重みはほぼ半分", "3 R: ほとんど数えない", "4 R: 無視（遠くの手前の物は、遮蔽にならない）", "→ 人物の背後の壁が、暗くならない"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "Δz を 0 → 4 R")
    return dict(name=name, page=G + "ao/artifacts/halo.md", before="### 範囲チェック：遠い遮蔽物の寄与を弱", scene=scene, size=(780, 400), times=[1.2, 4.0, 6.5, 9.0])


def SelfOcclusion():
    name = "bias-quant"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="深度の丸め誤差より、バイアスが小さいと、平らな面に縞が出る")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 60.0, 0.9, ylabel="深度の誤差 (m)")
    XLabel(scene, ax, "カメラからの距離 z (m)")
    err = lambda z: z * z / 13107.0
    ax.Curve(err, RED, width=4, n=100)
    scene.Text(root, ax.X(42), ax.Y(err(42)) - 14, "16 ビット深度の丸め誤差", size=12, weight=500, fill=RED)
    line = root.add("path", d="M0,0", fill="none", stroke=BLUE, stroke_width=4)
    betas = [0.0, 0.004, 0.008, 0.012, 0.016]
    prev = 0.0
    for k, b in enumerate(betas):
        t = 1.5 + k * 2.0
        d = ax.D(lambda z, b=b: b * z, n=60)
        if k == 0:
            line.Set(0, "d", d)
        else:
            line.Ramp(prev, t, "d", d)
        prev = t
    scene.Text(root, ax.X(2), ax.Y(0.8), "青: バイアス β·z", size=13, fill=BLUE)
    LiveText(scene, root, 390, 385, 1.5, 9.5, 4, lambda i, f: "β = %.3f: 縞が出る距離は %s" % (betas[i + 1], "z > %d m" % round(math.sqrt(13107.0 * betas[i + 1] ) * 13107.0 ** 0 * 0 + 13107.0 * betas[i + 1])) if False else "β = %.3f: 誤差がバイアスを超える距離 z > %d m（これより遠くで縞）" % (betas[i + 1], round(13107.0 * betas[i + 1])), size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "β を 0 → 0.016")
    return dict(name=name, page=G + "ao/artifacts/self-occlusion.md", before="### 対策 1：バイアスで余裕を持たせる", scene=scene, size=(780, 420), times=[1.5, 3.7, 6.0, 9.0])


def SaoMip():
    name = "sao-mip"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="サンプルまでの画面上の距離が 2 倍になるごとに、ミップが 1 つ上がる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 128.0, 6.0, ylabel="読むミップ レベル")
    XLabel(scene, ax, "サンプルまでの画面上の距離（画素）")
    fn = lambda d: max(0, min(5, math.floor(math.log2(max(d, 1.0))) - 3))
    pts = []
    for d in range(1, 129):
        pts.append((ax.X(d), ax.Y(fn(d) + 0.5)))
    root.add("path", d=PathD(pts), fill="none", stroke=GREEN, stroke_width=4)
    dot = root.add("circle", cx=ax.X(1), cy=ax.Y(0.5), r=7, fill=INK)
    prev = None
    n = 64
    for i in range(n + 1):
        d = 1 + 127 * i / n
        t = 1.0 + 8.0 * i / n
        if i == 0:
            dot.Set(t, "cx", ax.X(d))
            dot.Set(t, "cy", ax.Y(fn(d) + 0.5))
        else:
            dot.Ramp(prev, t, "cx", ax.X(d))
            dot.Ramp(prev, t, "cy", ax.Y(fn(d) + 0.5))
        prev = t
    for lv, d in ((0, 8), (1, 16), (2, 32), (3, 64), (4, 128)):
        scene.Text(root, ax.X(min(d, 125)), ax.y + ax.h + 18, str(d), size=11, weight=500, fill=GRAY, anchor="middle")
    scene.TextStack(root, 390, 365, [(0.0, 3.0, "8 画素以内: ミップ 0（細かい深度）"), (3.0, 5.5, "16〜32 画素: ミップ 1〜2"), (5.5, 20, "遠いサンプルほど粗いミップ → 小さい画像なのでキャッシュに乗る")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "距離 1 → 128 画素")
    return dict(name=name, page=G + "ao/sao.md", before="### どのミップから読むか", scene=scene, size=(780, 400), times=[1.5, 3.5, 6.0, 9.0])


def AlchemyWeight():
    name = "alchemy-weight"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="1 つの遮蔽物の効き方: 正面で近いほど強い（cosθ ÷ 距離）")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 90.0, 4.2, ylabel="遮蔽の強さ（相対）", xmin=-90.0)
    XLabel(scene, ax, "法線からの角度 θ (°)")
    cols = [BLUE, GREEN, RED]
    for k, rr in enumerate((1.0, 0.5, 0.25)):
        p = ax.Curve(lambda th, rr=rr: max(0.0, math.cos(math.radians(th))) / rr, cols[k], width=4, n=90, opacity=0)
        p.Show(1.0 + k * 3.0)
        scene.Text(root, ax.X(-88), ax.Y(min(4.0, 1.0 / rr)) - 8 + 0, "距離 %s" % rr, size=12, fill=cols[k], opacity=0).Show(1.0 + k * 3.0)
    scene.TextStack(root, 390, 360, [(0.0, 1.0, "式: max(0, v·n) ÷ (v·v) ≒ cosθ ÷ 距離"), (1.0, 4.0, "距離 1: 真上（θ = 0）で最大 1"), (4.0, 7.0, "距離 0.5: 2 倍強い"), (7.0, 20, "距離 0.25: 4 倍強い。横（θ = ±90°）はどれも 0")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "距離 1 → 0.5 → 0.25")
    return dict(name=name, page=G + "ao/alchemy-ao.md", before="### 各項の意味", scene=scene, size=(780, 400), times=[1.5, 4.5, 7.5, 11.0])


def SphereGray():
    name = "sphere-vs-hemisphere"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="平らな面で、球のサンプルは半分が面の中に入る（灰色になる）")
    root = scene.root
    rng = random.Random(7)
    pts = []
    while len(pts) < 16:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y <= 1:
            pts.append((x, y))
    count_s = 0
    for side, (cx, ttl) in enumerate(((210, "球にサンプル（Crytek）"), (560, "半球にサンプル（法線を使う）"))):
        cy = 190
        root.add("circle", cx=cx, cy=cy, r=100, fill="none", stroke=LIGHT, stroke_width=2, stroke_dasharray="6 4")
        root.add("rect", x=cx - 140, y=cy, width=280, height=60, fill="#cbd5e1")
        root.add("line", x1=cx - 140, y1=cy, x2=cx + 140, y2=cy, stroke=INK, stroke_width=3)
        scene.Text(root, cx, 70, ttl, size=14, fill=GRAY, anchor="middle")
        inside = 0
        for i, (x, y) in enumerate(pts):
            px, py = cx + x * 100, cy + (y if side == 0 else -abs(y)) * 100
            below = (side == 0 and y > 0)
            if below:
                inside += 1
            col = RED if below else GREEN
            c = root.add("circle", cx=R(px), cy=R(py), r=6, fill=col, opacity=0)
            c.Show(1.0 + i * 0.4)
        if side == 0:
            count_s = inside
        else:
            count_h = 0
        scene.Counter(root, cx, 335, [(0, 0)] + [(1.0 + i * 0.4, sum(1 for (xx, yy) in pts[:i + 1] if side == 0 and yy > 0)) for i in range(16)], size=26, fill=RED, anchor="middle")
    scene.Text(root, 210, 365, "面の中（赤）に入った数 / 16", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Text(root, 560, 365, "常に 0 / 16 → 平らな面は、遮蔽なし", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Text(root, 390, 398, "球では、何も遮るものがなくても、約半分が「遮蔽」と数えられる", size=13, weight=500, fill=INK, anchor="middle")
    scene.Note(1.0, name, "16 個のサンプルを順に表示")
    return dict(name=name, page=G + "ao/ssao-crytek.md", before="### 1. 平らな面が灰色になる", scene=scene, size=(780, 420), times=[2.0, 4.0, 6.5, 8.5])


def GtaoVisibility():
    name = "gtao-visibility"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="GTAO: 両側の地平線の高さが上がるほど、見える範囲が狭まる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 90.0, 1.05, ylabel="可視性（コサイン重み付き）")
    XLabel(scene, ax, "両側の地平線の角度 h (°、水平から)")

    def Vis(h):
        # 法線が視線と一致（γ = 0）、h1 = -h, h2 = +h のとき: â = 1 - sin(h)^2 ... 閉じた式から
        h = math.radians(h)
        # 論文の式を h1=-hh, h2=hh,  γ=0 で評価（地平線は天頂から測る: hh = 90° - h）
        hh = math.pi / 2 - h
        a = 0.25 * (-math.cos(2 * -hh) + 1) + 0.25 * (-math.cos(2 * hh) + 1)
        return a
    fn = lambda h: Vis(h)
    ax.Curve(fn, RED, width=4, n=90)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(fn(0)), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 9.0, 0.0, 90.0, n=45)
    LiveText(scene, root, 390, 360, 1.0, 9.0, 5, lambda i, f: "h = %d°: 可視性 %d %%" % (round(90 * f), round(100 * fn(90 * f))), size=15, fill=INK, anchor="middle")
    scene.Note(1.0, name, "h を 0 → 90°")
    return dict(name=name, page=G + "ao/gtao.md", before="### 内側の積分の式", scene=scene, size=(780, 420), times=[1.2, 3.5, 6.0, 9.0])


def TemporalConverge():
    name = "temporal-converge"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="毎フレーム違うノイズを、履歴と混ぜると、真の値に近づく")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 60.0, 1.0, ylabel="AO の値")
    XLabel(scene, ax, "フレーム")
    rng = random.Random(3)
    true_v = 0.55
    raw = [min(1.0, max(0.0, true_v + rng.gauss(0, 0.2))) for _ in range(61)]
    ema = [raw[0]]
    for v in raw[1:]:
        ema.append(ema[-1] * 0.9 + v * 0.1)
    ax.Curve(lambda f: true_v, "#94a3b8", width=2, n=2, dash="6 4")
    scene.Text(root, ax.X(58), ax.Y(true_v) - 8, "真の値", size=12, fill=GRAY, anchor="end")
    n = 60
    rawp = root.add("path", d="M0,0", fill="none", stroke="#cbd5e1", stroke_width=2)
    emap = root.add("path", d="M0,0", fill="none", stroke=RED, stroke_width=4)
    prev = 0.0
    rawp.Set(0, "d", PathD([(ax.X(0), ax.Y(raw[0])), (ax.X(0.01), ax.Y(raw[0]))]))
    emap.Set(0, "d", PathD([(ax.X(0), ax.Y(ema[0])), (ax.X(0.01), ax.Y(ema[0]))]))
    steps = 20
    for k in range(1, steps + 1):
        m = round(n * k / steps)
        t = 1.0 + 9.0 * k / steps
        rawp.Ramp(prev, t, "d", PathD([(ax.X(i), ax.Y(raw[i])) for i in range(m + 1)] + [(ax.X(m) + 0.01 * i, ax.Y(raw[m])) for i in range(0)]) if m >= 1 else PathD([(ax.X(0), ax.Y(raw[0])), (ax.X(0.01), ax.Y(raw[0]))])) if False else None
        prev = t
    # path with fixed point count so that Ramp can interpolate
    def Prog(arr, m):
        pts = []
        for i in range(n + 1):
            j = min(i, m)
            pts.append((ax.X(j), ax.Y(arr[j])))
        return PathD(pts)
    prev = 0.0
    rawp.Set(0, "d", Prog(raw, 0))
    emap.Set(0, "d", Prog(ema, 0))
    for k in range(1, steps + 1):
        m = round(n * k / steps)
        t = 1.0 + 9.0 * k / steps
        rawp.Ramp(prev, t, "d", Prog(raw, m))
        emap.Ramp(prev, t, "d", Prog(ema, m))
        prev = t
    scene.Text(root, 90, 100, "灰: 毎フレームの結果（ノイズだらけ）", size=13, fill=GRAY)
    scene.Text(root, 90, 120, "赤: 履歴と混ぜた結果（α = 0.1）", size=13, fill=RED)
    scene.TextStack(root, 390, 375, [(0.0, 1.0, "1 フレーム 8 サンプルだけ。ばらつきが大きい"), (1.0, 7.0, "混ぜるほど、ばらつきが減る"), (7.0, 20, "約 20 フレームで、実質 数十サンプル相当。動くと、履歴は捨てる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "フレーム 0 → 60")
    return dict(name=name, page=G + "ao/filtering/temporal.md", before="### ① 再投影", scene=scene, size=(780, 420), times=[1.5, 4.0, 7.0, 10.5])


def NoisePoints():
    name = "noise-points"
    scene = NewScene(name, 780, 400, duration=9.0, hold=1.5, title="ホワイト ノイズは固まりができる。ブルー ノイズは均一に散る")
    root = scene.root
    rng = random.Random(11)
    n = 64
    white = [(rng.random(), rng.random()) for _ in range(n)]
    blue = []
    for _ in range(n):
        best, bd = None, -1
        for _ in range(12):
            c = (rng.random(), rng.random())
            d = min([math.hypot(c[0] - b[0], c[1] - b[1]) for b in blue] or [9])
            if d > bd:
                best, bd = c, d
        blue.append(best)
    for k, (x0, pts, ttl, col) in enumerate(((60, white, "ホワイト ノイズ（独立な乱数）", RED), (420, blue, "ブルー ノイズ（近づきすぎない）", BLUE))):
        root.add("rect", x=x0, y=80, width=300, height=260, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, x0 + 150, 70, ttl, size=13, fill=GRAY, anchor="middle")
        for i, (x, y) in enumerate(pts):
            c = root.add("circle", cx=R(x0 + 8 + x * 284), cy=R(88 + y * 244), r=5, fill=col, opacity=0)
            c.Show(0.5 + i * 0.1)
    scene.TextStack(root, 390, 375, [(0.0, 6.0, "点を 64 個ずつ置いていく"), (6.0, 20, "左: 固まりと隙間ができる（ぼかしても低周波の斑が残る）／ 右: 均一なのでぼかしで消えやすい")], size=14, fill=INK, anchor="middle")
    scene.Note(0.5, name, "点を順に置く")
    return dict(name=name, page=G + "ao/filtering/noise-pattern.md", before="### ホワイト ノイズ", scene=scene, size=(780, 400), times=[2.0, 4.0, 7.0, 9.0])


def IrradianceConv():
    name = "irradiance-conv"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="鋭い入射光も、余弦でぼかすと、なめらかな放射照度になる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 180.0, 1.0, xmin=-180.0, ylabel="明るさ（相対）")
    XLabel(scene, ax, "方向の角度（°）。0 = 真上")

    def L(a):
        sun = math.exp(-0.5 * ((a - 35) / 6.0) ** 2)
        sky = 0.18 + 0.12 * math.cos(math.radians(a))
        return 0.7 * sun + sky if abs(a) < 90 else 0.05

    def E(th):
        s = 0.0
        for k in range(360):
            a = -180 + k
            s += L(a) * max(0.0, math.cos(math.radians(a - th)))
        return s / 120.0

    emax = max(E(t) for t in range(-180, 181, 4))
    ax.Curve(L, "#cbd5e1", width=3, n=180)
    scene.Text(root, ax.X(-175), ax.Y(0.92), "灰: 入ってくる光（太陽は鋭い）", size=13, fill=GRAY)
    scene.Text(root, ax.X(-175), ax.Y(0.80), "赤: 法線 n ごとの放射照度（なめらか）", size=13, fill=RED)
    fn = lambda th: E(th) / emax * 0.95
    p = ax.Curve(fn, RED, width=4.5, n=180, opacity=0)
    p.Show(1.0)
    dot = root.add("circle", cx=ax.X(-180), cy=ax.Y(fn(-180)), r=7, fill=INK)
    Sweep(dot, ax, fn, 2.0, 10.0, -180.0, 180.0, n=60)
    scene.TextStack(root, 390, 375, [(0.0, 2.0, "入ってくる光は、太陽のところだけ鋭い"), (2.0, 20, "法線を回すと、放射照度は、ゆるやかに変わる → 少ない数値で持てる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "n を −180° → 180°")
    return dict(name=name, page=G + "gi/theory/irradiance.md", before="### なぜ「なめらか」なのか", scene=scene, size=(780, 420), times=[1.2, 4.0, 7.0, 10.0])


def CloudPowder():
    name = "cloud-beer-powder"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="Beer（奥ほど暗い）× Powder（縁は暗い）= 縁が暗く、中が明るい雲")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 3.0, 1.05, ylabel="明るさ")
    XLabel(scene, ax, "光が雲の中を通った厚み（密度の積分）")
    cur = [("Beer  exp(−d)", lambda d: math.exp(-d), BLUE), ("Powder  1 − exp(−2d)", lambda d: 1 - math.exp(-2 * d), GREEN), ("積（Beer × Powder）", lambda d: math.exp(-d) * (1 - math.exp(-2 * d)) * 2.0, RED)]
    for k, (lab, fn, col) in enumerate(cur):
        p = ax.Curve(fn, col, width=4, n=100, opacity=0)
        p.Show(1.0 + k * 2.5)
        scene.Text(root, 90, 100 + k * 20, lab, size=13, fill=col, opacity=0).Show(1.0 + k * 2.5)
    scene.TextStack(root, 390, 375, [(0.0, 1.0, "雲の明るさを、2 つの項で決める"), (1.0, 3.5, "Beer: 厚いほど光が減る（縁が最も明るくなってしまう）"), (3.5, 6.0, "Powder: 薄い縁は、内側から出る光が少なく暗い"), (6.0, 20, "掛け合わせて、中間の厚みが最も明るい（積を 2 倍して表示）")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "Beer → Powder → 積")
    return dict(name=name, page=G + "atmosphere/clouds/lighting.md", before="### Powder 効果", scene=scene, size=(780, 420), times=[1.5, 4.0, 6.5, 9.0])


def CloudProfiles():
    name = "cloud-profiles"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="雲の種類で、高さごとの密度の形が違う")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 1.0, 1.05, ylabel="密度")
    XLabel(scene, ax, "層の中の高さ（0: 下端 〜 1: 上端）")

    def Remap(v, a, b, c, d):
        return c + (v - a) / (b - a) * (d - c)

    sat = lambda v: max(0.0, min(1.0, v))
    prof = [
        ("層雲: 下側に薄く", lambda h: sat(Remap(h, 0.0, 0.1, 0, 1)) * sat(Remap(h, 0.2, 0.3, 1, 0)), BLUE),
        ("層積雲: 下半分に厚み", lambda h: sat(Remap(h, 0.0, 0.2, 0, 1)) * sat(Remap(h, 0.4, 0.7, 1, 0)), GREEN),
        ("積雲: 雲底が平ら、上は丸い", lambda h: sat(Remap(h, 0.0, 0.07, 0, 1)) * sat(Remap(h, 0.2, 1.0, 1, 0)), RED),
    ]
    for k, (lab, fn, col) in enumerate(prof):
        p = ax.Curve(fn, col, width=4, n=100, opacity=0)
        p.Show(1.0 + k * 2.5)
        scene.Text(root, 90, 100 + k * 20, lab, size=13, fill=col, opacity=0).Show(1.0 + k * 2.5)
    scene.TextStack(root, 390, 365, [(0.0, 1.0, "ノイズの形に、高さのプロファイルを掛ける"), (1.0, 8.5, "プロファイルを変えるだけで、雲の種類が変わる"), (8.5, 20, "積雲: 底が平らで、てっぺんが丸い、雲らしい輪郭")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "層雲 → 層積雲 → 積雲")
    return dict(name=name, page=G + "atmosphere/clouds/layers.md", before="### 高度プロファイルの考え方", scene=scene, size=(780, 400), times=[1.5, 4.0, 6.5, 9.0])


def FogIntegrate():
    name = "fog-integrate"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="スライスを手前から奥へ累積する: 光は足され、透過率は掛けられる")
    root = scene.root
    n = 12
    rng = random.Random(5)
    S = [0.0, 0.1, 0.5, 0.9, 0.3, 0.1, 0.0, 0.6, 0.8, 0.2, 0.1, 0.0]
    sigma = [0.1, 0.15, 0.3, 0.4, 0.25, 0.15, 0.1, 0.3, 0.35, 0.2, 0.15, 0.1]
    dz = 1.0
    acc, tr = 0.0, 1.0
    accs, trs = [], []
    for i in range(n):
        st = math.exp(-sigma[i] * dz)
        integ = (S[i] - S[i] * st) / sigma[i]
        acc += integ * tr
        tr *= st
        accs.append(acc)
        trs.append(tr)
    assert abs(trs[-1] - math.exp(-sum(sigma) * dz)) < 1e-9
    x0, w = 90, 50
    for i in range(n):
        root.add("rect", x=x0 + i * w, y=100, width=w - 4, height=60, fill="#e0f2fe", stroke="#94a3b8", stroke_width=1)
        a = 0.15 + 0.85 * min(1.0, S[i])
        root.add("rect", x=x0 + i * w, y=100 + 60 * (1 - min(1.0, S[i])), width=w - 4, height=60 * min(1.0, S[i]), fill=AMBER, fill_opacity=0.8)
        scene.Text(root, x0 + i * w + (w - 4) / 2, 178, str(i + 1), size=11, weight=500, fill=GRAY, anchor="middle")
    scene.Text(root, x0, 92, "各スライスの散乱光（橙の高さ）", size=12, weight=500, fill=GRAY)
    ax = Axes(scene, root, 90, 215, 600, 140, 12.0, 1.0, xlabel="", ylabel="累積した光（橙）／ 透過率（青）", xmin=0.0)
    amax = max(accs) * 1.05
    pa = root.add("path", d="M0,0", fill="none", stroke=AMBER, stroke_width=4)
    pt = root.add("path", d="M0,0", fill="none", stroke=BLUE, stroke_width=4)

    def Prog(arr, m, scale):
        pts = [(ax.X(0), ax.Y(0 if scale != 1 else 1.0))]
        for i in range(n):
            j = min(i, m)
            pts.append((ax.X(i + 1), ax.Y(arr[j] * (1 if scale == 1 else 1.0 / amax))))
        return PathD(pts)
    prev = 0.0
    pa.Set(0, "d", Prog(accs, -1 if False else 0, 0))
    pt.Set(0, "d", Prog(trs, 0, 1))
    for k in range(1, n + 1):
        t = 1.0 + 9.0 * k / n
        pa.Ramp(prev, t, "d", Prog(accs, k - 1, 0))
        pt.Ramp(prev, t, "d", Prog(trs, k - 1, 1))
        prev = t
    LiveText(scene, root, 390, 395, 1.0, 10.0, n, lambda i, f: "スライス %d まで: 累積光 %.2f、透過率 %.2f" % (i + 1, accs[i], trs[i]), size=14, fill=INK, anchor="middle")
    scene.Text(root, 390, 422, "光 += 透過率 × (S − S·e^(−σΔz)) / σ　　透過率 ×= e^(−σΔz)", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "スライス 1 → 12")
    return dict(name=name, page=G + "atmosphere/volumetric-fog/integration.md", before="## ④ 適用", scene=scene, size=(780, 440), times=[2.5, 5.0, 8.0, 10.5])


def RidgeNoise():
    name = "ridge-steps"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="ノイズ → 絶対値 → 反転 → 2 乗で、尖った尾根ができる")
    root = scene.root
    rows = [("① ノイズ n", lambda x: math.sin(x * 2.0) * 0.6 + 0.3 * math.sin(x * 5.3 + 1), BLUE), ("② |n|（谷の線が 0）", None, GREEN), ("③ 1 − |n|（0 だった所が尾根）", None, AMBER), ("④ 2 乗（尾根を鋭くする）", None, RED)]
    n0 = rows[0][1]
    fns = [n0, lambda x: abs(n0(x)), lambda x: 1 - abs(n0(x)), lambda x: (1 - abs(n0(x))) ** 2]
    x0, x1 = 90, 700
    for k, (lab, _, col) in enumerate(rows):
        y = 100 + k * 80
        root.add("line", x1=x0, y1=y + 30, x2=x1, y2=y + 30, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, x0, y - 22, lab, size=13, fill=col)
        pts = []
        for i in range(121):
            xv = 0.0 + i * 0.07
            v = fns[k](xv)
            pts.append((x0 + (x1 - x0) * i / 120, y + 30 - (v if k == 0 else v) * 30 * (1 if k else 1)))
        p = root.add("path", d=PathD(pts), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(1.0 + k * 2.5)
    scene.TextStack(root, 390, 425, [(0.0, 1.0, "地形のリッジ ノイズを、段階ごとに見る"), (1.0, 3.5, "元のノイズ"), (3.5, 6.0, "絶対値: 0 を横切る所が、谷の折れ目"), (6.0, 8.5, "反転: 折れ目が、尖った尾根になる"), (8.5, 20, "2 乗: 尾根の先が鋭く、谷が平らになる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "① → ④")
    return dict(name=name, page=G + "terrain/generation/ridge.md", before="## よくあるミス", scene=scene, size=(780, 440), times=[1.5, 4.0, 6.5, 9.5])


FIGS = [HaloRange, SelfOcclusion, SaoMip, AlchemyWeight, SphereGray, GtaoVisibility, TemporalConverge, NoisePoints, IrradianceConv, CloudPowder, CloudProfiles, FogIntegrate, RidgeNoise]
