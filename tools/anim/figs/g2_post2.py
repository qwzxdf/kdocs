import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_gi import Lcg  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"
DARK, BRIGHT = "#0f172a", "#fff4b8"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


def Disp(v):
    return Mix(DARK, BRIGHT, min(1.0, (v / (1.0 + v)) * 1.6))


def Gauss(row, sig):
    n = len(row)
    rad = int(math.ceil(3 * sig))
    ws = [math.exp(-d * d / (2 * sig * sig)) for d in range(-rad, rad + 1)]
    t = sum(ws)
    return [sum(ws[k] * row[min(n - 1, max(0, i + d))] for k, d in enumerate(range(-rad, rad + 1))) / t for i in range(n)]


def Scene1d(n=48):
    row = [0.12] * n
    for i in range(6, 9):
        row[i] = 5.0
    row[20] = 14.0
    for i in range(30, 36):
        row[i] = 1.6
    return row


def Bar(st, root, sc, row, y, cw, x0, base, col, t, h=50.0, ymax=None, label=None, lc=None):
    pass


# ===================================================================== bloom threshold
def BloomThreshold():
    name = "bloom-threshold"
    st = Stage(name, "ブルームのしきい値: どこから光らせるか。硬く切ると縁が目立ち、ソフト ニーでなめらかにつなぐ", duration=21.0, subtitle="1 列 48 画素の HDR。明るさ 0.12(暗い面)・1.6(明るい面)・5 と 14(光源)。しきい値を 0.5 → 1.0 → 2.0 に上げる")
    sc, root = st.scene, st.root
    row = Scene1d()
    n = len(row)
    def Hard(v, th):
        return max(0.0, v - th)
    def Soft(v, th, k=0.5):
        kn = th * k
        s = min(max(v - th + kn, 0.0), 2 * kn)
        s = s * s / (4 * kn + 1e-5)
        return max(s, v - th)
    ths = [0.5, 1.0, 2.0]
    E = lambda a: sum(a)
    outs = [[Hard(v, t) for v in row] for t in ths]
    souts = [[Soft(v, t) for v in row] for t in ths]
    blur = [Gauss(o, 3.0) for o in outs]
    assert E(outs[0]) > E(outs[1]) > E(outs[2])
    CW, X0 = 17.0, 60.0
    st.Text(X0, 100, "入力(HDR)", size=13, weight=700, fill=AMBER)
    g0 = Grid(st, X0, 106, n, 1, CW, base=DARK, stroke="#94a3b8")
    for i, v in enumerate(row):
        g0.Paint(i, 0, 0.3, Disp(v))
    g0.Flush()
    t0, per = 1.5, 5.8
    for m, th in enumerate(ths):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        sc.Text(g, X0, 156, "しきい値 %.1f" % th, size=20, weight=700, fill=PURPLE)
        for r_, (lab, vals, col, y) in enumerate([("② 硬く切る: max(0, 明るさ − しきい値)", outs[m], RED, 190), ("③ ソフト ニー(切り口をなめらかに)", souts[m], BLUE, 244), ("④ ② をぼかした、にじむ光", blur[m], GREEN, 298)]):
            sc.Text(g, X0, y - 4, lab, size=12, weight=700, fill=col)
            gr = Grid(st, X0, y, n, 1, CW, base=DARK, parent=g, stroke="#94a3b8")
            for i, v in enumerate(vals):
                gr.Paint(i, 0, t0 + m * per + 0.4 + i * 0.03, Disp(v))
            gr.Flush()
        sc.Text(g, X0, 360, "取り出した光の量(合計): 硬い %.1f / ソフト %.1f / ぼかした後 %.1f" % (E(outs[m]), E(souts[m]), E(blur[m])), size=14, weight=700, fill=TEXT)
        d = {0.5: "暗い面(0.12)は光らない。1.6 の面は、光る側に入る → 画面全体がにじむ", 1.0: "1.6 の面が少し光る。光源だけが、強く光る", 2.0: "光源(5 と 14)だけが光る"}[th]
        sc.Text(g, X0, 384, d, size=13, weight=500, fill=MUTED)
    ser = [(t0 + m * per + 0.4, int(round(E(outs[m])))) for m in range(3)]
    st.Text(X0, 430, "取り出した光の量:", size=15)
    st.Counter(240, 434, ser, size=26, fill=RED)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.5, 480, 410, 450, 70, [("しきい値を上げると、光る範囲と量が減る(%.0f → %.0f → %.0f)" % (E(outs[0]), E(outs[1]), E(outs[2])), 14, "#1e3a8a"), ("硬く切ると、しきい値付近で、明るさが急に変わって、ちらつく", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "明るい所だけを取り出して、ぼかし、足す"), (t0, t_e, "しきい値が低いほど、たくさんの光がにじむ"), (t_e, 99, "ソフト ニーを使うと、しきい値の前後で、なめらかにつながる")], size=14, fill=MUTED, weight=500)
    for m, th in enumerate(ths):
        st.Note(t0 + m * per, "しきい値", "%.1f: 取り出した光 %.1f" % (th, E(outs[m])))
    return Build(st, name, "graphics/postprocess/bloom/threshold.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== bloom intensity
def BloomIntensity():
    name = "bloom-intensity"
    st = Stage(name, "ブルームの強さ: 足す量を増やすと、光がにじむが、暗い所が白っぽく浮く(コントラスト低下)", duration=20.0, subtitle="1 列の画像。ブルームの強さ k を 0 → 0.3 → 1.0 → 2.0 にして、トーンマップ後の見え方を比べる")
    sc, root = st.scene, st.root
    row = Scene1d()
    n = len(row)
    bl = Gauss([max(0.0, v - 1.0) for v in row], 3.0)
    bl = [a + b for a, b in zip(bl, Gauss([max(0.0, v - 1.0) for v in row], 8.0))]
    ks = [0.0, 0.3, 1.0, 2.0]
    rein = lambda x: x / (1 + x)
    out = [[rein(row[i] + k * bl[i]) for i in range(n)] for k in ks]
    # 暗い所(右端 10 画素)の明るさ = 黒浮き
    lift = [sum(out[m][i] for i in range(38, 48)) / 10 for m in range(4)]
    base_dark = lift[0]
    glow = [sum(out[m][i] for i in range(10, 18)) / 8 for m in range(4)]   # 光源の近くのにじみ
    assert lift[3] > lift[0] and glow[3] > glow[0]
    CW, X0 = 15.0, 60.0
    t0, per = 1.5, 4.0
    for m, k in enumerate(ks):
        y = 110 + m * 70
        sc.Text(root, X0, y - 4, "ブルームの強さ k = %g" % k, size=14, weight=700, fill=[GRAY, GREEN, AMBER, RED][m])
        g = Grid(st, X0, y, n, 1, CW, base=DARK, stroke="#94a3b8")
        for i in range(n):
            g.Paint(i, 0, t0 + m * per + i * 0.04, Hex([255 * Gam(out[m][i]) for _ in range(1)] * 3) if False else Mix(DARK, BRIGHT, out[m][i] ** 0.6))
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + n * 0.04)
        sc.Text(gx, X0 + n * CW + 8, y + 14, "光源の近く %.2f" % glow[m], size=12, weight=700, fill=TEXT)
        sc.Text(gx, X0 + n * CW + 8, y + 32, "暗い所 %.3f" % lift[m], size=12, weight=700, fill=(RED if lift[m] > base_dark * 1.3 else MUTED))
    st.Panel(30, 400, 900, 80, "暗い所の持ち上がり(k = 0 を基準)", color=PURPLE)
    for m, k in enumerate(ks):
        x = 50 + m * 220
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + n * 0.04)
        sc.Text(g, x, 444, "k = %g" % k, size=13, weight=700, fill=INK)
        sc.Text(g, x, 468, "×%.2f" % (lift[m] / base_dark), size=18, weight=700, fill=(RED if lift[m] / base_dark > 1.3 else GREEN))
    t_e = t0 + 4 * per + 1.0
    st.Caption(30, 534, [(0.0, t0, "ブルームは、元の画像に足す"), (t0, t_e, "k を上げるほど、光源の周りが光るが、暗い所まで持ち上がる"), (t_e, 99, "強すぎると、画面が白っぽくぼやける。控えめ(k ≈ 0.05〜0.3)が基本")], size=14, fill=MUTED, weight=500)
    for m, k in enumerate(ks):
        st.Note(t0 + m * per, "強さ", "k = %g: 暗い所 ×%.2f、光源の近く %.2f" % (k, lift[m] / base_dark, glow[m]))
    return Build(st, name, "graphics/postprocess/bloom/composite.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


def Gam(v):
    return max(0.0, min(1.0, v)) ** (1 / 2.2)


# ===================================================================== bloom mip chain
def BloomMipChain():
    name = "bloom-mip-chain"
    st = Stage(name, "縮小ぼかし: 1 段下げるごとに、同じ 5 画素のぼかしが、2 倍の範囲をぼかす", duration=20.0, subtitle="1 列 48 画素の光源(1 つ)。縮小 → 小さい画像でぼかす → 拡大して足す。ぼけの広さと、読み込み回数を数える")
    sc, root = st.scene, st.root
    n = 48
    row = [0.0] * n
    row[24] = 16.0
    levels = [row]
    for L in range(1, 5):
        prev = levels[-1]
        m = len(prev) // 2
        levels.append([(prev[2 * i] + prev[2 * i + 1]) / 2 for i in range(m)])
    k5 = [1, 4, 6, 4, 1]
    k5 = [v / 16 for v in k5]

    def Blur5(a):
        m = len(a)
        return [sum(k5[j] * a[min(m - 1, max(0, i + j - 2))] for j in range(5)) for i in range(m)]

    blurred = [Blur5(l) for l in levels]
    def Up(a, size):
        m = len(a)
        out = []
        for i in range(size):
            f = (i + 0.5) * m / size - 0.5
            i0 = int(math.floor(f))
            t = f - i0
            g = lambda q: a[min(m - 1, max(0, q))]
            out.append(g(i0) * (1 - t) + g(i0 + 1) * t)
        return out
    ups = [Up(blurred[L], n) for L in range(5)]
    sizes = [len(l) for l in levels]
    spread = []
    for L in range(5):
        u = ups[L]
        tot = sum(u)
        sd = math.sqrt(sum(((i - 23.5) ** 2) * v for i, v in enumerate(u)) / tot)
        spread.append(sd)
    assert spread[4] > spread[2] > spread[0]
    taps = [5 * s for s in sizes]
    cum = []
    c = 0
    for L in range(5):
        c += taps[L]
        cum.append(c)
    direct = n * (2 * int(round(spread[4] * 2)) + 1)
    CW, X0 = 14.0, 60.0
    t0, per = 1.5, 3.4
    for L in range(5):
        y = 110 + L * 64
        w = CW * n / sizes[L]
        g = root.add("g", opacity=0)
        g.Show(t0 + L * per)
        sc.Text(g, X0, y - 4, "段 %d: %d 画素 → ぼかす → 元の大きさに拡大" % (L, sizes[L]), size=12, weight=700, fill=[GRAY, BLUE, GREEN, AMBER, RED][L])
        gr = Grid(st, X0, y, n, 1, CW, base=DARK, parent=g, stroke="#94a3b8")
        for i in range(n):
            gr.Paint(i, 0, t0 + L * per + 0.4 + i * 0.03, Disp(ups[L][i] * 2.5))
        gr.Flush()
        sc.Text(g, X0 + n * CW + 8, y + 14, "ぼけの広さ ±%.1f 画素" % spread[L], size=12, weight=700, fill=TEXT)
        sc.Text(g, X0 + n * CW + 8, y + 32, "読み込み %d 回" % taps[L], size=12, weight=500, fill=MUTED)
    st.Text(40, 450, "読み込みの合計:", size=15)
    st.Counter(180, 454, [(t0 + L * per + 0.4, cum[L]) for L in range(5)], size=26, fill=PURPLE)
    t_e = t0 + 5 * per
    st.Box(t_e - 0.4, 400, 470, 530, 52, [("5 段で、広さ ±%.1f 画素のぼけ。読み込みは合計 %d 回" % (spread[4], cum[4]), 14, "#166534"), ("直接ぼかすと、同じ広さに %s 回(約 %.0f 倍)" % (Fmt(direct), direct / cum[4]), 13, "#991b1b")], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "光源を 1 点、置く"), (t0, t_e, "画像を半分にするたびに、同じ 5 画素のぼかしが、倍の広さに効く"), (t_e, 99, "小さい画像ほど安い。全部足すと、裾の広い光になる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "縮小", "段 0〜4: ぼけの広さ %s" % " / ".join("%.1f" % s for s in spread))
    return Build(st, name, "graphics/postprocess/bloom/downsample.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 15.0, 19.0])


# ===================================================================== dual filter
def DualFilter():
    name = "dual-filter-passes"
    st = Stage(name, "デュアル フィルター: 縮小は「中心 + 四隅」、拡大は「8 方向」のタップ。少ない読み込みで、ガウスに近いぼかし", duration=20.0, subtitle="1 列 48 画素の光源。縮小(1/2)× 3 段、拡大 × 3 段を、実際に計算して、ガウスと比べる")
    sc, root = st.scene, st.root
    n = 48
    row = [0.0] * n
    row[24] = 16.0
    row[25] = 16.0
    def Down(a):
        m = len(a) // 2
        out = []
        for i in range(m):
            c = a[min(len(a) - 1, 2 * i)]
            s = a[min(len(a) - 1, 2 * i + 1)]
            l = a[max(0, 2 * i - 1)]
            r = a[min(len(a) - 1, 2 * i + 2)]
            out.append((4 * (c + s) / 2 + l + r) / 6)
        return out
    def Up(a, size):
        out = []
        m = len(a)
        for i in range(size):
            f = (i + 0.5) * m / size - 0.5
            i0 = int(math.floor(f)); t = f - i0
            g = lambda q: a[min(m - 1, max(0, q))]
            out.append(g(i0) * (1 - t) + g(i0 + 1) * t)
        return out
    L1 = Down(row); L2 = Down(L1); L3 = Down(L2)
    U2 = [(a + b) / 2 for a, b in zip(Up(L3, len(L2)), L2)]
    U1 = [(a + b) / 2 for a, b in zip(Up(U2, len(L1)), L1)]
    U0 = Up(U1, n)
    def Norm(a):
        t = sum(a)
        return [v / t for v in a]
    dual = Norm(U0)
    sd_d = math.sqrt(sum(((i - 24.5) ** 2) * v for i, v in enumerate(dual)))
    gaus = Norm(Gauss(row, sd_d))
    err = sum(abs(a - b) for a, b in zip(dual, gaus))
    peak_ratio = max(dual) / max(gaus)
    assert err < 0.6
    stages = [("縮小 1(48 → 24)", L1, GRAY), ("縮小 2(24 → 12)", L2, BLUE), ("縮小 3(12 → 6)", L3, GREEN), ("拡大して足す(6 → 12 → 24 → 48)", U0, RED)]
    t0, per = 1.5, 3.4
    for m, (lab, a, col) in enumerate(stages):
        y = 110 + m * 64
        sz = len(a)
        cw = 15.0 * n / sz
        sc.Text(root, 60, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, 60, y, sz, 1, cw, base=DARK, stroke="#94a3b8", cell_h=17.0)
        for i in range(sz):
            g.Paint(i, 0, t0 + m * per + i * 0.03 * 48 / sz, Disp(a[i] * 2.0))
        g.Flush()
    taps_dual = 5 * len(L1) + 5 * len(L2) + 5 * len(L3) + 8 * len(L2) + 8 * len(L1) + 8 * n
    taps_gauss = n * (2 * int(math.ceil(3 * sd_d)) + 1)
    t_c = t0 + 4 * per
    st.Panel(30, 380, 900, 90, "ガウス ぼかし(同じ広さ σ = %.1f 画素)との比較" % sd_d, color=PURPLE)
    grg = Grid(st, 60, 400, n, 1, 15.0, base=DARK, stroke="#94a3b8")
    for i in range(n):
        grg.Paint(i, 0, t_c + i * 0.03, Disp(gaus[i] * 40.0))
    grg.Flush()
    grd = Grid(st, 60, 430, n, 1, 15.0, base=DARK, stroke="#94a3b8")
    for i in range(n):
        grd.Paint(i, 0, t_c + i * 0.03, Disp(dual[i] * 40.0))
    grd.Flush()
    sc.Text(root, 60 + n * 15 + 8, 414, "ガウス", size=12, weight=700, fill=BLUE)
    sc.Text(root, 60 + n * 15 + 8, 444, "デュアル", size=12, weight=700, fill=RED)
    t_e = t_c + n * 0.03 + 0.6
    st.Box(t_e, 520, 484, 410, 44, [("読み込み: デュアル %d 回 / ガウス %d 回(%.0f 分の 1)" % (taps_dual, taps_gauss, taps_gauss / taps_dual), 13, "#166534")], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "光源を置く"), (t0, t_c, "縮小で広い範囲を集め、拡大で、段ごとに足し戻す"), (t_c, t_e, "同じ広さのガウスと並べる"), (t_e, 99, "形は近く、読み込みがずっと少ない(ピーク比 %.2f)" % peak_ratio)], size=14, fill=MUTED, weight=500)
    st.Note(t0, "デュアル", "広さ σ = %.1f、ガウスとの差 %.2f、読み込み %d vs %d" % (sd_d, err, taps_dual, taps_gauss))
    return Build(st, name, "graphics/postprocess/bloom/dual-filter.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 19.0])


# ===================================================================== gaussian separable
def GaussianSeparable():
    name = "gaussian-separable"
    st = Stage(name, "分離可能なガウス: 2 次元のぼかしを、横 1 回 + 縦 1 回に分けると、同じ結果で、読み込みが半径に比例するだけになる", duration=21.0, subtitle="12×12 画素に光源を 1 つ。半径 4(9×9 = 81 タップ)の 2 次元ガウスと、横 9 + 縦 9 の 2 回を、比べる")
    sc, root = st.scene, st.root
    N, CS = 12, 17.0
    img = [[0.0] * N for _ in range(N)]
    img[5][6] = 10.0
    img[8][3] = 5.0
    sig, rad = 1.6, 4
    k = [math.exp(-d * d / (2 * sig * sig)) for d in range(-rad, rad + 1)]
    ks = sum(k)
    k = [v / ks for v in k]
    g = lambda a, i, j: a[min(N - 1, max(0, j))][min(N - 1, max(0, i))]
    full = [[sum(k[dx + rad] * k[dy + rad] * g(img, i + dx, j + dy) for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1)) for i in range(N)] for j in range(N)]
    horiz = [[sum(k[dx + rad] * g(img, i + dx, j) for dx in range(-rad, rad + 1)) for i in range(N)] for j in range(N)]
    sep = [[sum(k[dy + rad] * g(horiz, i, j + dy) for dy in range(-rad, rad + 1)) for i in range(N)] for j in range(N)]
    diff = max(abs(full[j][i] - sep[j][i]) for j in range(N) for i in range(N))
    assert diff < 1e-9
    px = [30, 335, 640]
    titles = [("① 入力", AMBER), ("② 横にぼかす(9 タップ)", BLUE), ("③ さらに縦にぼかす(9 タップ)", GREEN)]
    data = [img, horiz, sep]
    t0, per = 1.5, 4.5
    for p, (lab, col) in enumerate(titles):
        st.Panel(px[p], 100, N * CS + 4, N * CS + 4, lab, color=col)
        gr = Grid(st, px[p] + 2, 102, N, N, CS, base=DARK)
        for j in range(N):
            for i in range(N):
                gr.Paint(i, j, 0.3 if p == 0 else t0 + (p - 1) * per + 0.04 * (i + j), Disp(data[p][j][i]))
        gr.Flush()
    px_n = N * N
    st.Panel(30, 340, 900, 130, "読み込みの数", color=PURPLE)
    lines = [("2 次元のまま(9×9)", px_n * 81, RED, 380), ("分離(9 + 9)", px_n * 18, GREEN, 410)]
    t_c = t0 + 2 * per + 0.5
    for r_, (lab, v, col, y) in enumerate(lines):
        sc.Text(root, 50, y + 14, lab, size=14, weight=700, fill=col, opacity=0).Show(t_c)
        w = v / (px_n * 81) * 300
        b = root.add("rect", x=300, y=y, width=1, height=22, fill=col, opacity=0.85)
        b.Set(t_c, "width", 1)
        b.Ramp(t_c, t_c + 1.2, "width", R(w))
        sc.Text(root, 300 + w + 10, y + 17, "%s 回(1 画素あたり %d)" % (Fmt(v), v // px_n), size=13, weight=700, fill=col, opacity=0).Show(t_c + 1.2)
    st.Text(50, 458, "結果の最大の差: %.0e(同じ結果)" % max(diff, 1e-16), size=13, weight=700, fill=BLUE)
    big = (2 * 32 + 1)
    t_e = t_c + 2.4
    st.Box(t_e, 560, 100, 370, 0.0001, [], BLUE, "#eff6ff") if False else None
    st.Box(t_e, 660, 346, 270, 130, [("半径 32 のぼかしなら", 14, "#1e3a8a"), ("2 次元: %d タップ" % (big * big), 13, "#991b1b"), ("分離: %d タップ(%.0f 倍少ない)" % (2 * big, big * big / (2 * big)), 13, "#166534"), ("半径に比例なので、大きなぼかしも安い", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "ガウス関数は、横と縦に、分けて掛け算できる"), (t0, t0 + 2 * per, "横にぼかして、その結果を縦にぼかす"), (t_c, 99, "結果は 2 次元のぼかしと、完全に同じ。読み込みは、9 × 9 = 81 から 18 に")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "分離", "最大の差 %.0e。読み込み %s vs %s" % (diff, Fmt(px_n * 81), Fmt(px_n * 18)))
    return Build(st, name, "graphics/postprocess/bloom/gaussian.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 16.0, 20.0])


# ===================================================================== karis
def KarisFireflies():
    name = "karis-fireflies"
    st = Stage(name, "ホタル(ちらつく光の点): 1 画素だけ極端に明るいと、縮小で何倍にも広がる。Karis 平均で、明るさに応じて重みを下げる", duration=20.0, subtitle="1 列 32 画素に、極端に明るい 1 画素(1000)がある。縮小を 3 段くり返して、ふつうの平均と Karis 平均の差を見る")
    sc, root = st.scene, st.root
    n = 32
    row = [0.8] * n
    row[13] = 1000.0
    def Down(a, karis):
        m = len(a) // 2
        out = []
        for i in range(m):
            vs = [a[2 * i], a[2 * i + 1]]
            if karis:
                ws = [1 / (1 + 0.2126 * v) for v in vs]
                out.append(sum(v * w for v, w in zip(vs, ws)) / sum(ws))
            else:
                out.append(sum(vs) / 2)
        return out
    chains = {}
    for kar in (False, True):
        lv = [row]
        for L in range(3):
            lv.append(Down(lv[-1], kar))
        chains[kar] = lv
    peak = {k: [max(l) for l in v] for k, v in chains.items()}
    energy = {k: [sum(l) / len(l) for l in v] for k, v in chains.items()}
    assert peak[False][3] > 10 * peak[True][3]
    t0, per = 1.5, 3.4
    for r_, (kar, lab, col, y0) in enumerate([(False, "ふつうの平均", RED, 106), (True, "Karis 平均(明るい画素の重みを下げる)", GREEN, 270)]):
        sc.Text(root, 40, y0 - 4, lab, size=15, weight=700, fill=col)
        for L in range(4):
            a = chains[kar][L]
            sz = len(a)
            cw = 26.0 * n / sz
            y = y0 + 4 + L * 34
            gg = Grid(st, 190, y, sz, 1, 18.0 * n / sz, base=DARK, stroke="#94a3b8", cell_h=22.0)
            for i in range(sz):
                gg.Paint(i, 0, t0 + L * per * 0.5 + r_ * 0.0 + i * 0.03 * 32 / sz, Mix(DARK, BRIGHT, min(1.0, math.log10(1 + a[i]) / 3.0)))
            gg.Flush()
            sc.Text(root, 180, y + 14, "段 %d(%d 画素)" % (L, sz), size=11, weight=700, fill=MUTED, anchor="end")
            sc.Text(root, 790, y + 14, "最大 %.1f" % peak[kar][L], size=12, weight=700, fill=col)
    t_e = t0 + 4 * per * 0.5 + 1.5
    st.Box(t_e, 40, 430, 880, 76, [("段 3 の最大: ふつう %.1f / Karis %.1f(%.0f 倍の差)" % (peak[False][3], peak[True][3], peak[False][3] / peak[True][3]), 15, "#1e3a8a"), ("ふつうの平均は、1 画素の光が、縮小のたびに半分に広がるだけで、ほぼ消えない → ぼかした後に、大きな光の塊が出て、ちらつく", 12, TEXT), ("Karis 平均は、重み 1 ÷ (1 + 輝度)で、極端に明るい画素の影響を小さくする", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ゲームでは、小さくて、とても明るい反射(ハイライト)がある"), (t0, t_e, "縮小の平均で、1 画素の強い光が、広い範囲に混ざる"), (t_e, 99, "重みを付けると、その影響が小さくなり、ちらつきが抑えられる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "Karis", "段 3 の最大: ふつう %.1f / Karis %.1f" % (peak[False][3], peak[True][3]))
    return Build(st, name, "graphics/postprocess/bloom/karis-average.md", BEFORE, [2.0, 4.0, 6.0, 8.0, 12.0, 19.0])


# ===================================================================== TAA history clamp
def TaaHistoryClamp():
    name = "taa-history-clamp"
    st = Stage(name, "TAA の履歴クランプ: 前の画像の色を、いまの周りの色の範囲に押し込めて、ゴーストを消す", duration=21.0, subtitle="1 列 40 画素。明るい物(幅 6)が右へ 3 画素動いた。前のフレームの履歴をそのまま混ぜる場合と、周りの最小〜最大に押し込める場合")
    sc, root = st.scene, st.root
    n = 40
    cur = [0.1] * n
    prev = [0.1] * n
    for i in range(12, 18):
        prev[i] = 1.0
    for i in range(15, 21):
        cur[i] = 1.0
    alpha = 0.1
    plain = [alpha * cur[i] + (1 - alpha) * prev[i] for i in range(n)]
    lo = [min(cur[max(0, i - 1):min(n, i + 2)]) for i in range(n)]
    hi = [max(cur[max(0, i - 1):min(n, i + 2)]) for i in range(n)]
    clamp = [alpha * cur[i] + (1 - alpha) * min(hi[i], max(lo[i], prev[i])) for i in range(n)]
    ghost = lambda a: sum(abs(a[i] - cur[i]) for i in range(10, 15))
    g_p, g_c = ghost(plain), ghost(clamp)
    assert g_c < g_p / 2, (g_p, g_c)
    CW, X0 = 20.0, 60.0
    rows = [("前のフレーム(履歴)", prev, GRAY, 108), ("いまのフレーム(物が右へ動いた)", cur, BLUE, 164), ("履歴をそのまま混ぜる(α = 0.1)", plain, RED, 220), ("履歴を、周りの最小〜最大に押し込めてから混ぜる", clamp, GREEN, 276)]
    t0, per = 1.5, 3.4
    for r_, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(n):
            g.Paint(i, 0, 0.3 if r_ < 2 else t0 + (r_ - 2) * per + i * 0.05, Gray(1 - vals[i] * 0.9))
        g.Flush()
    # クランプの例
    ex = 13
    gx = root.add("g", opacity=0)
    gx.Show(t0 + 2 * per + 0.5)
    sc.Text(gx, X0, 340, "画素 %d の例: 履歴 %.1f、周りの範囲 %.1f〜%.1f" % (ex + 1, prev[ex], lo[ex], hi[ex]), size=14, weight=700, fill=TEXT)
    sc.Text(gx, X0, 364, "履歴 %.1f → 範囲に押し込めて %.1f → 結果 %.2f(押し込めないと %.2f)" % (prev[ex], min(hi[ex], max(lo[ex], prev[ex])), clamp[ex], plain[ex]), size=14, weight=700, fill=GREEN)
    fr = g.Frame(ex, 0, RED, 3)
    st.Text(60, 410, "ゴースト(物の後ろに残る、画素 11〜15 の差の合計):", size=14)
    sc.Text(root, 440, 412, "そのまま %.2f / クランプ %.2f(%.0f 分の 1)" % (g_p, g_c, g_p / g_c), size=18, weight=700, fill=PURPLE, opacity=0).Show(t0 + 2 * per + 3.0)
    t_e = t0 + 2 * per + 3.5
    st.Box(t_e, 60, 440, 860, 60, [("履歴が、いまの周りの色の範囲を外れていたら、その範囲の端に寄せる", 14, "#1e3a8a"), ("動いた後に残る、古い色(ゴースト)が、混ざらなくなる。代わりに、細かい線がちらつくことがある", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "動く物があると、前のフレームの色が、古くなる"), (t0, t_e, "古い色を、そのまま混ぜると、残像になる"), (t_e, 99, "周りの色の範囲に押し込めば、古い色が、自然に消える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "クランプ", "ゴースト: そのまま %.2f / クランプ %.2f" % (g_p, g_c))
    return Build(st, name, "graphics/postprocess/antialiasing/taa.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== TAA ghosting
def TaaGhosting():
    name = "taa-ghosting"
    st = Stage(name, "TAA のゴースト: 混ぜる割合 α が小さいほど、滑らかだが、残像が長く残る", duration=21.0, subtitle="明るい物が消えた画素。履歴の色が、新しい色へ、何フレームで置き換わるか。α を 0.5 → 0.2 → 0.1 → 0.05 で比べる")
    sc, root = st.scene, st.root
    alphas = [0.5, 0.2, 0.1, 0.05]
    F = 40
    res = []
    for a in alphas:
        v, ser = 1.0, []
        for f in range(F + 1):
            ser.append(v)
            v = a * 0.0 + (1 - a) * v
        res.append(ser)
    half = [next(f for f, v in enumerate(s) if v < 0.5) for s in res]
    gone = [next((f for f, v in enumerate(s) if v < 0.05), F) for s in res]
    assert half[0] < half[1] < half[2] < half[3]
    X0, W = 70.0, 820.0
    st.Panel(30, 96, 900, 230, "① 画素に残っている、消えた物の色(1 = 完全に残っている)", color=BLUE)
    XX = lambda f: X0 + f / F * W
    YY = lambda v: 300 - v * 170
    cols = [RED, AMBER, GREEN, BLUE]
    for m, a in enumerate(alphas):
        p = root.add("path", d=Poly([(XX(f), YY(v)) for f, v in enumerate(res[m])]), fill="none", stroke=cols[m], stroke_width=3.5, opacity=0)
        p.Show(1.5 + m * 3.6)
        sc.Text(root, XX(F) - 4, YY(res[m][F]) - 6, "α = %g" % a, size=12, weight=700, fill=cols[m], anchor="end", opacity=0).Show(1.5 + m * 3.6)
    root.add("line", x1=X0, y1=R(YY(0.05)), x2=X0 + W, y2=R(YY(0.05)), stroke=GRAY, stroke_width=1.5, stroke_dasharray="4 4")
    sc.Text(root, X0 + 6, R(YY(0.05)) - 4, "見えなくなる(5%)", size=11, weight=700, fill=GRAY)
    st.Panel(30, 346, 900, 130, "② 何フレームで、見えなくなるか(60 fps なら、× 0.0167 秒)", color=PURPLE)
    for m, a in enumerate(alphas):
        y = 380 + m * 22
        g = root.add("g", opacity=0)
        g.Show(1.5 + m * 3.6 + 1.0)
        sc.Text(g, 50, y + 14, "α = %g" % a, size=13, weight=700, fill=cols[m])
        w = gone[m] / F * 560
        g.add("rect", x=140, y=y, width=R(max(w, 3)), height=16, fill=cols[m], opacity=0.85)
        sc.Text(g, 140 + w + 8, y + 13, "%d フレーム(%.2f 秒)/ 半分まで %d フレーム" % (gone[m], gone[m] / 60, half[m]), size=12, weight=700, fill=TEXT)
    t_e = 1.5 + 4 * 3.6
    st.Box(t_e, 620, 490, 310, 36, [("小さい α は滑らか、でも、残像が長い", 13, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "物が消えたあとも、履歴の色が、少しずつ薄れながら、残る"), (1.5, t_e, "α が小さいほど、薄れるのが遅い"), (t_e, 99, "ゴーストを抑えるには、α を速度に応じて上げる、履歴を押し込める、などを併用する")], size=14, fill=MUTED, weight=500)
    for m, a in enumerate(alphas):
        st.Note(1.5 + m * 3.6, "ゴースト", "α = %g: 見えなくなるまで %d フレーム" % (a, gone[m]))
    return Build(st, name, "graphics/postprocess/antialiasing/taa-challenges.md", BEFORE, [2.0, 5.0, 8.5, 12.0, 16.0, 20.0])


# ===================================================================== SMAA
def SmaaEdgeWeights():
    name = "smaa-edge-weights"
    st = Stage(name, "SMAA: 縁を見つけ、階段の長さを調べて、画素ごとに、混ぜる割合を決める", duration=21.0, subtitle="緩い傾き(1/6)の縁。階段の 1 段が 6 画素。画素ごとに、縁の上下の色を、面積の割合で混ぜる")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 8, 22.0
    BG, FG = 0.95, 0.15
    slope = 1.0 / 6
    edge_y = lambda x: 3.0 + slope * x
    inside = lambda x, y: y > edge_y(x)
    img = [[1 if inside(i + 0.5, j + 0.5) else 0 for i in range(NX)] for j in range(NY)]
    truth = [[sum(1 for a in range(8) for b in range(8) if inside(i + (a + .5) / 8, j + (b + .5) / 8)) / 64 for i in range(NX)] for j in range(NY)]
    # 縁の検出(上下の画素の差)
    edge = [[(img[j][i] != img[j - 1][i]) if j > 0 else False for i in range(NX)] for j in range(NY)]
    # 階段の長さ(各行の連続する縁)
    runs = []
    for j in range(1, NY):
        i = 0
        while i < NX:
            if edge[j][i]:
                k = i
                while k < NX and edge[j][k]:
                    k += 1
                runs.append((j, i, k - i))
                i = k
            else:
                i += 1
    # 重み: 階段の長さ L の中の位置 t から、縁の線が画素の中を通る割合(面積)を決める
    out = [[FG if img[j][i] else BG for i in range(NX)] for j in range(NY)]
    for (j, i0, L) in runs:
        if L < 2:
            continue
        for t in range(L):
            i = i0 + t
            d = (t + 0.5 - L / 2) / L                   # 縁の線の、行の境目からのずれ(+ = 下)
            if d <= 0:
                c_up = -d                                # 上の行にも、縁の下側(FG)がはみ出す
                out[j - 1][i] = BG * (1 - c_up) + FG * c_up
            else:
                c = 1 - d                                # この行の FG の割合が減る
                out[j][i] = BG * (1 - c) + FG * c
    err = lambda a: sum(abs(a[j][i] - (BG * (1 - truth[j][i]) + FG * truth[j][i])) for j in range(NY) for i in range(NX)) / (NX * NY)
    e_in = err([[FG if img[j][i] else BG for i in range(NX)] for j in range(NY)])
    e_out = err(out)
    assert e_out < e_in
    px = [30, 335, 640]
    labs = [("① 入力(階段)", GRAY), ("② 縁の画素(赤枠)と階段の長さ", RED), ("③ 割合で混ぜた結果", BLUE)]
    CS2 = 12.5
    t0, dts = 1.5, 0.15
    for p, (lab, col) in enumerate(labs):
        st.Panel(px[p], 100, NX * CS2, NY * CS2, lab, color=col)
        g = Grid(st, px[p], 100, NX, NY, CS2, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                v = out[j][i] if p == 2 else (FG if img[j][i] else BG)
                g.Paint(i, j, 0.3 if p < 2 else t0 + 6.0 + i * dts * 0.6, Gray(v))
        g.Flush()
        if p == 1:
            for j in range(NY):
                for i in range(NX):
                    if edge[j][i]:
                        g.Frame(i, j, RED, 2).Set(t0 + i * dts * 0.6, "opacity", 1)
    st.Text(px[1], 224, "検出した縁の画素: %d 個" % sum(1 for r in edge for v in r if v), size=13, weight=700, fill=RED)
    long_runs = [L for _, _, L in runs]
    st.Text(30, 270, "階段の長さ(連続する縁):", size=14, weight=700)
    sc.Text(root, 250, 270, "、".join(str(L) for L in long_runs[:6]) + (" …" if len(long_runs) > 6 else "") + "(画素)", size=14, weight=700, fill=PURPLE, opacity=0).Show(t0 + 3.0)
    t_w = t0 + 6.0
    st.Panel(30, 296, 900, 120, "④ 長さ 6 の階段の、画素ごとの混ぜる割合(縁の位置で変わる)", color=GREEN)
    L = 6
    for t in range(L):
        d = (t + 0.5 - L / 2) / L
        wgt = -d if d <= 0 else 1 - d
        x = 60 + t * 140
        g = root.add("g", opacity=0)
        g.Show(t_w + t * 0.5)
        g.add("rect", x=x, y=340, width=120, height=24, fill="#d1fae5", stroke="#16a34a", stroke_width=1.5)
        g.add("rect", x=x, y=340, width=R(120 * wgt), height=24, fill="#16a34a", opacity=0.8)
        sc.Text(g, x, 334, "%d 番目: 割合 %.2f" % (t + 1, wgt), size=12, weight=700, fill=TEXT)
    t_e = t_w + L * 0.5 + 2.0
    st.Box(t_e, 30, 436, 900, 76, [("正解とのずれ(平均): 入力 %.3f → SMAA %.3f" % (e_in, e_out), 15, "#1e3a8a"), ("手順: 縁を見つける → 階段の長さを数える → 長さと位置から、混ぜる割合(面積)を決める → 隣の画素と混ぜる", 12, TEXT), ("ぼかさず、縁の画素だけを、面積に合わせて混ぜる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ジャギーは、階段の形"), (t0, t_w, "輝度の差から、縁の画素に印を付け、階段の長さを調べる"), (t_w, t_e, "階段の長さと、位置から、面積の割合を決める"), (t_e, 99, "その割合で混ぜて、なめらかな縁にする")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "SMAA", "ずれ: 入力 %.3f → SMAA %.3f、階段の長さ %s" % (e_in, e_out, long_runs[:4]))
    return Build(st, name, "graphics/postprocess/antialiasing/smaa.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


NAMES = ["bloom-threshold", "bloom-intensity", "bloom-mip-chain", "dual-filter-passes", "gaussian-separable", "karis-fireflies", "taa-history-clamp", "taa-ghosting", "smaa-edge-weights"]
FIGS = [BloomThreshold, BloomIntensity, BloomMipChain, DualFilter, GaussianSeparable, KarisFireflies, TaaHistoryClamp, TaaGhosting, SmaaEdgeWeights]
