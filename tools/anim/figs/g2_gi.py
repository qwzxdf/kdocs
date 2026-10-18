import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402

BEFORE = "## よくあるミス"


def Track(node, keys, attrs=("cx", "cy")):
    """keys = [(t, x, y), ...] に沿って動かす。"""
    prev = None
    for k, (t, x, y) in enumerate(keys):
        if k == 0:
            node.Set(t, attrs[0], R(x))
            node.Set(t, attrs[1], R(y))
        else:
            node.Ramp(prev, t, attrs[0], R(x))
            node.Ramp(prev, t, attrs[1], R(y))
        prev = t


def ProbeBilinear():
    name = "probe-bilinear"
    st = Stage(name, "プローブの補間: 壁を挟むと、普通の補間では光が漏れる(可視性で重みを直す)", duration=17.0, subtitle="壁の左は明るい部屋、右は暗い部屋。プローブ 5 個の明るさから、間の明るさを補間する。実際の明るさ(正解)と比べる")
    sc, root = st.scene, st.root
    LX, WALL = 8.0, 12.0
    probes = [6.0, 10.0, 14.0, 18.0, 22.0]
    AMB = 0.03

    def E(x):
        if x > WALL:
            return AMB
        return 0.9

    ep = [E(p) for p in probes]
    X0, XW = 50.0, 860.0
    UX = lambda x: X0 + (x - 6.0) / 16.0 * XW
    # 補間
    def Interp(x, vis):
        i = max(0, min(len(probes) - 2, int(math.floor((x - 6.0) / 4.0))))
        t = (x - probes[i]) / 4.0
        wl, wr = 1 - t, t
        if vis:
            vl = 0.0 if (probes[i] < WALL < x) or (x < WALL < probes[i]) else 1.0
            vr = 0.0 if (probes[i + 1] < WALL < x) or (x < WALL < probes[i + 1]) else 1.0
            wl, wr = wl * vl, wr * vr
            s = wl + wr
            if s > 0:
                wl, wr = wl / s, wr / s
        return wl * ep[i] + wr * ep[i + 1], wl, wr, i

    xs = [6.0 + 16.0 * k / 40 for k in range(41)]
    xs = [x for x in xs if abs(x - WALL) > 1e-6]
    truth = [E(x) for x in xs]
    plain = [Interp(x, False)[0] for x in xs]
    vis = [Interp(x, True)[0] for x in xs]
    err_p = sum(abs(a - b) for a, b in zip(plain, truth)) / len(xs)
    err_v = sum(abs(a - b) for a, b in zip(vis, truth)) / len(xs)
    assert err_v < err_p / 2, (err_p, err_v)
    # ---- 上: 部屋 ----
    st.Panel(30, 92, 900, 130, "① 断面(壁の左は明るく、右は暗い。プローブは 5 個)", color=AMBER)
    root.add("rect", x=R(UX(WALL) - 5), y=96, width=10, height=122, fill="#475569")
    sc.Text(root, UX(WALL) + 12, 114, "壁", size=13, fill="#475569")
    root.add("rect", x=36, y=100, width=14, height=114, fill=AMBER)
    sc.Text(root, 60, 114, "窓(光が入る)", size=12, fill="#92400e")
    for k, p in enumerate(probes):
        root.add("circle", cx=R(UX(p)), cy=185, r=14, fill=Mix("#0f172a", "#fde68a", min(1.0, ep[k])), stroke="#334155", stroke_width=2)
        sc.Text(root, R(UX(p)), 213, "%.2f" % ep[k], size=11, weight=700, fill=MUTED, anchor="middle")
    st.Text(40, 236, "プローブの明るさ(丸の色と数字)", size=12, weight=500, fill=MUTED)
    # ---- 下: 曲線 ----
    st.Panel(30, 262, 900, 190, "② 横軸の位置での明るさ", color=BLUE)
    ay0, ah = 275.0, 150.0
    ymax = 1.25 * max(ep)
    AY = lambda v: ay0 + ah - min(v, ymax) / ymax * ah
    root.add("rect", x=R(UX(WALL) - 5), y=ay0, width=10, height=ah, fill="#94a3b8", opacity=0.35)
    def Poly(vals, col, dash=None, width=3):
        pts = " ".join("%s,%s" % (R(UX(x)), R(AY(v))) for x, v in zip(xs, vals))
        # 壁で線を切る
        d = ""
        for k, (x, v) in enumerate(zip(xs, vals)):
            cmd = "M" if (k == 0 or (xs[k - 1] < WALL < x)) else "L"
            d += "%s%s,%s " % (cmd, R(UX(x)), R(AY(v)))
        extra = {"stroke_dasharray": dash} if dash else {}
        return root.add("path", d=d, fill="none", stroke=col, stroke_width=width, opacity=1, **extra)
    p_true = Poly(truth, GREEN, "7 5", 3)
    p_plain = Poly(plain, RED, None, 3.5)
    p_vis = Poly(vis, BLUE, None, 3.5)
    p_plain.Set(0, "opacity", 0)
    p_vis.Set(0, "opacity", 0)
    t_a, t_b, t_c = 1.0, 6.0, 11.0
    p_plain.Set(t_a, "opacity", 1)
    p_vis.Set(t_b, "opacity", 1)
    st.Legend(46, 444, [(GREEN, "正解"), (RED, "普通の補間"), (BLUE, "可視性つき補間")])
    # 動く点
    dot_room = root.add("circle", cx=R(UX(xs[0])), cy=185, r=5, fill=PURPLE)
    d_true = root.add("circle", cx=R(UX(xs[0])), cy=R(AY(truth[0])), r=5, fill=GREEN)
    d_plain = root.add("circle", cx=R(UX(xs[0])), cy=R(AY(plain[0])), r=5, fill=RED, opacity=0)
    d_vis = root.add("circle", cx=R(UX(xs[0])), cy=R(AY(vis[0])), r=5, fill=BLUE, opacity=0)
    Tspan = (t_a, t_c - 0.8)
    n = len(xs)
    keys = lambda f: [(Tspan[0] + (Tspan[1] - Tspan[0]) * k / (n - 1), UX(xs[k]), f(k)) for k in range(n)]
    Track(dot_room, [(t, x, 185) for t, x, y in keys(lambda k: 0)])
    Track(d_true, keys(lambda k: AY(truth[k])))
    Track(d_plain, keys(lambda k: AY(plain[k])))
    Track(d_vis, keys(lambda k: AY(vis[k])))
    d_plain.Show(t_a)
    d_vis.Show(t_b)
    pl_l = Interp(11.2, False)
    pl_r = Interp(12.8, False)
    vl_l = Interp(11.2, True)
    vl_r = Interp(12.8, True)
    tr_l, tr_r = E(11.2), E(12.8)
    st.Box(t_c, 30, 468, 900, 56, [("壁のすぐ右(x=12.8): 正解 %.2f / 普通 %.2f(光が漏れる)/ 可視性つき %.2f" % (tr_r, pl_r[0], vl_r[0]), 14, "#1e3a8a"), ("壁のすぐ左(x=11.2): 正解 %.2f / 普通 %.2f(暗く引っ張られる)/ 可視性つき %.2f" % (tr_l, pl_l[0], vl_l[0]), 14, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 536, [(0.0, t_a, "プローブは離れた点にだけ置く。間の明るさは補間で作る"), (t_a, t_b, "普通の補間(赤): 壁の向こうのプローブも混ぜるので、壁際で光が漏れる"), (t_b, t_c, "可視性つき(青): 壁で見えないプローブは、重みを 0 にする"), (t_c, 99, "平均のずれ: 普通 %.3f → 可視性つき %.3f" % (err_p, err_v))], size=14, fill=MUTED, weight=500)
    st.Note(t_a, "補間", "普通の補間。平均のずれ %.3f" % err_p)
    st.Note(t_b, "補間", "可視性つき。平均のずれ %.3f" % err_v)
    return Build(st, name, "graphics/gi/probes/interpolation.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 13.0, 16.0])


NAMES = ["probe-bilinear"]
FIGS = [ProbeBilinear]


class Lcg:
    def __init__(self, seed):
        self.s = seed

    def U(self):
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.s / 4294967296.0


def RestirReservoir():
    name = "restir-reservoir"
    st = Stage(name, "ReSTIR: たくさんの光から、明るさに比例して 1 つだけ選ぶ(リザーバー)", duration=20.0, subtitle="光 16 個のうち、影の光線を飛ばせるのは 1 本だけ。選び方で、結果のばらつきが大きく変わる")
    sc, root = st.scene, st.root
    N, M = 16, 8
    c = [0.2, 0.3, 0.2, 0.4, 5.0, 0.3, 0.2, 0.3, 0.3, 3.5, 0.2, 0.2, 0.3, 0.4, 0.2, 0.3]
    vis = [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]
    truth = sum(ci * vi for ci, vi in zip(c, vis))

    def TrialUniform(rng):
        j = int(rng.U() * N) % N
        return N * c[j] * vis[j]

    def TrialRis(rng):
        cand = [int(rng.U() * N) % N for _ in range(M)]
        ws = [c[j] * N for j in cand]
        tot = sum(ws)
        r = rng.U() * tot
        acc = 0.0
        sel = cand[-1]
        for j, w in zip(cand, ws):
            acc += w
            if r <= acc:
                sel = j
                break
        return (tot / M) * vis[sel] * 1.0 * (c[sel] / c[sel]), cand, sel

    # 統計(2000 回)
    T = 2000
    ru, rr = Lcg(12345), Lcg(98765)
    eu = [TrialUniform(ru) for _ in range(T)]
    er = [TrialRis(rr)[0] for _ in range(T)]
    mean = lambda a: sum(a) / len(a)
    rms = lambda a: math.sqrt(sum((x - truth) ** 2 for x in a) / len(a))
    rel_u, rel_r = rms(eu) / truth, rms(er) / truth
    assert rel_r < rel_u, (rel_u, rel_r)
    # ---- 左: 16 個の光 ----
    st.Panel(30, 92, 480, 220, "16 個の光(棒 = 影を無視した明るさ)", color=AMBER)
    bw = 26.0
    base = 288.0
    sc_h = 150 / 5.0
    for i in range(N):
        x = 44 + i * 29.5
        root.add("rect", x=R(x), y=R(base - c[i] * sc_h), width=bw, height=R(c[i] * sc_h), fill=("#fbbf24" if vis[i] else "#cbd5e1"), stroke="#f59e0b" if vis[i] else "#94a3b8", stroke_width=1.5)
        sc.Text(root, R(x + bw / 2), base + 14, str(i + 1), size=10, weight=500, fill=MUTED, anchor="middle")
    st.Legend(44, 114, [("#fbbf24", "光が届く"), ("#cbd5e1", "影になる(隠れている)")])
    st.Text(44, 136, "正解 = 届く光の合計 = %.1f" % truth, size=14, fill=GREEN)
    # ---- 3 回の試行 ----
    rng = Lcg(7)
    trials = []
    while len(trials) < 3:
        val, cand, sel = TrialRis(rng)
        trials.append((val, cand, sel))
    t0, dt, per = 1.0, 0.28, 3.4
    cand_frames = []
    for k, (val, cand, sel) in enumerate(trials):
        ts = t0 + k * per
        # リザーバーの経過(逐次選択)
        cur = None
        wsum = 0.0
        r2 = Lcg(1000 + k)
        picks = []
        for step, j in enumerate(cand):
            w = c[j] * N
            wsum += w
            if cur is None or r2.U() < w / wsum:
                cur = j
            picks.append(cur)
        # 最終の選択は TrialRis と同じ結果に合わせる(表示は逐次版の最後を使うため、推定値は表示側で再計算)
        sel_shown = picks[-1]
        est = (sum(c[j] * N for j in cand) / M) * vis[sel_shown]
        for step, j in enumerate(cand):
            t = ts + step * dt
            x = 44 + j * 29.5
            fr = root.add("rect", x=R(x - 2), y=R(base - c[j] * sc_h - 4), width=bw + 4, height=R(c[j] * sc_h + 8), fill="none", stroke=PURPLE, stroke_width=3, opacity=0)
            fr.Show(t, t + dt)
            pk = root.add("path", d="M%s,%s l-8,-14 l16,0 z" % (R(44 + picks[step] * 29.5 + bw / 2), R(base + 24)), fill=RED, opacity=0)
            pk.Show(t, t + dt if step < M - 1 else ts + per - 0.3)
        sc.Text(root, 560, 130 + k * 66, "試行 %d" % (k + 1), size=15, fill=PURPLE, opacity=0).Show(ts, t0 + (k + 1) * per - 0.2 if k < 2 else None)
        g = root.add("g", opacity=0)
        g.Show(ts + M * dt, ts + per if k < 2 else None)
        sc.Text(g, 560, 152 + k * 66, "候補 %d 個の合計 %.1f → 選んだ光 #%d(%s)" % (M, sum(c[j] * N for j in cand) / N, sel_shown + 1, "届く" if vis[sel_shown] else "影"), size=13, weight=500, fill=TEXT)
        sc.Text(g, 560, 172 + k * 66, "推定 = %.1f(正解 %.1f)" % (est, truth), size=15, fill=(GREEN if abs(est - truth) < 0.5 * truth else RED))
    # ---- 右: 統計 ----
    t_stat = t0 + 3 * per + 0.6
    st.Panel(30, 332, 900, 168, "2000 回ためしたときの、正解からのずれ(小さいほど良い)", color=BLUE)
    for r_, (lab, rel, col) in enumerate([("光を 1 つ、でたらめに選ぶ", rel_u, RED), ("ReSTIR: 8 個の候補から、明るさに比例して 1 つ選ぶ", rel_r, BLUE)]):
        y = 372 + r_ * 54
        sc.Text(root, 50, y + 20, lab, size=14, fill=col)
        w = min(480, rel * 130)
        b = root.add("rect", x=420, y=y, width=1, height=28, fill=col, opacity=0.85)
        b.Set(t_stat, "width", 1)
        b.Ramp(t_stat, t_stat + 1.6, "width", R(w))
        sc.Text(root, 420 + w + 10, y + 21, "ずれ %.0f%%" % (rel * 100), size=15, fill=col, opacity=0).Show(t_stat + 1.6)
    st.Box(t_stat + 2.4, 600, 108, 330, 190 - 62, [("影の光線は、どちらも 1 本だけ", 15, "#1e3a8a"), ("ReSTIR のずれは、ざっと %.1f 分の 1" % (rel_u / rel_r), 15, "#166534"), ("(明るい光 #5、#10 を、高い確率で選べる)", 12, MUTED)], BLUE, "#eff6ff") if False else None
    st.Text(50, 485, "ずれ = 2000 回の推定値の、二乗平均の平方根 ÷ 正解", size=12, weight=500, fill=MUTED)
    st.Caption(30, 530, [(0.0, t0, "光は 16 個。影の光線を飛ばせるのは 1 本だけ"), (t0, t_stat, "候補を 1 つずつ受け取り、明るさに比例した確率で「選択中」を入れ替える"), (t_stat, 99, "明るい光を選びやすいので、同じ 1 本でも、ばらつきが大幅に減る")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ReSTIR", "候補 %d 個から 1 つ選ぶ試行を 3 回見せる" % M)
    st.Note(t_stat, "ReSTIR", "2000 回: でたらめ選び ずれ %.0f%% / ReSTIR ずれ %.0f%%" % (rel_u * 100, rel_r * 100))
    return Build(st, name, "graphics/gi/rt-gi/restir.md", BEFORE, [1.5, 3.0, 5.0, 8.0, 12.0, 18.0])


NAMES += ["restir-reservoir"]
FIGS += [RestirReservoir]
