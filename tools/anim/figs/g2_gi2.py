import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== Voxel cone tracing
def VoxelConeTrace():
    name = "voxel-cone-trace"
    st = Stage(name, "ボクセル コーン トレーシング: 太る円錐で進み、遠いほど「粗いボクセル」を読む", duration=22.0, subtitle="2 次元のボクセル(24×12)。光線ではなく、広がる円錐を 1 本飛ばして、周りの色と遮蔽を一度に集める")
    sc, root = st.scene, st.root
    NX, NY = 24, 12
    CS = 24.0
    OX, OY = 40.0, 384.0                      # 左下
    solid = {}
    for i in range(NX):
        solid[(i, 0)] = (0.80, 0.80, 0.70)     # 床(明るい灰)
    for i in (17, 18):
        for j in range(1, 8):
            solid[(i, j)] = (0.95, 0.20, 0.18)   # 赤い壁
    for i in (11, 12):
        for j in (1, 2):
            solid[(i, j)] = (0.95, 0.85, 0.20)   # 黄色い箱
    # ミップ(2×2 ずつ、割合と色の平均)
    def MipLevel(L):
        s = 2 ** L
        cells = {}
        for ci in range(int(math.ceil(NX / s))):
            for cj in range(int(math.ceil(NY / s))):
                a, c = 0.0, [0.0, 0.0, 0.0]
                for di in range(s):
                    for dj in range(s):
                        v = solid.get((ci * s + di, cj * s + dj))
                        if v:
                            a += 1
                            for k in range(3):
                                c[k] += v[k]
                if a:
                    cells[(ci, cj)] = (a / (s * s), [c[k] / a for k in range(3)])
        return cells

    mips = [MipLevel(L) for L in range(4)]

    def Sample(x, y, L):
        s = 2 ** L
        cell = mips[L].get((int(math.floor(x / s)), int(math.floor(y / s))))
        return cell if cell else (0.0, [0.0, 0.0, 0.0])

    half = math.radians(28.0)
    P = (7.0, 1.02)

    def Trace(angle):
        ang = math.radians(angle)
        dv = (math.cos(ang), math.sin(ang))
        t, alpha, col = 1.0, 0.0, [0.0, 0.0, 0.0]
        steps = []
        while t < 22 and alpha < 0.95:
            d = max(1.0, 2 * t * math.tan(half))
            L = min(3, int(round(math.log2(d))))
            x, y = P[0] + dv[0] * t, P[1] + dv[1] * t
            if x < 0 or x >= NX or y < 0 or y >= NY:
                break
            a, c = Sample(x, y, L)
            a_eff = min(1.0, a * 1.3)
            for k in range(3):
                col[k] += (1 - alpha) * a_eff * c[k]
            alpha += (1 - alpha) * a_eff
            steps.append((x, y, d, L, a_eff, alpha, list(col)))
            t += max(1.0, d * 0.5)
        return steps, alpha, col

    angles = [8.0, 32.0, 62.0]
    traces = [Trace(a) for a in angles]
    assert len(traces[0][0]) <= 12 and traces[0][1] > 0.5
    st.Panel(30, 96, NX * CS + 20, NY * CS + 30, "① ボクセル(色つきが壁・床・箱)と、円錐", color=BLUE)
    for (i, j), c in solid.items():
        root.add("rect", x=R(OX + i * CS), y=R(OY - (j + 1) * CS), width=CS - 1, height=CS - 1, fill=Hex([255 * v for v in c]), stroke="#ffffff", stroke_width=0.8)
    root.add("circle", cx=R(OX + P[0] * CS), cy=R(OY - P[1] * CS), r=7, fill=INK)
    sc.Text(root, OX + P[0] * CS, OY - P[1] * CS + 22, "調べる点(床の上)", size=12, weight=700, fill=INK, anchor="middle")
    t0, per = 1.0, 6.8
    for m, (steps, alpha, col) in enumerate(traces):
        ang = math.radians(angles[m])
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        # 円錐の輪郭
        L = max(s[0] - P[0] for s in steps) * 1.15 if steps else 10
        for sgn in (-1, 1):
            g.add("line", x1=R(OX + P[0] * CS), y1=R(OY - P[1] * CS), x2=R(OX + (P[0] + math.cos(ang + sgn * half) * 14) * CS), y2=R(OY - (P[1] + math.sin(ang + sgn * half) * 14) * CS), stroke="#93c5fd", stroke_width=1.5, stroke_dasharray="5 4")
        for k, (x, y, d, Lv, a, al, c) in enumerate(steps):
            tt = t0 + m * per + 0.6 + k * 0.5
            n = g.add("g", opacity=0)
            n.Show(tt)
            n.add("circle", cx=R(OX + x * CS), cy=R(OY - y * CS), r=R(d * CS / 2), fill="#60a5fa", fill_opacity=0.14, stroke="#3b82f6", stroke_width=1.5)
            n.add("circle", cx=R(OX + x * CS), cy=R(OY - y * CS), r=4, fill=(RED if a > 0.05 else GREEN))
        sc.Text(g, 560, 120, "円錐 %d(角度 %d°)" % (m + 1, angles[m]), size=16, weight=700, fill=PURPLE)
    # 右: 数字
    X1 = 690
    st.Panel(X1, 96, 240, 330, "② 進むたびの読み込み", color=PURPLE)
    for m, (steps, alpha, col) in enumerate(traces):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 2 else None)
        for k, (x, y, d, Lv, a, al, c) in enumerate(steps):
            tt = t0 + m * per + 0.6 + k * 0.5
            yy = 130 + k * 21
            n = g.add("g", opacity=0)
            n.Show(tt)
            sc.Text(n, X1 + 12, yy, "歩 %d: 幅 %.1f → ミップ %d" % (k + 1, d, Lv), size=11, weight=700, fill=TEXT)
            sc.Text(n, X1 + 225, yy, "遮蔽 %.2f" % al, size=11, weight=700, fill=(RED if al > 0.5 else MUTED), anchor="end")
        res = Hex([255 * min(1.0, v) for v in col])
        sc.Text(g, X1 + 12, 392, "集めた色:", size=13, weight=700, fill=TEXT)
        g.add("rect", x=X1 + 90, y=376, width=60, height=22, fill=res, stroke="#334155", stroke_width=1.5)
        sc.Text(g, X1 + 160, 392, "遮蔽 %.2f" % alpha, size=13, weight=700, fill=PURPLE)
    st.Text(40, 452, "円錐 1 本あたりの歩数:", size=14)
    st.Counter(240, 456, [(t0 + m * per + 0.6 + len(traces[m][0]) * 0.5, len(traces[m][0])) for m in range(3)], size=22, fill=BLUE)
    t_end = t0 + 3 * per
    steps_total = sum(len(t[0]) for t in traces)
    wide = [t[0][-1][2] for t in traces if t[0]]
    st.Box(t_end - 0.5, 330, 436, 600, 80, [("円錐 3 本で %d 歩。1 歩ごとに、広い範囲を 1 回で読める" % steps_total, 15, "#1e3a8a"), ("最後の幅は %.0f ボクセル。細い光線なら、同じ幅を埋めるのに %.0f 本ずつ必要" % (wide[0], wide[0]), 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "細い光線を何百本も飛ばす代わりに、広がる円錐を数本飛ばす"), (t0, t_end, "遠くなるほど円錐が太くなり、粗い(ぼかした)ボクセルを読む"), (t_end, 99, "遮蔽が十分に溜まったら終わり。壁の赤い色が、床へにじむ")], size=14, fill=MUTED, weight=500)
    for m in range(3):
        st.Note(t0 + m * per, "コーン", "円錐 %d(%d°): %d 歩、遮蔽 %.2f" % (m + 1, angles[m], len(traces[m][0]), traces[m][1]))
    return Build(st, name, "graphics/gi/voxel-gi.md", BEFORE, [1.5, 4.0, 8.0, 12.0, 17.0, 21.0])


# ===================================================================== Radiance cascades
def RadianceCascades():
    name = "radiance-cascades"
    st = Stage(name, "ラディアンス カスケード: 近くは点を細かく、遠くは方向を細かく", duration=22.0, subtitle="16×16 の画面を、4 段のカスケードで調べる。各段の光線の総数は同じで、届く距離が 4 倍ずつ伸びる")
    sc, root = st.scene, st.root
    N0 = 16
    casc = []
    for i in range(4):
        probes = (N0 // 2 ** i) ** 2
        rays = 4 ** (i + 1)
        r0 = 0.0 if i == 0 else 1.0 * 4 ** (i - 1)
        r1 = 1.0 * 4 ** i
        casc.append((i, N0 // 2 ** i, probes, rays, r0, r1, probes * rays))
    assert all(c[6] == 1024 for c in casc)
    naive = N0 * N0 * (N0 * N0)      # 全プローブが、全方向へ、最大距離まで
    total = sum(c[6] for c in casc)
    cols = ["#60a5fa", "#34d399", "#fbbf24", "#f87171"]
    cs = 130.0
    for i, (lv, n, probes, rays, r0, r1, tot) in enumerate(casc):
        x = 40 + i * 225
        y = 110
        t = 1.0 + i * 3.6
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=x, y=y, width=cs + 40, height=cs + 40, fill="#ffffff", stroke=cols[i], stroke_width=2.5, rx=6)
        step = (cs + 40) / n
        for a in range(n):
            for b in range(n):
                g.add("circle", cx=R(x + (a + 0.5) * step), cy=R(y + (b + 0.5) * step), r=min(4.5, step * 0.18), fill=cols[i])
        # 1 つのプローブの、光線
        pcx, pcy = x + (cs + 40) / 2 + step / 2 * (0 if n % 2 == 0 else 0), y + (cs + 40) / 2
        for r_ in range(min(rays, 64)):
            ang = 2 * math.pi * (r_ + 0.5) / rays
            s0 = max(0.0, r0) * (cs / 20) * 0.9
            s1 = max(s0 + 3, r1 * (cs / 20) * 0.9 * (1 if i < 3 else 0.9))
            s1 = min(s1, (cs + 40) / 2 - 2)
            g.add("line", x1=R(pcx + math.cos(ang) * s0), y1=R(pcy + math.sin(ang) * s0), x2=R(pcx + math.cos(ang) * s1), y2=R(pcy + math.sin(ang) * s1), stroke=cols[i], stroke_width=1.3, opacity=0.8)
        sc.Text(g, x, y - 10, "カスケード %d" % i, size=15, weight=700, fill=cols[i])
        sc.Text(g, x, y + cs + 62, "点 %d × 方向 %d = %s 本" % (probes, rays, Fmt(tot)), size=13, weight=700, fill=TEXT)
        sc.Text(g, x, y + cs + 82, "届く距離 %g 〜 %g" % (r0, r1), size=12, weight=500, fill=MUTED)
        sc.Text(g, x, y + cs + 100, "点の間隔 %d、方向 %d 分割" % (2 ** i, rays), size=12, weight=500, fill=MUTED)
    t_e = 1.0 + 4 * 3.6
    st.Text(40, 410, "光線の総数:", size=16)
    series = []
    c_sum = 0
    for i, c in enumerate(casc):
        c_sum += c[6]
        series.append((1.0 + i * 3.6 + 0.3, c_sum))
    st.Counter(150, 414, series, size=26, fill=PURPLE)
    st.Box(t_e - 0.3, 330, 392, 600, 118, [("カスケード 4 段: 光線 %s 本" % Fmt(total), 17, "#1e3a8a"), ("全部の点が、全方向へ、最大距離まで調べる方法: %s 本(約 %d 倍)" % (Fmt(naive), round(naive / total)), 15, "#991b1b"), ("近くは細かい点で、遠くは粗い点でよい。後の段の結果を、前の段に混ぜる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.0, "遠くの光は、細かい位置の違いが、見た目にほとんど効かない"), (1.0, t_e, "段が進むごとに、点は 4 分の 1、方向は 4 倍、届く距離は 4 倍"), (t_e, 99, "どの段も光線の数が同じなので、全体の計算量が、距離に関係なく一定になる")], size=14, fill=MUTED, weight=500)
    for c in casc:
        st.Note(1.0 + c[0] * 3.6, "RC", "カスケード %d: 点 %d × 方向 %d = %d 本、距離 %g〜%g" % (c[0], c[2], c[3], c[6], c[4], c[5]))
    return Build(st, name, "graphics/gi/rt-gi/radiance-cascades.md", BEFORE, [2.0, 5.5, 9.0, 12.5, 17.0, 21.0])


# ===================================================================== SSGI
def SsgiBounce():
    name = "ssgi-bounce"
    st = Stage(name, "SSGI: 画面に見えている色を、周りの画素から集めて、壁の色が床へ「にじむ」", duration=19.0, subtitle="断面。右に赤い壁、床は灰色。床の 1 画素が、周りの見える画素(の明るさと色)を 16 個サンプルして集める")
    sc, root = st.scene, st.root
    NX = 40
    h = [0.0] * NX
    for i in range(30, 40):
        h[i] = 4.0
    wall = (0.90, 0.18, 0.15)
    floor = (0.80, 0.80, 0.78)
    K, RAD = 16, 6.0
    lit = lambda c: [0.9 * v for v in c]   # 直接光で照らされた色

    def Surf(x):
        c = int(math.floor(x))
        if 0 <= c < NX and h[c] > 0:
            return wall
        return floor

    def Gather(i, n_dirs, rad, det=True):
        px, pz = i + 0.5, 0.02
        acc = [0.0, 0.0, 0.0]
        wsum = 0.0
        for k in range(n_dirs):
            ang = math.pi * (k + 0.5) / n_dirs
            w = math.sin(ang)
            wsum += w
            r = rad * (0.4 + 0.6 * ((k * 0.6180339887) % 1.0)) if det else rad
            if n_dirs > 40:
                # 細かい光線: 最初に当たった面
                t = 0.02
                col = None
                while t < rad:
                    x, z = px + t * math.cos(ang), pz + t * math.sin(ang)
                    c = int(math.floor(x))
                    if 0 <= c < NX and h[c] > z:
                        col = lit(wall)
                        break
                    t += 0.02
                if col:
                    for q in range(3):
                        acc[q] += w * col[q]
            else:
                x, z = px + r * math.cos(ang), pz + r * math.sin(ang)
                c = int(math.floor(x))
                if 0 <= c < NX and h[c] > z:
                    for q in range(3):
                        acc[q] += w * lit(wall)[q]
        return [acc[q] / wsum for q in range(3)]

    base = [lit(floor)] * NX
    ssgi = []
    truth = []
    for i in range(NX):
        if h[i] > 0:
            ssgi.append(lit(wall))
            truth.append(lit(wall))
            continue
        g_s = Gather(i, K, RAD)
        g_t = Gather(i, 180, RAD)
        ssgi.append([min(1.0, lit(floor)[q] + floor[q] * 1.0 * g_s[q]) for q in range(3)])
        truth.append([min(1.0, lit(floor)[q] + floor[q] * 1.0 * g_t[q]) for q in range(3)])
    nobounce = [lit(floor) if h[i] == 0 else lit(wall) for i in range(NX)]
    err = lambda a: sum(sum(abs(a[i][q] - truth[i][q]) for q in range(3)) / 3 for i in range(30)) / 30
    e_n, e_s = err(nobounce), err(ssgi)
    assert e_s < e_n, (e_n, e_s)
    cs = 20.0
    ox = 60.0
    st.Panel(30, 96, 840, 150, "① 断面", color=BLUE)
    base_y = 226.0
    for i in range(NX):
        if h[i] > 0:
            root.add("rect", x=R(ox + i * cs), y=R(base_y - h[i] * 24), width=cs - 1, height=R(h[i] * 24), fill=Hex([255 * v for v in wall]))
    root.add("line", x1=ox, y1=base_y, x2=ox + NX * cs, y2=base_y, stroke="#94a3b8", stroke_width=3)
    ex = 26
    px, pz = ex + 0.5, 0.02
    root.add("circle", cx=R(ox + px * cs), cy=R(base_y - pz * 24), r=7, fill=INK)
    sc.Text(root, ox + px * cs, base_y + 18, "調べる画素", size=12, weight=700, fill=INK, anchor="middle")
    root.add("path", d="M%s,%s A%s,%s 0 0 1 %s,%s" % (R(ox + (px - RAD) * cs), R(base_y), R(RAD * cs), R(RAD * 24), R(ox + (px + RAD) * cs), R(base_y)), fill="none", stroke="#93c5fd", stroke_width=2, stroke_dasharray="5 4")
    t0, dt = 1.0, 0.35
    for k in range(K):
        ang = math.pi * (k + 0.5) / K
        r = RAD * (0.4 + 0.6 * ((k * 0.6180339887) % 1.0))
        x, z = px + r * math.cos(ang), pz + r * math.sin(ang)
        c = int(math.floor(x))
        hit = 0 <= c < NX and h[c] > z
        tt = t0 + k * dt
        g = root.add("g", opacity=0)
        g.Show(tt)
        g.add("line", x1=R(ox + px * cs), y1=R(base_y - pz * 24), x2=R(ox + x * cs), y2=R(base_y - z * 24), stroke=(RED if hit else "#86efac"), stroke_width=1.2, stroke_dasharray="3 3")
        g.add("circle", cx=R(ox + x * cs), cy=R(base_y - z * 24), r=4.5, fill=(RED if hit else GREEN))
    n_hit = sum(1 for k in range(K) if (lambda ang, r: (lambda x, z: 0 <= int(math.floor(x)) < NX and h[int(math.floor(x))] > z)(px + r * math.cos(ang), pz + r * math.sin(ang)))(math.pi * (k + 0.5) / K, RAD * (0.4 + 0.6 * ((k * 0.6180339887) % 1.0))))
    st.Text(40, 276, "サンプル %d 個のうち、赤い壁に当たったのは %d 個" % (K, n_hit), size=14, weight=700, fill=RED)
    # 帯
    t_s = t0 + K * dt + 0.8
    rows = [("色のにじみなし(直接光だけ)", nobounce, GRAY, 306), ("SSGI(%d サンプル)" % K, ssgi, BLUE, 350), ("正解(細かい光線 180 本)", truth, GREEN, 394)]
    for r_, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, 40, y - 4, lab, size=13, weight=700, fill=col)
        grid = Grid(st, ox, y, NX, 1, cs, base="#e5e7eb", stroke="#94a3b8")
        for i in range(NX):
            grid.Paint(i, 0, t_s + r_ * 2.2 + i * 0.04, Hex([255 * v for v in vals[i]]))
        grid.Flush()
    t_end = t_s + 3 * 2.2 + 0.5
    st.Text(40, 450, "サンプル数(画素あたり):", size=14)
    st.Text(250, 450, "SSGI %d 個 / 正解 180 本" % K, size=14, weight=700, fill=PURPLE)
    st.Box(t_end, 40, 462, 860, 56, [("壁に近い床へ、赤い色がにじむ。正解とのずれ(平均): にじみなし %.3f → SSGI %.3f" % (e_n, e_s), 15, "#1e3a8a"), ("画面に見えていない物(壁の裏・画面の外)の色は、集められない", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "床の画素が、周りの見える画素の色を集める"), (t0, t_s, "半円の中に、16 個のサンプルを撒き、壁に当たったら、その色を足す"), (t_s, t_end, "全部の画素で繰り返すと、壁の近くの床が、赤みを帯びる"), (t_end, 99, "細かい光線の正解に、近い色になる(サンプルが少ないとノイズが出る)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "SSGI", "サンプル %d 個のうち %d 個が壁に当たる" % (K, n_hit))
    st.Note(t_end, "SSGI", "ずれ: にじみなし %.3f / SSGI %.3f" % (e_n, e_s))
    return Build(st, name, "graphics/gi/ssgi.md", BEFORE, [1.5, 4.5, 7.5, 10.5, 14.0, 18.0])


# ===================================================================== SH bands
def ShBands():
    name = "sh-bands"
    st = Stage(name, "球面調和関数(SH): 空の明るさを、少ない数で近似する。段数を上げると、細部が戻る", duration=20.0, subtitle="2 次元(円)の空で説明する。太陽と、青い空のある空を、0 段〜3 段の波で近似する")
    sc, root = st.scene, st.root
    NS = 360

    def Sky(a):
        # 角度 a(0 = 右、90 = 上)の明るさ
        up = math.sin(math.radians(a))
        base = 0.25 + 0.30 * max(0.0, up)
        sun = 1.6 * math.exp(-((((a - 50) + 180) % 360 - 180) / 14.0) ** 2)
        return base + sun

    vals = [Sky(a) for a in range(NS)]

    def Fit(nb):
        coef = []
        for k in range(nb + 1):
            if k == 0:
                coef.append((sum(vals) / NS, 0.0))
            else:
                re = sum(vals[a] * math.cos(math.radians(k * a)) for a in range(NS)) * 2 / NS
                im = sum(vals[a] * math.sin(math.radians(k * a)) for a in range(NS)) * 2 / NS
                coef.append((re, im))
        return coef

    def Eval(coef, a):
        v = coef[0][0]
        for k in range(1, len(coef)):
            v += coef[k][0] * math.cos(math.radians(k * a)) + coef[k][1] * math.sin(math.radians(k * a))
        return v

    errs, fits = [], []
    for nb in range(0, 4):
        c = Fit(nb)
        fits.append(c)
        e = math.sqrt(sum((Eval(c, a) - vals[a]) ** 2 for a in range(NS)) / NS)
        errs.append(e)
    assert errs[0] > errs[1] > errs[2] > errs[3]
    names = ["0 段(平均だけ)", "1 段(向きの偏り)", "2 段", "3 段"]
    nfloat = [1, 3, 5, 7]
    CX, CY, RR = 480.0, 250.0, 120.0
    # 左: 真の空と近似の極座標
    st.Panel(30, 96, 450, 330, "① 空の明るさ(円の外へ伸ばした線 = 明るい)", color=BLUE)
    def Polar(f, cx, cy, scale):
        pts = []
        for a in range(0, 361, 3):
            v = f(a)
            r = 30 + v * scale
            pts.append((cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))))
        return pts
    PX, PY = 255.0, 262.0
    root.add("circle", cx=PX, cy=PY, r=30, fill="none", stroke=LIGHT, stroke_width=1.5)
    root.add("path", d=Poly(Polar(lambda a: Sky(a), PX, PY, 55)) + " Z", fill="#fde68a", fill_opacity=0.3, stroke=GRAY, stroke_width=2.5)
    sc.Text(root, 50, 126, "灰 = 本当の空", size=12, weight=700, fill=GRAY)
    t0, per = 1.0, 4.6
    cur = root.add("path", d=Poly(Polar(lambda a: Eval(fits[0], a), PX, PY, 55)) + " Z", fill="none", stroke=RED, stroke_width=3.5)
    items = [(t0 + m * per, Poly(Polar(lambda a, m=m: Eval(fits[m], a), PX, PY, 55)) + " Z") for m in range(4)]
    cur.Steps("d", items)
    sc.Text(root, 50, 144, "赤 = 近似", size=12, weight=700, fill=RED)
    # 右: 係数と誤差
    st.Panel(510, 96, 420, 330, "② 近似の段数と、必要な数・ずれ", color=PURPLE)
    for m in range(4):
        y = 140 + m * 66
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        sc.Text(g, 530, y, names[m], size=16, weight=700, fill=PURPLE)
        sc.Text(g, 530, y + 22, "必要な係数 %d 個(1 色あたり)" % nfloat[m], size=13, weight=500, fill=TEXT)
        w = errs[m] / errs[0] * 250
        g.add("rect", x=530, y=y + 30, width=R(w), height=14, fill=RED, opacity=0.8)
        sc.Text(g, 530 + w + 8, y + 42, "ずれ %.3f" % errs[m], size=12, weight=700, fill=RED)
    st.Text(40, 462, "係数の数(1 色あたり):", size=14)
    st.Counter(240, 466, [(t0 + m * per + 0.3, nfloat[m]) for m in range(4)], size=24, fill=PURPLE)
    st.Text(310, 466, "→ RGB の 3 色で、×3", size=14, weight=500, fill=MUTED)
    t_end = t0 + 4 * per
    st.Box(t_end - 0.5, 520, 440, 410, 80, [("3 段で、ずれは 0 段の %.0f%%" % (100 * errs[3] / errs[0]), 15, "#1e3a8a"), ("実際の 3 次元では 2 段(9 係数 × 3 色 = 27 個)がよく使われる", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "空の明るさを、向きの関数として覚えたい。全部の向きは、保存できない"), (t0, t_end, "波(周波数)を足す。0 段は平均だけ、段が上がると細かい違いが戻る"), (t_end, 99, "ゆるやかな変化なら、少ない係数で足りる。鋭い太陽は、段を上げても、残りやすい")], size=14, fill=MUTED, weight=500)
    for m in range(4):
        st.Note(t0 + m * per, "SH", "%s: 係数 %d 個、ずれ %.3f" % (names[m], nfloat[m], errs[m]))
    return Build(st, name, "graphics/gi/theory/spherical-harmonics.md", BEFORE, [1.5, 5.0, 10.0, 15.0, 18.0, 19.5])


NAMES = ["voxel-cone-trace", "radiance-cascades", "ssgi-bounce", "sh-bands"]
FIGS = [VoxelConeTrace, RadianceCascades, SsgiBounce, ShBands]
