import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_gi import Track  # noqa: E402

BEFORE = "## よくあるミス"
LIT, DARKC = "#fde68a", "#334155"


# ===================================================================== PCSS
def PcssPenumbra():
    name = "pcss-penumbra"
    st = Stage(name, "PCSS: 遮る物から受ける面までが遠いほど、影の縁(半影)が広がる", duration=21.0, subtitle="断面。面積のある光(幅 4)の下に遮る板。受ける床を 3 通りの高さに動かして、実際に光を数える")
    sc, root = st.scene, st.root
    LW, BW = 4.0, 3.0
    cx, bx = 8.0, 8.0
    yb = 3.0                       # 遮る板の高さ(光の下)
    yrs = [4.5, 7.0, 11.0]          # 受ける面の位置(光からの距離)
    NS = 64                         # 光のサンプル数
    NC = 40
    X0, SX = 60.0, 52.0
    Y0, SY = 120.0, 20.0
    UX = lambda x: X0 + x * SX
    UY = lambda y: Y0 + y * SY

    def Vis(X, yr):
        lit = 0
        for s in range(NS):
            lx = cx - LW / 2 + LW * (s + 0.5) / NS
            t = yb / yr
            xx = lx + (X - lx) * t
            if abs(xx - bx) <= BW / 2:
                continue
            lit += 1
        return lit / NS

    def Pen(yr):
        # 影の濃さが 0.05〜0.95 の範囲の幅(横方向)
        xs = [i * 0.01 for i in range(0, 1601)]
        vs = [Vis(x, yr) for x in xs]
        left = [x for x, v in zip(xs, vs) if 0.02 < v < 0.98 and x < bx]
        return (max(left) - min(left)) if left else 0.0

    pens = [Pen(yr) for yr in yrs]
    theo = [LW * (yr - yb) / yb for yr in yrs]
    assert pens[0] < pens[1] < pens[2], pens
    st.Panel(30, 96, 900, 300, "① 光・遮る板・受ける面(断面)", color=AMBER)
    root.add("rect", x=R(UX(cx - LW / 2)), y=R(UY(0) - 10), width=R(LW * SX), height=10, fill=AMBER)
    sc.Text(root, UX(cx), UY(0) - 16, "面積のある光(幅 %g)" % LW, size=13, weight=700, fill="#92400e", anchor="middle")
    root.add("rect", x=R(UX(bx - BW / 2)), y=R(UY(yb)), width=R(BW * SX), height=8, fill="#475569")
    sc.Text(root, UX(bx), UY(yb) - 6, "遮る板", size=12, weight=700, fill="#475569", anchor="middle")
    # 受ける面の位置ごと
    t0, per = 1.0, 6.2
    for m, yr in enumerate(yrs):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        g.add("line", x1=R(UX(0)), y1=R(UY(yr)), x2=R(UX(16)), y2=R(UY(yr)), stroke="#94a3b8", stroke_width=3)
        # 光の端から、板の端を通る線
        for lx in (cx - LW / 2, cx + LW / 2):
            for ex in (bx - BW / 2, bx + BW / 2):
                t = yr / yb
                fx = lx + (ex - lx) * t
                g.add("line", x1=R(UX(lx)), y1=R(UY(0)), x2=R(UX(fx)), y2=R(UY(yr)), stroke="#fbbf24", stroke_width=1, stroke_dasharray="3 4", opacity=0.9)
        sc.Text(g, 40, UY(yr) + 18, "受ける面: 光から %g(板から %g)" % (yr, yr - yb), size=12, weight=700, fill=MUTED)
        # 結果の帯(40 マス)
        grid = Grid(st, X0, 346 + 0, NC, 1, 16.0 * SX / NC, base="#e5e7eb", parent=g, stroke="#94a3b8")
        for i in range(NC):
            X = 16.0 * (i + 0.5) / NC
            v = Vis(X, yr)
            grid.Paint(i, 0, t0 + m * per + 0.5 + 0.05 * i, Mix(DARKC, LIT, v))
        grid.Flush()
    sc.Text(root, 60, 340, "受ける面での光の当たり方(黄 = 全部届く、暗い = 全部隠れる)", size=12, weight=500, fill=MUTED)
    # 数値
    ser_t = [t0 + m * per + 0.3 for m in range(3)]
    for m in range(3):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        sc.Text(g, 60, 418, "半影の幅(実測): %.2f" % pens[m], size=18, weight=700, fill=RED)
        sc.Text(g, 360, 418, "相似三角形: 光の幅 × 板から受ける面まで ÷ 光から板まで = %g × %g ÷ %g = %.2f" % (LW, yrs[m] - yb, yb, theo[m]), size=13, weight=500, fill=TEXT)
        sc.Text(g, 60, 446, ["板に近い: 縁がくっきり(接触した影)", "少し離れる: 縁がぼやけ始める", "さらに離れる: 縁が広くぼやける"][m], size=14, weight=700, fill=PURPLE)
    # PCSS の手順
    st.Text(60, 482, "PCSS の 3 手順:", size=14, weight=700, fill=BLUE)
    st.Text(190, 482, "① 板までの距離を調べる(ブロッカー探索)→ ② 半影の幅を計算 → ③ その幅で PCF", size=13, weight=500, fill=TEXT)
    t_end = t0 + 3 * per
    st.Box(t_end - 0.4, 560, 496, 370, 36, [("読み込み: 探索 16 + PCF 25 = 41 回 / 画素", 13, "#1e3a8a")], BLUE, "#eff6ff") if False else None
    st.Caption(30, 534, [(0.0, t0, "面積のある光は、遮られ方が場所で変わるので、縁がぼける"), (t0, t_end, "受ける面を動かして、光を 64 個の点に分けて数える"), (t_end, 99, "半影の幅は、板から受ける面までの距離に比例する。これを PCF の広さに使うのが PCSS")], size=14, fill=MUTED, weight=500)
    for m in range(3):
        st.Note(t0 + m * per, "PCSS", "受ける面 %g: 半影の幅 %.2f(式 %.2f)" % (yrs[m], pens[m], theo[m]))
    return Build(st, name, "graphics/shadows/pcss.md", BEFORE, [1.5, 4.0, 8.0, 11.0, 16.0, 20.0])


# ===================================================================== Contact shadow
def ContactShadowMarch():
    name = "contact-shadow-march"
    st = Stage(name, "コンタクト シャドウ: 画面の深度を、光の方向へたどって、物の足元の細かい影を作る", duration=20.0, subtitle="断面。地面に、高さ 1.5 の小さな物。シャドウ マップ(荒い)で見逃す足元の影を、画面の深度で補う")
    sc, root = st.scene, st.root
    NX = 32
    CS, OX, OY = 26.0, 40.0, 300.0
    ZS = 36.0
    ca, sa = math.cos(math.radians(40)), math.sin(math.radians(40))   # 光の来る向き(左上)
    h = [0.0] * NX
    for i in range(13, 16):
        h[i] = 1.5
    for i in (22, 23):
        h[i] = 4.0
    # 光の方向(画素から光へ): (-ca, +sa)
    def March(i, steps=6, step=0.5):
        x, z = i + 0.5, h[i] + 0.02
        n = 0
        for k in range(1, steps + 1):
            n += 1
            xx, zz = x - ca * step * k, z + sa * step * k
            c = int(math.floor(xx))
            if 0 <= c < NX and h[c] > zz + 0.02:
                return True, n
        return False, n

    def True_shadow(i):
        x, z = i + 0.5, h[i]
        t = 0.0
        while t < 12:
            xx, zz = x - ca * t, z + sa * t
            c = int(math.floor(xx))
            if 0 <= c < NX and h[c] > zz + 0.002 and not (c == i):
                return True
            t += 0.01
        return False

    truth = [True_shadow(i) if h[i] == 0.0 else False for i in range(NX)]
    # 荒いシャドウ マップ(1 マス 2 画素分)で、バイアスつき → 足元を見逃す
    BIAS = 2.6
    def ShadowMap(i):
        # 2 画素 1 マス。マスの中の「いちばん手前(光に近い)の高さ」だけ覚える
        b = i // 2
        cols = [2 * b, 2 * b + 1]
        # 光に向かう方向のずれ: 地面のマスの代表高さ = 物がある列の最大
        hmax = max(h[c] for c in cols if 0 <= c < NX)
        # 物の影が地面に落ちるかを、荒いマスの高さで判定(バイアス BIAS 画素ぶん手前を無視)
        x = i + 0.5
        t = BIAS
        while t < 12:
            xx, zz = x - ca * t, sa * t
            c = int(math.floor(xx))
            if 0 <= c < NX:
                cb = c // 2
                hm = max(h[q] for q in (2 * cb, 2 * cb + 1) if 0 <= q < NX)
                if hm > zz + 0.02 and c != i:
                    return True
            t += 0.05
        return False

    sm = [ShadowMap(i) if h[i] == 0.0 else False for i in range(NX)]
    ct = [March(i)[0] if h[i] == 0.0 else False for i in range(NX)]
    comb = [a or b for a, b in zip(sm, ct)]
    err = lambda s: sum(1 for i in range(NX) if (s[i] != truth[i]))
    e_sm, e_ct, e_cb = err(sm), err(ct), err(comb)
    assert e_cb < e_sm and e_cb < e_ct and e_sm >= 1 and e_ct >= 1, (e_sm, e_ct, e_cb)
    st.Panel(30, 96, 900, 190, "① 断面(光は左上から)", color=AMBER)
    X = lambda x: OX + x * CS
    Zy = lambda z: OY - 60 - z * ZS * 1.0 + 60
    base_y = 244.0
    ZY = lambda z: base_y - z * ZS
    root.add("line", x1=40, y1=base_y, x2=40 + NX * CS, y2=base_y, stroke="#94a3b8", stroke_width=3)
    for i in range(NX):
        if h[i] > 0:
            root.add("rect", x=R(X(i)), y=R(ZY(h[i])), width=CS, height=R(h[i] * ZS), fill="#cbd5e1", stroke="#94a3b8", stroke_width=1.5)
    sc.Text(root, X(14.5), ZY(1.5) - 6, "小さな物", size=12, weight=700, fill=MUTED, anchor="middle")
    sc.Text(root, X(23.0), ZY(4.0) - 6, "高い物", size=12, weight=700, fill=MUTED, anchor="middle")
    for k in range(5):
        x0 = 1.0 + k * 3.0
        root.add("line", x1=R(X(x0)), y1=R(ZY(5.0)), x2=R(X(x0 + 5.0 * ca / sa)), y2=R(ZY(0)), stroke="#fbbf24", stroke_width=1.2, stroke_dasharray="4 5", opacity=0.8)
    # 3 つの帯
    rows = [("正解(光線を細かく調べる)", truth, GREEN, 318), ("荒いシャドウ マップ(+ バイアス)", sm, RED, 360), ("画面の深度をたどる(コンタクト)", ct, BLUE, 402), ("両方をあわせる", comb, PURPLE, 444)]
    t0, dts = 1.5, 0.12
    gap = NX * dts + 0.8
    for r, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, 40, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, OX, y, NX, 1, CS, base="#e5e7eb", stroke="#94a3b8")
        for i in range(NX):
            g.Paint(i, 0, t0 + r * gap + i * dts, "#cbd5e1" if h[i] > 0 else (DARKC if vals[i] else LIT))
        g.Flush()
        for i in range(NX):
            if h[i] == 0.0 and vals[i] != truth[i]:
                fr = g.Frame(i, 0, RED, 3)
                fr.Set(t0 + r * gap + i * dts, "opacity", 1)
    # 1 画素のたどり方(図)
    ex = 16
    t_e = t0 + 2 * gap
    gx = root.add("g", opacity=0)
    gx.Show(t_e, t_e + gap)
    x, z = ex + 0.5, h[ex] + 0.02
    pts = [(x, z)]
    for k in range(1, 7):
        xx, zz = x - ca * 0.5 * k, z + sa * 0.5 * k
        pts.append((xx, zz))
        c = int(math.floor(xx))
        col = RED if (0 <= c < NX and h[c] > zz + 0.02) else GREEN
        gx.add("circle", cx=R(X(xx)), cy=R(ZY(zz)), r=3.5, fill=col)
    gx.add("circle", cx=R(X(x)), cy=R(ZY(z)), r=6, fill=INK)
    sc.Text(gx, X(x), ZY(z) + 20, "調べる画素", size=11, weight=700, fill=INK, anchor="middle")
    ser = []
    cnt = 0
    for i in range(NX):
        if h[i] == 0.0:
            cnt += March(i)[1]
        ser.append((t0 + 2 * gap + i * dts, cnt))
    st.Text(560, 312, "深度の読み込み(コンタクト):", size=13, fill=BLUE)
    st.Counter(760, 316, ser, size=20, fill=BLUE)
    t_end = t0 + 4 * gap
    st.Box(t_end, 560, 340, 370, 120, [("正解とのくいちがい(画素数)", 13, MUTED), ("シャドウ マップだけ: %d 画素(足元を見逃す)" % e_sm, 14, "#991b1b"), ("コンタクトだけ: %d 画素(遠い影に届かない)" % e_ct, 14, "#1e3a8a"), ("両方: %d 画素 → 足元まで影が付く" % e_cb, 14, "#166534")], PURPLE, "#faf5ff")
    st.Caption(30, 534, [(0.0, t0, "荒いシャドウ マップは、物の足元の短い影を、バイアスで見逃す"), (t0, t_end, "画面の深度を、光の方向に 6 歩たどると、足元の短い影が見つかる(遠くの影は、届かない)"), (t_end, 99, "遠くの大きな影はシャドウ マップ、足元の細かい影はコンタクト、と役割を分ける")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "コンタクト", "くいちがい: シャドウ マップ %d / コンタクト %d / 両方 %d" % (e_sm, e_ct, e_cb))
    return Build(st, name, "graphics/shadows/contact-shadows.md", BEFORE, [1.5, 4.0, 8.0, 13.0, 18.0, 19.8])


# ===================================================================== SDF soft shadow
def SdfSoftShadow():
    name = "sdf-soft-shadow"
    st = Stage(name, "SDF の柔らかい影: 光に向かう途中で、物にどれだけ「かすったか」で、影の濃さを決める", duration=21.0, subtitle="円の物。床の各点から光へ、距離場を使って進む。min(k·距離 ÷ 進んだ長さ)が小さいほど、影が濃い")
    sc, root = st.scene, st.root
    CXo, CYo, RAD = 14.0, 3.2, 1.2
    LX, LY = 5.0, 9.0                 # 光(点)
    FLOOR = 0.0
    NC = 56
    X0, SX = 60.0, 30.0
    Y0, SY = 398.0, 30.0
    UX = lambda x: X0 + x * SX
    UY = lambda y: Y0 - y * SY

    def Sdf(x, y):
        return math.hypot(x - CXo, y - CYo) - RAD

    def Shadow(X, k):
        ro = (X, FLOOR + 0.02)
        rd = (LX - ro[0], LY - ro[1])
        L = math.hypot(*rd)
        rd = (rd[0] / L, rd[1] / L)
        t, res, n = 0.1, 1.0, 0
        while t < L and n < 64:
            d = Sdf(ro[0] + rd[0] * t, ro[1] + rd[1] * t)
            n += 1
            if d < 0.001:
                return 0.0, n
            res = min(res, k * d / t)
            t += max(d, 0.04)
        return max(0.0, min(1.0, res)), n

    ks = [4.0, 12.0, 64.0]
    data = []
    for k in ks:
        vals = [Shadow(28.0 * (i + 0.5) / NC, k) for i in range(NC)]
        data.append(vals)
    soft_w = []
    for m, vals in enumerate(data):
        soft_w.append(sum(1 for v, n in vals if 0.05 < v < 0.95) * 28.0 / NC)
    assert soft_w[0] > soft_w[1] > soft_w[2] and soft_w[2] >= 0
    avg_n = [sum(n for v, n in vals) / len(vals) for vals in data]
    st.Panel(30, 96, 900, 330, "① 光・円の物・床", color=AMBER)
    root.add("line", x1=R(UX(0)), y1=R(UY(0)), x2=R(UX(28)), y2=R(UY(0)), stroke="#94a3b8", stroke_width=3)
    root.add("circle", cx=R(UX(CXo)), cy=R(UY(CYo)), r=R(RAD * SX), fill="#cbd5e1", stroke="#94a3b8", stroke_width=2)
    root.add("circle", cx=R(UX(LX)), cy=R(UY(LY)), r=11, fill=AMBER)
    sc.Text(root, UX(LX) + 16, UY(LY) + 4, "光(点)", size=13, weight=700, fill="#92400e")
    # 例の光線(床の 1 点)から)
    ex = 18.5
    t0, per = 1.0, 6.4
    for m, k in enumerate(ks):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        # たどる様子(円で距離を示す)
        ro = (ex, 0.02)
        rd = (LX - ro[0], LY - ro[1])
        L = math.hypot(*rd)
        rd = (rd[0] / L, rd[1] / L)
        t, n = 0.1, 0
        while t < L and n < 12:
            px, py = ro[0] + rd[0] * t, ro[1] + rd[1] * t
            d = Sdf(px, py)
            g.add("circle", cx=R(UX(px)), cy=R(UY(py)), r=R(max(d, 0.02) * SX), fill="none", stroke="#60a5fa", stroke_width=1.2, opacity=0.8)
            g.add("circle", cx=R(UX(px)), cy=R(UY(py)), r=3, fill=BLUE)
            n += 1
            t += max(d, 0.04)
        g.add("circle", cx=R(UX(ex)), cy=R(UY(0.02)), r=6, fill=INK)
        sc.Text(g, 40, 112 + 0, "k = %g" % k, size=20, weight=700, fill=PURPLE)
        # 結果の帯
        grid = Grid(st, X0, 440, NC, 1, 28.0 * SX / 28.0 * 28.0 / NC, base="#e5e7eb", parent=g, stroke="#94a3b8")
        for i, (v, nn) in enumerate(data[m]):
            grid.Paint(i, 0, t0 + m * per + 0.6 + 0.06 * i, Mix(DARKC, LIT, v))
        grid.Flush()
        sc.Text(g, 60, 436, "床の明るさ(黄 = 光が届く、暗い = 影)", size=12, weight=500, fill=MUTED)
        sc.Text(g, 60, 480, "k = %g: 影の縁のぼけ幅 %.1f、1 点あたりの歩数 平均 %.1f" % (k, soft_w[m], avg_n[m]), size=15, weight=700, fill=RED)
        sc.Text(g, 60, 504, ["k が小さい: 広くぼける(柔らかい影)", "k が中くらい: ほどよい", "k が大きい: くっきり(ほぼ硬い影)"][m], size=13, weight=500, fill=MUTED)
    ser = [(t0 + m * per + 0.4, int(round(avg_n[m]))) for m in range(3)]
    st.Text(560, 112, "1 点あたりの歩数(平均):", size=14)
    st.Counter(740, 116, ser, size=24, fill=BLUE)
    t_end = t0 + 3 * per
    st.Caption(30, 534, [(0.0, t0, "距離場(SDF)= 各点から、物までの一番近い距離"), (t0, t_end, "光に向かって進みながら、k × 距離 ÷ 進んだ長さ の最小値を記録する"), (t_end, 99, "かすった度合いが、そのまま、影の濃さになる。k で、ぼけ具合を調整する")], size=14, fill=MUTED, weight=500)
    for m in range(3):
        st.Note(t0 + m * per, "SDF", "k = %g: ぼけ幅 %.1f、平均 %.1f 歩" % (ks[m], soft_w[m], avg_n[m]))
    return Build(st, name, "graphics/shadows/sdf-shadows.md", BEFORE, [1.5, 4.0, 8.0, 11.0, 16.0, 20.0])


NAMES = ["pcss-penumbra", "contact-shadow-march", "sdf-soft-shadow"]
FIGS = [PcssPenumbra, ContactShadowMarch, SdfSoftShadow]
