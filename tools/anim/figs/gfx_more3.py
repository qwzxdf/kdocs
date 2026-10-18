import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402

G = "graphics/"
BEFORE = "## よくあるミス"


def XLabel(scene, ax, text):
    scene.Text(scene.root, ax.x + ax.w, ax.y + ax.h + 36, text, size=12, weight=500, fill=GRAY, anchor="end")


def Morph(name, page, title, xlabel, ylabel, xmax, ymax, fns, caps, color=AMBER, ticks=None, ref=None, n=80):
    """パラメータだけ違う曲線を、順にぐにゃっと変形させる。"""
    scene = NewScene(name, 780, 420, duration=1.2 + 2.6 * len(fns) + 0.6, hold=1.5, title=title)
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, xmax, ymax, ylabel=ylabel)
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
    size = (780, 420)
    times = [1.0 + 2.6 * k + 1.2 for k in range(len(fns))][:4]
    return dict(name=name, page=G + page, before=BEFORE, scene=scene, size=size, times=times)


def Fresnel():
    f0s = [0.02, 0.04, 0.2, 0.9]
    fns = [lambda a, f=f: f + (1 - f) * (1 - math.cos(math.radians(a))) ** 5 for f in f0s]
    caps = ["F0 = 0.02（水）: 真上から見ると 2%、浅い角度で 100% に近づく", "F0 = 0.04（ガラスなど多くの非金属）: 同じ形で、底が少し高い", "F0 = 0.2（宝石など）: 底が高く、変化が小さい", "F0 = 0.9（金属）: 角度によらず、ほとんど反射する"]
    return Morph("fresnel-f0", "translucency/refraction/fresnel.md", "フレネル反射率: F0 で曲線の底が変わり、浅い角度で 1 に近づく", "視線と法線の角度 (度)", "反射率 F", 90.0, 1.05, fns, caps, color=BLUE, ticks=[0, 30, 60, 90])


def GgxLobe():
    alphas = [0.05, 0.15, 0.3, 0.6]
    fns = [lambda a, al=al: al ** 4 / ((math.cos(math.radians(a)) ** 2 * (al * al - 1) + 1) ** 2) for al in alphas]
    caps = ["alpha = 0.05（つるつる）: 細くて鋭い光点", "alpha = 0.15: 少し広がる", "alpha = 0.3: ぼんやりした光の塊", "alpha = 0.6（ざらざら）: 広くて弱い"]
    return Morph("ggx-lobe", "water/shading/specular.md", "粗さを上げると、ハイライトの山が、低く広くなる(山の高さを 1 に正規化)", "ハーフベクトルと法線の角度 (度)", "D(θ) ÷ D(0)", 40.0, 1.05, fns, caps, color=RED, ticks=[0, 10, 20, 30, 40])


def Obscurance():
    ks = [0.5, 1.0, 2.0, 4.0]
    fns = [lambda d, k=k: 1 - math.exp(-k * d) for k in ks]
    caps = ["k = 0.5: ゆるやか。遠くの物まで遮蔽に数える", "k = 1: 距離 1 で、光の 63% が届く", "k = 2: 近い物だけが、強く効く", "k = 4: ごく近い物だけ(AO の半径を小さくしたのと同じ)"]
    return Morph("obscurance-rho", "ao/theory/obscurance.md", "遮蔽物が近いほど暗く、遠いほど光が届く: ρ(d) = 1 − exp(−k·d)", "遮蔽物までの距離 d", "光が届く割合 ρ(d)", 4.0, 1.05, fns, caps, color=GREEN, ticks=[0, 1, 2, 3, 4])


def FoamDecay():
    ds = [0.95, 0.98, 0.99]
    half = [math.log(0.5) / math.log(d) for d in ds]
    fns = [lambda f, d=d: d ** f for d in ds]
    caps = ["decay = %.2f: 半分になるまで約 %d フレーム（60fps で %.1f 秒）" % (d, round(h), h / 60) for d, h in zip(ds, half)]
    assert [round(h) for h in half] == [14, 34, 69]
    return Morph("foam-decay", "water/shore-foam/foam-history.md", "泡は毎フレーム decay 倍に薄れる: 値が 1 に近いほど長く残る", "経過フレーム", "泡の濃さ", 180.0, 1.05, fns, caps, color=BLUE, ticks=[0, 60, 120, 180])


def HeightBlend():
    cs = [1.0, 2.0, 4.0, 10.0]
    fns = [lambda t, c=c: max(0.0, min(1.0, (t - 0.5) * c + 0.5)) for c in cs]
    caps = ["コントラスト 1: 2 つの地面が、全体でなだらかに混ざる", "コントラスト 2: 境目が、少し細くなる", "コントラスト 4: 小石の高い所から先に、顔を出す", "コントラスト 10: ほぼ切り替え。石の隙間に土が残る"]
    return Morph("height-blend-contrast", "terrain/texturing/height-blend.md", "高さで混ぜると、重みの曲線が急になる(石の高い所から先に出る)", "ペイントの濃さ t（0 = 土、1 = 石）", "石の重み", 1.0, 1.05, fns, caps, color=PURPLE, ticks=[0, 0.5, 1])


def DispersionDelta():
    def fn(a):
        s = math.sin(math.radians(a))
        return math.degrees(math.asin(s / 1.51) - math.asin(s / 1.53)) * 10
    scene = NewScene("dispersion-delta", 780, 420, duration=10.0, hold=1.5, title="入射角が大きいほど、赤と青の曲がり方の差が広がる(差を 10 倍で表示)")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 90.0, math.ceil(fn(89.5) * 1.1), ylabel="屈折角の差 θ赤 − θ青（度 × 10）")
    XLabel(scene, ax, "入射角 (度)")
    for v in (0, 30, 60, 90):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    ax.Curve(fn, PURPLE, width=4, n=90)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 9.0, 0.0, 89.0, n=60)
    LiveText(scene, root, 390, 392, 1.0, 9.0, 4, lambda i, f: ["0 度（真正面）: 差はゼロ。色は分かれない", "30 度: 差はわずか", "60 度: 差が目に見えてくる", "ふちに近い角度: 差が最大 → 縁に虹色が出る"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, "dispersion-delta", "入射角 0 → 90")
    return dict(name="dispersion-delta", page=G + "translucency/refraction/dispersion.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 8.5])


def ConstantBias():
    name = "bias-needed"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="必要なバイアスは、面が斜めなほど増える。一定のバイアスでは足りない")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 80.0, 6.0, ylabel="必要なバイアス（シャドウ マップの 1 テクセル単位）")
    XLabel(scene, ax, "光と面の法線の角度 (度)")
    for v in (0, 20, 40, 60, 80):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    need = lambda a: math.tan(math.radians(a))
    ax.Curve(lambda a: 1.0, GRAY, width=3, dash="6 5")
    scene.Text(root, ax.X(66), ax.Y(1.0) - 10, "一定のバイアス = 1", size=12, weight=500, fill=GRAY)
    ax.Curve(need, RED, width=4, n=100, x1=80.0)
    scene.Text(root, ax.X(52), ax.Y(need(52)) - 12, "必要な量 = tan θ", size=12, weight=700, fill=RED)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, need, 1.0, 9.5, 0.0, 78.0, n=60)
    LiveText(scene, root, 390, 392, 1.0, 9.5, 4, lambda i, f: ["光が真上から: 必要なバイアスはほぼ 0", "45 度: ちょうど 1 テクセル(一定の 1 と交わる)", "60 度: 1.7 テクセル必要 → 足りない所に縞(アクネ)", "浅い角度: 数テクセル必要。大きくすると影が離れる"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "角度を 0 → 78 度")
    return dict(name=name, page=G + "shadows/bias/constant-bias.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def PeterPanning():
    name = "bias-tradeoff"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="バイアスの綱引き(概念図): 小さいと縞、大きいと影が離れる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 2.0, 1.05, ylabel="目立ち方（概念図）")
    XLabel(scene, ax, "バイアスの大きさ（テクセル）")
    for v in (0, 0.5, 1, 1.5, 2):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "%g" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    acne = lambda b: max(0.0, 1 - b / 1.0) ** 1.5
    pan = lambda b: min(1.0, b / 2.0) ** 1.2
    ax.Curve(acne, RED, width=4, n=80)
    ax.Curve(pan, BLUE, width=4, n=80)
    scene.Text(root, ax.X(0.08), ax.Y(0.55), "シャドウ アクネ(縞)", size=13, weight=700, fill=RED)
    scene.Text(root, ax.X(1.35), ax.Y(0.55), "ピーターパンニング", size=13, weight=700, fill=BLUE)
    band = root.add("rect", x=ax.X(0.9), y=ax.y, width=ax.X(1.15) - ax.X(0.9), height=ax.h, fill=GREEN, opacity=0)
    band.Set(6.0, "opacity", 0.22)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=7, fill=INK)
    Sweep(dot, ax, acne, 1.0, 5.5, 0.0, 1.0, n=30)
    dot2 = root.add("circle", cx=ax.X(1.0), cy=ax.Y(pan(1.0)), r=7, fill=INK, opacity=0)
    dot2.Show(5.5)
    Sweep(dot2, ax, pan, 5.5, 9.5, 1.0, 1.8, n=30)
    scene.TextStack(root, 390, 392, [(0.0, 1.0, "バイアスを 0 から増やしていく"), (1.0, 5.5, "小さい: 自分の影で縞が出る。増やすほど消える"), (5.5, 20, "縞が消えた後も増やすと、影が物から離れる。緑の帯が、ちょうどよい範囲")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "バイアスを増やす")
    return dict(name=name, page=G + "shadows/bias/peter-panning.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.5, 9.5])


def DepthBeer():
    name = "water-depth-color"
    scene = NewScene(name, 780, 460, duration=11.0, hold=1.5, title="水は深くなるほど、赤から先に吸われ、青緑だけが残る")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 230, 20.0, 1.05, ylabel="残る光 exp(−σ·深さ)")
    XLabel(scene, ax, "水の深さ (m)")
    sig = {"R": 0.45, "G": 0.07, "B": 0.02}
    cols = {"R": RED, "G": GREEN, "B": BLUE}
    for k, key in enumerate("RGB"):
        fn = lambda d, s=sig[key]: math.exp(-s * d)
        c = ax.Curve(fn, cols[key], width=4, n=80, opacity=0)
        c.Show(0.8 + k * 0.4)
        dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=6, fill=cols[key])
        Sweep(dot, ax, fn, 2.0, 9.5, 0.0, 20.0, n=60)
        scene.Text(root, ax.X(19.4), ax.Y(fn(19.4)) - 10, key, size=13, weight=700, fill=cols[key])
    root.add("rect", x=70, y=345, width=640, height=34, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    sw = root.add("rect", x=72, y=347, width=636, height=30, fill="#ffffff")
    RampFill(sw, "fill", 2.0, 9.5, 40, lambda f: Hex([255 * math.exp(-sig[c] * 20 * f) for c in "RGB"]))
    scene.Text(root, 70, 338, "白い砂底が、深さ d の水を通して見える色", size=12, weight=500, fill=GRAY)
    LiveText(scene, root, 390, 420, 2.0, 9.5, 4, lambda i, f: ["浅い所: 砂の色がそのまま見える", "数 m: 赤が消えて、緑がかった色に", "10 m 前後: 青緑だけが残る", "20 m: ほぼ暗い青(吸収で光が足りない)"][i], size=14, fill=INK, anchor="middle")
    scene.Note(2.0, name, "深さ 0 → 20 m")
    return dict(name=name, page=G + "water/shading/depth-color.md", before=BEFORE, scene=scene, size=(780, 460), times=[1.5, 4.0, 6.5, 9.5])


def DitherGrid():
    name = "dither-alpha"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="ディザ透明: アルファを上げると、閾値の小さい画素から順に不透明になる")
    root = scene.root
    bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
    cs, ox, oy = 62, 150, 90
    for idx in range(16):
        cx, cy = ox + (idx % 4) * cs, oy + (idx // 4) * cs
        thr = (bayer[idx] + 0.5) / 16
        root.add("rect", x=cx, y=cy, width=cs - 4, height=cs - 4, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        on = root.add("rect", x=cx, y=cy, width=cs - 4, height=cs - 4, fill=INK, opacity=0)
        on.Set(1.0 + thr * 11.0, "opacity", 1)
        scene.Text(root, cx + (cs - 4) / 2, cy + cs / 2 + 4, "%.2f" % thr, size=12, weight=700, fill=GRAY, anchor="middle")
    scene.Text(root, ox, oy - 12, "各画素の数字 = 閾値。アルファ > 閾値 なら描く(黒)", size=13, weight=500, fill=GRAY)
    LiveText(scene, root, 390, 395, 1.0, 12.0, 6, lambda i, f: "アルファ = %.2f → %d / 16 画素が不透明" % ((i + 0.5) / 6, round((i + 0.5) / 6 * 16)), size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "アルファ 0 → 1")
    return dict(name=name, page=G + "translucency/alpha-test/dither.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.5, 4.5, 8.0, 12.0])


def ClipmapRings():
    name = "clipmap-rings"
    scene = NewScene(name, 780, 480, duration=11.0, hold=1.5, title="クリップマップ: 同じ格子数の層を、倍々の広さで入れ子にする")
    root = scene.root
    cx, cy, base = 390, 235, 160
    cols = [GREEN, BLUE, AMBER, RED]
    for lv in range(4):
        half = base * (0.5 ** (3 - lv))
        cells = 8
        step = 2 * half / cells
        g = root.add("g", opacity=0)
        g.add("rect", x=cx - half, y=cy - half, width=2 * half, height=2 * half, fill="none", stroke=cols[lv], stroke_width=2.5)
        for i in range(1, cells):
            g.add("line", x1=cx - half + i * step, y1=cy - half, x2=cx - half + i * step, y2=cy + half, stroke=cols[lv], stroke_width=1)
            g.add("line", x1=cx - half, y1=cy - half + i * step, x2=cx + half, y2=cy - half + i * step, stroke=cols[lv], stroke_width=1)
        g.Show(1.0 + (3 - lv) * 2.2)
    root.add("circle", cx=cx, cy=cy, r=6, fill=INK)
    scene.Text(root, cx + 10, cy - 8, "カメラ", size=12, weight=700, fill=INK)
    scene.TextStack(root, 390, 450, [(0.0, 1.0, "どの層も 8×8 のマス(頂点の数は同じ)"), (1.0, 3.2, "層 0: 最も細かい。カメラの足元"), (3.2, 5.4, "層 1: 広さ 2 倍、マスも 2 倍の粗さ"), (5.4, 7.6, "層 2: さらに 2 倍"), (7.6, 20, "層 3: 遠景。頂点の数は変わらないのに、遠くまで届く")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "層 0 → 3")
    return dict(name=name, page=G + "terrain/lod/clipmap.md", before=BEFORE, scene=scene, size=(780, 480), times=[1.5, 3.5, 6.0, 9.0])


def HeightMip():
    name = "height-mip-bars"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="高さのミップ: 隣り合う 2 つを平均して、半分の解像度を作る")
    root = scene.root
    h0 = [0.30, 0.80, 0.55, 0.65, 0.20, 0.35, 0.90, 0.50]
    levels = [h0]
    while len(levels[-1]) > 1:
        a = levels[-1]
        levels.append([(a[2 * i] + a[2 * i + 1]) / 2 for i in range(len(a) // 2)])
    base_y, width, x0, maxh = 330, 560, 110, 200
    cols = [GRAY, BLUE, GREEN, AMBER]
    for lv, hs in enumerate(levels):
        n = len(hs)
        w = width / n
        g = root.add("g", opacity=0)
        for i, hv in enumerate(hs):
            g.add("rect", x=x0 + i * w + 3, y=base_y - hv * maxh, width=w - 6, height=hv * maxh, fill=cols[lv], opacity=0.85 if lv else 0.7)
        scene.Text(g, x0 - 12, base_y - 6, "層 %d（%d 点）" % (lv, n), size=12, weight=700, fill=cols[lv], anchor="end")
        if lv == 0:
            g.Show(1.0)
        else:
            g.Show(1.0 + lv * 3.0)
        # 前の層は、次が出たら薄くする
        if lv + 1 < len(levels):
            g.Set(1.0 + (lv + 1) * 3.0, "opacity", 0.25)
    root.add("line", x1=x0, y1=base_y, x2=x0 + width, y2=base_y, stroke="#94a3b8", stroke_width=2)
    scene.TextStack(root, 390, 385, [(0.0, 1.0, "8 点の高さ"), (1.0, 4.0, "元の高さ（層 0）"), (4.0, 7.0, "2 つずつ平均 → 4 点（層 1）。山の細かい凹凸が消える"), (7.0, 10.0, "さらに平均 → 2 点（層 2）"), (10.0, 20, "最後は 1 点（全体の平均の高さ）。遠景には、粗い層を使う")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "層 0 → 3")
    return dict(name=name, page=G + "terrain/lod/height-mip.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.5, 4.5, 7.5, 10.5])


def ShStorage():
    name = "sh-coeff-count"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="SH の次数が上がると、必要な係数が増える(RGB の 3 色ぶん)")
    root = scene.root
    bands = [("L0（1 次）", 1, GREEN), ("L1（2 次）", 4, BLUE), ("L2（3 次）", 9, RED)]
    base_y, x0 = 300, 170
    total = 0
    for k, (lab, cnt, col) in enumerate(bands):
        total += cnt
        h = cnt * 22
        g = root.add("g", opacity=0)
        g.add("rect", x=x0 + k * 150, y=base_y - h, width=100, height=h, fill=col, opacity=0.85)
        scene.Text(g, x0 + k * 150 + 50, base_y - h - 28, "%d 個" % cnt, size=16, weight=700, fill=col, anchor="middle")
        scene.Text(g, x0 + k * 150 + 50, base_y - h - 10, "×3 色 = %d" % (cnt * 3), size=12, weight=500, fill=GRAY, anchor="middle")
        scene.Text(g, x0 + k * 150 + 50, base_y + 20, lab, size=13, weight=700, fill=INK, anchor="middle")
        g.Show(1.0 + k * 2.4)
    assert total == 14 and sum(c for _, c, _ in bands) * 3 == 42
    root.add("line", x1=120, y1=base_y, x2=660, y2=base_y, stroke="#94a3b8", stroke_width=2)
    scene.TextStack(root, 390, 365, [(0.0, 1.0, "次数ごとの係数の数 (次数 l で 2l+1 個)"), (1.0, 3.4, "L0: 1 個。向きによらない明るさ"), (3.4, 5.8, "L1: 4 個になる(累計)。大まかな明暗の向き"), (5.8, 20, "L2: 9 個(累計)。×3 色で 27 個。ゲームで一般的な次数")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "L0 → L2")
    return dict(name=name, page=G + "gi/probes/sh-storage.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.5, 4.0, 7.0, 9.0])


def ChunkStream():
    name = "chunk-stream"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="カメラが動くと、近いチャンクを読み込み、遠いチャンクを捨てる")
    root = scene.root
    cols_n, rows_n, cs, ox, oy = 10, 5, 62, 80, 80
    radius = 2.2
    cam_x = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    cam_y = 2.0

    def loaded(cx, ci):
        return math.hypot(cx - cam_x[ci], cam_y - 2.0) <= radius

    for r in range(rows_n):
        for c in range(cols_n):
            x, y = ox + c * cs, oy + r * cs
            root.add("rect", x=x, y=y, width=cs - 4, height=cs - 4, fill="#ffffff", stroke="#cbd5e1", stroke_width=1.5)
            ov = root.add("rect", x=x, y=y, width=cs - 4, height=cs - 4, fill=Mix("#bbf7d0", "#22c55e", 0.5), opacity=0)
            state = [loaded(c, ci) if r == 2 or abs(r - 2) <= 2 else False for ci in range(6)]
            state = [math.hypot(c - cam_x[ci], r - cam_y) <= radius for ci in range(6)]
            for ci in range(6):
                t = 1.0 + ci * 1.7
                ov.Set(t, "opacity", 1 if state[ci] else 0)
    cam = root.add("circle", cx=ox + 2.0 * cs + cs / 2 - 2, cy=oy + 2 * cs + cs / 2 - 2, r=9, fill=INK)
    for ci in range(1, 6):
        cam.Ramp(1.0 + (ci - 1) * 1.7 + 0.9, 1.0 + ci * 1.7, "cx", ox + cam_x[ci] * cs + cs / 2 - 2)
    cam.Set(0, "cy", oy + 2 * cs + cs / 2 - 2)
    scene.Text(root, ox, oy - 12, "緑 = 読み込み済みのチャンク（カメラから一定の距離内）", size=13, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 420, [(0.0, 1.0, "カメラの周りだけ、メモリに置く"), (1.0, 5.0, "右へ動く: 前方のチャンクを読み込み、後ろを捨てる"), (5.0, 20, "ワールド全体の大きさに関係なく、メモリ量が一定")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "カメラを右へ")
    return dict(name=name, page=G + "terrain/heightmap-mesh/chunks.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 3.5, 6.0, 9.0])


def SunArc():
    name = "sun-arc"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="時刻から太陽の向きを決める: 1 日で半円を描く")
    root = scene.root
    cx, cy, rad = 390, 300, 230
    root.add("line", x1=cx - rad - 30, y1=cy, x2=cx + rad + 30, y2=cy, stroke="#94a3b8", stroke_width=2)
    arc = "M%d,%d A%d,%d 0 0 1 %d,%d" % (cx - rad, cy, rad, rad, cx + rad, cy)
    root.add("path", d=arc, fill="none", stroke=LIGHT, stroke_width=3, stroke_dasharray="6 6")
    sun = root.add("circle", cx=cx - rad, cy=cy, r=16, fill=AMBER)
    moon = root.add("circle", cx=cx + rad, cy=cy, r=12, fill="#94a3b8", opacity=0)
    n = 48
    prev = 1.0
    for i in range(n + 1):
        f = i / n
        a = math.pi * (1 - f)
        x, y = cx + rad * math.cos(a), cy - rad * math.sin(a)
        t = 1.0 + f * 10.0
        if i == 0:
            sun.Set(t, "cx", x)
            sun.Set(t, "cy", y)
        else:
            sun.Ramp(prev, t, "cx", x)
            sun.Ramp(prev, t, "cy", y)
        prev = t
    moon.Show(11.2)
    scene.Text(root, cx - rad, cy + 22, "日の出（東）", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Text(root, cx + rad, cy + 22, "日没（西）", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Text(root, cx, cy - rad - 20, "正午", size=12, weight=500, fill=GRAY, anchor="middle")
    LiveText(scene, root, 390, 370, 1.0, 11.0, 5, lambda i, f: ["6 時: 地平線(長い影・赤い空)", "9 時: 昇る途中(影は西に長い)", "12 時: 最も高い(影は最短)", "15 時: 下がる途中", "18 時: 地平線に沈む → 月が昇る"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "6 時 → 18 時")
    return dict(name=name, page=G + "atmosphere/sky-models/celestial.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 4.0, 6.0, 9.0])


FIGS = [Fresnel, GgxLobe, Obscurance, FoamDecay, HeightBlend, DispersionDelta, ConstantBias, PeterPanning, DepthBeer, DitherGrid, ClipmapRings, HeightMip, ShStorage, ChunkStream, SunArc]
