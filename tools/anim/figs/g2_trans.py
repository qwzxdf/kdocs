import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def C(rgb):
    return Hex([255 * v for v in rgb])


def Over(dst, src, a):
    return [src[k] * a + dst[k] * (1 - a) for k in range(3)]


# ===================================================================== WBOIT
def WboitLayers():
    name = "wboit-layers"
    st = Stage(name, "WBOIT: 並べ替えずに、重みを付けて 1 回で混ぜる(半透明 3 枚)", duration=18.0, subtitle="1 列 28 画素に、赤・緑・青の半透明を重ねる。正解は「奥から順に混ぜた」結果")
    sc, root = st.scene, st.root
    N, CW, X0 = 28, 25.0, 60.0
    BG = (0.95, 0.95, 0.95)
    quads = [("赤", (1.0, 0.25, 0.25), 0.5, 3.0, 2, 17), ("緑", (0.2, 0.8, 0.3), 0.6, 6.0, 8, 23), ("青", (0.2, 0.4, 1.0), 0.5, 12.0, 12, 27)]
    correct, wrong, wb, accs, revs = [], [], [], [], []
    for i in range(N):
        cov = [q for q in quads if q[4] <= i < q[5]]
        col = list(BG)
        for q in sorted(cov, key=lambda q: -q[3]):
            col = Over(col, q[1], q[2])
        correct.append(col)
        col = list(BG)
        for q in cov:
            col = Over(col, q[1], q[2])
        wrong.append(col)
        acc = [0.0, 0.0, 0.0, 0.0]
        rev = 1.0
        for q in cov:
            z = q[3]
            w = max(0.01, min(3000.0, 10.0 / (1e-5 + (z / 5.0) ** 2 + (z / 200.0) ** 6)))
            for k in range(3):
                acc[k] += q[1][k] * q[2] * w
            acc[3] += q[2] * w
            rev *= 1 - q[2]
        avg = [acc[k] / max(acc[3], 1e-5) for k in range(3)]
        wb.append([avg[k] * (1 - rev) + BG[k] * rev for k in range(3)])
        accs.append(acc[3])
        revs.append(rev)
    err = lambda a: sum(sum(abs(a[i][k] - correct[i][k]) for k in range(3)) / 3 for i in range(N)) / N
    e_wrong, e_wb = err(wrong), err(wb)
    assert e_wb < e_wrong, (e_wrong, e_wb)
    st.Text(X0, 98, "半透明の 3 枚(深度 3 / 6 / 12)", size=13, fill=MUTED)
    for k, (nm, col, a, z, x0, x1) in enumerate(quads):
        y = 106 + k * 26
        g = root.add("g", opacity=0)
        g.Show(1.0 + k * 1.2)
        g.add("rect", x=R(X0 + x0 * CW), y=y, width=R((x1 - x0) * CW), height=22, fill=C(col), fill_opacity=a)
        sc.Text(g, R(X0 + x0 * CW + 6), y + 16, "%s α=%.1f 深度 %g" % (nm, a, z), size=12, weight=700, fill="#1f2937")
    rows = [("正解(奥から順に混ぜる = 並べ替えが必要)", correct, GREEN, 206), ("描いた順に混ぜる(並べ替えなし)", wrong, RED, 262), ("WBOIT(重み付き平均・並べ替えなし)", wb, BLUE, 318)]
    t0, dts = 5.0, 0.12
    gap = N * dts + 0.8
    for r, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 5, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(N):
            g.Paint(i, 0, t0 + r * gap + i * dts, C(vals[i]))
        g.Flush()
    t1 = t0 + 3 * gap
    st.Text(X0, 380, "WBOIT が 1 回の描画で貯める 2 つの値", size=13, fill=MUTED)
    gA = Grid(st, X0, 388, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    gB = Grid(st, X0, 414, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    amax = max(accs)
    for i in range(N):
        gA.Paint(i, 0, t0 + 2 * gap + i * dts, Mix("#f1f5f9", "#7c3aed", accs[i] / amax))
        gB.Paint(i, 0, t0 + 2 * gap + i * dts, Mix("#f1f5f9", "#0ea5e9", 1 - revs[i]))
    gA.Flush()
    gB.Flush()
    sc.Text(root, X0 + N * CW + 8, 403, "合計(α×重み)", size=11, weight=500, fill="#7c3aed")
    sc.Text(root, X0 + N * CW + 8, 429, "1 − 透過率", size=11, weight=500, fill="#0ea5e9")
    st.Box(t1, 60, 450, 840, 62, [("正解とのずれ(平均): 描いた順 %.3f / WBOIT %.3f" % (e_wrong, e_wb), 15, "#1e3a8a"), ("WBOIT は、手前ほど重みを大きくして平均する。並べ替えなしの 1 パスで、順序を近似する", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.0, "半透明は、混ぜる順番で色が変わる"), (1.0, t0, "3 枚が重なる(描いた順 = 手前から)"), (t0, t0 + gap, "正解: 奥から順に混ぜる。事前の並べ替えが必要"), (t0 + gap, t0 + 2 * gap, "描いた順にそのまま混ぜると、順序が逆なので色が違う"), (t0 + 2 * gap, t1, "WBOIT: 重み付き平均と、透過率の積を貯めて、最後に合成"), (t1, 99, "完全には一致しないが、並べ替えなしで、かなり近い")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "OIT", "正解、描いた順、WBOIT の 3 通りを塗る(28 画素)")
    st.Note(t1, "OIT", "ずれ: 描いた順 %.3f / WBOIT %.3f" % (e_wrong, e_wb))
    return Build(st, name, "graphics/translucency/oit/wboit.md", BEFORE, [2.0, 6.0, 10.0, 14.0, 17.0, 17.9])


# ===================================================================== A2C
def A2cCoverage():
    name = "a2c-coverage"
    st = Stage(name, "Alpha To Coverage: アルファを、MSAA サブサンプルの「覆う数」に変える", duration=16.0, subtitle="葉っぱの縁のようなアルファ(左 0 → 右 1)を、1 列 24 画素で描く。1 画素は 4 サンプル")
    sc, root = st.scene, st.root
    N, CW, X0 = 24, 33.0, 60.0
    alpha = lambda x: max(0.0, min(1.0, (x - 6.0) / 12.0))
    FG, BGc = (0.15, 0.55, 0.20), (0.95, 0.95, 0.95)
    mix = lambda a: [FG[k] * a + BGc[k] * (1 - a) for k in range(3)]
    offs = [0.125, 0.375, 0.625, 0.875]
    thr = [0.375, 0.875, 0.125, 0.625]
    truth, test, a2c = [], [], []
    for i in range(N):
        a = alpha(i + 0.5)
        truth.append(mix(a))
        test.append(mix(1.0 if a >= 0.5 else 0.0))
        n = sum(1 for o, t in zip(offs, thr) if alpha(i + o) > t)
        a2c.append(mix(n / 4.0))
    err = lambda v: sum(sum(abs(v[i][k] - truth[i][k]) for k in range(3)) / 3 for i in range(N)) / N
    e_t, e_a = err(test), err(a2c)
    levels_t = len({round(c[0], 3) for c in test})
    levels_a = len({round(c[0], 3) for c in a2c})
    assert e_a < e_t and levels_t == 2 and levels_a >= 4
    rows = [("正解(アルファをそのまま使う)", truth, GREEN, 120), ("アルファ テスト(0.5 で切る: 1 サンプル)", test, RED, 196), ("Alpha To Coverage(4 サンプルの数に変換)", a2c, BLUE, 272)]
    st.Text(X0, 100, "アルファの値(白 = 0、黒 = 1)", size=13, fill=MUTED)
    ag = Grid(st, X0, 104, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    t0, dts = 1.0, 0.18
    for i in range(N):
        ag.Paint(i, 0, 0.3, Gray(1 - alpha(i + 0.5)))
    ag.Flush()
    for r, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 2, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y + 4, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(N):
            g.Paint(i, 0, t0 + i * dts, C(vals[i]))
        g.Flush()
    pick = 11
    ts = t0 + N * dts + 0.4
    st.Panel(60, 346, 380, 150, "画素 %d の中を拡大(4 サンプル)" % (pick + 1), color=PURPLE)
    g = root.add("g", opacity=0)
    g.Show(ts)
    for s_, (o, t) in enumerate(zip(offs, thr)):
        a = alpha(pick + o)
        on = a > t
        x = 80 + s_ * 85
        g.add("rect", x=x, y=372, width=75, height=60, fill=(C(FG) if on else C(BGc)), stroke="#94a3b8", stroke_width=1.5)
        sc.Text(g, x + 37, 452, "α=%.2f" % a, size=11, weight=700, fill=TEXT, anchor="middle")
        sc.Text(g, x + 37, 468, "しきい値 %.2f" % t, size=10, weight=500, fill=MUTED, anchor="middle")
        sc.Text(g, x + 37, 408, "覆う" if on else "覆わない", size=12, weight=700, fill=("#ffffff" if on else MUTED), anchor="middle")
    n_pick = sum(1 for o, t in zip(offs, thr) if alpha(pick + o) > t)
    sc.Text(g, 80, 488, "覆うサンプルが %d / 4 個 → 画素の濃さ %.2f" % (n_pick, n_pick / 4), size=14, weight=700, fill=PURPLE)
    st.Text(480, 372, "表せる濃さの段階:", size=15)
    sc.Text(root, 480, 396, "アルファ テスト: %d 段階(0 か 1)" % levels_t, size=15, fill=RED, opacity=0).Show(ts)
    sc.Text(root, 480, 420, "A2C: %d 段階(0, 1/4, 2/4, 3/4, 1)" % levels_a, size=15, fill=BLUE, opacity=0).Show(ts)
    t_end = ts + 1.0
    st.Box(t_end, 480, 440, 450, 70, [("正解とのずれ: アルファ テスト %.3f / A2C %.3f" % (e_t, e_a), 15, "#1e3a8a"), ("MSAA を使っているときだけ有効。サンプル数が多いほど滑らか", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "葉っぱの縁のアルファは、なめらかに 0 から 1 へ変わる"), (t0, ts, "アルファ テスト: 0.5 で切るので、縁が階段状になる(ジャギー)"), (ts, t_end, "A2C: アルファの大きさを「覆うサンプルの数」に変える"), (t_end, 99, "同じ画素でも、サンプルごとに覆う / 覆わないが違い、5 段階の濃さになる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "A2C", "3 通りで 24 画素を塗る")
    st.Note(t_end, "A2C", "ずれ: アルファ テスト %.3f / A2C %.3f" % (e_t, e_a))
    return Build(st, name, "graphics/translucency/alpha-test/alpha-to-coverage.md", BEFORE, [1.5, 3.5, 6.0, 8.5, 12.0, 15.0])


# ===================================================================== Hashed alpha
def HashedAlpha():
    name = "hashed-alpha-sweep"
    st = Stage(name, "ハッシュ アルファ: 画素ごとのでたらめなしきい値で切り、重ねるとなめらかになる", duration=18.0, subtitle="アルファが左 0.1 → 右 0.9 の板。1 フレームだけだとザラザラ、8 フレーム平均で本来の濃さに近づく")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 8, 17.0
    FG, BGc = "#0f766e", "#f8fafc"

    def Hash(x, y, f):
        v = (x * 73856093) ^ (y * 19349663) ^ (f * 83492791)
        v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
        v ^= v >> 16
        return (v & 0xFFFF) / 65536.0

    alpha = lambda x: 0.1 + 0.8 * x / (NX - 1)
    F = 8
    onf = [[[1.0 if alpha(x) > Hash(x, y, f) else 0.0 for x in range(NX)] for y in range(NY)] for f in range(F)]
    avg = lambda n: [[sum(onf[f][y][x] for f in range(n)) / n for x in range(NX)] for y in range(NY)]
    errf = lambda g: sum(abs(g[y][x] - alpha(x)) for y in range(NY) for x in range(NX)) / (NX * NY)
    e1 = errf(onf[0])
    eavg = [errf(avg(n)) for n in range(1, F + 1)]
    assert eavg[-1] < e1 / 1.8, (e1, eavg)
    X1, X2 = 30, 495
    st.Panel(X1, 100, NX * CS, NY * CS, "1 フレームだけ(0 か 1 のザラザラ)", color=RED)
    gl = Grid(st, X1, 100, NX, NY, CS, base=BGc)
    for y in range(NY):
        for x in range(NX):
            gl.Paint(x, y, 0.5, Mix(BGc, FG, onf[0][y][x]))
    gl.Flush()
    st.Panel(X2, 100, NX * CS, NY * CS, "フレームを重ねた平均", color=BLUE)
    gr = Grid(st, X2, 100, NX, NY, CS, base=BGc)
    t0, dt = 1.5, 1.7
    for n in range(1, F + 1):
        a = avg(n)
        for y in range(NY):
            for x in range(NX):
                gr.Paint(x, y, t0 + (n - 1) * dt, Mix(BGc, FG, a[y][x]))
    gr.Flush()
    sc.Text(root, X1, 262, "正解(アルファ通り)", size=13, weight=700, fill=GREEN)
    gt = Grid(st, X1, 268, NX, 1, CS, base=BGc, stroke="#94a3b8")
    for x in range(NX):
        gt.Paint(x, 0, 0.5, Mix(BGc, FG, alpha(x)))
    gt.Flush()
    st.Text(X1, 316, "平均したフレーム数:", size=15)
    st.Counter(X1 + 175, 318, [(t0 + n * dt, n + 1) for n in range(F)], size=22, fill=BLUE)
    ax0, ay0, aw, ah = X2 + 10, 300, 360, 90
    st.Panel(X2, 290, NX * CS, 110, "正解とのずれ(小さいほど良い)", color=PURPLE)
    ymax = max(e1, eavg[0]) * 1.1
    X = lambda n: ax0 + 6 + (n - 1) / (F - 1) * (aw - 24)
    Y = lambda e: ay0 + ah - 12 - e / ymax * (ah - 24)
    root.add("line", x1=R(ax0), y1=R(Y(e1)), x2=R(ax0 + aw), y2=R(Y(e1)), stroke=RED, stroke_width=2, stroke_dasharray="6 5")
    sc.Text(root, ax0 + aw, Y(e1) - 5, "1 フレーム %.3f" % e1, size=11, weight=700, fill=RED, anchor="end")
    for n in range(1, F + 1):
        tt = t0 + (n - 1) * dt
        d = root.add("circle", cx=R(X(n)), cy=R(Y(eavg[n - 1])), r=4.5, fill=BLUE, opacity=0)
        d.Show(tt)
        sc.Text(root, R(X(n)), R(Y(eavg[n - 1])) - 8, "%.3f" % eavg[n - 1], size=9, weight=700, fill=BLUE, anchor="middle", opacity=0).Show(tt)
    t_end = t0 + F * dt + 0.6
    st.Box(t_end, 30, 420, 900, 86, [("1 フレーム: ずれ %.3f → %d フレーム平均: ずれ %.3f" % (e1, F, eavg[-1]), 16, "#1e3a8a"), ("画素ごとのしきい値を毎フレーム変えるので、「画素ごとに違う運」が平均されて、アルファに近づく", 13, MUTED), ("(TAA と組み合わせて使う。しきい値を毎フレーム変えないと、ずっとザラザラのまま)", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "アルファが しきい値より大きい画素だけを描く(しきい値は画素ごとにでたらめ)"), (t0, t_end, "毎フレームしきい値を変えて、重ねる"), (t_end, 99, "並べ替えも、特別な描画もいらないが、ノイズと引き換え")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ハッシュ", "フレーム 1〜%d を平均" % F)
    return Build(st, name, "graphics/translucency/alpha-test/hashed-alpha.md", BEFORE, [1.5, 4.0, 8.0, 12.0, 15.0, 17.5])


# ===================================================================== Depth peeling
def DepthPeeling():
    name = "depth-peeling-passes"
    st = Stage(name, "デプス ピーリング: 手前の層から 1 枚ずつ「皮をむく」ように取り出して、正しく混ぜる", duration=19.0, subtitle="1 列 24 画素に、3 枚の半透明を重ねる。毎回の描画(パス)で、まだ取っていない一番手前の層を取る")
    sc, root = st.scene, st.root
    N, CW, X0 = 24, 33.0, 60.0
    BG = (0.95, 0.95, 0.95)
    quads = [("A", (0.95, 0.3, 0.3), 0.5, 5.0, 2, 14), ("B", (0.2, 0.75, 0.3), 0.6, 3.0, 8, 20), ("C", (0.25, 0.45, 1.0), 0.5, 7.0, 0, 22)]
    layers = [sorted([q for q in quads if q[4] <= i < q[5]], key=lambda q: q[3]) for i in range(N)]
    P = max(len(c) for c in layers)
    assert P == 3
    peeled = [[(layers[i][p] if p < len(layers[i]) else None) for i in range(N)] for p in range(P)]
    final, correct = [], []
    for i in range(N):
        col = list(BG)
        for p in range(P - 1, -1, -1):
            q = peeled[p][i]
            if q is not None:
                col = Over(col, q[1], q[2])
        final.append(col)
        col = list(BG)
        for q in sorted([q for q in quads if q[4] <= i < q[5]], key=lambda q: -q[3]):
            col = Over(col, q[1], q[2])
        correct.append(col)
    assert max(abs(final[i][k] - correct[i][k]) for i in range(N) for k in range(3)) < 1e-9
    nfrag = sum(len(l) for l in layers)
    st.Text(X0, 96, "半透明の 3 枚(深度: 小さいほど手前)", size=13, fill=MUTED)
    for k, (nm, col, a, z, x0, x1) in enumerate(quads):
        y = 102 + k * 22
        root.add("rect", x=R(X0 + x0 * CW), y=y, width=R((x1 - x0) * CW), height=18, fill=C(col), fill_opacity=a)
        sc.Text(root, R(X0 + x0 * CW + 6), y + 14, "%s 深度 %g" % (nm, z), size=11, weight=700, fill=TEXT)
    t0, per = 1.5, 4.0
    ser = []
    cnt = 0
    for p in range(P):
        y = 190 + p * 62
        sc.Text(root, X0, y - 3, "パス %d: %d 番目に手前の層を取る" % (p + 1, p + 1), size=13, weight=700, fill=PURPLE)
        g = Grid(st, X0, y, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(N):
            q = peeled[p][i]
            g.Paint(i, 0, t0 + p * per + i * 0.1, C(Over(BG, q[1], q[2])) if q else "#e5e7eb")
        g.Flush()
        cnt += nfrag
        ser.append((t0 + p * per, cnt))
    st.Text(X0, 392, "描いた断片の数(各パスで全部描き直す):", size=14)
    st.Counter(X0 + 330, 394, ser, size=22, fill=RED)
    t_c = t0 + P * per
    st.Text(X0, 422, "奥のパスから手前へ混ぜた結果", size=13, weight=700, fill=GREEN)
    gf = Grid(st, X0, 428, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        gf.Paint(i, 0, t_c + i * 0.06, C(final[i]))
    gf.Flush()
    t_end = t_c + N * 0.06 + 0.8
    st.Box(t_end, 60, 462, 840, 56, [("結果は、奥から順に混ぜた正解と完全に一致(ずれ 0)", 15, "#166534"), ("代わりに、層の数 %d 回、シーンを描き直す(断片 %d 個 → 合計 %d 個)" % (P, nfrag, P * nfrag), 14, "#991b1b")], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "画素ごとに、手前から何枚重なっているかは、描くまで分からない"), (t0, t0 + P * per, "毎回、前のパスで取った層より奥で、一番手前の層だけを残す"), (t0 + P * per, t_end, "取れた層を、奥から手前へ混ぜる"), (t_end, 99, "正確だが、層の数だけ描き直す(高コスト)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ピーリング", "%d パス。各パスで断片を全部描き直す(合計 %d)" % (P, P * nfrag))
    return Build(st, name, "graphics/translucency/oit/depth-peeling.md", BEFORE, [2.0, 5.5, 9.5, 13.0, 16.0, 18.5])


NAMES = ["wboit-layers", "a2c-coverage", "hashed-alpha-sweep", "depth-peeling-passes"]
FIGS = [WboitLayers, A2cCoverage, HashedAlpha, DepthPeeling]
