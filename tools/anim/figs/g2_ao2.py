import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_ao import Profile  # noqa: E402

BEFORE = "## よくあるミス"


def TrueAo(h, i, rad):
    """断面で、全方向を細かく調べた「本当の」AO(余弦で重み付け)。"""
    px, pz = i + 0.5, h[i]
    n = len(h)
    vis = tot = 0.0
    for d in range(1, 180):
        phi = math.radians(d - 0.5)
        w = math.sin(phi)
        tot += w
        ok = True
        t = 0.02
        while t < rad:
            x, z = px + t * math.cos(phi), pz + t * math.sin(phi)
            c = int(math.floor(x))
            if 0 <= c < n and h[c] > z + 1e-9 and x >= 0:
                ok = False
                break
            t += 0.02
        if ok:
            vis += w
    return vis / tot


def HbaoHorizon():
    name = "hbao-horizon"
    st = Stage(name, "HBAO: 左右に進みながら「いちばん高い見上げ角(水平線)」を探して、AO を決める", duration=18.0, subtitle="同じ断面で、SSAO(サンプル 8 個)と比べる。正解は、全方向を細かく調べた値")
    sc, root = st.scene, st.root
    h = Profile()
    n = len(h)
    cs, ox, oy, zs = 20.0, 40.0, 330.0, 44.0
    RAD, STEPS, DS = 3.5, 7, 0.5
    focus = 10
    X = lambda x: ox + x * cs
    Z = lambda z: oy - z * zs
    px, pz = focus + 0.5, h[focus]
    st.Panel(30, 90, 490, 274, "① 左右に 0.5 ずつ進んで、見上げ角を調べる", color=BLUE)
    for i in range(n):
        if h[i] > 0:
            root.add("rect", x=R(ox + i * cs), y=R(oy - h[i] * zs), width=cs, height=R(h[i] * zs), fill="#cbd5e1", stroke="#94a3b8", stroke_width=1)
    root.add("line", x1=ox, y1=oy, x2=ox + n * cs, y2=oy, stroke="#94a3b8", stroke_width=2)
    root.add("circle", cx=R(X(px)), cy=R(Z(pz)), r=8, fill=INK)
    st.Text(X(px) - 8, Z(pz) + 24, "調べるピクセル", size=13, anchor="middle")
    t0, dt = 1.2, 0.42

    def Angles(side):
        best, rows = 0.0, []
        for k in range(1, STEPS + 1):
            s = k * DS
            x = px + side * s
            c = int(math.floor(x))
            hz = h[c] if 0 <= c < n else 0.0
            ang = math.atan2(max(0.0, hz - pz), s)
            best = max(best, ang)
            rows.append((k, c, hz, ang, best))
        return rows

    rows_r, rows_l = Angles(+1), Angles(-1)
    hR, hL = rows_r[-1][4], rows_l[-1][4]
    ao_h = (math.cos(hL) + math.cos(hR)) / 2
    truth_f = TrueAo(h, focus, RAD)
    # 描画: 順に(右 7 歩 → 左 7 歩)
    seq = [(+1, r) for r in rows_r] + [(-1, r) for r in rows_l]
    for q, (side, (k, c, hz, ang, best)) in enumerate(seq):
        t = t0 + q * dt
        sx = px + side * k * DS
        g = root.add("g", opacity=0)
        g.Show(t, t + dt if q < len(seq) - 1 else None)
        g.add("line", x1=R(X(px)), y1=R(Z(pz)), x2=R(X(sx)), y2=R(Z(max(pz, hz))), stroke=AMBER, stroke_width=1.5, stroke_dasharray="4 4")
        g.add("circle", cx=R(X(sx)), cy=R(Z(max(pz, hz))), r=5, fill=(RED if hz > pz else GREEN), stroke="#ffffff", stroke_width=1.5)
        # 最大の見上げ角の線(水平線)
        L = 3.2
        g.add("line", x1=R(X(px)), y1=R(Z(pz)), x2=R(X(px + side * L * math.cos(best))), y2=R(Z(pz + L * math.sin(best))), stroke=RED, stroke_width=3.5)
    st.Text(40, 350, "赤い線 = ここまでで一番高い見上げ角(水平線)", size=12, weight=500, fill=RED)
    # ---- 右: 表 ----
    st.Panel(550, 90, 380, 274, "② 進むたびの見上げ角", color=PURPLE)
    st.Text(566, 114, "高さ(深度から読む)→ 見上げ角 → これまでの最大", size=12, weight=500, fill=MUTED)
    for q, (side, (k, c, hz, ang, best)) in enumerate(seq):
        tt = t0 + q * dt
        col = 0 if q < STEPS else 1
        y = 138 + (q % STEPS) * 25
        xx = 566 + col * 182
        g = root.add("g", opacity=0)
        g.Show(tt)
        sc.Text(g, xx, y, ("→" if side > 0 else "←") + "%d" % k, size=12, weight=700, fill=PURPLE)
        sc.Text(g, xx + 26, y, "高さ %.1f" % hz, size=12, weight=500, fill=TEXT)
        sc.Text(g, xx + 84, y, "%2d°" % round(math.degrees(ang)), size=13, weight=700, fill=(RED if ang > 0 else GREEN))
        sc.Text(g, xx + 126, y, "最大 %2d°" % round(math.degrees(best)), size=12, weight=700, fill=INK)
    st.Text(566, 330, "深度の読み込み:", size=14)
    st.Counter(690, 332, [(t0 + q * dt, q + 1) for q in range(len(seq))], size=20, fill=PURPLE)
    t_calc = t0 + len(seq) * dt
    sc.Text(root, 566, 352, "AO = (cos %d° + cos %d°)/2 = %.3f" % (round(math.degrees(hL)), round(math.degrees(hR)), ao_h), size=15, fill=PURPLE, opacity=0).Show(t_calc)
    # ---- 下: 全列 ----
    st.Text(30, 392, "③ 全部の列で同じことをして、SSAO(8 サンプル)と、正解とを比べる", size=14)
    # SSAO 計算(g2_ao と同じ規則)
    K = 8
    golden = 0.6180339887

    def Ssao(i):
        qx, qz = i + 0.5, h[i]
        occ = 0
        for k in range(K):
            ang = math.pi * (k + 0.5) / K
            r = RAD * (0.35 + 0.65 * ((k * golden) % 1.0))
            sx, sz = qx + r * math.cos(ang), qz + r * math.sin(ang)
            c = max(0, min(n - 1, int(math.floor(sx))))
            if h[c] > sz + 0.05 and abs(h[c] - qz) < RAD:
                occ += 1
        return 1.0 - occ / K

    def Hbao(i):
        qx, qz = i + 0.5, h[i]
        best = [0.0, 0.0]
        for si, side in enumerate((+1, -1)):
            for k in range(1, STEPS + 1):
                s = k * DS
                c = int(math.floor(qx + side * s))
                hz = h[c] if 0 <= c < n else 0.0
                best[si] = max(best[si], math.atan2(max(0.0, hz - qz), s))
        return (math.cos(best[0]) + math.cos(best[1])) / 2

    tru = [TrueAo(h, i, RAD) for i in range(n)]
    hb = [Hbao(i) for i in range(n)]
    ss = [Ssao(i) for i in range(n)]
    e_h = sum(abs(a - b) for a, b in zip(hb, tru)) / n
    e_s = sum(abs(a - b) for a, b in zip(ss, tru)) / n
    assert e_h < e_s, (e_h, e_s)
    rows = [("正解", tru, GREEN, 404), ("HBAO(14 回読む)", hb, BLUE, 430), ("SSAO(8 回読む)", ss, RED, 456)]
    t_sw, dts = t_calc + 1.0, 0.15
    for lab, vals, col, y in rows:
        st.Text(30, y + 15, lab, size=12, fill=col)
        grid = Grid(st, 200, y, n, 1, cs, base="#e5e7eb", stroke="#94a3b8")
        for i in range(n):
            grid.Paint(i, 0, t_sw + i * dts, Gray(0.1 + 0.9 * vals[i]))
        grid.Flush()
    st.Text(692, 420, "HBAO の読み込み:", size=13)
    st.Counter(830, 422, [(t_sw + i * dts, (i + 1) * STEPS * 2) for i in range(n)], size=18, fill=BLUE)
    st.Text(692, 446, "SSAO の読み込み:", size=13)
    st.Counter(830, 448, [(t_sw + i * dts, (i + 1) * K) for i in range(n)], size=18, fill=RED)
    t_end = t_sw + n * dts + 0.5
    st.Box(t_end, 692, 460, 238, 60, [("正解とのずれ(平均)", 12, MUTED), ("HBAO %.3f / SSAO %.3f" % (e_h, e_s), 15, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 532, [(0.0, t0, "断面で、1 つのピクセルから左右に進む"), (t0, t_calc, "進むたびに、見上げ角の最大値(水平線)を更新する"), (t_calc, t_sw, "左右の水平線から、光が見える角度の広さ(AO)が決まる"), (t_sw, t_end, "全部の列で繰り返し、SSAO と正解を並べる"), (t_end, 99, "HBAO は「方向」を調べるので、同じ回数なら正解に近い")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "HBAO", "左右に %d 歩ずつ進む(読み込み %d 回)" % (STEPS, 2 * STEPS))
    st.Note(t_end, "HBAO", "正解とのずれ: HBAO %.3f / SSAO %.3f" % (e_h, e_s))
    return Build(st, name, "graphics/ao/hbao.md", BEFORE, [2.0, 4.0, 6.5, 9.0, 12.0, 17.0])


NAMES = ["hbao-horizon"]
FIGS = [HbaoHorizon]


class Lcg:
    def __init__(self, seed):
        self.s = seed

    def U(self):
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.s / 4294967296.0


def BilateralBlur():
    name = "bilateral-blur"
    st = Stage(name, "バイラテラル ブラー: 深度が近い画素だけを平均して、輪郭をにじませずにノイズを消す", duration=18.0, subtitle="1 列 48 画素。左は手前(深度 1)、右は奥(深度 3)。AO にノイズが乗っている")
    sc, root = st.scene, st.root
    N, CW, X0 = 48, 17.0, 60.0
    EDGE = 24
    depth = [1.0 if i < EDGE else 3.0 for i in range(N)]
    clean = [0.85 if i < EDGE else 0.40 for i in range(N)]
    rng = Lcg(2024)
    noisy = [max(0.0, min(1.0, clean[i] + (rng.U() - 0.5) * 0.6)) for i in range(N)]
    RAD, SIG, SIGZ = 5, 2.5, 0.35

    def Blur(bilateral):
        out = []
        for i in range(N):
            num = den = 0.0
            for d in range(-RAD, RAD + 1):
                j = i + d
                if j < 0 or j >= N:
                    continue
                w = math.exp(-d * d / (2 * SIG * SIG))
                if bilateral:
                    w *= math.exp(-((depth[i] - depth[j]) ** 2) / (2 * SIGZ * SIGZ))
                num += w * noisy[j]
                den += w
            out.append(num / den)
        return out

    gau, bil = Blur(False), Blur(True)
    rms = lambda a: math.sqrt(sum((x - y) ** 2 for x, y in zip(a, clean)) / N)
    edge_idx = range(EDGE - 4, EDGE + 4)
    e_edge = lambda a: sum(abs(a[i] - clean[i]) for i in edge_idx) / 8
    r_n, r_g, r_b = rms(noisy), rms(gau), rms(bil)
    ed_g, ed_b = e_edge(gau), e_edge(bil)
    assert r_b < r_n and ed_b < ed_g, (r_n, r_g, r_b, ed_g, ed_b)
    rows = [("ノイズのある AO", noisy, GRAY, 142), ("普通のぼかし(ガウス)", gau, RED, 192), ("バイラテラル(深度も見る)", bil, BLUE, 242), ("正解(ノイズなし)", clean, GREEN, 292)]
    st.Text(X0, 96, "深度(濃い = 手前 / 薄い = 奥)", size=13, fill=MUTED)
    dg = Grid(st, X0, 102, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(N):
        dg.Paint(i, 0, 0.3, Mix("#334155", "#cbd5e1", (depth[i] - 1.0) / 2.0))
    dg.Flush()
    t0, dts = 1.0, 0.16
    grids = []
    for lab, vals, col, y in rows:
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(N):
            tt = 0.3 if vals is noisy or vals is clean else t0 + i * dts
            g.Paint(i, 0, tt, Gray(0.08 + 0.92 * vals[i]))
        g.Flush()
        grids.append(g)
    # 走査枠
    mk = root.add("rect", x=R(X0), y=136, width=CW, height=173, fill="none", stroke=AMBER, stroke_width=3, opacity=0)
    for i in range(N):
        t = t0 + i * dts
        mk.Set(t, "x", R(X0 + i * CW))
        mk.Set(t, "opacity", 1)
    mk.Set(t0 + N * dts, "opacity", 0)
    # 輪郭の線
    root.add("line", x1=R(X0 + EDGE * CW), y1=96, x2=R(X0 + EDGE * CW), y2=314, stroke=RED, stroke_width=2, stroke_dasharray="5 4")
    sc.Text(root, X0 + EDGE * CW, 332, "深度の段差(輪郭)", size=12, weight=700, fill=RED, anchor="middle")
    # 重みのインセット(輪郭のすぐ左の画素 i = EDGE-2)
    ic = EDGE - 2
    t_in = t0 + ic * dts + 0.1
    ix, iy = 60.0, 350.0
    st.Panel(ix, iy, 420, 150, "輪郭の近くの画素(画素 %d)が使う重み" % (ic + 1), color=PURPLE)
    g = root.add("g", opacity=0)
    g.Show(t_in + 0.3)
    bwid = 20.0
    for d in range(-RAD, RAD + 1):
        j = ic + d
        wg = math.exp(-d * d / (2 * SIG * SIG))
        wb = wg * math.exp(-((depth[ic] - depth[j]) ** 2) / (2 * SIGZ * SIGZ))
        x = ix + 20 + (d + RAD) * 36
        g.add("rect", x=R(x), y=R(iy + 120 - wg * 80), width=bwid, height=R(wg * 80), fill="#fca5a5", opacity=0.9)
        g.add("rect", x=R(x + bwid - 2), y=R(iy + 120 - wb * 80), width=bwid - 4, height=R(max(wb * 80, 0.5)), fill="#3b82f6", opacity=0.95)
        sc.Text(g, R(x + bwid), R(iy + 138), str(j + 1), size=10, weight=500, fill=(RED if depth[j] != depth[ic] else MUTED), anchor="middle")
    sc.Text(g, ix + 210, iy + 40, "赤 = ガウス / 青 = バイラテラル", size=11, weight=700, fill=MUTED, anchor="middle")
    st.Text(520, 372, "輪郭の向こう側(赤い番号)の重み:", size=13, fill=TEXT)
    far_g = sum(math.exp(-d * d / (2 * SIG * SIG)) for d in range(-RAD, RAD + 1) if depth[ic + d] != depth[ic])
    far_b = sum(math.exp(-d * d / (2 * SIG * SIG)) * math.exp(-((depth[ic] - depth[ic + d]) ** 2) / (2 * SIGZ * SIGZ)) for d in range(-RAD, RAD + 1) if depth[ic + d] != depth[ic])
    near = sum(math.exp(-d * d / (2 * SIG * SIG)) for d in range(-RAD, RAD + 1) if depth[ic + d] == depth[ic])
    sc.Text(root, 520, 396, "ガウス %.0f%% → バイラテラル %.1f%%" % (100 * far_g / (far_g + near), 100 * far_b / (far_b + near)), size=17, fill=PURPLE, opacity=0).Show(t_in + 0.6)
    t_end = t0 + N * dts + 0.6
    st.Box(t_end, 520, 416, 410, 100, [("正解とのずれ(全体): ガウス %.3f / バイラテラル %.3f" % (r_g, r_b), 14, "#1e3a8a"), ("輪郭の近く(8 画素): ガウス %.3f / バイラテラル %.3f" % (ed_g, ed_b), 14, "#991b1b"), ("ガウスは輪郭を越えて混ぜるので、段差がにじむ", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ノイズのある AO を、ぼかして消したい"), (t0, t0 + N * dts, "左から右へ、各画素の周り 11 画素を、重み付きで平均する"), (t0 + N * dts, 99, "バイラテラルは、深度が違う画素の重みを 0 に近づけるので、輪郭が保たれる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ぼかし", "ガウスとバイラテラルを同時に走査(半径 %d)" % RAD)
    st.Note(t_end, "ぼかし", "輪郭付近のずれ: ガウス %.3f / バイラテラル %.3f" % (ed_g, ed_b))
    return Build(st, name, "graphics/ao/filtering/bilateral-blur.md", BEFORE, [1.5, 4.0, 6.0, 9.0, 12.0, 17.0])


NAMES += ["bilateral-blur"]
FIGS += [BilateralBlur]
