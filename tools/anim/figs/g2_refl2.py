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


# ===================================================================== Parallax
def ParallaxBox():
    name = "parallax-box"
    st = Stage(name, "視差補正: キューブマップの反射を、部屋の箱に合わせて「どこに映るか」を直す", duration=21.0, subtitle="部屋(幅 12、高さ 6)の断面。プローブは部屋の中央。床の点から、右の壁へ反射する光線を調べる")
    sc, root = st.scene, st.root
    W, Hh = 12.0, 6.0
    probe = (6.0, 3.0)
    ox, oy, S = 360.0, 430.0, 42.0
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * S
    # 床の点 8 個(x = 0.8 … 5.0)から、斜め上へ反射(右壁へ)
    pts = [(0.8 + k * 0.6, 0.0) for k in range(8)]
    angle = math.radians(24.0)
    rv = (math.cos(angle), math.sin(angle))

    def WallHit(p, d):
        t = (W - p[0]) / d[0]
        y = p[1] + d[1] * t
        return (W, y)

    data = []
    for p in pts:
        true_hit = WallHit(p, rv)
        # 補正なし: プローブ中心から同じ向きに飛ばして、壁に当たる所を読む
        unc = WallHit(probe, rv)
        # 補正あり: 真の当たり点の向きで、プローブから読む
        d2 = (true_hit[0] - probe[0], true_hit[1] - probe[1])
        L = math.hypot(*d2)
        cor = WallHit(probe, (d2[0] / L, d2[1] / L))
        data.append((p, true_hit, unc, cor))
    e_unc = sum(abs(d[2][1] - d[1][1]) for d in data) / len(data)
    e_cor = sum(abs(d[3][1] - d[1][1]) for d in data) / len(data)
    assert e_cor < 1e-9 and e_unc > 0.4
    st.Panel(30, 96, 900, 360, "① 部屋の断面", color=BLUE)
    root.add("rect", x=R(X(0)), y=R(Y(Hh)), width=R(W * S), height=R(Hh * S), fill="#f8fafc", stroke="#475569", stroke_width=4)
    root.add("circle", cx=R(X(probe[0])), cy=R(Y(probe[1])), r=9, fill=PURPLE)
    sc.Text(root, X(probe[0]), Y(probe[1]) - 14, "プローブ(キューブマップの中心)", size=12, weight=700, fill=PURPLE, anchor="middle")
    # 壁の目盛(模様 = 高さの目印)
    for k in range(0, 7):
        root.add("line", x1=X(W), y1=Y(k), x2=X(W) + 8, y2=Y(k), stroke="#475569", stroke_width=2)
        sc.Text(root, X(W) + 12, Y(k) + 4, "高さ %d" % k, size=11, weight=500, fill=MUTED)
    t0, per = 1.0, 1.9
    for k, (p, th, un, co) in enumerate(data):
        t = t0 + k * per
        g = root.add("g", opacity=0)
        g.Show(t, t + per if k < len(data) - 1 else None)
        g.add("circle", cx=R(X(p[0])), cy=R(Y(p[1])), r=7, fill=INK)
        g.add("line", x1=R(X(p[0])), y1=R(Y(p[1])), x2=R(X(th[0])), y2=R(Y(th[1])), stroke=GREEN, stroke_width=3.5)
        g.add("circle", cx=R(X(th[0])), cy=R(Y(th[1])), r=7, fill=GREEN)
        g.add("line", x1=R(X(probe[0])), y1=R(Y(probe[1])), x2=R(X(un[0])), y2=R(Y(un[1])), stroke=RED, stroke_width=2.5, stroke_dasharray="6 5")
        g.add("circle", cx=R(X(un[0])), cy=R(Y(un[1])), r=7, fill=RED)
        sc.Text(g, 40, 150, "床の点 %d(x = %.1f)" % (k + 1, p[0]), size=15, weight=700, fill=INK)
        sc.Text(g, 40, 174, "本当に映る高さ(緑): %.2f" % th[1], size=14, weight=700, fill=GREEN)
        sc.Text(g, 40, 196, "補正なし(赤): %.2f → ずれ %.2f" % (un[1], abs(un[1] - th[1])), size=14, weight=700, fill=RED)
        sc.Text(g, 40, 218, "補正あり: %.2f → ずれ 0.00" % co[1], size=14, weight=700, fill=BLUE)
    st.Legend(40, 250, [(GREEN, "本当の反射")])
    st.Legend(40, 272, [(RED, "補正なし(プローブから同じ向き)")])
    st.Text(40, 480, "ずれの平均:", size=15)
    st.Counter(150, 484, [(t0 + k * per + 0.2, int(round(100 * sum(abs(d[2][1] - d[1][1]) for d in data[:k + 1]) / (k + 1)))) for k in range(len(data))], size=24, fill=RED)
    st.Text(205, 484, "(高さ × 100)", size=12, weight=500, fill=MUTED)
    t_end = t0 + len(data) * per
    st.Box(t_end, 300, 462, 630, 62, [("補正なし: 平均 %.2f ずれる(床の点によって違う)" % e_unc, 15, "#991b1b"), ("補正あり: ずれ 0(部屋が箱なので、光線と箱の交点で厳密に直せる)", 14, "#166534")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "キューブマップは、プローブの位置から見た景色。床の点とは、見る位置が違う"), (t0, t_end, "床の点ごとに、本当に映る場所と、プローブから読む場所を比べる"), (t_end, 99, "光線と箱の交点を求め、その向きでプローブを読むと、位置が合う")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "視差補正", "床の点 8 個: 補正なしの平均ずれ %.2f、補正ありは 0" % e_unc)
    return Build(st, name, "graphics/reflections/probes/parallax.md", BEFORE, [1.5, 4.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== Roughness lobe
def RoughnessLobe():
    name = "roughness-lobe"
    st = Stage(name, "ざらざらした面の反射: 粗さに応じて、光線の向きをばらつかせて平均する(確率的 SSR)", duration=21.0, subtitle="粗さが上がると、反射の光線が広がる。ばらつかせた光線を少数だけ使うと、ざらつき(ノイズ)が出る")
    sc, root = st.scene, st.root
    # 上: 粗さごとの光線の広がり
    rough = [0.1, 0.4, 0.8]
    N = 16
    rng = Lcg(5)
    st.Panel(30, 96, 900, 170, "① 粗さごとの、反射光線の広がり(法線は真上)", color=BLUE)
    t0, per = 1.0, 2.6
    spread = []
    for m, a in enumerate(rough):
        cx = 150 + m * 300
        base = 240.0
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        g.add("line", x1=cx - 90, y1=base, x2=cx + 90, y2=base, stroke="#94a3b8", stroke_width=3)
        angs = []
        for k in range(N):
            u = rng.U()
            tan_t = a * a * math.sqrt(u) / math.sqrt(max(1e-6, 1 - u)) if False else a * math.sqrt(u / max(1e-6, 1 - u))
            th = min(math.atan(tan_t), math.radians(80))
            sg = 1 if rng.U() < 0.5 else -1
            angs.append(sg * th)
        # 反射方向の中心は垂直(0°)
        for ang in angs:
            g.add("line", x1=cx, y1=base, x2=R(cx + math.sin(ang) * 85), y2=R(base - math.cos(ang) * 85), stroke=RED, stroke_width=1.6, opacity=0.85)
        sd = math.degrees(math.sqrt(sum(a_ * a_ for a_ in angs) / N))
        spread.append(sd)
        sc.Text(g, cx, 122, "粗さ %.1f: 広がり約 %d°" % (a, round(sd)), size=14, weight=700, fill=PURPLE, anchor="middle")
    assert spread[0] < spread[1] < spread[2]
    # 下: 平均する光線の数でノイズが変わる
    t_n = t0 + 3 * per + 0.4
    st.Text(40, 296, "粗さ 0.4 の面に映る縞模様(1 画素ごとに、光線を N 本使って平均)", size=14, weight=700)
    NP = 48
    CW, X0 = 15.0, 60.0
    a = 0.4
    D = 10.0

    def Stripe(x):
        return 0.9 if int(math.floor(x / 1.2)) % 2 == 0 else 0.15

    def Pixel(i, n, seed):
        r = Lcg(seed * 1000 + i)
        centre = D * math.tan(math.radians(-8 + 16 * i / NP))
        acc = 0.0
        for _ in range(n):
            u = r.U()
            th = math.atan(a * math.sqrt(u / max(1e-6, 1 - u))) * (1 if r.U() < 0.5 else -1)
            hit = centre + D * (math.tan(th) * 0.35)
            acc += Stripe(hit)
        return acc / n

    ref = [Pixel(i, 512, 9) for i in range(NP)]
    rows = [(1, "1 本", RED), (4, "4 本", AMBER), (16, "16 本", GREEN)]
    errs = []
    for r_, (n, lab, col) in enumerate(rows):
        vals = [Pixel(i, n, 3 + r_) for i in range(NP)]
        errs.append(sum(abs(v - rf) for v, rf in zip(vals, ref)) / NP)
    assert errs[0] > errs[1] > errs[2]
    y0s = [314, 354, 394]
    for r_, ((n, lab, col), y) in enumerate(zip(rows, y0s)):
        sc.Text(root, 40, y + 14, "N = " + lab, size=13, weight=700, fill=col, opacity=1)
    gridr = []
    for r_, ((n, lab, col), y) in enumerate(zip(rows, y0s)):
        vals = [Pixel(i, n, 3 + r_) for i in range(NP)]
        g = Grid(st, X0 + 40, y, NP, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(NP):
            g.Paint(i, 0, t_n + r_ * 2.4 + i * 0.03, Gray(vals[i]))
        g.Flush()
    sc.Text(root, 40, 440, "基準(512 本)", size=13, weight=700, fill=BLUE)
    gref = Grid(st, X0 + 40, 426, NP, 1, CW, base="#e5e7eb", stroke="#94a3b8")
    for i in range(NP):
        gref.Paint(i, 0, t_n + 3 * 2.4 + i * 0.03, Gray(ref[i]))
    gref.Flush()
    t_end = t_n + 3 * 2.4 + 1.8
    for r_, (n, lab, col) in enumerate(rows):
        sc.Text(root, 940, 330 + r_ * 40, "基準とのずれ %.3f" % errs[r_], size=12, weight=700, fill=col, anchor="end", opacity=0).Show(t_n + r_ * 2.4 + 1.6)
    st.Box(t_end, 560, 462, 370, 60, [("1 本 → 16 本で、ずれは %.1f 分の 1" % (errs[0] / errs[2]), 15, "#166534"), ("本数を増やすほど、きれい。代わりに、読み込みが増える", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "粗い面は、いろいろな向きから、光を集める"), (t0, t_n, "粗さに応じて、光線の向きを確率的にばらつかせる"), (t_n, t_end, "1 画素あたり少数の光線で平均すると、ざらつくので、フレームをまたいで混ぜて消す"), (t_end, 99, "(光線を増やす代わりに、TAA やぼかしで、ノイズを消すのが一般的)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "確率的 SSR", "粗さ 0.1 / 0.4 / 0.8 の広がり: %d° / %d° / %d°" % tuple(round(s) for s in spread))
    st.Note(t_n, "確率的 SSR", "ずれ: 1 本 %.3f / 4 本 %.3f / 16 本 %.3f" % tuple(errs))
    return Build(st, name, "graphics/reflections/ssr-stochastic.md", BEFORE, [1.5, 4.5, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== Prefilter
def PrefilterMips():
    name = "prefilter-mips"
    st = Stage(name, "環境マップの事前フィルタ: 粗さごとに、あらかじめぼかしたものをミップに入れておく", duration=22.0, subtitle="2 次元(円)の空。太陽と空がある。粗さ 0・0.25・0.5・0.75・1 の 5 段で、ぼかし具合と、画素数を見る")
    sc, root = st.scene, st.root
    NS = 180

    def Sky(a):
        return 0.20 + 0.15 * max(0.0, math.sin(math.radians(a))) + 1.8 * math.exp(-((((a - 70) + 180) % 360 - 180) / 6.0) ** 2) + 0.7 * math.exp(-((((a - 200) + 180) % 360 - 180) / 10.0) ** 2)

    base = [Sky(2 * i) for i in range(NS)]
    rs = [0.0, 0.25, 0.5, 0.75, 1.0]

    def Filter(r):
        if r == 0:
            return base[:]
        sig = max(1.0, 3 + 40 * r * r)         # 度
        out = []
        for i in range(NS):
            num = den = 0.0
            for d in range(-NS // 2, NS // 2):
                w = math.exp(-((d * 2) ** 2) / (2 * sig * sig))
                if w < 1e-4:
                    continue
                num += w * base[(i + d) % NS]
                den += w
            out.append(num / den)
        return out

    fl = [Filter(r) for r in rs]
    peaks = [max(f) for f in fl]
    assert peaks[0] > peaks[2] > peaks[4]
    faces = [256, 128, 64, 32, 16]
    mem = [f * f * 6 * 4 * 4 for f in faces]
    total = sum(mem)
    X0, W = 50.0, 520.0
    XX = lambda a: X0 + a / 360.0 * W
    st.Panel(30, 96, 580, 330, "① 反射の向きごとの明るさ(横軸 = 向き 0〜360°)", color=BLUE)
    cols = [GRAY, BLUE, GREEN, AMBER, RED]
    t0, per = 1.0, 3.4
    ymax = max(peaks) * 1.05
    YY = lambda v: 410 - v / ymax * 270
    for m, r in enumerate(rs):
        d = Poly([(XX(2 * i), YY(fl[m][i])) for i in range(NS)])
        g = root.add("path", d=d, fill="none", stroke=cols[m], stroke_width=3, opacity=0)
        g.Show(t0 + m * per)
        sc.Text(root, 590, 150 + m * 22, "粗さ %.2f: 最大 %.2f" % (r, peaks[m]), size=12, weight=700, fill=cols[m], anchor="end", opacity=0).Show(t0 + m * per)
    # 右: ミップのサイズ
    st.Panel(640, 96, 290, 330, "② ミップごとの大きさ", color=PURPLE)
    for m, r in enumerate(rs):
        y = 130 + m * 56
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        w = faces[m] / 256.0 * 150
        g.add("rect", x=660, y=y, width=R(w), height=26, fill=cols[m], opacity=0.85)
        sc.Text(g, 660, y - 4, "粗さ %.2f" % r, size=12, weight=700, fill=cols[m])
        sc.Text(g, 660 + w + 8, y + 18, "%d×%d × 6 面" % (faces[m], faces[m]), size=12, weight=700, fill=TEXT)
        sc.Text(g, 660, y + 42, "%s KB(1 面に RGBA16F)" % Fmt(mem[m] // 1024), size=11, weight=500, fill=MUTED)
    st.Text(40, 452, "合計のメモリ:", size=15)
    ser = []
    c = 0
    for m in range(5):
        c += mem[m]
        ser.append((t0 + m * per + 0.3, c // 1024))
    st.Counter(180, 456, ser, size=24, fill=PURPLE)
    st.Text(250, 456, "KB(1 つのプローブ)", size=14)
    # 読み出し: 粗さ 0.4
    t_l = t0 + 5 * per + 0.4
    rr = 0.4
    pos = rr / 0.25
    lo = int(math.floor(pos))
    fr = pos - lo
    a_look = 70
    idx = a_look // 2
    v_lo, v_hi = fl[lo][idx], fl[lo + 1][idx]
    v = v_lo * (1 - fr) + v_hi * fr
    g = root.add("g", opacity=0)
    g.Show(t_l)
    g.add("line", x1=R(XX(a_look)), y1=140, x2=R(XX(a_look)), y2=410, stroke=INK, stroke_width=2, stroke_dasharray="5 4")
    sc.Text(g, XX(a_look) + 8, 132, "反射の向き 70°", size=12, weight=700, fill=INK)
    st.Box(t_l + 0.3, 330, 436, 600, 74, [("粗さ 0.4 の読み出し: ミップ %d(%.2f)と %d(%.2f)を混ぜる" % (lo, rs[lo], lo + 1, rs[lo + 1]), 14, "#1e3a8a"), ("%.2f × %.2f + %.2f × %.2f = %.2f" % (v_lo, 1 - fr, v_hi, fr, v), 14, "#1e3a8a"), ("読み込みは 1〜2 回でよい(毎回ぼかさなくてよい)", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ざらざらした面の反射は、広い範囲の平均。毎回計算すると重い"), (t0, t_l, "粗さごとに、前もってぼかした環境マップを作り、ミップに入れる"), (t_l, 99, "使うときは、粗さに近い 2 つのミップを読んで混ぜるだけ")], size=14, fill=MUTED, weight=500)
    for m, r in enumerate(rs):
        st.Note(t0 + m * per, "プリフィルタ", "粗さ %.2f: 面 %d×%d、最大 %.2f" % (r, faces[m], faces[m], peaks[m]))
    return Build(st, name, "graphics/reflections/probes/prefilter.md", BEFORE, [1.5, 5.0, 8.5, 12.0, 15.0, 21.0])


# ===================================================================== Planar mirror
def PlanarMirror():
    name = "planar-mirror"
    st = Stage(name, "平面反射: カメラを鏡に対して反転して、もう 1 回シーンを描く", duration=20.0, subtitle="断面。床が鏡。本物のカメラが見る「床に映った像」は、鏡の下に置いた仮想カメラから見た景色と同じ")
    sc, root = st.scene, st.root
    ox, oy, S = 120.0, 250.0, 30.0
    X = lambda x: ox + x * S
    Y = lambda y: oy - y * S
    cam = (1.0, 4.2)
    obj = [(7.5, 3.0), (11.0, 2.0)]        # 物体(杭の先端)
    st.Panel(30, 96, 900, 330, "① 断面(灰色の線 = 鏡の床)", color=BLUE)
    root.add("line", x1=X(0), y1=Y(0), x2=X(26), y2=Y(0), stroke="#475569", stroke_width=5)
    for p in obj:
        root.add("line", x1=X(p[0]), y1=Y(0), x2=X(p[0]), y2=Y(p[1]), stroke="#94a3b8", stroke_width=6)
        root.add("circle", cx=X(p[0]), cy=Y(p[1]), r=8, fill=AMBER)
    root.add("circle", cx=X(cam[0]), cy=Y(cam[1]), r=9, fill=INK)
    sc.Text(root, X(cam[0]), Y(cam[1]) - 14, "カメラ", size=12, weight=700, fill=INK, anchor="middle")
    vcam = (cam[0], -cam[1])
    t0, per = 1.0, 5.0
    g = root.add("g", opacity=0)
    g.Show(t0)
    # 光の道(鏡で曲がる)
    hit_data = []
    for k, p in enumerate(obj):
        # 鏡の像の位置
        mp = (p[0], -p[1])
        # カメラから像への直線が、鏡(y = 0)と交わる点
        tt = cam[1] / (cam[1] + p[1])
        hx = cam[0] + (p[0] - cam[0]) * tt
        hit_data.append((p, mp, hx))
        ga = root.add("g", opacity=0)
        ga.Show(t0 + 0.3 + k * 4.0)
        ga.add("line", x1=R(X(cam[0])), y1=R(Y(cam[1])), x2=R(X(hx)), y2=R(Y(0)), stroke=RED, stroke_width=3)
        ga.add("line", x1=R(X(hx)), y1=R(Y(0)), x2=R(X(p[0])), y2=R(Y(p[1])), stroke=RED, stroke_width=3)
        ga.add("circle", cx=R(X(hx)), cy=R(Y(0)), r=6, fill=RED)
        sc.Text(ga, X(hx), Y(0) + 22, "光が鏡で曲がる点 x = %.2f" % hx, size=12, weight=700, fill=RED, anchor="middle")
    # 仮想カメラと像
    gv = root.add("g", opacity=0)
    gv.Show(t0 + 9.0)
    gv.add("circle", cx=R(X(vcam[0])), cy=R(Y(vcam[1])), r=9, fill="#94a3b8", stroke=INK, stroke_width=2, stroke_dasharray="3 3")
    sc.Text(gv, X(vcam[0]), Y(vcam[1]) + 22, "仮想カメラ(鏡の下に反転)", size=12, weight=700, fill=MUTED, anchor="middle")
    for k, (p, mp, hx) in enumerate(hit_data):
        gv.add("circle", cx=R(X(mp[0])), cy=R(Y(mp[1])), r=8, fill="#fde68a", stroke="#f59e0b", stroke_width=2)
        gv.add("line", x1=R(X(vcam[0])), y1=R(Y(vcam[1])), x2=R(X(mp[0])), y2=R(Y(mp[1])), stroke=GREEN, stroke_width=3, stroke_dasharray="7 5")
        sc.Text(gv, X(mp[0]) + 12, Y(mp[1]) + 5, "像", size=12, weight=700, fill="#92400e")
        # 一致の確認
        t = cam[1] / (cam[1] + p[1])
        # 仮想カメラから像への線が鏡と交わる点
        t2 = cam[1] / (cam[1] + p[1])
        hv = vcam[0] + (mp[0] - vcam[0]) * t2
        assert abs(hv - hx) < 1e-9
    # 数字
    st.Text(40, 452, "鏡で曲がる点(2 つの物体):", size=14)
    items = [(t0 + 0.3, ""), ]
    sc.Text(root, 270, 452, "x = %.2f と %.2f" % (hit_data[0][2], hit_data[1][2]), size=14, weight=700, fill=RED, opacity=0).Show(t0 + 4.4)
    sc.Text(root, 470, 452, "仮想カメラの直線と交わる点: 同じ値 (一致)", size=14, weight=700, fill=GREEN, opacity=0).Show(t0 + 10.0)
    # コスト
    n_obj = 120
    t_c = t0 + 12.0
    st.Panel(30, 470, 900, 48, "", color=PURPLE)
    sc.Text(root, 44, 500, "描画回数: 反射なし %d → 平面反射 %d(シーンを 2 回描く)/ SSR は %d + 画面全体 1 回" % (n_obj, 2 * n_obj, n_obj), size=14, weight=700, fill=PURPLE, opacity=0).Show(t_c)
    st.Caption(30, 534, [(0.0, t0, "床の鏡に映る像は、鏡の下にある「もう 1 つの世界」を見ているのと同じ"), (t0, t0 + 9.0, "本物のカメラから見ると、光は鏡で曲がって物体へ届く"), (t0 + 9.0, t_c, "鏡の下に、カメラを反転して置くと、同じ線が、まっすぐ物体の像へ伸びる"), (t_c, 99, "反転したカメラで、もう 1 回シーンを描く(描画 2 倍)。完全に正確だが、鏡が平面のときだけ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "平面反射", "鏡で曲がる点: %.2f / %.2f(仮想カメラの直線と一致)" % (hit_data[0][2], hit_data[1][2]))
    return Build(st, name, "graphics/reflections/planar.md", BEFORE, [1.5, 4.0, 8.0, 11.0, 14.0, 19.0])


NAMES = ["parallax-box", "roughness-lobe", "prefilter-mips", "planar-mirror"]
FIGS = [ParallaxBox, RoughnessLobe, PrefilterMips, PlanarMirror]
