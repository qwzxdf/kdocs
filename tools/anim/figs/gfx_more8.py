import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402
from gfx_more4 import Morph, XLabel  # noqa: E402

G = "graphics/"
BEFORE = "## よくあるミス"


def Retarget(info, page):
    info["page"] = page
    return info


def CosFraction():
    name = "cos-weighted-fraction"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="半球から届く光の大半は、真上に近い角度から来る(cos で重みが付く)")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 90.0, 1.05, ylabel="θ 以内から来る光の割合")
    XLabel(scene, ax, "真上からの角度 θ (度)")
    for v in (0, 15, 30, 45, 60, 75, 90):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda a: math.sin(math.radians(a)) ** 2
    ax.Curve(fn, BLUE, width=4, n=90)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 10.0, 0.0, 90.0, n=60)
    assert abs(fn(45) - 0.5) < 1e-9 and abs(fn(60) - 0.75) < 1e-9 and abs(fn(30) - 0.25) < 1e-9
    LiveText(scene, root, 390, 392, 1.0, 10.0, 4, lambda i, f: ["θ = 30 度以内: 光の 25%（半球の面積では 13%）", "θ = 45 度以内: 50%", "θ = 60 度以内: 75%", "残りの 25% は、60〜90 度の浅い角度から来る"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "θ を 0 → 90")
    return dict(name=name, page=G + "ao/theory/from-rendering-equation.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def BlurNoise():
    name = "blur-noise"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="ぼかす範囲を広げると、ノイズは 1/(2r+1) に減る(代わりにボケる)")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 8.0, 1.05, ylabel="ノイズの大きさ（ぼかさない時 = 1）")
    XLabel(scene, ax, "ぼかす半径 r（画素）")
    for v in range(0, 9):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda r: 1 / (2 * r + 1)
    ax.Curve(fn, RED, width=4, n=80)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 10.0, 0.0, 8.0, n=48)
    assert abs(fn(2) - 0.2) < 1e-12 and abs(fn(4) - 1 / 9) < 1e-12
    LiveText(scene, root, 390, 392, 1.0, 10.0, 4, lambda i, f: ["r = 0: ぼかさない。ノイズ 1", "r = 2（5×5 の平均）: ノイズ 0.2 まで下がる", "r = 4（9×9）: 0.11。ただし輪郭がボケ始める", "だから輪郭を保つ、深度を見るぼかしを使う"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "r を 0 → 8")
    return dict(name=name, page=G + "ao/artifacts/noise-flicker.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def BilateralWeight():
    sig = [0.05, 0.1, 0.3, 1.0]
    fns = [lambda d, s=s: math.exp(-(d * d) / (2 * s * s)) for s in sig]
    caps = ["σ = 0.05: 深度が少し違うだけで、重みがほぼ 0（輪郭を厳密に守る）", "σ = 0.1: 近い深度だけを平均する", "σ = 0.3: 段差の大きい所も、少し混ざる", "σ = 1.0: ほぼ普通のぼかし（輪郭を越えて混ざる）"]
    info = Morph("bilateral-weight", "x.md", "深度を見るぼかし: 中心との深度差が大きい画素は、重みを下げる", "中心との深度の差", "平均に使う重み", 1.0, 1.05, fns, caps, color=GREEN, ticks=[0, 0.25, 0.5, 0.75, 1.0])
    return Retarget(info, G + "ao/filtering/pipeline.md")


def HgPhase():
    gs = [0.0, 0.5, 0.76, 0.9]
    hg = lambda a, g: (1 - g * g) / (1 + g * g - 2 * g * math.cos(math.radians(a))) ** 1.5
    fns = [lambda a, g=g: math.log10(hg(a, g)) for g in gs]
    caps = ["g = 0: どの向きにも均等(全方向)。1 を 10 の 0 乗とする", "g = 0.5: 前に少し強い", "g = 0.76: 前方(0 度)が %.0f 倍、後方(180 度)が %.2f 倍。霧・雲でよく使う値" % (hg(0, 0.76), hg(180, 0.76)), "g = 0.9: 前方がとても強い。太陽に向かうと、霞が光る"]
    info = Morph("hg-phase", "x.md", "ヘニエイ・グリーンスタイン: g が大きいほど、前方に強く散乱する(縦軸は 10 の何乗倍か)", "散乱の角度 (度、0 = 進行方向のまま)", "log10(p(θ)·4π)", 180.0, 2.5, fns, caps, color=AMBER, ticks=[0, 45, 90, 135, 180], ymin=-2.0)
    return Retarget(info, G + "atmosphere/scattering/single-scattering.md")


def MultiScatterSum():
    name = "multi-scatter-sum"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="何度も散乱した光を足していく: 1 回だけの 5 分の 1 でも、積み重なる")
    root = scene.root
    rho = 0.8
    orders = [rho ** k for k in range(8)]
    total = sum(orders)
    assert abs(sum(rho ** k for k in range(400)) - 5.0) < 1e-9
    x0, base_y, scale = 90, 320, 60
    acc = 0.0
    for k, v in enumerate(orders):
        x = x0 + k * 74
        h = v * scale * 3.2
        r = root.add("rect", x=x, y=base_y - h, width=60, height=h, fill=(BLUE if k == 0 else AMBER), opacity=0)
        r.Show(1.0 + k * 1.2)
        scene.Text(root, x + 30, base_y - h - 8, "%.2f" % v, size=12, weight=700, fill=GRAY, anchor="middle", opacity=0).Show(1.0 + k * 1.2)
        scene.Text(root, x + 30, base_y + 20, "%d 回" % (k + 1), size=12, weight=700, fill=INK, anchor="middle")
        acc += v
    root.add("line", x1=x0 - 10, y1=base_y, x2=x0 + 8 * 74, y2=base_y, stroke="#94a3b8", stroke_width=2)
    cum = [(1.0 + k * 1.2, sum(orders[:k + 1])) for k in range(8)]
    items = [(0.0, 1.0, "アルベド(反射する割合) 0.8 の媒質。散乱 1 回目の光を 1 とする")] + [(1.0 + k * 1.2, 1.0 + (k + 1) * 1.2 if k < 7 else 99, "%d 回目まで足した合計: %.2f" % (k + 1, sum(orders[:k + 1]))) for k in range(8)]
    scene.TextStack(root, 390, 380, items, size=14, fill=INK, anchor="middle")
    scene.Text(root, 390, 405, "無限に足すと 1/(1−0.8) = 5。1 回だけの計算では 8 割以上の光が足りない", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "散乱の回数を増やす")
    return dict(name=name, page=G + "atmosphere/scattering/multiple-scattering.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def EmaConverge():
    al = [0.5, 0.2, 0.1, 0.05]
    fns = [lambda n, a=a: 1 - (1 - a) ** n for a in al]
    half = [math.ceil(math.log(0.1) / math.log(1 - a)) for a in al]
    caps = ["α = %.2f: 約 %d フレームで、90%% 収束。ただし、揺れが残りやすい" % (al[0], half[0]), "α = %.2f: 約 %d フレーム" % (al[1], half[1]), "α = %.2f: 約 %d フレーム。よく使う値" % (al[2], half[2]), "α = %.2f: 約 %d フレーム。滑らかだが、反応が遅い(残像)" % (al[3], half[3])]
    assert half == [4, 11, 22, 45]
    info = Morph("ema-converge", "x.md", "履歴との混ぜ方 lerp(履歴, 今回, α): α が小さいほど滑らかで、収束は遅い", "経過フレーム", "新しい値の反映率", 60.0, 1.05, fns, caps, color=PURPLE, ticks=[0, 10, 20, 30, 40, 50, 60])
    return Retarget(info, G + "atmosphere/volumetric-fog/temporal.md")


def SsrEdgeFade():
    ws = [0.02, 0.08, 0.15, 0.3]
    fns = [lambda x, w=w: min(1.0, min(x, 1 - x) / w) for w in ws]
    caps = ["幅 0.02: 端のぎりぎりまで反射を出す。切れ目が目立つ", "幅 0.08: 端でなだらかに消える", "幅 0.15: より広く消える", "幅 0.3: 画面の 30% が薄まる。反射が弱く見える"]
    info = Morph("ssr-fade-width", "x.md", "画面の端で反射を薄めて、画面外の情報が無い切れ目を、目立たなくする", "画面上の位置（0 = 左端、1 = 右端）", "反射の強さ", 1.0, 1.05, fns, caps, color=BLUE, ticks=[0, 0.25, 0.5, 0.75, 1])
    return Retarget(info, G + "reflections/ssr-basics/color-fade.md")


def BuoyancyDraft():
    name = "buoyancy-draft"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="浮力は沈んだ体積に比例し、重さと釣り合う深さで止まる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 1.0, 1.4, ylabel="力（重さ = 1 とする）")
    XLabel(scene, ax, "沈んでいる深さ ÷ 箱の高さ")
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "%g" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    density = 0.6
    buoy = lambda d: min(d, 1.0) / density
    ax.Curve(lambda d: 1.0, RED, width=3, dash="6 5")
    scene.Text(root, ax.X(0.02), ax.Y(1.0) - 10, "重さ（下向き）", size=12, weight=700, fill=RED)
    ax.Curve(buoy, BLUE, width=4, n=80)
    scene.Text(root, ax.X(0.15), ax.Y(buoy(0.15)) - 14, "浮力（上向き）", size=12, weight=700, fill=BLUE)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, buoy, 1.0, 8.0, 0.0, 0.6, n=48)
    stay = root.add("circle", cx=ax.X(0.6), cy=ax.Y(buoy(0.6)), r=10, fill="none", stroke=GREEN, stroke_width=4, opacity=0)
    stay.Show(8.0)
    assert abs(buoy(0.6) - 1.0) < 1e-12
    scene.TextStack(root, 390, 392, [(0.0, 1.0, "箱の密度が、水の 0.6 倍だとする"), (1.0, 4.0, "沈めるほど、押し返す力が増える"), (4.0, 8.0, "浮力 < 重さ: まだ沈む"), (8.0, 20, "深さ 0.6 で浮力 = 重さ → 釣り合って止まる(緑の丸)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "沈める")
    return dict(name=name, page=G + "water/interaction/buoyancy.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.5])


def WeightedPick():
    name = "weighted-pick"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="重み付き抽選: 重みを並べた帯に、乱数で矢を刺す")
    root = scene.root
    items = [("ノーマル", 50, GRAY), ("レア", 30, BLUE), ("エピック", 15, PURPLE), ("伝説", 5, AMBER)]
    total = sum(w for _, w, _ in items)
    assert total == 100
    x0, w0, y = 70, 640, 150
    acc = 0
    spans = []
    for nm, w, col in items:
        sx = x0 + acc / total * w0
        sw = w / total * w0
        root.add("rect", x=sx, y=y, width=sw, height=50, fill=col, opacity=0.9)
        scene.Text(root, sx + sw / 2, y + 22, nm, size=12 if w > 10 else 10, weight=700, fill="#ffffff", anchor="middle")
        scene.Text(root, sx + sw / 2, y + 40, "%d" % w, size=12, weight=700, fill="#ffffff", anchor="middle")
        spans.append((acc, acc + w, nm))
        acc += w
    rs = [12, 63, 97]
    res = []
    for r in rs:
        for a, b, nm in spans:
            if a <= r < b:
                res.append(nm)
    assert res == ["ノーマル", "レア", "伝説"]
    for k, r in enumerate(rs):
        t0 = 1.0 + k * 3.8
        t1 = t0 + 3.8 if k < 2 else None
        xx = x0 + r / total * w0
        g = root.add("g", opacity=0)
        Arrow = g.add("line", x1=xx, y1=100, x2=xx, y2=146, stroke=RED, stroke_width=4, marker_end=scene.marker)
        scene.Text(g, xx, 92, "乱数 %d" % r, size=13, weight=700, fill=RED, anchor="middle")
        g.Show(t0, t1)
    scene.TextStack(root, 390, 280, [(0.0, 1.0, "重みの合計 100 の帯を、重みの長さで分ける")] + [(1.0 + k * 3.8, 1.0 + (k + 1) * 3.8 if k < 2 else 99, "0〜99 の乱数 %d → %s" % (rs[k], res[k])) for k in range(3)], size=15, fill=INK, anchor="middle")
    scene.Text(root, 390, 330, "確率 = 重み ÷ 合計。伝説は 5%、ノーマルは 50%", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "乱数を 3 回引く")
    return dict(name=name, page="gamemath/random.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.5, 5.0, 9.0, 12.0])


def ParentChild():
    name = "scene-parent-child"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="親を動かすと、子も付いてくる: ワールド位置 = 親の位置 + 子の相対位置")
    root = scene.root
    y = 180
    root.add("line", x1=60, y1=y + 50, x2=720, y2=y + 50, stroke=LIGHT, stroke_width=1.5)
    parent = root.add("rect", x=100, y=y - 20, width=64, height=64, fill=BLUE, opacity=0.9)
    child = root.add("rect", x=100 + 140, y=y - 5, width=34, height=34, fill=AMBER, opacity=0.95)
    link = root.add("line", x1=132, y1=y + 12, x2=257, y2=y + 12, stroke=GRAY, stroke_width=2, stroke_dasharray="5 4")
    pt = scene.Text(root, 132, y - 30, "親", size=13, weight=700, fill=BLUE, anchor="middle")
    ct = scene.Text(root, 257, y - 30, "子", size=13, weight=700, fill=AMBER, anchor="middle")
    parent.Ramp(4.0, 8.0, "x", 100 + 360)
    child.Ramp(4.0, 8.0, "x", 100 + 140 + 360)
    link.Ramp(4.0, 8.0, "x1", 132 + 360)
    link.Ramp(4.0, 8.0, "x2", 257 + 360)
    ct.Ramp(4.0, 8.0, "x", 257 + 360)
    pt.Ramp(4.0, 8.0, "x", 132 + 360)
    scene.TextStack(root, 390, 320, [(0.0, 1.0, "子は「親から右へ 140」という相対位置を持つ"), (1.0, 4.0, "親が x = 132 にいれば、子は 132 + 140 = 272 に表示される"), (4.0, 8.0, "親を右へ動かす。子の相対位置は、そのまま"), (8.0, 20.0, "親が 492 に来た → 子は 492 + 140 = 632。子のデータは、書き換えていない")], size=14, fill=INK, anchor="middle")
    scene.Note(4.0, name, "親を動かす")
    return dict(name=name, page="engine/scene.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.0, 3.0, 6.0, 10.0])


FIGS = [CosFraction, BlurNoise, BilateralWeight, HgPhase, MultiScatterSum, EmaConverge, SsrEdgeFade, BuoyancyDraft, WeightedPick, ParentChild]
