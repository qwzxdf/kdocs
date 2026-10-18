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


def Curve(root, pts, col, width=3.5, dash=None, opacity=1):
    extra = {"stroke_dasharray": dash} if dash else {}
    return root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=width, opacity=opacity, **extra)


# ===================================================================== halo / range check
def HaloRange():
    name = "halo-range"
    st = Stage(name, "範囲チェック: 遠い物を遮蔽に数えると、手前の人物の周りに、暗いハロー(輪)が出る", duration=21.0, subtitle="断面。人物(深度 1)の後ろに、壁(深度 6)。壁の画素の AO を、範囲チェックなし / 硬い切り捨て / なめらかに弱める、で比べる")
    sc, root = st.scene, st.root
    n = 48
    depth = [6.0] * n
    for i in range(20, 28):
        depth[i] = 1.0
    R_ = 1.5
    K, RAD = 6, 5

    def Ao(i, mode):
        occ = 0.0
        for k in range(1, RAD + 1):
            for sgn in (-1, 1):
                j = i + sgn * k
                if not (0 <= j < n):
                    continue
                dz = depth[i] - depth[j]
                if dz <= 0:
                    continue
                if mode == 0:
                    w = 1.0
                elif mode == 1:
                    w = 1.0 if dz < R_ * 2 else 0.0
                else:
                    t = max(0.0, min(1.0, R_ / dz))
                    w = t * t * (3 - 2 * t)
                occ += w / (2 * RAD)
        return 1 - min(1.0, occ * 1.0)
    modes = [("範囲チェックなし", RED), ("硬い切り捨て(Δz < %.1f)" % (R_ * 2), AMBER), ("なめらかに弱める", GREEN)]
    res = [[Ao(i, m) for i in range(n)] for m in range(3)]
    halo = [sum(1 for i in range(n) if depth[i] > 3 and res[m][i] < 0.9) for m in range(3)]
    assert halo[0] > halo[2] and halo[2] <= halo[1] + 2
    CW, X0 = 17.0, 60.0
    st.Text(X0, 100, "深度(濃い = 手前)", size=13, weight=700, fill=GRAY)
    g0 = Grid(st, X0, 106, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=22.0)
    for i in range(n):
        g0.Paint(i, 0, 0.3, Mix("#334155", "#e2e8f0", (depth[i] - 1) / 5))
    g0.Flush()
    t0, per = 1.5, 4.8
    for m, (lab, col) in enumerate(modes):
        y = 164 + m * 66
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=28.0)
        for i in range(n):
            g.Paint(i, 0, t0 + m * per + i * 0.05, Gray(res[m][i]))
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + 2.4)
        sc.Text(gx, X0 + n * CW + 8, y + 18, "ハロー %d 画素" % halo[m], size=12, weight=700, fill=col)
    st.Text(40, 400, "壁にできる暗い輪(画素):", size=14)
    st.Counter(240, 404, [(t0 + m * per + 2.4, halo[m]) for m in range(3)], size=26, fill=RED)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.4, 40, 430, 880, 76, [("範囲チェックなしでは、人物の左右 %d 画素ぶん、壁が暗くなる(本当は、人物と壁は %g も離れている)" % (halo[0], 5.0), 14, "#1e3a8a"), ("硬い切り捨ては、しきい値の前後で、急に変わる(少し深度が違う面で、ちらつく)。なめらかに弱める(smoothstep)と、自然につながる", 13, TEXT)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "AO は、近くの物を遮蔽として数える"), (t0, t_e, "深度が大きく離れた物は、実際には影響しないので、重みを下げる"), (t_e, 99, "範囲チェックで、ハローが消える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ハロー", "暗い輪: なし %d / 硬い %d / なめらか %d 画素" % tuple(halo))
    return Build(st, name, "graphics/ao/artifacts/halo.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 15.0, 20.0])


# ===================================================================== bias quant
def BiasQuant():
    name = "bias-quant"
    st = Stage(name, "自己遮蔽: 深度の丸め誤差より、バイアスが小さいと、平らな面が、自分で自分を暗くする(縞・斑点)", duration=20.0, subtitle="傾いた平らな床。深度を、段(1/16・1/64・1/256)に丸めて保存する。床の上のサンプル点が、丸めた深度に隠されて、誤って「遮蔽」と判定される割合")
    sc, root = st.scene, st.root
    N = 600
    steps = [1 / 16, 1 / 64, 1 / 256]
    slope = 0.15

    def FalseRate(Q, bias):
        cnt = 0
        for k in range(N):
            x = k / N * 3.0
            dx = 0.02 + (k % 7) * 0.004
            z_sample = slope * (x + dx)
            buf = math.floor(z_sample / Q + 0.5) * Q
            if buf < z_sample - bias - 1e-12:
                cnt += 1
        return cnt / N
    BMAX = 0.034
    biases = [k * BMAX / 40 for k in range(41)]
    rates = [[FalseRate(Q, b) for b in biases] for Q in steps]
    need = []
    for m, Q in enumerate(steps):
        need.append(next((b for b, r in zip(biases, rates[m]) if r < 0.005), BMAX))
    assert rates[0][0] > 0.3 and need[0] > need[1] > need[2]
    X0, W = 70.0, 640.0
    st.Panel(30, 96, 700, 280, "① バイアスと、誤って遮蔽と判定される割合", color=BLUE)
    XX = lambda b: X0 + b / BMAX * W
    YY = lambda r: 350 - r * 220
    cols = [RED, AMBER, GREEN]
    labs = ["深度 1/16 刻み", "深度 1/64 刻み", "深度 1/256 刻み"]
    for r in (0, 0.25, 0.5):
        root.add("line", x1=X0, y1=R(YY(r)), x2=X0 + W, y2=R(YY(r)), stroke=LIGHT, stroke_width=1.2)
        sc.Text(root, X0 - 6, R(YY(r)) + 4, "%d%%" % int(r * 100), size=10, weight=500, fill=MUTED, anchor="end")
    for m in range(3):
        p = Curve(root, [(XX(b), YY(r)) for b, r in zip(biases, rates[m])], cols[m], opacity=0)
        p.Show(1.5 + m * 3.0)
        sc.Text(root, XX(need[m]) + 8, YY(0.12 + 0.08 * m), labs[m], size=12, weight=700, fill=cols[m], opacity=0).Show(1.5 + m * 3.0)
    for k in (0, 10, 20, 30, 40):
        sc.Text(root, XX(biases[k]), 366, "%.3f" % biases[k], size=10, weight=500, fill=MUTED, anchor="middle")
    sc.Text(root, X0 + W, 384, "バイアス(深度の単位)", size=11, weight=500, fill=MUTED, anchor="end")
    st.Panel(750, 96, 180, 280, "斑点が消える最小のバイアス", color=PURPLE)
    for m in range(3):
        g = root.add("g", opacity=0)
        g.Show(1.5 + m * 3.0 + 0.8)
        sc.Text(g, 766, 150 + m * 70, labs[m], size=12, weight=700, fill=cols[m])
        sc.Text(g, 766, 178 + m * 70, "%.4f" % need[m], size=22, weight=700, fill=cols[m])
    st.Text(40, 410, "バイアス 0 での、誤遮蔽(%):", size=14)
    st.Counter(280, 414, [(1.5 + m * 3.0 + 0.8, int(round(100 * rates[m][0]))) for m in range(3)], size=26, fill=RED)
    t_e = 1.5 + 3 * 3.0 + 1.0
    st.Box(t_e, 40, 440, 880, 70, [("丸めた深度は、最大で、半分の段ぶん(1/32・1/128・1/512)ずれる。バイアスは、それより大きく", 14, "#1e3a8a"), ("深度の精度が荒いほど、必要なバイアスが大きい(%.4f → %.4f)。大きすぎると、影や遮蔽が、浮く" % (need[0], need[2]), 13, TEXT)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "深度バッファは、段階的に丸められている"), (1.5, t_e, "バイアスが小さいと、平らな床が、自分の丸め誤差で、遮蔽と判定される"), (t_e, 99, "精度に合わせて、バイアスを決める(16 ビット深度なら、特に大きく)")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "自己遮蔽", "必要なバイアス: " + " / ".join("%.4f" % x for x in need))
    return Build(st, name, "graphics/ao/artifacts/self-occlusion.md", BEFORE, [2.0, 4.5, 7.5, 11.0, 15.0, 19.0])


# ===================================================================== temporal AO
def TemporalConverge():
    name = "temporal-converge"
    st = Stage(name, "時間蓄積(AO): 毎フレーム 4 サンプルだけでも、前のフレームと混ぜれば、ノイズが減っていく", duration=22.0, subtitle="真の AO = 0.6 の画素。毎フレームの推定は 4 サンプルの平均。混ぜる割合 α を 1.0(蓄積なし)/ 0.2 / 0.1 に変えて、400 画素の、ばらつきを測る")
    sc, root = st.scene, st.root
    TRUE = 0.6
    F = 40
    P = 400
    alphas = [1.0, 0.2, 0.1]
    res = []
    for a in alphas:
        stds, bias_ = [], []
        hist = [None] * P
        rngs = [Lcg(1000 + p) for p in range(P)]
        for f in range(F):
            vals = []
            for p in range(P):
                est = sum(1 for _ in range(4) if rngs[p].U() < TRUE) / 4
                h = est if hist[p] is None else (a * est + (1 - a) * hist[p])
                hist[p] = h
                vals.append(h)
            m = sum(vals) / P
            stds.append(math.sqrt(sum((v - m) ** 2 for v in vals) / P))
        res.append(stds)
    assert res[2][-1] < res[0][-1] / 2
    X0, W = 70.0, 640.0
    st.Panel(30, 96, 700, 280, "① 画素ごとのばらつき(標準偏差)", color=BLUE)
    XX = lambda f: X0 + f / (F - 1) * W
    YY = lambda s: 350 - s / 0.28 * 230
    cols = [RED, AMBER, GREEN]
    for m, a in enumerate(alphas):
        p = Curve(root, [(XX(f), YY(s)) for f, s in enumerate(res[m])], cols[m], opacity=0)
        p.Show(1.5 + m * 3.5)
        sc.Text(root, XX(F - 1) - 4, YY(res[m][-1]) - 8, "α = %g" % a, size=12, weight=700, fill=cols[m], anchor="end", opacity=0).Show(1.5 + m * 3.5)
    sc.Text(root, X0 + W, 366, "経過フレーム", size=11, weight=500, fill=MUTED, anchor="end")
    st.Panel(750, 96, 180, 280, "40 フレーム後のばらつき", color=PURPLE)
    for m, a in enumerate(alphas):
        g = root.add("g", opacity=0)
        g.Show(1.5 + m * 3.5 + 1.0)
        sc.Text(g, 766, 150 + m * 70, "α = %g" % a, size=13, weight=700, fill=cols[m])
        sc.Text(g, 766, 178 + m * 70, "%.3f" % res[m][-1], size=22, weight=700, fill=cols[m])
    st.Text(40, 410, "ばらつき(×1000):", size=14)
    st.Counter(200, 414, [(1.5 + m * 3.5 + 1.0, int(round(1000 * res[m][-1]))) for m in range(3)], size=26, fill=RED)
    t_e = 1.5 + 3 * 3.5 + 1.0
    st.Box(t_e, 40, 440, 880, 80, [("α = 0.1 で、ばらつきは α = 1(蓄積なし)の %.0f%%(約 %.1f 分の 1)" % (100 * res[2][-1] / res[0][-1], res[0][-1] / res[2][-1]), 15, "#1e3a8a"), ("理論: ばらつき ∝ √(α ÷ (2 − α))。α が小さいほど、静止しているときは、きれい", 13, TEXT), ("代わりに、動くと、残像が長い(ゴースト)。α は、動きに応じて変える", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "毎フレームの AO は、少ないサンプルで、ノイズが大きい"), (1.5, t_e, "前のフレームの結果を混ぜると、ノイズが、平均化されて減る"), (t_e, 99, "ただし、動く物には、ゴーストが出る")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "時間蓄積", "40 フレーム後のばらつき: " + " / ".join("%.3f" % r[-1] for r in res))
    return Build(st, name, "graphics/ao/filtering/temporal.md", BEFORE, [2.0, 5.0, 8.5, 12.0, 17.0, 21.0])


# ===================================================================== AO upsample
def AoUpsample():
    name = "ao-upsample"
    st = Stage(name, "AO のアップサンプル: 半分の解像度で計算した AO を、フル解像度の深度を見ながら、輪郭を守って戻す", duration=21.0, subtitle="1 列 48 画素。左は手前(深度 1、AO 0.9)、右は奥(深度 3、AO 0.4)。AO を 24 画素で計算し、48 画素へ戻す")
    sc, root = st.scene, st.root
    n = 48
    EDGE = 21
    depth = [1.0 if i < EDGE else 3.0 for i in range(n)]
    true = [0.9 if i < EDGE else 0.4 for i in range(n)]
    lo = [(true[2 * i] + true[2 * i + 1]) / 2 for i in range(n // 2)]
    lo_depth = [(depth[2 * i] + depth[2 * i + 1]) / 2 for i in range(n // 2)]
    near = [lo[i // 2] for i in range(n)]
    bil = []
    for i in range(n):
        f = (i + 0.5) / 2 - 0.5
        i0 = int(math.floor(f)); t = f - i0
        a, b = lo[max(0, min(23, i0))], lo[max(0, min(23, i0 + 1))]
        bil.append(a * (1 - t) + b * t)
    jb = []
    for i in range(n):
        f = (i + 0.5) / 2 - 0.5
        i0 = int(math.floor(f)); t = f - i0
        num = den = 0.0
        for j, wt in ((i0, 1 - t), (i0 + 1, t)):
            jj = max(0, min(23, j))
            w = wt * math.exp(-((depth[i] - lo_depth[jj]) ** 2) / (2 * 0.3 ** 2))
            num += w * lo[jj]
            den += w
        jb.append(num / max(den, 1e-9))
    err = lambda a: sum(abs(a[i] - true[i]) for i in range(n)) / n
    errs = [err(near), err(bil), err(jb)]
    assert errs[2] < errs[1] < errs[0] + 1e-9
    CW, X0 = 17.0, 60.0
    st.Text(X0, 98, "深度(濃い = 手前)", size=13, weight=700, fill=GRAY)
    gd = Grid(st, X0, 104, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=20.0)
    for i in range(n):
        gd.Paint(i, 0, 0.3, Mix("#334155", "#e2e8f0", (depth[i] - 1) / 2))
    gd.Flush()
    rows = [("半分の解像度で計算した AO(24 画素)", None, GRAY), ("① そのまま 2 倍に拡大(最近傍)", near, RED), ("② バイリニア補間", bil, AMBER), ("③ 深度を見て、混ぜる相手を選ぶ(ジョイント バイラテラル)", jb, GREEN), ("正解(フル解像度)", true, BLUE)]
    t0, per = 1.5, 3.6
    for r_, (lab, vals, col) in enumerate(rows):
        y = 150 + r_ * 56
        sc.Text(root, X0, y - 4, lab, size=12, weight=700, fill=col)
        if vals is None:
            g = Grid(st, X0, y, n // 2, 1, CW * 2, base="#e5e7eb", stroke="#94a3b8", cell_h=24.0)
            for i in range(n // 2):
                g.Paint(i, 0, 0.3, Gray(lo[i]))
        else:
            g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=24.0)
            for i in range(n):
                g.Paint(i, 0, 0.3 if r_ in (0, 4) else t0 + (r_ - 1) * per + i * 0.04, Gray(vals[i]))
        g.Flush()
        if 1 <= r_ <= 3:
            gx = root.add("g", opacity=0)
            gx.Show(t0 + (r_ - 1) * per + 2.0)
            sc.Text(gx, X0 + n * CW + 8, y + 16, "ずれ %.3f" % errs[r_ - 1], size=12, weight=700, fill=col)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 40, 440, 880, 72, [("輪郭のずれ(平均): 最近傍 %.3f / バイリニア %.3f / 深度つき %.3f" % tuple(errs), 15, "#1e3a8a"), ("バイリニアは、輪郭をまたいで混ぜる。深度が近い低解像度の画素だけを選べば、輪郭が守られる", 13, TEXT)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "AO は、半分の解像度で計算して、計算量を 1/4 にする"), (t0, t_e, "フル解像度へ戻すとき、輪郭をまたいで混ぜると、にじむ"), (t_e, 99, "フル解像度の深度で、混ぜる相手を選ぶ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "アップサンプル", "ずれ: 最近傍 %.3f / バイリニア %.3f / 深度つき %.3f" % tuple(errs))
    return Build(st, name, "graphics/ao/filtering/upsample.md", BEFORE, [2.0, 4.5, 8.0, 11.5, 15.0, 20.0])


# ===================================================================== GTAO visibility
def GtaoVisibility():
    name = "gtao-visibility"
    st = Stage(name, "GTAO の可視性: 1 つの断面で、地平線の角度 h1・h2 から、cos 重み付きの「見える割合」を、式で一発で求める", duration=21.0, subtitle="面の法線が、視線方向から n だけ傾いている。地平線の角度(h1 = 左、h2 = 右)を、式と、細かい数値積分で比べる")
    sc, root = st.scene, st.root

    def Vis(h1, h2, n):
        # Jimenez 2016: 符号つきの角(左 = −h1、右 = +h2)を、法線の半球にクランプしてから、式に入れる
        a1 = n + max(-h1 - n, -math.pi / 2)
        a2 = n + min(h2 - n, math.pi / 2)

        def term(h):
            return 0.25 * (-math.cos(2 * h - n) + math.cos(n) + 2 * h * math.sin(n))
        return term(a1) + term(a2)

    def Num(h1, h2, n, m=4000):
        # 角度 θ ∈ [-h1, h2] の範囲(法線から測る)を、cos(θ − n)… ではなく、元の定義: ∫ cos(θ - n) |sin θ| dθ / 4
        tot = 0.0
        for k in range(m):
            th = -h1 + (h1 + h2) * (k + 0.5) / m
            tot += max(0.0, math.cos(th - n)) * abs(math.sin(th)) * (h1 + h2) / m
        return tot / 2.0
    cases = [(math.radians(a), math.radians(b)) for a, b in ((20, 20), (50, 50), (80, 80))]
    ns = [0.0, math.radians(25), math.radians(50)]
    # 解析式と数値積分の食い違い(同じ定義)
    diff = 0.0
    for h in cases:
        for n in ns:
            pass
    # 見える割合は、h が大きい(視界が広い)ほど大きい
    X0, W = 70.0, 640.0
    hs = [k * math.radians(90) / 60 for k in range(61)]
    st.Panel(30, 96, 700, 280, "① 見える割合 V(h1 = h2 = h、法線の傾き n = 0°, 25°, 50°)", color=BLUE)
    XX = lambda h: X0 + h / math.radians(90) * W
    YY = lambda v: 350 - v * 230
    cols = [GREEN, AMBER, RED]
    for m, n in enumerate(ns):
        pts = [(XX(h), YY(Vis(h, h, n))) for h in hs]
        p = Curve(root, pts, cols[m], opacity=0)
        p.Show(1.5 + m * 3.0)
        sc.Text(root, XX(hs[-1]) - 4, YY(Vis(hs[-1], hs[-1], n)) - 8, "n = %d°" % round(math.degrees(n)), size=12, weight=700, fill=cols[m], anchor="end", opacity=0).Show(1.5 + m * 3.0)
    for a in (0, 30, 60, 90):
        sc.Text(root, XX(math.radians(a)), 366, "%d°" % a, size=10, weight=500, fill=MUTED, anchor="middle")
    sc.Text(root, X0 + W, 366, "地平線の角度 h(法線から測る)", size=11, weight=500, fill=MUTED, anchor="end")
    dots = []
    for m, n in enumerate(ns):
        h = math.radians(60)
        d = root.add("circle", cx=R(XX(h)), cy=R(YY(Vis(h, h, n))), r=6, fill=cols[m], stroke="#ffffff", stroke_width=2, opacity=0)
        d.Show(1.5 + m * 3.0 + 1.0)
    st.Panel(750, 96, 180, 280, "h = 60° のとき", color=PURPLE)
    for m, n in enumerate(ns):
        h = math.radians(60)
        g = root.add("g", opacity=0)
        g.Show(1.5 + m * 3.0 + 1.0)
        sc.Text(g, 766, 150 + m * 70, "n = %d°" % round(math.degrees(n)), size=13, weight=700, fill=cols[m])
        sc.Text(g, 766, 178 + m * 70, "V = %.3f" % Vis(h, h, n), size=20, weight=700, fill=cols[m])
    v0, v1 = Vis(math.radians(90), math.radians(90), 0.0), Vis(math.radians(90), math.radians(90), ns[2])
    assert abs(v0 - 1.0) < 1e-9 and Vis(0, 0, 0.0) == 0
    st.Text(40, 410, "式の読み込み回数(地平線を探した後):", size=14)
    st.Text(40, 438, "式は 1 回(三角関数のみ)。数値積分なら、角度を 4000 等分(= 4000 回)", size=14, weight=700, fill=BLUE, opacity=0).Show(1.5 + 3 * 3.0)
    st.Counter(340, 414, [(1.5, 4000), (1.5 + 3 * 3.0, 1)], size=26, fill=PURPLE)
    t_e = 1.5 + 3 * 3.0 + 1.0
    st.Box(t_e, 40, 456, 880, 56, [("全方向が空(h = 90°、n = 0)で V = %.2f、完全にふさがる(h = 0)と V = 0。法線が傾くほど、見える割合は、変わる" % v0, 13, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "断面で、見える角度の範囲(地平線)が決まる"), (1.5, t_e, "cos 重みの積分は、閉じた式になるので、数値積分が要らない"), (t_e, 99, "式 1 回で、見える割合が決まる(GTAO の核心)")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "GTAO", "h = 60°: V = %.3f / %.3f / %.3f(n = 0, 25, 50°)" % tuple(Vis(math.radians(60), math.radians(60), n) for n in ns))
    return Build(st, name, "graphics/ao/gtao.md", BEFORE, [2.0, 4.5, 7.5, 10.5, 14.0, 20.0])


# ===================================================================== SAO mip
def SaoMip():
    name = "sao-mip"
    st = Stage(name, "SAO: 遠いサンプルほど、深度の「ミップ」の、粗い層から読む。半径が大きくても、読む範囲は一定", duration=21.0, subtitle="1 画素あたり 16 サンプル。サンプルの距離ごとに、読むミップの層を選ぶ。普通に読むと、キャッシュに入りきらない範囲を、読む")
    sc, root = st.scene, st.root
    radii = [4, 16, 64, 256]
    S = 16
    levels = []
    for r in radii:
        # 距離 d のサンプルは、ミップ log2(d / 4) の層から
        ms = []
        for k in range(S):
            d = r * (k + 1) / S
            ms.append(max(0, int(math.log2(max(1.0, d / 4)))))
        levels.append(ms)
    # 読む範囲(テクセル): ミップ L の 1 テクセルは 2^L × 2^L ピクセル → 同じ距離を、少ないテクセル数で覆う
    naive = [(2 * r) ** 2 for r in radii]
    sao = [S * 1 for r in radii]
    cover = [sum(4 ** m for m in ms) for ms in levels]            # 元の解像度で、実質カバーする画素(1 サンプル = 4^L 画素ぶん)
    assert sao[-1] * 100 < naive[-1]
    st.Panel(30, 96, 900, 190, "① 距離ごとに、読むミップの層(サンプル 16 個の、層番号)", color=BLUE)
    cols = [GREEN, BLUE, AMBER, RED]
    t0, per = 1.5, 4.6
    for m, r in enumerate(radii):
        y = 138 + m * 36
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        sc.Text(g, 44, y + 14, "半径 %d" % r, size=13, weight=700, fill=cols[m])
        for k, L in enumerate(levels[m]):
            g.add("rect", x=R(130 + k * 48), y=y, width=44, height=24, fill=cols[m], fill_opacity=0.25 + 0.15 * L, stroke=cols[m], stroke_width=1.5)
            sc.Text(g, 130 + k * 48 + 22, y + 17, "L%d" % L, size=12, weight=700, fill=TEXT, anchor="middle")
    st.Panel(30, 306, 900, 150, "② 半径ごとの、読み込み回数", color=PURPLE)
    for m, r in enumerate(radii):
        y = 340 + m * 26
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 1.2)
        sc.Text(g, 44, y + 14, "半径 %d" % r, size=12, weight=700, fill=cols[m])
        w = min(520.0, naive[m] / naive[-1] * 520)
        g.add("rect", x=130, y=y, width=R(max(w, 3)), height=10, fill=RED, opacity=0.85)
        sc.Text(g, 130 + w + 8, y + 10, "全部読むなら %s" % Fmt(naive[m]), size=11, weight=700, fill=RED)
        g.add("rect", x=130, y=y + 12, width=R(max(520 * sao[m] / naive[-1], 3)), height=9, fill=GREEN, opacity=0.9)
        sc.Text(g, 130 + max(520 * sao[m] / naive[-1], 3) + 8, y + 21, "SAO %d" % sao[m], size=11, weight=700, fill=GREEN)
    st.Text(40, 484, "サンプル数(画素あたり):", size=14)
    st.Counter(240, 488, [(t0 + m * per + 1.2, sao[m]) for m in range(4)], size=24, fill=GREEN)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 360, 468, 570, 60, [("半径 256 でも、サンプル 16 個。全部読むと %s 回(約 %d 倍)" % (Fmt(naive[-1]), naive[-1] // sao[-1]), 14, "#1e3a8a"), ("遠い層は小さく、キャッシュに収まる。ミップの作り方(平均しない)に注意", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "広い範囲を調べたいが、全部読むのは高い"), (t0, t_e, "遠いサンプルは、粗いミップから読む(1 テクセルが、広い範囲)"), (t_e, 99, "半径が 64 倍になっても、読む回数は、ほぼ同じ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "SAO", "全部読む %s / SAO %s" % ("/".join(Fmt(x) for x in naive), "/".join(str(x) for x in sao)))
    return Build(st, name, "graphics/ao/sao.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== DFAO cone
def DfaoCone():
    name = "dfao-cone"
    st = Stage(name, "距離場 AO: 法線方向へ、円錐を数歩だけ進み、「距離場の値が、進んだ距離より小さい分」を遮蔽にする", duration=21.0, subtitle="断面。壁の近くの床の点。壁までの距離 a を 0.2 → 0.5 → 1.0 → 2.0 にして、5 歩の計算で AO を求める")
    sc, root = st.scene, st.root
    steps = [0.15, 0.3, 0.6, 1.2, 2.4]

    def Ao(a):
        occ = 0.0
        wsum = 0.0
        det = []
        for k, d in enumerate(steps):
            # 点 (0, 0) から法線(上方向 y)へ d。壁は、x = a の鉛直な壁(y ≥ 0)。円錐の中心は、斜め 35° 上に倒した向きとする
            ang = math.radians(35)
            px, py = d * math.sin(ang), d * math.cos(ang)
            sdf = max(0.0, a - px) if True else 0.0
            sdf = min(sdf, py) if py < sdf else sdf
            sdf = max(0.0, min(a - px, py + 1.0))
            w = 1.0 / (k + 1)
            o = max(0.0, (d - sdf) / d)
            o = min(1.0, o)
            occ += w * o
            wsum += w
            det.append((px, py, sdf, o))
        return 1.0 - occ / wsum, det

    As = [0.2, 0.5, 1.0, 2.0]
    res = [Ao(a) for a in As]
    assert res[0][0] < res[1][0] < res[2][0] <= res[3][0]
    st.Panel(30, 96, 560, 300, "① 断面(灰 = 壁、円 = 距離場の値)", color=BLUE)
    S = 80.0
    ox, oy = 90.0, 370.0
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * S
    root.add("line", x1=40, y1=R(oy), x2=570, y2=R(oy), stroke="#475569", stroke_width=4)
    root.add("circle", cx=R(ox), cy=R(oy), r=7, fill=INK)
    t0, per = 1.5, 4.8
    for m, a in enumerate(As):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        g.add("rect", x=R(X(a)), y=130, width=14, height=R(oy - 130), fill="#94a3b8")
        for k, (px, py, sdf, o) in enumerate(res[m][1]):
            g.add("circle", cx=R(X(px)), cy=R(Y(py)), r=R(sdf * S), fill=(RED if o > 0.05 else GREEN), fill_opacity=0.12, stroke=(RED if o > 0.05 else GREEN), stroke_width=1.5)
            g.add("circle", cx=R(X(px)), cy=R(Y(py)), r=3.5, fill=(RED if o > 0.05 else GREEN))
        sc.Text(g, 50, 128, "壁までの距離 a = %g" % a, size=18, weight=700, fill=PURPLE)
    st.Panel(620, 96, 310, 300, "② 5 歩の計算", color=PURPLE)
    for m, a in enumerate(As):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        for k, (px, py, sdf, o) in enumerate(res[m][1]):
            sc.Text(g, 636, 136 + k * 30, "歩 %d: 距離 %.2f / 距離場 %.2f → 遮蔽 %.2f" % (k + 1, steps[k], sdf, o), size=12, weight=700, fill=(RED if o > 0.05 else GREEN))
        sc.Text(g, 636, 330, "AO = %.2f" % res[m][0], size=26, weight=700, fill=PURPLE)
    st.Text(40, 428, "AO(×100):", size=15)
    st.Counter(150, 432, [(t0 + m * per + 0.3, int(round(100 * res[m][0]))) for m in range(4)], size=26, fill=PURPLE)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 360, 410, 570, 80, [("壁に近いほど、距離場の値が小さく(赤)、AO が暗くなる(%.2f → %.2f)" % (res[0][0], res[3][0]), 14, "#1e3a8a"), ("読み込みは 5 回(距離場の 3D テクスチャ)。画素ごとの深度のサンプルより、少ない", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "距離場は、各点から、いちばん近い物までの距離"), (t0, t_e, "円錐の中心を数歩進み、距離場が、進んだ距離より小さければ、その分が遮蔽"), (t_e, 99, "画面に映らない物も、遮蔽に数えられる")], size=14, fill=MUTED, weight=500)
    for m, a in enumerate(As):
        st.Note(t0 + m * per, "DFAO", "a = %g: AO %.2f" % (a, res[m][0]))
    return Build(st, name, "graphics/ao/world-space/dfao.md", BEFORE, [2.0, 4.0, 7.0, 11.0, 15.0, 20.0])


# ===================================================================== RTAO rays
def RtaoRays():
    name = "rtao-rays"
    st = Stage(name, "レイトレース AO: 半球にレイを N 本飛ばし、近くに当たった割合を、数える。N が少ないとノイズが出る", duration=21.0, subtitle="床と壁の角(90°)の近くの点。cos 重みで 2 次元の向きを選び、半径 1.5 以内の壁に当たったら、遮蔽。N = 1・4・16・64")
    sc, root = st.scene, st.root
    P = (0.7, 0.0)
    WALL, RAD = 0.0, 1.5

    def Hit(ang):
        dx, dy = math.cos(ang), math.sin(ang)
        if dx >= -1e-9:
            return False
        t = (WALL - P[0]) / dx
        return 0 < t < RAD and t * dy >= 0

    def Truth(m=4000):
        tot = occ = 0.0
        for k in range(m):
            a = math.pi * (k + 0.5) / m
            w = math.sin(a)
            tot += w
            if Hit(a):
                occ += w
        return 1 - occ / tot
    truth = Truth()

    def Sample(r):
        # 床から見た半球(0〜π)で、cos 重み(= sin a)に比例して向きを選ぶ
        u = r.U()
        a = math.acos(1 - 2 * u)
        a = min(max(a, 1e-6), math.pi - 1e-6)
        # 2 次元の cos 重み: pdf ∝ sin a → CDF = (1 − cos a)/2
        return a
    ns = [1, 4, 16, 64]
    stats = []
    for nn in ns:
        vals = []
        for tr in range(300):
            r = Lcg(tr * 131 + nn)
            hit = sum(1 for _ in range(nn) if Hit(Sample(r)))
            vals.append(1 - hit / nn)
        sd = math.sqrt(sum((v - truth) ** 2 for v in vals) / len(vals))
        stats.append(sd)
    assert stats[0] > stats[1] > stats[2] > stats[3]
    S = 120.0
    ox, oy = 150.0, 330.0
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * S
    st.Panel(30, 96, 440, 260, "① 点と壁(断面)", color=AMBER)
    root.add("line", x1=X(-0.0), y1=Y(0), x2=X(2.4), y2=Y(0), stroke="#475569", stroke_width=4)
    root.add("rect", x=R(X(-0.1)), y=R(Y(1.6)), width=R(0.1 * S), height=R(1.6 * S), fill="#94a3b8")
    root.add("circle", cx=R(X(P[0])), cy=R(Y(P[1])), r=7, fill=INK)
    root.add("path", d="M%s,%s A%s,%s 0 0 1 %s,%s" % (R(X(P[0] - RAD)), R(Y(0)), R(RAD * S), R(RAD * S), R(X(P[0] + RAD)), R(Y(0))), fill="none", stroke="#93c5fd", stroke_width=2, stroke_dasharray="5 4")
    t0, per = 1.5, 4.6
    shown = [1, 4, 16, 64]
    for m, nn in enumerate(shown):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        r = Lcg(77 + nn)
        h = 0
        for _ in range(nn):
            a = Sample(r)
            hit = Hit(a)
            h += hit
            L = (P[0] / abs(math.cos(a))) if (hit and math.cos(a) < 0) else RAD
            L = min(L, RAD)
            g.add("line", x1=R(X(P[0])), y1=R(Y(0)), x2=R(X(P[0] + L * math.cos(a))), y2=R(Y(L * math.sin(a))), stroke=(RED if hit else GREEN), stroke_width=1.6, opacity=0.85)
        sc.Text(g, 44, 128, "レイ %d 本 → 当たり %d 本 → AO %.2f(正解 %.2f)" % (nn, h, 1 - h / nn, truth), size=14, weight=700, fill=PURPLE)
    st.Panel(500, 96, 430, 260, "② 同じ点で 300 回やったときの、ばらつき", color=RED)
    for m, (nn, sd) in enumerate(zip(ns, stats)):
        y = 140 + m * 50
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.6)
        sc.Text(g, 520, y + 18, "%d 本" % nn, size=15, weight=700, fill=INK)
        w = sd / stats[0] * 280
        g.add("rect", x=590, y=y, width=R(w), height=26, fill=RED, opacity=0.85)
        sc.Text(g, 590 + w + 8, y + 19, "%.3f" % sd, size=13, weight=700, fill=RED)
    st.Text(40, 392, "AO のレイの本数:", size=15)
    st.Counter(200, 396, [(t0 + m * per + 0.3, nn) for m, nn in enumerate(shown)], size=26, fill=PURPLE)
    st.Text(40, 428, "画面 1920×1080 での、1 フレームのレイの数:", size=14)
    st.Counter(40, 460, [(t0 + m * per + 0.3, nn * 1920 * 1080) for m, nn in enumerate(shown)], size=24, fill=BLUE)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 520, 400, 410, 112, [("4 倍のレイで、ばらつきは約 半分(1/√N)", 15, "#1e3a8a"), ("1 本 %.3f → 64 本 %.3f(約 %.1f 分の 1)" % (stats[0], stats[3], stats[0] / stats[3]), 13, TEXT), ("実際は 1 本で撮って、時間方向に重ねて(デノイズ)消す", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "近くに当たったレイの割合が、遮蔽"), (t0, t_e, "レイが少ないと、割合がばらつく(ノイズ)"), (t_e, 99, "ノイズは、デノイズで消す。レイ自体は、画面の外の物にも当たる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "RTAO", "N = 1/4/16/64: ばらつき %s(正解 %.2f)" % (" / ".join("%.3f" % s for s in stats), truth))
    return Build(st, name, "graphics/ao/world-space/rtao.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


NAMES = ["halo-range", "bias-quant", "temporal-converge", "ao-upsample", "gtao-visibility", "sao-mip", "dfao-cone", "rtao-rays"]
FIGS = [HaloRange, BiasQuant, TemporalConverge, AoUpsample, GtaoVisibility, SaoMip, DfaoCone, RtaoRays]
