import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_gi import Lcg  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


def Rgbh(c):
    return Hex([255 * max(0.0, min(1.0, v)) for v in c])


def Enc(v):
    return max(0.0, min(1.0, v)) ** (1 / 2.2)


def Strip(st, root, sc, x0, y, cols, cw, t0, dt, lab=None, lc=GRAY, ch=30.0, stroke="#94a3b8"):
    if lab:
        sc.Text(root, x0, y - 4, lab, size=13, weight=700, fill=lc)
    g = Grid(st, x0, y, len(cols), 1, cw, base="#e5e7eb", stroke=stroke, cell_h=ch)
    for i, c in enumerate(cols):
        g.Paint(i, 0, t0 + i * dt, c if isinstance(c, str) else Rgbh(c))
    g.Flush()
    return g


# ===================================================================== basic adjustments
def BasicAdjustments():
    name = "basic-adjustments"
    st = Stage(name, "基本の補正: 露出・コントラスト・彩度。順番を変えると、結果が変わる", duration=21.0, subtitle="6 色のパレットに、補正を、1 つずつ足す。各段階の「平均の明るさ」と「平均の彩度」を、計算する")
    sc, root = st.scene, st.root
    pal = [(0.8, 0.25, 0.2), (0.9, 0.6, 0.15), (0.3, 0.65, 0.25), (0.2, 0.5, 0.8), (0.5, 0.3, 0.7), (0.5, 0.5, 0.5)]
    lum = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    def sat(c):
        mx, mn = max(c), min(c)
        return 0 if mx < 1e-9 else (mx - mn) / mx
    def Expo(c, e):
        return tuple(v * 2 ** e for v in c)
    def Contrast(c, k, piv=0.18):
        return tuple(max(0.0, piv * (v / piv) ** k) for v in c)
    def Sat(c, k):
        l = lum(c)
        return tuple(max(0.0, l + (v - l) * k) for v in c)
    steps = [("元の色", lambda c: c), ("+ 露出 +0.5 段", lambda c: Expo(c, 0.5)), ("+ コントラスト 1.3", lambda c: Contrast(Expo(c, 0.5), 1.3)), ("+ 彩度 1.4", lambda c: Sat(Contrast(Expo(c, 0.5), 1.3), 1.4))]
    outs = [[f(c) for c in pal] for _, f in steps]
    ml = [sum(lum(c) for c in o) / 6 for o in outs]
    ms = [sum(sat(c) for c in o) / 6 for o in outs]
    # 順番を入れ替え
    A = [Sat(Contrast(Expo(c, 0.5), 1.3), 1.4) for c in pal]
    B = [Contrast(Sat(Expo(c, 0.5), 1.4), 1.3) for c in pal]
    diff = sum(abs(a[k] - b[k]) for a, b in zip(A, B) for k in range(3)) / 18
    assert ms[3] > ms[0] and ml[1] > ml[0] and diff > 0.005
    CW, X0 = 78.0, 70.0
    t0, per = 1.5, 3.8
    for m, (lab, f) in enumerate(steps):
        y = 108 + m * 70
        Strip(st, root, sc, X0, y, [Enc(1.0) and tuple(Enc(v) for v in c) for c in outs[m]], CW, t0 + m * per, 0.3, lab, [GRAY, BLUE, PURPLE, RED][m], 40.0)
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 2.0)
        sc.Text(g, X0 + 6 * CW + 14, y + 16, "平均の明るさ %.3f" % ml[m], size=12, weight=700, fill=TEXT)
        sc.Text(g, X0 + 6 * CW + 14, y + 36, "平均の彩度 %.3f" % ms[m], size=12, weight=700, fill=TEXT)
    t_o = t0 + 4 * per
    st.Panel(30, 392, 900, 90, "順番を入れ替えると(コントラスト → 彩度 と、 彩度 → コントラスト)", color=PURPLE)
    for k, (lab, cols) in enumerate([("コントラスト → 彩度", A), ("彩度 → コントラスト", B)]):
        x = 50 + k * 440
        sc.Text(root, x, 430, lab, size=12, weight=700, fill=TEXT, opacity=0).Show(t_o)
        g = Grid(st, x, 436, 6, 1, 40.0, base="#e5e7eb", stroke="#94a3b8", cell_h=24.0)
        for i, c in enumerate(cols):
            g.Paint(i, 0, t_o + i * 0.2, Rgbh([Enc(v) for v in c]))
        g.Flush()
    sc.Text(root, 700, 466, "色の差(平均)%.3f" % diff, size=13, weight=700, fill=RED, opacity=0).Show(t_o + 2.0)
    st.Caption(30, 534, [(0.0, t0, "補正は、色に順番に掛けていく"), (t0, t_o, "露出で明るく、コントラストで、明暗の差を広げ、彩度で、鮮やかにする"), (t_o, 99, "順番を変えると、結果が少し違う。決まった順番で、作る")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "補正", "平均の彩度 %.3f → %.3f、順番の違い %.3f" % (ms[0], ms[3], diff))
    return Build(st, name, "graphics/postprocess/color-grading/basic-adjustments.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== LUT lookup
def ColorLutLookup():
    name = "color-lut-lookup"
    st = Stage(name, "LUT(色の対応表): 入力の色から、出力の色を表で引く。表が粗くても、間を補間してなめらかにする", duration=21.0, subtitle="S 字の色補正カーブを、8・16・32 個の表で近似する。入力 64 通りを、最も近い値で引く場合と、補間する場合で比べる")
    sc, root = st.scene, st.root
    f = lambda x: x * x * (3 - 2 * x)
    def Table(N):
        return [f(i / (N - 1)) for i in range(N)]
    def Near(tbl, x):
        N = len(tbl)
        return tbl[min(N - 1, max(0, int(round(x * (N - 1)))))]
    def Lin(tbl, x):
        N = len(tbl)
        p = x * (N - 1)
        i = min(N - 2, int(p))
        t = p - i
        return tbl[i] * (1 - t) + tbl[i + 1] * t
    xs = [k / 63 for k in range(64)]
    Ns = [8, 16, 32]
    res = []
    for N in Ns:
        tb = Table(N)
        en = sum(abs(Near(tb, x) - f(x)) for x in xs) / 64
        el = sum(abs(Lin(tb, x) - f(x)) for x in xs) / 64
        res.append((N, en, el))
    assert all(e[2] < e[1] for e in res) and res[0][2] > res[2][2]
    X0, W = 70.0, 520.0
    st.Panel(30, 96, 580, 270, "① 色補正カーブ(縦 = 出力)", color=BLUE)
    XX = lambda x: X0 + x * W
    YY = lambda v: 340 - v * 200
    root.add("path", d=Poly([(XX(x), YY(f(x))) for x in xs]), fill="none", stroke=GRAY, stroke_width=2.5, stroke_dasharray="5 4")
    t0, per = 1.5, 6.0
    for m, (N, en, el) in enumerate(res):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        tb = Table(N)
        g.add("path", d=Poly([(XX(x), YY(Near(tb, x))) for x in xs]), fill="none", stroke=RED, stroke_width=3)
        g.add("path", d=Poly([(XX(x), YY(Lin(tb, x))) for x in xs]), fill="none", stroke=GREEN, stroke_width=3.5)
        for i in range(N):
            g.add("circle", cx=R(XX(i / (N - 1))), cy=R(YY(tb[i])), r=4.5, fill=INK)
        sc.Text(g, 50, 128, "表の大きさ %d 個" % N, size=20, weight=700, fill=PURPLE)
    st.Legend(70, 354, [(GRAY, "本当のカーブ"), (RED, "最も近い値で引く"), (GREEN, "間を補間する")])
    st.Panel(640, 96, 290, 270, "② 本当のカーブとのずれ", color=PURPLE)
    for m, (N, en, el) in enumerate(res):
        y = 140 + m * 70
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.6)
        sc.Text(g, 656, y, "表 %d 個" % N, size=14, weight=700, fill=INK)
        sc.Text(g, 656, y + 22, "最も近い値: %.4f" % en, size=13, weight=700, fill=RED)
        sc.Text(g, 656, y + 42, "補間: %.4f" % el, size=13, weight=700, fill=GREEN)
    st.Text(40, 400, "表の個数:", size=15)
    st.Counter(150, 404, [(t0 + m * per, N) for m, (N, _, _) in enumerate(res)], size=26, fill=PURPLE)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.4, 40, 430, 880, 70, [("補間すると、8 個の表でも、最も近い値の 32 個より、ずれが小さい(%.4f と %.4f)" % (res[0][2], res[2][1]), 14, "#1e3a8a"), ("実際は 3D の表(32×32×32 = %s 個)を、GPU の補間で引く。1 回の読み込みで済む" % Fmt(32 ** 3), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "どんな複雑な補正も、「入力 → 出力」の表にできる"), (t0, t_e, "表が粗くても、間を補間すれば、なめらか"), (t_e, 99, "画面の全画素で、表を 1 回引くだけ。どれだけ複雑でも、コストは一定")], size=14, fill=MUTED, weight=500)
    for m, (N, en, el) in enumerate(res):
        st.Note(t0 + m * per, "LUT", "表 %d 個: 最も近い値 %.4f / 補間 %.4f" % (N, en, el))
    return Build(st, name, "graphics/postprocess/color-grading/index.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== Lift Gamma Gain
def ColorLggCurves():
    name = "color-lgg-curves"
    st = Stage(name, "リフト・ガンマ・ゲイン: 暗い所(リフト)・中間(ガンマ)・明るい所(ゲイン)を、別々に動かす", duration=21.0, subtitle="入力 0〜1 → 出力。3 つのつまみを、1 つずつ動かして、暗部・中間・明部が、どれだけ動くかを計算する")
    sc, root = st.scene, st.root
    def Out(x, lift, gamma, gain):
        v = gain * (x + lift * (1 - x))
        return max(0.0, v) ** (1 / gamma)
    xs = [k / 60 for k in range(61)]
    sets = [("基準", 0.0, 1.0, 1.0, GRAY), ("リフト +0.1", 0.1, 1.0, 1.0, BLUE), ("ガンマ 1.5", 0.0, 1.5, 1.0, GREEN), ("ゲイン 0.8", 0.0, 1.0, 0.8, RED)]
    pts = [0.1, 0.5, 0.9]
    delta = []
    for lab, l, g_, ga, c in sets:
        delta.append([Out(p, l, g_, ga) - p for p in pts])
    assert abs(delta[1][0]) > abs(delta[1][2]) and abs(delta[2][1]) > abs(delta[2][0]) and abs(delta[3][2]) > abs(delta[3][0])
    X0, W = 70.0, 420.0
    st.Panel(30, 96, 480, 340, "曲線(青 = リフト、緑 = ガンマ、赤 = ゲイン)", color=PURPLE)
    XX = lambda x: X0 + x * W
    YY = lambda v: 410 - v * 270
    root.add("path", d=Poly([(XX(x), YY(x)) for x in xs]), fill="none", stroke=GRAY, stroke_width=2, stroke_dasharray="5 4")
    for p in pts:
        root.add("line", x1=R(XX(p)), y1=140, x2=R(XX(p)), y2=410, stroke=LIGHT, stroke_width=1.3, stroke_dasharray="3 4")
    sc.Text(root, XX(0.1), 426, "暗部", size=11, weight=700, fill=MUTED, anchor="middle")
    sc.Text(root, XX(0.5), 426, "中間", size=11, weight=700, fill=MUTED, anchor="middle")
    sc.Text(root, XX(0.9), 426, "明部", size=11, weight=700, fill=MUTED, anchor="middle")
    t0, per = 1.5, 4.8
    for m in range(1, 4):
        lab, l, g_, ga, c = sets[m]
        pth = root.add("path", d=Poly([(XX(x), YY(Out(x, l, g_, ga))) for x in xs]), fill="none", stroke=c, stroke_width=3.5, opacity=0)
        pth.Show(t0 + (m - 1) * per)
    st.Panel(540, 96, 390, 340, "それぞれが動かした量(出力 − 入力)", color=BLUE)
    for m in range(1, 4):
        lab, l, g_, ga, c = sets[m]
        g = root.add("g", opacity=0)
        g.Show(t0 + (m - 1) * per + 0.5)
        sc.Text(g, 560, 134 + (m - 1) * 100, lab, size=16, weight=700, fill=c)
        for k, (pn, d) in enumerate(zip(["暗部(0.1)", "中間(0.5)", "明部(0.9)"], delta[m])):
            w = abs(d) / 0.25 * 160
            g.add("rect", x=680, y=146 + (m - 1) * 100 + k * 20, width=R(max(w, 2)), height=14, fill=c if d >= 0 else "#94a3b8", opacity=0.85)
            sc.Text(g, 566, 158 + (m - 1) * 100 + k * 20, pn, size=11, weight=500, fill=TEXT)
            sc.Text(g, 680 + w + 6, 158 + (m - 1) * 100 + k * 20, "%+.3f" % d, size=11, weight=700, fill=c)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 40, 452, 880, 60, [("リフトは暗部を、ガンマは中間を、ゲインは明部を、いちばん動かす。互いに、他をあまり動かさない", 14, "#1e3a8a"), ("3 つのつまみで、「暗部を青く、明部を橙に」といった、色の演出が作れる(RGB それぞれに設定)", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "明るさを、全体で、一括して動かすのではなく、明るさの範囲ごとに動かす"), (t0, t_e, "3 つのつまみは、効く範囲が違う"), (t_e, 99, "色ごとにつまみを持たせると、色味のグレーディングになる")], size=14, fill=MUTED, weight=500)
    for m in range(1, 4):
        st.Note(t0 + (m - 1) * per, "LGG", "%s: 暗 %+.3f / 中 %+.3f / 明 %+.3f" % ((sets[m][0],) + tuple(delta[m])))
    return Build(st, name, "graphics/postprocess/color-grading/lift-gamma-gain.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== LUT half texel
def LutHalfTexel():
    name = "lut-half-texel"
    st = Stage(name, "LUT の半テクセル補正: テクスチャの座標 0 と 1 は、端のテクセルの「中心」ではない。補正しないと、表全体がずれる", duration=20.0, subtitle="16 個の表(テクセル)を、GPU の補間で引く。入力 0 〜 1 を、そのまま座標にした場合と、補正した場合の誤差")
    sc, root = st.scene, st.root
    N = 16
    f = lambda x: x ** 1.0 * 0.8 + 0.2 * math.sin(math.pi * x) * 0.0 + (x * x * (3 - 2 * x)) * 0.2
    tb = [f(i / (N - 1)) for i in range(N)]
    def Fetch(u):
        # テクセル中心は (i + 0.5) / N。範囲外は端にクランプ
        p = u * N - 0.5
        i0 = int(math.floor(p))
        t = p - i0
        g = lambda i: tb[min(N - 1, max(0, i))]
        return g(i0) * (1 - t) + g(i0 + 1) * t
    xs = [k / 80 for k in range(81)]
    plain = [Fetch(x) for x in xs]
    corr = [Fetch(x * (N - 1) / N + 0.5 / N) for x in xs]
    true = [f(x) for x in xs]
    e_p = [abs(a - b) for a, b in zip(plain, true)]
    e_c = [abs(a - b) for a, b in zip(corr, true)]
    ends = lambda e: max(e)
    assert ends(e_p) > 0.01 and ends(e_c) < ends(e_p) / 3, (ends(e_p), ends(e_c))
    X0, W = 70.0, 600.0
    st.Panel(30, 96, 660, 260, "① 表の値(黒い点 = 各テクセルの中心)と、引いた値", color=BLUE)
    XX = lambda x: X0 + x * W
    YY = lambda v: 330 - v * 200
    root.add("path", d=Poly([(XX(x), YY(v)) for x, v in zip(xs, true)]), fill="none", stroke=GRAY, stroke_width=2.5, stroke_dasharray="5 4")
    for i in range(N):
        root.add("circle", cx=R(XX((i + 0.5) / N)), cy=R(YY(tb[i])), r=4, fill=INK)
    t0, per = 1.5, 5.0
    pp = root.add("path", d=Poly([(XX(x), YY(v)) for x, v in zip(xs, plain)]), fill="none", stroke=RED, stroke_width=3.5, opacity=0)
    pc = root.add("path", d=Poly([(XX(x), YY(v)) for x, v in zip(xs, corr)]), fill="none", stroke=GREEN, stroke_width=3.5, opacity=0)
    pp.Show(t0)
    pc.Show(t0 + per)
    st.Legend(80, 124, [(GRAY, "本当のカーブ"), (RED, "そのまま 0〜1 を座標に"), (GREEN, "補正: u × (N−1)/N + 0.5/N")])
    st.Panel(710, 96, 220, 260, "最大の誤差", color=RED)
    for k, (lab, e, c) in enumerate([("そのまま", ends(e_p), RED), ("補正あり", ends(e_c), GREEN)]):
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per + 1.0)
        sc.Text(g, 726, 140 + k * 70, lab, size=14, weight=700, fill=c)
        sc.Text(g, 726, 170 + k * 70, "%.4f" % e, size=22, weight=700, fill=c)
    st.Panel(30, 376, 900, 100, "クランプと補間の仕組み", color=PURPLE)
    st.Text(50, 412, "座標 0 は、最初のテクセルの「左端」。中心は 0.5/16 = %.4f の位置" % (0.5 / N), size=14, weight=700, fill=TEXT)
    st.Text(50, 440, "座標 0〜1 を、そのまま、テクセル 0〜15 の位置に使うと、表全体が、少し伸びて(縮んで)引かれる。中間の色が、本来の値と、ずれる", size=13, weight=500, fill=TEXT)
    st.Text(50, 462, "補正は、入力を、最初と最後のテクセルの中心の間に押し込む", size=13, weight=700, fill=GREEN)
    t_e = t0 + 2 * per
    st.Box(t_e, 560, 486, 370, 40, [("補正しないと、中間の明るさが、わずかにずれる", 13, "#991b1b")], RED, "#fef2f2")
    st.Caption(30, 534, [(0.0, t0, "LUT を引くとき、入力の 0〜1 を、そのまま座標にしてはいけない"), (t0, t0 + per, "そのまま引くと、中間で、ずれる"), (t0 + per, t_e, "半テクセルぶん、内側へ寄せると、ぴったり合う"), (t_e, 99, "3D LUT でも、同じ補正をする(3 軸すべて)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "半テクセル", "最大の誤差: そのまま %.4f / 補正 %.4f" % (ends(e_p), ends(e_c)))
    return Build(st, name, "graphics/postprocess/color-grading/lut-3d.md", BEFORE, [2.0, 4.0, 7.0, 11.0, 15.0, 19.0])


# ===================================================================== LUT blend zones
def LutBlendZones():
    name = "lut-blend-zones"
    st = Stage(name, "場所ごとの色補正: 2 つの LUT を、プレイヤーの位置で、なめらかに混ぜる", duration=21.0, subtitle="洞窟(青く暗い補正)から、野外(暖かく明るい補正)へ歩く。中間の灰色のパレットの見え方を、位置ごとに計算する")
    sc, root = st.scene, st.root
    cave = lambda c: tuple(min(1.0, v * g) for v, g in zip(c, (0.65, 0.8, 1.05)))
    out = lambda c: tuple(min(1.0, v * g) for v, g in zip(c, (1.15, 1.02, 0.85)))
    pal = [(0.5, 0.5, 0.5), (0.8, 0.3, 0.25), (0.3, 0.6, 0.3), (0.3, 0.45, 0.8)]
    smooth = lambda t: t * t * (3 - 2 * t)
    zone = (14.0, 34.0)
    def W(x):
        return smooth(max(0.0, min(1.0, (x - zone[0]) / (zone[1] - zone[0]))))
    def Blend(c, x):
        w = W(x)
        a, b = cave(c), out(c)
        return tuple(a[k] * (1 - w) + b[k] * w for k in range(3))
    n = 48
    # 上: 通路
    st.Panel(30, 96, 900, 90, "① 通路(左 = 洞窟、右 = 野外)。黄色の帯 = 混ぜる区間", color=BLUE)
    root.add("rect", x=R(60 + zone[0] * 17), y=114, width=R((zone[1] - zone[0]) * 17), height=60, fill="#fde68a", opacity=0.5)
    for i in range(n):
        w = W(i + 0.5)
        root.add("rect", x=R(60 + i * 17), y=150, width=16.5, height=18, fill=Mix("#334155", "#fbbf24", w))
    pl = root.add("circle", cx=R(60 + 4 * 17), cy=130, r=9, fill=INK)
    xs_p = [4, 14, 24, 34, 44]
    t0, per = 1.5, 3.4
    for m in range(1, 5):
        pl.Ramp(t0 + (m - 1) * per + 2.0, t0 + m * per, "cx", R(60 + xs_p[m] * 17))
    # 下: パレット
    for m, x in enumerate(xs_p):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + 0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per - 0.3 if m > 0 else 0.0, t0 + (m + 1) * per - 0.3 if m < 4 else None)
        w = W(x)
        for k, c in enumerate(pal):
            col = Blend(c, x)
            g.add("rect", x=R(60 + k * 120), y=216, width=108, height=90, fill=Rgbh([Enc(v) for v in col]), stroke="#94a3b8", stroke_width=1.5)
        sc.Text(g, 60, 330, "位置 %d: 洞窟の LUT の割合 %.2f / 野外の LUT の割合 %.2f" % (x, 1 - w, w), size=16, weight=700, fill=PURPLE)
        g2 = pal[0]
        gcol = Blend(g2, x)
        sc.Text(g, 60, 358, "灰色の見え方(R, G, B): %.2f, %.2f, %.2f" % tuple(gcol), size=14, weight=700, fill=TEXT)
    sc.Text(root, 60, 205, "色見本(灰・赤・緑・青)", size=13, weight=700, fill=MUTED)
    sc.Text(root, 560, 250, "灰色の R − B(暖かさ):", size=14, weight=700, fill=TEXT)
    st.Counter(560, 290, [(t0 + m * per - 0.3 + 0.01 if m else 0.0, int(round(100 * (Blend(pal[0], x)[0] - Blend(pal[0], x)[2])))) for m, x in enumerate(xs_p)], size=30, fill=RED)
    st.Text(630, 290, "(×0.01。マイナス = 青い、プラス = 暖かい)", size=12, weight=500, fill=MUTED)
    jump = max(abs(Blend(pal[0], x + 1)[0] - Blend(pal[0], x)[0]) for x in range(0, 47))
    sharp = abs(cave(pal[0])[0] - out(pal[0])[0])
    assert jump < sharp * 0.2
    t_e = t0 + 5 * per
    st.Box(t_e - 0.5, 40, 400, 880, 90, [("1 歩ごとの色の変化は、最大 %.3f(なめらか)。一気に切り替えると、一度に %.2f 変わる(ちらつき)" % (jump, sharp), 15, "#1e3a8a"), ("2 つの LUT を混ぜる重みを、位置から計算する(smoothstep)。LUT 自体を混ぜるか、結果を混ぜる", 13, TEXT), ("場所ごとに LUT を持つと、同じゲームでも、場面の雰囲気を作り分けられる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "洞窟と野外で、別の色補正をしたい"), (t0, t_e, "歩きながら、2 つの LUT の重みを、少しずつ入れ替える"), (t_e, 99, "境目で、色が急に変わらない")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ブレンド", "1 歩の最大変化 %.3f(切り替えなら %.2f)" % (jump, sharp))
    return Build(st, name, "graphics/postprocess/color-grading/lut-authoring.md", BEFORE, [2.0, 5.0, 8.5, 12.0, 15.5, 20.0])


# ===================================================================== white balance
def WhiteBalance():
    name = "white-balance"
    st = Stage(name, "ホワイト バランス: 暖色の光の下の「白」を、本当の白に戻す。直しすぎると、逆の色が付く", duration=20.0, subtitle="灰色の面と、赤い面を、オレンジ色の光(R:G:B = 1 : 0.78 : 0.5)で照らす。補正の強さを 0 → 0.5 → 1.0 → 1.5 に変える")
    sc, root = st.scene, st.root
    light = (1.0, 0.78, 0.5)
    surf = [("灰色", (0.5, 0.5, 0.5)), ("白", (0.9, 0.9, 0.9)), ("赤", (0.8, 0.2, 0.15)), ("青", (0.2, 0.35, 0.8))]
    seen = [tuple(a * b for a, b in zip(c, light)) for _, c in surf]
    gains = lambda k: tuple((1.0 / l) ** k for l in light)
    def Apply(c, k):
        g = gains(k)
        m = max(g[1], 1e-9)
        return tuple(min(1.0, v * x / g[1] * 1.0) for v, x in zip(c, g))
    ks = [0.0, 0.5, 1.0, 1.5]
    outs = [[Apply(s, k) for s in seen] for k in ks]
    cast = lambda c: (c[0] - c[2]) / max(1e-9, (c[0] + c[1] + c[2]) / 3)
    casts = [cast(o[0]) for o in outs]
    assert abs(casts[2]) < 1e-9 and casts[0] > 0.3 and casts[3] < 0
    CW, X0 = 110.0, 90.0
    t0, per = 1.5, 4.2
    for m, k in enumerate(ks):
        y = 108 + m * 72
        sc.Text(root, X0 - 8, y + 28, "補正 %.1f" % k, size=14, weight=700, fill=[GRAY, BLUE, GREEN, RED][m], anchor="end")
        g = Grid(st, X0, y, 4, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=56.0)
        for i, c in enumerate(outs[m]):
            g.Paint(i, 0, t0 + m * per, Rgbh([Enc(v) for v in c]))
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + 0.5)
        sc.Text(gx, X0 + 4 * CW + 16, y + 20, "灰色の色かぶり %+.2f" % casts[m], size=14, weight=700, fill=(GREEN if abs(casts[m]) < 0.05 else RED))
        sc.Text(gx, X0 + 4 * CW + 16, y + 42, ["暖かすぎる(オレンジ)", "まだ少し暖かい", "灰色が、灰色に戻った", "直しすぎ(青っぽい)"][m], size=12, weight=500, fill=MUTED)
    for i, (lab, _) in enumerate(surf):
        sc.Text(root, X0 + i * CW + CW / 2, 98, lab, size=13, weight=700, fill=INK, anchor="middle")
    st.Text(40, 420, "灰色の「色かぶり」(R − B):", size=14)
    st.Counter(260, 424, [(t0 + m * per + 0.5, int(round(100 * casts[m]))) for m in range(4)], size=26, fill=RED)
    st.Text(310, 424, "(×0.01。0 が理想)", size=12, weight=500, fill=MUTED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.4, 440, 410, 490, 90, [("補正 1.0 で、灰色が灰色に戻る。ほかの色も、本来の色に近づく", 14, "#166534"), ("補正 1.5 では、逆の色(青)が付く。ゲームでは、演出で、わざと暖かさを残すことが多い", 12, MUTED), ("補正 = 光の色の逆数を、R・G・B に掛ける", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "暖かい光の下では、白い物も、オレンジ色に見える"), (t0, t_e, "光の色の逆の倍率を掛けると、白が白に戻る"), (t_e, 99, "直しすぎると、逆の色が付く")], size=14, fill=MUTED, weight=500)
    for m, k in enumerate(ks):
        st.Note(t0 + m * per, "WB", "補正 %.1f: 灰色の色かぶり %+.2f" % (k, casts[m]))
    return Build(st, name, "graphics/postprocess/color-grading/white-balance.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


# ===================================================================== Cel ramp
def CelRamp():
    name = "cel-ramp"
    st = Stage(name, "セル シェーディング: N·L を、段に区切ると、アニメ調の影になる。段数でタッチが変わる", duration=20.0, subtitle="球の断面(光は左上)。N·L を 2・3・4 段に区切って塗る。なめらかな陰影と、どれだけ違うかを計算する")
    sc, root = st.scene, st.root
    n = 48
    ndl = [max(0.0, math.cos(math.radians(-80 + 160 * (i + 0.5) / n - 35))) for i in range(n)]
    def Quant(v, steps, th):
        k = sum(1 for t in th if v >= t)
        return k / (len(th))
    sets = [("なめらか(通常)", None, GRAY), ("2 段", [0.35], RED), ("3 段", [0.2, 0.6], GREEN), ("4 段", [0.15, 0.4, 0.7], BLUE)]
    vals = [[v for v in ndl]]
    errs = [0.0]
    for lab, th, col in sets[1:]:
        q = [Quant(v, len(th) + 1, th) * (1.0) for v in ndl]
        vals.append(q)
        errs.append(sum(abs(a - b) for a, b in zip(q, ndl)) / n)
    nb = [1 + sum(1 for i in range(1, n) if abs(vals[m][i] - vals[m][i - 1]) > 1e-9) for m in range(4)]
    assert errs[1] > errs[3]
    CW, X0 = 14.5, 60.0
    t0, per = 1.5, 4.0
    for m, (lab, th, col) in enumerate(sets):
        y = 112 + m * 62
        Strip(st, root, sc, X0, y, [Gray(0.12 + 0.88 * v) for v in vals[m]], CW, t0 + m * per, 0.03, lab, col, 34.0)
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 1.6)
        if m:
            sc.Text(g, X0 + n * CW + 10, y + 14, "なめらかとの差 %.3f" % errs[m], size=12, weight=700, fill=col)
            sc.Text(g, X0 + n * CW + 10, y + 32, "境目 %d 本" % (nb[m] - 1), size=11, weight=500, fill=MUTED)
    # 境目のしきい値
    st.Panel(30, 372, 900, 110, "段のしきい値と、タッチ", color=PURPLE)
    t_c = t0 + 4 * per + 0.3
    lines = [("2 段", "N·L ≥ 0.35 で、明るい。それ以外は、影。はっきりしたマンガ調", RED), ("3 段", "明・中・影。もっとも標準的なアニメ調", GREEN), ("4 段", "段が多い分、なめらかに近づく。グラデーション寄り", BLUE)]
    for k, (a, b, c) in enumerate(lines):
        y = 408 + k * 22
        sc.Text(root, 50, y + 8, a, size=13, weight=700, fill=c, opacity=0).Show(t_c + k * 1.0)
        sc.Text(root, 130, y + 8, b, size=13, weight=500, fill=TEXT, opacity=0).Show(t_c + k * 1.0)
    st.Caption(30, 534, [(0.0, t0, "なめらかな陰影を、段に区切る"), (t0, t_c, "段が少ないほど、くっきり。多いほど、なめらかに近づく"), (t_c, 99, "段の境目の位置(しきい値)で、影の形が決まる。ランプ画像で、アーティストが調整する")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "セル", "なめらかとの差: 2 段 %.3f / 3 段 %.3f / 4 段 %.3f" % tuple(errs[1:]))
    return Build(st, name, "graphics/postprocess/stylized/cel-shading.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


# ===================================================================== Toon stages
def ToonStages():
    name = "toon-stages"
    st = Stage(name, "トゥーンの手順: ベース色 → 段のある陰 → リム ライト → 輪郭線。1 層ずつ足す", duration=21.0, subtitle="球の断面(48 画素)。層を 1 つずつ足して、各段階の見え方を、実際に計算する")
    sc, root = st.scene, st.root
    n = 48
    base = (0.95, 0.55, 0.3)
    lightd = (-0.5, 0.8)
    pts = []
    for i in range(n):
        x = (i + 0.5) / n * 2 - 1
        z = math.sqrt(max(0.0, 1 - x * x))
        pts.append((x, z))
    ndl = [max(0.0, p[0] * lightd[0] + p[1] * lightd[1]) for p in pts]
    ndv = [p[1] for p in pts]
    def Ramp(v):
        return 0.55 if v < 0.25 else (0.8 if v < 0.6 else 1.0)
    s1 = [tuple(base) for _ in range(n)]
    s2 = [tuple(v * Ramp(ndl[i]) for v in base) for i in range(n)]
    rim = lambda i: max(0.0, 1 - ndv[i] * 3.0) ** 1.0 if ndv[i] < 0.34 else 0.0
    s3 = [tuple(min(1.0, s2[i][k] + rim(i) * 0.9) for k in range(3)) for i in range(n)]
    s4 = [tuple(0.05 for _ in range(3)) if ndv[i] < 0.12 else s3[i] for i in range(n)]
    layers = [("① ベース色(一様)", s1, GRAY), ("② 段のある陰を掛ける(3 段)", s2, GREEN), ("③ リム ライト(縁を明るく)を足す", s3, AMBER), ("④ 輪郭線(視線に近い縁を、黒く)", s4, RED)]
    tot = [sum(sum(c) for c in s) / (3 * n) for _, s, _ in layers]
    ncol = [len({tuple(round(v, 2) for v in c) for c in s}) for _, s, _ in layers]
    assert ncol[1] > ncol[0] and ncol[3] >= ncol[2]
    CW, X0 = 14.5, 60.0
    t0, per = 1.5, 4.4
    for m, (lab, s, col) in enumerate(layers):
        y = 112 + m * 70
        Strip(st, root, sc, X0, y, [tuple(Enc(v) for v in c) for c in s], CW, t0 + m * per, 0.04, lab, col, 40.0)
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 2.0)
        sc.Text(g, X0 + n * CW + 10, y + 16, "色の種類 %d" % ncol[m], size=12, weight=700, fill=col)
        sc.Text(g, X0 + n * CW + 10, y + 36, "平均の明るさ %.2f" % tot[m], size=11, weight=500, fill=MUTED)
    st.Text(40, 420, "各段階の「色の種類」(数が少ないほど、べた塗り):", size=14)
    st.Counter(430, 424, [(t0 + m * per + 2.0, ncol[m]) for m in range(4)], size=26, fill=PURPLE)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 40, 444, 880, 66, [("層は、それぞれ独立。トゥーンは、写実の逆で、わざと情報を減らして「見せたい形」を強調する", 14, "#1e3a8a"), ("輪郭線は、法線と視線のなす角(縁の部分)でも作れる。別方式の輪郭線(裏面・エッジ検出)もある", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "トゥーン調は、いくつかの層の重ね合わせ"), (t0, t_e, "べた塗り → 段の陰 → リム ライト → 輪郭、と足していく"), (t_e, 99, "層ごとにオン・オフして、タッチを調整できる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "トゥーン", "色の種類: %s" % " → ".join(str(x) for x in ncol))
    return Build(st, name, "graphics/postprocess/stylized/index.md", BEFORE, [2.0, 5.0, 9.0, 14.0, 18.0, 20.0])


# ===================================================================== Outline edge detect
def OutlineEdgeDetect():
    name = "outline-edge-detect"
    st = Stage(name, "輪郭線(エッジ検出): 深度の差だけでは、同じ深さで、向きが変わる折れ目を見逃す。法線の差も、使う", duration=21.0, subtitle="24×12 画素。後ろの壁(深度 10)の前に、手前の箱(深度 4、上面と側面)がある。3 つの方法で、輪郭の画素を、見つける")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 12, 12.5
    depth = [[10.0] * NX for _ in range(NY)]
    nrm = [[2 for _ in range(NX)] for _ in range(NY)]       # 法線の向き ID(背景は、前面と同じ向き)
    for j in range(3, 11):
        for i in range(4, 20):
            depth[j][i] = 4.0
            nrm[j][i] = 1 if j < 6 else 2                      # 上面 / 前面
    nrm_b = lambda i, j: nrm[min(NY - 1, max(0, j))][min(NX - 1, max(0, i))]
    d_b = lambda i, j: depth[min(NY - 1, max(0, j))][min(NX - 1, max(0, i))]
    def Edge(use_d, use_n):
        e = {}
        for j in range(NY):
            for i in range(NX):
                ed = max(abs(d_b(i + 1, j) - depth[j][i]), abs(d_b(i, j + 1) - depth[j][i]), abs(d_b(i - 1, j) - depth[j][i]), abs(d_b(i, j - 1) - depth[j][i]))
                en = any(nrm_b(i + a, j + b) != nrm[j][i] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if (use_d and ed > 1.0) or (use_n and en):
                    e[(i, j)] = 1
        return e
    ed, en, eb = Edge(True, False), Edge(False, True), Edge(True, True)
    fold = {(i, j) for (i, j) in eb if (i, j) not in ed}
    assert len(fold) > 0 and len(eb) > len(ed) and len(en) < len(eb), (len(ed), len(en), len(eb))
    px = [30, 335, 640]
    labs = [("① 深度の差だけ", RED, ed), ("② 法線の差だけ", GREEN, en), ("③ 両方", BLUE, eb)]
    t0, per = 1.5, 3.8
    for p, (lab, col, e) in enumerate(labs):
        st.Panel(px[p], 100, NX * CS, NY * CS, lab, color=col)
        g = Grid(st, px[p], 100, NX, NY, CS, base="#f8fafc")
        for j in range(NY):
            for i in range(NX):
                base_c = "#cbd5e1" if depth[j][i] < 5 else "#f1f5f9"
                if nrm[j][i] == 1:
                    base_c = "#e2e8f0"
                g.Paint(i, j, 0.3, base_c)
                if (i, j) in e:
                    g.Paint(i, j, t0 + p * per + 0.05 * (i + j), "#111827")
        g.Flush()
    st.Text(30, 280, "箱の上面と前面の境(深度は同じ 4)が、輪郭に、なるか?", size=14, weight=700)
    ser = [(t0 + p * per + 0.05 * (NX + NY), len(e)) for p, (lab, col, e) in enumerate(labs)]
    st.Text(30, 320, "輪郭の画素:", size=15)
    st.Counter(150, 324, ser, size=26, fill=PURPLE)
    t_c = t0 + 3 * per
    for k, (lab, v, c) in enumerate([("深度だけ", len(ed), RED), ("法線だけ", len(en), GREEN), ("両方", len(eb), BLUE)]):
        pass
    sc.Text(root, 30, 360, "深度だけ: %d 画素。箱の折れ目の %d 画素を見逃す" % (len(ed), len(fold)), size=14, weight=700, fill=RED, opacity=0).Show(t_c)
    sc.Text(root, 30, 386, "法線だけ: %d 画素。背景と前面は向きが同じなので、箱の左右・下の外側を見逃す" % len(en), size=14, weight=700, fill=GREEN, opacity=0).Show(t_c + 1.0)
    sc.Text(root, 30, 412, "両方: %d 画素。外側も、折れ目も、拾える" % len(eb), size=14, weight=700, fill=BLUE, opacity=0).Show(t_c + 2.0)
    st.Box(t_c + 3.0, 560, 340, 370, 120, [("深度 = 輪郭の外側(物と背景)", 14, "#991b1b"), ("法線 = 輪郭の内側(折れ目)", 14, "#166534"), ("両方を足すと、きれいな線画になる", 14, "#1e3a8a"), ("読み込み: 各画素で、深度と法線を 4 近傍に読む", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "画面の絵から、輪郭線を作る"), (t0, t_c, "深度の差・法線の差で、隣と違う画素を見つける"), (t_c, 99, "どちらか一方だと、線が足りない")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "エッジ", "深度 %d / 法線 %d / 両方 %d(折れ目 %d)" % (len(ed), len(en), len(eb), len(fold)))
    return Build(st, name, "graphics/postprocess/stylized/outline-edge.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== Outline hull
def OutlineHullWidth():
    name = "outline-hull-width"
    st = Stage(name, "裏面法線の輪郭線: 世界で一定の太さにすると、遠くで細く、近くで太くなる。距離で補正して、画面で一定にする", duration=20.0, subtitle="輪郭の太さ(世界座標 0.02 m)を、距離 2・5・10・20 m で、画面の画素に直す。補正の有無で比べる")
    sc, root = st.scene, st.root
    F = 1000.0
    w = 0.02
    ds = [2.0, 5.0, 10.0, 20.0]
    plain = [F * w / d for d in ds]
    target = 4.0
    corr = [target for _ in ds]
    scale = [target * d / F for d in ds]
    assert plain[0] > plain[3] * 5
    X0 = 70.0
    st.Panel(30, 96, 900, 190, "① 輪郭の画面での太さ(画素)", color=BLUE)
    t0, per = 1.5, 3.8
    for m, d in enumerate(ds):
        x = 70 + m * 220
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        sc.Text(g, x, 126, "距離 %g m" % d, size=15, weight=700, fill=INK)
        # 物体(円)と輪郭
        r_obj = 360.0 / d / 2.4
        g.add("circle", cx=R(x + 70), cy=206, r=R(min(r_obj, 56)), fill="#cbd5e1", stroke=INK, stroke_width=R(max(0.5, plain[m])))
        sc.Text(g, x, 280, "太さ %.1f 画素" % plain[m], size=13, weight=700, fill=RED)
    st.Panel(30, 306, 900, 150, "② 補正して、画面で一定(%g 画素)にする" % target, color=GREEN)
    t_c = t0 + 4 * per + 0.3
    for m, d in enumerate(ds):
        x = 70 + m * 220
        g = root.add("g", opacity=0)
        g.Show(t_c + m * 0.8)
        g.add("circle", cx=R(x + 70), cy=382, r=R(min(360.0 / d / 2.4 * 0.8, 40)), fill="#cbd5e1", stroke=INK, stroke_width=target)
        sc.Text(g, x, 446, "世界の太さ %.3f m" % scale[m], size=13, weight=700, fill=GREEN)
    st.Text(40, 480, "距離 2 m と 20 m の、太さの比:", size=14)
    st.Counter(280, 484, [(t0 + 3 * per + 0.3, int(round(plain[0] / plain[3]))), (t_c + 2.4, 1)], size=26, fill=RED)
    st.Text(320, 484, "倍(補正なし)→ 1 倍(補正あり)", size=13, weight=500, fill=MUTED)
    t_e = t_c + 3.4
    st.Box(t_e, 560, 466, 370, 56, [("補正: 太さ ∝ 距離(カメラから頂点までの距離を、掛ける)", 13, "#166534"), ("遠景も近景も、同じ太さの線になる", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "裏返した殻を、法線方向へ、少し膨らませて、輪郭にする"), (t0, t_c, "世界で一定の太さだと、遠いほど画面で細くなる"), (t_c, 99, "距離に比例して膨らませると、画面では一定の太さ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "輪郭", "太さ(画素): " + " / ".join("%g m → %.1f" % (d, p) for d, p in zip(ds, plain)))
    return Build(st, name, "graphics/postprocess/stylized/outline-hull.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


# ===================================================================== Halftone
def HalftoneDots():
    name = "halftone-dots"
    st = Stage(name, "ハーフトーン: 明るさを、点の大きさに置き換える。点の面積が、暗さに比例するようにする", duration=20.0, subtitle="黒 → 白のグラデーションを、12×4 のセルの点で表す。点の半径の決め方を 2 通り比べる(半径 ∝ 暗さ と、面積 ∝ 暗さ)")
    sc, root = st.scene, st.root
    NC = 12
    cell = 54.0
    dark = [1 - (i + 0.5) / NC for i in range(NC)]
    r_lin = [d * cell * 0.5 * 1.0 for d in dark]
    r_area = [math.sqrt(d) * cell * 0.5 for d in dark]
    area = lambda r: math.pi * r * r
    cover = lambda r: area(r) / (cell * cell)
    maxc = math.pi / 4
    err_lin = sum(abs(cover(r) - maxc * d) for r, d in zip(r_lin, dark)) / NC
    err_area = sum(abs(cover(r) - maxc * d) for r, d in zip(r_area, dark)) / NC
    assert err_area < err_lin
    X0 = 60.0
    t0, per = 1.5, 5.5
    rows = [("半径 ∝ 暗さ", r_lin, RED, 120, err_lin), ("面積 ∝ 暗さ(半径 ∝ √暗さ)", r_area, GREEN, 260, err_area)]
    st.Text(X0, 108, "元のグラデーション(暗い → 明るい)", size=13, weight=700, fill=GRAY)
    g0 = Grid(st, X0, 112, NC, 1, cell, base="#e5e7eb", stroke="#94a3b8", cell_h=20.0)
    for i in range(NC):
        g0.Paint(i, 0, 0.3, Gray(1 - dark[i]))
    g0.Flush()
    for r_, (lab, rs, col, y, e) in enumerate(rows):
        yy = 160 + r_ * 130
        sc.Text(root, X0, yy - 6, lab, size=14, weight=700, fill=col)
        root.add("rect", x=X0, y=yy, width=NC * cell, height=cell, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        for i, rad in enumerate(rs):
            c = root.add("circle", cx=R(X0 + (i + 0.5) * cell), cy=R(yy + cell / 2), r=R(max(rad, 0.1)), fill="#111827", opacity=0)
            c.Show(t0 + r_ * per + i * 0.25)
        gx = root.add("g", opacity=0)
        gx.Show(t0 + r_ * per + NC * 0.25)
        sc.Text(gx, X0, yy + cell + 22, "点の面積の割合と、目標の暗さ(最大 π/4 = 0.785)との差の平均: %.3f" % e, size=14, weight=700, fill=col)
    st.Panel(30, 430, 900, 60, "暗さが 0.5 のセルでは", color=PURPLE)
    i5 = NC // 2
    sc.Text(root, 50, 472, "目標 %.2f に対して、半径 ∝ 暗さ → %.2f(薄すぎ)/ 面積 ∝ 暗さ → %.2f(ちょうど)" % (maxc * dark[i5], cover(r_lin[i5]), cover(r_area[i5])), size=14, weight=700, fill=TEXT, opacity=0).Show(t0 + 2 * per)
    st.Caption(30, 534, [(0.0, t0, "印刷のような、点で濃淡を作る表現"), (t0, t0 + 2 * per, "半径を暗さに比例させると、明るく出すぎる(面積は半径の 2 乗)"), (t0 + 2 * per, 99, "面積が暗さに比例するように、半径に √ を掛ける")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ハーフトーン", "ずれ: 半径比例 %.3f / 面積比例 %.3f" % (err_lin, err_area))
    return Build(st, name, "graphics/postprocess/stylized/posterize-halftone.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 19.0])


NAMES = ["basic-adjustments", "color-lut-lookup", "color-lgg-curves", "lut-half-texel", "lut-blend-zones", "white-balance", "cel-ramp", "toon-stages", "outline-edge-detect", "outline-hull-width", "halftone-dots"]
FIGS = [BasicAdjustments, ColorLutLookup, ColorLggCurves, LutHalfTexel, LutBlendZones, WhiteBalance, CelRamp, ToonStages, OutlineEdgeDetect, OutlineHullWidth, HalftoneDots]
