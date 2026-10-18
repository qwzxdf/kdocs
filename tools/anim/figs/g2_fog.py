import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== Fog integrate
def FogIntegrate():
    name = "fog-integrate"
    st = Stage(name, "霧の積分: 手前の層から順に、「光が減った分」と「霧が足した光」を積み重ねる", duration=22.0, subtitle="1 本の視線を、奥行き 16 枚のスライス(froxel)に分けて、前から順に積算する。霧の塊が、途中にある")
    sc, root = st.scene, st.root
    NZ = 16
    near, far = 0.5, 64.0
    edges = [near * (far / near) ** (i / NZ) for i in range(NZ + 1)]
    dz = [edges[i + 1] - edges[i] for i in range(NZ)]
    mid = [(edges[i] + edges[i + 1]) / 2 for i in range(NZ)]
    dens = [0.004 + 0.045 * math.exp(-((mid[i] - 14.0) / 5.0) ** 2) for i in range(NZ)]   # 霧の塊(距離 14 付近)
    insc = [0.6 + 0.4 * math.exp(-((mid[i] - 14.0) / 9.0) ** 2) for i in range(NZ)]         # 各スライスに溜まった光(光の注入の結果)
    T, L = 1.0, 0.0
    rows = []
    for i in range(NZ):
        a = math.exp(-dens[i] * dz[i])
        S_i = dens[i] * insc[i]
        add = (S_i - S_i * a) / dens[i] if dens[i] > 1e-9 else 0.0
        L += T * add
        T *= a
        rows.append((T, L, add, a))
    # 単純な足し算(厚みを考えない)
    T2, L2 = 1.0, 0.0
    for i in range(NZ):
        L2 += T2 * insc[i] * dens[i] * dz[i]
        T2 *= math.exp(-dens[i] * dz[i])
    err = abs(L - L2)
    assert rows[-1][0] < 1.0 and 0.05 < L < 1.0, (rows[-1], L)
    X0, BW = 60.0, 48.0
    st.Panel(30, 96, 900, 150, "① 各スライス(手前 → 奥)の、霧の濃さ", color=BLUE)
    for i in range(NZ):
        x = X0 + i * (BW + 3.5) * 1.0
        h = dens[i] / max(dens) * 90
        root.add("rect", x=R(x), y=R(228 - h), width=BW, height=R(max(h, 2)), fill="#93c5fd", opacity=0.9)
        sc.Text(root, R(x + BW / 2), 240, "%g m" % round(mid[i], 1), size=9, weight=500, fill=MUTED, anchor="middle")
    st.Text(40, 126, "棒 = そのスライスの霧の濃さ(中央が、霧の塊)。スライスの厚みは、奥ほど厚い", size=12, weight=500, fill=MUTED)
    st.Panel(30, 262, 900, 160, "② 積算の途中経過(前から順に)", color=PURPLE)
    t0, dts = 1.5, 0.9
    for i in range(NZ):
        t = t0 + i * dts
        x = X0 + i * (BW + 3.5)
        T_i, L_i, add, a = rows[i]
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=R(x), y=R(400 - T_i * 100), width=BW / 2 - 1, height=R(T_i * 100), fill="#c4b5fd", opacity=0.95)
        g.add("rect", x=R(x + BW / 2), y=R(400 - min(1.0, L_i) * 100), width=BW / 2 - 1, height=R(min(1.0, L_i) * 100), fill="#fcd34d", opacity=0.95)
    st.Legend(46, 288, [("#c4b5fd", "残った光(透過率 T)"), ("#fcd34d", "集めた霧の光")])
    ser = [(t0 + i * dts, int(round(100 * rows[i][0]))) for i in range(NZ)]
    st.Text(560, 290, "透過率:", size=15)
    st.Counter(640, 292, ser, size=22, fill=PURPLE)
    st.Text(690, 292, "%", size=16, weight=700, fill=PURPLE)
    ser2 = [(t0 + i * dts, int(round(100 * rows[i][1]))) for i in range(NZ)]
    st.Text(730, 290, "霧の光:", size=15)
    st.Counter(805, 292, ser2, size=22, fill="#b45309")
    t_end = t0 + NZ * dts + 0.6
    px = 1920 * 1080
    voxels = 160 * 90 * 64
    naive = px * 64
    st.Box(t_end, 30, 440, 900, 76, [("最終: 透過率 %d%%、霧の光 %.2f。厚みを考えた式で、足し算より正確(差 %.2f)" % (round(100 * rows[-1][0]), L, err), 15, "#1e3a8a"), ("3D テクスチャ 160×90×64 = %s 個で積算。画素ごとに 64 回進める方法は %s 回(約 %d 倍)" % (Fmt(voxels), Fmt(naive), round(naive / voxels)), 14, "#166534")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "霧の中を進む光は、減る(吸収・散乱)ことと、足される(霧が光る)ことを同時に受ける"), (t0, t_end, "前のスライスから順に、T(残る光)を掛けて、霧の光を足す"), (t_end, 99, "積算は 1 回。以後、どの画素も、奥行きに応じて、結果を 1 回読むだけ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "霧", "16 枚のスライスを前から積算。最終 T = %.3f、霧の光 = %.3f" % (rows[-1][0], L))
    return Build(st, name, "graphics/atmosphere/volumetric-fog/integration.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 18.0, 21.0])


# ===================================================================== Light injection
def LightInjection():
    name = "light-injection"
    st = Stage(name, "光の注入: 霧の 3D 格子の各マスに、「そこに届く光」を、ライトごとに書き込む", duration=20.0, subtitle="上から見た 1 つのスライス(24×12 マス)。2 つのライトと、光を遮る壁。各マスで、光を計算して足す")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 12, 25.0
    OX, OY = 40.0, 110.0
    lights = [(5.0, 3.0, (1.0, 0.75, 0.40), "暖色"), (19.0, 8.0, (0.45, 0.70, 1.0), "寒色")]
    wall = [(11, j) for j in range(0, 7)]    # 壁(光を遮る)

    def Blocked(a, b, p):
        # 線分 a→b が壁マスを通るか
        for k in range(40):
            t = k / 40
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            if (int(math.floor(x)), int(math.floor(y))) in wall:
                return True
        return False

    def Contribution(i, j, lt):
        c = (i + 0.5, j + 0.5)
        d2 = (c[0] - lt[0]) ** 2 + (c[1] - lt[1]) ** 2
        if Blocked((lt[0], lt[1]), c, None):
            return [0.0, 0.0, 0.0]
        a = 1.0 / (1.0 + 0.35 * d2)
        return [lt[2][k] * a for k in range(3)]

    stage1 = [[Contribution(i, j, lights[0]) for i in range(NX)] for j in range(NY)]
    stage2 = [[[stage1[j][i][k] + Contribution(i, j, lights[1])[k] for k in range(3)] for i in range(NX)] for j in range(NY)]
    st.Panel(30, 96, NX * CS + 20, NY * CS + 20, "① 霧の 1 スライス(各マスに、光を足す)", color=AMBER)
    t0, per = 1.5, 5.5
    ev = [stage1, stage2]
    g = Grid(st, OX, OY, NX, NY, CS, base="#0f172a")
    for j in range(NY):
        for i in range(NX):
            if (i, j) in wall:
                g.Paint(i, j, 0.3, "#475569")
                continue
            for m in range(2):
                v = ev[m][j][i]
                g.Paint(i, j, t0 + m * per + 0.05 * i, Hex([255 * min(1.0, x * 1.1) for x in v]))
    g.Flush()
    for m, lt in enumerate(lights):
        c = Hex([255 * v for v in lt[2]])
        n = root.add("g", opacity=0)
        n.Show(t0 + m * per - 0.5)
        n.add("circle", cx=R(OX + lt[0] * CS), cy=R(OY + lt[1] * CS), r=16, fill=c, opacity=0.4)
        n.add("circle", cx=R(OX + lt[0] * CS), cy=R(OY + lt[1] * CS), r=8, fill=c, stroke="#ffffff", stroke_width=2.5)
        sc.Text(n, OX + lt[0] * CS, OY + lt[1] * CS - 20, "ライト %d(%s)" % (m + 1, lt[3]), size=12, weight=700, fill="#ffffff", anchor="middle")
    sc.Text(root, OX + 11.5 * CS, OY + 7 * CS + 16, "壁(光を遮る)", size=11, weight=700, fill="#475569", anchor="middle")
    # 右: 計算量
    X1 = 680
    st.Panel(X1, 96, 250, 330, "② かかった計算", color=PURPLE)
    cells = NX * NY - len(wall)
    for m in range(2):
        gg = root.add("g", opacity=0)
        gg.Show(t0 + m * per)
        sc.Text(gg, X1 + 14, 140 + m * 70, "ライト %d" % (m + 1), size=16, weight=700, fill=PURPLE)
        sc.Text(gg, X1 + 14, 164 + m * 70, "%d マスで 1 回ずつ計算" % cells, size=13, weight=500, fill=TEXT)
    st.Text(X1 + 14, 300, "計算した回数:", size=14)
    st.Counter(X1 + 14, 332, [(t0 + m * per + 0.05 * NX, cells * (m + 1)) for m in range(2)], size=30, fill=PURPLE)
    full = 160 * 90 * 64
    st.Text(X1 + 14, 372, "実際の格子 160×90×64 なら", size=12, weight=500, fill=MUTED)
    st.Text(X1 + 14, 392, "%s マス × ライト数" % Fmt(full), size=13, weight=700, fill=TEXT)
    t_e = t0 + 2 * per + 0.6
    px = 1920 * 1080
    st.Box(t_e, 30, 440, 900, 74, [("格子に書き込むのは、ライトごとに %s マス(ライト 100 個なら %s 回)" % (Fmt(full), Fmt(100 * full)), 15, "#1e3a8a"), ("画素ごとに霧の中を進んで、ライトを足す方法なら、画素 %s × 歩数 64 × ライト数 になる" % Fmt(px), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "霧の中の各点に、どの色の光が、どれだけ届いているかを、先に調べて貯めておく"), (t0, t0 + per, "ライト 1: 距離で弱まり、壁の向こうには届かない"), (t0 + per, t_e, "ライト 2: 足し合わせると、2 色が混ざる所もできる"), (t_e, 99, "画面の画素には、関係しない計算量。ライトが増えても、格子の数だけ増える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "注入", "ライト 1: %d マスを計算(壁の %d マスを除く)" % (cells, len(wall)))
    st.Note(t0 + per, "注入", "ライト 2: 合計 %d 回" % (2 * cells))
    return Build(st, name, "graphics/atmosphere/volumetric-fog/injection.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 19.0])


# ===================================================================== Height fog
def HeightFogRay():
    name = "height-fog-ray"
    st = Stage(name, "高さ霧: 低い所ほど濃い霧を、視線に沿って積分する(式で一発 vs 少しずつ進める)", duration=22.0, subtitle="霧の濃さ = σ0 · exp(−b · 高さ)。カメラは高さ 4 から、斜め下の地面を見る。進める歩数で、式の値に近づく")
    sc, root = st.scene, st.root
    s0, b = 0.05, 0.35
    cam = (0.0, 4.0)
    tgt = (40.0, 0.0)
    L = math.hypot(tgt[0] - cam[0], tgt[1] - cam[1])
    dx, dy = (tgt[0] - cam[0]) / L, (tgt[1] - cam[1]) / L

    def Dens(h):
        return s0 * math.exp(-b * h)

    # 解析解
    def Analytic():
        h0 = cam[1]
        if abs(dy) < 1e-9:
            return Dens(h0) * L
        return s0 * math.exp(-b * h0) * (1 - math.exp(-b * dy * L)) / (b * dy) * -1 if False else s0 * math.exp(-b * h0) * (math.exp(-b * dy * L) - 1) / (-b * dy)

    exact = Analytic()
    def March(n):
        dt = L / n
        tau = 0.0
        for k in range(n):
            t = (k + 0.5) * dt
            tau += Dens(cam[1] + dy * t) * dt
        return tau

    ns = [2, 4, 8, 16, 64]
    taus = [March(n) for n in ns]
    errs = [abs(t - exact) / exact for t in taus]
    assert errs[0] > errs[2] > errs[4] and exact > 0.1
    ox, oy, SX, SY = 60.0, 330.0, 20.0, 40.0
    X = lambda x: ox + x * SX
    Y = lambda y: oy - y * SY
    st.Panel(30, 96, 900, 250, "① 断面(青い濃さ = 霧の濃さ)", color=BLUE)
    for k in range(40):
        h0 = k * 0.1
        a = Dens(h0) / s0
        root.add("rect", x=X(0), y=R(Y(h0 + 0.1)), width=R(40 * SX), height=R(0.1 * SY + 0.3), fill="#60a5fa", fill_opacity=R(0.08 + 0.55 * a))
    root.add("line", x1=X(0), y1=Y(0), x2=X(40), y2=Y(0), stroke="#475569", stroke_width=4)
    root.add("circle", cx=X(cam[0]), cy=Y(cam[1]), r=8, fill=INK)
    sc.Text(root, X(cam[0]) + 12, Y(cam[1]) - 6, "カメラ(高さ 4)", size=12, weight=700, fill=INK)
    root.add("line", x1=X(cam[0]), y1=Y(cam[1]), x2=X(tgt[0]), y2=Y(tgt[1]), stroke="#fca5a5", stroke_width=2, stroke_dasharray="6 5")
    t0, per = 1.5, 3.6
    cols = [RED, AMBER, GREEN, BLUE, PURPLE]
    for m, n in enumerate(ns):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < len(ns) - 1 else None)
        dt = L / n
        for k in range(n):
            t = (k + 0.5) * dt
            px, py = cam[0] + dx * t, cam[1] + dy * t
            g.add("circle", cx=R(X(px)), cy=R(Y(py)), r=min(6, 3 + 40 / n), fill=cols[m])
        sc.Text(g, 60, 128, "歩数 %d" % n, size=18, weight=700, fill=cols[m])
        sc.Text(g, 60, 152, "霧の濃さの積分(光学的厚さ)= %.3f" % taus[m], size=14, weight=700, fill=TEXT)
        sc.Text(g, 60, 174, "式の値 %.3f に対するずれ %.1f%%" % (exact, 100 * errs[m]), size=14, weight=700, fill=(RED if errs[m] > 0.05 else GREEN))
    # 下の棒
    st.Panel(30, 360, 560, 150, "② 歩数ごとのずれ(%)", color=PURPLE)
    for m, n in enumerate(ns):
        y = 388 + m * 24
        t = t0 + m * per + 0.3
        w = max(2.0, min(380.0, errs[m] * 100 * 14))
        gg = root.add("g", opacity=0)
        gg.Show(t)
        sc.Text(gg, 46, y + 12, "%d 歩" % n, size=12, weight=700, fill=cols[m])
        gg.add("rect", x=100, y=y, width=R(w), height=16, fill=cols[m], opacity=0.85)
        sc.Text(gg, 100 + w + 8, y + 13, "%.1f%%" % (100 * errs[m]), size=12, weight=700, fill=cols[m])
    t_e = t0 + len(ns) * per
    st.Box(t_e - 0.4, 620, 372, 310, 130, [("式 exp で、積分が一発で出る", 15, "#1e3a8a"), ("τ = σ0·e^(−b·h0)·(1 − e^(−b·dy·L)) ÷ (b·dy)", 13, TEXT), ("= %.3f(歩数 0 のコスト)" % exact, 14, "#166534"), ("少しずつ進めると、歩数分の計算が必要", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "霧は、低い所ほど濃い。視線が通る高さで、濃さが変わる"), (t0, t_e, "少しずつ進めて足すと、歩数が増えるほど、式の値に近づく"), (t_e, 99, "濃さが指数関数なら、積分は式で一発。毎画素の積分でも、歩数ゼロで正確")], size=14, fill=MUTED, weight=500)
    for m, n in enumerate(ns):
        st.Note(t0 + m * per, "高さ霧", "歩数 %d: τ = %.3f(式 %.3f、ずれ %.1f%%)" % (n, taus[m], exact, 100 * errs[m]))
    return Build(st, name, "graphics/atmosphere/aerial-fog/height-fog.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 18.0, 21.0])


NAMES = ["fog-integrate", "light-injection", "height-fog-ray"]
FIGS = [FogIntegrate, LightInjection, HeightFogRay]
