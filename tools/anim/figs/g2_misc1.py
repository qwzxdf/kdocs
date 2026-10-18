import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== Snell
def SnellRefraction():
    name = "snell-refraction"
    st = Stage(name, "屈折: ガラス板を斜めに通る光は、曲がり、横にずれて出てくる(スネルの法則)", duration=22.0, subtitle="厚さ 3 のガラス板(n = 1.5)。入射角を 20° → 40° → 60° → 75° に変えて、曲がる角度とずれを計算する")
    sc, root = st.scene, st.root
    n = 1.5
    T = 3.0
    ox, oy, S = 330.0, 215.0, 30.0
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * S
    angles = [20.0, 40.0, 60.0, 75.0]
    rows = []
    for a in angles:
        ti = math.radians(a)
        tr = math.asin(math.sin(ti) / n)
        # 板の上面の入口を (0, 0)、板の中で厚さ T 進み、下面で出る
        x_in = 0.0
        x_out = T * math.tan(tr)
        # 直進していたら、板の下面で x = T * tan(ti)
        x_str = T * math.tan(ti)
        # 横ずれ(出る光線と、入る光線の延長線の距離)
        shift = T * math.sin(ti - tr) / math.cos(tr)
        rows.append((a, math.degrees(tr), x_out, x_str, shift))
    assert rows[0][4] < rows[1][4] < rows[2][4] < rows[3][4]
    st.Panel(30, 96, 900, 280, "① ガラス板の断面(上 = 空気、中 = ガラス、下 = 空気)", color=BLUE)
    root.add("rect", x=R(X(-6)), y=R(Y(0)), width=R(12 * S), height=R(T * S), fill="#bae6fd", fill_opacity=0.5, stroke="#38bdf8", stroke_width=2)
    sc.Text(root, X(-5.8), Y(0) + 18, "ガラス(n = 1.5)", size=12, weight=700, fill="#0369a1")
    sc.Text(root, X(-5.8), Y(0) - 8, "空気(n = 1)", size=12, weight=500, fill=MUTED)
    t0, per = 1.0, 5.2
    for m, (a, tr, xo, xs, shift) in enumerate(rows):
        ti = math.radians(a)
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        L0 = 1.5
        # 入る光線(空気中)
        g.add("line", x1=R(X(-L0 * math.sin(ti))), y1=R(Y(L0 * math.cos(ti))), x2=R(X(0)), y2=R(Y(0)), stroke=AMBER, stroke_width=4)
        # ガラスの中
        g.add("line", x1=R(X(0)), y1=R(Y(0)), x2=R(X(xo)), y2=R(Y(-T)), stroke=RED, stroke_width=4)
        # 出る光線
        g.add("line", x1=R(X(xo)), y1=R(Y(-T)), x2=R(X(xo + L0 * math.sin(ti))), y2=R(Y(-T - L0 * math.cos(ti))), stroke=AMBER, stroke_width=4)
        # 入る光線をそのまま延ばした線
        g.add("line", x1=R(X(0)), y1=R(Y(0)), x2=R(X(xs)), y2=R(Y(-T)), stroke=GRAY, stroke_width=2, stroke_dasharray="6 5")
        g.add("line", x1=R(X(xs)), y1=R(Y(-T)), x2=R(X(xs + L0 * math.sin(ti))), y2=R(Y(-T - L0 * math.cos(ti))), stroke=GRAY, stroke_width=2, stroke_dasharray="6 5")
        # 法線
        g.add("line", x1=R(X(0)), y1=R(Y(1.5)), x2=R(X(0)), y2=R(Y(-1.0)), stroke="#94a3b8", stroke_width=1.5, stroke_dasharray="3 4")
        sc.Text(g, 50, 130, "入射角 %d°" % a, size=22, weight=700, fill=PURPLE)
        sc.Text(g, 50, 158, "sin %d° ÷ 1.5 = sin(屈折角)" % a, size=14, weight=500, fill=TEXT)
        sc.Text(g, 50, 182, "屈折角 %.1f°" % tr, size=16, weight=700, fill=RED)
        sc.Text(g, 50, 208, "出口の横ずれ(灰色 = 曲がらない場合との差): %.2f" % shift, size=14, weight=700, fill="#92400e")
    st.Text(40, 410, "背景の縞模様を、ガラスごしに見たときのずれ:", size=14, weight=700)
    # 縞をずらす
    N, CW, X1 = 36, 16.0, 40.0
    stripes = lambda i: "#2563eb" if (i // 3) % 2 == 0 else "#93c5fd"
    g0 = Grid(st, X1, 424, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        g0.Paint(i, 0, 0.3, stripes(i))
    g0.Flush()
    sc.Text(root, X1 + N * CW + 8, 438, "ガラスなし", size=12, weight=700, fill=GRAY)
    g1 = Grid(st, X1, 452, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for m, (a, tr, xo, xs, shift) in enumerate(rows):
        dxp = int(round(shift * 2.0))
        for i in range(N):
            g1.Paint(i, 0, t0 + m * per + 0.4, stripes((i + dxp) % (N * 2)))
    g1.Flush()
    sc.Text(root, X1 + N * CW + 8, 466, "ガラスごし", size=12, weight=700, fill=RED)
    series = [(t0 + m * per + 0.3, int(round(100 * rows[m][4]))) for m in range(4)]
    st.Text(40, 502, "ずれの大きさ(×100):", size=14)
    st.Counter(200, 506, series, size=22, fill=RED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.4, 640, 480, 290, 50, [("入射角が大きいほど、横ずれが増える", 14, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "光は、空気からガラスへ入ると、曲がる(屈折率が違うため)"), (t0, t_e, "角度を変えると、曲がり方と、横ずれが変わる"), (t_e, 99, "ゲームでは、ガラスの法線を使って、画面の背景を、ずらして見せる(スクリーン スペース屈折)")], size=14, fill=MUTED, weight=500)
    for m, (a, tr, xo, xs, shift) in enumerate(rows):
        st.Note(t0 + m * per, "屈折", "入射角 %d°: 屈折角 %.1f°、横ずれ %.2f" % (a, tr, shift))
    return Build(st, name, "graphics/translucency/refraction/index.md", BEFORE, [1.5, 4.5, 8.0, 12.0, 17.0, 21.0])


# ===================================================================== Beer thickness
def BeerThickness():
    name = "beer-thickness"
    st = Stage(name, "色つきガラス: 光が通る厚さに応じて、色ごとに光が減る(ベールの法則)", duration=20.0, subtitle="緑がかったガラスは、赤と青を多く吸う。厚い所ほど、緑が濃く、暗くなる")
    sc, root = st.scene, st.root
    sig = {"R": 0.60, "G": 0.12, "B": 0.45}   # 厚さ 1 あたりの吸収
    back = (1.0, 1.0, 1.0)
    # 上: くさび形(厚さ 0〜4)
    N, CW, X0 = 40, 20.0, 60.0
    st.Text(X0, 110, "くさび形のガラス(左 = 薄い 0、右 = 厚い 4)", size=14, weight=700, fill=BLUE)
    for i in range(N):
        t = 4.0 * (i + 0.5) / N
        pass
    g = Grid(st, X0, 120, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    t0, dts = 1.5, 0.12
    wedge = []
    for i in range(N):
        t = 4.0 * (i + 0.5) / N
        col = [back[k] * math.exp(-sig[c] * t) for k, c in enumerate("RGB")]
        wedge.append(col)
        g.Paint(i, 0, t0 + i * dts, Hex([255 * v for v in col]))
    g.Flush()
    # 曲線
    st.Panel(X0 - 20, 168, N * CW + 40, 130, "色ごとに通る光の割合(厚さ → 光)", color=PURPLE)
    ax0, ay0, aw, ah = X0, 184.0, N * CW, 96.0
    XX = lambda t: ax0 + t / 4.0 * aw
    YY = lambda v: ay0 + ah - v * ah
    for c, col in zip("RGB", [RED, GREEN, BLUE]):
        pts = [(XX(4.0 * k / 60), YY(math.exp(-sig[c] * 4.0 * k / 60))) for k in range(61)]
        p = root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(t0 + N * dts + 0.3 + "RGB".index(c) * 0.7)
        sc.Text(root, ax0 + aw - 8, YY(math.exp(-sig[c] * 4.0)) - 6, c, size=13, weight=700, fill=col, anchor="end", opacity=0).Show(t0 + N * dts + 0.3 + "RGB".index(c) * 0.7)
    # 下: 球(厚さが場所で変わる)
    st.Text(40, 330, "ガラスの球(中心ほど厚い)を、正面から見る", size=14, weight=700, fill=BLUE)
    D, CS = 18, 8.0
    sph = []
    for j in range(D):
        for i in range(D):
            x, y = (i + 0.5 - D / 2) / (D / 2), (j + 0.5 - D / 2) / (D / 2)
            r2 = x * x + y * y
            sph.append((i, j, 3.0 * math.sqrt(max(0.0, 1 - r2)) if r2 < 1 else None))
    gs = Grid(st, 60, 338, D, D, CS, base="#ffffff")
    t_s = t0 + N * dts + 2.6
    for (i, j, t) in sph:
        if t is None:
            gs.Paint(i, j, 0.3, "#ffffff")
        else:
            col = [back[k] * math.exp(-sig[c] * t) for k, c in enumerate("RGB")]
            gs.Paint(i, j, t_s + 0.012 * (i + j), Hex([255 * v for v in col]))
    gs.Flush()
    # 右: 数値
    t_mid = 3.0
    colm = [math.exp(-sig[c] * t_mid) for c in "RGB"]
    colt = [math.exp(-sig[c] * 0.5) for c in "RGB"]
    colc = [math.exp(-sig[c] * 3.0) for c in "RGB"]
    st.Box(t_s + 1.5, 260, 338, 670, 130, [("薄い所(厚さ 0.5): R %d%% / G %d%% / B %d%% → ほぼ透明" % tuple(round(100 * v) for v in colt), 14, "#1e3a8a"), ("球の中心(厚さ 3.0): R %d%% / G %d%% / B %d%% → 濃い緑" % tuple(round(100 * v) for v in colc), 14, "#166534"), ("色ごとの係数 σ が違うので、厚さによって「色合い」が変わる", 13, TEXT), ("(薄くて青白い → 厚くて濃い緑)。厚さ = 表と裏の深度の差で、画素ごとに求める", 12, MUTED)], GREEN, "#f0fdf4")
    sx = [(t_s + 0.012 * (i + j), 0) for (i, j, t) in sph if t is not None]
    st.Text(260, 500, "計算した画素:", size=14)
    ser = []
    c = 0
    for k in range(D):
        c += sum(1 for (i, j, t) in sph if t is not None and (i + j) == k)
        ser.append((t_s + 0.012 * k, c))
    st.Counter(380, 504, ser, size=22, fill=PURPLE)
    st.Caption(30, 534, [(0.0, t0, "色つきのガラスは、光が通る距離が長いほど、色が濃くなる"), (t0, t0 + N * dts + 2.5, "厚さ 0 → 4 で、色ごとの光の減り方が変わる(緑は減りにくい)"), (t_s, 99, "球では、中心ほど厚いので、中心が濃い緑、ふちは薄く透明になる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ベール", "くさび形: 厚さ 0〜4 の 40 段階を計算")
    st.Note(t_s, "ベール", "球: 中心の厚さ 3.0 → R %d%% / G %d%% / B %d%%" % tuple(round(100 * v) for v in colc))
    return Build(st, name, "graphics/translucency/refraction/thickness-color.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 14.0, 19.0])


# ===================================================================== FXAA
def FxaaEdge():
    name = "fxaa-edge"
    st = Stage(name, "FXAA: 輝度の差が大きい画素だけを見つけて、周りの色と混ぜる(後処理 1 回)", duration=18.0, subtitle="縁のある 20×8 画素の画像。まず、周りと輝度が大きく違う画素を探し、そこだけ、ぼかす")
    sc, root = st.scene, st.root
    NX, NY, CS = 20, 8, 13.0
    BG, FG = 0.95, 0.15
    inside = lambda x, y: y > 0.5 * x - 0.8

    def Samp(x, y):
        return FG if inside(x, y) else BG

    def Truth(i, j, m=8):
        return sum(Samp(i + (a + 0.5) / m, j + (b + 0.5) / m) for a in range(m) for b in range(m)) / (m * m)

    img = [[Samp(i + 0.5, j + 0.5) for i in range(NX)] for j in range(NY)]
    truth = [[Truth(i, j) for i in range(NX)] for j in range(NY)]
    TH = 0.20
    edge = {}
    out = [row[:] for row in img]
    for j in range(NY):
        for i in range(NX):
            c = img[j][i]
            nb = [img[min(NY - 1, max(0, j + dj))][min(NX - 1, max(0, i + di))] for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            lo, hi = min(nb + [c]), max(nb + [c])
            ctr = hi - lo
            if ctr >= TH:
                edge[(i, j)] = ctr
                k = min(0.5, ctr * 0.7)
                out[j][i] = (1 - k) * c + k * sum(nb) / 4
    n_edge = len(edge)
    n_all = NX * NY
    err_in = sum(abs(img[j][i] - truth[j][i]) for j in range(NY) for i in range(NX)) / n_all
    err_out = sum(abs(out[j][i] - truth[j][i]) for j in range(NY) for i in range(NX)) / n_all
    assert err_out < err_in and 0 < n_edge < n_all / 2
    px = [30, 335, 640]
    titles = [("① 入力(ジャギー)", GRAY), ("② 縁の画素を探す(赤枠)", RED), ("③ 縁だけ、周りと混ぜた結果", BLUE)]
    t0, dts = 1.5, 0.12
    for p, (lab, col) in enumerate(titles):
        st.Panel(px[p], 100, NX * CS, NY * CS, lab, color=col)
        g = Grid(st, px[p], 100, NX, NY, CS, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                v = out[j][i] if p == 2 else img[j][i]
                tt = (0.5 if p < 2 else t0 + 7.5 + i * dts * 0.6)
                g.Paint(i, j, tt, Gray(v))
        g.Flush()
        if p == 1:
            for (i, j), ctr in edge.items():
                fr = g.Frame(i, j, RED, 2.5)
                fr.Set(t0 + i * dts + j * 0.02, "opacity", 1)
    ser = []
    c = 0
    for i in range(NX):
        c += sum(1 for (ii, jj) in edge if ii == i)
        ser.append((t0 + i * dts, c))
    st.Text(px[1], 330, "縁の画素:", size=15)
    st.Counter(px[1] + 90, 332, ser, size=22, fill=RED)
    st.Text(px[1] + 130, 332, "/ %d" % n_all, size=14, weight=500, fill=MUTED)
    st.Text(px[2], 330, "ずれ(正解との平均差):", size=13)
    sc.Text(root, px[2], 356, "入力 %.3f → 結果 %.3f" % (err_in, err_out), size=15, weight=700, fill=BLUE, opacity=0).Show(t0 + 9.0)
    skip = n_all - n_edge
    t_e = t0 + 9.5
    st.Box(t_e, 30, 384, 900, 110, [("縁の画素 %d 個だけ、念入りに処理。残り %d 個(%.0f%%)は、輝度の差が小さいので、そのまま" % (n_edge, skip, 100 * skip / n_all), 15, "#1e3a8a"), ("手順: ① 周りの 4 画素と輝度の差を調べる → ② 差が大きければ縁 → ③ 縁なら、周りの色と混ぜる(差が大きいほど、多く)", 13, TEXT), ("1 回の後処理で済み、とても軽い。ただし、細かい模様まで、ぼかしてしまうことがある", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ジャギーは、輝度の差が大きい所(縁)にだけ出る"), (t0, t0 + 7.5, "画面をなぞって、縁の画素に印を付ける"), (t0 + 7.5, t_e, "縁の画素だけを、周りの画素と混ぜる"), (t_e, 99, "縁以外は、触らないので軽い")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "FXAA", "縁の画素 %d / %d(しきい値 %.2f)" % (n_edge, n_all, TH))
    return Build(st, name, "graphics/postprocess/antialiasing/fxaa.md", BEFORE, [1.5, 3.5, 6.0, 9.0, 12.0, 17.0])


# ===================================================================== MSAA
def MsaaSamples():
    name = "msaa-samples"
    st = Stage(name, "MSAA: 縁の判定(カバレッジ)だけ 4 倍に増やし、色の計算は、画素に 1 回で済ませる", duration=20.0, subtitle="三角形の縁。1 画素に 4 つのサンプル点。何個が三角形の中かを数えて、その割合で色を混ぜる")
    sc, root = st.scene, st.root
    NX, NY, CS = 12, 8, 24.0
    BG, FG = (0.96, 0.96, 0.96), (0.15, 0.45, 0.85)
    inside = lambda x, y: y > 0.62 * x + 0.9
    offs = [(0.125, 0.625), (0.375, 0.125), (0.625, 0.875), (0.875, 0.375)]
    mix = lambda a: [FG[k] * a + BG[k] * (1 - a) for k in range(3)]
    none, msaa, ssaa, cover = {}, {}, {}, {}
    for j in range(NY):
        for i in range(NX):
            c = sum(1 for dx, dy in offs if inside(i + dx, j + dy))
            cover[(i, j)] = c
            none[(i, j)] = mix(1.0 if inside(i + 0.5, j + 0.5) else 0.0)
            msaa[(i, j)] = mix(c / 4.0)
            m = 8
            ssaa[(i, j)] = mix(sum(1 for a in range(m) for b in range(m) if inside(i + (a + 0.5) / m, j + (b + 0.5) / m)) / (m * m))
    err = lambda d: sum(sum(abs(d[k][c] - ssaa[k][c]) for c in range(3)) / 3 for k in d) / len(d)
    e_n, e_m = err(none), err(msaa)
    assert e_m < e_n
    partial = sum(1 for v in cover.values() if 0 < v < 4)
    full = sum(1 for v in cover.values() if v == 4)
    touched = partial + full
    shade_msaa = touched                      # 色の計算は 1 画素 1 回(触れた画素だけ)
    shade_ssaa = touched * 4                  # 4 倍の解像度で描くと、色の計算も 4 倍
    assert shade_ssaa == 4 * shade_msaa
    px = [30, 335, 640]
    labs = [("① MSAA なし(中心で 1 回判定)", RED), ("② MSAA 4x(4 サンプルで判定)", BLUE), ("③ 正解(1 画素 64 サンプル)", GREEN)]
    data = [none, msaa, ssaa]
    t0, dts = 1.5, 0.2
    cv = lambda c: Hex([255 * v for v in c])
    for p, (lab, col) in enumerate(labs):
        st.Panel(px[p], 100, NX * CS * 0.9, NY * CS * 0.9, lab, color=col)
    CS2 = CS * 0.9
    for p in range(3):
        g = Grid(st, px[p], 100, NX, NY, CS2, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                g.Paint(i, j, t0 + i * dts * 0.5, cv(data[p][(i, j)]))
        g.Flush()
    # MSAA の例の 1 画素: 拡大
    ex = (4, 4)
    for ex in [(i, j) for (i, j), v in cover.items() if 0 < v < 4][:1]:
        pass
    ex = [(i, j) for (i, j), v in cover.items() if v == 2][0] if any(v == 2 for v in cover.values()) else [(i, j) for (i, j), v in cover.items() if 0 < v < 4][0]
    fr = root.add("rect", x=R(px[1] + ex[0] * CS2), y=R(100 + ex[1] * CS2), width=CS2, height=CS2, fill="none", stroke=RED, stroke_width=3, opacity=0)
    t_z = t0 + NX * dts * 0.5 + 0.8
    fr.Show(t_z)
    zx, zy, zs = 600, 330, 130.0
    gz = root.add("g", opacity=0)
    gz.Show(t_z)
    gz.add("rect", x=zx, y=zy, width=zs, height=zs, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    # 境目の線(この画素の中)
    pts = []
    for k in range(0, 11):
        xx = ex[0] + k / 10
        yy = 0.62 * xx + 0.9
        if ex[1] <= yy <= ex[1] + 1:
            pts.append((zx + (xx - ex[0]) * zs, zy + (yy - ex[1]) * zs))
    if len(pts) >= 2:
        gz.add("polygon", points=" ".join("%s,%s" % (R(a), R(b)) for a, b in pts + [(zx + zs, zy + zs), (zx, zy + zs)]) if False else "0,0", fill="none")
        gz.add("line", x1=R(pts[0][0]), y1=R(pts[0][1]), x2=R(pts[-1][0]), y2=R(pts[-1][1]), stroke=INK, stroke_width=3)
    for dx, dy in offs:
        ins = inside(ex[0] + dx, ex[1] + dy)
        gz.add("circle", cx=R(zx + dx * zs), cy=R(zy + dy * zs), r=9, fill=(BLUE if ins else "#cbd5e1"), stroke="#334155", stroke_width=2)
    sc.Text(gz, zx, zy - 10, "赤枠の画素を拡大: 4 サンプル", size=12, weight=700, fill=RED)
    c_in = cover[ex]
    sc.Text(gz, zx + zs + 12, zy + 30, "三角形の中: %d / 4 個" % c_in, size=14, weight=700, fill=BLUE)
    sc.Text(gz, zx + zs + 12, zy + 56, "色 = 三角形 %.2f + 背景 %.2f" % (c_in / 4, 1 - c_in / 4), size=12, weight=500, fill=TEXT)
    sc.Text(gz, zx + zs + 12, zy + 76, "(色の計算は 1 回)", size=12, weight=500, fill=MUTED)
    # 数字
    st.Text(40, 336, "色を計算した回数(画素シェーダー):", size=14, weight=700)
    ser1 = [(t0 + i * dts * 0.5, sum(1 for (ii, jj), v in cover.items() if ii <= i and v > 0)) for i in range(NX)]
    st.Text(40, 366, "MSAA 4x:", size=14, fill=BLUE)
    st.Counter(150, 369, ser1, size=24, fill=BLUE)
    ser2 = [(t, 4 * v) for t, v in ser1]
    st.Text(40, 400, "解像度を 4 倍にして描く(SSAA):", size=14, fill=RED)
    st.Counter(300, 403, ser2, size=24, fill=RED)
    t_e = t_z + 2.0
    st.Box(t_e, 30, 430, 560, 88, [("正解とのずれ: なし %.3f → MSAA %.3f" % (e_n, e_m), 15, "#1e3a8a"), ("色の計算 %d 回 vs SSAA %d 回(4 倍)。判定とメモリだけ 4 倍" % (shade_msaa, shade_ssaa), 14, "#166534"), ("内側の画素は、4 サンプルとも同じ → 色は 1 回で足りる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "縁の画素は、三角形に半分だけかかっている"), (t0, t_z, "4 つのサンプル点が、三角形の中か外かを、画素ごとに数える"), (t_z, t_e, "中の数の割合で、三角形の色と背景を混ぜる"), (t_e, 99, "色の計算は 1 画素 1 回のまま。解像度を上げるより、ずっと安い")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "MSAA", "縁の画素 %d 個(完全に内側 %d 個)" % (partial, full))
    st.Note(t_e, "MSAA", "色の計算: MSAA %d 回 / SSAA %d 回、ずれ %.3f → %.3f" % (shade_msaa, shade_ssaa, e_n, e_m))
    return Build(st, name, "graphics/postprocess/antialiasing/msaa.md", BEFORE, [1.5, 3.5, 6.0, 9.0, 12.0, 17.0])


NAMES = ["snell-refraction", "beer-thickness", "fxaa-edge", "msaa-samples"]
FIGS = [SnellRefraction, BeerThickness, FxaaEdge, MsaaSamples]
