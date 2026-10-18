import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_gi import Track, Lcg  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== CDLOD
def TerrainQuadtree():
    name = "terrain-quadtree"
    st = Stage(name, "四分木 LOD: カメラに近い所だけ細かく分け、遠くは大きなまま描く", duration=21.0, subtitle="16×16 の地形。分けた回数 = レベル。カメラとの距離がノードの大きさの 1.5 倍より近ければ、4 つに分ける")
    sc, root = st.scene, st.root
    S, MAXL = 16.0, 4
    CS = 26.0
    X0, Y0 = 40.0, 100.0
    cols = ["#7dd3fc", "#86efac", "#fde047", "#fdba74", "#fca5a5"]
    cams = [(2.5, 13.0), (8.0, 8.0), (13.5, 2.5)]

    def Select(cam):
        out = []

        def Rec(L, x, y):
            s = S / (2 ** L)
            nx = max(x, min(cam[0], x + s))
            ny = max(y, min(cam[1], y + s))
            d = math.hypot(cam[0] - nx, cam[1] - ny)
            if L < MAXL and d < s * 1.5:
                h = s / 2
                for dx in (0, h):
                    for dy in (0, h):
                        Rec(L + 1, x + dx, y + dy)
            else:
                out.append((L, x, y, s))

        Rec(0, 0.0, 0.0)
        return out

    sels = [Select(c) for c in cams]
    full = 4 ** MAXL
    counts = [len(s) for s in sels]
    assert all(c < full for c in counts)
    area = [sum(s * s for _, _, _, s in sel) for sel in sels]
    assert all(abs(a - S * S) < 1e-9 for a in area)
    st.Panel(30, 96, S * CS + 20, S * CS + 20, "上から見た地形(色 = レベル)", color=BLUE)
    t0, per = 1.0, 6.0
    for m, sel in enumerate(sels):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        for (L, x, y, s) in sel:
            g.add("rect", x=R(X0 + x * CS), y=R(Y0 + y * CS), width=R(s * CS - 1.5), height=R(s * CS - 1.5), fill=cols[L], fill_opacity=0.55, stroke="#334155", stroke_width=1.2)
    cam = root.add("circle", cx=R(X0 + cams[0][0] * CS), cy=R(Y0 + cams[0][1] * CS), r=9, fill=INK, stroke="#ffffff", stroke_width=2.5)
    for m in range(1, 3):
        cam.Ramp(t0 + m * per - 1.2, t0 + m * per - 0.2, "cx", R(X0 + cams[m][0] * CS))
        cam.Ramp(t0 + m * per - 1.2, t0 + m * per - 0.2, "cy", R(Y0 + cams[m][1] * CS))
    sc.Text(root, X0 + cams[0][0] * CS + 12, Y0 + cams[0][1] * CS - 10, "カメラ", size=12, weight=700, fill=INK)
    # 右: 数字
    X1 = 500
    st.Panel(X1, 96, 430, 220, "選ばれたノード", color=PURPLE)
    for m, sel in enumerate(sels):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        per_level = [sum(1 for (L, *_r) in sel if L == l) for l in range(MAXL + 1)]
        for l in range(MAXL + 1):
            y = 136 + l * 26
            g.add("rect", x=X1 + 20, y=y - 14, width=18, height=18, fill=cols[l], opacity=0.8)
            sc.Text(g, X1 + 48, y, "レベル %d(1 辺 %g): %d 個" % (l, S / 2 ** l, per_level[l]), size=14, weight=500, fill=TEXT)
        sc.Text(g, X1 + 20, 290, "ノード %d 個 → 三角形 %s 個" % (len(sel), Fmt(len(sel) * 128)), size=18, weight=700, fill=PURPLE)
    st.Text(X1, 346, "ノード数:", size=16)
    st.Counter(X1 + 100, 350, [(t0 + m * per + 0.3, counts[m]) for m in range(3)], size=28, fill=PURPLE)
    st.Box(t0 + 3 * per - 0.5, X1, 376, 430, 100, [("全部を最も細かく描くと、ノード %d 個(三角形 %s 個)" % (full, Fmt(full * 128)), 14, "#991b1b"), ("四分木: %d / %d / %d 個(それぞれ %.0f%% / %.0f%% / %.0f%%)" % (counts[0], counts[1], counts[2], 100 * counts[0] / full, 100 * counts[1] / full, 100 * counts[2] / full), 14, "#166534"), ("どのノードも、同じ 8×8 の格子を使い回す(1 ノード = 三角形 128 個)", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 530, [(0.0, t0, "地形を 1 枚の大きなノードから始める"), (t0, t0 + per, "カメラが左下: そこだけ細かく分かれる"), (t0 + per, t0 + 2 * per, "カメラが中央: 中央が細かく、まわりは大きなまま"), (t0 + 2 * per, 99, "カメラが右上: 細かい所が追いかけてくる。描く数は、ほぼ一定")], size=14, fill=MUTED, weight=500)
    for m in range(3):
        st.Note(t0 + m * per, "LOD", "カメラ (%.1f, %.1f): ノード %d 個(全部細かくすると %d 個)" % (cams[m][0], cams[m][1], counts[m], full))
    return Build(st, name, "graphics/terrain/lod/cdlod.md", BEFORE, [1.5, 4.5, 7.5, 10.5, 15.0, 20.0])


# ===================================================================== fBm
def FbmOctaves():
    name = "fbm-octaves"
    st = Stage(name, "fBm: 周波数を 2 倍・振幅を半分にしたノイズを重ねて、自然な起伏を作る", duration=20.0, subtitle="1 次元のバリュー ノイズ。オクターブを 1 つずつ足していき、最後に「振幅の落とし方」を変えて比べる")
    sc, root = st.scene, st.root
    NS = 96
    rng = Lcg(77)
    lat = [rng.U() * 2 - 1 for _ in range(80)]

    def Noise(x):
        i = int(math.floor(x))
        f = x - i
        u = f * f * (3 - 2 * f)
        return lat[i % 80] * (1 - u) + lat[(i + 1) % 80] * u

    def Oct(o, gain, x):
        return (gain ** o) * Noise(x * 4.0 * (2 ** o) / NS * 1.0 + 0.37 * o)

    OC = 5
    def Total(n, gain):
        return [sum(Oct(o, gain, x) for o in range(n)) for x in range(NS)]

    X0, W = 50.0, 420.0
    XX = lambda i: X0 + i / (NS - 1) * W
    t0, per = 1.2, 2.4
    # 左: オクターブ
    st.Panel(30, 96, 460, 330, "① 各オクターブ(周波数 2 倍、振幅 1/2)", color=PURPLE)
    for o in range(OC):
        y = 140 + o * 56
        vals = [Oct(o, 0.5, x) for x in range(NS)]
        d = Poly([(XX(i), y - v * 30) for i, v in enumerate(vals)])
        g = root.add("g", opacity=0)
        g.Show(t0 + o * per)
        g.add("path", d=d, fill="none", stroke=[BLUE, GREEN, AMBER, RED, PURPLE][o], stroke_width=2.5)
        sc.Text(g, 56, y - 28, "オクターブ %d: 周波数 ×%d、振幅 %.2f" % (o + 1, 2 ** o, 0.5 ** o), size=12, weight=700, fill=[BLUE, GREEN, AMBER, RED, PURPLE][o])
    # 右: 累積
    st.Panel(510, 96, 420, 330, "② 足した結果", color=BLUE)
    cum_path = root.add("path", d=Poly([(510 + 16 + i / (NS - 1) * 388, 260) for i in range(NS)]), fill="none", stroke=BLUE, stroke_width=3.5)
    items = []
    for n in range(1, OC + 1):
        vals = Total(n, 0.5)
        items.append((t0 + (n - 1) * per, Poly([(526 + i / (NS - 1) * 388, 260 - v * 90) for i, v in enumerate(vals)])))
    cum_path.Steps("d", items)
    ser = [(t0 + n * per, n + 1) for n in range(OC)]
    cnt_items = [(0.0, t0, "ノイズ 0 回")] + [(t0 + n * per, t0 + (n + 1) * per if n < OC - 1 else 99, "足したオクターブ %d 個 = ノイズを 1 点あたり %d 回計算" % (n + 1, n + 1)) for n in range(OC)]
    st.Caption(530, 410, cnt_items, size=13, fill=PURPLE)
    # 下: 振幅の落とし方
    t_g = t0 + OC * per + 0.6
    st.Panel(30, 446, 900, 70, "③ 振幅の落とし方(gain)を変える", color=GREEN)
    gains = [0.35, 0.5, 0.7]
    for k, gn in enumerate(gains):
        vals = Total(OC, gn)
        rough = sum(abs(vals[i + 1] - vals[i]) for i in range(NS - 1)) / (NS - 1)
        x = 50 + k * 300
        g = root.add("g", opacity=0)
        g.Show(t_g + k * 2.0)
        g.add("path", d=Poly([(x + i / (NS - 1) * 250, 488 - v * 18) for i, v in enumerate(vals)]), fill="none", stroke=GREEN, stroke_width=2.5)
        sc.Text(g, x, 466, "gain %.2f: ざらつき %.3f" % (gn, rough), size=13, weight=700, fill=GREEN)
    rough_list = [sum(abs(Total(OC, gn)[i + 1] - Total(OC, gn)[i]) for i in range(NS - 1)) / (NS - 1) for gn in gains]
    assert rough_list[0] < rough_list[1] < rough_list[2]
    st.Caption(30, 534, [(0.0, t0, "地形の高さを、ノイズを重ねて作る"), (t0, t_g, "オクターブを足すほど、大きな起伏の上に、細かい起伏が乗る"), (t_g, 99, "gain が小さいと滑らか、大きいとざらつく。オクターブの数だけ、計算が増える")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "fBm", "オクターブ 1〜%d を足す" % OC)
    st.Note(t_g, "fBm", "gain 0.35 / 0.5 / 0.7: ざらつき %.3f / %.3f / %.3f" % tuple(rough_list))
    return Build(st, name, "graphics/terrain/generation/fbm.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== Cloud raymarch
def CloudRaymarch():
    name = "cloud-raymarch"
    st = Stage(name, "雲のレイマーチ: 光線を少しずつ進めて、密度を読み、透過率が下がったら打ち切る", duration=19.0, subtitle="雲の断面(40×14 マス)。カメラから右上へ光線を飛ばす。1 歩ごとに、密度から透過率を更新する")
    sc, root = st.scene, st.root
    NX, NY, CS = 40, 14, 14.0
    X0, Y0 = 40.0, 100.0
    blobs = [(14.0, 5.0, 4.2, 1.0), (21.0, 7.0, 3.4, 0.9), (27.0, 4.5, 3.0, 0.8)]

    def Dens(x, y):
        d = sum(a * math.exp(-((x - cx) ** 2 + ((y - cy) * 1.5) ** 2) / (2 * r * r)) for cx, cy, r, a in blobs)
        return max(0.0, min(1.0, d - 0.12))

    # y は下向きの画面座標(上が高い)
    cam = (1.0, 12.5)
    ang = math.radians(16.0)
    dirv = (math.cos(ang), -math.sin(ang))
    DT, SIG = 0.9, 2.6
    MAXS = 60
    T, rad = 1.0, 0.0
    steps = []
    exit_at = None
    for k in range(MAXS):
        t = (k + 0.5) * DT
        x, y = cam[0] + dirv[0] * t, cam[1] + dirv[1] * t
        if x >= NX or y < 0:
            break
        d = Dens(x, y)
        a = 1 - math.exp(-SIG * d * DT)
        rad += T * a
        T *= 1 - a
        steps.append((x, y, d, T, rad))
        if T < 0.05 and exit_at is None:
            exit_at = k + 1
    n_all = len(steps)
    n_stop = exit_at if exit_at else n_all
    assert exit_at is not None and n_stop < n_all
    full_rad = steps[-1][4]
    stop_rad = steps[n_stop - 1][4]
    st.Panel(30, 96, NX * CS + 20, NY * CS + 20, "雲(濃い所ほど青白く)と、光線", color=BLUE)
    g = Grid(st, X0 + 0, Y0 + 0, NX, NY, CS, base="#f8fafc")
    for j in range(NY):
        for i in range(NX):
            g.Paint(i, j, 0.4, Mix("#f8fafc", "#64748b", Dens(i + 0.5, j + 0.5)))
    g.Flush()
    root.add("circle", cx=R(X0 + cam[0] * CS), cy=R(Y0 + cam[1] * CS), r=8, fill=INK)
    sc.Text(root, X0 + cam[0] * CS + 10, Y0 + cam[1] * CS + 22, "カメラ", size=12, weight=700, fill=INK)
    t0, dts = 1.0, 0.16
    for k, (x, y, d, Tk, rk) in enumerate(steps):
        t = t0 + k * dts
        stopped = (k + 1 > n_stop)
        col = "#9ca3af" if stopped else Mix("#34d399", "#ef4444", min(1.0, d * 1.6))
        node = root.add("circle", cx=R(X0 + x * CS), cy=R(Y0 + y * CS), r=(3.2 if d < 0.01 else 3.2 + 4 * d), fill=col, stroke="#ffffff", stroke_width=1, opacity=0)
        node.Show(t)
    # 打ち切りの印
    xs, ys = steps[n_stop - 1][0], steps[n_stop - 1][1]
    stop_t = t0 + (n_stop - 1) * dts
    ring = root.add("circle", cx=R(X0 + xs * CS), cy=R(Y0 + ys * CS), r=13, fill="none", stroke=RED, stroke_width=4, opacity=0)
    ring.Show(stop_t + 0.05)
    sc.Text(root, X0 + xs * CS, Y0 + ys * CS - 20, "透過率 5% 未満で打ち切り", size=12, weight=700, fill=RED, anchor="middle", opacity=0).Show(stop_t + 0.05)
    # 右: 透過率
    X1 = 650
    st.Panel(X1, 96, 280, 250, "透過率 T と、集めた光", color=PURPLE)
    bar = root.add("rect", x=X1 + 30, y=R(150), width=36, height=R(150), fill="#c4b5fd", stroke="#7c3aed", stroke_width=2)
    for k, (x, y, d, Tk, rk) in enumerate(steps[:n_stop]):
        t = t0 + k * dts
        bar.Set(t, "y", R(300 - 150 * Tk))
        bar.Set(t, "height", R(max(150 * Tk, 0.5)))
    sc.Text(root, X1 + 48, 322, "T", size=14, weight=700, fill=PURPLE, anchor="middle")
    bar2 = root.add("rect", x=X1 + 130, y=R(300), width=36, height=0.5, fill="#fde68a", stroke="#f59e0b", stroke_width=2)
    for k, (x, y, d, Tk, rk) in enumerate(steps[:n_stop]):
        t = t0 + k * dts
        bar2.Set(t, "y", R(300 - 150 * min(1.0, rk)))
        bar2.Set(t, "height", R(max(150 * min(1.0, rk), 0.5)))
    sc.Text(root, X1 + 148, 322, "光", size=14, weight=700, fill="#b45309", anchor="middle")
    st.Text(X1 + 190, 190, "T の値:", size=12, weight=500, fill=MUTED)
    st.Counter(X1 + 190, 220, [(t0 + k * dts, int(round(100 * steps[k][3]))) for k in range(n_stop)], size=24, fill=PURPLE)
    st.Text(X1 + 232, 220, "%", size=16, weight=700, fill=PURPLE)
    st.Text(30, 392, "密度を読んだ回数:", size=16)
    st.Counter(190, 396, [(t0 + k * dts, k + 1) for k in range(n_stop)], size=26, fill=RED)
    t_end = t0 + n_stop * dts + 0.8
    st.Box(t_end, 330, 372, 600, 124, [("最後まで進めると %d 回、打ち切ると %d 回(%.0f%% 減)" % (n_all, n_stop, 100 * (1 - n_stop / n_all)), 16, "#1e3a8a"), ("集めた光: 最後まで %.3f / 打ち切り %.3f(差 %.1f%%)" % (full_rad, stop_rad, 100 * abs(full_rad - stop_rad) / full_rad), 15, "#166534"), ("濃い雲に入ると、奥は、ほとんど見えない。だから、早めにやめて良い", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "光線を少しずつ進めて、その場所の雲の密度を読む"), (t0, t0 + n_stop * dts, "雲に入ると、密度に応じて透過率 T が下がり、光が集まる"), (t_end - 0.8, 99, "T が十分小さくなったら、残りの区間は、見た目にほぼ影響しない")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "レイマーチ", "歩幅 %.1f、最大 %d 歩" % (DT, n_all))
    st.Note(stop_t, "レイマーチ", "歩 %d で透過率 5%% 未満 → 打ち切り" % n_stop)
    return Build(st, name, "graphics/atmosphere/clouds/raymarch.md", BEFORE, [1.5, 3.5, 5.5, 8.0, 11.0, 18.0])


# ===================================================================== Sunset
def SunsetPath():
    name = "sunset-path"
    st = Stage(name, "夕焼け: 太陽が低いほど、光が空気の中を長く通り、青から先に散ってなくなる", duration=19.0, subtitle="図は大気の厚みを誇張。太陽の高さを 90° → 30° → 10° → 2° に下げて、色を計算する")
    sc, root = st.scene, st.root
    RE, HA = 420.0, 56.0
    CX, CY = 330.0, 740.0
    # 地面(円弧)と大気
    st.Panel(30, 96, 600, 340, "地面と大気(断面)", color=BLUE)
    clip = sc.defs.add("clipPath", id="sun-clip")
    clip.add("rect", x=32, y=98, width=596, height=336)
    earth = root.add("g", clip_path="url(#sun-clip)")
    earth.add("circle", cx=CX, cy=CY, r=RE, fill="#d1fae5", stroke="#34d399", stroke_width=2)
    earth.add("circle", cx=CX, cy=CY, r=RE + HA, fill="#e0f2fe", fill_opacity=0.0, stroke="#93c5fd", stroke_width=2.5, stroke_dasharray="6 5")
    ox, oy = CX, CY - RE
    root.add("circle", cx=ox, cy=oy, r=7, fill=INK)
    sc.Text(root, ox, oy + 24, "見る人", size=12, weight=700, fill=INK, anchor="middle")
    elevs = [90.0, 30.0, 10.0, 2.0]
    tau = {"R": 0.0416, "G": 0.097, "B": 0.237}   # 海面での 天頂方向 の光学的厚さ(レイリー散乱)

    def AirMass(e):
        return 1.0 / (math.sin(math.radians(e)) + 0.50572 * (e + 6.07995) ** -1.6364)

    def Path(e):
        er = math.radians(e)
        return math.sqrt((RE + HA) ** 2 - (RE * math.cos(er)) ** 2) - RE * math.sin(er)

    def Trans(e):
        m = AirMass(e)
        return {c: math.exp(-tau[c] * m) for c in tau}

    res = [(e, Path(e), AirMass(e), Trans(e)) for e in elevs]
    assert res[3][2] > res[2][2] > res[1][2] > res[0][2] and res[3][3]["B"] < res[3][3]["R"]
    ph = 4.2
    t0 = 1.0
    for k, (e, L, m, T) in enumerate(res):
        er = math.radians(e)
        ex, ey = ox + math.cos(er) * L, oy - math.sin(er) * L
        g = root.add("g", opacity=0, clip_path="url(#sun-clip)")
        if k == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + ph, "opacity", 0)
        else:
            g.Show(t0 + k * ph, t0 + (k + 1) * ph if k < 3 else None)
        # 光線(太陽の方へ)
        far = 215.0
        g.add("line", x1=R(ox), y1=R(oy), x2=R(ox + math.cos(er) * far * (1 if e > 20 else 1.0)), y2=R(oy - math.sin(er) * far), stroke="#fde68a", stroke_width=2, stroke_dasharray="6 5")
        g.add("line", x1=R(ox), y1=R(oy), x2=R(ex), y2=R(ey), stroke=RED, stroke_width=4)
        sx, sy = ox + math.cos(er) * 215, oy - math.sin(er) * 215
        g.add("circle", cx=R(sx), cy=R(sy), r=14, fill=AMBER)
        sc.Text(g, ox + 40, oy + 22, "太陽の高さ %d°" % e, size=14, weight=700, fill=RED)
    # 右: 数字と色
    X1 = 660
    st.Panel(X1, 96, 270, 340, "太陽の色(大気を抜けた後)", color=PURPLE)
    for k, (e, L, m, T) in enumerate(res):
        g = root.add("g", opacity=0)
        if k == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + ph, "opacity", 0)
        else:
            g.Show(t0 + k * ph, t0 + (k + 1) * ph if k < 3 else None)
        col = Hex([255 * T["R"] ** 1.0 / max(T.values()) if False else 255 * T["R"] / T["R"] * (T["R"]) for _ in range(1)] * 3) if False else None
        sun = [T["R"], T["G"], T["B"]]
        mx = max(sun)
        swatch = Hex([255 * (c / mx) ** 1.0 * (0.55 + 0.45 * mx) for c in sun])
        g.add("circle", cx=R(X1 + 135), cy=170, r=44, fill=swatch, stroke="#334155", stroke_width=2)
        sc.Text(g, X1 + 135, 238, "空気の通る長さ: 天頂の %.1f 倍" % m, size=13, weight=700, fill=TEXT, anchor="middle")
        for ci, (cn, ccol) in enumerate([("R", RED), ("G", GREEN), ("B", BLUE)]):
            y = 262 + ci * 30
            g.add("rect", x=X1 + 40, y=y, width=R(190 * T[cn]), height=18, fill=ccol, opacity=0.85)
            sc.Text(g, X1 + 28, y + 14, cn, size=12, weight=700, fill=ccol, anchor="end")
            sc.Text(g, X1 + 40 + 190 * T[cn] + 6, y + 14, "%d%%" % round(100 * T[cn]), size=12, weight=700, fill=MUTED)
        sc.Text(g, X1 + 135, 370, ["真上: ほぼ白", "少し黄色っぽい", "オレンジ", "深い赤"][k], size=16, weight=700, fill=PURPLE, anchor="middle")
    st.Counter(70, 470, [(t0 + k * ph, int(elevs[k])) for k in range(4)], size=30, fill=RED)
    st.Text(120, 470, "度(太陽の高さ)", size=16)
    t_end = t0 + 4 * ph + 0.3
    st.Box(t_end - 0.3, 330, 450, 600, 70, [("青の光は、2° では %d%% しか届かない。赤は %d%%" % (round(100 * res[3][3]["B"]), round(100 * res[3][3]["R"])), 15, "#7f1d1d"), ("短い波長ほど散りやすい(レイリー散乱)。だから夕日は赤く、昼の空は青い", 13, MUTED)], RED, "#fef2f2")
    st.Caption(30, 534, [(0.0, t0, "太陽の光が、大気を通る長さを計算する"), (t0, t0 + ph, "真上: 一番短い。ほぼ白"), (t0 + ph, t0 + 2 * ph, "30°: 通る長さ 2 倍"), (t0 + 2 * ph, t0 + 3 * ph, "10°: 5〜6 倍。青が減る"), (t0 + 3 * ph, 99, "2°: 20 倍以上。青も緑もほとんど散って、赤だけ残る")], size=14, fill=MUTED, weight=500)
    for k, (e, L, m, T) in enumerate(res):
        st.Note(t0 + k * ph, "夕焼け", "高さ %d°: 空気の量 %.1f 倍、R %d%% / G %d%% / B %d%%" % (e, m, round(100 * T["R"]), round(100 * T["G"]), round(100 * T["B"])))
    return Build(st, name, "graphics/atmosphere/scattering/index.md", BEFORE, [1.5, 3.5, 6.0, 10.5, 14.0, 18.0])


# ===================================================================== SSS blur
def SssBlur():
    name = "sss-blur"
    st = Stage(name, "スクリーン スペース SSS: 赤だけ広く、青は狭くぼかすと、肌の「にじむ光」になる", duration=18.0, subtitle="1 列 48 画素の肌に、細い白い光の線が当たる。色ごとに、ぼかす広さ(ガウス)を変える")
    sc, root = st.scene, st.root
    N, CW, X0 = 48, 17.0, 60.0
    sig = {"R": 4.0, "G": 1.8, "B": 0.9}
    inp = [1.0 if 22 <= i <= 23 else 0.04 for i in range(N)]

    def Blur(s):
        out = []
        rad = int(math.ceil(3 * s))
        ws = [math.exp(-d * d / (2 * s * s)) for d in range(-rad, rad + 1)]
        tot = sum(ws)
        for i in range(N):
            acc = 0.0
            for k, d in enumerate(range(-rad, rad + 1)):
                j = min(N - 1, max(0, i + d))
                acc += ws[k] * inp[j]
            out.append(acc / tot)
        return out, rad

    ch = {c: Blur(s) for c, s in sig.items()}
    cols = {"R": RED, "G": GREEN, "B": BLUE}
    # 入力
    st.Text(X0, 98, "入力: 光の当たり方(細い線)", size=13, fill=MUTED)
    gi = Grid(st, X0, 104, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        gi.Paint(i, 0, 0.3, Gray(inp[i] ** 0.6))
    gi.Flush()
    # 色ごとの結果の棒グラフ
    st.Panel(30, 160, 900, 150, "① 色ごとのぼかし(縦 = 明るさ)", color=PURPLE)
    t0, per = 1.0, 2.6
    for k, c in enumerate("RGB"):
        vals, rad = ch[c]
        d = Poly([(X0 + (i + 0.5) * CW, 300 - min(1.0, vals[i] * 1.1) * 110) for i in range(N)])
        gp = root.add("path", d=d, fill="none", stroke=cols[c], stroke_width=3.5, opacity=0)
        gp.Show(t0 + k * per)
        sc.Text(root, 860, 196 + k * 18, "%s: ぼかす広さ σ = %.1f 画素" % (c, sig[c]), size=12, weight=700, fill=cols[c], anchor="end", opacity=0).Show(t0 + k * per)
    # 合成結果
    st.Text(X0, 332, "② 3 色を重ねた、肌の色", size=14, weight=700, fill=TEXT)
    gc = Grid(st, X0, 340, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    t_c = t0 + 3 * per + 0.6
    base = (0.9, 0.62, 0.52)
    for i in range(N):
        rgb = [min(1.0, base[k] * (0.18 + 1.35 * ch[c][0][i])) for k, c in enumerate("RGB")]
        gc.Paint(i, 0, t_c + 0.03 * i, Hex([255 * v for v in rgb]))
    gc.Flush()
    gn = Grid(st, X0, 366, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        rgb = [min(1.0, base[k] * (0.18 + 1.35 * inp[i] * 0.45)) for k in range(3)]
        gn.Paint(i, 0, t_c + 0.03 * i, Hex([255 * v for v in rgb]))
    gn.Flush()
    sc.Text(root, X0 + N * CW + 8, 358, "ぼかした", size=12, weight=700, fill=PURPLE)
    sc.Text(root, X0 + N * CW + 8, 384, "ぼかさない", size=12, weight=700, fill=MUTED)
    # コスト
    r_max = ch["R"][1]
    sep = 2 * (2 * r_max + 1)
    full2d = (2 * r_max + 1) ** 2
    px = 1920 * 1080
    assert sep < full2d
    st.Panel(30, 412, 900, 98, "③ 画面全体(1920×1080)でぼかすのに必要な読み込み(R の広さ σ=%.1f、半径 %d)" % (sig["R"], r_max), color=RED)
    t_k = t_c + N * 0.03 + 0.8
    g = root.add("g", opacity=0)
    g.Show(t_k)
    sc.Text(g, 50, 452, "縦横 2 回に分ける(分離)", size=14, weight=700, fill=GREEN)
    sc.Text(g, 50, 476, "1 画素あたり %d 回 → 画面全体で %s 回" % (sep, Fmt(sep * px)), size=14, weight=500, fill=TEXT)
    sc.Text(g, 490, 452, "2 次元でそのまま", size=14, weight=700, fill=RED)
    sc.Text(g, 490, 476, "1 画素あたり %s 回 → 画面全体で %s 回" % (Fmt(full2d), Fmt(full2d * px)), size=14, weight=500, fill=TEXT)
    sc.Text(g, 900, 500, "約 %d 倍の差" % round(full2d / sep), size=16, weight=700, fill=PURPLE, anchor="end")
    st.Caption(30, 534, [(0.0, t0, "光は、肌の中で散らばって、少し離れた所から出てくる"), (t0, t_c, "赤は広く、緑は中くらい、青は狭く、ぼかす"), (t_c, t_k, "重ねると、光の線のまわりに、赤い にじみが残る"), (t_k, 99, "縦横に分けると、読み込みが桁違いに少なくなる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "SSS", "R / G / B で、ぼかす広さを変える(σ = %.1f / %.1f / %.1f)" % (sig["R"], sig["G"], sig["B"]))
    st.Note(t_k, "SSS", "分離 %d 回 vs 2 次元 %d 回(1 画素あたり)" % (sep, full2d))
    return Build(st, name, "graphics/skin-hair/skin/screen-space-sss.md", BEFORE, [1.5, 4.0, 7.0, 10.5, 13.0, 17.0])


NAMES = ["terrain-quadtree", "fbm-octaves", "cloud-raymarch", "sunset-path", "sss-blur"]
FIGS = [TerrainQuadtree, FbmOctaves, CloudRaymarch, SunsetPath, SssBlur]
