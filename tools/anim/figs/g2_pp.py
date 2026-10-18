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
