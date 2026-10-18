import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402

BEFORE = "## よくあるミス"


def Scene1D():
    nx = 64
    zs = [9.0] * nx
    for i in range(14, 18):
        zs[i] = 4.6
    for i in range(30, 33):
        zs[i] = 5.4
    for i in range(52, 64):
        zs[i] = 2.6
    return nx, zs


def SsrHizSteps():
    name = "ssr-hiz-steps"
    st = Stage(name, "SSR の光線追跡: 1 マスずつ進める方法と、Hi-Z で大きく飛ばす方法", duration=14.0, subtitle="同じ深度、同じ光線。当たる場所が同じでも、深度バッファを読む回数は大きく違う")
    sc, root = st.scene, st.root
    nx, zs = Scene1D()
    X0, CSX, TOPS = 50.0, 13.0, [100.0, 288.0]
    ZSC = 13.0
    x0, z0, slope = 2.0, 1.0, 0.035
    zr = lambda x: z0 + slope * (x - x0)
    LV = 3
    mins = [list(zs)]
    for L in range(1, LV + 1):
        prev = mins[-1]
        mins.append([min(prev[2 * c], prev[2 * c + 1]) for c in range(len(prev) // 2)])

    # --- 計算 ---
    lin = []
    hit_lin = None
    for c in range(int(x0), nx):
        lin.append(c)
        if zr(c + 1) >= zs[c]:
            hit_lin = c
            break
    hiz = []
    x, L = x0, 0
    hit_hiz = None
    while x < nx:
        size = 2 ** L
        cell = int(math.floor(x / size))
        xe = (cell + 1) * size
        if zr(xe) < mins[L][cell]:
            hiz.append((cell, L, "skip", x, xe))
            x = xe
            L = min(L + 1, LV)
        elif L == 0:
            hiz.append((cell, L, "hit", x, xe))
            hit_hiz = cell
            break
        else:
            hiz.append((cell, L, "down", x, xe))
            L -= 1
    assert hit_lin == hit_hiz, (hit_lin, hit_hiz)
    n_lin, n_hiz = len(lin), len(hiz)
    assert n_hiz < n_lin / 2

    Z = lambda top, z: top + z * ZSC
    X = lambda c: X0 + c * CSX
    heads = [("線形に追跡(1 マスずつ)", RED), ("Hi-Z で追跡(深度の最小値のミップで飛ばす)", BLUE)]
    lcol = ["#22c55e", "#3b82f6", "#a855f7", "#f97316"]
    for p in range(2):
        top = TOPS[p]
        st.Panel(30, top - 4, 900, 150, heads[p][0], color=heads[p][1])
        # 地形(中身が詰まった所)
        pts = ["%s,%s" % (R(X(0)), R(top + 140))]
        for c in range(nx):
            pts.append("%s,%s" % (R(X(c)), R(Z(top, zs[c]))))
            pts.append("%s,%s" % (R(X(c + 1)), R(Z(top, zs[c]))))
        pts.append("%s,%s" % (R(X(nx)), R(top + 140)))
        root.add("polygon", points=" ".join(pts), fill="#cbd5e1", stroke="#94a3b8", stroke_width=1.5)
        # 光線
        root.add("line", x1=R(X(x0)), y1=R(Z(top, zr(x0))), x2=R(X(nx)), y2=R(Z(top, zr(nx))), stroke="#fca5a5", stroke_width=2, stroke_dasharray="6 5")
        root.add("circle", cx=R(X(x0)), cy=R(Z(top, zr(x0))), r=6, fill=INK)
        st.Text(X(x0) + 8, Z(top, zr(x0)) - 8, "光線の出発点", size=12, fill=INK)
    # 線形
    dt_l = 0.085
    top = TOPS[0]
    series = []
    for k, c in enumerate(lin):
        t = 1.0 + k * dt_l
        last = (k == len(lin) - 1)
        col = RED if last else "#22c55e"
        d = root.add("circle", cx=R(X(c + 0.5)), cy=R(Z(top, zr(c + 0.5))), r=(6 if last else 3.5), fill=col, opacity=0)
        d.Show(t)
        series.append((t, k + 1))
    st.Text(500, 84, "深度の読み込み:", size=14)
    st.Counter(640, 86, series, size=20, fill=RED)
    t_lin_end = 1.0 + len(lin) * dt_l
    # Hi-Z
    dt_h = 0.55
    top = TOPS[1]
    series = []
    for k, (cell, L, act, xs, xe) in enumerate(hiz):
        t = 1.0 + k * dt_h
        size = 2 ** L
        a, b = cell * size, (cell + 1) * size
        r = root.add("rect", x=R(X(a)), y=R(top), width=R(size * CSX), height=140, fill=lcol[L], fill_opacity=0.18, stroke=lcol[L], stroke_width=2.5, opacity=0)
        r.Show(t)
        lab = sc.Text(root, R(X(a) + size * CSX / 2), top + 135, ("L%d" % L) if act != "hit" else "命中", size=12, weight=700, fill=lcol[L] if act != "hit" else RED, anchor="middle", opacity=0)
        lab.Show(t)
        d = root.add("circle", cx=R(X(min(xe, nx))), cy=R(Z(top, zr(min(xe, nx)))), r=(6 if act == "hit" else 4), fill=(RED if act == "hit" else lcol[L]), opacity=0)
        d.Show(t)
        series.append((t, k + 1))
    st.Text(500, 272, "深度の読み込み:", size=14)
    st.Counter(640, 274, series, size=20, fill=BLUE)
    t_hiz_end = 1.0 + len(hiz) * dt_h
    # 凡例
    st.Legend(40, 450, [(lcol[0], "L0: 1 マス"), (lcol[1], "L1: 2 マス"), (lcol[2], "L2: 4 マス"), (lcol[3], "L3: 8 マス")])
    t_end = max(t_lin_end, t_hiz_end) + 0.8
    st.Box(t_end, 30, 462, 900, 56, [("命中は同じ(列 %d)。深度の読み込みは 線形 %d 回 → Hi-Z %d 回(約 %.1f 分の 1)" % (hit_lin, n_lin, n_hiz, n_lin / n_hiz), 17, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 532, [(0.0, 1.0, "同じ地形(灰色)に、同じ光線を飛ばす"), (1.0, t_hiz_end, "上: 毎回 1 マス進む。 下: 空いている所は、大きな枠でまとめて飛ばす"), (t_hiz_end, 99, "手前の遮蔽物が無い所を、一気に飛ばせるのが Hi-Z の強み")], size=14, fill=MUTED, weight=500)
    st.Note(1.0, "線形", "1 マスずつ進める。命中まで %d 回" % n_lin)
    st.Note(1.0, "Hi-Z", "枠を大きく飛ばす。命中まで %d 回" % n_hiz)
    return Build(st, name, "graphics/reflections/ssr-hiz.md", BEFORE, [1.5, 3.5, 5.5, 8.0, 10.0, 13.0])


NAMES = ["ssr-hiz-steps"]
FIGS = [SsrHizSteps]
