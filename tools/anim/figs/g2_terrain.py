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


def Noise1(seed, n=200, per=12):
    r = Lcg(seed)
    lat = [r.U() * 2 - 1 for _ in range(per + 3)]
    def f(x):
        i = int(math.floor(x)); t = x - i
        u = t * t * (3 - 2 * t)
        return lat[i % len(lat)] * (1 - u) + lat[(i + 1) % len(lat)] * u
    return f


def Fbm(seed, oct_=4):
    fs = [Noise1(seed + k * 31) for k in range(oct_)]
    return lambda x: sum((0.5 ** k) * fs[k](x * (2 ** k)) for k in range(oct_)) / 1.8


def Panel1d(st, root, sc, title, color, y0=96, h=230):
    st.Panel(30, y0, 900, h, title, color=color)


# ===================================================================== domain warp
def DomainWarp():
    name = "domain-warp"
    st = Stage(name, "ドメイン ワープ: 地形を読む「座標」を、別のノイズでゆがめると、自然な曲がりくねりができる", duration=21.0, subtitle="縞模様(直線)を、座標ゆがめの強さ 0 → 2 → 5 → 9 で、ゆがめる。縞の曲がり具合を、計算する")
    sc, root = st.scene, st.root
    NX, NY, CS = 30, 10, 14.0
    wx, wy = Fbm(5, 3), Fbm(11, 3)
    stripe = lambda x: 1.0 if int(math.floor(x / 3.0)) % 2 == 0 else 0.0
    amps = [0.0, 2.0, 5.0, 9.0]
    grids = []
    bend = []
    for a in amps:
        g = [[stripe(i + a * wx((i / 6.0, ) [0] + j * 0.0 + j / 5.0 * 0.7) + a * 0.0) for i in range(NX)] for j in range(NY)]
        grids.append(g)
    # 各行での、縞の左端の位置(曲がり)
    def Edge(g, j):
        for i in range(1, NX):
            if g[j][i] != g[j][i - 1]:
                return i
        return NX
    def Bend(g):
        es = [Edge(g, j) for j in range(NY)]
        return max(es) - min(es)
    # 2 次元のゆがみ: 縞の座標に、x と y の両方で変わるノイズ
    def Warped(a):
        out = []
        for j in range(NY):
            row = []
            for i in range(NX):
                dx = a * wx(i / 9.0 + j / 7.0)
                dy = a * wy(i / 7.0 + j / 9.0 + 3.0) * 0.3
                row.append(stripe(i + dx + dy))
            out.append(row)
        return out
    grids = [Warped(a) for a in amps]
    bends = [Bend(g) for g in grids]
    assert bends[0] == 0 and bends[3] > bends[1] >= 0
    px = [30, 255, 480, 705]
    t0, per = 1.5, 4.5
    cs = 7.2
    for m, a in enumerate(amps):
        x = px[m]
        st.Panel(x, 100, NX * cs + 4, NY * cs + 4, "強さ %g" % a, color=[GRAY, BLUE, GREEN, RED][m])
        g = Grid(st, x + 2, 102, NX, NY, cs, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                g.Paint(i, j, t0 + m * per + 0.02 * (i + j), "#1e293b" if grids[m][j][i] else "#f8fafc")
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + 1.5)
        sc.Text(gx, x, 196, "縞の曲がり幅 %d 画素" % bends[m], size=13, weight=700, fill=[GRAY, BLUE, GREEN, RED][m])
    # 1 次元の説明
    st.Panel(30, 240, 900, 150, "1 本の線で見る(座標 x を、ノイズでずらして、縞を読む)", color=PURPLE)
    xs = list(range(NX * 2))
    for m, a in enumerate(amps[1:], start=1):
        pts = [(60 + i * 12.5, 372 - (stripe(i / 2.0 + a * wx(i / 18.0)) * 40 + (m - 1) * 0)) for i in xs]
        p = root.add("path", d=Poly(pts), fill="none", stroke=[BLUE, GREEN, RED][m - 1], stroke_width=2.5, opacity=0)
        p.Show(t0 + 4 * per + (m - 1) * 1.2)
    base_pts = [(60 + i * 12.5, 372 - stripe(i / 2.0) * 40) for i in xs]
    root.add("path", d=Poly(base_pts), fill="none", stroke=GRAY, stroke_width=2, stroke_dasharray="4 4")
    st.Counter(40, 430, [(t0 + m * per + 1.5, bends[m]) for m in range(4)], size=26, fill=PURPLE)
    st.Text(100, 430, "画素(縞の曲がり幅)", size=14)
    t_e = t0 + 4 * per + 3.6
    st.Box(t_e, 480, 410, 450, 74, [("読む座標を、ノイズで動かす = ワープ", 14, "#1e3a8a"), ("強さを上げるほど、直線が、蛇行する。ノイズを重ねてもよい", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "まっすぐな縞(高さの元になる模様)がある"), (t0, t_e, "読む場所を、別のノイズで動かすと、縞が曲がる"), (t_e, 99, "強さが大きいほど、複雑に、うねる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ワープ", "縞の曲がり幅: " + " / ".join("%d" % b for b in bends))
    return Build(st, name, "graphics/terrain/generation/domain-warp.md", BEFORE, [2.0, 5.0, 9.5, 14.0, 17.0, 20.0])


# ===================================================================== erosion
def ErosionDroplet():
    name = "erosion-droplet"
    st = Stage(name, "侵食(水滴): 水滴が坂を下りながら、土を削り、平らになるところで置いていく", duration=22.0, subtitle="1 次元の山。水滴 1 つを、頂上から、60 歩シミュレートする。削った量と、置いた量(合計は保存される)")
    sc, root = st.scene, st.root
    n = 64
    f = Fbm(3, 3)
    h = [6.0 + 7.0 * f(i / 7.0) + 8.0 * math.exp(-((i - 20) / 12.0) ** 2) for i in range(n)]
    h0 = h[:]
    # 水滴
    pos, vel, water, sed = 22.0, 0.0, 1.0, 0.0
    cap_k = 4.0
    erode_k, deposit_k = 0.5, 0.4
    hist = []
    eroded = deposited = 0.0
    for step in range(60):
        i = int(pos)
        if i < 1 or i >= n - 2:
            break
        slope = h[i] - h[i + 1] if vel >= 0 else 0
        slope = h[i] - h[i + 1]
        # 進む向きは、低い方
        sl = h[i] - h[i + 1] if h[i + 1] < h[i - 1] else h[i] - h[i - 1]
        d = 1 if h[i + 1] < h[i - 1] else -1
        cap = max(0.02, abs(sl)) * (abs(vel) + 0.5) * water * cap_k
        if sed > cap:
            dep = (sed - cap) * deposit_k
            h[i] += dep
            sed -= dep
            deposited += dep
        else:
            er = min((cap - sed) * erode_k, 0.3)
            h[i] -= er
            sed += er
            eroded += er
        vel = 0.9 * vel + d * max(0.05, abs(sl))
        pos += d * max(0.6, min(1.5, abs(vel) * 1.0 + 0.6))
        water *= 0.99
        hist.append((int(pos), eroded, deposited, sed, list(h)))
    mass0 = sum(h0)
    mass1 = sum(h) + sed
    assert abs(mass0 - mass1) < 1e-6 and eroded > 0.3 and deposited > 0.0, (mass0 - mass1, eroded, deposited, len(hist))
    st.Panel(30, 96, 900, 250, "① 高さ(灰 = 最初、色 = 現在)。水滴の通った所が、削れる", color=BLUE)
    X0, W = 60.0, 840.0
    XX = lambda i: X0 + i / (n - 1) * W
    YY = lambda v: 336 - v * 15
    root.add("path", d=Poly([(XX(i), YY(v)) for i, v in enumerate(h0)]), fill="none", stroke=GRAY, stroke_width=2.5, stroke_dasharray="5 4")
    cur = root.add("path", d=Poly([(XX(i), YY(v)) for i, v in enumerate(h0)]), fill="none", stroke=BLUE, stroke_width=3.5)
    drop = root.add("circle", cx=R(XX(14)), cy=R(YY(h0[14]) - 10), r=7, fill="#38bdf8", stroke=INK, stroke_width=1.5)
    t0, dt = 1.5, 0.28
    items = []
    prev = None
    for k, (ps, er, dp, sd, hh) in enumerate(hist):
        t = t0 + k * dt
        items.append((t, Poly([(XX(i), YY(v)) for i, v in enumerate(hh)])))
        if k == 0:
            drop.Set(t, "cx", R(XX(ps)))
            drop.Set(t, "cy", R(YY(hh[min(n - 1, ps)]) - 10))
        else:
            drop.Ramp(prev, t, "cx", R(XX(ps)))
            drop.Ramp(prev, t, "cy", R(YY(hh[min(n - 1, ps)]) - 10))
        prev = t
    cur.Steps("d", items)
    st.Text(40, 372, "削った土:", size=14)
    st.Counter(120, 376, [(t0 + k * dt, int(round(100 * e))) for k, (ps, e, dp, sd, hh) in enumerate(hist)], size=24, fill=RED)
    st.Text(220, 372, "置いた土:", size=14)
    st.Counter(300, 376, [(t0 + k * dt, int(round(100 * dp))) for k, (ps, e, dp, sd, hh) in enumerate(hist)], size=24, fill=GREEN)
    st.Text(400, 372, "運んでいる土:", size=14)
    st.Counter(510, 376, [(t0 + k * dt, int(round(100 * sd))) for k, (ps, e, dp, sd, hh) in enumerate(hist)], size=24, fill=PURPLE)
    st.Text(600, 376, "(すべて ×0.01)", size=12, weight=500, fill=MUTED)
    t_e = t0 + len(hist) * dt + 0.8
    st.Box(t_e, 40, 410, 880, 84, [("削った %.2f = 置いた %.2f + 運んでいる %.2f(合計は、最初から %.6f ずれ)" % (eroded, deposited, sed, abs(mass0 - mass1)), 15, "#1e3a8a"), ("傾きが急で速いほど、たくさん運べるので、削る。平らで遅いと、運びきれず、置く", 13, TEXT), ("これを、水滴 数万個で繰り返すと、谷や、扇状地ができる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "水滴を、山の上から落とす"), (t0, t_e, "坂では、土を削って運び、平らな所で、置いていく"), (t_e, 99, "土の総量は、変わらない。形だけが、自然に変わる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "侵食", "60 歩。削った %.2f、置いた %.2f、運搬 %.2f" % (eroded, deposited, sed))
    return Build(st, name, "graphics/terrain/generation/erosion.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 21.0])


# ===================================================================== height conversion
def HeightPow():
    name = "height-pow-curve"
    st = Stage(name, "ノイズを高さに直す: 冪(べき)を掛けると、平野が広がり、山が尖る", duration=21.0, subtitle="1 次元のノイズ(−1〜1)を、高さ ((n+1)/2)^p にする。p = 1・2・3 で、海面より下(0.3 以下)の割合と、山の鋭さを計算する")
    sc, root = st.scene, st.root
    n = 160
    f = Fbm(9, 4)
    noise = [max(-1.0, min(1.0, f(i / 14.0) * 1.9)) for i in range(n)]
    ps = [1.0, 2.0, 3.0]
    prof = [[((v + 1) / 2) ** p for v in noise] for p in ps]
    low = [sum(1 for v in pr if v < 0.3) / n for pr in prof]
    peak = [sum(1 for v in pr if v > 0.7) / n for pr in prof]
    assert low[2] > low[0] and peak[2] < peak[0]
    X0, W = 60.0, 840.0
    XX = lambda i: X0 + i / (n - 1) * W
    t0, per = 1.5, 5.5
    for m, p in enumerate(ps):
        y = 110 + m * 98
        root.add("rect", x=X0, y=y, width=W, height=84, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
        root.add("rect", x=X0, y=R(y + 84 - 0.3 * 84), width=W, height=R(0.3 * 84), fill="#bae6fd", opacity=0.6)
        pts = [(XX(i), y + 84 - v * 80) for i, v in enumerate(prof[m])]
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        g.add("path", d=Poly(pts), fill="none", stroke=[BLUE, GREEN, RED][m], stroke_width=3)
        sc.Text(g, X0 + 8, y + 16, "p = %g" % p, size=18, weight=700, fill=[BLUE, GREEN, RED][m])
        sc.Text(g, X0 + W - 8, y + 16, "海面より下 %d%% / 高い山(0.7 以上)%d%%" % (round(100 * low[m]), round(100 * peak[m])), size=13, weight=700, fill=TEXT, anchor="end")
    st.Text(40, 410, "海面より下の割合(%):", size=14)
    st.Counter(240, 414, [(t0 + m * per + 0.5, int(round(100 * low[m]))) for m in range(3)], size=26, fill=BLUE)
    st.Text(40, 448, "高い山の割合(%):", size=14)
    st.Counter(240, 452, [(t0 + m * per + 0.5, int(round(100 * peak[m]))) for m in range(3)], size=26, fill=RED)
    t_e = t0 + 3 * per
    st.Box(t_e - 0.3, 420, 400, 510, 90, [("p を上げると、低い所が広がり(%d%% → %d%%)、" % (round(100 * low[0]), round(100 * low[2])), 14, "#1e3a8a"), ("高い山は、少数の尖った所だけが残る(%d%% → %d%%)" % (round(100 * peak[0]), round(100 * peak[2])), 14, "#1e3a8a"), ("同じノイズから、島・平野・山脈と、地形の雰囲気を作り分けられる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ノイズの値を、そのまま高さにすると、丸い起伏になる"), (t0, t_e, "冪を掛けると、平野が広がり、山が目立つ"), (t_e, 99, "p が地形の個性を決める")], size=14, fill=MUTED, weight=500)
    for m, p in enumerate(ps):
        st.Note(t0 + m * per, "冪", "p = %g: 低い %d%% / 山 %d%%" % (p, round(100 * low[m]), round(100 * peak[m])))
    return Build(st, name, "graphics/terrain/generation/height-conversion.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== ridge
def RidgeSteps():
    name = "ridge-steps"
    st = Stage(name, "リッジ ノイズ: ノイズ → 絶対値 → 反転 → 2 乗 で、尾根が尖る", duration=22.0, subtitle="1 次元のノイズに 4 つの変換を、順に掛ける。各段階での、いちばん尖った所の曲がり(2 階微分)を、計算する")
    sc, root = st.scene, st.root
    n = 200
    f = Fbm(21, 3)
    a = [f(i / 16.0) * 1.7 for i in range(n)]
    b = [abs(v) for v in a]
    c = [1 - v for v in b]
    d = [v * v for v in c]
    stages = [("① ノイズ(−1〜1)", a, BLUE), ("② 絶対値(谷の線が 0 に折れる)", b, GREEN), ("③ 反転(1 − 絶対値): 0 だった所が、尾根になる", c, AMBER), ("④ 2 乗(尾根を鋭く、谷を平らに)", d, RED)]
    def Sharp(v):
        return max(abs(v[i - 1] - 2 * v[i] + v[i + 1]) for i in range(1, n - 1))
    sh = [Sharp(v) for _, v, _ in stages]
    assert sh[1] > sh[0]
    X0, W = 60.0, 840.0
    XX = lambda i: X0 + i / (n - 1) * W
    t0, per = 1.5, 4.8
    for m, (lab, v, col) in enumerate(stages):
        y = 108 + m * 90
        lo, hi = (min(v), max(v))
        root.add("rect", x=X0, y=y, width=W, height=76, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
        pts = [(XX(i), y + 70 - (x - lo) / (hi - lo) * 62) for i, x in enumerate(v)]
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        g.add("path", d=Poly(pts), fill="none", stroke=col, stroke_width=3)
        sc.Text(g, X0 + 8, y + 18, lab, size=14, weight=700, fill=col)
        sc.Text(g, X0 + W - 8, y + 18, "最も尖った所の曲がり %.3f" % sh[m], size=13, weight=700, fill=TEXT, anchor="end")
    st.Text(40, 478, "最も尖った所の曲がり(×1000):", size=14)
    st.Counter(300, 482, [(t0 + m * per + 0.5, int(round(1000 * sh[m]))) for m in range(4)], size=26, fill=RED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.3, 480, 462, 450, 64, [("絶対値で、0 を横切る所が、折れる(鋭い)。反転で山になり、2 乗で尾根がより鋭くなる", 12, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "ふつうのノイズは、丸い"), (t0, t_e, "絶対値で折り、反転して山にし、2 乗で鋭くする"), (t_e, 99, "山脈のような、尖った尾根ができる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "リッジ", "曲がり: " + " → ".join("%.3f" % s for s in sh))
    return Build(st, name, "graphics/terrain/generation/ridge.md", BEFORE, [2.0, 5.0, 9.5, 14.0, 18.0, 21.0])


# ===================================================================== chunk stream
def ChunkStream():
    name = "chunk-stream"
    st = Stage(name, "チャンクのストリーミング: カメラが動くと、近いチャンクを読み込み、遠いチャンクを捨てる。メモリは一定", duration=22.0, subtitle="20×8 のチャンクの世界。カメラの半径 2.5 チャンク以内を読み込む。カメラを右へ 8 チャンク動かして、読み込み・解放の数を数える")
    sc, root = st.scene, st.root
    NX, NY, CS = 20, 8, 28.0
    OX, OY = 50.0, 120.0
    rad = 2.5
    cam = [(3.0 + k, 4.0) for k in range(9)]
    def Loaded(c):
        return {(i, j) for i in range(NX) for j in range(NY) if math.hypot(i + 0.5 - c[0], j + 0.5 - c[1]) <= rad}
    sets = [Loaded(c) for c in cam]
    loads = [len(sets[k] - sets[k - 1]) for k in range(1, 9)]
    unloads = [len(sets[k - 1] - sets[k]) for k in range(1, 9)]
    mem = [len(s) for s in sets]
    assert max(mem) - min(mem) <= 2 and sum(loads) > 0
    g = Grid(st, OX, OY, NX, NY, CS, base="#f1f5f9", stroke="#94a3b8")
    t0, dt = 1.5, 2.2
    for k, s in enumerate(sets):
        prev = sets[k - 1] if k else set()
        for i in range(NX):
            for j in range(NY):
                if (i, j) in s:
                    g.Paint(i, j, t0 + k * dt, "#86efac" if (i, j) not in prev else "#22c55e")
                    g.Paint(i, j, t0 + k * dt + 0.9, "#22c55e")
                elif (i, j) in prev:
                    g.Paint(i, j, t0 + k * dt, "#fca5a5")
                    g.Paint(i, j, t0 + k * dt + 0.9, "#f1f5f9")
    g.Flush()
    g.Lines(color="#ffffff", opacity=0.5)
    camn = root.add("circle", cx=R(OX + cam[0][0] * CS), cy=R(OY + cam[0][1] * CS), r=9, fill=INK)
    for k in range(1, 9):
        camn.Ramp(t0 + (k - 1) * dt + 1.0, t0 + k * dt, "cx", R(OX + cam[k][0] * CS))
        camn.Ramp(t0 + (k - 1) * dt + 1.0, t0 + k * dt, "cy", R(OY + cam[k][1] * CS))
    st.Text(40, 398, "読み込んだ数(累計):", size=14)
    c = 0
    ser = [(t0, 0)]
    for k in range(1, 9):
        c += loads[k - 1]
        ser.append((t0 + k * dt, c))
    st.Counter(230, 402, ser, size=24, fill=GREEN)
    st.Text(40, 430, "捨てた数(累計):", size=14)
    c = 0
    ser = [(t0, 0)]
    for k in range(1, 9):
        c += unloads[k - 1]
        ser.append((t0 + k * dt, c))
    st.Counter(230, 434, ser, size=24, fill=RED)
    st.Text(40, 462, "いま、メモリにあるチャンク:", size=14)
    st.Counter(300, 466, [(t0 + k * dt, mem[k]) for k in range(9)], size=24, fill=PURPLE)
    t_e = t0 + 9 * dt
    st.Box(t_e - 0.5, 480, 392, 450, 100, [("メモリのチャンクは %d〜%d 個で、ほぼ一定" % (min(mem), max(mem)), 14, "#1e3a8a"), ("1 歩あたり、新しく %d〜%d、捨てる %d〜%d" % (min(loads), max(loads), min(unloads), max(unloads)), 13, TEXT), ("世界が、どれだけ広くても、必要なメモリは、半径で決まる", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "広い世界を、全部は持てない"), (t0, t_e, "カメラの周りだけ持つ。動いた分だけ、読み込み・解放する"), (t_e, 99, "読み込みは、1 フレームに 1 つずつ、などに分けて、ガクつきを防ぐ")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "チャンク", "メモリ %d〜%d 個、読み込み計 %d、解放計 %d" % (min(mem), max(mem), sum(loads), sum(unloads)))
    return Build(st, name, "graphics/terrain/heightmap-mesh/chunks.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 21.0])


# ===================================================================== heightmap lift
def HeightmapLift():
    name = "heightmap-lift"
    st = Stage(name, "高さマップを、格子の頂点の高さに使う: 平らな格子を、1 頂点ずつ持ち上げ、法線は、隣の高さの差から求める", duration=21.0, subtitle="1 次元の断面。頂点 17 個の平らな線を、高さマップで持ち上げる。三角形の数と、各頂点の法線の傾きを計算する")
    sc, root = st.scene, st.root
    n = 17
    f = Fbm(14, 3)
    hm = [max(0.0, 2.0 + 3.0 * f(i / 3.0)) for i in range(n)]
    X0, SX, Y0, SY = 70.0, 50.0, 330.0, 36.0
    XX = lambda i: X0 + i * SX
    st.Panel(30, 96, 900, 270, "① 平らな格子 → 高さで持ち上げた格子(青 = 持ち上げた線)", color=BLUE)
    root.add("line", x1=XX(0), y1=Y0, x2=XX(n - 1), y2=Y0, stroke="#94a3b8", stroke_width=2.5, stroke_dasharray="5 4")
    for i in range(n):
        root.add("circle", cx=R(XX(i)), cy=Y0, r=4, fill="#94a3b8")
    t0, dt = 1.5, 0.5
    lift = root.add("path", d=Poly([(XX(i), Y0) for i in range(n)]), fill="none", stroke=BLUE, stroke_width=3.5)
    lift.Steps("d", [(t0 + k * dt, Poly([(XX(i), Y0 - (hm[i] * min(1.0, 1.0) if i <= k else 0) * SY) for i in range(n)])) for k in range(n)])
    for i in range(n):
        d = root.add("circle", cx=R(XX(i)), cy=R(Y0), r=5.5, fill=BLUE, opacity=0)
        d.Show(t0 + i * dt)
        d.Set(t0 + i * dt, "cy", R(Y0 - hm[i] * SY))
    # 法線
    t_n = t0 + n * dt + 0.6
    nrm = []
    for i in range(n):
        a = hm[max(0, i - 1)]
        b = hm[min(n - 1, i + 1)]
        dx = (XX(min(n - 1, i + 1)) - XX(max(0, i - 1))) / SX
        nrm.append((-(b - a) / dx, 1.0))
    for i in range(n):
        nx, nz = nrm[i]
        L = math.hypot(nx, nz)
        g = root.add("g", opacity=0)
        g.Show(t_n + i * 0.15)
        g.add("line", x1=R(XX(i)), y1=R(Y0 - hm[i] * SY), x2=R(XX(i) + nx / L * 26), y2=R(Y0 - hm[i] * SY - nz / L * 26), stroke=RED, stroke_width=2.5)
    tri_flat = 2 * (n - 1)
    st.Text(40, 404, "格子の頂点:", size=14)
    st.Counter(150, 408, [(t0 + k * dt, k + 1) for k in range(n)], size=24, fill=BLUE)
    st.Text(40, 440, "法線(赤い線)は、左右の高さの差 (b − a) から求める: 法線 = (−(b − a)÷間隔, 1) を、正規化", size=13, weight=700, fill=RED, opacity=0).Show(t_n)
    steep = max(abs(nx) / math.hypot(nx, nz) for nx, nz in nrm)
    t_e = t_n + n * 0.15 + 0.6
    st.Box(t_e, 40, 456, 880, 56, [("頂点を動かすだけ。三角形の数(2D では %d)は、変わらない。いちばん傾いた所の法線: 傾き %.2f" % (tri_flat, steep), 14, "#1e3a8a"), ("頂点シェーダーで、高さマップを読んで、持ち上げる(CPU でメッシュを作り直さない)", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "平らな格子に、高さマップを、1 頂点ずつ当てはめる"), (t0, t_n, "頂点を持ち上げる"), (t_n, t_e, "隣の高さの差から、法線(陰の向き)を求める"), (t_e, 99, "メッシュの形は変えず、頂点の高さだけで、地形になる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "高さ", "頂点 %d 個、最大の傾き %.2f" % (n, steep))
    return Build(st, name, "graphics/terrain/heightmap-mesh/grid-mesh.md", BEFORE, [2.0, 5.0, 8.0, 11.0, 15.0, 20.0])


# ===================================================================== bilinear height
def BilinearHeight():
    name = "bilinear-height"
    st = Stage(name, "好きな位置の高さ: 周りの 4 つの高さを、距離で混ぜる(バイリニア)。最も近い 1 点だと、階段になる", duration=22.0, subtitle="なだらかな坂の上に、キャラクターが歩く。高さマップは 1 マス = 1 m。1 マスの途中の位置で、2 つの方法の高さを比べる")
    sc, root = st.scene, st.root
    hm = {(i, j): 0.5 * i + 0.2 * j + 0.3 * math.sin(i * 1.3) for i in range(8) for j in range(6)}
    true = lambda x, y: 0.5 * x + 0.2 * y + 0.3 * math.sin(x * 1.3)
    def Bil(x, y):
        i, j = int(math.floor(x)), int(math.floor(y))
        u, v = x - i, y - j
        return hm[(i, j)] * (1 - u) * (1 - v) + hm[(i + 1, j)] * u * (1 - v) + hm[(i, j + 1)] * (1 - u) * v + hm[(i + 1, j + 1)] * u * v
    def Near(x, y):
        return hm[(int(round(x)), int(round(y)))]
    path = [(1.0 + 5.0 * k / 50, 2.0 + 1.5 * math.sin(k / 8)) for k in range(51)]
    eb = [abs(Bil(x, y) - true(x, y)) for x, y in path]
    en = [abs(Near(x, y) - true(x, y)) for x, y in path]
    assert sum(eb) < sum(en) / 2
    X0, W = 60.0, 840.0
    XX = lambda k: X0 + k / 50 * W
    zs = [true(x, y) for x, y in path]
    zlo, zhi = min(zs) - 0.3, max(zs) + 0.5
    YY = lambda v: 330 - (v - zlo) / (zhi - zlo) * 210
    st.Panel(30, 96, 900, 260, "歩いた線に沿った高さ", color=BLUE)
    root.add("path", d=Poly([(XX(k), YY(z)) for k, z in enumerate(zs)]), fill="none", stroke=GRAY, stroke_width=2.5, stroke_dasharray="6 5")
    root.add("path", d=Poly([(XX(k), YY(Near(x, y))) for k, (x, y) in enumerate(path)]), fill="none", stroke=RED, stroke_width=3.5, opacity=1)
    pb = root.add("path", d=Poly([(XX(k), YY(Bil(x, y))) for k, (x, y) in enumerate(path)]), fill="none", stroke=GREEN, stroke_width=3.5, opacity=0)
    pb.Show(9.0)
    st.Legend(70, 124, [(GRAY, "本当の高さ"), (RED, "最も近い 1 点"), (GREEN, "周りの 4 点を混ぜる")])
    dot = root.add("circle", cx=R(XX(0)), cy=R(YY(zs[0])), r=7, fill=INK)
    prev = None
    for k, z in enumerate(zs):
        t = 1.5 + 20.0 * k / 50 * 0.0 + 6.0 * k / 50 + (0 if k < 0 else 0)
        t = 1.5 + 6.0 * k / 50
        if k == 0:
            dot.Set(t, "cx", R(XX(k))); dot.Set(t, "cy", R(YY(z)))
        else:
            dot.Ramp(prev, t, "cx", R(XX(k))); dot.Ramp(prev, t, "cy", R(YY(z)))
        prev = t
    st.Text(40, 392, "足元の高さのずれ(平均、cm):", size=14)
    st.Counter(300, 396, [(1.5, 0), (7.5, int(round(100 * sum(en) / 51))), (15.0, int(round(100 * sum(eb) / 51)))], size=26, fill=RED)
    st.Text(340, 396, "(最近点 → バイリニア)", size=12, weight=500, fill=MUTED)
    t_e = 16.0
    st.Box(t_e, 40, 420, 880, 90, [("ずれの平均: 最も近い 1 点 %.1f cm → バイリニア %.1f cm" % (100 * sum(en) / 51, 100 * sum(eb) / 51), 15, "#1e3a8a"), ("最も近い 1 点だと、1 m ごとに、階段状に段差。キャラが、ガクガク上下する", 13, TEXT), ("バイリニアは、4 回読むだけで、なめらか。当たり判定・接地・草の根元に、使う", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, 1.5, "高さマップは、整数の格子点にしか、高さが無い"), (1.5, 9.0, "最も近い格子点の高さを使うと、階段になる"), (9.0, 99, "周りの 4 点を、距離で混ぜると、なめらかな坂になる")], size=14, fill=MUTED, weight=500)
    st.Note(1.5, "高さ取得", "ずれの平均: 近傍 %.1f cm / バイリニア %.1f cm" % (100 * sum(en) / 51, 100 * sum(eb) / 51))
    return Build(st, name, "graphics/terrain/heightmap-mesh/height-query.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 15.0, 21.0])


# ===================================================================== clipmap
def ClipmapRings():
    name = "clipmap-rings"
    st = Stage(name, "クリップマップ: 同じ頂点数の層を、倍々の広さで入れ子にする。頂点数は一定で、遠くまで届く", duration=21.0, subtitle="断面。層ごとに、33 頂点。層 0 の間隔が 1 m、層 1 が 2 m、層 2 が 4 m、…。カメラの周りだけ、細かい")
    sc, root = st.scene, st.root
    L = 5
    cols = [GREEN, BLUE, AMBER, RED, PURPLE]
    V = 33
    spacing = [2 ** k for k in range(L)]
    span = [V * s for s in spacing]
    st.Panel(30, 96, 900, 280, "層の広がり(横 = カメラからの距離 m、対数)", color=BLUE)
    X0 = 70.0
    LX = lambda d: X0 + (math.log2(max(d, 1.0)) / math.log2(span[-1] / 2)) * 800
    cy = 330.0
    root.add("line", x1=60, y1=cy, x2=900, y2=cy, stroke="#94a3b8", stroke_width=2)
    root.add("circle", cx=X0, cy=cy, r=7, fill=INK)
    t0, per = 1.5, 3.4
    for k in range(L):
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per)
        r = span[k] / 2
        y = 130 + k * 36
        g.add("rect", x=R(LX(1)), y=y, width=R(LX(r) - LX(1)), height=26, fill=cols[k], opacity=0.8)
        sc.Text(g, LX(1) + 6, y + 18, "層 %d: 間隔 %d m、〜 %d m" % (k, spacing[k], r), size=12, weight=700, fill="#ffffff")
        for i in range(V // 2 + 1):
            g.add("line", x1=R(LX(max(1, i * spacing[k]))), y1=y + 26, x2=R(LX(max(1, i * spacing[k]))), y2=y + 32, stroke=cols[k], stroke_width=1.5)
    full = (span[-1] // 1) ** 2
    clip = L * V * V
    st.Text(40, 400, "頂点の数(層ごとに 33×33):", size=14)
    st.Counter(280, 404, [(t0 + k * per, V * V * (k + 1)) for k in range(L)], size=26, fill=PURPLE)
    st.Text(40, 436, "同じ範囲を、全部 1 m 間隔で作ると:", size=14)
    st.Text(330, 436, "%s 頂点(約 %.0f 倍)" % (Fmt(full), full / clip), size=18, weight=700, fill=RED, opacity=0).Show(t0 + L * per)
    t_e = t0 + L * per + 1.0
    st.Box(t_e, 40, 456, 880, 56, [("%d 層 %s 頂点で、半径 %d m まで届く。近く(1 m 間隔)から、遠く(%d m 間隔)まで、頂点数は一定" % (L, Fmt(clip), span[-1] // 2, spacing[-1]), 14, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "遠くの地形を、近くと同じ細かさで描くのは、無駄"), (t0, t_e, "層を足すごとに、広さが 2 倍、間隔も 2 倍になる"), (t_e, 99, "カメラが動くと、層ごとに、動く単位(間隔)ぶんだけ、ずらして、追いかける")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "クリップマップ", "%d 層、頂点 %d、半径 %d m" % (L, clip, span[-1] // 2))
    return Build(st, name, "graphics/terrain/lod/clipmap.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== LOD cracks
def LodCracks():
    name = "lod-cracks"
    st = Stage(name, "LOD の継ぎ目の割れ目: 粗い側と細かい側で、境の頂点の高さが食い違うと、穴が空く。細かい側を、粗い側に合わせる", duration=21.0, subtitle="断面。左は LOD 1(間隔 2)、右は LOD 0(間隔 1)。境(x = 8)の近くの高さを、計算して、割れ目の大きさを測る")
    sc, root = st.scene, st.root
    f = Fbm(30, 3)
    h = lambda x: 3.0 + 2.2 * f(x / 2.2)
    xs0 = [8 + k for k in range(0, 9)]                 # 細かい側: 間隔 1
    xs1 = [0 + 2 * k for k in range(0, 5)]             # 粗い側: 間隔 2(0,2,4,6,8)
    # 粗い側の線: 頂点を結ぶ
    def Coarse(x):
        i = min(3, int(x // 2))
        t = (x - 2 * i) / 2
        return h(2 * i) * (1 - t) + h(2 * i + 2) * t
    # 細かい側で、粗い側の端に当たる所(x = 8 のすぐ右の頂点 x = 9 など)は、問題なし。T 字の接合は、粗い側の辺の途中に、細かい側の頂点が来る場合
    # 境を縦にしない: 粗い側が x=0..8、細かい側が x=8..16 で、さらに粗い側の頂点間(x = 7)に、細かい側の頂点 7 を置く領域もある、という設定
    fine_xs = list(range(0, 17))
    # 割れ目: 細かい側の頂点(整数 x)が、粗い辺の上にない所の差
    gaps = [abs(h(x) - Coarse(x)) if x <= 8 else 0 for x in range(0, 9)]
    gap_max = max(gaps)
    fixed = [0.0 for _ in gaps]
    assert gap_max > 0.1
    X0, SX, Y0, SY = 60.0, 50.0, 330.0, 36.0
    st.Panel(30, 96, 900, 260, "① 高さ(黒 = 細かい LOD の頂点、赤い線 = 粗い LOD の辺)", color=BLUE)
    XX = lambda x: X0 + x * SX
    root.add("path", d=Poly([(XX(x), Y0 - h(x) * SY) for x in fine_xs]), fill="none", stroke=INK, stroke_width=2.5)
    for x in fine_xs:
        root.add("circle", cx=R(XX(x)), cy=R(Y0 - h(x) * SY), r=4, fill=INK)
    t0 = 1.5
    root.add("line", x1=R(XX(8)), y1=110, x2=R(XX(8)), y2=Y0, stroke=GRAY, stroke_width=1.5, stroke_dasharray="4 4")
    sc.Text(root, XX(8) + 6, 124, "LOD の境", size=12, weight=700, fill=MUTED)
    cp = root.add("path", d=Poly([(XX(x), Y0 - Coarse(x) * SY) for x in [k / 2 for k in range(0, 17)]]), fill="none", stroke=RED, stroke_width=3.5, opacity=0)
    cp.Show(t0)
    for x in range(0, 9):
        if x % 2 == 1:
            g = root.add("g", opacity=0)
            g.Show(t0 + 1.0 + x * 0.3)
            g.add("line", x1=R(XX(x)), y1=R(Y0 - h(x) * SY), x2=R(XX(x)), y2=R(Y0 - Coarse(x) * SY), stroke=AMBER, stroke_width=5)
    sc.Text(root, 70, 134, "オレンジ = 割れ目(同じ x で、高さが違う)", size=13, weight=700, fill="#b45309", opacity=0).Show(t0 + 1.0)
    odd = [abs(h(x) - Coarse(x)) for x in range(1, 9, 2)]
    st.Text(40, 380, "奇数の頂点での割れ目:", size=14)
    st.Counter(240, 384, [(t0 + 1.0 + (2 * k + 1) * 0.3, int(round(100 * odd[k]))) for k in range(4)], size=24, fill=RED)
    st.Text(290, 384, "(×0.01 m。粗い辺と、細かい頂点の高さの差)", size=12, weight=500, fill=MUTED)
    t_f = t0 + 5.5
    fx = root.add("path", d=Poly([(XX(x), Y0 - (Coarse(x) if x <= 8 else h(x)) * SY) for x in fine_xs]), fill="none", stroke=GREEN, stroke_width=4, opacity=0)
    fx.Show(t_f)
    st.Text(40, 420, "対策: 粗い辺の上にある、細かい頂点を、粗い辺の高さへ下ろす(奇数番目を、両隣の平均にする)", size=14, weight=700, fill=GREEN, opacity=0).Show(t_f)
    t_e = t_f + 2.5
    st.Box(t_e, 40, 446, 880, 60, [("割れ目の最大 %.2f m → 対策後 0 m" % gap_max, 15, "#166534"), ("頂点の高さを、LOD 境でだけ、粗い側に合わせると、継ぎ目が閉じる(スカートで、隠す方法もある)", 12, MUTED)], GREEN, "#f0fdf4")
    st.Caption(30, 534, [(0.0, t0, "LOD の異なる地形が、隣り合う"), (t0, t_f, "細かい側の頂点が、粗い辺の上にないと、高さが食い違って、穴が見える"), (t_f, 99, "境の頂点を、粗い辺に載せれば、割れ目が閉じる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "割れ目", "最大 %.2f m → 対策後 0" % gap_max)
    return Build(st, name, "graphics/terrain/lod/cracks.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== height mip
def HeightMipBars():
    name = "height-mip-bars"
    st = Stage(name, "高さのミップ: 隣り合う高さを平均して、半分の大きさを作る。遠景は粗い層で、足りる", duration=22.0, subtitle="1 次元の高さ 16 点。層 0(16 点)→ 層 1(8 点)→ 層 2(4 点)→ 層 3(2 点)。層が粗いほど、元の地形との差が増える")
    sc, root = st.scene, st.root
    f = Fbm(44, 3)
    h0 = [max(0.1, 3.0 + 3.0 * f(i / 2.0)) for i in range(16)]
    levels = [h0]
    while len(levels[-1]) > 2:
        a = levels[-1]
        levels.append([(a[2 * i] + a[2 * i + 1]) / 2 for i in range(len(a) // 2)])
    def Expand(lv, size):
        k = size // len(lv)
        return [lv[i // k] for i in range(size)]
    errs = [sum(abs(a - b) for a, b in zip(Expand(l, 16), h0)) / 16 for l in levels]
    mx = [max(abs(a - b) for a, b in zip(Expand(l, 16), h0)) for l in levels]
    assert errs[3] > errs[1] > errs[0]
    X0, W, base_y, sc_h = 70.0, 800.0, 360.0, 36.0
    cols = [GRAY, BLUE, GREEN, AMBER]
    t0, per = 1.5, 4.8
    for L, lv in enumerate(levels):
        m = len(lv)
        cw = W / m
        g = root.add("g", opacity=0)
        g.Show(t0 + L * per, t0 + (L + 1) * per if L < len(levels) - 1 else None)
        for i, v in enumerate(lv):
            g.add("rect", x=R(X0 + i * cw + 2), y=R(base_y - v * sc_h), width=R(cw - 4), height=R(v * sc_h), fill=cols[L], opacity=0.55 if L else 0.35)
        sc.Text(g, X0, 128 + L * 0, "層 %d(%d 点): 元との差(平均)%.2f / 最大 %.2f" % (L, m, errs[L], mx[L]), size=15, weight=700, fill=cols[L])
        if L:
            g.add("path", d=Poly([(X0 + i * (W / 16) + (W / 32), base_y - h0[i] * sc_h) for i in range(16)]), fill="none", stroke=INK, stroke_width=2.5)
    for L in range(len(levels)):
        pass
    root.add("line", x1=X0, y1=base_y, x2=X0 + W, y2=base_y, stroke="#94a3b8", stroke_width=2)
    st.Text(40, 420, "点の数:", size=14)
    st.Counter(120, 424, [(t0 + L * per, len(l)) for L, l in enumerate(levels)], size=26, fill=PURPLE)
    st.Text(40, 458, "元の地形との差(×0.01 m):", size=14)
    st.Counter(280, 462, [(t0 + L * per, int(round(100 * errs[L]))) for L in range(len(levels))], size=26, fill=RED)
    t_e = t0 + len(levels) * per
    st.Box(t_e - 0.5, 440, 410, 490, 100, [("層が 1 つ上がると、点は半分、差は増える(%.2f → %.2f)" % (errs[0], errs[3]), 14, "#1e3a8a"), ("遠くは、画面で 1 画素が数 m ぶんなので、粗い層で、見た目が変わらない", 13, TEXT), ("遠い頂点を、粗い層から読めば、テクスチャの読み込みが軽く、キャッシュにも優しい", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "高さを、隣と平均して、小さな高さマップを作る"), (t0, t_e, "層を重ねるほど、粗く、小さく"), (t_e, 99, "距離に応じて、層を選ぶ(ミップ)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ミップ", "元との差(平均): " + " / ".join("%.2f" % e for e in errs))
    return Build(st, name, "graphics/terrain/lod/height-mip.md", BEFORE, [2.0, 5.0, 9.0, 14.0, 18.0, 21.0])


NAMES = ["domain-warp", "erosion-droplet", "height-pow-curve", "ridge-steps", "chunk-stream", "heightmap-lift", "bilinear-height", "clipmap-rings", "lod-cracks", "height-mip-bars"]
FIGS = [DomainWarp, ErosionDroplet, HeightPow, RidgeSteps, ChunkStream, HeightmapLift, BilinearHeight, ClipmapRings, LodCracks, HeightMipBars]
