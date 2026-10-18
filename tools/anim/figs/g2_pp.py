import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402

BEFORE = "## よくあるミス"


def Halton(i, b):
    f, r = 1.0, 0.0
    while i > 0:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def TaaJitter():
    name = "taa-jitter"
    st = Stage(name, "TAA: 毎フレーム、画素の中の別の場所を測り、履歴と平均して縁をなめらかにする", duration=17.0, subtitle="三角形の縁(斜めの線)を、12×8 画素で描く。1 フレームだけ vs 8 フレームぶん平均")
    sc, root = st.scene, st.root
    NX, NY, CS = 12, 8, 24.0
    BG, FG = "#f1f5f9", "#334155"
    inside = lambda x, y: y > 0.55 * x + 0.9 - 0.0
    N = 8

    def Truth(i, j, m=8):
        c = 0
        for a in range(m):
            for b in range(m):
                if inside(i + (a + 0.5) / m, j + (b + 0.5) / m):
                    c += 1
        return c / (m * m)

    truth = {(i, j): Truth(i, j) for j in range(NY) for i in range(NX)}
    jit = [(Halton(k + 1, 2) - 0.5, Halton(k + 1, 3) - 0.5) for k in range(N)]
    samples = {(i, j): [1.0 if inside(i + 0.5 + jx, j + 0.5 + jy) else 0.0 for (jx, jy) in jit] for j in range(NY) for i in range(NX)}
    alias = {(i, j): 1.0 if inside(i + 0.5, j + 0.5) else 0.0 for j in range(NY) for i in range(NX)}
    err_alias = sum(abs(alias[k] - truth[k]) for k in truth) / len(truth)
    err_taa = []
    for n in range(1, N + 1):
        e = sum(abs(sum(samples[k][:n]) / n - truth[k]) for k in truth) / len(truth)
        err_taa.append(e)
    assert err_taa[-1] < err_taa[0] and err_taa[-1] < err_alias

    px = [30, 345, 660]
    titles = [("1 フレームだけ(画素の中心で 1 回測る)", RED), ("TAA(ジッター + 履歴の平均)", BLUE), ("正解(1 画素あたり 64 回測る)", GREEN)]
    grids = []
    for p in range(3):
        st.Panel(px[p], 100, NX * CS, NY * CS, titles[p][0], color=titles[p][1])
        grids.append(Grid(st, px[p], 100, NX, NY, CS, base=BG))
    t0, dtf = 1.2, 1.7
    # 左(エイリアス)と右(正解): 最初から出す
    for (i, j) in truth:
        grids[0].Paint(i, j, 0.5, Mix(BG, FG, alias[(i, j)]))
        grids[2].Paint(i, j, t0 + N * dtf + 0.5, Mix(BG, FG, truth[(i, j)]))
        for n in range(1, N + 1):
            v = sum(samples[(i, j)][:n]) / n
            grids[1].Paint(i, j, t0 + (n - 1) * dtf + 0.4, Mix(BG, FG, v))
    for g in grids:
        g.Flush()
        g.Lines(color="#ffffff", opacity=0.35)
    # ジッターの位置
    st.Panel(30, 360, 150, 150, "このフレームで測る場所", color=PURPLE)
    root.add("rect", x=30, y=360, width=150, height=150, fill="#f8fafc", stroke=LINE, stroke_width=1.5, rx=6)
    root.add("line", x1=105, y1=360, x2=105, y2=510, stroke=LIGHT, stroke_width=1)
    root.add("line", x1=30, y1=435, x2=180, y2=435, stroke=LIGHT, stroke_width=1)
    for k, (jx, jy) in enumerate(jit):
        t = t0 + k * dtf
        d = root.add("circle", cx=R(105 + jx * 140), cy=R(435 + jy * 140), r=6, fill=PURPLE, opacity=0)
        d.Show(t, t + dtf if k < N - 1 else None)
        old = root.add("circle", cx=R(105 + jx * 140), cy=R(435 + jy * 140), r=3, fill="#c4b5fd", opacity=0)
        old.Set(t + dtf, "opacity", 1)
        sc.Text(root, R(105 + jx * 140) + 8, R(435 + jy * 140) - 6, str(k + 1), size=10, weight=700, fill=PURPLE, opacity=0).Show(t, t + dtf)
    # 誤差のグラフ
    st.Panel(210, 360, 340, 150, "正解とのずれ(小さいほど良い)", color=BLUE)
    ax0, ay0, aw, ah = 232, 380, 300, 110
    ymax = max(err_alias, err_taa[0]) * 1.15
    X = lambda n: ax0 + (n - 1) / (N - 1) * aw
    Y = lambda e: ay0 + ah - e / ymax * ah
    root.add("line", x1=ax0, y1=ay0 + ah, x2=ax0 + aw, y2=ay0 + ah, stroke=LINE, stroke_width=1.5)
    root.add("line", x1=R(ax0), y1=R(Y(err_alias)), x2=R(ax0 + aw), y2=R(Y(err_alias)), stroke=RED, stroke_width=2.5, stroke_dasharray="6 5")
    st.Text(ax0 + aw, Y(err_alias) - 6, "1 フレームだけ: %.3f" % err_alias, size=12, fill=RED, anchor="end")
    for n in range(1, N + 1):
        t = t0 + (n - 1) * dtf + 0.5
        d = root.add("circle", cx=R(X(n)), cy=R(Y(err_taa[n - 1])), r=5, fill=BLUE, opacity=0)
        d.Show(t)
        sc.Text(root, R(X(n)), R(Y(err_taa[n - 1])) - 10, "%.3f" % err_taa[n - 1], size=10, weight=700, fill=BLUE, anchor="middle", opacity=0).Show(t)
        sc.Text(root, R(X(n)), ay0 + ah + 14, str(n), size=11, weight=500, fill=MUTED, anchor="middle")
    st.Text(ax0 + aw, ay0 + ah + 26, "平均したフレーム数", size=11, weight=500, fill=MUTED, anchor="end")
    # カウンター
    st.Text(580, 372, "平均したフレーム数:", size=15)
    st.Counter(760, 374, [(t0 + k * dtf + 0.4, k + 1) for k in range(N)], size=22, fill=BLUE)
    t_end = t0 + N * dtf + 0.8
    st.Box(t_end, 580, 392, 350, 118, [("1 フレームだけ: ずれ %.3f(階段状)" % err_alias, 15, "#991b1b"), ("TAA %d フレーム: ずれ %.3f(%.0f%% 減)" % (N, err_taa[-1], 100 * (1 - err_taa[-1] / err_alias)), 15, "#1e3a8a"), ("1 フレームあたりの測定は、どちらも 1 回", 13, MUTED), ("(測る場所を毎回ずらしているだけ)", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 530, [(0.0, t0, "斜めの縁は、画素の中心で 1 回測ると、階段状(ジャギー)になる"), (t0, t0 + N * dtf, "毎フレーム、測る場所を少しずつずらして、履歴と平均する"), (t0 + N * dtf, t_end + 1, "右の「正解」は、1 画素を 64 回測った結果"), (t_end + 1, 99, "TAA は 1 フレームあたり 1 回の測定で、正解に近づく")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "TAA", "ジッター位置 %d 個を順に使う(Halton 2,3)" % N)
    st.Note(t_end, "TAA", "ずれ: 1 フレーム %.3f → TAA %d フレーム %.3f" % (err_alias, N, err_taa[-1]))
    return Build(st, name, "graphics/postprocess/antialiasing/index.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 16.0])


NAMES = ["taa-jitter"]
FIGS = [TaaJitter]


# ===================================================================== Bloom
def BloomStages():
    name = "bloom-stages"
    st = Stage(name, "ブルーム: 明るい所だけ取り出し、縮小してぼかし、元に足す", duration=22.0, subtitle="24×12 画素の HDR 画像で、実際に計算する。ぼかしは「縮小 → 拡大」で、安く作る")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 12, 11.5
    DARK, BRIGHT = "#0f172a", "#fff4b8"

    # --- HDR 画像 ---
    img = [[0.10 + 0.06 * (i / NX) for i in range(NX)] for j in range(NY)]
    def Disc(cx, cy, r, v):
        for j in range(NY):
            for i in range(NX):
                if (i + 0.5 - cx) ** 2 + (j + 0.5 - cy) ** 2 <= r * r:
                    img[j][i] = max(img[j][i], v)
    Disc(6.0, 5.0, 1.6, 6.0)
    Disc(16.5, 7.0, 1.0, 14.0)
    Disc(19.5, 3.0, 1.2, 3.0)
    for i in range(10, 14):
        img[9][i] = 1.6

    def Thr(v):
        return max(0.0, v - 1.0)

    def Down(a):
        h, w = len(a), len(a[0])
        H, W = (h + 1) // 2, (w + 1) // 2
        out = []
        for j in range(H):
            row = []
            for i in range(W):
                vals = [a[min(h - 1, 2 * j + dj)][min(w - 1, 2 * i + di)] for dj in (0, 1) for di in (0, 1)]
                row.append(sum(vals) / 4.0)
            out.append(row)
        return out

    def Up(a, H, W):
        h, w = len(a), len(a[0])
        out = []
        for j in range(H):
            row = []
            for i in range(W):
                fx, fy = (i + 0.5) * w / W - 0.5, (j + 0.5) * h / H - 0.5
                x0, y0 = int(math.floor(fx)), int(math.floor(fy))
                tx, ty = fx - x0, fy - y0
                g = lambda x, y: a[max(0, min(h - 1, y))][max(0, min(w - 1, x))]
                row.append(g(x0, y0) * (1 - tx) * (1 - ty) + g(x0 + 1, y0) * tx * (1 - ty) + g(x0, y0 + 1) * (1 - tx) * ty + g(x0 + 1, y0 + 1) * tx * ty)
            out.append(row)
        return out

    thr = [[Thr(v) for v in row] for row in img]
    l1 = Down(thr)
    l2 = Down(l1)
    l3 = Down(l2)
    levels = [l1, l2, l3]
    ups = [Up(l, NY, NX) for l in levels]
    bloom_parts = []
    acc = [[0.0] * NX for _ in range(NY)]
    for k in (2, 1, 0):
        acc = [[acc[j][i] + ups[k][j][i] for i in range(NX)] for j in range(NY)]
        bloom_parts.append([row[:] for row in acc])
    final = [[img[j][i] + 0.8 * bloom_parts[-1][j][i] for i in range(NX)] for j in range(NY)]

    def Disp(v):
        return Mix(DARK, BRIGHT, min(1.0, (v / (1.0 + v)) * 1.6))

    sizes = [(len(l[0]), len(l)) for l in levels]
    assert sizes == [(12, 6), (6, 3), (3, 2)]
    # --- 計算量 ---
    n_full = NX * NY
    chain_px = n_full + sum(w * h for w, h in sizes) + (sizes[2][0] * sizes[2][1] * 0) + sum(w * h for w, h in sizes[1::-1]) + n_full
    chain_taps = 4 * chain_px
    R_dir = 12
    direct_taps = n_full * 2 * (2 * R_dir + 1)
    assert direct_taps > chain_taps
    t0 = 1.0
    # パネル配置
    X1, X2, X3 = 30, 340, 650
    Y1, Y2 = 100, 300
    st.Panel(X1, Y1, NX * CS, NY * CS, "① 入力(HDR: 白より明るい光がある)", color=AMBER)
    g1 = Grid(st, X1, Y1, NX, NY, CS, base=DARK)
    for j in range(NY):
        for i in range(NX):
            g1.Paint(i, j, 0.3, Disp(img[j][i]))
    g1.Flush()
    # 値の数字(明るい所だけ)
    for (cx, cy, v) in [(6, 5, 6.0), (16, 7, 14.0), (19, 3, 3.0)]:
        sc.Text(root, X1 + cx * CS + CS / 2, Y1 + cy * CS + CS / 2 + 4, "%g" % v, size=10, weight=700, fill="#7c2d12", anchor="middle")
    st.Panel(X2, Y1, NX * CS, NY * CS, "② しきい値 1.0 を引く(明るい所だけ残す)", color=RED)
    g2 = Grid(st, X2, Y1, NX, NY, CS, base="#0b1220")
    for j in range(NY):
        for i in range(NX):
            g2.Paint(i, j, t0 + 2.0 + 0.04 * i, Disp(thr[j][i]))
    g2.Flush()
    ser = [(t0 + 2.0 + 0.04 * i, (i + 1) * NY) for i in range(NX)]
    st.Text(X2, 256, "判定した画素:", size=13)
    st.Counter(X2 + 100, 258, ser, size=18, fill=RED)
    # 縮小チェーン
    st.Panel(X3, Y1, NX * CS, NY * CS, "③ 縮小(2×2 を平均)を 3 回", color=PURPLE)
    cur_x = X3 + 8
    down_t = t0 + 5.0
    ser3 = []
    cnt = 0
    for k, l in enumerate(levels):
        w, h = len(l[0]), len(l)
        gk = Grid(st, cur_x, Y1 + 10, w, h, CS, base="#0b1220")
        for j in range(h):
            for i in range(w):
                gk.Paint(i, j, down_t + k * 1.8 + 0.1 * (i + j * w) / (w * h) * 4, Disp(l[j][i]))
        gk.Flush()
        sc.Text(root, cur_x, Y1 + 10 + h * CS + 16, "%d×%d" % (w, h), size=12, weight=700, fill=PURPLE)
        cnt += w * h
        ser3.append((down_t + k * 1.8, cnt))
        cur_x += w * CS + 10
    st.Text(X3, 256, "縮小で処理した画素:", size=13)
    st.Counter(X3 + 138, 258, ser3, size=18, fill=PURPLE)
    # 拡大して足す
    st.Panel(X1, Y2, NX * CS, NY * CS, "④ 小さい順に拡大して足す(ぼけた光)", color=BLUE)
    g4 = Grid(st, X1, Y2, NX, NY, CS, base="#0b1220")
    up_t = down_t + 3 * 1.8 + 0.8
    for k, part in enumerate(bloom_parts):
        for j in range(NY):
            for i in range(NX):
                g4.Paint(i, j, up_t + k * 1.7, Disp(part[j][i]))
    g4.Flush()
    st.Caption(X1, 452, [(0.0, 3.0, ""), (up_t, up_t + 1.7, "一番小さい 3×2 を拡大(とても広くぼける)"), (up_t + 1.7, up_t + 3.4, "6×3 を拡大して足す(中くらい)"), (up_t + 3.4, 99, "12×6 を拡大して足す(細かい光も残る)")], size=13, fill=BLUE, weight=500)
    # 合成
    st.Panel(X2, Y2, NX * CS, NY * CS, "⑤ 元の画像に足す(ブルーム × 0.8)", color=GREEN)
    g5 = Grid(st, X2, Y2, NX, NY, CS, base="#0b1220")
    fin_t = up_t + 3 * 1.7 + 0.6
    for j in range(NY):
        for i in range(NX):
            g5.Paint(i, j, fin_t + 0.04 * i, Disp(final[j][i]))
    g5.Flush()
    # 結果ボックス
    st.Box(fin_t + 1.4, X3, Y2 - 2, 276, 170, [("縮小 → 拡大のブルーム", 15, "#1e3a8a"), ("画素の処理 %d 回(約 %s 読み込み)" % (chain_px, Fmt(chain_taps)), 13, TEXT), ("同じ広がりを直接ぼかすと", 14, "#991b1b"), ("半径 %d で %s 読み込み" % (R_dir, Fmt(direct_taps)), 13, TEXT), ("→ 縮小チェーンは約 %.1f 倍 安い" % (direct_taps / chain_taps), 15, "#166534"), ("画面が大きいほど、差は広がる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 530, [(0.0, 3.0, "① 光源は、白(1.0)より明るい値を持っている"), (3.0, 6.0, "② しきい値より明るい分だけを取り出す"), (6.0, up_t, "③ 縮小を繰り返すと、少ない画素で広い範囲をぼかせる"), (up_t, fin_t, "④ 小さい画像から順に拡大して足すと、裾の広い光になる"), (fin_t, 99, "⑤ 元の画像に足して、光がにじんだ画像になる")], size=14, fill=MUTED, weight=500)
    st.Note(t0 + 2.0, "ブルーム", "しきい値で明るい分だけ残す(%d 画素を判定)" % n_full)
    st.Note(down_t, "ブルーム", "縮小 3 回: %s" % " → ".join("%d×%d" % s for s in sizes))
    st.Note(fin_t, "ブルーム", "合成。縮小チェーン %d 回 vs 直接ぼかし %s 読み込み" % (chain_px, Fmt(direct_taps)))
    return Build(st, name, "graphics/postprocess/bloom/index.md", BEFORE, [1.0, 4.0, 8.0, 11.0, 15.0, 21.0])


NAMES += ["bloom-stages"]
FIGS += [BloomStages]


# ===================================================================== DOF
def Avg(colors):
    from storyboard import Rgb, Hex
    rgb = [Rgb(c) for c in colors]
    return Hex([sum(c[k] for c in rgb) / len(rgb) for k in range(3)])


def DofFocusSweep():
    name = "dof-focus-sweep"
    st = Stage(name, "被写界深度: ピントの距離から外れるほど、ぼかす半径(錯乱円)が大きくなる", duration=20.0, subtitle="横 1 列の画像(48 画素)に、手前から奥まで 5 つの物体。ピントを 3 通りに動かして、実際にぼかす")
    sc, root = st.scene, st.root
    N = 48
    CW, X0 = 18.0, 48.0
    depths = [2.0, 4.0, 8.0, 16.0, 32.0]
    bounds = [0, 8, 16, 26, 36, 48]
    pal = [("#ef4444", "#fecaca"), ("#f59e0b", "#fde68a"), ("#22c55e", "#bbf7d0"), ("#3b82f6", "#bfdbfe"), ("#a855f7", "#e9d5ff")]
    src, dep = [], []
    for k in range(5):
        for i in range(bounds[k], bounds[k + 1]):
            src.append(pal[k][(i // 2) % 2])
            dep.append(depths[k])
    assert len(src) == N
    K = 6.0
    foci = [2.0, 8.0, 32.0]

    def Coc(d, f):
        return K * abs(1.0 / f - 1.0 / d) / (1.0 / 2.0 - 1.0 / 32.0)

    def Blur(f):
        out, rs = [], []
        for i in range(N):
            r = int(round(Coc(dep[i], f)))
            r = min(r, 6)
            idx = range(max(0, i - r), min(N, i + r + 1))
            out.append(Avg([src[j] for j in idx]))
            rs.append(r)
        return out, rs

    res = [Blur(f) for f in foci]
    taps = [sum(2 * r + 1 for r in rs) for _, rs in res]
    assert taps[0] > N and len(set(taps)) == 3
    t_ph = [1.0, 7.5, 14.0]
    ph = 6.0
    # 行 1: 元の画像
    st.Text(X0, 98, "元の画像(全部くっきり)", size=14, fill=TEXT)
    for i in range(N):
        root.add("rect", x=R(X0 + i * CW), y=104, width=CW + 0.3, height=36, fill=src[i])
    for k in range(5):
        xm = X0 + (bounds[k] + bounds[k + 1]) / 2 * CW
        sc.Text(root, xm, 160, "%g m" % depths[k], size=13, weight=700, fill=INK, anchor="middle")
    for b in bounds[1:-1]:
        root.add("line", x1=X0 + b * CW, y1=104, x2=X0 + b * CW, y2=168, stroke="#ffffff", stroke_width=2)
    # ピント面のマーカー
    mk = root.add("rect", x=R(X0 + bounds[0] * CW - 2), y=100, width=R((bounds[1] - bounds[0]) * CW + 4), height=44, fill="none", stroke=RED, stroke_width=4, opacity=1)
    for p in range(1, 3):
        k = depths.index(foci[p])
        mk.Set(t_ph[p], "x", R(X0 + bounds[k] * CW - 2))
        mk.Set(t_ph[p], "width", R((bounds[k + 1] - bounds[k]) * CW + 4))
    sc.Text(root, X0, 184, "▲ 赤枠 = ピントが合う距離", size=12, weight=700, fill=RED)
    # 行 2: 錯乱円(ぼかす半径)の棒
    st.Text(X0, 208, "ぼかす半径(画素)", size=14, fill=TEXT)
    base = 280.0
    for i in range(N):
        hs = [res[p][1][i] * 10.0 for p in range(3)]
        r = root.add("rect", x=R(X0 + i * CW + 2), y=R(base - hs[0]), width=CW - 4, height=R(hs[0]) if hs[0] else 0.01, fill="#f87171", opacity=0.9)
        r.Set(0, "height", max(hs[0], 0.01))
        for p in range(1, 3):
            r.Set(t_ph[p], "y", R(base - hs[p]))
            r.Set(t_ph[p], "height", max(hs[p], 0.01))
    root.add("line", x1=X0, y1=base, x2=X0 + N * CW, y2=base, stroke=LINE, stroke_width=1.5)
    # 行 3: ぼかし後
    st.Text(X0, 312, "ぼかした後の画像", size=14, fill=TEXT)
    cells = Grid(st, X0, 320, N, 1, CW, base="#e5e7eb")
    for p in range(3):
        for i in range(N):
            cells.Paint(i, 0, t_ph[p] + 0.04 * i + 0.5, res[p][0][i])
    cells.Flush()
    for g in range(1):
        pass
    # 文字
    labels = ["ピント: 手前(2 m)", "ピント: 中くらい(8 m)", "ピント: 奥(32 m)"]
    notes = ["手前がくっきり、奥ほどぼける", "真ん中がくっきり。手前も奥も、同じくらいぼける", "奥がくっきり、手前ほどぼける"]
    st.Caption(X0, 392, [(0.0, t_ph[0], "5 つの物体を、手前から奥へ並べる"), (t_ph[0], t_ph[1], labels[0]), (t_ph[1], t_ph[2], labels[1]), (t_ph[2], 99, labels[2])], size=18, fill=RED)
    st.Caption(X0, 418, [(t_ph[0], t_ph[1], notes[0]), (t_ph[1], t_ph[2], notes[1]), (t_ph[2], 99, notes[2])], size=14, fill=MUTED, weight=500)
    # カウンター
    st.Text(X0, 462, "この設定で、ぼかしに読む画素の数:", size=15)
    series = []
    for p in range(3):
        for i in range(N):
            series.append((t_ph[p] + 0.04 * i + 0.5, (sum(2 * res[p][1][j] + 1 for j in range(i + 1)) if True else 0)))
    ser = []
    for p in range(3):
        for i in range(N):
            ser.append((t_ph[p] + 0.04 * i + 0.5, sum(2 * res[p][1][j] + 1 for j in range(i + 1))))
    st.Counter(X0 + 230, 465, ser, size=22, fill=PURPLE)
    st.Box(t_ph[2] + 3.0, 560, 436, 370, 84, [("ピント手前 %d / 中 %d / 奥 %d 回読む" % tuple(taps), 15, "#4c1d95"), ("ぼける所が多いほど、読む画素が増える", 13, MUTED), ("(画素ごとに、半径が違うのが被写界深度の特徴)", 12, MUTED)], PURPLE, "#faf5ff")
    st.Note(t_ph[0], "DOF", "ピント 2 m: 読む画素 %d" % taps[0])
    st.Note(t_ph[1], "DOF", "ピント 8 m: 読む画素 %d" % taps[1])
    st.Note(t_ph[2], "DOF", "ピント 32 m: 読む画素 %d" % taps[2])
    return Build(st, name, "graphics/postprocess/dof/index.md", BEFORE, [1.0, 4.0, 8.5, 11.5, 15.0, 19.0])


NAMES += ["dof-focus-sweep"]
FIGS += [DofFocusSweep]


# ===================================================================== Motion blur
def MotionBlurShutter():
    name = "motion-blur-shutter"
    st = Stage(name, "モーション ブラー: シャッターが開いている間の位置を、全部足して平均する", duration=18.0, subtitle="1 フレームで 16 画素動く棒(幅 4 画素)を、シャッターの開き具合を変えて撮る。8 回に分けて足す")
    sc, root = st.scene, st.root
    N, CW, X0 = 48, 18.0, 48.0
    V, WID, S = 16.0, 4.0, 8
    x0 = 8.0
    angles = [(0.0, "シャッター 0°(一瞬)", GRAY), (90.0, "シャッター 90°", GREEN), (180.0, "シャッター 180°(映画の標準)", BLUE), (360.0, "シャッター 360°(開きっぱなし)", RED)]
    peaks = []
    stripes = []
    for a, _, _ in angles:
        span = V * a / 360.0
        pos = [x0 + (span * k / (S - 1) if a else 0.0) for k in range(S)]
        px = []
        for i in range(N):
            acc = 0.0
            for p in pos:
                ov = max(0.0, min(i + 1, p + WID) - max(i, p))
                acc += ov
            px.append(acc / (S * 1.0))
        peaks.append(max(px))
        stripes.append((pos, px))
    assert abs(peaks[0] - 1.0) < 1e-9 and peaks[3] < peaks[2] < peaks[1] < peaks[0]
    row_h = 78
    dt = 0.22
    rows_t = [1.0, 4.4, 8.0, 11.6]
    for r, (a, label, col) in enumerate(angles):
        y = 96 + r * row_h
        st.Text(X0, y - 4, label, size=14, fill=col)
        # 軌跡(ゴースト)
        pos, px = stripes[r]
        root.add("rect", x=X0, y=y + 4, width=N * CW, height=26, fill="#f8fafc", stroke="#e2e8f0", stroke_width=1)
        for k, p in enumerate(pos):
            t = rows_t[r] + k * dt
            g = root.add("rect", x=R(X0 + p * CW), y=y + 6, width=R(WID * CW), height=22, fill=col, opacity=0)
            g.Set(t, "opacity", 0.32 if a else 0.9)
            if a:
                sc.Text(root, R(X0 + (p + WID / 2) * CW), y + 22, str(k + 1), size=10, weight=700, fill="#ffffff", anchor="middle", opacity=0).Show(t)
        # 結果(足して平均)
        cells = Grid(st, X0, y + 36, N, 1, CW, base="#e5e7eb")
        tt = rows_t[r] + S * dt + 0.2
        for i in range(N):
            cells.Paint(i, 0, tt, Mix("#f8fafc", col if a else "#334155", min(1.0, px[i])))
        cells.Flush()
        sc.Text(root, X0 + N * CW + 6, y + 56, "", size=1)
        pk = sc.Text(root, 900, y + 25, "最大 %d%%" % round(100 * peaks[r]), size=14, weight=700, fill=col, anchor="end", opacity=0)
        pk.Show(tt)
    ser = []
    cnt = 0
    for r in range(1, 4):
        for k in range(S):
            cnt += 1
            ser.append((rows_t[r] + k * dt, cnt))
    st.Text(48, 428, "足した位置の数(合計):", size=15)
    st.Counter(250, 431, ser, size=22, fill=PURPLE)
    t_end = rows_t[3] + S * dt + 1.4
    st.Box(t_end, 560, 406, 370, 100, [("ブラーの長さ = 速さ × シャッターの開き", 15, "#1e3a8a"), ("0° → 90° → 180° → 360° で、長さ 0 / 4 / 8 / 16 画素", 13, TEXT), ("全体の明るさは変えずに、ぼかすので、ピークが下がる", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(48, 480, [(0.0, rows_t[0], "同じ動きを、シャッターの開き具合だけ変えて撮る"), (rows_t[0], rows_t[1], "シャッター 0°: 位置は 1 つ。くっきり止まって見える"), (rows_t[1], rows_t[2], "90°: 動く間の 8 つの位置を足す。少し尾を引く"), (rows_t[2], rows_t[3], "180°: 映画で一般的な長さ"), (rows_t[3], 99, "360°: 動く全区間が尾になる。薄く長くなる")], size=14, fill=MUTED, weight=500)
    st.Note(rows_t[0], "MB", "シャッター 0°: ブラーなし、最大 100%")
    for r in range(1, 4):
        st.Note(rows_t[r], "MB", "%s: 8 回足す、最大 %d%%" % (angles[r][1], round(100 * peaks[r])))
    return Build(st, name, "graphics/postprocess/motion-blur/index.md", BEFORE, [1.5, 5.0, 9.0, 12.5, 15.0, 17.0])


NAMES += ["motion-blur-shutter"]
FIGS += [MotionBlurShutter]
