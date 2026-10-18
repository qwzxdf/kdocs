import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_gi import Track, Lcg  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== Gerstner
def WaterGerstner():
    name = "water-gerstner"
    st = Stage(name, "ゲルストナー波: 水の粒は円を描く。横にも動くので、山が尖って谷が広がる", duration=22.0, subtitle="波の断面(横から見た図)。尖り具合 Q を 0 → 0.5 → 0.95 に上げる。水面の粒が円運動をする")
    sc, root = st.scene, st.root
    A = 1.1
    K = 2 * math.pi / 8.0
    OM = 1.4
    NP = 72
    X0, SX, Y0, SY = 70.0, 108.0, 225.0, 42.0
    Qs = [0.0, 0.5, 0.95]
    labels = ["Q = 0（ふつうの正弦波）", "Q = 0.5", "Q = 0.95（限界の近く）"]
    notes = ["粒は上下にだけ動く。山も谷も同じ形", "粒が円を描くので、山が狭く、谷が広くなる", "山がとがる。Q = 1 を超えると、水面が自分を貫いて崩れる"]
    ph = 7.0
    nf = 28
    st.Panel(30, 96, 900, 230, "① 水面の形(粒の位置を結んだ線)", color=BLUE)
    root.add("line", x1=30, y1=Y0, x2=930, y2=Y0, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="5 5")
    sc.Text(root, 40, Y0 - 6, "静かな水面", size=11, weight=500, fill=MUTED)

    def Surface(q, t):
        pts = []
        for i in range(NP + 1):
            x0 = 8.0 * i / NP * 1.0 * 1.0
            x0 = 12.0 * i / NP
            ph_ = K * x0 - OM * t
            x = x0 - q * A * math.sin(ph_)
            y = A * math.cos(ph_)
            pts.append((X0 + x * SX * 0.5, Y0 - y * SY))
        return pts

    def Metrics(q):
        pts = []
        for i in range(2001):
            x0 = -4.0 + 8.0 * i / 2000
            ph_ = K * x0
            pts.append((x0 - q * A * math.sin(ph_), A * math.cos(ph_)))
        above = [p[0] for p in pts if p[1] > 0]
        width = (max(above) - min(above)) / 8.0
        J = min(1 - q * A * K * math.cos(K * (-4.0 + 8.0 * i / 2000)) for i in range(2001))
        return width, J

    metr = [Metrics(q) for q in Qs]
    assert metr[0][0] > metr[1][0] > metr[2][0] and metr[2][1] > 0 and metr[1][1] > metr[2][1], metr
    path = root.add("path", d=Poly(Surface(0.0, 0.0)), fill="none", stroke=BLUE, stroke_width=4)
    frames = []
    for p, q in enumerate(Qs):
        for f in range(nf):
            t = 1.0 + p * ph + f * (ph / nf)
            frames.append((t, Poly(Surface(q, (f * (ph / nf)) * 1.0))))
    path.Steps("d", frames)
    # 粒(5 個): 円を描く
    parts = [1.0, 3.0, 5.0, 7.0, 9.0]
    for x0 in parts:
        node = root.add("circle", cx=0, cy=0, r=7, fill=RED)
        keys = []
        for p, q in enumerate(Qs):
            for f in range(nf + 1):
                tt = f * (ph / nf)
                ph_ = K * x0 - OM * tt
                x = x0 - q * A * math.sin(ph_)
                y = A * math.cos(ph_)
                keys.append((1.0 + p * ph + tt - (0.0 if f < nf else 1e-3), X0 + x * SX * 0.5, Y0 - y * SY))
        # 位相の境目で飛ばないよう、各位相を別に Track する
        for p in range(len(Qs)):
            seg = keys[p * (nf + 1):(p + 1) * (nf + 1)]
        prev = None
        for kk, (t, x, y) in enumerate(keys):
            if kk == 0:
                node.Set(t, "cx", R(x))
                node.Set(t, "cy", R(y))
            else:
                if kk % (nf + 1) == 0:
                    node.Set(t, "cx", R(x))
                    node.Set(t, "cy", R(y))
                else:
                    node.Ramp(prev, t, "cx", R(x))
                    node.Ramp(prev, t, "cy", R(y))
            prev = t
    # 数値
    for p, q in enumerate(Qs):
        t0, t1 = 1.0 + p * ph, 1.0 + (p + 1) * ph
        g = root.add("g", opacity=0)
        if p == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t1, "opacity", 0)
        else:
            g.Show(t0, t1 if p < 2 else None)
        sc.Text(g, 60, 360, labels[p], size=20, weight=700, fill=PURPLE)
        sc.Text(g, 60, 388, notes[p], size=14, weight=500, fill=TEXT)
        sc.Text(g, 60, 424, "山の水平幅 = 波長の %d%%" % round(100 * metr[p][0]), size=16, weight=700, fill=BLUE)
        sc.Text(g, 60, 450, "水面が詰まる度合い(J の最小値)= %.2f" % metr[p][1], size=16, weight=700, fill=(RED if metr[p][1] < 0.5 else GREEN))
    st.Box(1.0 + 3 * ph - 0.3, 520, 360, 410, 150, [("粒は、円を描いて動く(上下 + 横)", 15, "#1e3a8a"), ("Q を上げるほど、山が狭く・とがり、谷が広くなる", 14, TEXT), ("J = 1 − Q·A·k·cos(…) が 0 を下回ると、水面が自分を貫く", 13, MUTED), ("そこが「波頭が崩れる」= 泡が出る場所", 13, MUTED)], BLUE, "#eff6ff")
    st.Note(1.0, "ゲルストナー", "Q = 0: 正弦波、山の幅 %d%%、J 最小 %.2f" % (round(100 * metr[0][0]), metr[0][1]))
    st.Note(1.0 + ph, "ゲルストナー", "Q = 0.5: 山の幅 %d%%、J 最小 %.2f" % (round(100 * metr[1][0]), metr[1][1]))
    st.Note(1.0 + 2 * ph, "ゲルストナー", "Q = 0.95: 山の幅 %d%%、J 最小 %.2f" % (round(100 * metr[2][0]), metr[2][1]))
    return Build(st, name, "graphics/water/waves/gerstner.md", BEFORE, [2.0, 5.0, 9.0, 12.0, 16.0, 21.0])


# ===================================================================== FFT
def FftSpectrum():
    name = "fft-spectrum"
    st = Stage(name, "FFT の海: 波を「周波数ごとの強さ」で作り、逆変換で一度に高さにする", duration=20.0, subtitle="64 点の 1 次元の海。周波数ごとに、決まった強さの波を足し合わせる。時間が進むと、位相が回る")
    sc, root = st.scene, st.root
    N = 64
    KM = 20
    rng = Lcg(31)
    amp = []
    for k in range(1, KM + 1):
        a = math.exp(-1.0 / (k * 0.18) ** 2 * 0.05) / (k ** 1.15) * 3.0 * math.exp(-(k / 14.0) ** 2)
        amp.append(a)
    ph0 = [rng.U() * 2 * math.pi for _ in range(KM)]
    g = 9.8
    om = [math.sqrt(g * (2 * math.pi * k / 24.0)) * 0.55 for k in range(1, KM + 1)]

    def H(x, t):
        return sum(amp[k] * math.cos(2 * math.pi * (k + 1) * x / N - om[k] * t + ph0[k]) for k in range(KM))

    hs = [H(x, 0.0) for x in range(N)]
    hmax = max(abs(v) for v in hs) * 1.6
    # 離散フーリエ変換の確認(正しく元に戻るか)
    def Dft(vals):
        out = []
        for k in range(1, KM + 1):
            re = sum(vals[x] * math.cos(2 * math.pi * k * x / N) for x in range(N)) * 2 / N
            im = -sum(vals[x] * math.sin(2 * math.pi * k * x / N) for x in range(N)) * 2 / N
            out.append(math.hypot(re, im))
        return out

    back = Dft(hs)
    assert max(abs(a - b) for a, b in zip(back, amp)) < 1e-6
    # 上: 周波数ごとの強さ
    st.Panel(30, 96, 420, 200, "① 周波数ごとの波の強さ(スペクトル)", color=PURPLE)
    bx0, by0 = 50.0, 280.0
    amax = max(amp)
    for k in range(KM):
        h = amp[k] / amax * 140
        r = root.add("rect", x=R(bx0 + k * 19.5), y=R(by0 - h), width=16, height=R(h), fill="#c4b5fd", stroke="#7c3aed", stroke_width=1, opacity=0)
        r.Show(1.0 + k * 0.08)
    sc.Text(root, 50, 292, "低い周波数(長い波)", size=11, weight=500, fill=MUTED)
    sc.Text(root, 440, 292, "高い周波数(短い波)", size=11, weight=500, fill=MUTED, anchor="end")
    # 下: 高さ
    st.Panel(480, 96, 450, 200, "② 逆変換でできる、海の高さ", color=BLUE)
    X = lambda x: 500 + x / (N - 1) * 410
    Y = lambda v: 196 - v / hmax * 80
    root.add("line", x1=500, y1=196, x2=910, y2=196, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="5 5")
    path = root.add("path", d=Poly([(X(x), Y(H(x, 0.0))) for x in range(N)]), fill="none", stroke=BLUE, stroke_width=3.5)
    nfr = 36
    frames = [(1.0 + 2.2 + f * 0.33, Poly([(X(x), Y(H(x, f * 0.33 * 1.0))) for x in range(N)])) for f in range(nfr)]
    path.Steps("d", frames)
    # 足し合わせの途中(最初の 6 個の波)
    st.Text(40, 322, "波を 1 つずつ足していくと(最初の時刻)", size=13, fill=MUTED)
    pg = root.add("path", d=Poly([(50 + x / (N - 1) * 380, 370 - 0) for x in range(N)]), fill="none", stroke="#a78bfa", stroke_width=3)
    stack = []
    for cnt in (1, 2, 4, 8, 20):
        vals = [sum(amp[k] * math.cos(2 * math.pi * (k + 1) * x / N + ph0[k]) for k in range(cnt)) for x in range(N)]
        stack.append((cnt, Poly([(50 + x / (N - 1) * 380, 370 - vals[x] / hmax * 52) for x in range(N)])))
    pg.Steps("d", [(3.0 + i * 1.3, d) for i, (cnt, d) in enumerate(stack)])
    lab = sc.TextStack(root, 50, 418, [(3.0 + i * 1.3, 3.0 + (i + 1) * 1.3 if i < 4 else 99, "波 %d 個を足した形" % cnt) for i, (cnt, d) in enumerate(stack)], size=13, fill=PURPLE)
    # コスト
    st.Panel(480, 322, 450, 150, "③ 計算の回数(N 点)", color=RED)
    sizes = [64, 256, 1024, 4096]
    for i, n in enumerate(sizes):
        direct = n * n
        fft = int(n * math.log2(n))
        y = 354 + i * 28
        t = 11.0 + i * 1.2
        gx = root.add("g", opacity=0)
        gx.Show(t)
        sc.Text(gx, 496, y, "N = %d" % n, size=13, weight=700, fill=INK)
        sc.Text(gx, 590, y, "そのまま %s 回" % Fmt(direct), size=13, weight=500, fill=RED)
        sc.Text(gx, 750, y, "FFT %s 回" % Fmt(fft), size=13, weight=500, fill=GREEN)
        sc.Text(gx, 880, y, "×%d 速い" % round(direct / fft), size=13, weight=700, fill=BLUE, anchor="end")
    st.Caption(30, 520, [(0.0, 1.0, "海の高さを、直接作らず、周波数ごとの強さから作る"), (1.0, 3.0, "① 周波数ごとの強さを決める(長い波ほど強い)"), (3.0, 11.0, "② 波を足し合わせると、複雑な波になる。逆変換が一度にやってくれる"), (11.0, 99, "③ 逆変換を FFT で行えば、N が大きいほど、そのままの計算より桁違いに速い")], size=14, fill=MUTED, weight=500)
    st.Note(1.0, "FFT", "周波数 %d 個の強さ → 高さ 64 点" % KM)
    st.Note(11.0, "FFT", "計算回数: N=4096 で、そのまま %s / FFT %s" % (Fmt(4096 * 4096), Fmt(4096 * 12)))
    return Build(st, name, "graphics/water/waves/fft-ocean.md", BEFORE, [1.5, 3.5, 6.0, 9.0, 13.0, 19.0])


# ===================================================================== Jacobian
def JacobianFold():
    name = "jacobian-fold"
    st = Stage(name, "ヤコビアン: 水面が詰まって、折り返す所(J が小さい所)に泡を出す", duration=21.0, subtitle="3 つの波を足した、横にも動く水面。尖り具合 λ を上げると、折り返す所が増える")
    sc, root = st.scene, st.root
    N = 160
    comps = [(1.0, 0.55, 0.0), (2.0, 0.35, 1.3), (3.0, 0.22, 2.6)]   # (波の数, 振幅, 位相)
    L = 16.0
    X0, SX = 60.0, 50.0
    Y0, SY = 236.0, 82.0

    def Surf(lam):
        pts, J = [], []
        for i in range(N + 1):
            x0 = L * i / N
            dx = sum(a * math.sin(2 * math.pi * k * x0 / L * 1.0 + ph) for k, a, ph in comps)
            y = sum(a * math.cos(2 * math.pi * k * x0 / L + ph) for k, a, ph in comps)
            x = x0 - lam * dx
            pts.append((x, y))
            dj = sum(a * (2 * math.pi * k / L) * math.cos(2 * math.pi * k * x0 / L + ph) for k, a, ph in comps)
            J.append(1 - lam * dj)
        return pts, J

    lams = [0.0, 0.6, 1.2, 1.8]
    TH = 0.25
    data = [Surf(l) for l in lams]
    foam = [sum(1 for j in J if j < TH) for pts, J in data]
    assert foam[0] == 0 and foam[-1] > foam[1] >= 0 and foam[-1] > 4, foam
    st.Panel(30, 96, 900, 220, "① 水面の形(赤い点 = J が %.2f より小さい = 泡)" % TH, color=BLUE)
    root.add("line", x1=40, y1=Y0, x2=920, y2=Y0, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="5 5")
    ph = 4.6
    cur = root.add("path", d=Poly([(X0 + p[0] * SX, Y0 - p[1] * SY) for p in data[0][0]]), fill="none", stroke=BLUE, stroke_width=3.5)
    items = []
    for m in range(len(lams)):
        items.append((1.0 + m * ph, Poly([(X0 + p[0] * SX, Y0 - p[1] * SY) for p in data[m][0]])))
    cur.Steps("d", items)
    for m in range(len(lams)):
        t0 = 1.0 + m * ph
        t1 = 1.0 + (m + 1) * ph if m < len(lams) - 1 else None
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t1, "opacity", 0)
        else:
            g.Show(t0, t1)
        for i, (p, j) in enumerate(zip(data[m][0], data[m][1])):
            if j < TH:
                g.add("circle", cx=R(X0 + p[0] * SX), cy=R(Y0 - p[1] * SY), r=4, fill=RED)
        sc.Text(g, 60, 352, "λ = %.1f" % lams[m], size=22, weight=700, fill=PURPLE)
        sc.Text(g, 60, 382, "J が %.2f より小さい点: %d / %d 個" % (TH, foam[m], N + 1), size=15, weight=700, fill=(RED if foam[m] else GREEN))
        # J の帯
        gr = Grid(st, 60, 410, 80, 1, 10.0, base="#e5e7eb", parent=g, stroke="#94a3b8")
        for q in range(80):
            j = data[m][1][min(N, int(q * N / 80))]
            gr.Paint(q, 0, t0 + 0.2, "#fca5a5" if j < TH else Mix("#f1f5f9", "#38bdf8", min(1.0, max(0.0, j / 2.0))))
        gr.Flush()
        sc.Text(g, 60, 404, "J の帯(赤 = 泡)", size=12, weight=700, fill=MUTED)
    series = [(1.0 + m * ph + 0.2, foam[m]) for m in range(len(lams))]
    st.Text(560, 362, "泡の点の数:", size=16)
    st.Counter(670, 366, series, size=26, fill=RED)
    st.Box(1.0 + len(lams) * ph - 0.6, 560, 384, 370, 120, [("J = (横の伸び縮み)× 1 を、数値で調べる", 14, "#1e3a8a"), ("J < %.2f の所 = 水面が詰まって、折り返す所" % TH, 14, TEXT), ("→ 泡の濃さを、その場所だけ上げる", 14, TEXT), ("λ を上げるほど、泡の出る範囲が広がる", 13, MUTED)], BLUE, "#eff6ff")
    for m, l in enumerate(lams):
        st.Note(1.0 + m * ph, "ヤコビアン", "λ = %.1f: 泡の点 %d / %d" % (l, foam[m], N + 1))
    st.Caption(30, 530, [(0.0, 1.0, "水面の各点が、横にどれだけ動いたかから、詰まり具合 J を計算する"), (1.0, 1.0 + len(lams) * ph, "λ を上げて、波頭を尖らせる。J が小さい所に、赤い点(泡)が出る"), (1.0 + len(lams) * ph, 99, "泡は、波頭に沿って、自然に出る")], size=14, fill=MUTED, weight=500)
    return Build(st, name, "graphics/water/shore-foam/crest-jacobian.md", BEFORE, [1.5, 4.0, 7.0, 10.5, 15.0, 20.0])


# ===================================================================== Caustics
def CausticsRays():
    name = "caustics-rays"
    st = Stage(name, "コースティクス: 波が光を集めて、水底に明るい線を作る", duration=18.0, subtitle="真上から来る平行な光 48 本が、波打つ水面で曲がり(n = 1.33)、水底の 1 マスに当たる。当たった本数 = 明るさ")
    sc, root = st.scene, st.root
    NR = 48
    NB = 24
    n_w = 1.33
    AMP, WL, DEPTH = 0.5, 8.0, 9.0
    x_lo, x_hi = 0.0, 12.0
    SX = 70.0
    X0 = 60.0
    Ys, Yf = 130.0, 330.0
    SYD = (Yf - Ys) / DEPTH

    def Hit(x0, ph):
        k = 2 * math.pi / WL
        h = AMP * math.cos(k * x0 + ph)
        sl = -AMP * k * math.sin(k * x0 + ph)
        # 法線 (−sl, 1) → 入射は (0, −1)
        nx, ny = -sl, 1.0
        nl = math.hypot(nx, ny)
        nx, ny = nx / nl, ny / nl
        ci = ny
        si = math.sqrt(max(0.0, 1 - ci * ci))
        sin_t = si / n_w
        # 屈折の向き(下向き)
        sign = 1.0 if nx > 0 else -1.0
        th = math.asin(sin_t)
        ti = math.asin(si) * (1 if nx < 0 else -1) * -1
        # 水平方向のずれ: 法線から見た屈折角と入射角の差
        a_i = math.atan2(-nx, ny)             # 面の傾き(法線と鉛直の角)
        a_t = math.asin(math.sin(a_i) / n_w)
        dir_ang = a_i - a_t                     # 鉛直からの角度
        xh = x0 + math.tan(dir_ang) * (DEPTH - 0.0)
        return h, xh

    phases = [0.0, 1.6, 3.2]
    result = []
    for ph in phases:
        bins = [0] * NB
        rays = []
        for r in range(NR):
            x0 = x_lo + (x_hi - x_lo) * (r + 0.5) / NR
            h, xh = Hit(x0, ph)
            b = int(math.floor((xh - x_lo) / (x_hi - x_lo) * NB))
            if 0 <= b < NB:
                bins[b] += 1
            rays.append((x0, h, xh))
        result.append((bins, rays))
    uni = NR / NB
    peaks = [max(b) for b, _ in result]
    assert min(peaks) >= 4 and sum(result[0][0]) > NR * 0.8, (peaks, sum(result[0][0]))
    t0, per = 1.0, 5.5
    st.Panel(30, 96, 900, 250, "水面(波)と、屈折した光線", color=BLUE)
    root.add("rect", x=X0, y=Yf, width=(x_hi - x_lo) * SX, height=14, fill="#94a3b8")
    sc.Text(root, X0 + (x_hi - x_lo) * SX + 8, Yf + 12, "水底", size=12, weight=700, fill=MUTED)
    sc.Text(root, X0 + (x_hi - x_lo) * SX + 8, Ys + 4, "水面", size=12, weight=700, fill=MUTED)
    root.add("rect", x=X0, y=Ys, width=(x_hi - x_lo) * SX, height=Yf - Ys, fill="#bae6fd", opacity=0.35)
    for p, ph in enumerate(phases):
        bins, rays = result[p]
        g = root.add("g", opacity=0)
        if p == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + p * per, t0 + (p + 1) * per if p < 2 else None)
        # 水面の線
        pts = []
        for i in range(121):
            x0 = x_lo + (x_hi - x_lo) * i / 120
            k = 2 * math.pi / WL
            pts.append((X0 + x0 * SX, Ys - AMP * math.cos(k * x0 + ph) * 40))
        g.add("path", d=Poly(pts), fill="none", stroke=BLUE, stroke_width=3)
        for r, (x0, h, xh) in enumerate(rays):
            g.add("line", x1=R(X0 + x0 * SX), y1=R(Ys - h * 40), x2=R(X0 + xh * SX), y2=Yf, stroke="#fbbf24", stroke_width=1.2, opacity=0.8)
    # 棒グラフ(当たった本数)
    st.Panel(30, 366, 900, 130, "水底の 1 マスあたりに当たった光線の本数(平らな水面なら、どこも %.0f 本)" % uni, color=AMBER)
    bw = 900 / NB - 6
    for p in range(3):
        bins = result[p][0]
        g = root.add("g", opacity=0)
        if p == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + p * per, t0 + (p + 1) * per if p < 2 else None)
        for b in range(NB):
            v = bins[b]
            hgt = v * 14
            g.add("rect", x=R(40 + b * (900 / NB)), y=R(490 - hgt), width=R(bw), height=R(max(hgt, 0.5)), fill=Mix("#fde68a", "#f59e0b", min(1.0, v / 6.0)))
            if v:
                sc.Text(g, R(40 + b * (900 / NB) + bw / 2), R(490 - hgt) - 3, str(v), size=10, weight=700, fill="#92400e", anchor="middle")
        sc.Text(g, 900, 392, "最も明るい所: %d 本(平均の %.1f 倍)" % (peaks[p], peaks[p] / uni), size=14, weight=700, fill=RED, anchor="end")
    # 平坦の基準線
    root.add("line", x1=40, y1=R(490 - uni * 14), x2=930, y2=R(490 - uni * 14), stroke=GREEN, stroke_width=2, stroke_dasharray="6 5")
    st.Caption(30, 530, [(0.0, t0, "波の斜面が、光を曲げる"), (t0, t0 + per, "時刻 1: 斜面が光を中央に寄せる所が、明るい線になる"), (t0 + per, t0 + 2 * per, "時刻 2: 波が動くと、明るい線も動く"), (t0 + 2 * per, 99, "時刻 3: 本数が集まった所ほど明るい。これがコースティクス")], size=14, fill=MUTED, weight=500)
    for p in range(3):
        st.Note(t0 + p * per, "コースティクス", "時刻 %d: 最大 %d 本(平均 %.1f 本の %.1f 倍)" % (p + 1, peaks[p], uni, peaks[p] / uni))
    return Build(st, name, "graphics/water/underwater/caustics.md", BEFORE, [1.5, 4.5, 8.0, 11.5, 14.0, 17.0])


NAMES = ["water-gerstner", "fft-spectrum", "jacobian-fold", "caustics-rays"]
FIGS = [WaterGerstner, FftSpectrum, JacobianFold, CausticsRays]
