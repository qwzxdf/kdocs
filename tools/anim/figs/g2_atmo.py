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


def Curve(root, pts, col, width=3.5, dash=None, opacity=1):
    extra = {"stroke_dasharray": dash} if dash else {}
    return root.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=width, opacity=opacity, **extra)


def Rgbh(c):
    return Hex([255 * max(0.0, min(1.0, v)) for v in c])


def Enc(v):
    return max(0.0, min(1.0, v)) ** (1 / 2.2)


# ===================================================================== fog curves
def FogCurves():
    name = "fog-curves"
    st = Stage(name, "フォグの式: 線形・指数・指数の 2 乗。遠くの物が、どれだけ残って見えるかが、違う", duration=21.0, subtitle="距離 0〜200 m。物の色が残る割合(透過率)を、3 つの式で計算する。密度は、100 m で 5% しか残らないように、そろえる")
    sc, root = st.scene, st.root
    D = 200.0
    k_lin = 120.0
    k_exp = -math.log(0.05) / 100.0
    k_exp2 = math.sqrt(-math.log(0.05)) / 100.0
    f = {"linear": lambda d: max(0.0, 1 - d / k_lin), "exp": lambda d: math.exp(-k_exp * d), "exp2": lambda d: math.exp(-(k_exp2 * d) ** 2)}
    names = [("linear", "線形(開始 0・終了 120 m)", RED), ("exp", "指数 exp(−k·d)", GREEN), ("exp2", "指数の 2 乗 exp(−(k·d)²)", BLUE)]
    ds = [D * k / 100 for k in range(101)]
    st.Panel(30, 96, 640, 270, "① 透過率(1 = くっきり、0 = 霧の色)", color=BLUE)
    XX = lambda d: 70 + d / D * 570
    YY = lambda v: 340 - v * 220
    for d in (0, 50, 100, 150, 200):
        sc.Text(root, XX(d), 358, "%d m" % d, size=10, weight=500, fill=MUTED, anchor="middle")
        root.add("line", x1=R(XX(d)), y1=120, x2=R(XX(d)), y2=340, stroke=LIGHT, stroke_width=1)
    t0, per = 1.5, 4.2
    for m, (key, lab, col) in enumerate(names):
        p = Curve(root, [(XX(d), YY(f[key](d))) for d in ds], col, opacity=0)
        p.Show(t0 + m * per)
        sc.Text(root, XX(150) - 4, YY(f[key](150)) - 8 if key != "linear" else YY(0.0) - 8, lab, size=12, weight=700, fill=col, anchor="end", opacity=0).Show(t0 + m * per)
    # 物の見え方: 距離 20・50・100・150 の物(同じ赤)
    dsel = [20, 50, 100, 150]
    st.Panel(690, 96, 240, 270, "② 物の見え方(赤い物)", color=PURPLE)
    fog = (0.75, 0.8, 0.85)
    obj = (0.85, 0.2, 0.15)
    for m, (key, lab, col) in enumerate(names):
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.5)
        sc.Text(g, 706, 132 + m * 76, lab.split("(")[0], size=12, weight=700, fill=col)
        for k, d in enumerate(dsel):
            t = f[key](d)
            c = tuple(obj[i] * t + fog[i] * (1 - t) for i in range(3))
            g.add("rect", x=R(706 + k * 52), y=140 + m * 76, width=46, height=36, fill=Rgbh([Enc(v) for v in c]), stroke="#94a3b8", stroke_width=1)
            sc.Text(g, 706 + k * 52 + 23, 190 + m * 76, "%dm" % d, size=10, weight=500, fill=MUTED, anchor="middle")
    t100 = [f[k](100) for k, _, _ in names]
    t150 = [f[k](150) for k, _, _ in names]
    assert t150[0] == 0.0 and t150[1] > 0.0 and t150[2] < t150[1]
    st.Text(40, 400, "距離 150 m の物の、残る割合(%):", size=14)
    st.Counter(300, 404, [(t0 + m * per + 0.5, int(round(100 * t150[m]))) for m in range(3)], size=26, fill=PURPLE)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 40, 432, 880, 76, [("線形は、終了距離で、完全に霧の色。指数は、遠くでも、少し残る(150 m で %d%%)" % round(100 * t150[1]), 14, "#1e3a8a"), ("指数の 2 乗は、近くはくっきり、あるところで、一気に霞む。濃い霧の感じに合う(150 m で %d%%)" % round(100 * t150[2]), 13, TEXT), ("物理的には、指数(Beer の法則)が基本。ほかは、見た目の調整用", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "距離に応じて、物の色を、霧の色へ近づける"), (t0, t_e, "式によって、遠くの物の残り方が、違う"), (t_e, 99, "100 m で 5% にそろえても、近くと遠くの見え方が違う")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "フォグ", "150 m の残り: 線形 %d%% / 指数 %d%% / 指数² %d%%" % tuple(round(100 * x) for x in t150))
    return Build(st, name, "graphics/atmosphere/aerial-fog/fog-equation.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 15.0, 20.0])


# ===================================================================== beer rgb
def BeerRgb():
    name = "beer-rgb"
    st = Stage(name, "空気遠近法: 青の光ほど散って減り、遠くの山は、青く霞んで、薄くなる(物の色 + 空気の色)", duration=22.0, subtitle="同じ茶色の山が、距離 0.5〜48 km に並ぶ。色ごとに、減る割合と、空気が足す光(空の青)を計算して、1 つずつ見る")
    sc, root = st.scene, st.root
    sig = {"R": 0.012, "G": 0.028, "B": 0.065}      # 1 km あたりの減衰
    sky = (0.45, 0.65, 1.0)
    obj = (0.45, 0.30, 0.20)
    dist = [0.5, 1, 2, 4, 8, 12, 18, 25, 33, 40, 48]
    cols_t = []
    cols_m = []
    for d in dist:
        T = tuple(math.exp(-sig[c] * d) for c in "RGB")
        direct = tuple(obj[i] * T[i] for i in range(3))
        scat = tuple(sky[i] * (1 - T[i]) for i in range(3))
        cols_t.append(T)
        cols_m.append(tuple(direct[i] + scat[i] for i in range(3)))
    assert cols_t[-1][0] > cols_t[-1][2]
    contrast = [abs(c[0] - c[2]) for c in cols_m]
    X0, cw = 50.0, 78.0
    t0, dts = 1.5, 0.7
    # 山(三角形)を並べる
    st.Panel(30, 96, 900, 160, "① 山の色(左 = 近い、右 = 遠い)", color=BLUE)
    root.add("rect", x=32, y=98, width=896, height=156, fill=Rgbh([Enc(v) for v in sky]), fill_opacity=0.35)
    for k, d in enumerate(dist):
        x = X0 + k * cw
        tri = root.add("polygon", points="%s,%s %s,%s %s,%s" % (R(x), 240, R(x + cw * 0.5), 150, R(x + cw), 240), fill="#e5e7eb", opacity=0)
        tri.Set(t0 + k * dts, "fill", Rgbh([Enc(v) for v in cols_m[k]]))
        tri.Show(t0 + k * dts)
        sc.Text(root, x + cw / 2, 252, ("%g km" % d), size=10, weight=500, fill=MUTED, anchor="middle", opacity=0).Show(t0 + k * dts)
    # 色ごとの透過率
    st.Panel(30, 276, 440, 190, "② 色ごとに残る光 T = exp(−σ·距離)", color=PURPLE)
    XX = lambda d: 60 + d / 48 * 390
    YY = lambda v: 446 - v * 130
    t_c = t0 + len(dist) * dts + 0.5
    for c, col in zip("RGB", [RED, GREEN, BLUE]):
        p = Curve(root, [(XX(d), YY(math.exp(-sig[c] * d))) for d in [k / 2 for k in range(97)]], col, opacity=0)
        p.Show(t_c + "RGB".index(c) * 0.9)
        sc.Text(root, XX(48) + 4, YY(math.exp(-sig[c] * 48)) + 4, "%s %d%%" % (c, round(100 * math.exp(-sig[c] * 48))), size=11, weight=700, fill=col, opacity=0).Show(t_c + "RGB".index(c) * 0.9)
    st.Panel(490, 276, 440, 190, "③ 遠い山が、物の色と、空の色の、どちらに近いか", color=RED)
    for k_, (lab, cc) in enumerate([("48 km 先の山", cols_m[-1]), ("空の色", sky), ("近い山(0.5 km)", cols_m[0])]):
        y = 312 + k_ * 44
        g = root.add("g", opacity=0)
        g.Show(t_c + 3.0 + k_ * 0.8)
        g.add("rect", x=510, y=y, width=60, height=32, fill=Rgbh([Enc(v) for v in cc]), stroke="#94a3b8", stroke_width=1.5)
        sc.Text(g, 582, y + 21, lab + "   R %.2f / G %.2f / B %.2f" % cc, size=13, weight=700, fill=TEXT)
    st.Text(40, 494, "遠い山と空の、色の差(R の差 + G の差 + B の差):", size=13)
    dsky = sum(abs(cols_m[-1][i] - sky[i]) for i in range(3))
    dobj = sum(abs(cols_m[0][i] - sky[i]) for i in range(3))
    st.Counter(430, 498, [(t_c + 3.0, int(round(100 * dobj))), (t_c + 5.4, int(round(100 * dsky)))], size=24, fill=RED)
    st.Text(480, 498, "(×0.01。近い山 → 48 km 先)", size=12, weight=500, fill=MUTED)
    t_e = t_c + 6.5
    st.Caption(30, 534, [(0.0, t0, "遠くの物は、色が薄くなり、青みを帯びる(空気遠近法)"), (t0, t_c, "距離を増やすと、山の色が、空の色へ近づく"), (t_c, t_e, "赤は残り、青は先に消える。代わりに、空気が、青い光を足す"), (t_e, 99, "遠景を空の色に近づけると、奥行きが出る")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "空気遠近法", "48 km: 残る光 R %d%% / G %d%% / B %d%%、空との差 %.2f → %.2f" % ((100 * cols_t[-1][0], 100 * cols_t[-1][1], 100 * cols_t[-1][2]) + (dobj, dsky)))
    return Build(st, name, "graphics/atmosphere/aerial-fog/physical.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 21.0])


# ===================================================================== cloud coverage
def CloudCoverage():
    name = "cloud-coverage"
    st = Stage(name, "雲の量(カバレッジ): ノイズから、しきい値を引いて、残った所だけを、雲にする", duration=21.0, subtitle="32×12 のノイズ(0〜1)。カバレッジ 0.2・0.5・0.8 で、雲になる画素の割合と、雲のつながり(塊の数)を計算する")
    sc, root = st.scene, st.root
    NX, NY, CS = 32, 12, 14.0
    r = Lcg(9)
    base = [[r.U() for _ in range(NX // 4 + 2)] for _ in range(NY // 4 + 2)]

    def N(x, y):
        fx, fy = x / 4, y / 4
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = base[j][i] * (1 - tx) + base[j][i + 1] * tx
        b = base[j + 1][i] * (1 - tx) + base[j + 1][i + 1] * tx
        return a * (1 - ty) + b * ty
    noise = [[0.6 * N(i, j) + 0.4 * N(i * 2.1 % 28, j * 2.1 % 8) for i in range(NX)] for j in range(NY)]
    lo = min(min(r_) for r_ in noise)
    hi = max(max(r_) for r_ in noise)
    noise = [[(v - lo) / (hi - lo) for v in row] for row in noise]
    covs = [0.2, 0.5, 0.8]

    def Dens(v, c):
        return max(0.0, min(1.0, (v - (1 - c)) / 0.25))
    dens = [[[Dens(v, c) for v in row] for row in noise] for c in covs]
    frac = [sum(1 for row in d for v in row if v > 0.05) / (NX * NY) for d in dens]
    assert frac[0] < frac[1] < frac[2]

    def Blobs(d):
        seen = set(); n_ = 0
        for j in range(NY):
            for i in range(NX):
                if d[j][i] > 0.05 and (i, j) not in seen:
                    n_ += 1
                    st_ = [(i, j)]
                    while st_:
                        a, b = st_.pop()
                        if (a, b) in seen or not (0 <= a < NX and 0 <= b < NY) or d[b][a] <= 0.05:
                            continue
                        seen.add((a, b))
                        st_ += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]
        return n_
    blobs = [Blobs(d) for d in dens]
    px = [30, 335, 640]
    t0, per = 1.5, 4.5
    st.Panel(30, 96, NX * 9.0 + 6, NY * 9.0 + 6, "元のノイズ", color=GRAY)
    g0 = Grid(st, 33, 99, NX, NY, 9.0, base="#e5e7eb")
    for j in range(NY):
        for i in range(NX):
            g0.Paint(i, j, 0.3, Gray(1 - noise[j][i]))
    g0.Flush()
    for m, c in enumerate(covs):
        x = [330, 640, 330][m]
        y = [96, 96, 230][m]
        st.Panel(x, y, NX * 9.0 + 6, NY * 9.0 + 6, "カバレッジ %.1f" % c, color=[BLUE, GREEN, RED][m])
        g = Grid(st, x + 3, y + 3, NX, NY, 9.0, base="#7dd3fc")
        for j in range(NY):
            for i in range(NX):
                g.Paint(i, j, t0 + m * per + 0.02 * (i + j), Mix("#7dd3fc", "#ffffff", dens[m][j][i]))
        g.Flush()
    st.Text(40, 262, "雲になる画素の割合(%):", size=14)
    st.Counter(240, 266, [(t0 + m * per + 0.02 * (NX + NY), int(round(100 * frac[m]))) for m in range(3)], size=26, fill=PURPLE)
    st.Text(40, 300, "雲の塊の数:", size=14)
    st.Counter(240, 304, [(t0 + m * per + 0.02 * (NX + NY), blobs[m]) for m in range(3)], size=26, fill=BLUE)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 330, 230, 600, 90, [("カバレッジを上げると、雲の割合が、%d%% → %d%% → %d%% と増え、塊が、つながる(塊の数 %d → %d → %d)" % (round(100 * frac[0]), round(100 * frac[1]), round(100 * frac[2]), blobs[0], blobs[1], blobs[2]), 14, "#1e3a8a"), ("濃さ = (ノイズ − (1 − カバレッジ)) ÷ 幅 を 0〜1 に切る。カバレッジは、天気で動かす", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "同じノイズから、雲の量を、1 つのつまみで決める"), (t0, t_e, "しきい値より大きい所だけが、雲になる"), (t_e, 99, "天気の遷移は、カバレッジを動かすだけ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "カバレッジ", "割合 %s、塊 %s" % ("/".join("%d%%" % round(100 * f_) for f_ in frac), "/".join(map(str, blobs))))
    return Build(st, name, "graphics/atmosphere/clouds/density-model.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== cloud profiles
def CloudProfiles():
    name = "cloud-profiles"
    st = Stage(name, "雲の高さ方向の形: 雲の種類ごとに、高さに応じた、密度の山(プロファイル)を掛ける", duration=21.0, subtitle="高さ 0〜1(雲の層の下端〜上端)。積雲・層雲・積乱雲の密度の形と、垂直に積分した「厚さ」を、計算する")
    sc, root = st.scene, st.root
    sm = lambda a, b, x: max(0.0, min(1.0, (x - a) / (b - a))) ** 2 * (3 - 2 * max(0.0, min(1.0, (x - a) / (b - a))))
    prof = {
        "層雲(薄く平ら)": lambda h: sm(0.0, 0.1, h) * (1 - sm(0.2, 0.3, h)),
        "積雲(もこもこ)": lambda h: sm(0.0, 0.1, h) * (1 - sm(0.6, 0.9, h)),
        "積乱雲(高く伸びる)": lambda h: sm(0.0, 0.07, h) * (1 - sm(0.9, 1.0, h)),
    }
    cols = [BLUE, GREEN, RED]
    hs = [k / 100 for k in range(101)]
    thick = {k: sum(f(h) for h in hs) / 100 for k, f in prof.items()}
    ks = list(prof.keys())
    assert thick[ks[0]] < thick[ks[1]] < thick[ks[2]]
    X0, W = 110.0, 440.0
    st.Panel(30, 96, 560, 310, "① 高さと密度(横 = 密度、縦 = 高さ)", color=BLUE)
    XX = lambda v: X0 + v * W
    YY = lambda h: 380 - h * 250
    root.add("line", x1=X0, y1=130, x2=X0, y2=380, stroke="#94a3b8", stroke_width=2)
    sc.Text(root, 70, 134, "上端", size=11, weight=700, fill=MUTED)
    sc.Text(root, 70, 384, "下端", size=11, weight=700, fill=MUTED)
    t0, per = 1.5, 4.8
    for m, k in enumerate(ks):
        pts = [(XX(prof[k](h)), YY(h)) for h in hs]
        p = Curve(root, pts, cols[m], opacity=0)
        p.Show(t0 + m * per)
        fill = root.add("path", d=Poly([(X0, YY(0))] + pts + [(X0, YY(1))]) + " Z", fill=cols[m], fill_opacity=0.12, opacity=0)
        fill.Show(t0 + m * per)
    st.Panel(620, 96, 310, 310, "② 垂直に積分した厚さ", color=PURPLE)
    for m, k in enumerate(ks):
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.8)
        sc.Text(g, 636, 136 + m * 90, k, size=14, weight=700, fill=cols[m])
        w = thick[k] / thick[ks[2]] * 250
        g.add("rect", x=636, y=146 + m * 90, width=R(w), height=22, fill=cols[m], opacity=0.85)
        sc.Text(g, 636 + w + 8, 163 + m * 90, "%.2f" % thick[k], size=13, weight=700, fill=cols[m])
        sc.Text(g, 636, 192 + m * 90, "密度のピーク: 高さ %.2f" % max(hs, key=lambda h: prof[k](h) - 0.001 * h), size=11, weight=500, fill=MUTED)
    st.Text(40, 440, "垂直の厚さ(×100):", size=14)
    st.Counter(200, 444, [(t0 + m * per + 0.8, int(round(100 * thick[k]))) for m, k in enumerate(ks)], size=26, fill=PURPLE)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 330, 424, 600, 90, [("同じ天気の値でも、種類ごとに、高さ方向の密度が違う", 14, "#1e3a8a"), ("厚さの比: 層雲 %.2f : 積雲 %.2f : 積乱雲 %.2f。厚いほど、暗く、影が濃い" % tuple(thick[k] for k in ks), 13, TEXT), ("雲の形 = 横の形(ノイズ)× 高さの形(プロファイル)", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "雲の層の中の、高さごとの密度を決める"), (t0, t_e, "種類ごとに、密度の山の位置と幅が違う"), (t_e, 99, "プロファイルを掛けると、雲の底は平らに、頂上は丸くなる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "プロファイル", "厚さ: " + " / ".join("%s %.2f" % (k, thick[k]) for k in ks))
    return Build(st, name, "graphics/atmosphere/clouds/layers.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== beer powder
def CloudBeerPowder():
    name = "cloud-beer-powder"
    st = Stage(name, "雲の光: Beer の法則(奥へ進むと暗い)に、Powder 効果(縁は暗い)を掛けて、雲らしい明暗にする", duration=21.0, subtitle="雲の中へ、光が深さ d まで入る。Beer = exp(−k·d)、Powder = 1 − exp(−2k·d)。縁(浅い所)と奥の明るさを、式で計算する")
    sc, root = st.scene, st.root
    k = 1.2
    D = 4.0
    ds = [D * i / 80 for i in range(81)]
    beer = lambda d: math.exp(-k * d)
    powder = lambda d: 1 - math.exp(-2 * k * d)
    both = lambda d: 2 * beer(d) * powder(d)
    peak_d = max(ds, key=both)
    assert abs(peak_d - math.log(2) / (2 * k) * 1) < 0.1 or peak_d > 0.1
    st.Panel(30, 96, 560, 260, "① 光が入る深さと、明るさ", color=BLUE)
    XX = lambda d: 70 + d / D * 500
    YY = lambda v: 330 - v * 200
    for d in (0, 1, 2, 3, 4):
        sc.Text(root, XX(d), 348, "%d" % d, size=10, weight=500, fill=MUTED, anchor="middle")
    sc.Text(root, 580, 348, "深さ d", size=10, weight=500, fill=MUTED, anchor="end")
    curves = [("Beer(奥へ減る)", beer, GREEN), ("Powder(縁は暗い)", powder, AMBER), ("Beer × Powder × 2", both, RED)]
    t0, per = 1.5, 4.5
    for m, (lab, f, col) in enumerate(curves):
        p = Curve(root, [(XX(d), YY(f(d))) for d in ds], col, opacity=0)
        p.Show(t0 + m * per)
        sc.Text(root, XX(3.9), YY(f(3.9)) - 8, lab, size=12, weight=700, fill=col, anchor="end", opacity=0).Show(t0 + m * per)
    # 雲の断面(帯)
    st.Panel(620, 96, 310, 260, "② 雲の断面(左 = 縁、右 = 奥)", color=PURPLE)
    N = 24
    for r_, (lab, f, col) in enumerate(curves):
        y = 140 + r_ * 70
        sc.Text(root, 636, y - 4, lab, size=11, weight=700, fill=col)
        g = Grid(st, 636, y, N, 1, 11.5, base="#e5e7eb", stroke="#94a3b8", cell_h=34.0)
        for i in range(N):
            d = D * (i + 0.5) / N
            g.Paint(i, 0, t0 + r_ * per + 0.04 * i, Gray(min(1.0, f(d)) * 0.95 + 0.04))
        g.Flush()
    edge, deep = both(0.1), both(3.0)
    st.Text(40, 390, "縁の明るさ(d = 0.1)/ 最も明るい所 / 奥(d = 3):", size=14)
    sc.Text(root, 40, 420, "Beer だけ: %.2f / %.2f / %.2f" % (beer(0.1), max(beer(d) for d in ds), beer(3.0)), size=14, weight=700, fill=GREEN, opacity=0).Show(t0)
    sc.Text(root, 40, 444, "Beer × Powder × 2: %.2f / %.2f(深さ %.2f)/ %.2f" % (both(0.1), max(both(d) for d in ds), peak_d, both(3.0)), size=14, weight=700, fill=RED, opacity=0).Show(t0 + 2 * per)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 430, 400, 500, 90, [("Beer だけだと、縁がいちばん明るい。Powder を掛けると、縁が暗く、少し奥で最大(深さ %.2f)" % peak_d, 13, "#1e3a8a"), ("雲の縁が暗く縁取られる、ふわふわした感じが出る(太陽に向かう側では弱い)", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "雲に入った光は、進むほど、吸われて減る(Beer の法則)"), (t0, t0 + per, "Beer だけでは、縁が、いちばん明るく見える"), (t0 + per, t_e, "縁は、まだ光が散っていないので暗い(Powder)。掛けると、縁だけが暗くなる"), (t_e, 99, "雲らしい、中が明るく、縁が少し暗い見た目")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "Beer-Powder", "縁 %.2f / 最大 %.2f / 奥 %.2f(Beer × Powder)" % (edge, max(both(d) for d in ds), deep))
    return Build(st, name, "graphics/atmosphere/clouds/lighting.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== cloud bayer
def CloudBayer():
    name = "cloud-bayer"
    st = Stage(name, "雲の時間蓄積: 1 フレームに 16 分の 1 の画素だけ描き、残りは、前のフレームの結果を、動きに合わせて使う", duration=22.0, subtitle="8×8 画素。更新する画素を、Bayer の順で 1 つずつ(4×4 パターン)。画素ごとの「データの古さ」と、全画素が新しくなるまでのフレーム数を数える")
    sc, root = st.scene, st.root
    NX, NY, CS = 8, 8, 40.0
    bay = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
    order = lambda i, j: bay[(i % 4) + 4 * (j % 4)]
    F = 16
    age = [[F] * NX for _ in range(NY)]
    snaps = []
    cost_naive = NX * NY * F
    cost_bayer = 0
    for f in range(F):
        for j in range(NY):
            for i in range(NX):
                age[j][i] += 1
        upd = 0
        for j in range(NY):
            for i in range(NX):
                if order(i, j) == f:
                    age[j][i] = 0
                    upd += 1
        cost_bayer += upd
        snaps.append(([r[:] for r in age], upd))
    maxage = [max(max(r) for r in a) for a, _ in snaps]
    assert snaps[-1][0] and max(max(r) for r in snaps[-1][0]) <= 15 and cost_bayer == NX * NY
    st.Panel(30, 96, NX * CS + 6, NY * CS + 6, "画素の「データの古さ」(0 = 今フレームに更新)", color=BLUE)
    g = Grid(st, 33, 99, NX, NY, CS, base="#e5e7eb")
    t0, dt = 1.5, 1.05
    for f in range(F):
        a, upd = snaps[f]
        for j in range(NY):
            for i in range(NX):
                v = a[j][i]
                col = "#f97316" if v == 0 else Mix("#bbf7d0", "#1e3a8a", min(1.0, v / 15))
                g.Paint(i, j, t0 + f * dt, col)
    g.Flush()
    g.Lines(color="#ffffff", opacity=0.4)
    st.Text(30 + NX * CS + 30, 130, "橙 = このフレームに更新した画素(4 個)", size=13, weight=700, fill="#c2410c")
    st.Text(30 + NX * CS + 30, 156, "緑 → 青 = 前に更新してから、経ったフレーム数", size=13, weight=700, fill=BLUE)
    st.Text(30 + NX * CS + 30, 200, "フレーム:", size=15)
    st.Counter(30 + NX * CS + 130, 204, [(t0 + f * dt, f + 1) for f in range(F)], size=26, fill=PURPLE)
    st.Text(30 + NX * CS + 30, 244, "いちばん古い画素の古さ:", size=14)
    st.Counter(30 + NX * CS + 230, 248, [(t0 + f * dt, min(15, maxage[f])) for f in range(F)], size=24, fill=BLUE)
    st.Text(30 + NX * CS + 30, 286, "描いた画素の合計:", size=14)
    st.Counter(30 + NX * CS + 190, 290, [(t0 + f * dt, (f + 1) * (NX * NY // 16)) for f in range(F)], size=24, fill=RED)
    t_e = t0 + F * dt
    st.Box(t_e, 30, 440, 900, 72, [("1 フレームに描く画素: %d / %d(%d 分の 1)。%d フレームで、全画素が更新される" % (NX * NY // 16, NX * NY, 16, 16), 15, "#1e3a8a"), ("毎フレーム全部描くと %d 回 → 4×4 パターンで %d 回(16 倍安い)。残りは、再投影した、前フレームの結果を使う" % (cost_naive // 16 * 1, NX * NY // 16), 13, TEXT), ("動くと再投影がずれて、ゴーストが出る → 近傍クランプ・履歴の重みの調整で、抑える", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "雲のレイマーチは重いので、全画素は、毎フレーム描けない"), (t0, t_e, "4×4 の順で、離れた画素を 1 つずつ更新する(Bayer)"), (t_e, 99, "16 フレームで、全画素が新しくなる。コストは 1/16")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "Bayer 更新", "1 フレーム %d 画素、16 フレームで全画素" % (NX * NY // 16))
    return Build(st, name, "graphics/atmosphere/clouds/temporal.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 21.0])


# ===================================================================== radial streak
def RadialStreak():
    name = "radial-streak"
    st = Stage(name, "放射ぼかし: 光源から画素へ向かう線の上で、何回か読んで足す。読む回数が少ないと、筋が途切れる", duration=21.0, subtitle="光源から 1 本の線(48 画素)。途中に細い遮蔽物が 3 本。各画素が、光源の方向へ N 回読んで、明るさを足す")
    sc, root = st.scene, st.root
    n = 48
    light_at = 0
    occl = [False] * n
    for i in (10, 11, 22, 23, 24, 36):
        occl[i] = True
    bright = [0.0 if occl[i] else 1.0 for i in range(n)]
    density = 0.8

    def Streak(N, jitter=False):
        out = []
        for i in range(n):
            acc = 0.0
            for s in range(N):
                t = (s + (0.5 if not jitter else (0.37 + 0.13 * (i % 5)))) / N
                j = int(i * (1 - t * density))
                acc += bright[max(0, min(n - 1, j))] * (1 - t * 0.5)
            out.append(acc / N)
        return out
    truth = Streak(512)
    cases = [("N = 4", Streak(4), RED), ("N = 8", Streak(8), AMBER), ("N = 16", Streak(16), GREEN), ("N = 64", Streak(64), BLUE), ("正解(N = 512)", truth, GRAY)]
    errs = [sum(abs(a - b) for a, b in zip(v, truth)) / n for _, v, _ in cases]
    assert errs[0] > errs[1] > errs[2] > errs[3]
    CW, X0 = 17.0, 60.0
    t0, per = 1.5, 3.4
    st.Text(X0, 100, "遮る物(黒)と、光(白)。左端が光源に近い", size=13, weight=700, fill=GRAY)
    g0 = Grid(st, X0, 106, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=22.0)
    for i in range(n):
        g0.Paint(i, 0, 0.3, "#111827" if occl[i] else "#fef3c7")
    g0.Flush()
    for m, (lab, v, col) in enumerate(cases):
        y = 160 + m * 54
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=26.0)
        for i in range(n):
            g.Paint(i, 0, 0.3 if m == 4 else t0 + m * per + i * 0.04, Gray(1 - v[i] * 0.9))
        g.Flush()
        if m < 4:
            gx = root.add("g", opacity=0)
            gx.Show(t0 + m * per + 2.0)
            sc.Text(gx, X0 + n * CW + 8, y + 18, "ずれ %.3f" % errs[m], size=12, weight=700, fill=col)
    st.Text(40, 440, "読み込み(1 画素あたり):", size=14)
    st.Counter(240, 444, [(t0 + m * per, N) for m, N in enumerate([4, 8, 16, 64])], size=26, fill=PURPLE)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 330, 424, 600, 90, [("N が少ないと、筋が、飛び飛びの点線のようになる(ずれ %.3f)。N = 64 で、ほぼなめらか(%.3f)" % (errs[0], errs[3]), 14, "#1e3a8a"), ("ふつうは N = 32〜64。読み込みは、画面全体 × N なので、重い。ジッターで、帯を、ノイズに変える手もある", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "光源に向かう線の上を、少しずつ読んで、明るさを足す"), (t0, t_e, "読む回数が少ないと、遮蔽物の影が、飛び飛びになる"), (t_e, 99, "回数を増やすと、筋がなめらかになる(コストも増える)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "放射ぼかし", "ずれ: " + " / ".join("%.3f" % e for e in errs[:4]))
    return Build(st, name, "graphics/atmosphere/god-rays/radial-blur.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 20.0])


# ===================================================================== decay weights
def DecayWeights():
    name = "decay-weights"
    st = Stage(name, "放射ぼかしの減衰(decay): 1 に近いほど、遠くの光も効いて、筋が長く伸びる", duration=21.0, subtitle="光源から 64 画素の線。各画素が、光源の方向へ 32 回読んで、decay^i の重みで足す。光源だけが明るいときの、筋の明るさ")
    sc, root = st.scene, st.root
    n = 64
    N = 32
    bright = [0.0] * n
    bright[0] = 1.0
    bright[1] = 0.8
    bright[2] = 0.5
    decays = [0.90, 0.95, 0.97, 0.99]

    def Streak(dc):
        out = []
        for i in range(n):
            acc = 0.0
            wsum = 0.0
            for s in range(N):
                t = (s + 0.5) / N
                j = int(i * (1 - t))
                w = dc ** s
                acc += bright[max(0, j)] * w
            out.append(acc / N)
        return out
    prof = [Streak(d) for d in decays]
    reach = [next((i for i in range(n - 1, -1, -1) if p[i] > 0.02), 0) for p in prof]
    assert reach[3] > reach[0]
    X0, W = 70.0, 560.0
    st.Panel(30, 96, 640, 260, "① 光源からの距離と、筋の明るさ", color=BLUE)
    XX = lambda i: X0 + i / (n - 1) * W
    ymax = max(max(p) for p in prof)
    YY = lambda v: 330 - v / ymax * 200
    cols = [RED, AMBER, GREEN, BLUE]
    t0, per = 1.5, 4.2
    for m, dc in enumerate(decays):
        p = Curve(root, [(XX(i), YY(v)) for i, v in enumerate(prof[m])], cols[m], opacity=0)
        p.Show(t0 + m * per)
        sc.Text(root, XX(n - 1) - 4, YY(prof[m][n - 4]) - 10, "decay %.2f" % dc, size=12, weight=700, fill=cols[m], anchor="end", opacity=0).Show(t0 + m * per)
    root.add("line", x1=X0, y1=R(YY(0.02)), x2=X0 + W, y2=R(YY(0.02)), stroke=GRAY, stroke_width=1.5, stroke_dasharray="4 4")
    sc.Text(root, X0 + 6, R(YY(0.02)) - 4, "見えなくなる(0.02)", size=10, weight=700, fill=GRAY)
    st.Panel(690, 96, 240, 260, "筋が届く距離(画素)", color=PURPLE)
    for m, dc in enumerate(decays):
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.8)
        sc.Text(g, 706, 136 + m * 52, "decay %.2f" % dc, size=13, weight=700, fill=cols[m])
        sc.Text(g, 706, 160 + m * 52, "%d 画素" % reach[m], size=20, weight=700, fill=cols[m])
    st.Text(40, 392, "筋が届く距離:", size=15)
    st.Counter(180, 396, [(t0 + m * per + 0.8, reach[m]) for m in range(4)], size=26, fill=PURPLE)
    st.Text(230, 396, "画素", size=14)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 40, 430, 880, 76, [("decay 0.90 → 0.99 で、筋が届く距離が %d → %d 画素" % (reach[0], reach[3]), 15, "#1e3a8a"), ("重み decay^i は、遠くを読むほど小さい。1 に近いと、遠くの光源の光も、そのまま混ざって、筋が長い", 13, TEXT), ("伸ばしすぎると、画面全体が白っぽくぼける。強さ(weight)と一緒に調整する", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "遠くを読んだ分の重みを、decay の累乗で、弱めていく"), (t0, t_e, "decay が 1 に近いほど、筋が、遠くまで伸びる"), (t_e, 99, "伸ばしすぎず、見た目で決める")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "decay", "届く距離: " + " / ".join("%d" % r_ for r_ in reach))
    return Build(st, name, "graphics/atmosphere/god-rays/tuning.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== rayleigh wavelength
def RayleighWavelength():
    name = "rayleigh-wavelength"
    st = Stage(name, "レイリー散乱: 散る量は、波長の 4 乗に反比例する。だから、昼の空は青く、夕日は赤い", duration=22.0, subtitle="波長 400〜700 nm の光。散る量を計算して、空の色(散った光)と、夕日の色(残った光)を、作る")
    sc, root = st.scene, st.root
    wl = list(range(400, 701, 20))
    scat = [(550.0 / w) ** 4 for w in wl]
    smax = max(scat)
    # 目の感度(R, G, B)を、ガウスで近似
    def Resp(w):
        r = math.exp(-((w - 600) / 45.0) ** 2) + 0.15 * math.exp(-((w - 450) / 30.0) ** 2)
        g = math.exp(-((w - 545) / 45.0) ** 2)
        b = math.exp(-((w - 450) / 30.0) ** 2)
        return r, g, b
    def Spectrum(f):
        acc = [0.0, 0.0, 0.0]
        for w, s in zip(wl, f):
            rr = Resp(w)
            for k in range(3):
                acc[k] += rr[k] * s
        return acc
    sun = [1.0] * len(wl)
    sky_raw = Spectrum([s for s in scat])
    sky_n = [v / max(sky_raw) for v in sky_raw]
    # 空気の量 m の分だけ通った太陽
    def Sunset(m, k=0.35):
        T = [math.exp(-k * m * s) for s in scat]
        raw = Spectrum(T)
        return [v / max(raw) for v in raw], T
    ms = [0.0, 1.0, 5.0, 12.0]
    sets = [Sunset(m) for m in ms]
    assert sky_n[2] > sky_n[0]
    assert sets[3][0][0] > sets[3][0][2]
    st.Panel(30, 96, 560, 200, "① 波長ごとに散る量(550 nm を 1 とする)", color=BLUE)
    bw = 520 / len(wl)
    for k, (w, s) in enumerate(zip(wl, scat)):
        h = s / smax * 150
        cr = Resp(w)
        col = Rgbh([cr[0] * 0.9, cr[1] * 0.9, cr[2] * 0.95 + 0.05])
        r_ = root.add("rect", x=R(54 + k * bw), y=R(270 - h), width=R(bw - 2), height=R(h), fill=Hex([200 * (w >= 580), 150 * (500 <= w < 600) + 60, 255 * (w < 500)]) if False else col, opacity=0)
        r_.Show(1.5 + k * 0.1)
        if k % 3 == 0:
            sc.Text(root, 54 + k * bw + bw / 2, 288, "%d" % w, size=9, weight=500, fill=MUTED, anchor="middle")
    st.Text(54, 118, "400 nm(青)は 700 nm(赤)の %.1f 倍 散る" % (scat[0] / scat[-1]), size=13, weight=700, fill=BLUE, opacity=0).Show(1.5 + len(wl) * 0.1)
    st.Panel(610, 96, 320, 200, "② 昼の空の色(散った光)", color=PURPLE)
    t_s = 1.5 + len(wl) * 0.1 + 0.8
    g = root.add("g", opacity=0)
    g.Show(t_s)
    g.add("rect", x=630, y=130, width=280, height=90, fill=Rgbh([Enc(v) for v in sky_n]), stroke="#94a3b8", stroke_width=1.5)
    sc.Text(g, 630, 244, "R %.2f / G %.2f / B %.2f" % tuple(sky_n), size=14, weight=700, fill=TEXT)
    sc.Text(g, 630, 268, "散る量の多い、短い波長が、空の色になる", size=12, weight=500, fill=MUTED)
    st.Panel(30, 316, 900, 150, "③ 太陽の光が、空気の中を通った後の色(空気の量 = 天頂の何倍か)", color=RED)
    t_c = t_s + 3.0
    for k, (m, (c, T)) in enumerate(zip(ms, sets)):
        x = 50 + k * 220
        gg = root.add("g", opacity=0)
        gg.Show(t_c + k * 2.4)
        gg.add("circle", cx=x + 36, cy=388, r=32, fill=Rgbh([Enc(v) for v in c]), stroke="#334155", stroke_width=2)
        sc.Text(gg, x + 82, 372, "空気 %g 倍" % m if m else "空気なし", size=13, weight=700, fill=INK)
        sc.Text(gg, x + 82, 394, "R %.2f G %.2f B %.2f" % tuple(c), size=11, weight=500, fill=TEXT)
        sc.Text(gg, x + 82, 414, ["元の太陽(白)", "昼(少し黄色)", "夕方(橙)", "夕焼け(赤)"][k], size=12, weight=700, fill=RED)
    t_e = t_c + 4 * 2.4 + 0.5
    st.Box(t_e, 40, 478, 880, 40, [("青い光は、空の方へ散り、赤い光は、太陽の方向に残る", 14, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "光の波長によって、空気で散る量が違う(波長の 4 乗に反比例)"), (1.5, t_s, "短い青は、赤の約 %.0f 倍 散る" % (scat[0] / scat[-1])), (t_s, t_c, "散った光を見ると、空は青い"), (t_c, 99, "空気を長く通った太陽は、青が抜けて、赤くなる")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "レイリー", "400 nm / 700 nm の散る量の比 %.1f 倍、空の色 R %.2f G %.2f B %.2f" % ((scat[0] / scat[-1],) + tuple(sky_n)))
    return Build(st, name, "graphics/atmosphere/scattering/atmosphere-model.md", BEFORE, [2.0, 4.0, 7.0, 11.0, 15.0, 21.0])


# ===================================================================== multi scatter
def MultiScatterSum():
    name = "multi-scatter-sum"
    st = Stage(name, "多重散乱: 光は、何度も散る。アルベド(反射する割合)が高いほど、何回目まで足さないと、足りない", duration=21.0, subtitle="1 回目の散乱を 1 とする。散乱 k 回目の光は、アルベド^(k−1)。アルベド 0.5・0.8・0.95 で、合計がどう積み上がるかを計算する")
    sc, root = st.scene, st.root
    albedos = [0.5, 0.8, 0.95]
    K = 24
    sums = [[sum(a ** j for j in range(k + 1)) for k in range(K)] for a in albedos]
    limit = [1 / (1 - a) for a in albedos]
    need = [next(k + 1 for k in range(200) if sum(a ** j for j in range(k + 1)) >= 0.95 * (1 / (1 - a))) for a in albedos]
    assert need[0] < need[1] < need[2] and need[2] > 10
    st.Panel(30, 96, 640, 280, "① 散乱を k 回足したときの合計", color=BLUE)
    XX = lambda k: 70 + k / (K - 1) * 570
    ymax = 22.0
    YY = lambda v: 350 - v / ymax * 230
    cols = [GREEN, AMBER, RED]
    for kk in (1, 5, 10, 15, 20):
        sc.Text(root, XX(kk - 1), 366, "%d" % kk, size=10, weight=500, fill=MUTED, anchor="middle")
    t0, per = 1.5, 4.8
    for m, a in enumerate(albedos):
        pts = [(XX(k), YY(sums[m][k])) for k in range(K)]
        p = Curve(root, pts, cols[m], opacity=0)
        p.Show(t0 + m * per)
        root.add("line", x1=70, y1=R(YY(limit[m])), x2=640, y2=R(YY(limit[m])), stroke=cols[m], stroke_width=1.5, stroke_dasharray="4 4", opacity=0).Show(t0 + m * per + 0.5)
        sc.Text(root, 640, R(YY(limit[m])) - 5, "上限 %.1f" % limit[m], size=11, weight=700, fill=cols[m], anchor="end", opacity=0).Show(t0 + m * per + 0.5)
    st.Panel(690, 96, 240, 280, "95% に届くまでの回数", color=PURPLE)
    for m, a in enumerate(albedos):
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per + 0.8)
        sc.Text(g, 706, 140 + m * 76, "アルベド %.2f" % a, size=13, weight=700, fill=cols[m])
        sc.Text(g, 706, 168 + m * 76, "%d 回" % need[m], size=24, weight=700, fill=cols[m])
        sc.Text(g, 706, 188 + m * 76, "1 回だけでは 1/%.1f = %d%%" % (limit[m], round(100 / limit[m])), size=11, weight=500, fill=MUTED)
    st.Text(40, 410, "95% に必要な回数:", size=15)
    st.Counter(240, 414, [(t0 + m * per + 0.8, need[m]) for m in range(3)], size=28, fill=PURPLE)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 40, 440, 880, 70, [("雲(アルベド 0.95 以上)は、1 回の散乱では、全体の %d%% しか光らない。20 回以上必要" % round(100 / limit[2]), 14, "#1e3a8a"), ("毎回レイマーチで何十回も散らせるのは無理 → 少数の回数を、減衰を弱めて、足す近似(オクターブ)を使う", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "光は、媒質の中で、何度も散る"), (t0, t_e, "アルベドが高いほど、後の回数まで、光が残る"), (t_e, 99, "雲や霧は、アルベドが高い。多重散乱を、近似で足す")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "多重散乱", "95% に必要な回数: " + " / ".join("%d" % n_ for n_ in need))
    return Build(st, name, "graphics/atmosphere/scattering/multiple-scattering.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


NAMES = ["fog-curves", "beer-rgb", "cloud-coverage", "cloud-profiles", "cloud-beer-powder", "cloud-bayer", "radial-streak", "decay-weights", "rayleigh-wavelength", "multi-scatter-sum"]
FIGS = [FogCurves, BeerRgb, CloudCoverage, CloudProfiles, CloudBeerPowder, CloudBayer, RadialStreak, DecayWeights, RayleighWavelength, MultiScatterSum]
