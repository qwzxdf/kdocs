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


def Rgbh(c):
    return Hex([255 * max(0.0, min(1.0, v)) for v in c])


# ===================================================================== CoC graph
def CocGraph():
    name = "coc-graph"
    st = Stage(name, "錯乱円(CoC): ピントの距離からのずれで、ぼける半径が決まる。手前は急に、奥はゆるやかに大きくなる", duration=21.0, subtitle="レンズの式から計算。ピントを 2 m → 5 m → 20 m に動かして、各距離の CoC(画素)を見る")
    sc, root = st.scene, st.root
    f, N = 0.05, 2.8
    sensor = 0.036
    W = 1920.0

    def Coc(d, S):
        c = (f * f / (N * (S - f))) * abs(d - S) / d          # センサー上の直径(m)
        return c / sensor * W / 2                             # 画素の半径

    ds = [1.0 * (60.0 / 1.0) ** (k / 100) for k in range(101)]
    focus = [2.0, 5.0, 20.0]
    curves = [[min(Coc(d, S), 14) for d in ds] for S in focus]
    near_far = []
    for S in focus:
        n1, n2 = Coc(S / 1.5, S), Coc(S * 1.5, S)
        near_far.append((n1, n2))
        assert n1 > n2
    X0, W_ = 70.0, 820.0
    XX = lambda d: X0 + (math.log(d) - 0.0) / math.log(60.0) * W_
    YY = lambda v: 330 - v / 14 * 200
    st.Panel(30, 96, 900, 270, "① 距離ごとのぼける半径(画素)", color=BLUE)
    for d in (1, 2, 5, 10, 20, 60):
        sc.Text(root, XX(d), 352, "%g m" % d, size=11, weight=500, fill=MUTED, anchor="middle")
        root.add("line", x1=R(XX(d)), y1=120, x2=R(XX(d)), y2=334, stroke=LIGHT, stroke_width=1.2)
    cols = [RED, GREEN, BLUE]
    cur = root.add("path", d=Poly([(XX(d), YY(v)) for d, v in zip(ds, curves[0])]), fill="none", stroke=RED, stroke_width=4)
    t0, per = 1.5, 5.8
    cur.Steps("d", [(t0 + m * per, Poly([(XX(d), YY(v)) for d, v in zip(ds, curves[m])])) for m in range(3)])
    for m, S in enumerate(focus):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        g.add("line", x1=R(XX(S)), y1=120, x2=R(XX(S)), y2=334, stroke=cols[m], stroke_width=2, stroke_dasharray="5 4")
        sc.Text(g, XX(S) + 6, 136, "ピント %g m" % S, size=14, weight=700, fill=cols[m])
        sc.Text(g, 90, 140 if S > 3 else 160, "", size=1)
        sc.Text(g, 90, 396, "ピント %g m: 手前(%.1f m)で %.1f 画素、奥(%.1f m)で %.1f 画素" % (S, S / 1.5, near_far[m][0], S * 1.5, near_far[m][1]), size=15, weight=700, fill=cols[m])
    st.Text(40, 432, "同じ距離の比(÷1.5 と ×1.5)でも、手前のほうが、ずっとぼける", size=14, weight=700, fill=TEXT)
    ser = [(t0 + m * per + 0.3, int(round(near_far[m][0]))) for m in range(3)]
    st.Text(40, 470, "手前側のぼけ(画素):", size=14)
    st.Counter(200, 474, ser, size=24, fill=RED)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.5, 480, 446, 450, 70, [("ピントが近いほど、全体が大きくぼける", 14, "#1e3a8a"), ("ピント 2 m で手前 %.1f 画素 / ピント 20 m で %.1f 画素" % (near_far[0][0], near_far[2][0]), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ピントの合う距離は、ぼけが 0 になる"), (t0, t_e, "離れるほど、ぼけが増える。手前は急、奥は頭打ち"), (t_e, 99, "ポストプロセスは、この CoC を、深度から画素ごとに計算して使う")], size=14, fill=MUTED, weight=500)
    for m, S in enumerate(focus):
        st.Note(t0 + m * per, "CoC", "ピント %g m: 手前 %.1f 画素、奥 %.1f 画素" % (S, near_far[m][0], near_far[m][1]))
    return Build(st, name, "graphics/postprocess/dof/coc.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== gather weight
def DofGatherWeight():
    name = "dof-gather-weight"
    st = Stage(name, "ギャザーの重み: ピントが合っている画素の色を、ぼけた画素に混ぜない(にじみを防ぐ)", duration=21.0, subtitle="左 24 画素は、ピントの合った赤い物(CoC 0)。右は、ぼけた青い背景(CoC 4)。境目のぼけた側の画素は、周りを集めてぼかす")
    sc, root = st.scene, st.root
    n = 48
    col = [(0.9, 0.2, 0.2) if i < 24 else (0.2, 0.4, 0.95) for i in range(n)]
    coc = [0 if i < 24 else 4 for i in range(n)]
    def Naive(i):
        r = coc[i]
        idx = range(max(0, i - r), min(n, i + r + 1))
        return tuple(sum(col[j][k] for j in idx) / len(idx) for k in range(3))
    def Weighted(i):
        r = coc[i]
        idx = [j for j in range(max(0, i - r), min(n, i + r + 1)) if coc[j] >= abs(j - i) or coc[j] >= r * 0.5]
        if not idx:
            idx = [i]
        return tuple(sum(col[j][k] for j in idx) / len(idx) for k in range(3))
    naive = [Naive(i) if coc[i] else col[i] for i in range(n)]
    wei = [Weighted(i) if coc[i] else col[i] for i in range(n)]
    red_leak = lambda a: sum(max(0.0, a[i][0] - 0.2) for i in range(24, 32))
    l_n, l_w = red_leak(naive), red_leak(wei)
    assert l_w < l_n / 2
    CW, X0 = 18.0, 60.0
    rows = [("入力(CoC を数字で示す: 0 = ピントが合っている)", col, GRAY, 112), ("そのまま集める(境目で、赤がにじむ)", naive, RED, 190), ("重みを付けて集める(ピントの合った画素は混ぜない)", wei, GREEN, 268)]
    t0, per = 1.5, 5.0
    for r_, (lab, vals, c, y) in enumerate(rows):
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=c)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(n):
            g.Paint(i, 0, 0.3 if r_ == 0 else t0 + (r_ - 1) * per + i * 0.05, Rgbh(vals[i]))
        g.Flush()
    for i in (0, 12, 24, 36, 47):
        sc.Text(root, X0 + (i + 0.5) * CW, 148, "CoC %d" % coc[i], size=9, weight=700, fill=MUTED, anchor="middle")
    ex = 25
    t_x = t0 + 2 * per + 0.3
    fr = root.add("rect", x=R(X0 + (ex - 4) * CW), y=186, width=R(9 * CW), height=26, fill="none", stroke=AMBER, stroke_width=3, opacity=0)
    fr.Show(t_x)
    r = coc[ex]
    idx = range(max(0, ex - r), min(n, ex + r + 1))
    n_red = sum(1 for j in idx if j < 24)
    n_w = len([j for j in range(max(0, ex - r), min(n, ex + r + 1)) if coc[j] >= abs(j - ex) or coc[j] >= r * 0.5 if j < 24])
    sc.Text(root, X0, 340, "画素 %d(CoC %d)が集める 9 画素のうち、赤い(ピントの合った)画素は %d 個" % (ex + 1, r, n_red), size=14, weight=700, fill=TEXT, opacity=0).Show(t_x)
    sc.Text(root, X0, 366, "そのまま: 赤 %d / 9 が混ざる → 青い背景が赤みを帯びる。重みを付けると、赤 %d / 9" % (n_red, n_w), size=14, weight=700, fill=RED, opacity=0).Show(t_x)
    t_e = t_x + 1.5
    st.Box(t_e, 60, 400, 860, 90, [("赤のにじみ(境目から 8 画素の、赤成分の合計): そのまま %.2f → 重み付き %.2f" % (l_n, l_w), 15, "#1e3a8a"), ("集める画素に、その画素自身の CoC を見て、「自分のぼけがここまで届く」ときだけ、混ぜる", 13, TEXT), ("ピントの合った物の輪郭が、ぼけた背景に、にじまなくなる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ぼけた画素は、周りを集めて平均する"), (t0, t0 + per, "そのまま集めると、ピントの合った画素の色が、混ざってにじむ"), (t0 + per, t_e, "各画素の CoC を見て、重みを付けると、混ざらない"), (t_e, 99, "ピントの合った物の輪郭が、くっきり残る")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ギャザー", "赤のにじみ: そのまま %.2f / 重み付き %.2f" % (l_n, l_w))
    return Build(st, name, "graphics/postprocess/dof/gather.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== near field
def DofNearField():
    name = "dof-near-field"
    st = Stage(name, "手前のぼけ: 手前の物は、ぼけが、後ろのピントの合った所へ、はみ出す。後ろの画素のぼけ(0)だけでは足りない", duration=21.0, subtitle="1 列 48 画素。中央の手前の物(幅 8、CoC 5)が、ピントの合った背景に重なる。ぼけの広がりを、2 つの方法で比べる")
    sc, root = st.scene, st.root
    n = 48
    obj = (20, 28)
    col_obj, col_bg = (0.9, 0.25, 0.2), (0.85, 0.9, 0.95)
    img = [col_obj if obj[0] <= i < obj[1] else col_bg for i in range(n)]
    R_ = 5
    coc = [R_ if obj[0] <= i < obj[1] else 0 for i in range(n)]
    # 方法 A: 画素自身の CoC で集める(背景は CoC 0 → ぼけない)
    A = []
    for i in range(n):
        r = coc[i]
        idx = range(max(0, i - r), min(n, i + r + 1))
        A.append(tuple(sum(img[j][k] for j in idx) / len(idx) for k in range(3)))
    # 方法 B: 手前の物の CoC を、周りへ広げ(最大値を、半径 R_ で広げる)、そのぼけで集める
    cb = [max(coc[max(0, i - R_):min(n, i + R_ + 1)]) for i in range(n)]
    B = []
    for i in range(n):
        r = cb[i]
        idx = range(max(0, i - r), min(n, i + r + 1))
        B.append(tuple(sum(img[j][k] for j in idx) / len(idx) for k in range(3)))
    # 正解: 手前の物を、円盤(R_)でぼかした合成
    T = []
    for i in range(n):
        cov = sum(1 for j in range(i - R_, i + R_ + 1) if obj[0] <= j < obj[1]) / (2 * R_ + 1)
        T.append(tuple(col_obj[k] * cov + col_bg[k] * (1 - cov) for k in range(3)))
    err = lambda a: sum(abs(a[i][1] - T[i][1]) for i in range(n)) / n
    eA, eB = err(A), err(B)
    wid = lambda a: sum(1 for i in range(n) if abs(a[i][1] - col_bg[1]) > 0.04)
    wA, wB, wT = wid(A), wid(B), wid(T)
    assert eB < eA and wB > wA
    CW, X0 = 18.0, 60.0
    rows = [("入力", img, GRAY, 108), ("画素自身のぼけだけで集める", A, RED, 168), ("手前のぼけを、周りへ広げてから集める", B, GREEN, 228), ("正解(手前の物を円盤でぼかす)", T, BLUE, 288)]
    t0, per = 1.5, 4.2
    for r_, (lab, vals, c, y) in enumerate(rows):
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=c)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(n):
            g.Paint(i, 0, 0.3 if r_ in (0, 3) else t0 + (r_ - 1) * per + i * 0.05, Rgbh(vals[i]))
        g.Flush()
    st.Text(X0, 354, "手前の物の外へ、ぼけがはみ出した幅(画素):", size=14, weight=700)
    ser = [(t0 + 0 * per + 2.5, wA), (t0 + 1 * per + 2.5, wB)]
    st.Counter(430, 358, ser, size=26, fill=PURPLE)
    st.Text(480, 358, "(正解は %d)" % wT, size=13, weight=500, fill=MUTED)
    st.Panel(30, 392, 900, 90, "正解とのずれ(平均)", color=PURPLE)
    t_e = t0 + 2 * per + 0.5
    for k, (lab, e, c) in enumerate([("画素自身だけ", eA, RED), ("広げてから集める", eB, GREEN)]):
        sc.Text(root, 50 + k * 440, 434, lab, size=14, weight=700, fill=c, opacity=0).Show(t_e + k * 1.2)
        sc.Text(root, 50 + k * 440, 464, "%.3f" % e, size=22, weight=700, fill=c, opacity=0).Show(t_e + k * 1.2)
    st.Caption(30, 534, [(0.0, t0, "手前の物は、ぼけると、後ろの背景の上に、はみ出して見える"), (t0, t0 + per, "背景の画素は、自分のぼけが 0 なので、はみ出しが再現できない(輪郭がくっきり残る)"), (t0 + per, t_e, "手前の CoC を周りへ広げると、はみ出しが再現できる"), (t_e, 99, "はみ出しの幅が、正解に近づく")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "手前ぼけ", "はみ出し幅: 自身 %d / 広げる %d / 正解 %d" % (wA, wB, wT))
    return Build(st, name, "graphics/postprocess/dof/near-far.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 15.0, 20.0])


# ===================================================================== scatter vs gather
def DofScatterGather():
    name = "dof-scatter-gather"
    st = Stage(name, "スキャッター(広げる)とギャザー(集める): ぼけの半径が大きいほど、直接のスキャッターは高い。タップ数を固定したギャザーは、一定", duration=20.0, subtitle="1920×1080。ぼける半径(画素)ごとの、1 画素あたりの処理の回数を、数えて比べる")
    sc, root = st.scene, st.root
    rs = [2, 4, 8, 16, 32]
    px = 1920 * 1080
    scatter = [(2 * r + 1) ** 2 for r in rs]
    gather_full = scatter[:]
    gather_fix = [min(s, 49) for s in scatter]
    assert scatter[-1] > gather_fix[-1] * 20
    st.Panel(30, 96, 900, 280, "① 1 画素あたり、必要な処理の回数(対数目盛)", color=BLUE)
    X0 = 90.0
    LY = lambda v: 346 - (math.log10(v) / math.log10(5000)) * 220
    for v in (1, 10, 100, 1000):
        root.add("line", x1=70, y1=R(LY(v)), x2=900, y2=R(LY(v)), stroke=LIGHT, stroke_width=1.2)
        sc.Text(root, 66, R(LY(v)) + 4, str(v), size=10, weight=500, fill=MUTED, anchor="end")
    t0, per = 1.5, 3.0
    for k, r in enumerate(rs):
        x = X0 + k * 160
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per)
        for j, (v, c, lab) in enumerate([(scatter[k], RED, "広げる(円盤を全部書き込む)"), (gather_fix[k], GREEN, "集める(上限 49 タップ)")]):
            bx = x + j * 62
            g.add("rect", x=R(bx), y=R(LY(v)), width=54, height=R(346 - LY(v)), fill=c, opacity=0.88)
            sc.Text(g, bx + 27, R(LY(v)) - 5, str(v), size=12, weight=700, fill=c, anchor="middle")
        sc.Text(g, x + 58, 364, "半径 %d" % r, size=13, weight=700, fill=INK, anchor="middle")
    st.Legend(80, 124, [(RED, "広げる(円盤を全部書き込む)"), (GREEN, "集める(タップ数に上限 49)")])
    ser = [(t0 + k * per + 0.3, scatter[k] * px // 1000000) for k in range(5)]
    st.Text(40, 410, "画面全体の、広げる処理の書き込み(百万回):", size=14)
    st.Counter(430, 414, ser, size=26, fill=RED)
    t_e = t0 + 5 * per
    st.Box(t_e, 40, 436, 880, 80, [("半径 32 では、広げる %s 回 / 画素、集める(上限つき)%d 回 / 画素(約 %.0f 倍)" % (Fmt(scatter[-1]), gather_fix[-1], scatter[-1] / gather_fix[-1]), 15, "#1e3a8a"), ("集める方は、サンプルを減らすので、粗くなる(ノイズ・縞)。広げる方は、きれいだが重い", 13, TEXT), ("だから、ぼけの小さい所は、集める。明るい大きなぼけだけを、広げる、という組み合わせが多い", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ぼかし方は、広げる(スキャッター)と、集める(ギャザー)の 2 通り"), (t0, t_e, "ぼけが大きくなると、円盤の面積が、半径の 2 乗で増える"), (t_e, 99, "上限つきの集めは、一定のコスト。見た目とコストを、天秤にかける")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ぼかし", "半径 %s: 広げる %s / 集める %s" % ("/".join(map(str, rs)), "/".join(map(str, scatter)), "/".join(map(str, gather_fix))))
    return Build(st, name, "graphics/postprocess/dof/scatter.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 14.0, 19.0])


# ===================================================================== bokeh shapes
def BokehShapes():
    name = "bokeh-shapes-anim"
    st = Stage(name, "ボケの形: 絞りの羽根の枚数が、点の光のぼけの形になる", duration=20.0, subtitle="15×15 画素の点光源のぼけ。羽根 5・6・8 枚と、円(羽根が多い)を、実際に計算して並べる")
    sc, root = st.scene, st.root
    N = 15
    c = (N - 1) / 2
    def Poly_k(nb, x, y, R0=6.2):
        dx, dy = x - c, y - c
        r = math.hypot(dx, dy)
        if nb == 0:
            return 1.0 if r <= R0 else 0.0
        a = math.atan2(dy, dx)
        sec = 2 * math.pi / nb
        d = r * math.cos((a % sec) - sec / 2)
        apothem = R0 * math.cos(math.pi / nb)
        return 1.0 if d <= apothem else 0.0
    shapes = [(5, "羽根 5 枚"), (6, "羽根 6 枚"), (8, "羽根 8 枚"), (0, "円(羽根が多い・丸い絞り)")]
    areas = []
    for nb, _ in shapes:
        grid = [[Poly_k(nb, i, j) for i in range(N)] for j in range(N)]
        areas.append(sum(sum(r) for r in grid))
    t0, per = 1.5, 3.8
    cs = 15.0
    for k, (nb, lab) in enumerate(shapes):
        x = 30 + k * 225
        st.Panel(x, 110, N * cs + 6, N * cs + 6, lab, color=[RED, AMBER, GREEN, BLUE][k])
        g = Grid(st, x + 3, 113, N, N, cs, base="#0f172a")
        for j in range(N):
            for i in range(N):
                if Poly_k(nb, i, j):
                    g.Paint(i, j, t0 + k * per + 0.03 * (abs(i - c) + abs(j - c)), "#fde68a")
        g.Flush()
        gg = root.add("g", opacity=0)
        gg.Show(t0 + k * per + 1.0)
        sc.Text(gg, x, 372, "光の当たる画素 %d 個" % areas[k], size=13, weight=700, fill=TEXT)
        sc.Text(gg, x, 392, ["角が 5 つ。羽根の数が少ない", "六角形", "八角形。丸に近い", "丸い(理想)"][k], size=12, weight=500, fill=MUTED)
    # 点光源がたくさん: 夜景の玉ボケ
    t_c = t0 + 4 * per + 0.5
    st.Panel(30, 420, 900, 60, "夜景の光点 5 つを、羽根 6 枚のボケで描くと(1 列に簡略)", color=PURPLE)
    row = [0.0] * 60
    for p, v in ((8, 1.0), (19, 0.7), (33, 1.0), (40, 0.5), (52, 0.8)):
        row[p] = v
    k6 = [Poly_k(6, i, c) for i in range(N)]
    out = [sum(row[min(59, max(0, i + d - 7))] * k6[d] for d in range(N)) / sum(k6) for i in range(60)]
    g = Grid(st, 44, 440, 60, 1, 14.0, base="#0f172a", stroke="#94a3b8")
    for i in range(60):
        g.Paint(i, 0, t_c + i * 0.04, Mix("#0f172a", "#fde68a", min(1.0, out[i] * 5)))
    g.Flush()
    st.Caption(30, 534, [(0.0, t0, "本物のカメラの絞りは、羽根を重ねた多角形"), (t0, t_c, "点の光は、その多角形の形のまま、ぼける"), (t_c, 99, "ゲームでは、フィルターの形を変えるだけで、カメラの個性(五角形・円形)が出せる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ボケ", "光る画素: 5 枚 %d / 6 枚 %d / 8 枚 %d / 円 %d" % tuple(areas))
    return Build(st, name, "graphics/postprocess/dof/bokeh-shape.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


# ===================================================================== CA shift
def ChromaticShift():
    name = "chromatic-aberration-shift"
    st = Stage(name, "色収差: 画面の中心から離れるほど、赤と青が逆向きにずれ、白い縁に、色のにじみが出る", duration=20.0, subtitle="1 列 64 画素。白と黒の境目(縁)が 3 カ所。赤を外へ、青を内へ、中心からの距離に比例してずらす")
    sc, root = st.scene, st.root
    n = 64
    edges = [16, 32, 56]
    base = [1.0 if (16 <= i < 32 or 56 <= i < 64) else 0.0 for i in range(n)]
    c0 = (n - 1) / 2
    def Shift(k):
        out = []
        for i in range(n):
            d = (i - c0) / c0
            rs = i - k * d * c0 * 0.18        # 赤: 外から来る
            bs = i + k * d * c0 * 0.18
            def S(a, p):
                q = max(0.0, min(n - 1.0, p))
                i0 = int(math.floor(q)); t = q - i0
                i1 = min(n - 1, i0 + 1)
                return a[i0] * (1 - t) + a[i1] * t
            out.append((S(base, rs), S(base, i), S(base, bs)))
        return out
    ks = [0.0, 0.5, 1.0, 2.0]
    res = [Shift(k) for k in ks]
    def Fringe(a, i0):
        return sum(1 for j in range(max(0, i0 - 6), min(n, i0 + 6)) if abs(a[j][0] - a[j][2]) > 0.15)
    fr_center = [Fringe(r, 32) for r in res]
    fr_edge = [Fringe(r, 56) for r in res]
    assert fr_edge[3] > fr_edge[1] > fr_edge[0] and fr_center[3] <= fr_edge[3]
    CW, X0 = 10.5, 60.0
    t0, per = 1.5, 4.0
    for m, k in enumerate(ks):
        y = 116 + m * 62
        sc.Text(root, X0, y - 4, "ずれの強さ k = %g" % k, size=13, weight=700, fill=[GRAY, GREEN, AMBER, RED][m])
        g = Grid(st, X0, y, n, 1, CW, base="#0f172a", stroke="#94a3b8", cell_h=30.0)
        for i in range(n):
            g.Paint(i, 0, t0 + m * per + i * 0.03, Rgbh(res[m][i]))
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + 1.5)
        sc.Text(gx, X0 + n * CW + 10, y + 12, "中心の縁 %d 画素" % fr_center[m], size=12, weight=700, fill=TEXT)
        sc.Text(gx, X0 + n * CW + 10, y + 30, "端の縁 %d 画素" % fr_edge[m], size=12, weight=700, fill=(RED if fr_edge[m] > 3 else TEXT))
    for e in edges:
        root.add("line", x1=R(X0 + e * CW), y1=100, x2=R(X0 + e * CW), y2=366, stroke=LIGHT, stroke_width=1, stroke_dasharray="3 4")
    sc.Text(root, X0 + c0 * CW, 380, "▲ 画面の中心", size=12, weight=700, fill=MUTED, anchor="middle")
    st.Text(40, 420, "端の縁の、色のにじみ(画素):", size=14)
    st.Counter(240, 424, [(t0 + m * per + 1.5, fr_edge[m]) for m in range(4)], size=26, fill=RED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.5, 480, 410, 450, 70, [("中心はずれない。端ほど、赤と青が離れる", 14, "#1e3a8a"), ("中心の縁: %d → %d 画素 / 端の縁: %d → %d 画素" % (fr_center[0], fr_center[3], fr_edge[0], fr_edge[3]), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "レンズは、色(波長)によって、曲がり方が少し違う"), (t0, t_e, "中心からの距離に比例して、赤を外へ、青を内へずらす"), (t_e, 99, "ずれを強くしすぎると、見づらい。やりすぎない")], size=14, fill=MUTED, weight=500)
    for m, k in enumerate(ks):
        st.Note(t0 + m * per, "色収差", "k = %g: 中心 %d / 端 %d 画素" % (k, fr_center[m], fr_edge[m]))
    return Build(st, name, "graphics/postprocess/lens-effects/index.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


# ===================================================================== grain luma
def FilmGrainLuma():
    name = "film-grain-luma"
    st = Stage(name, "フィルム グレイン: 暗い所と明るい所には、粒を弱く、中間に強く(明るさに応じて強さを変える)", duration=20.0, subtitle="黒 → 白の階調(48 段)に、でたらめな粒を足す。粒の強さの掛け方を 2 通りで比べる")
    sc, root = st.scene, st.root
    n = 48
    rng = Lcg(404)
    noise = [rng.U() * 2 - 1 for _ in range(n)]
    lum = [(i + 0.5) / n for i in range(n)]
    amp0 = 0.12
    flat = [amp0 for _ in lum]
    shaped = [amp0 * 4 * l * (1 - l) for l in lum]
    flat_img = [max(0.0, min(1.0, l + a * nz)) for l, a, nz in zip(lum, flat, noise)]
    shp_img = [max(0.0, min(1.0, l + a * nz)) for l, a, nz in zip(lum, shaped, noise)]
    dark_n = lambda img: sum(abs(img[i] - lum[i]) for i in range(0, 8)) / 8
    mid_n = lambda img: sum(abs(img[i] - lum[i]) for i in range(20, 28)) / 8
    bri_n = lambda img: sum(abs(img[i] - lum[i]) for i in range(40, 48)) / 8
    assert dark_n(shp_img) < dark_n(flat_img) / 2 and mid_n(shp_img) > mid_n(flat_img) * 0.8
    CW, X0 = 17.0, 60.0
    st.Text(X0, 108, "階調(粒なし)", size=13, weight=700, fill=GRAY)
    g0 = Grid(st, X0, 114, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=34.0)
    for i in range(n):
        g0.Paint(i, 0, 0.3, Gray(lum[i]))
    g0.Flush()
    rows = [("一様な強さの粒", flat_img, RED, 190), ("明るさに応じた強さの粒(中間が最大)", shp_img, GREEN, 262)]
    t0, per = 1.5, 4.5
    for r_, (lab, img, c, y) in enumerate(rows):
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=c)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=34.0)
        for i in range(n):
            g.Paint(i, 0, t0 + r_ * per + i * 0.05, Gray(img[i]))
        g.Flush()
    # 粒の強さの曲線
    st.Panel(30, 320, 560, 170, "粒の強さ(横 = 明るさ)", color=PURPLE)
    ax0, ay0, aw, ah = 60.0, 336.0, 510.0, 130.0
    XX = lambda l: ax0 + l * aw
    YY = lambda a: ay0 + ah - a / 0.13 * ah
    t_c = t0 + 2 * per + 0.3
    p1 = root.add("path", d=Poly([(XX(l), YY(amp0)) for l in [k / 40 for k in range(41)]]), fill="none", stroke=RED, stroke_width=3.5, opacity=0)
    p2 = root.add("path", d=Poly([(XX(l), YY(amp0 * 4 * l * (1 - l))) for l in [k / 40 for k in range(41)]]), fill="none", stroke=GREEN, stroke_width=3.5, opacity=0)
    p1.Show(t_c)
    p2.Show(t_c + 1.0)
    # 数字
    t_n = t_c + 2.2
    st.Panel(620, 320, 310, 170, "粒の見え方(平均の揺れ)", color=BLUE)
    for k, (lab, vals) in enumerate([("暗い所", (dark_n(flat_img), dark_n(shp_img))), ("中間", (mid_n(flat_img), mid_n(shp_img))), ("明るい所", (bri_n(flat_img), bri_n(shp_img)))]):
        y = 366 + k * 36
        g = root.add("g", opacity=0)
        g.Show(t_n + k * 0.8)
        sc.Text(g, 636, y, lab, size=13, weight=700, fill=INK)
        sc.Text(g, 726, y, "一様 %.3f" % vals[0], size=12, weight=700, fill=RED)
        sc.Text(g, 826, y, "調整 %.3f" % vals[1], size=12, weight=700, fill=GREEN)
    st.Caption(30, 534, [(0.0, t0, "粒を足して、フィルムらしくする"), (t0, t_c, "一様に足すと、暗い所が、粒でざらつく"), (t_c, 99, "明るさに応じて強さを変えると、暗部がきれいで、中間に粒が出る(本物のフィルムに近い)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "グレイン", "暗い所の揺れ: 一様 %.3f / 調整 %.3f" % (dark_n(flat_img), dark_n(shp_img)))
    return Build(st, name, "graphics/postprocess/lens-effects/film-grain.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== Vignette
def VignetteParams():
    name = "vignette-params"
    st = Stage(name, "ビネット: 画面の端を暗くする。半径(どこから暗くするか)と、柔らかさで、形が変わる", duration=20.0, subtitle="横 1 列(中心 → 端)。半径と柔らかさを変えて、端の暗さと、暗くなる範囲を計算する")
    sc, root = st.scene, st.root
    def V(r, rad, soft, strength=0.7):
        t = max(0.0, min(1.0, (r - rad) / max(soft, 1e-3)))
        s = t * t * (3 - 2 * t)
        return 1 - strength * s
    sets = [("半径 0.5・柔らかさ 0.3", 0.5, 0.3), ("半径 0.5・柔らかさ 0.8", 0.5, 0.8), ("半径 0.3・柔らかさ 0.3", 0.3, 0.3), ("半径 0.8・柔らかさ 0.1", 0.8, 0.1)]
    rs = [k / 60 * 1.4 for k in range(61)]
    ax0, ay0, aw, ah = 70.0, 120.0, 560.0, 190.0
    XX = lambda r: ax0 + r / 1.4 * aw
    YY = lambda v: ay0 + ah - v * ah
    st.Panel(30, 96, 620, 240, "① 明るさの倍率(横 = 中心からの距離。1.0 = 画面の端の方向)", color=BLUE)
    for r in (0.5, 1.0):
        root.add("line", x1=R(XX(r)), y1=ay0, x2=R(XX(r)), y2=ay0 + ah, stroke=LIGHT, stroke_width=1.2, stroke_dasharray="3 4")
    sc.Text(root, XX(1.0), 326, "画面の端(左右)", size=11, weight=700, fill=MUTED, anchor="middle")
    sc.Text(root, XX(1.4), 326, "角", size=11, weight=700, fill=MUTED, anchor="middle")
    cols = [RED, GREEN, AMBER, BLUE]
    cur = root.add("path", d=Poly([(XX(r), YY(V(r, sets[0][1], sets[0][2]))) for r in rs]), fill="none", stroke=RED, stroke_width=4)
    t0, per = 1.5, 4.2
    cur.Steps("d", [(t0 + m * per, Poly([(XX(r), YY(V(r, rad, soft))) for r in rs])) for m, (lab, rad, soft) in enumerate(sets)])
    # 画面の暗さ(2 次元)の割合
    def Frac(rad, soft):
        cnt = tot = 0
        for j in range(30):
            for i in range(48):
                x = (i + 0.5) / 48 * 2 - 1
                y = ((j + 0.5) / 30 * 2 - 1) * 0.5625
                r = math.hypot(x, y) / 1.0
                tot += 1
                if V(r, rad, soft) < 0.9:
                    cnt += 1
        return cnt / tot
    fr = [Frac(rad, soft) for _, rad, soft in sets]
    X1, Y1, CS = 680.0, 110.0, 5.8
    st.Panel(670, 96, 260, 200, "② 画面の見え方(16:9)", color=PURPLE)
    for m, (lab, rad, soft) in enumerate(sets):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        gr = Grid(st, 680, 120, 28, 16, 8.8, base="#ffffff", parent=g, stroke="#94a3b8", cell_h=8.4)
        for j in range(16):
            for i in range(28):
                x = (i + 0.5) / 28 * 2 - 1
                y = ((j + 0.5) / 16 * 2 - 1) * 0.5625
                gr.Paint(i, j, t0 + m * per + 0.1, Gray(V(math.hypot(x, y), rad, soft)))
        gr.Flush()
        sc.Text(g, 680, 270, "暗くなる範囲(10%% 以上): %d%%" % round(100 * fr[m]), size=12, weight=700, fill=cols[m])
        sc.Text(g, 40, 372, lab, size=20, weight=700, fill=cols[m])
        sc.Text(g, 40, 402, "端の明るさ: %.2f / 角の明るさ: %.2f" % (V(1.0, rad, soft), V(1.4, rad, soft)), size=14, weight=700, fill=TEXT)
        sc.Text(g, 40, 428, "暗くなる範囲: 画面の %d%%" % round(100 * fr[m]), size=14, weight=700, fill=TEXT)
    st.Text(40, 470, "暗くなる範囲(%):", size=14)
    st.Counter(180, 474, [(t0 + m * per + 0.3, int(round(100 * fr[m]))) for m in range(4)], size=24, fill=PURPLE)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.4, 400, 440, 530, 70, [("半径が小さいほど、広い範囲が暗い。柔らかさが小さいほど、境目が硬い", 14, "#1e3a8a"), ("強すぎると、画面が見づらい。ゲームでは、弱めにする", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "端を暗くすると、視線が中央に集まる"), (t0, t_e, "半径と柔らかさで、形を決める"), (t_e, 99, "ダメージ表現などで、強さを時間で変える使い方もある")], size=14, fill=MUTED, weight=500)
    for m, (lab, rad, soft) in enumerate(sets):
        st.Note(t0 + m * per, "ビネット", "%s: 暗くなる範囲 %d%%" % (lab, round(100 * fr[m])))
    return Build(st, name, "graphics/postprocess/lens-effects/vignette.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 19.0])


NAMES = ["coc-graph", "dof-gather-weight", "dof-near-field", "dof-scatter-gather", "bokeh-shapes-anim", "chromatic-aberration-shift", "film-grain-luma", "vignette-params"]
FIGS = [CocGraph, DofGatherWeight, DofNearField, DofScatterGather, BokehShapes, ChromaticShift, FilmGrainLuma, VignetteParams]
