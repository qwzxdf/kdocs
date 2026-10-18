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


def Aces(x):
    return max(0.0, min(1.0, (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)))


def Gam(v):
    return max(0.0, min(1.0, v)) ** (1 / 2.2)


# ===================================================================== Auto exposure histogram
def AutoExposureHistogram():
    name = "auto-exposure-histogram"
    st = Stage(name, "自動露出(ヒストグラム): 画面の明るさの分布を作り、暗い所と明るすぎる所を除いた平均で、露出を決める", duration=21.0, subtitle="24×12 画素の HDR 画像(窓から日が差す部屋)。明るさを 8 段のビンに数える")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 12, 14.0
    img = [[0.08 + 0.02 * (i / NX) for i in range(NX)] for j in range(NY)]
    for j in range(2, 9):
        for i in range(15, 23):
            img[j][i] = 6.0 + 2.0 * ((i + j) % 3)
    for j in range(8, 12):
        for i in range(2, 12):
            img[j][i] = 0.22
    img[10][3] = 0.001
    ev = lambda v: math.log2(max(v, 1e-4))
    edges = list(range(-6, 4))               # EV -6 .. 3
    nb = len(edges) - 1
    bins = [0] * nb
    which = {}
    for j in range(NY):
        for i in range(NX):
            e = ev(img[j][i])
            b = max(0, min(nb - 1, int(math.floor(e - edges[0]))))
            bins[b] += 1
            which[(i, j)] = b
    total = NX * NY
    assert sum(bins) == total
    lo_c, hi_c = 0.10, 0.90
    cum = 0
    keep = []
    for b in range(nb):
        a, c = cum / total, (cum + bins[b]) / total
        keep.append(not (c <= lo_c or a >= hi_c))
        cum += bins[b]
    wsum = sum(bins[b] for b in range(nb) if keep[b])
    mean_ev = sum((edges[b] + 0.5) * bins[b] for b in range(nb) if keep[b]) / wsum
    plain_ev = sum(ev(img[j][i]) for j in range(NY) for i in range(NX)) / total
    avg_lin = sum(img[j][i] for j in range(NY) for i in range(NX)) / total
    target = 0.18
    expo_h = target / (2 ** mean_ev)
    expo_a = target / avg_lin
    st.Panel(30, 96, NX * CS + 16, NY * CS + 16, "① 入力(HDR)", color=AMBER)
    g = Grid(st, 38, 104, NX, NY, CS, base="#0f172a")
    t0, dts = 1.5, 0.06
    for j in range(NY):
        for i in range(NX):
            g.Paint(i, j, 0.3, Hex([255 * Gam(img[j][i] * 0.9)] * 3))
    g.Flush()
    cols = ["#0e7490", "#0891b2", "#38bdf8", "#60a5fa", "#818cf8", "#a78bfa", "#f472b6", "#fb7185", "#fbbf24"]
    # ヒストグラム
    X1 = 410
    st.Panel(X1, 96, 520, 200, "② 明るさ(EV)ごとの画素数", color=PURPLE)
    base_y = 270
    scl = 150.0 / max(bins)
    for b in range(nb):
        x = X1 + 18 + b * 55
        t = t0 + b * 1.0
        for (i, j), bb in which.items():
            pass
        h = bins[b] * scl
        gg = root.add("g", opacity=0)
        gg.Show(t)
        gg.add("rect", x=x, y=R(base_y - h), width=46, height=R(max(h, 1)), fill=cols[b], opacity=0.9)
        sc.Text(gg, x + 23, R(base_y - h) - 5, str(bins[b]), size=12, weight=700, fill=TEXT, anchor="middle")
        sc.Text(gg, x + 23, base_y + 14, "%+d〜%+d" % (edges[b], edges[b + 1]), size=10, weight=500, fill=MUTED, anchor="middle")
    # 数えている画素のハイライト
    for b in range(nb):
        t = t0 + b * 1.0
        for (i, j), bb in which.items():
            if bb == b:
                fr = g.Frame(i, j, cols[b], 2.5)
                fr.Show(t, t + 1.0)
    # 切り捨て
    t_c = t0 + nb * 1.0 + 0.8
    for b in range(nb):
        if not keep[b]:
            x = X1 + 18 + b * 55
            x_ = root.add("rect", x=x, y=140, width=46, height=130, fill="#ffffff", fill_opacity=0.65, opacity=0)
            x_.Show(t_c)
    sc.Text(root, X1 + 18, 118, "下位 10% と上位 10% を捨てる(白く薄れた所)", size=12, weight=700, fill=RED, opacity=0).Show(t_c)
    # 結果
    t_r = t_c + 1.8
    st.Panel(30, 330, 900, 150, "③ 平均の明るさと、そこから決める露出", color=BLUE)
    lines = [("全画素の単純平均(明るい窓に引っぱられる)", "平均 %.2f → 露出 ×%.3f" % (avg_lin, expo_a), RED), ("ヒストグラムの中央を使った平均(窓と暗がりを除く)", "平均 EV %.1f → 露出 ×%.3f" % (mean_ev, expo_h), GREEN)]
    for k, (a, b, col) in enumerate(lines):
        y = 366 + k * 40
        sc.Text(root, 50, y, a, size=14, weight=700, fill=col, opacity=0).Show(t_r + k * 1.4)
        sc.Text(root, 540, y, b, size=16, weight=700, fill=col, opacity=0).Show(t_r + k * 1.4)
    px_a = [[Gam(img[j][i] * expo_a) for i in range(NX)] for j in range(NY)]
    px_h = [[Gam(img[j][i] * expo_h) for i in range(NX)] for j in range(NY)]
    mean_dark = lambda pic: sum(pic[j][i] for j in range(8, 12) for i in range(2, 12)) / 40
    dk_a, dk_h = mean_dark(px_a), mean_dark(px_h)
    assert dk_h > dk_a
    st.Text(50, 450, "暗がりの見え方:", size=14)
    sc.Text(root, 170, 450, "単純平均 → 画面の明るさ %.2f(つぶれる)/ ヒストグラム → %.2f(見える)" % (dk_a, dk_h), size=14, weight=700, fill=PURPLE, opacity=0).Show(t_r + 3.0)
    st.Caption(30, 534, [(0.0, t0, "窓の外は明るすぎて、平均を引っぱってしまう"), (t0, t_c, "画素を明るさ(EV)ごとのビンに数える"), (t_c, t_r, "暗すぎる画素と、明るすぎる画素を、捨てる"), (t_r, 99, "残りの平均が、目に見えてほしい明るさ → 露出が決まる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "露出", "ビン %d 個。平均 EV %.1f(単純平均 EV %.1f)" % (nb, mean_ev, math.log2(avg_lin)))
    return Build(st, name, "graphics/postprocess/tonemapping/auto-exposure.md", BEFORE, [1.5, 4.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== Auto exposure adapt
def AutoExposureAdapt():
    name = "auto-exposure-adapt"
    st = Stage(name, "自動露出の適応: 急に明るくなっても、露出はゆっくり追いかける(目の慣れ)", duration=22.0, subtitle="部屋(明るさ 0.2)から、外(明るさ 8)へ出て、また戻る。露出が追いつく速さ(慣れの速さ)を 3 通りで比べる")
    sc, root = st.scene, st.root
    dt = 1 / 30
    T = 18.0
    n = int(T / dt)
    scene_l = lambda t: 8.0 if 4.0 <= t < 11.0 else 0.2
    target = 0.18
    ks = [("速い(τ = 0.3 秒)", 0.3, RED), ("ふつう(τ = 1 秒)", 1.0, GREEN), ("ゆっくり(τ = 3 秒)", 3.0, BLUE)]
    res = []
    for lab, tau, col in ks:
        e = target / 0.2
        ser = []
        for k in range(n + 1):
            t = k * dt
            want = target / scene_l(t)
            a = 1 - math.exp(-dt / tau)
            e += (want - e) * a
            ser.append(e)
        res.append(ser)
    shown = lambda ser, k: min(1.0, scene_l(k * dt) * ser[k])
    # 明るさが適正(0.18 付近)に戻るまでの時間
    def Recover(ser, t0):
        for k in range(int(t0 / dt), n + 1):
            v = scene_l(k * dt) * ser[k]
            if v < 0.18 * 1.6:
                return k * dt - t0
        return float("inf")
    rec = [Recover(s, 4.0) for s in res]
    peak = [max(scene_l(k * dt) * s[k] for k in range(int(4 / dt), int(5 / dt))) for s in res]
    assert rec[0] < rec[1] < rec[2]
    X0, W = 70.0, 820.0
    XX = lambda t: X0 + t / T * W
    st.Panel(30, 96, 900, 200, "① 画面に出る明るさ(1.0 = 白飛び)", color=BLUE)
    YY = lambda v: 276 - min(v, 1.4) * 130
    root.add("line", x1=X0, y1=R(YY(1.0)), x2=X0 + W, y2=R(YY(1.0)), stroke="#ef4444", stroke_width=1.5, stroke_dasharray="4 4")
    sc.Text(root, X0 + W, R(YY(1.0)) - 4, "白飛び", size=11, weight=700, fill="#ef4444", anchor="end")
    root.add("rect", x=R(XX(4)), y=100, width=R(XX(11) - XX(4)), height=190, fill="#fde68a", fill_opacity=0.25)
    sc.Text(root, XX(4) + 8, 118, "外へ出る(明るさ 0.2 → 8)", size=12, weight=700, fill="#92400e")
    step = 6
    for m, (lab, tau, col) in enumerate(ks):
        pts = [(XX(k * dt), YY(shown(res[m], k))) for k in range(0, n + 1, step)]
        p = root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(1.0 + m * 5.0)
        sc.Text(root, 80, 130 + m * 20, "%s: 戻るまで %.1f 秒、最大 %.1f" % (lab, rec[m], peak[m]), size=12, weight=700, fill=col, opacity=0).Show(1.0 + m * 5.0)
    st.Panel(30, 316, 900, 150, "② 露出の値(小さい = 絞っている)", color=PURPLE)
    emax = max(max(s) for s in res)
    emin = min(min(s) for s in res)
    EY = lambda v: 450 - (math.log(v) - math.log(emin)) / (math.log(emax) - math.log(emin)) * 100
    for m, (lab, tau, col) in enumerate(ks):
        pts = [(XX(k * dt), EY(res[m][k])) for k in range(0, n + 1, step)]
        p = root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3, opacity=0)
        p.Show(1.0 + m * 5.0)
    t_e = 1.0 + 3 * 5.0
    st.Box(t_e, 520, 330, 400, 130, [("速い: すぐ慣れるが、急に画面が変わって不自然", 13, "#991b1b"), ("ゆっくり: 長い間、白飛び(最大 %.1f)" % peak[2], 13, "#1e3a8a"), ("ふつう: 戻るまで %.1f 秒" % rec[1], 14, "#166534"), ("明るい所へは速く、暗い所へは遅く、が自然(目と同じ)", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, 1.0, "露出は、毎フレーム、目標の明るさへ、少しだけ近づける(指数関数的に)"), (1.0, t_e, "τ(慣れの時間)が小さいほど、速く追いつく"), (t_e, 99, "適正な速さは、ゲームの演出で決める")], size=14, fill=MUTED, weight=500)
    for m, (lab, tau, col) in enumerate(ks):
        st.Note(1.0 + m * 5.0, "適応", "%s: 戻るまで %.1f 秒、最大 %.1f" % (lab, rec[m], peak[m]))
    return Build(st, name, "graphics/postprocess/tonemapping/auto-exposure.md", BEFORE, [2.0, 6.0, 11.0, 16.0, 19.0, 21.0])


# ===================================================================== Exposure EV
def ExposureEv():
    name = "exposure-ev"
    st = Stage(name, "露出(EV): 1 段上げると、明るさが 2 倍。同じ絵を、−3 〜 +3 段で並べる", duration=19.0, subtitle="線形の明るさ 0.02 〜 3 の 5 つの面。EV を変えて、画面(sRGB)での見え方がどう変わるか")
    sc, root = st.scene, st.root
    surf = [("黒い布", 0.02), ("濃い灰", 0.07), ("中間の灰", 0.18), ("明るい壁", 0.7), ("光る面", 3.0)]
    evs = [-3, -1, 0, 1, 3]
    t0, per = 1.5, 3.2
    cw = 120.0
    X0 = 110.0
    for k, (lab, v) in enumerate(surf):
        sc.Text(root, X0 + k * (cw + 14) + cw / 2, 116, lab, size=14, weight=700, fill=INK, anchor="middle")
        sc.Text(root, X0 + k * (cw + 14) + cw / 2, 134, "明るさ %g" % v, size=12, weight=500, fill=MUTED, anchor="middle")
    for k in range(5):
        pass
    sq = []
    for k, (lab, v) in enumerate(surf):
        r = root.add("rect", x=R(X0 + k * (cw + 14)), y=146, width=cw, height=100, fill=Gray(v), stroke="#94a3b8", stroke_width=1.5)
        r.Steps("fill", [(t0 + m * per, Gray(v * 2.0 ** e)) for m, e in enumerate(evs)])
        sq.append(r)
        t = sc.Text(root, X0 + k * (cw + 14) + cw / 2, 205, "", size=13, weight=700, fill="#ef4444", anchor="middle")
    # 数字(面ごと、EV ごと)
    for m, e in enumerate(evs):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 4 else None)
        sc.Text(g, 40, 290, "露出 %+d EV(×%g)" % (e, 2.0 ** e), size=22, weight=700, fill=PURPLE)
        for k, (lab, v) in enumerate(surf):
            out = v * 2.0 ** e
            clip = out >= 1.0
            sc.Text(g, X0 + k * (cw + 14) + cw / 2, 270 if False else 322, "%.3f" % out, size=13, weight=700, fill=("#ef4444" if clip else TEXT), anchor="middle")
            sc.Text(g, X0 + k * (cw + 14) + cw / 2, 342, "白飛び" if clip else ("%d / 255" % round(255 * Gam(out))), size=11, weight=700 if clip else 500, fill=("#ef4444" if clip else MUTED), anchor="middle")
    sc.Text(root, 60, 322, "掛けた後", size=12, weight=700, fill=MUTED, anchor="end")
    sc.Text(root, 60, 342, "画面の値", size=12, weight=700, fill=MUTED, anchor="end")
    # 白飛びと潰れの数
    clip_n = []
    dark_n = []
    for e in evs:
        outs = [v * 2.0 ** e for _, v in surf]
        clip_n.append(sum(1 for o in outs if o >= 1.0))
        dark_n.append(sum(1 for o in outs if Gam(o) < 0.12))
    assert clip_n[-1] > clip_n[0] and dark_n[0] > dark_n[-1]
    st.Panel(30, 372, 900, 100, "白飛びした面と、黒くつぶれた面の数", color=RED)
    for m, e in enumerate(evs):
        x = 70 + m * 175
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        sc.Text(g, x, 414, "%+d EV" % e, size=14, weight=700, fill=INK)
        sc.Text(g, x, 436, "白飛び %d / つぶれ %d" % (clip_n[m], dark_n[m]), size=13, weight=700, fill=(RED if clip_n[m] + dark_n[m] > 2 else GREEN))
    st.Counter(70, 466, [(t0 + m * per + 0.2, e) for m, e in enumerate(evs)], size=1, fill="#ffffff") if False else None
    st.Box(t0 + 5 * per, 560, 480, 370, 40, [("全部がちょうど見える露出は、無い → トーンマップが必要", 13, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "1 EV 上げる = 光の量が 2 倍(カメラの絞り 1 段)"), (t0, t0 + 5 * per, "5 つの面は、明るさがバラバラ。露出を変えると、見える面が、入れ替わる"), (t0 + 5 * per, 99, "暗い面を見えるように上げると、明るい面が白飛びする")], size=14, fill=MUTED, weight=500)
    for m, e in enumerate(evs):
        st.Note(t0 + m * per, "EV", "%+d EV: 白飛び %d、つぶれ %d" % (e, clip_n[m], dark_n[m]))
    return Build(st, name, "graphics/postprocess/tonemapping/exposure.md", BEFORE, [2.0, 5.5, 8.5, 12.0, 15.0, 18.0])


# ===================================================================== Hable
def TonemapHable():
    name = "tonemap-hable"
    st = Stage(name, "Hable(Uncharted 2)のフィルミック曲線: 暗い所は立ち上がりをゆるやかに(つま先)、明るい所は、なだらかに(肩)", duration=20.0, subtitle="同じ明るさの階調を、直線的な圧縮(Reinhard)と並べる。曲線の傾きが、コントラストを決める")
    sc, root = st.scene, st.root

    def Hable(x):
        A, B, C, D, E, F = 0.15, 0.50, 0.10, 0.20, 0.02, 0.30
        f = lambda v: ((v * (A * v + C * B) + D * E) / (v * (A * v + B) + D * F)) - E / F
        return max(0.0, min(1.0, f(2.0 * x) / f(11.2)))

    rein = lambda x: x / (1 + x)
    xs = [0.02 * (8.0 / 0.02) ** (k / 80) for k in range(81)]
    slope = lambda f, x: (f(x * 1.01) - f(x)) / (x * 0.01) * x
    toe_h, toe_r = slope(Hable, 0.1), slope(rein, 0.1)
    mid_h, mid_r = slope(Hable, 0.8), slope(rein, 0.8)
    sho_h, sho_r = slope(Hable, 5.0), slope(rein, 5.0)
    assert toe_h < toe_r and mid_h > mid_r
    X0, W = 70.0, 440.0
    st.Panel(30, 96, 500, 270, "① 曲線(横 = 入力、対数)", color=BLUE)
    XX = lambda x: X0 + (math.log(x) - math.log(0.02)) / (math.log(8.0) - math.log(0.02)) * W
    YY = lambda v: 346 - v * 210
    root.add("path", d=Poly([(XX(x), YY(rein(x))) for x in xs]), fill="none", stroke=BLUE, stroke_width=3.5)
    root.add("path", d=Poly([(XX(x), YY(Hable(x))) for x in xs]), fill="none", stroke=RED, stroke_width=3.5)
    st.Legend(80, 124, [(BLUE, "Reinhard"), (RED, "Hable")])
    for lab, x in (("暗い所", 0.1), ("中間", 0.8), ("明るい所", 5.0)):
        root.add("line", x1=R(XX(x)), y1=140, x2=R(XX(x)), y2=346, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="3 4")
        sc.Text(root, XX(x), 360, lab, size=11, weight=700, fill=MUTED, anchor="middle")
    # 階調の帯
    N = 28
    xs2 = [0.02 * (8.0 / 0.02) ** (k / (N - 1)) for k in range(N)]
    st.Panel(560, 96, 370, 270, "② 階調の見え方", color=PURPLE)
    t0 = 1.5
    for r_, (lab, f, col) in enumerate([("入力(ただ明るさを並べた)", lambda x: min(1.0, x), GRAY), ("Reinhard", rein, BLUE), ("Hable", Hable, RED)]):
        y = 140 + r_ * 70
        sc.Text(root, 576, y - 6, lab, size=13, weight=700, fill=col)
        g = Grid(st, 576, y, N, 1, 12.5, base="#e5e7eb", stroke="#94a3b8")
        for k, x in enumerate(xs2):
            g.Paint(k, 0, t0 + r_ * 3.0 + k * 0.06, Gray(f(x)))
        g.Flush()
    t_r = t0 + 3 * 3.0
    st.Panel(30, 386, 900, 90, "③ 傾き(= コントラスト)。大きいほど、階調の差がはっきり", color=GREEN)
    for k, (lab, sh, sr) in enumerate([("暗い所(入力 0.1)", toe_h, toe_r), ("中間(入力 0.8)", mid_h, mid_r), ("明るい所(入力 5)", sho_h, sho_r)]):
        x = 50 + k * 300
        g = root.add("g", opacity=0)
        g.Show(t_r + k * 1.2)
        sc.Text(g, x, 424, lab, size=13, weight=700, fill=INK)
        sc.Text(g, x, 448, "Reinhard %.2f / Hable %.2f" % (sr, sh), size=14, weight=700, fill=(GREEN if sh > sr else BLUE))
        sc.Text(g, x, 466, "Hable の方が%s" % ("コントラストが高い" if sh > sr else "なだらか"), size=12, weight=500, fill=MUTED)
    st.Caption(30, 534, [(0.0, t0, "曲線の形が、画の「味」を決める"), (t0, t_r, "同じ階調を、3 通りで並べる"), (t_r, 99, "Hable は、中間のコントラストを上げ、暗部と明部をなだらかにする(フィルムの特性)")], size=14, fill=MUTED, weight=500)
    st.Note(t_r, "Hable", "傾き: 暗 %.2f/%.2f、中 %.2f/%.2f、明 %.2f/%.2f(Hable/Reinhard)" % (toe_h, toe_r, mid_h, mid_r, sho_h, sho_r))
    return Build(st, name, "graphics/postprocess/tonemapping/filmic-hable.md", BEFORE, [2.0, 4.0, 7.0, 11.0, 15.0, 19.0])


# ===================================================================== Reinhard
def TonemapReinhard():
    name = "tonemap-reinhard"
    st = Stage(name, "Reinhard: x ÷ (1 + x)。どんなに明るくても 1 を超えないが、白に届かない。白点を足して、直す", duration=20.0, subtitle="明るさ 0 〜 8 の階調。素の Reinhard と、白点つき(L_white)を比べる。L_white を 2 → 4 → 8 に変える")
    sc, root = st.scene, st.root
    rein = lambda x: x / (1 + x)
    rw = lambda x, w: min(1.0, x * (1 + x / (w * w)) / (1 + x))
    xs = [8.0 * k / 80 for k in range(81)]
    ws = [2.0, 4.0, 8.0]
    st.Panel(30, 96, 600, 270, "① 曲線", color=BLUE)
    X0, W = 70.0, 540.0
    XX = lambda x: X0 + x / 8.0 * W
    YY = lambda v: 346 - v * 220
    root.add("path", d=Poly([(XX(x), YY(min(1.0, x))) for x in xs]), fill="none", stroke=GRAY, stroke_width=2, stroke_dasharray="5 4")
    root.add("path", d=Poly([(XX(x), YY(rein(x))) for x in xs]), fill="none", stroke=BLUE, stroke_width=3.5)
    cur = root.add("path", d=Poly([(XX(x), YY(rw(x, ws[0]))) for x in xs]), fill="none", stroke=RED, stroke_width=4)
    t0, per = 1.5, 5.0
    cur.Steps("d", [(t0 + m * per, Poly([(XX(x), YY(rw(x, w))) for x in xs])) for m, w in enumerate(ws)])
    st.Legend(80, 124, [(GRAY, "そのまま"), (BLUE, "素の Reinhard"), (RED, "白点つき")])
    N = 28
    xs2 = [8.0 * (k + 1) / N for k in range(N)]
    st.Panel(660, 96, 270, 270, "② 数字", color=PURPLE)
    white_pt = rein(8.0)
    assert white_pt < 0.9
    for m, w in enumerate(ws):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        v8 = rw(8.0, w)
        sc.Text(g, 676, 134, "L_white = %g" % w, size=20, weight=700, fill=RED)
        sc.Text(g, 676, 164, "入力 8 の出力: %.2f" % v8, size=15, weight=700, fill=TEXT)
        sc.Text(g, 676, 188, "素の Reinhard では %.2f" % white_pt, size=13, weight=500, fill=BLUE)
        sc.Text(g, 676, 216, "入力 %g 以上は 1(白)" % w if v8 >= 1.0 else "入力 8 でも、まだ白ではない", size=13, weight=700, fill=(GREEN if v8 >= 1.0 else MUTED))
    st.Panel(30, 386, 900, 90, "③ 階調の見え方(入力 0.3 〜 8)", color=GREEN)
    for r_, (lab, f, col) in enumerate([("素の Reinhard", rein, BLUE), ("白点つき(L_white = 4)", lambda x: rw(x, 4.0), RED)]):
        y = 408 + r_ * 34
        sc.Text(root, 40, y + 14, lab, size=12, weight=700, fill=col)
        g = Grid(st, 230, y, N, 1, 22.0, base="#e5e7eb", stroke="#94a3b8")
        for k, x in enumerate(xs2):
            g.Paint(k, 0, t0 + 3 * per + k * 0.05 - 3 * per + 3.0, Gray(f(x)))
        g.Flush()
    st.Caption(30, 534, [(0.0, t0, "素の Reinhard は、どんなに明るくても、白に届かない"), (t0, t0 + 3 * per, "白点 L_white を決めると、その明るさが、ちょうど白になる"), (t0 + 3 * per, 99, "L_white が小さいほど、明るい所が潰れやすい")], size=14, fill=MUTED, weight=500)
    for m, w in enumerate(ws):
        st.Note(t0 + m * per, "Reinhard", "L_white = %g: 入力 8 → %.2f" % (w, rw(8.0, w)))
    return Build(st, name, "graphics/postprocess/tonemapping/reinhard.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 17.0, 19.0])


# ===================================================================== Hue preservation
def HuePreserve():
    name = "hue-preserve"
    st = Stage(name, "色相の保存: 色ごとにトーンマップすると、明るい所で色が白くずれる。明るさだけを圧縮すると、色が保たれる", duration=20.0, subtitle="オレンジ(R:G:B = 1 : 0.45 : 0.1)の明るさを 0.1 〜 16 倍。2 通りの方法で、色相(色の種類)の変化を計算する")
    sc, root = st.scene, st.root
    base = (1.0, 0.45, 0.1)
    exps = [0.1 * (16 / 0.1) ** (k / 27) for k in range(28)]
    rein = lambda x: x / (1 + x)

    def Hue(c):
        r, g, b = c
        mx, mn = max(c), min(c)
        if mx - mn < 1e-9:
            return 0.0
        if mx == r:
            h = ((g - b) / (mx - mn)) % 6
        elif mx == g:
            h = (b - r) / (mx - mn) + 2
        else:
            h = (r - g) / (mx - mn) + 4
        return h * 60

    def Sat(c):
        mx, mn = max(c), min(c)
        return 0.0 if mx < 1e-9 else (mx - mn) / mx

    per_ch = [[rein(base[k] * e) for k in range(3)] for e in exps]
    lum = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    lum_only = []
    for e in exps:
        c = [base[k] * e for k in range(3)]
        L = lum(c)
        s = rein(L) / L
        lum_only.append([min(1.0, v * s) for v in c])
    h0 = Hue(base)
    hs_a = [abs(Hue(c) - h0) for c in per_ch]
    hs_b = [abs(Hue(c) - h0) for c in lum_only]
    sat_a = [Sat(c) for c in per_ch]
    assert max(hs_a) > max(hs_b) and sat_a[-1] < Sat(base) * 0.6
    N, CW, X0 = 28, 28.0, 70.0
    rows = [("色ごとにトーンマップ(R, G, B それぞれに x ÷ (1 + x))", per_ch, RED, 120), ("明るさ(輝度)だけを圧縮して、色の比率は保つ", lum_only, GREEN, 190)]
    t0 = 1.5
    for r_, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 6, lab, size=14, weight=700, fill=col)
        g = Grid(st, X0, y, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for k, c in enumerate(vals):
            g.Paint(k, 0, t0 + r_ * 4.0 + k * 0.1, Hex([255 * Gam(v) for v in c]))
        g.Flush()
    st.Text(X0, 262, "← 暗い(×0.1)                       明るい(×16) →", size=12, weight=500, fill=MUTED)
    t_h = t0 + 2 * 4.0 + 0.5
    st.Panel(30, 286, 900, 190, "色相のずれ(度)。元のオレンジ = %d°" % round(h0), color=PURPLE)
    ax0, ay0, aw, ah = 70.0, 304.0, 820.0, 150.0
    XX = lambda k: ax0 + k / 27 * aw
    ymax = max(hs_a) * 1.15
    YY = lambda v: ay0 + ah - v / ymax * ah
    for vals, col, lab in ((hs_a, RED, "色ごと"), (hs_b, GREEN, "輝度だけ")):
        p = root.add("path", d=Poly([(XX(k), YY(v)) for k, v in enumerate(vals)]), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(t_h + (0 if col == RED else 1.5))
    st.Legend(80, 470, [(RED, "色ごと(最大ずれ %d°)" % round(max(hs_a))), (GREEN, "輝度だけ(最大ずれ %d°)" % round(max(hs_b)))])
    t_e = t_h + 3.5
    st.Box(t_e, 80, 300, 470, 70, [("色ごと: 明るいほど、白っぽくなる(彩度 %.2f → %.2f)" % (Sat(base), sat_a[-1]), 13, "#991b1b"), ("輝度だけ: 色相が保たれる。ただし、1 を超える成分は切る必要がある", 13, "#166534")], PURPLE, "#faf5ff")
    st.Caption(30, 534, [(0.0, t0, "明るい炎は、色ごとに圧縮すると、白に近づく(色が失われる)"), (t0, t_h, "2 通りで、明るさ 28 段階を塗る"), (t_h, 99, "輝度だけを圧縮すると、色相が保たれる。どちらが良いかは、絵作りで決める")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "色相", "色相のずれ(最大): 色ごと %d° / 輝度のみ %d°" % (round(max(hs_a)), round(max(hs_b))))
    return Build(st, name, "graphics/postprocess/tonemapping/hue-preservation.md", BEFORE, [2.0, 6.0, 9.0, 12.0, 15.0, 19.0])


# ===================================================================== Gamma
def GammaSrgb():
    name = "gamma-srgb"
    st = Stage(name, "ガンマ: 光の量(線形)の足し算を、ガンマ空間でやると、暗くなる", duration=20.0, subtitle="白と黒の細かい縞(縞 1 本ごとに 1 画素)を、縮小して平均する。ガンマ空間で平均する場合と、線形に直してから平均する場合")
    sc, root = st.scene, st.root
    N, CW, X0 = 32, 26.0, 70.0
    stripes = [1.0 if (i % 2 == 0) else 0.0 for i in range(N)]       # 線形の光(白 = 1)
    # 画面に出す値(sRGB)
    enc = lambda v: v ** (1 / 2.2)
    dec = lambda v: v ** 2.2
    shown = [enc(v) for v in stripes]
    # 縮小: 隣り合う 2 つを平均
    wrong = [(shown[2 * k] + shown[2 * k + 1]) / 2 for k in range(N // 2)]               # sRGB 値のまま平均
    right = [enc((stripes[2 * k] + stripes[2 * k + 1]) / 2) for k in range(N // 2)]      # 線形で平均して、再び sRGB へ
    assert abs(dec(wrong[0]) - 0.5) > 0.2 and abs(dec(right[0]) - 0.5) < 1e-9
    st.Text(X0, 108, "元の縞(白 = 光 1、黒 = 光 0。遠くから見ると、光の量は半分)", size=13, weight=700, fill=TEXT)
    g0 = Grid(st, X0, 114, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        g0.Paint(i, 0, 0.3, Gray(stripes[i]))
    g0.Flush()
    t0, dts = 1.5, 0.2
    rows = [("sRGB の値のまま平均(間違い)", wrong, RED, 200), ("線形に直して平均 → sRGB へ戻す(正しい)", right, GREEN, 270)]
    for r_, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 6, lab, size=14, weight=700, fill=col)
        g = Grid(st, X0, y, N // 2, 1, CW * 2, base="#e5e7eb", stroke="#94a3b8")
        for k, v in enumerate(vals):
            g.Paint(k, 0, t0 + r_ * 4.0 + k * dts, Hex([255 * v] * 3))
        g.Flush()
    # 参照: 本当に半分の光
    sc.Text(root, X0, 336, "参照: 光が半分の灰色(sRGB で %d / 255)" % round(255 * enc(0.5)), size=13, weight=700, fill=BLUE)
    gr = Grid(st, X0, 342, N // 2, 1, CW * 2, base="#e5e7eb", stroke="#94a3b8")
    for k in range(N // 2):
        gr.Paint(k, 0, 0.3, Hex([255 * enc(0.5)] * 3))
    gr.Flush()
    t_n = t0 + 8.0 + 4.0
    st.Panel(30, 414, 900, 80, "平均後の光の量(1 = 白、本当は 0.50)", color=PURPLE)
    for k, (lab, vals, col, y) in enumerate(rows):
        x = 50 + k * 450
        g = root.add("g", opacity=0)
        g.Show(t_n + k * 1.5)
        lin = dec(vals[0])
        sc.Text(g, x, 450, lab.split("(")[0], size=13, weight=700, fill=col)
        sc.Text(g, x, 478, "%.2f(本当の光の %d%%)" % (lin, round(100 * lin / 0.5)), size=18, weight=700, fill=col)
    st.Caption(30, 534, [(0.0, t0, "画像の値は、暗い所を細かく表すように、ガンマ(約 2.2 乗)で保存されている"), (t0, t_n, "縮小(平均)を、2 通りでやってみる"), (t_n, 99, "光の足し算は、線形でやらないと、暗くなる(縮小、ブルーム、ブレンドすべて)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ガンマ", "sRGB 値で平均: 光 %.2f / 線形で平均: 光 %.2f" % (dec(wrong[0]), dec(right[0])))
    return Build(st, name, "graphics/postprocess/tonemapping/gamma-srgb.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 19.0])


NAMES = ["auto-exposure-histogram", "auto-exposure-adapt", "exposure-ev", "tonemap-hable", "tonemap-reinhard", "hue-preserve", "gamma-srgb"]
FIGS = [AutoExposureHistogram, AutoExposureAdapt, ExposureEv, TonemapHable, TonemapReinhard, HuePreserve, GammaSrgb]
