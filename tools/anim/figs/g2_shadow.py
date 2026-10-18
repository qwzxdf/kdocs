import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402

LIT = "#fde68a"
SHADOW = "#475569"


def ShadowMapScene():
    """断面で作る、シャドウ マップの実験。地面 28 マス + 箱。光は左上から。"""
    a = math.radians(50.0)
    ca, sa = math.cos(a), math.sin(a)
    U = lambda x, y: x * sa + y * ca       # 光に垂直な座標(シャドウ マップの横)
    V = lambda x, y: x * ca - y * sa       # 光の向きの距離(深度)
    BIN = 1.3
    # 各マスの「中心」から光線を飛ばして、いちばん近い面までの距離を表に書く
    umax = U(28.0, 0.0)
    umin = U(0.0, 0.0) - 0.0
    umin = min(umin, U(8.0, 3.0))
    umin = min(umin, U(0.0, 0.0))
    nb = int(math.ceil((max(umax, U(12.0, 3.0)) - umin) / BIN)) + 1
    depth = {}
    for b in range(nb):
        uc = umin + (b + 0.5) * BIN
        cands = []
        v = uc * ca / sa                      # 地面 y = 0
        x = uc * sa + v * ca
        if 0.0 <= x <= 28.0:
            cands.append(v)
        v = (uc * ca - 3.0) / sa              # 箱の上 y = 3
        x = uc * sa + v * ca
        if 8.0 <= x <= 12.0:
            cands.append(v)
        for wx in (8.0, 12.0):                # 箱の壁
            v = (wx - uc * sa) / ca
            y = uc * ca - v * sa
            if 0.0 <= y <= 3.0:
                cands.append(v)
        if cands:
            depth[b] = min(cands)
    nb = max(depth) + 1
    return dict(a=a, U=U, V=V, BIN=BIN, umin=umin, depth=depth, nb=nb)


def Judge(S, x, y, bias):
    b = int(math.floor((S["U"](x, y) - S["umin"]) / S["BIN"]))
    d = S["depth"].get(b, 1e9)
    return S["V"](x, y) - bias > d + 1e-9, b


def truth_shadow(S, x):
    """光線をさかのぼって、箱に当たるか(本物の影か)。"""
    if 8.0 < x < 12.0:
        return True
    ca, sa = math.cos(S["a"]), math.sin(S["a"])
    t = 0.0
    while t < 20.0:
        px, py = x - ca * t, sa * t
        if 8.0 <= px <= 12.0 and py <= 3.0:
            return True
        t += 0.01
    return False


def ShadowMapAcne():
    name = "shadow-map-probe"
    st = Stage(name, "シャドウ マップ: 光から見た「いちばん手前の深度」と比べて、影かどうかを決める", duration=22.0, subtitle="断面図。地面 28 マスのそれぞれを、光の側の深度表(シャドウ マップ)と比べる")
    sc, root = st.scene, st.root
    S = ShadowMapScene()
    N = 28
    cs, ox, oy = 17.0, 44.0, 258.0
    X = lambda x: ox + x * cs
    Y = lambda y: oy - y * cs
    BIAS_FIX = 1.2
    st.Panel(30, 92, 500, 200, "① 光から見たシーン(断面)", color=AMBER)
    # 地面と箱
    root.add("line", x1=X(0), y1=Y(0), x2=X(N), y2=Y(0), stroke="#94a3b8", stroke_width=3)
    root.add("rect", x=X(8), y=Y(3), width=4 * cs, height=3 * cs, fill="#cbd5e1", stroke="#94a3b8", stroke_width=2)
    st.Text(X(10), Y(1.4) + 4, "箱", size=14, fill=MUTED, anchor="middle")
    # 光線
    ca, sa = math.cos(S["a"]), math.sin(S["a"])
    for k in range(7):
        x0 = 1.0 + k * 3.6
        root.add("line", x1=R(X(x0)), y1=R(Y(8.5)), x2=R(X(x0 + 8.5 * ca / sa)), y2=R(Y(0.0)), stroke="#fbbf24", stroke_width=1.5, stroke_dasharray="5 5", opacity=0.85)
    sun = root.add("circle", cx=R(X(0.2)), cy=R(Y(9.0)), r=9, fill=AMBER)
    st.Text(X(0.2) + 14, Y(9.0) + 4, "光", size=13, fill=AMBER)

    # ---- 右: シャドウ マップ(深度の表) ----
    st.Panel(560, 92, 370, 200, "② シャドウ マップ(光から見た深度の表)", color=PURPLE)
    nb = S["nb"]
    bw = 340.0 / nb
    dmax = max(S["depth"].values())
    dmin = min(S["depth"].values())
    bars = []
    for b in range(nb):
        d = S["depth"].get(b)
        if d is None:
            continue
        hgt = 20 + 120 * (d - dmin) / (dmax - dmin)
        t = 1.0 + 0.22 * b
        g = root.add("rect", x=R(575 + b * bw), y=R(270 - hgt), width=R(bw - 2), height=R(hgt), fill="#c4b5fd", stroke="#7c3aed", stroke_width=1, opacity=0)
        g.Show(t)
        bars.append((t, b))
    st.Text(575, 112, "各マスに「いちばん近い面までの距離」を 1 つだけ書く", size=12, weight=500, fill=MUTED)
    st.Text(930 - 14, 284, "(棒が長い = 遠い)", size=11, weight=500, fill=MUTED, anchor="end")
    t_map_end = 1.0 + 0.22 * nb + 0.6
    st.Text(575, 312, "表への書き込み:", size=13)
    st.Counter(690, 314, [(t, i + 1) for i, (t, b) in enumerate(bars)], size=20, fill=PURPLE)
    st.Text(730, 312, "マス(深度の最小値だけ残す)", size=12, weight=500, fill=MUTED)

    # ---- 下: 地面 28 マスの判定 ----
    st.Text(30, 340, "③ 地面の 28 マスを、表と比べる(黄 = 光が当たる / 暗い = 影、赤枠 = 偽の影、青枠 = 欠けた影)", size=14)
    BIAS_FIX, BIAS_BIG = 0.8, 1.6
    rows = [("バイアス 0", 0.0, 356, RED), ("バイアス %.1f" % BIAS_FIX, BIAS_FIX, 408, GREEN), ("バイアス %.1f" % BIAS_BIG, BIAS_BIG, 460, BLUE)]
    t_start = t_map_end + 0.6
    dt = 0.12
    gap = N * dt + 1.4
    stats = []
    for r, (label, bias, ry, col) in enumerate(rows):
        grid = Grid(st, ox + 90, ry + 12, N, 1, 12.5, base="#e5e7eb", stroke="#94a3b8")
        st.Text(30, ry + 25, label, size=13, fill=col)
        false_n = missed_n = shadow_n = 0
        series = []
        for i in range(N):
            x = i + 0.5
            is_sh, b = Judge(S, x, 0.0, bias)
            hit = truth_shadow(S, x)
            ts = t_start + r * gap + i * dt
            grid.Paint(i, 0, ts, SHADOW if is_sh else LIT)
            if is_sh:
                shadow_n += 1
            if is_sh and not hit:
                false_n += 1
                grid.Frame(i, 0, RED, 3).Set(ts, "opacity", 1)
            if hit and not is_sh:
                missed_n += 1
                grid.Frame(i, 0, BLUE, 3).Set(ts, "opacity", 1)
            series.append((ts, i + 1))
        grid.Flush()
        stats.append((shadow_n, false_n, missed_n))
        st.Counter(ox + 90 + N * 12.5 + 14, ry + 31, series, size=17, fill=col)
        st.Text(ox + 90 + N * 12.5 + 48, ry + 30, "マス", size=12, weight=500, fill=MUTED)
    (sh0, f0, m0), (sh1, f1, m1), (sh2, f2, m2) = stats
    assert f0 >= 4 and f1 == 0 and m1 == 0 and m2 >= 1 and f2 == 0, stats
    t_end = t_start + 3 * gap
    st.Box(t_end, 610, 346, 320, 134, [("バイアス 0: 偽の影 %d マス(縞)" % f0, 15, "#991b1b"), ("バイアス %.1f: 偽の影 0、欠け 0 → 良い" % BIAS_FIX, 15, "#166534"), ("バイアス %.1f: 影が %d マス欠ける" % (BIAS_BIG, m2), 15, "#1e40af"), ("小さすぎると縞、大きすぎると影が浮く", 13, MUTED)], PURPLE, "#faf5ff")
    st.Caption(30, 524, [(0.0, 1.0, "光から見て、各方向のいちばん手前の面までの距離だけを覚える"), (1.0, t_map_end, "① 光から見た深度を、表(シャドウ マップ)に書く(マスの中心だけで測る)"), (t_start, t_start + gap, "② 地面の各マスの「光からの距離」を、表と比べる(バイアス 0)"), (t_start + gap, t_start + 2 * gap, "③ 比べる前に、少しだけ引く → 縞が消える"), (t_start + 2 * gap, t_end, "④ 引きすぎると、本物の影まで欠ける(影が浮く)"), (t_end, 99, "バイアスは、偽の影が消える最小に近い値にする")], size=14, fill=MUTED, weight=500)
    st.Note(1.0, "光", "シャドウ マップ %d マスに、深度の最小値を書く" % len(bars))
    st.Note(t_start, "判定", "バイアス 0: 影 %d マス(偽 %d)" % (sh0, f0))
    st.Note(t_start + gap, "判定", "バイアス %.1f: 影 %d マス(偽 %d)" % (BIAS_FIX, sh1, f1))
    st.Note(t_start + 2 * gap, "判定", "バイアス %.1f: 影 %d マス(欠け %d)" % (BIAS_BIG, sh2, m2))
    return Build(st, name, "graphics/shadows/shadow-map-basics/index.md", "## よくあるミス", [2.5, 5.5, 8.0, 12.0, 16.0, 21.0])


NAMES = ["shadow-map-probe"]
FIGS = [ShadowMapAcne]


# ===================================================================== PCF
def PcfKernel():
    name = "pcf-kernel"
    st = Stage(name, "PCF: 周りの数マスを調べて平均し、影の縁をなめらかにする", duration=16.0, subtitle="同じシャドウ マップ(1 マス = 3×3 ピクセルの荒い表)を、1 回 / 3×3 回 / 5×5 回 読んで比べる")
    sc, root = st.scene, st.root
    NX, NY, CS = 22, 14, 13.0
    TS = 3.0
    TX, TY = int(math.ceil(NX / TS)), int(math.ceil(NY / TS))
    cx0, cy0, rad = 11.0, 7.0, 6.2

    def mask(tx, ty):
        if tx < 0 or ty < 0 or tx >= TX or ty >= TY:
            return 0
        px, py = (tx + 0.5) * TS, (ty + 0.5) * TS
        return 1 if (px - cx0) ** 2 + (py - cy0) ** 2 <= rad * rad else 0

    def Pcf(x, y, k):
        r = k // 2
        vals = []
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                vals.append(mask(int(math.floor((x + 0.5 + dx * TS) / TS)), int(math.floor((y + 0.5 + dy * TS) / TS))))
        return sum(vals) / len(vals), vals

    ks = [1, 3, 5]
    titles = [("PCF なし(1 回)", RED), ("PCF 3×3(9 回)", BLUE), ("PCF 5×5(25 回)", GREEN)]
    px0 = [30, 335, 640]
    # 見本のピクセル(縁の上で、3×3 と 5×5 が違う値になる所)
    pick = None
    for y in range(NY):
        for x in range(NX):
            s1 = Pcf(x, y, 1)[0]
            s3 = Pcf(x, y, 3)[0]
            s5 = Pcf(x, y, 5)[0]
            if 0 < s3 < 1 and 0 < s5 < 1 and abs(s3 - s5) > 0.05 and x > 14 and 3 < y < 11:
                pick = (x, y)
                break
        if pick:
            break
    assert pick is not None
    dt = 0.16
    t0 = 1.0
    distinct = []
    for p, (k, (title, col)) in enumerate(zip(ks, titles)):
        x0 = px0[p]
        st.Panel(x0, 96, NX * CS, NY * CS, title, color=col)
        grid = Grid(st, x0, 96, NX, NY, CS, base="#e5e7eb")
        vals = set()
        series = []
        for i in range(NX):
            for j in range(NY):
                s, _ = Pcf(i, j, k)
                vals.add(round(s, 4))
                grid.Paint(i, j, t0 + i * dt, Mix(LIT, SHADOW, s))
            series.append((t0 + i * dt, (i + 1) * NY * k * k))
        grid.Flush()
        grid.Lines(color="#ffffff", opacity=0.18)
        distinct.append(len(vals))
        fr = root.add("rect", x=R(x0 + pick[0] * CS), y=R(96 + pick[1] * CS), width=CS, height=CS, fill="none", stroke=RED, stroke_width=3, opacity=0)
        fr.Show(t0 + NX * dt + 0.3)
        st.Text(x0, 304 + 18, "読み込み:", size=14)
        st.Counter(x0 + 78, 324, series, size=20, fill=col)
        # 見本ピクセルの内訳
        s, v = Pcf(pick[0], pick[1], k)
        g = root.add("g", opacity=0)
        g.Show(t0 + NX * dt + 0.6)
        kc = 15.0
        gx, gy = x0 + 6, 340
        for q, vv in enumerate(v):
            xx, yy = gx + (q % k) * kc, gy + (q // k) * kc
            g.add("rect", x=R(xx), y=R(yy), width=kc - 1, height=kc - 1, fill=("#334155" if vv else "#fde68a"), stroke="#94a3b8", stroke_width=1)
        sc.Text(g, x0 + 6 + k * kc + 12, gy + 16, "赤枠の画素:", size=12, weight=500, fill=MUTED)
        sc.Text(g, x0 + 6 + k * kc + 12, gy + 36, "影 %d / %d マス" % (sum(v), len(v)), size=14, fill=TEXT)
        sc.Text(g, x0 + 6 + k * kc + 12, gy + 58, "= 影の濃さ %.2f" % s, size=16, fill=col)
    assert distinct[0] == 2 and distinct[1] > distinct[0] and distinct[2] > distinct[1]
    t_end = t0 + NX * dt + 1.5
    st.Box(t_end, 30, 440, 900, 74, [("影の濃さの段階: 1 回 → %d 種類(0 か 1 だけ)/ 3×3 → %d 種類 / 5×5 → %d 種類" % tuple(distinct), 16, "#1e3a8a"), ("読み込みは 1 : 9 : 25。縁のなめらかさと引き換えに、画面の全画素で テクスチャ読み込みが 9 倍・25 倍に増える", 14, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 528, [(0.0, t0, "同じ荒いシャドウ マップを、3 通りの読み方で比べる"), (t0, t0 + NX * dt, "画面を左から右へなぞって、各画素の影の濃さを決める"), (t0 + NX * dt, t_end, "縁の 1 画素の中身: 読んだ 1 マスずつの 影 / 光 を、平均する"), (t_end, 99, "読む範囲が広いほどなめらかだが、読み込みが増える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "PCF", "3 つの読み方で画面をなぞる(1 / 9 / 25 回読み込み)")
    st.Note(t_end, "PCF", "影の濃さの段階: %d / %d / %d 種類" % tuple(distinct))
    return Build(st, name, "graphics/shadows/pcf.md", "## よくあるミス", [1.8, 3.5, 5.5, 8.0, 12.0, 15.0])


NAMES += ["pcf-kernel"]
FIGS += [PcfKernel]


# ===================================================================== CSM
def CascadeSplits():
    name = "cascade-splits"
    st = Stage(name, "カスケード シャドウ マップ: 距離で区切って、近くほど細かい影を割り当てる", duration=21.0, subtitle="4 つの影マップ(各 1024×1024)を、どこで区切るか。区切り方で、影の細かさが変わる")
    sc, root = st.scene, st.root
    NEAR, FAR, K = 0.5, 300.0, 4
    FOV = math.radians(60.0)
    SW, RES = 1920.0, 1024.0
    tan = math.tan(FOV / 2)
    X = lambda d: 70 + d / FAR * 830
    HALF = lambda d: d * tan / FAR * 150
    y0 = 200.0
    uni = [NEAR + (FAR - NEAR) * i / K for i in range(K + 1)]
    log = [NEAR * (FAR / NEAR) ** (i / K) for i in range(K + 1)]
    lam = 0.75
    pra = [lam * log[i] + (1 - lam) * uni[i] for i in range(K + 1)]
    modes = [("均等に区切る", uni, RED), ("対数で区切る", log, BLUE), ("混ぜる(実用)", pra, GREEN)]

    def Q(sp, i):
        n, f = sp[i], sp[i + 1]
        return math.sqrt(f / n) * SW / RES

    qs = [[Q(sp, i) for i in range(K)] for _, sp, _ in modes]
    assert qs[0][0] > 15 and max(qs[1]) - min(qs[1]) < 1e-9 and max(qs[2]) < qs[0][0]
    casc_col = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6"]
    st.Panel(30, 82, 900, 232, "カメラの上から見た図(左 = カメラ、右 = 遠く)", color=BLUE)
    root.add("circle", cx=70, cy=y0, r=7, fill=INK)
    polys = []
    for i in range(K):
        d = lambda m, i=i: "M%s,%s L%s,%s L%s,%s L%s,%s Z" % (R(X(modes[m][1][i])), R(y0 - HALF(modes[m][1][i])), R(X(modes[m][1][i + 1])), R(y0 - HALF(modes[m][1][i + 1])), R(X(modes[m][1][i + 1])), R(y0 + HALF(modes[m][1][i + 1])), R(X(modes[m][1][i])), R(y0 + HALF(modes[m][1][i])))
        p = root.add("path", d="M0,0 L0,0 L0,0 L0,0 Z", fill=casc_col[i], fill_opacity=0.55, stroke="#334155", stroke_width=1.5)
        polys.append((p, d))
    # 時刻
    tm = [1.0, 7.0, 13.0]
    morph = 1.6
    for i, (p, dfn) in enumerate(polys):
        p.Set(0.0, "d", dfn(0))
        p.Ramp(tm[1] - morph, tm[1], "d", dfn(1))
        p.Ramp(tm[2] - morph, tm[2], "d", dfn(2))
    # 区切りの距離ラベル
    for i in range(1, K):
        for m in range(3):
            pass
    for i in range(1, K + 1):
        for m in range(3):
            n = sc.Text(root, R(X(modes[m][1][i])), 306, "%.0f m" % modes[m][1][i], size=12, weight=700, fill=modes[m][2], anchor="middle", opacity=0)
            if m == 0:
                n.Set(0.0, "opacity", 1)
                n.Set(tm[1] - morph, "opacity", 0)
            elif m == 1:
                n.Show(tm[1] - morph * 0.0, tm[2] - morph)
            else:
                n.Show(tm[2])
    # ---- 下: 影の細かさ ----
    st.Panel(30, 352, 560, 150, "区間の真ん中で、影の 1 マス = 画面の何ピクセルぶんか", color=PURPLE, sub="小さいほど細かい")
    bx0, bw, base_y = 70, 78, 490
    SC = 3.4
    bars = []
    for i in range(K):
        r = root.add("rect", x=bx0 + i * 130, y=R(base_y - qs[0][i] * SC), width=bw, height=R(qs[0][i] * SC), fill=casc_col[i], opacity=0.85)
        r.Ramp(tm[1] - morph, tm[1], "y", R(base_y - qs[1][i] * SC))
        r.Ramp(tm[1] - morph, tm[1], "height", R(qs[1][i] * SC))
        r.Ramp(tm[2] - morph, tm[2], "y", R(base_y - qs[2][i] * SC))
        r.Ramp(tm[2] - morph, tm[2], "height", R(qs[2][i] * SC))
        sc.Text(root, bx0 + i * 130 + bw / 2, base_y + 4 + 0, "", size=1)
        st.Text(bx0 + i * 130 + bw / 2, 508 - 0, "カスケード %d" % (i + 1), size=12, weight=700, fill=INK, anchor="middle")
        # 数値(3 モードぶんを出し分け)
        for m in range(3):
            ta = tm[m] - (morph if m else 0.0)
            tb = tm[m + 1] - morph if m < 2 else 99
            n = sc.Text(root, bx0 + i * 130 + bw / 2, R(base_y - qs[m][i] * SC) - 6, "%.1f" % qs[m][i], size=14, weight=700, fill=modes[m][2], anchor="middle", opacity=0)
            if m == 0:
                n.Set(0.0, "opacity", 1)
                n.Set(tm[1] - morph, "opacity", 0)
            elif m == 1:
                n.Show(tm[1], tm[2] - morph)
            else:
                n.Show(tm[2])
    # ---- 右下: 説明 ----
    st.Box(0.5, 620, 372, 310, 128, [("", 1, TEXT)], LINE, "#f8fafc")
    lines = [("均等: カスケード 1 が粗い(%.0f)" % qs[0][0], RED, "遠景は十分細かいが、足元がぼやける"), ("対数: 全部そろう(%.1f)" % qs[1][0], BLUE, "でも、中間距離に無駄が出る"), ("混ぜる(λ=%.2f): 最大 %.1f" % (lam, max(qs[2])), GREEN, "よく選ばれる折衷案")]
    for m, (a, col, b) in enumerate(lines):
        ta = tm[m] - (morph if m else 0.0)
        tb = tm[m + 1] - morph if m < 2 else 99
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(tm[1] - morph, "opacity", 0)
        elif m == 1:
            g.Show(tm[1], tm[2] - morph)
        else:
            g.Show(tm[2])
        sc.Text(g, 636, 410, a, size=15, fill=col)
        sc.Text(g, 636, 436, b, size=13, weight=500, fill=MUTED)
    st.Caption(30, 528, [(0.0, tm[1] - morph, "① 均等に区切る: 近い所の影が、荒くなりやすい"), (tm[1] - morph, tm[2] - morph, "② 対数で区切る: 全カスケードの細かさが、そろう"), (tm[2] - morph, 99, "③ 二つを混ぜる: 近くを少し細かくして、遠くを無駄にしない")], size=14, fill=MUTED, weight=500)
    st.Note(tm[0], "CSM", "均等: カスケードごとの粗さ %s" % ", ".join("%.1f" % v for v in qs[0]))
    st.Note(tm[1], "CSM", "対数: %s" % ", ".join("%.1f" % v for v in qs[1]))
    st.Note(tm[2], "CSM", "混ぜる(λ=%.2f): %s" % (lam, ", ".join("%.1f" % v for v in qs[2])))
    return Build(st, name, "graphics/shadows/cascaded.md", "## よくあるミス", [1.0, 5.0, 8.5, 12.0, 15.0, 20.0])


NAMES += ["cascade-splits"]
FIGS += [CascadeSplits]
