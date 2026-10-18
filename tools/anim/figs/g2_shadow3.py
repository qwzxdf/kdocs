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


def Moments(ds):
    mu = sum(ds) / len(ds)
    var = max(1e-5, sum(d * d for d in ds) / len(ds) - mu * mu)
    return mu, var


def Cheb(ds, t):
    mu, var = Moments(ds)
    if t <= mu:
        return 1.0
    return var / (var + (t - mu) ** 2)


# ===================================================================== VSM Chebyshev
def VsmChebyshev():
    name = "vsm-chebyshev"
    st = Stage(name, "分散シャドウ マップ(VSM): 深度の平均と分散だけ覚えて、チェビシェフの不等式で「光が届く割合の上限」を出す", duration=21.0, subtitle="フィルター範囲の 16 サンプルの深度が、手前の物(0.4)6 個と、奥の地面(0.8)10 個。受ける点の深度 t を 0.2 → 1.0 に動かす")
    sc, root = st.scene, st.root
    ds = [0.4] * 6 + [0.8] * 10
    mu, var = Moments(ds)
    ts = [0.2 + 0.8 * k / 40 for k in range(41)]
    truth = lambda t: sum(1 for d in ds if d >= t - 1e-9) / len(ds)
    tv = [truth(t) for t in ts]
    cv = [Cheb(ds, t) for t in ts]
    assert all(c + 1e-9 >= a for c, a in zip(cv, tv))
    gap = max(c - a for c, a in zip(cv, tv))
    X0, W = 70.0, 440.0
    st.Panel(30, 96, 480, 170, "① 16 個のサンプルの深度(棒 = 1 個)", color=BLUE)
    for i, d in enumerate(ds):
        h = d * 110
        root.add("rect", x=R(48 + i * 27), y=R(250 - h), width=22, height=R(h), fill=("#fca5a5" if d < 0.5 else "#93c5fd"), stroke="#64748b", stroke_width=1)
    st.Text(48, 118, "赤 = 手前の物(深度 0.4)、青 = 奥の地面(0.8)", size=12, weight=500, fill=MUTED)
    root.add("line", x1=40, y1=R(250 - mu * 110), x2=490, y2=R(250 - mu * 110), stroke=GREEN, stroke_width=2.5, stroke_dasharray="6 5")
    sc.Text(root, 488, R(250 - mu * 110) - 6, "平均 μ = %.3f" % mu, size=12, weight=700, fill=GREEN, anchor="end")
    st.Panel(540, 96, 390, 170, "② 覚えておく値は、たった 2 つ", color=PURPLE)
    for k, (a, b) in enumerate([("平均(深度の平均)", "μ = %.3f" % mu), ("2 乗の平均 − 平均の 2 乗", "分散 σ² = %.4f" % var), ("保存するもの", "(深度, 深度²) の 2 枚")]):
        sc.Text(root, 560, 130 + k * 40, a, size=13, weight=500, fill=MUTED)
        sc.Text(root, 560, 150 + k * 40, b, size=16, weight=700, fill=PURPLE)
    st.Panel(30, 290, 900, 190, "③ 受ける点の深度 t を動かしたときの、光が届く割合", color=RED)
    ax0, ay0, aw, ah = 70.0, 304.0, 820.0, 150.0
    XX = lambda t: ax0 + (t - 0.2) / 0.8 * aw
    YY = lambda v: ay0 + ah - v * ah
    root.add("path", d=Poly([(XX(t), YY(v)) for t, v in zip(ts, tv)]), fill="none", stroke=GREEN, stroke_width=3.5)
    root.add("path", d=Poly([(XX(t), YY(v)) for t, v in zip(ts, cv)]), fill="none", stroke=RED, stroke_width=3.5, stroke_dasharray="7 5")
    st.Legend(80, 472, [(GREEN, "正解(深度の分布をそのまま数える)"), (RED, "VSM(平均と分散から、チェビシェフ)")])
    t0, t1 = 1.5, 14.0
    d1 = root.add("circle", cx=R(XX(ts[0])), cy=R(YY(tv[0])), r=6, fill=GREEN)
    d2 = root.add("circle", cx=R(XX(ts[0])), cy=R(YY(cv[0])), r=6, fill=RED)
    for k, t in enumerate(ts):
        tt = t0 + (t1 - t0) * k / (len(ts) - 1)
        for node, v in ((d1, tv[k]), (d2, cv[k])):
            if k == 0:
                node.Set(tt, "cx", R(XX(t)))
                node.Set(tt, "cy", R(YY(v)))
            else:
                node.Ramp(tp, tt, "cx", R(XX(t)))
                node.Ramp(tp, tt, "cy", R(YY(v)))
        tp = tt
    items = [(0.0, t0, "受ける点が、手前の物より手前(t ≤ μ)なら、無条件で光が届く")]
    items += [(t0, t0 + 5.0, "t が 0.4 〜 0.8: 正解は 0.625(奥の 10 個だけ届く)、VSM は それ以上の値(上限)"), (t0 + 5.0, t1, "t > 0.8: 全部の深度より奥 → 正解は 0、VSM は 小さいが 0 ではない")]
    st.Caption(70, 500, items, size=13, fill=INK)
    st.Box(t1 + 1.0, 540, 96, 390, 170, [("VSM は、上限なので、", 15, "#991b1b"), ("本当より明るくなる側にずれる", 15, "#991b1b"), ("最大のずれ %.2f" % gap, 15, "#991b1b"), ("(光が漏れる = ライト ブリーディング)", 13, MUTED)], RED, "#fef2f2")
    st.Note(t0, "VSM", "平均 %.3f、分散 %.4f。最大のずれ %.2f" % (mu, var, gap))
    return Build(st, name, "graphics/shadows/vsm/index.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== VSM light bleeding
def VsmLightBleeding():
    name = "vsm-light-bleeding"
    st = Stage(name, "VSM の光漏れ: 手前の物が 2 段あると、平均と分散だけでは、影が薄くなる", duration=20.0, subtitle="手前の物 A(0.15)と B(0.45)が重なる所の、奥(深度 0.6)の点。正解は 4 分の 3 が影。式で出した光の割合を比べる")
    sc, root = st.scene, st.root
    ds = [0.15] * 6 + [0.45] * 6 + [0.95] * 4
    t = 0.6
    truth = sum(1 for d in ds if d >= t) / len(ds)
    raw = Cheb(ds, t)
    lo = lambda p, a: max(0.0, min(1.0, (p - a) / (1 - a)))
    fixes = [("何もしない", raw), ("0.2 以下を 0 にして伸ばす", lo(raw, 0.2)), ("0.4 以下を 0 にして伸ばす", lo(raw, 0.4)), ("0.6 以下を 0 にして伸ばす", lo(raw, 0.6))]
    assert raw > truth + 0.1
    mu, var = Moments(ds)
    st.Panel(30, 96, 440, 200, "① 16 個のサンプルの深度", color=BLUE)
    for i, d in enumerate(ds):
        root.add("rect", x=R(48 + i * 26), y=R(280 - d * 150), width=21, height=R(d * 150), fill=("#fca5a5" if d < 0.3 else "#fcd34d" if d < 0.6 else "#93c5fd"), stroke="#64748b", stroke_width=1)
    root.add("line", x1=40, y1=R(280 - t * 150), x2=460, y2=R(280 - t * 150), stroke=INK, stroke_width=2.5, stroke_dasharray="5 4")
    sc.Text(root, 458, R(280 - t * 150) - 6, "受ける点 t = %.1f" % t, size=12, weight=700, fill=INK, anchor="end")
    st.Text(48, 118, "A = 0.15(6 個)、B = 0.45(6 個)、地面 0.95(4 個)", size=12, weight=500, fill=MUTED)
    st.Panel(500, 96, 430, 200, "② 数える と 式で出す", color=PURPLE)
    sc.Text(root, 520, 134, "正解: t より奥のサンプル = %d / 16 → 光 %.2f" % (round(truth * 16), truth), size=15, weight=700, fill=GREEN)
    sc.Text(root, 520, 164, "平均 μ = %.3f、分散 σ² = %.3f" % (mu, var), size=14, weight=500, fill=TEXT)
    sc.Text(root, 520, 194, "σ² ÷ (σ² + (t − μ)²) = %.3f" % raw, size=15, weight=700, fill=RED)
    sc.Text(root, 520, 226, "→ 本当は %.2f なのに、%.2f も光が漏れる" % (truth, raw), size=15, weight=700, fill="#991b1b")
    t0, per = 3.0, 3.4
    st.Panel(30, 320, 900, 170, "③ 漏れを減らす補正(低い値を 0 にして、残りを 0〜1 に伸ばす)", color=GREEN)
    for k, (lab, v) in enumerate(fixes):
        y = 352 + k * 32
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per)
        sc.Text(g, 50, y + 14, lab, size=13, weight=700, fill=TEXT)
        w = v * 420
        g.add("rect", x=300, y=y, width=R(max(w, 2)), height=20, fill=(RED if v > truth + 0.05 else GREEN), opacity=0.85)
        sc.Text(g, 300 + w + 8, y + 15, "光 %.2f" % v, size=13, weight=700, fill=TEXT)
    root.add("line", x1=R(300 + truth * 420), y1=340, x2=R(300 + truth * 420), y2=482, stroke=GREEN, stroke_width=2.5, stroke_dasharray="6 5")
    sc.Text(root, R(300 + truth * 420) + 6, 336, "正解 %.2f" % truth, size=12, weight=700, fill=GREEN)
    over = lo(raw, 0.6)
    t_e = t0 + 4 * per
    st.Box(t_e, 500, 96, 430, 200, [("補正を強くすると漏れは減るが、", 15, "#1e3a8a"), ("薄い影も消えやすい(補正 0.6 で光 %.2f)" % over, 15, "#1e3a8a"), ("→ 補正値は、見た目で調整する", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "平均と分散だけでは、「手前の物が 2 段ある」ことが分からない"), (t0, t_e, "漏れを、低い値を切り捨てる補正で、減らしていく"), (t_e, 99, "補正のしすぎは、薄い影を消す")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "光漏れ", "正解 %.2f に対し、補正なし %.2f" % (truth, raw))
    return Build(st, name, "graphics/shadows/vsm/light-bleeding.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== ESM
def EsmExp():
    name = "esm-exp"
    st = Stage(name, "ESM: 光が届く割合を、exp(−c·(受ける点の深度 − 手前の深度)) で近似する。c が大きいほど影がくっきり", duration=20.0, subtitle="手前の物の深度 0.5 の前後で、受ける点の深度 t を動かす。c を 4 → 16 → 48 に上げて、本当の階段状(0 か 1)に近づく")
    sc, root = st.scene, st.root
    occ = 0.5
    cs = [4.0, 16.0, 48.0]
    ts = [0.2 + 0.7 * k / 60 for k in range(61)]
    truth = lambda t: 1.0 if t <= occ + 1e-9 else 0.0
    f = lambda c, t: min(1.0, math.exp(-c * (t - occ)))
    errs = [sum(abs(f(c, t) - truth(t)) for t in ts) / len(ts) for c in cs]
    assert errs[0] > errs[1] > errs[2]
    ax0, ay0, aw, ah = 70.0, 120.0, 820.0, 200.0
    st.Panel(30, 96, 900, 260, "光が届く割合", color=BLUE)
    XX = lambda t: ax0 + (t - 0.2) / 0.7 * aw
    YY = lambda v: ay0 + ah - v * ah
    root.add("path", d=Poly([(XX(t), YY(truth(t))) for t in ts]), fill="none", stroke=GREEN, stroke_width=3, stroke_dasharray="6 5")
    root.add("line", x1=R(XX(occ)), y1=ay0, x2=R(XX(occ)), y2=ay0 + ah, stroke=GRAY, stroke_width=1.5, stroke_dasharray="3 4")
    sc.Text(root, XX(occ) + 6, ay0 + 14, "手前の物 0.5", size=12, weight=700, fill=GRAY)
    cur = root.add("path", d=Poly([(XX(t), YY(f(cs[0], t))) for t in ts]), fill="none", stroke=RED, stroke_width=4)
    t0, per = 1.5, 5.2
    cur.Steps("d", [(t0 + m * per, Poly([(XX(t), YY(f(c, t))) for t in ts])) for m, c in enumerate(cs)])
    for m, c in enumerate(cs):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        sc.Text(g, 90, 140, "c = %g" % c, size=22, weight=700, fill=RED)
        sc.Text(g, 90, 168, "正解(緑の破線)とのずれ %.3f" % errs[m], size=14, weight=700, fill=TEXT)
        w = {4.0: "ぼやけた影。手前の物の近くで、光が漏れる", 16.0: "くっきりしてきた", 48.0: "ほぼ階段状。ただし、c が大きすぎると、数値が壊れる(オーバーフロー)"}[c]
        sc.Text(g, 90, 190, w, size=13, weight=500, fill=MUTED)
    st.Text(40, 392, "ESM の保存値:", size=14, weight=700)
    st.Text(150, 392, "exp(c · 深度)。16 ビット float だと c ≈ 11 が限界(exp が 65504 を超える)", size=13, weight=500, fill=TEXT)
    lim = math.log(65504)
    assert 10 < lim < 12
    st.Text(40, 420, "float の限界から、c の最大: ln(65504) = %.2f(深度が 1 の場合)" % lim, size=14, weight=700, fill="#991b1b")
    t_e = t0 + 3 * per
    st.Box(t_e - 0.5, 560, 436, 370, 74, [("c を上げる = 影がくっきり。ただし数値の限界がある", 14, "#1e3a8a"), ("ずれ: c=4 → %.3f / 16 → %.3f / 48 → %.3f" % tuple(errs), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "硬い影(0 か 1)を、なめらかな式で近似する"), (t0, t_e, "c を上げるほど階段に近づく"), (t_e, 99, "c の上げすぎは、数値の限界で壊れる。EVSM は、その対策")], size=14, fill=MUTED, weight=500)
    for m, c in enumerate(cs):
        st.Note(t0 + m * per, "ESM", "c = %g: ずれ %.3f" % (c, errs[m]))
    return Build(st, name, "graphics/shadows/vsm/esm.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== Perspective aliasing
def PerspectiveAliasing():
    name = "perspective-aliasing"
    st = Stage(name, "透視エイリアシング: 近くでは、シャドウ マップの 1 マスが、画面で大きく見える", duration=21.0, subtitle="断面。カメラから床を見て、シャドウ マップの 1 マス(床の上で一定の幅)が、画面の何画素ぶんになるか")
    sc, root = st.scene, st.root
    H = 2.0               # カメラの高さ
    FOCAL = 600.0         # 画面の大きさ
    TEXEL = 0.25          # 影の 1 マスの床上の幅(m)
    ds = [3.0, 6.0, 12.0, 24.0, 48.0]
    rows = []
    for d in ds:
        # 床の点 d と d + TEXEL の画面位置の差
        y1 = FOCAL * H / d
        y2 = FOCAL * H / (d + TEXEL)
        rows.append((d, y1 - y2))
    assert rows[0][1] > rows[1][1] > rows[4][1]
    ox, oy, S = 70.0, 280.0, 8.5
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * 40
    st.Panel(30, 96, 900, 230, "① 断面(床にシャドウ マップの 1 マスが一定の幅で並ぶ)", color=BLUE)
    root.add("line", x1=X(0), y1=Y(0), x2=X(100), y2=Y(0), stroke="#475569", stroke_width=3)
    root.add("circle", cx=X(0), cy=Y(H), r=8, fill=INK)
    sc.Text(root, X(0) + 10, Y(H) - 8, "カメラ(高さ %g m)" % H, size=12, weight=700, fill=INK)
    for k in range(0, 120):
        x = k * TEXEL * 1.0
        if x > 50:
            break
        root.add("line", x1=R(X(x)), y1=Y(0), x2=R(X(x)), y2=Y(0) + 8, stroke=AMBER, stroke_width=1.5)
    st.Text(40, 120, "オレンジの短い線 = 影のマスの境目(%.2f m ごと)" % TEXEL, size=12, weight=500, fill=MUTED)
    t0, per = 1.5, 3.6
    for m, (d, px) in enumerate(rows):
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per, t0 + (m + 1) * per if m < 4 else None)
        g.add("line", x1=R(X(0)), y1=R(Y(H)), x2=R(X(d)), y2=R(Y(0)), stroke=RED, stroke_width=2)
        g.add("line", x1=R(X(0)), y1=R(Y(H)), x2=R(X(d + TEXEL)), y2=R(Y(0)), stroke=RED, stroke_width=2)
        g.add("rect", x=R(X(d)), y=R(Y(0)) - 5, width=R(max(3, TEXEL * S)), height=10, fill=RED)
        sc.Text(g, X(d), Y(0) + 34, "距離 %g m" % d, size=13, weight=700, fill=RED, anchor="middle")
    # 画面の帯
    st.Panel(30, 346, 900, 100, "② その 1 マスが、画面でどれだけの画素になるか", color=PURPLE)
    for m, (d, px) in enumerate(rows):
        x = 50 + m * 175
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        w = min(150.0, px * 6)
        g.add("rect", x=x, y=382, width=R(max(w, 2)), height=26, fill=(RED if px > 3 else GREEN), opacity=0.85)
        sc.Text(g, x, 376, "距離 %g m" % d, size=12, weight=700, fill=TEXT)
        sc.Text(g, x + 4, 428, "%.1f 画素 / マス" % px, size=14, weight=700, fill=(RED if px > 3 else GREEN))
    ser = [(t0 + m * per + 0.2, int(round(rows[m][1] * 10))) for m in range(5)]
    st.Text(40, 478, "1 マスの画素数(×10):", size=14)
    st.Counter(220, 482, ser, size=22, fill=RED)
    st.Box(t0 + 5 * per, 480, 460, 450, 60, [("近く(3 m)は %.1f 画素 / マス → ギザギザが目立つ" % rows[0][1], 14, "#991b1b"), ("遠く(48 m)は %.2f 画素 / マス → ほぼ見えない" % rows[4][1], 14, "#166534")], PURPLE, "#faf5ff")
    st.Caption(30, 534, [(0.0, t0, "シャドウ マップのマスは、光の側から見て、均等に並ぶ"), (t0, t0 + 5 * per, "カメラから見ると、近いほど 1 マスが大きく見える"), (t0 + 5 * per, 99, "だから、カスケードで、近くほど細かい影の表を使う")], size=14, fill=MUTED, weight=500)
    for m, (d, px) in enumerate(rows):
        st.Note(t0 + m * per, "透視", "距離 %g m: 1 マスは %.2f 画素" % (d, px))
    return Build(st, name, "graphics/shadows/shadow-map-basics/aliasing-stabilize.md", BEFORE, [2.0, 5.5, 9.0, 12.5, 16.0, 20.0])


# ===================================================================== RT shadow samples
def RtShadowSamples():
    name = "rt-shadow-samples"
    st = Stage(name, "レイトレースの影: 面積のある光に、影の光線を N 本飛ばして、割合で濃さを決める", duration=21.0, subtitle="1 つの点から、光(幅 4)の上のでたらめな点へ N 本。遮られた本数の割合が影の濃さ。同じ点で何度もやって、ばらつきを見る")
    sc, root = st.scene, st.root
    LW, BW = 4.0, 3.0
    yb, yr = 3.0, 6.0
    Xp = 5.5
    Y0, X0, S = 120.0, 60.0, 40.0

    def Vis(lx):
        t = yb / yr
        xx = lx + (Xp - lx) * t
        return abs(xx - 8.0) > BW / 2
    NS = 400
    truth = sum(1 for k in range(NS) if Vis(8.0 - LW / 2 + LW * (k + 0.5) / NS)) / NS
    assert 0.1 < truth < 0.9
    ns = [1, 4, 16, 64]
    stats = []
    for n in ns:
        vals = []
        for trial in range(200):
            r = Lcg(trial * 7919 + n)
            vals.append(sum(1 for _ in range(n) if Vis(8.0 - LW / 2 + LW * r.U())) / n)
        sd = math.sqrt(sum((v - truth) ** 2 for v in vals) / len(vals))
        stats.append((n, sd))
    assert stats[0][1] > stats[1][1] > stats[2][1] > stats[3][1]
    st.Panel(30, 96, 440, 250, "① 光・遮る板・受ける点(断面)", color=AMBER)
    UX = lambda x: X0 + x * 26.0
    UY = lambda y: Y0 + y * 34.0
    root.add("rect", x=R(UX(8 - LW / 2)), y=R(UY(0) - 8), width=R(LW * 26), height=8, fill=AMBER)
    root.add("rect", x=R(UX(8 - BW / 2)), y=R(UY(yb)), width=R(BW * 26), height=7, fill="#475569")
    root.add("line", x1=UX(0), y1=R(UY(yr)), x2=UX(15), y2=R(UY(yr)), stroke="#94a3b8", stroke_width=3)
    root.add("circle", cx=R(UX(Xp)), cy=R(UY(yr)), r=7, fill=INK)
    t0, per = 1.5, 4.2
    shown = [1, 4, 16, 64]
    for m, n in enumerate(shown):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        r = Lcg(99 + n)
        lit = 0
        for k in range(n):
            lx = 8 - LW / 2 + LW * r.U()
            v = Vis(lx)
            lit += v
            g.add("line", x1=R(UX(Xp)), y1=R(UY(yr)), x2=R(UX(lx)), y2=R(UY(0)), stroke=(GREEN if v else RED), stroke_width=1.5, opacity=0.8)
        sc.Text(g, 50, 338, "光線 %d 本 → 届いた %d 本 → 光 %.2f(正解 %.2f)" % (n, lit, lit / n, truth), size=14, weight=700, fill=PURPLE)
    st.Panel(500, 96, 430, 250, "② 同じ点で 200 回やったときの、ばらつき", color=RED)
    for m, (n, sd) in enumerate(stats):
        y = 140 + m * 50
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.5)
        sc.Text(g, 520, y + 18, "%d 本" % n, size=15, weight=700, fill=INK)
        w = sd / stats[0][1] * 260
        g.add("rect", x=590, y=y, width=R(w), height=26, fill=RED, opacity=0.85)
        sc.Text(g, 590 + w + 8, y + 19, "ばらつき %.3f" % sd, size=13, weight=700, fill=RED)
    ser = [(t0 + m * per + 0.3, n) for m, n in enumerate(shown)]
    st.Text(40, 384, "影の光線の本数:", size=15)
    st.Counter(190, 388, ser, size=26, fill=PURPLE)
    st.Text(40, 420, "画面 1920×1080 での 1 フレームの光線:", size=14)
    st.Counter(40, 452, [(t0 + m * per + 0.3, n * 1920 * 1080) for m, n in enumerate(shown)], size=26, fill=BLUE)
    t_e = t0 + 4 * per
    st.Box(t_e, 520, 380, 410, 116, [("4 倍の本数で、ばらつきは約 半分(1/√N)", 15, "#1e3a8a"), ("1 本 %.3f → 64 本 %.3f(約 %.1f 分の 1)" % (stats[0][1], stats[3][1], stats[0][1] / stats[3][1]), 14, TEXT), ("実際は 1 本で撮って、時間方向に重ねて(デノイズ)消す", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "面積のある光の影は、半影ができる"), (t0, t_e, "光の上の点を、ばらつかせて選び、遮られた割合を数える"), (t_e, 99, "本数を増やすほど、きれい。でも、光線は、画素数に比例して増える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "RT 影", "N = 1 / 4 / 16 / 64: ばらつき %.3f / %.3f / %.3f / %.3f" % tuple(s for _, s in stats))
    return Build(st, name, "graphics/shadows/ray-traced.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== Stipple shadow
def StippleShadow():
    name = "stipple-shadow"
    st = Stage(name, "半透明の影: 透明度に応じて、シャドウ マップに「点描」で書き込み、PCF でなめらかにする", duration=19.0, subtitle="1 列 24 マスの影の表に、透明度の違う 3 枚の板の影を書く。点描のパターンのままだと粗いが、PCF で平均すると、薄い影になる")
    sc, root = st.scene, st.root
    N = 24
    bay = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
    thr = lambda i, j=0: (bay[(i % 4) + 4 * (j % 4)] + 0.5) / 16
    alphas = [(0.25, 0, 7), (0.5, 8, 15), (0.8, 16, 23)]
    NY = 4
    grid = [[0.0] * N for _ in range(NY)]
    for a, x0, x1 in alphas:
        for j in range(NY):
            for i in range(x0, x1 + 1):
                grid[j][i] = 1.0 if a > thr(i, j) else 0.0
    # 本当の影の濃さ
    want = [a for a, x0, x1 in alphas for i in range(x0, x1 + 1)]
    # PCF 4 幅
    def Pcf(i):
        vals = [grid[j][min(N - 1, max(0, i + d))] for j in range(NY) for d in (-1, 0, 1, 2)]
        return sum(vals) / len(vals)
    pcf = [Pcf(i) for i in range(N)]
    raw = [sum(grid[j][i] for j in range(NY)) / NY for i in range(N)]
    err_raw = sum(abs(raw[i] - want[i]) for i in range(N)) / N
    err_pcf = sum(abs(pcf[i] - want[i]) for i in range(N)) / N
    assert err_pcf <= err_raw + 1e-9
    CW, X0 = 30.0, 60.0
    st.Text(X0, 100, "① 透明度の違う 3 枚(α = 0.25、0.5、0.8)", size=14, weight=700)
    for k, (a, x0, x1) in enumerate(alphas):
        root.add("rect", x=R(X0 + x0 * CW), y=108, width=R((x1 - x0 + 1) * CW - 2), height=22, fill="#94a3b8", fill_opacity=a)
        sc.Text(root, R(X0 + (x0 + x1 + 1) / 2 * CW), 124, "α = %.2f" % a, size=12, weight=700, fill=INK, anchor="middle")
    st.Panel(X0 - 8, 150, N * CW + 16, NY * 30 + 14, "② 影の表への書き込み(黒 = 書く、白 = 書かない)", color=PURPLE)
    g = Grid(st, X0, 158, N, NY, 30.0, base="#ffffff", stroke="#94a3b8")
    t0, dts = 1.5, 0.15
    for j in range(NY):
        for i in range(N):
            g.Paint(i, j, t0 + i * dts, "#334155" if grid[j][i] else "#ffffff")
    g.Flush()
    t_p = t0 + N * dts + 0.6
    sc.Text(root, X0, 318, "③ 平均する(PCF): 4 マス × 4 行", size=14, weight=700, fill=BLUE)
    gp = Grid(st, X0, 326, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        gp.Paint(i, 0, t_p + i * 0.08, Gray(1 - pcf[i]))
    gp.Flush()
    sc.Text(root, X0, 378, "④ 本当の影の濃さ(正解)", size=14, weight=700, fill=GREEN)
    gt = Grid(st, X0, 386, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        gt.Paint(i, 0, t_p + i * 0.08, Gray(1 - want[i]))
    gt.Flush()
    t_e = t_p + N * 0.08 + 0.6
    st.Box(t_e, 60, 436, 840, 74, [("正解とのずれ: 点描のまま(縦に平均)%.3f → PCF %.3f" % (err_raw, err_pcf), 15, "#1e3a8a"), ("点描は、1 マスに 0 か 1 しか書けない。周りの平均で、薄い影を作る(特別なテクスチャは不要)", 13, TEXT)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "シャドウ マップは「物がある / ない」の 2 値。薄い影は書けない"), (t0, t_p, "透明度を、点描(しきい値との比較)で、書く / 書かないに変える"), (t_p, t_e, "PCF で平均すると、点描が混ざって、薄い影になる"), (t_e, 99, "透明度に近い濃さになる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "点描", "しきい値は 4×4 のディザ。ずれ: 点描 %.3f → PCF %.3f" % (err_raw, err_pcf))
    return Build(st, name, "graphics/shadows/special-cases/translucent-shadows.md", BEFORE, [1.5, 3.5, 5.5, 8.0, 11.0, 17.0])


# ===================================================================== VSM pages
def VsmPages():
    name = "vsm-pages"
    st = Stage(name, "仮想シャドウ マップ: 巨大な影の表を、画面に見える所だけ、ページ単位で作る", duration=21.0, subtitle="16×16 ページの仮想的な表(各ページ 128×128 マス)。カメラが動くと、見える所のページだけを、確保・描画する")
    sc, root = st.scene, st.root
    NP, CS = 16, 26.0
    X0, Y0 = 40.0, 110.0
    cams = [(3.0, 11.0), (8.0, 8.0), (12.0, 3.0)]
    FOV = 3.0

    def Need(c):
        need = set()
        for i in range(NP):
            for j in range(NP):
                d = math.hypot(i + 0.5 - c[0], j + 0.5 - c[1])
                if d <= FOV * 1.35:
                    need.add((i, j))
        return need

    needs = [Need(c) for c in cams]
    total = NP * NP
    assert all(len(n) < total * 0.25 for n in needs)
    cache = set()
    drawn = []
    for n in needs:
        drawn.append(len(n - cache))
        cache |= n
    st.Panel(30, 96, NP * CS + 20, NP * CS + 20, "仮想的な表(青 = 確保済み、赤 = 今フレームで描いた)", color=BLUE)
    g = Grid(st, X0, Y0, NP, NP, CS, base="#f1f5f9")
    t0, per = 1.5, 6.0
    have = set()
    for m, need in enumerate(needs):
        for (i, j) in need:
            new = (i, j) not in have
            g.Paint(i, j, t0 + m * per + 0.05 * (i + j), "#fca5a5" if new else "#93c5fd")
            g.Paint(i, j, t0 + m * per + 2.4, "#93c5fd")
        have |= need
    g.Flush()
    g.Lines(color="#ffffff", opacity=0.6)
    cam = root.add("circle", cx=R(X0 + cams[0][0] * CS), cy=R(Y0 + cams[0][1] * CS), r=9, fill=INK)
    for m in range(1, 3):
        cam.Ramp(t0 + m * per - 1.0, t0 + m * per - 0.1, "cx", R(X0 + cams[m][0] * CS))
        cam.Ramp(t0 + m * per - 1.0, t0 + m * per - 0.1, "cy", R(Y0 + cams[m][1] * CS))
    X1 = 520
    st.Panel(X1, 96, 410, 230, "かかった作業", color=PURPLE)
    page_mem = 128 * 128 * 4
    for m in range(3):
        gg = root.add("g", opacity=0)
        gg.Show(t0 + m * per)
        sc.Text(gg, X1 + 16, 134 + m * 60, "フレーム %d: 見えるページ %d 個" % (m + 1, len(needs[m])), size=14, weight=700, fill=PURPLE)
        sc.Text(gg, X1 + 16, 156 + m * 60, "新しく描いたページ %d 個(キャッシュ %d 個)" % (drawn[m], len(needs[m]) - drawn[m]), size=13, weight=500, fill=TEXT)
    st.Text(40, 470, "描いたページ:", size=15)
    cum = []
    c = 0
    for m in range(3):
        c += drawn[m]
        cum.append((t0 + m * per + 0.3, c))
    st.Counter(170, 474, cum, size=24, fill=RED)
    st.Text(210, 474, "/ 全 %d ページ" % total, size=14, weight=500, fill=MUTED)
    full_mem = total * page_mem // 1024 // 1024
    used = len(needs[2]) * page_mem // 1024 // 1024
    st.Box(t0 + 3 * per - 0.5, X1, 344, 410, 130, [("全部を確保すると %d MB(2048×2048 マスの表)" % full_mem, 14, "#991b1b"), ("見えるページだけなら %d MB" % used, 15, "#166534"), ("動いても、新しく見えるページだけを描く(キャッシュ)", 13, TEXT), ("ライトが動かなければ、前のページを、そのまま使う", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "巨大な表を全部持つのは無理。見える所だけ持つ"), (t0, t0 + 3 * per, "カメラが動くと、新しく見える所だけを描き足す"), (t0 + 3 * per, 99, "描くページが少ないので、高解像度の影が、安く作れる")], size=14, fill=MUTED, weight=500)
    for m in range(3):
        st.Note(t0 + m * per, "仮想影", "フレーム %d: 見える %d、新規 %d" % (m + 1, len(needs[m]), drawn[m]))
    return Build(st, name, "graphics/shadows/virtual-shadow-maps.md", BEFORE, [2.0, 4.0, 8.0, 12.0, 16.0, 20.0])


NAMES = ["vsm-chebyshev", "vsm-light-bleeding", "esm-exp", "perspective-aliasing", "rt-shadow-samples", "stipple-shadow", "vsm-pages"]
FIGS = [VsmChebyshev, VsmLightBleeding, EsmExp, PerspectiveAliasing, RtShadowSamples, StippleShadow, VsmPages]
