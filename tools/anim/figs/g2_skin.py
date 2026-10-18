import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from storyboard import Hex  # noqa: E402

BEFORE = "## よくあるミス"


def Poly(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


# ===================================================================== Pre-integrated skin
def PreintLut():
    name = "preint-lut"
    st = Stage(name, "事前積分スキン: 光 × 曲率 の表で、影の境目の赤いにじみを作る", duration=21.0, subtitle="球の影の境目(N·L が 0 の付近)で、赤は広くにじみ、青は鋭く切れる。その差を、表にあらかじめ焼き込む")
    sc, root = st.scene, st.root
    # 拡散プロファイル(色ごとのガウス幅。単位は半径 1 の球での角度に相当)
    sig = {"R": 0.80, "G": 0.34, "B": 0.14}   # 色ごとの拡散の広さ(球の半径 1 に対する距離)

    def Integrate(ndl, curv, s):
        th = math.acos(max(-1.0, min(1.0, ndl)))
        r = 1.0 / curv
        num = den = 0.0
        n = 160
        for i in range(n):
            x = -math.pi + 2 * math.pi * (i + 0.5) / n
            w = math.exp(-((r * x) ** 2) / (2 * s * s))
            c = max(0.0, math.cos(th + x))
            num += c * w
            den += w
        return num / den

    _raw = Integrate

    def Integrate(ndl, curv, s):          # 明るい側(N·L = 1)で、どの色も 1 になるよう、そろえる
        return _raw(ndl, curv, s) / _raw(1.0, curv, s)

    NL = 24
    CV = [0.25, 0.5, 1.0, 2.0]
    def Lut(ndl, curv):
        return [Integrate(ndl, curv, sig[c]) for c in "RGB"]
    lut = {}
    for j, cv in enumerate(CV):
        for i in range(NL):
            ndl = -1.0 + 2.0 * (i + 0.5) / NL
            lut[(i, j)] = Lut(ndl, cv)
    # ターミネーター(N·L = 0 付近)の差
    t_ndl = -0.15
    lam = max(0.0, t_ndl)
    pre = Lut(t_ndl, 1.0)
    assert pre[0] > pre[2] and pre[0] > 0.02 and lam == 0.0
    # 左: LUT
    st.Panel(30, 96, 500, 190, "① 表(横 = N·L、縦 = 曲率)", color=PURPLE)
    cw, ch = 17.0, 40.0
    for (i, j), rgb in lut.items():
        r = root.add("rect", x=R(104 + i * cw), y=R(112 + j * 40), width=cw + 0.3, height=40.3, fill="#e5e7eb")
        r.Steps("fill", [(1.5 + 0.06 * i + 0.4 * j, Hex([255 * min(1.0, v * 1.15) for v in rgb]))])
    for j, cv in enumerate(CV):
        sc.Text(root, 98, 138 + j * 40, "曲率 %.2f" % cv, size=11, weight=700, fill=MUTED, anchor="end")
    sc.Text(root, 104, 282, "← 影(−1)", size=11, weight=500, fill=MUTED)
    sc.Text(root, 512, 282, "光が当たる(+1)→", size=11, weight=500, fill=MUTED, anchor="end")
    # 右: 色ごとの曲線
    st.Panel(560, 96, 370, 190, "② 影の境目付近の明るさ(曲率 1)", color=BLUE)
    ax0, ay0, aw, ah = 580.0, 112.0, 330.0, 150.0
    nl_vals = [-1.0 + 2.0 * i / 59 for i in range(60)]
    XX = lambda v: ax0 + (v + 1) / 2 * aw
    YY = lambda v: ay0 + ah - v * ah
    root.add("line", x1=R(XX(0)), y1=ay0, x2=R(XX(0)), y2=ay0 + ah, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="4 4")
    sc.Text(root, XX(0), ay0 + ah + 14, "N·L = 0(影の境目)", size=10, weight=500, fill=MUTED, anchor="middle")
    lam_path = root.add("path", d=Poly([(XX(v), YY(max(0.0, v))) for v in nl_vals]), fill="none", stroke=GRAY, stroke_width=3, stroke_dasharray="6 5", opacity=0)
    lam_path.Show(9.0)
    sc.Text(root, 700, 130, "灰の破線 = ふつうの拡散(境目で急に 0)", size=11, weight=700, fill=GRAY, opacity=0).Show(9.0)
    for c, col in zip("RGB", [RED, GREEN, BLUE]):
        pts = [(XX(v), YY(min(1.0, Integrate(v, 1.0, sig[c])))) for v in nl_vals]
        p = root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(5.0 + "RGB".index(c) * 1.2)
    # 動く点: N·L を変える
    for c, col in zip("RGB", [RED, GREEN, BLUE]):
        dot = root.add("circle", cx=R(XX(-1)), cy=R(YY(Integrate(-1.0, 1.0, sig[c]))), r=5.5, fill=col, opacity=0)
        dot.Show(9.0)
        prev = None
        for k, v in enumerate(nl_vals):
            t = 9.0 + 7.0 * k / (len(nl_vals) - 1)
            x, y = XX(v), YY(min(1.0, Integrate(v, 1.0, sig[c])))
            if prev is None:
                dot.Set(t, "cx", R(x))
                dot.Set(t, "cy", R(y))
            else:
                dot.Ramp(prev, t, "cx", R(x))
                dot.Ramp(prev, t, "cy", R(y))
            prev = t
    # 下: 球の見た目(ふつうの拡散 と 事前積分)
    st.Text(40, 322, "球の影の境目(上 = ふつうの拡散、下 = 事前積分)", size=13, weight=700, fill=TEXT)
    NS = 48
    t_s = 16.8
    for r_, (lab, f, y) in enumerate([("ふつうの拡散", lambda v: [max(0.0, v)] * 3, 340), ("事前積分", lambda v: [min(1.0, Integrate(v, 1.0, sig[c]) * 1.1) for c in "RGB"], 392)]):
        sc.Text(root, 40, y + 14, lab, size=12, weight=700, fill=(GRAY if r_ == 0 else PURPLE))
        gr = Grid(st, 150, y, NS, 1, 16.0, base="#e5e7eb", stroke="#94a3b8")
        for i in range(NS):
            v = -1.0 + 2.0 * (i + 0.5) / NS
            c = f(v)
            gr.Paint(i, 0, t_s + 0.03 * i, Hex([255 * min(1.0, x * 0.98) for x in c]))
        gr.Flush()
    t_end = t_s + NS * 0.03 + 0.4
    st.Box(t_end, 560, 436, 370, 76, [("影の境目(N·L = %.2f)での色" % t_ndl, 13, MUTED), ("事前積分: R %.2f / G %.2f / B %.2f → 赤く にじむ" % tuple(pre), 14, "#991b1b"), ("ふつうの拡散: R 0 / G 0 / B 0(真っ黒)", 14, TEXT)], PURPLE, "#faf5ff")
    st.Caption(30, 534, [(0.0, 1.5, "肌の中で光が散らばるので、影の境目で赤い光が先に回り込む"), (1.5, 5.0, "光の当たり方と曲率から、色を求める表(LUT)を、あらかじめ作る"), (5.0, 9.0, "赤は広く、青は狭く(境目で鋭く)切れる"), (9.0, t_s, "N·L を動かすと、境目の外でも、赤がまだ残っている"), (t_s, 99, "球に当てると、ふつうの拡散は硬く切れて、事前積分は、赤い帯がにじむ")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "事前積分", "表 %d×%d を計算(色ごとの拡散プロファイル σ = %.2f / %.2f / %.2f)" % (NL, len(CV), sig["R"], sig["G"], sig["B"]))
    return Build(st, name, "graphics/skin-hair/skin/pre-integrated.md", BEFORE, [1.5, 4.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== Kajiya-Kay
def KajiyaLobes():
    name = "kajiya-lobes"
    st = Stage(name, "髪のハイライト: 毛の向き(接線)から、細い帯のハイライトを計算する(Kajiya-Kay)", duration=20.0, subtitle="毛の流れ(曲線)の上で、毛の向きが少しずつ変わる。光と視線は固定。1 つ目(白)と、ずらした 2 つ目(色つき)を足す")
    sc, root = st.scene, st.root
    NX, NY, CS = 22, 24, 12.0
    L = (0.0, 0.5, 0.866)           # 光の向き(上寄りから)
    V = (0.0, 0.0, 1.0)             # 視線
    normalize = lambda v: tuple(c / math.sqrt(sum(a * a for a in v)) for c in v)
    L = normalize(L)

    def Tangent(i, j):
        # 毛は縦に流れる。行ごとに傾きが変わり、列ごとに少し捻れる(つやの帯が曲がる)
        ang = math.radians(-55 + 110 * j / (NY - 1))
        tw = math.radians(-12 + 24 * i / (NX - 1))
        t = (math.sin(tw), math.cos(ang) * math.cos(tw), math.sin(ang) * math.cos(tw))
        return normalize(t)

    def Spec(t, p, shift):
        # 接線をずらして(法線方向に shift)から、Kajiya-Kay
        n = (0.0, 0.0, 1.0)
        tt = normalize(tuple(t[k] + shift * n[k] for k in range(3)))
        tl = sum(tt[k] * L[k] for k in range(3))
        tv = sum(tt[k] * V[k] for k in range(3))
        s = math.sqrt(max(0.0, 1 - tl * tl)) * math.sqrt(max(0.0, 1 - tv * tv)) - tl * tv
        return max(0.0, s) ** p

    p1, s1 = 90.0, -0.10
    p2, s2 = 28.0, 0.28
    prim = [[Spec(Tangent(i, j), p1, s1) for i in range(NX)] for j in range(NY)]
    sec = [[Spec(Tangent(i, j), p2, s2) for i in range(NX)] for j in range(NY)]
    hair = (0.20, 0.12, 0.08)
    secc = (1.0, 0.55, 0.25)
    comb = [[[min(1.0, hair[k] + 0.9 * prim[j][i] + 0.7 * sec[j][i] * secc[k]) for k in range(3)] for i in range(NX)] for j in range(NY)]
    pa = max(max(r) for r in prim)
    sa = max(max(r) for r in sec)
    assert pa > 0.3 and sa > 0.2
    panels = [("1 つ目: 白い帯(鋭い・p=%g)" % p1, GRAY, 30), ("2 つ目: 色つきの帯(広い・p=%g、ずらす)" % p2, AMBER, 335), ("足した結果(髪の色 + 2 つのハイライト)", PURPLE, 640)]
    t0, per = 1.0, 4.4
    hl = lambda v: Hex([255 * min(1.0, x) for x in v])
    for m, (lab, col, x) in enumerate(panels):
        st.Panel(x, 96, NX * CS, NY * CS, lab, color=col)
        g = Grid(st, x, 96, NX, NY, CS, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                if m == 0:
                    c = [min(1.0, 0.06 + prim[j][i]) * 0.9] * 3
                elif m == 1:
                    c = [min(1.0, 0.06 + sec[j][i] * secc[k]) * 0.9 for k in range(3)]
                else:
                    c = comb[j][i]
                g.Paint(i, j, t0 + m * per + 0.04 * j, hl(c))
        g.Flush()
    # 数字
    t_e = t0 + 3 * per
    st.Text(40, 410, "計算した画素: %d 個(1 個ごとに、pow を 2 回)" % (NX * NY), size=14)
    st.Counter(430, 414, [(t0 + m * per + 0.04 * NY, (m + 1) * NX * NY) for m in range(3)], size=22, fill=PURPLE)
    st.Text(30, 440, "Kajiya-Kay:  sin(T,L)·sin(T,V) − (T·L)(T·V)  を p 乗する", size=13, weight=700, fill=BLUE)
    st.Text(30, 462, "T = 毛の向き、L = 光、V = 視線。毛を円柱と見て、「円錐状に」光が散らばるので、帯になる", size=12, weight=500, fill=MUTED)
    st.Box(t_e, 560, 410, 370, 100, [("1 つ目(白): 表面の反射。p が大きいので細い", 13, TEXT), ("2 つ目(色): 髪の中を通った光。接線をずらして、広く・色つき", 13, "#92400e"), ("帯の位置が、毛の向きで動くので、艶が髪に沿って流れる", 13, "#1e3a8a")], PURPLE, "#faf5ff")
    st.Caption(30, 534, [(0.0, t0, "毛の向き(接線)は、場所ごとに変わる"), (t0, t0 + per, "1 つ目: 毛の向きだけから、細い白い帯が決まる"), (t0 + per, t0 + 2 * per, "2 つ目: 接線を少しずらして、広い色つきの帯を足す"), (t0 + 2 * per, 99, "足すと、髪の艶が、白と色の 2 本の帯になる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "Kajiya-Kay", "p=%g(shift %.2f)と p=%g(shift %.2f)で、%d 画素ぶん計算" % (p1, s1, p2, s2, NX * NY))
    return Build(st, name, "graphics/skin-hair/hair/kajiya-kay.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== Thin translucency
def ThinTransmit():
    name = "thin-transmit"
    st = Stage(name, "薄い物の透過光: 耳や葉が、後ろからの光で、赤く(緑に)透ける", duration=20.0, subtitle="耳の断面(厚さの違うところ)を、後ろから照らす。色ごとに「厚さに応じて」光が減る(ベールの法則)")
    sc, root = st.scene, st.root
    NX, NY, CS = 28, 14, 14.0
    sig = {"R": 0.55, "G": 1.3, "B": 2.6}   # 厚さ 1 あたりの吸収(赤は抜けやすい)
    cx0, cy0 = NX / 2, NY / 2

    def Thick(i, j):
        d = ((i + 0.5 - cx0) / 12.5) ** 2 + ((j + 0.5 - cy0) / 6.5) ** 2
        return max(0.0, 2.6 * (1 - d) ** 0.7) if d < 1 else 0.0

    thick = [[Thick(i, j) for i in range(NX)] for j in range(NY)]
    back = (1.0, 0.95, 0.85)
    skin = (0.85, 0.55, 0.45)

    def Out(i, j):
        t = thick[j][i]
        if t <= 0:
            return None
        trans = [math.exp(-sig[c] * t) for c in "RGB"]
        return [back[k] * trans[k] for k in range(3)], trans

    st.Panel(30, 96, NX * CS, NY * CS, "① 厚さ(濃い = 厚い)", color=BLUE)
    g1 = Grid(st, 30, 96, NX, NY, CS, base="#f8fafc")
    for j in range(NY):
        for i in range(NX):
            t = thick[j][i]
            g1.Paint(i, j, 0.5, Mix("#f8fafc", "#475569", t / 2.6) if t > 0 else "#f8fafc")
    g1.Flush()
    X2 = 30 + NX * CS + 40
    st.Panel(X2, 96, NX * CS, NY * CS, "② 後ろから光を当てたときの色", color=RED)
    g2 = Grid(st, X2, 96, NX, NY, CS, base="#0f172a")
    t0, dt = 1.5, 0.06
    for j in range(NY):
        for i in range(NX):
            o = Out(i, j)
            if o:
                g2.Paint(i, j, t0 + dt * i, Hex([255 * min(1.0, v * 1.3) for v in o[0]]))
            else:
                g2.Paint(i, j, t0 + dt * i, "#0f172a")
    g2.Flush()
    # 中央の断面(1 行)で、色ごとの透過率
    mid = NY // 2
    xs = [i for i in range(NX) if thick[mid][i] > 0]
    st.Panel(30, 316, 440, 150, "③ 中央の行での、色ごとに通り抜ける光の割合", color=PURPLE)
    ax0, ay0, aw, ah = 50.0, 330.0, 400.0, 110.0
    XX = lambda i: ax0 + i / (NX - 1) * aw
    YY = lambda v: ay0 + ah - v * ah
    for c, col in zip("RGB", [RED, GREEN, BLUE]):
        pts = [(XX(i), YY(math.exp(-sig[c] * thick[mid][i]))) for i in xs]
        p = root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3.5, opacity=0)
        p.Show(t0 + NX * dt + 0.4 + "RGB".index(c) * 0.8)
        sc.Text(root, 455, YY(math.exp(-sig[c] * thick[mid][NX // 2])) + 4, c, size=13, weight=700, fill=col, opacity=0).Show(t0 + NX * dt + 0.4 + "RGB".index(c) * 0.8)
    # 数字
    ci = NX // 2
    o = Out(ci, mid)
    edge = Out(xs[1], mid)
    t_e = t0 + NX * dt + 3.0
    st.Box(t_e, 490, 330, 440, 136, [("ふちの薄い所(厚さ %.1f): R %.0f%% / G %.0f%% / B %.0f%%" % ((thick[mid][xs[1]],) + tuple(100 * v for v in edge[1])), 14, "#1e3a8a"), ("真ん中の厚い所(厚さ %.1f): R %.0f%% / G %.0f%% / B %.0f%%" % ((thick[mid][ci],) + tuple(100 * v for v in o[1])), 14, "#991b1b"), ("厚いほど、青 → 緑 → 赤の順に光が減り、赤が残る", 13, TEXT), ("(ゲームでは、厚さを、事前に焼いた画像で持つ)", 12, MUTED)], PURPLE, "#faf5ff")
    st.Caption(30, 530, [(0.0, t0, "耳のように薄い所は、後ろの光が、肉を通り抜けてくる"), (t0, t0 + NX * dt, "各画素の厚さから、色ごとの光の減り方を計算する"), (t0 + NX * dt, t_e, "青はすぐ消え、赤が最後まで残る"), (t_e, 99, "ふちは明るく、真ん中は暗い赤。これが、耳が赤く透ける理由")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "透過", "28×14 画素の厚さから、色ごとの透過率を計算")
    return Build(st, name, "graphics/skin-hair/skin/thin-translucency.md", BEFORE, [1.5, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== Eye refraction
def EyeRefraction():
    name = "eye-refraction"
    st = Stage(name, "目の屈折: 角膜(透明な丸いドーム)の中を光が曲がり、虹彩が、本当の位置からずれて見える", duration=20.0, subtitle="断面。角膜の屈折率 n = 1.376。斜めから見るほど、虹彩の見える位置が、横にずれる")
    sc, root = st.scene, st.root
    n_c = 1.376
    depth = 3.1                                  # 角膜の表面から虹彩までの深さ(mm)
    SX = 38.0
    ox, oy = 480.0, 232.0                       # 角膜の頂点
    X = lambda x: ox + x * SX
    Y = lambda y: oy - y * SX * 1.0
    st.Panel(30, 96, 900, 330, "① 目の断面(上 = 外、下 = 目の中)", color=BLUE)
    # 角膜: 平らに近い近似(頂点まわり)
    root.add("line", x1=X(-5.5), y1=Y(0), x2=X(5.5), y2=Y(0), stroke="#38bdf8", stroke_width=5)
    sc.Text(root, X(-5.4), Y(0) - 8, "角膜の表面", size=12, weight=700, fill="#0284c7")
    root.add("rect", x=X(-5.5), y=Y(0), width=R(11 * SX), height=R(depth * SX), fill="#bae6fd", fill_opacity=0.35)
    root.add("line", x1=X(-5.5), y1=Y(-depth), x2=X(5.5), y2=Y(-depth), stroke="#7c3aed", stroke_width=5)
    sc.Text(root, X(-5.4), Y(-depth) + 18, "虹彩(色のついた円盤)", size=12, weight=700, fill="#7c3aed")
    root.add("circle", cx=R(X(0)), cy=R(Y(-depth)), r=7, fill=PURPLE)
    angles = [0.0, 20.0, 40.0, 60.0]
    rows = []
    for a in angles:
        th = math.radians(a)
        # 視線: 目の外から、角度 a で見る。虹彩の点 P(0, -depth) を見たい
        # 屈折して外に出る光線を逆にたどる: 内側角 = asin(sin(a)/n)
        tr = math.asin(math.sin(th) / n_c)
        # 虹彩上の点 P から、内側角 tr で上へ → 表面の点 x_s
        xs = depth * math.tan(tr)
        # 外側の直進(屈折がない場合)の見える位置: 表面の同じ点から角度 a で戻ると、虹彩の深さで x_ns
        x_ns = xs - depth * math.tan(th)
        shift = abs(x_ns - 0.0)
        rows.append((a, tr, xs, x_ns, shift))
    assert rows[1][4] < rows[2][4] < rows[3][4]
    t0, per = 1.0, 4.6
    for m, (a, tr, xs, x_ns, shift) in enumerate(rows):
        th = math.radians(a)
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        # 外の視線(表面から外へ)
        far = 3.0
        g.add("line", x1=R(X(xs)), y1=R(Y(0)), x2=R(X(xs + far * math.sin(th))), y2=R(Y(far * math.cos(th))), stroke=GREEN, stroke_width=3.5)
        # 目の中の光線(曲がっている)
        g.add("line", x1=R(X(xs)), y1=R(Y(0)), x2=R(X(0)), y2=R(Y(-depth)), stroke=RED, stroke_width=3.5)
        # 屈折がないと見なしたときの延長線
        g.add("line", x1=R(X(xs)), y1=R(Y(0)), x2=R(X(x_ns)), y2=R(Y(-depth)), stroke=GRAY, stroke_width=2.5, stroke_dasharray="6 5")
        g.add("circle", cx=R(X(x_ns)), cy=R(Y(-depth)), r=8, fill="#e9d5ff", stroke=PURPLE, stroke_width=2)
        sc.Text(g, X(x_ns), Y(-depth) + 24, "屈折を無視した位置", size=11, weight=700, fill=MUTED, anchor="middle")
        sc.Text(g, 50, 130, "見る角度 %d°" % a, size=20, weight=700, fill=PURPLE)
        sc.Text(g, 50, 156, "目の中での角度 %.1f°(sin θ ÷ 1.376 から)" % math.degrees(tr), size=14, weight=500, fill=TEXT)
        sc.Text(g, 50, 178, "虹彩の位置のずれ: %.2f mm" % shift, size=16, weight=700, fill=RED)
    st.Legend(50, 404, [(GREEN, "外から見る向き"), (RED, "目の中の光(曲がる)"), (GRAY, "曲がらないと考えたとき")])
    st.Text(40, 452, "ずれの大きさ:", size=15)
    st.Counter(150, 456, [(t0 + m * per + 0.3, int(round(100 * rows[m][4]))) for m in range(4)], size=24, fill=RED)
    st.Text(205, 456, "(0.01 mm 単位)", size=12, weight=500, fill=MUTED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.5, 340, 436, 590, 80, [("正面から見ると、ずれ 0。斜めになるほど、虹彩が横にずれて見える", 14, "#1e3a8a"), ("ゲームでは、虹彩のテクスチャ座標を、この分だけずらす(視差オフセット)", 13, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "角膜は透明なドーム。光は、その中で曲がる(屈折)"), (t0, t_e, "斜めから見ると、虹彩の見える位置が、本当の位置から、横にずれる"), (t_e, 99, "このずれを、テクスチャ座標の補正で作ると、目が「奥行きのある丸い物」に見える")], size=14, fill=MUTED, weight=500)
    for m, (a, tr, xs, x_ns, shift) in enumerate(rows):
        st.Note(t0 + m * per, "目", "角度 %d°: 内側 %.1f°、ずれ %.2f mm" % (a, math.degrees(tr), shift))
    return Build(st, name, "graphics/skin-hair/skin/eyes.md", BEFORE, [1.5, 4.5, 8.0, 11.0, 15.0, 19.0])


NAMES = ["preint-lut", "kajiya-lobes", "thin-transmit", "eye-refraction"]
FIGS = [PreintLut, KajiyaLobes, ThinTransmit, EyeRefraction]
