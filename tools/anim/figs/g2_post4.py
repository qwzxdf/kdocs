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


def Rgbh(c):
    return Hex([255 * max(0.0, min(1.0, v)) for v in c])


def Row(st, root, sc, x0, y, vals, cw, t0, dt, lab=None, col=GRAY, ch=26.0, f=None):
    f = f or (lambda v: Gray(1 - v))
    if lab:
        sc.Text(root, x0, y - 4, lab, size=13, weight=700, fill=col)
    g = Grid(st, x0, y, len(vals), 1, cw, base="#e5e7eb", stroke="#94a3b8", cell_h=ch)
    for i, v in enumerate(vals):
        g.Paint(i, 0, t0 + i * dt, f(v))
    g.Flush()
    return g


# ===================================================================== MB jitter
def MotionBlurJitter():
    name = "motion-blur-jitter"
    st = Stage(name, "モーション ブラーのサンプル: 少ない数で等間隔に取ると、帯になる。ずらして取ると、ノイズになる", duration=21.0, subtitle="1 列 64 画素。幅 4 の明るい棒が、1 フレームで 16 画素、右へ動く。流れた軌跡を、4 サンプルや 16 サンプルで描く")
    sc, root = st.scene, st.root
    n, W, V = 64, 4, 16
    x0 = 12
    def Bar(i, p):
        return max(0.0, min(i + 1, p + W) - max(i, p))
    def Truth():
        m = 256
        return [sum(Bar(i, x0 + V * (k + 0.5) / m) for k in range(m)) / m for i in range(n)]
    tr = Truth()
    def Uniform(k):
        return [sum(Bar(i, x0 + V * (s + 0.5) / k) for s in range(k)) / k for i in range(n)]
    def Jitter(k, seed):
        out = []
        for i in range(n):
            r = Lcg(seed + i * 977)
            out.append(sum(Bar(i, x0 + V * ((s + r.U()) / k)) for s in range(k)) / k)
        return out
    cases = [("4 サンプル・等間隔", Uniform(4), RED), ("4 サンプル・ずらす(ジッター)", Jitter(4, 7), AMBER), ("16 サンプル・等間隔", Uniform(16), GREEN), ("正解(256 サンプル)", tr, BLUE)]
    err = lambda a: sum(abs(a[i] - tr[i]) for i in range(n)) / n
    rough = lambda a: sum(abs(a[i + 1] - 2 * a[i] + a[i - 1]) for i in range(1, n - 1))
    errs = [err(c[1]) for c in cases]
    assert errs[2] < errs[0], errs
    CW, X0 = 12.5, 60.0
    t0, per = 1.5, 4.0
    for m, (lab, vals, col) in enumerate(cases):
        y = 112 + m * 62
        Row(st, root, sc, X0, y, vals, CW, t0 + m * per, 0.035, lab, col, 28.0, lambda v: Gray(1 - min(1.0, v * 1.0)))
        gx = root.add("g", opacity=0)
        gx.Show(t0 + m * per + 2.0)
        sc.Text(gx, X0 + n * CW + 10, y + 12, "ずれ %.3f" % errs[m], size=12, weight=700, fill=col)
        sc.Text(gx, X0 + n * CW + 10, y + 30, "読み込み %s" % ["4", "4", "16", "256"][m], size=11, weight=500, fill=MUTED)
    t_e = t0 + 4 * per
    st.Text(40, 400, "読み込みの回数(1 画素あたり):", size=14)
    st.Counter(300, 404, [(t0, 4), (t0 + per, 4), (t0 + 2 * per, 16), (t0 + 3 * per, 256)], size=26, fill=PURPLE)
    st.Box(t_e - 0.5, 40, 436, 880, 76, [("4 サンプル: 等間隔だと、流れが「4 つの棒」に見える(帯)。ずらすと、1 本の流れ + ノイズ", 14, "#1e3a8a"), ("ずれ: 等間隔 4 = %.3f / ずらす 4 = %.3f / 等間隔 16 = %.3f" % (errs[0], errs[1], errs[2]), 13, TEXT), ("ノイズは、TAA や、ぼかしで消せる。帯は、消えない。だから、ジッターを使う", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "動いた軌跡を、画素ごとに、何点かサンプルして平均する"), (t0, t_e, "サンプルが少ないと、「離れた棒」が見える(帯)"), (t_e, 99, "ずらして取れば、帯が消えて、ノイズに変わる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ジッター", "ずれ: 等間隔4 %.3f / ジッター4 %.3f / 等間隔16 %.3f" % tuple(errs[:3]))
    return Build(st, name, "graphics/postprocess/motion-blur/blur-pass.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== camera blur
def CameraBlur():
    name = "camera-blur"
    st = Stage(name, "カメラ ブラー: カメラが動くと、近い物ほど、画面で大きく動く(流れが長い)", duration=20.0, subtitle="断面。カメラが右へ 1 m 動く。深度(距離)ごとに、画面の動き(画素)が、距離に反比例する")
    sc, root = st.scene, st.root
    F = 900.0
    move = 0.4
    ds = [2.0, 4.0, 8.0, 16.0, 40.0]
    vel = [F * move / d for d in ds]
    assert vel[0] > vel[1] > vel[4]
    st.Panel(30, 96, 900, 190, "① 上から見た図(カメラ → 右へ。柱が距離ごとに立つ)", color=BLUE)
    ox, oy = 90.0, 250.0
    X = lambda d: ox + d * 17.0
    root.add("circle", cx=ox, cy=oy, r=9, fill=INK)
    sc.Text(root, ox, oy + 26, "カメラ", size=12, weight=700, fill=INK, anchor="middle")
    cols = [RED, AMBER, GREEN, BLUE, PURPLE]
    t0, per = 1.5, 3.0
    for k, d in enumerate(ds):
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per)
        g.add("rect", x=R(X(d)) - 7, y=R(oy - 70), width=14, height=70, fill=cols[k], opacity=0.85)
        sc.Text(g, X(d), oy - 78, "%g m" % d, size=12, weight=700, fill=cols[k], anchor="middle")
        g.add("line", x1=R(X(d)), y1=R(oy - 30), x2=R(X(d)), y2=R(oy - 30), stroke=cols[k], stroke_width=0)
    # 画面での流れ
    st.Panel(30, 306, 900, 150, "② 画面での流れの長さ(画素)= 焦点距離 × カメラの動き ÷ 距離", color=PURPLE)
    for k, d in enumerate(ds):
        y = 342 + k * 22
        g = root.add("g", opacity=0)
        g.Show(t0 + k * per + 0.4)
        sc.Text(g, 50, y + 12, "%g m" % d, size=12, weight=700, fill=cols[k])
        w = vel[k] / vel[0] * 600
        g.add("rect", x=120, y=y, width=R(max(w, 3)), height=16, fill=cols[k], opacity=0.85)
        sc.Text(g, 120 + w + 8, y + 13, "%.0f 画素" % vel[k], size=12, weight=700, fill=cols[k])
    st.Text(40, 480, "いま見ている距離の流れ(画素):", size=14)
    st.Counter(300, 484, [(t0 + k * per + 0.4, int(round(vel[k]))) for k in range(5)], size=24, fill=RED)
    t_e = t0 + 5 * per
    st.Box(t_e, 360, 466, 570, 54, [("近い物(2 m)は 遠い物(40 m)の %d 倍 流れる" % round(vel[0] / vel[4]), 14, "#1e3a8a"), ("だから、深度バッファから、画素ごとの流れを計算する", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "カメラが動くと、画面全体が流れる。でも、流れ方は、距離で違う"), (t0, t_e, "近い物ほど、画面で大きく動く"), (t_e, 99, "遠景はほとんど流れず、近景が大きく流れる(視差)")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "カメラ", "流れ: " + " / ".join("%g m → %.0f 画素" % (d, v) for d, v in zip(ds, vel)))
    return Build(st, name, "graphics/postprocess/motion-blur/camera-blur.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 19.0])


# ===================================================================== object blur rotation
def ObjectBlurRotation():
    name = "object-blur-rotation"
    st = Stage(name, "回転する物のブラー: 先端ほど速く動く。直線で流すと、回転が大きいとき、先端が外れる", duration=21.0, subtitle="プロペラの羽根(半径 1〜5)。1 フレームで回る角度を 10° → 30° → 60° → 90° に変える。円弧と、直線の差を測る")
    sc, root = st.scene, st.root
    cx, cy, S = 300.0, 290.0, 34.0
    angles = [10.0, 30.0, 60.0, 90.0]
    rads = [1.0, 2.0, 3.0, 4.0, 5.0]
    def Dev(r, a):
        th = math.radians(a)
        # 円弧の中点と、直線(弦)の中点の距離(矢高)
        return r * (1 - math.cos(th / 2))
    devs = [[Dev(r, a) for r in rads] for a in angles]
    assert devs[3][4] > devs[1][4] > devs[0][4]
    st.Panel(30, 96, 560, 340, "① 回る羽根の先端が通る道(青 = 円弧、赤 = 直線で流した場合)", color=BLUE)
    root.add("circle", cx=cx, cy=cy, r=6, fill=INK)
    t0, per = 1.5, 4.8
    for m, a in enumerate(angles):
        th = math.radians(a)
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        for r in rads:
            n = 18
            arc = [(cx + r * S * math.cos(-th * k / n + 0.0), cy - r * S * math.sin(-th * k / n + 0.0)) for k in range(n + 1)]
            arc = [(cx + r * S * math.cos(th * k / n), cy - r * S * math.sin(th * k / n)) for k in range(n + 1)]
            g.add("path", d=Poly(arc), fill="none", stroke=BLUE, stroke_width=2.5)
            g.add("line", x1=R(arc[0][0]), y1=R(arc[0][1]), x2=R(arc[-1][0]), y2=R(arc[-1][1]), stroke=RED, stroke_width=2.5, stroke_dasharray="5 4")
        g.add("line", x1=cx, y1=cy, x2=R(cx + 5 * S), y2=cy, stroke=GRAY, stroke_width=3)
        sc.Text(g, 50, 128, "1 フレームで %d° 回る" % a, size=20, weight=700, fill=PURPLE)
    st.Panel(620, 96, 310, 340, "② 円弧と直線のずれ(矢高)", color=RED)
    for m, a in enumerate(angles):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        for k, r in enumerate(rads):
            y = 150 + k * 50
            sc.Text(g, 636, y + 14, "半径 %g" % r, size=12, weight=700, fill=INK)
            w = devs[m][k] / devs[3][4] * 160
            g.add("rect", x=706, y=y, width=R(max(w, 2)), height=18, fill=RED, opacity=0.85)
            sc.Text(g, 706 + w + 6, y + 14, "%.2f" % devs[m][k], size=12, weight=700, fill=RED)
    st.Text(40, 470, "先端(半径 5)のずれ:", size=14)
    st.Counter(200, 474, [(t0 + m * per + 0.3, int(round(100 * devs[m][4]))) for m in range(4)], size=24, fill=RED)
    st.Text(250, 474, "(×0.01)", size=12, weight=500, fill=MUTED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.4, 360, 456, 570, 64, [("回転が小さい(10°)なら、直線で近似して十分(ずれ %.2f)" % devs[0][4], 13, "#166534"), ("90° では、ずれ %.2f。サンプルを、回転で曲げて取る方法もある" % devs[3][4], 13, "#991b1b")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "回転する物の、先端は、中心より速く動く"), (t0, t_e, "角度が大きくなると、円弧が曲がり、直線との差が広がる"), (t_e, 99, "速度バッファは直線の近似。大きな回転は、フレームを分けて描くなどで補う")], size=14, fill=MUTED, weight=500)
    for m, a in enumerate(angles):
        st.Note(t0 + m * per, "回転", "%d°: 先端のずれ %.2f" % (a, devs[m][4]))
    return Build(st, name, "graphics/postprocess/motion-blur/object-blur.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== MB vs TAA
def MotionBlurVsTaa():
    name = "motion-blur-vs-taa"
    st = Stage(name, "モーション ブラーと TAA: TAA は、動きに合わせて前の色を使い、くっきり保つ。ブラーは、動きの跡を、わざとぼかす", duration=21.0, subtitle="棒(幅 4)が右へ動く。速さ 4・8・16・32 画素 / フレーム。見た目の流れの長さと、TAA で、履歴を使いすぎたときの残像を比べる")
    sc, root = st.scene, st.root
    speeds = [4, 8, 16, 32]
    shutter = 0.5
    alpha = 0.1
    blur_len = [v * shutter for v in speeds]
    ghost_len = []
    for v in speeds:
        # 履歴をそのまま混ぜたときの残像(5% 未満になるまでの距離)
        k = math.ceil(math.log(0.05) / math.log(1 - alpha))
        ghost_len.append(k * v)
    assert ghost_len[-1] > blur_len[-1] * 10
    st.Panel(30, 96, 900, 250, "① 速さごとの、跡の長さ(画素)", color=BLUE)
    t0, per = 1.5, 4.2
    for m, v in enumerate(speeds):
        y = 138 + m * 52
        g = root.add("g", opacity=0)
        g.Show(t0 + m * per)
        sc.Text(g, 50, y + 14, "速さ %d" % v, size=14, weight=700, fill=INK)
        w1 = blur_len[m] / ghost_len[-1] * 560
        w2 = ghost_len[m] / ghost_len[-1] * 560
        g.add("rect", x=140, y=y, width=R(max(w1, 3)), height=16, fill=GREEN, opacity=0.85)
        sc.Text(g, 140 + w1 + 8, y + 13, "ブラー(シャッター 1/2): %g 画素" % blur_len[m], size=12, weight=700, fill=GREEN)
        g.add("rect", x=140, y=y + 20, width=R(max(w2, 3)), height=16, fill=RED, opacity=0.85)
        sc.Text(g, 140 + w2 + 8 if m < 3 else 140, y + 33, "履歴の残像(α=0.1、5%% まで): %g 画素" % ghost_len[m], size=12, weight=700, fill=RED)
    st.Panel(30, 366, 900, 110, "② 使い分け", color=PURPLE)
    t_c = t0 + 4 * per + 0.3
    items = [("TAA(再投影つき)", "動きの分だけ履歴の位置をずらして使う → 棒は、くっきり。ぼけない", GREEN), ("モーション ブラー", "動きの跡を、わざとぼかす → 速さが「見える」。映像らしさ", BLUE), ("TAA の履歴を再投影しない", "跡が %g 画素も残る → ゴースト(悪い)" % ghost_len[3], RED)]
    for k, (a, b, c) in enumerate(items):
        y = 400 + k * 24
        sc.Text(root, 50, y + 6, a, size=13, weight=700, fill=c, opacity=0).Show(t_c + k * 1.2)
        sc.Text(root, 260, y + 6, b, size=13, weight=500, fill=TEXT, opacity=0).Show(t_c + k * 1.2)
    st.Caption(30, 534, [(0.0, t0, "動く物は、TAA でも、ブラーでも、見た目が変わる"), (t0, t0 + 4 * per, "ブラーは、速さに比例して長くなる(意図した効果)"), (t0 + 4 * per, 99, "TAA の残像は、バグ。両方を使うときは、ブラーを先に、TAA を後に")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "ブラーと TAA", "ブラー %s / 残像 %s(画素)" % ("/".join("%g" % x for x in blur_len), "/".join("%g" % x for x in ghost_len)))
    return Build(st, name, "graphics/postprocess/motion-blur/strength-taa.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== tile max
def TileMax():
    name = "tile-max"
    st = Stage(name, "タイルの最大速度: 画面を小さなタイルに分け、タイルごとの最大の動きを調べて、ぼかす必要のない所を飛ばす", duration=21.0, subtitle="48×24 画素の速度(明るさ = 動きの大きさ)。4×4 のタイルごとに最大を取り、隣のタイルへ広げる。速い所だけ、重いぼかしをする")
    sc, root = st.scene, st.root
    NX, NY, T = 48, 24, 4
    vel = [[0.2 for _ in range(NX)] for _ in range(NY)]
    for j in range(3, 8):
        for i in range(6, 11):
            vel[j][i] = 9.0
    for j in range(16, 20):
        for i in range(34, 39):
            vel[j][i] = 5.0
    TX, TY = NX // T, NY // T
    tmax = [[max(vel[j][i] for j in range(ty * T, ty * T + T) for i in range(tx * T, tx * T + T)) for tx in range(TX)] for ty in range(TY)]
    nmax = [[max(tmax[min(TY - 1, max(0, ty + dy))][min(TX - 1, max(0, tx + dx))] for dx in (-1, 0, 1) for dy in (-1, 0, 1)) for tx in range(TX)] for ty in range(TY)]
    heavy = [[nmax[ty][tx] > 1.0 for tx in range(TX)] for ty in range(TY)]
    n_heavy = sum(1 for r in heavy for v in r if v)
    n_tiles = TX * TY
    assert 0 < n_heavy < n_tiles * 0.5
    CS = 15.0
    px = [30, 335, 640]
    labs = [("① 速度(明るい = 速い)", AMBER), ("② タイルごとの最大", PURPLE), ("③ 隣へ広げた最大(赤 = 重いぼかしが必要)", RED)]
    t0, per = 1.5, 4.0
    for p, (lab, col) in enumerate(labs):
        st.Panel(px[p], 100, NX * 6.0 + 4, NY * 6.0 + 4, lab, color=col)
    cs2 = 6.0
    g1 = Grid(st, px[0], 102, NX, NY, cs2, base="#0f172a")
    for j in range(NY):
        for i in range(NX):
            g1.Paint(i, j, 0.3, Mix("#0f172a", "#fde68a", min(1.0, vel[j][i] / 9.0)))
    g1.Flush()
    cs3 = cs2 * T
    g2 = Grid(st, px[1], 102, TX, TY, cs3, base="#0f172a")
    for ty in range(TY):
        for tx in range(TX):
            g2.Paint(tx, ty, t0 + 0.12 * (tx + ty), Mix("#0f172a", "#c4b5fd", min(1.0, tmax[ty][tx] / 9.0)))
    g2.Flush()
    g3 = Grid(st, px[2], 102, TX, TY, cs3, base="#0f172a")
    for ty in range(TY):
        for tx in range(TX):
            g3.Paint(tx, ty, t0 + per + 0.12 * (tx + ty), "#ef4444" if heavy[ty][tx] else "#1e293b")
    g3.Flush()
    t_c = t0 + 2 * per
    st.Text(40, 270, "タイルの数:", size=14)
    st.Counter(150, 274, [(t0 + 0.12 * (TX + TY), n_tiles), (t0 + per + 0.12 * (TX + TY), n_heavy)], size=24, fill=PURPLE)
    st.Text(190, 274, "(最初は全 %d 個 → 重いぼかしが必要 %d 個)" % (n_tiles, n_heavy), size=13, weight=500, fill=MUTED)
    cost_heavy = 40
    cost_light = 2
    full = n_tiles * cost_heavy
    tiled = n_heavy * cost_heavy + (n_tiles - n_heavy) * cost_light
    t_k = t_c + 0.5
    st.Panel(30, 300, 900, 170, "ぼかしの読み込み(1 タイルあたり: 重い %d、軽い %d)" % (cost_heavy, cost_light), color=GREEN)
    for k, (lab, v, col, y) in enumerate([("全タイルを重いぼかし", full, RED, 336), ("タイルの最大で、振り分ける", tiled, GREEN, 372)]):
        sc.Text(root, 50, y + 14, lab, size=14, weight=700, fill=col, opacity=0).Show(t_k + k * 1.2)
        w = v / full * 560
        b = root.add("rect", x=290, y=y, width=1, height=22, fill=col, opacity=0.85)
        b.Set(t_k + k * 1.2, "width", 1)
        b.Ramp(t_k + k * 1.2, t_k + k * 1.2 + 1.0, "width", R(w))
        sc.Text(root, 290 + w + 10, y + 17, "%d(×1 タイル)" % v, size=13, weight=700, fill=col, opacity=0).Show(t_k + k * 1.2 + 1.0)
    st.Text(50, 436, "約 %.1f 倍 速い。隣のタイルへ広げる理由: 隣の速い物の流れが、このタイルに、はみ出してくるから" % (full / tiled), size=14, weight=700, fill=BLUE, opacity=0).Show(t_k + 3.0)
    st.Caption(30, 534, [(0.0, t0, "画面の大半は、動かないので、ブラーは要らない"), (t0, t0 + per, "タイルごとに、最大の速さを調べる"), (t0 + per, t_c, "隣のタイルへ広げて、はみ出しに備える"), (t_c, 99, "速いタイルだけに、重い処理をする")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "タイル", "全 %d タイル中、重い %d タイル。読み込み %d → %d" % (n_tiles, n_heavy, full, tiled))
    return Build(st, name, "graphics/postprocess/motion-blur/tile-max.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 14.0, 20.0])


# ===================================================================== velocity buffer
def VelocityBuffer():
    name = "velocity-buffer"
    st = Stage(name, "速度バッファ: 画素ごとに「前のフレームでは、どこにいたか」を書いておき、前の色を引き当てる", duration=21.0, subtitle="1 列 48 画素。物 A は右へ 8、物 B は左へ 4 動いた。速度から前の位置を求めて、前のフレームの画像を読む")
    sc, root = st.scene, st.root
    n = 48
    colA, colB, bg = (0.95, 0.35, 0.3), (0.25, 0.5, 0.95), (0.88, 0.9, 0.92)
    def Frame(posA, posB):
        img = [bg] * n
        img = list(img)
        for i in range(n):
            if posA <= i < posA + 6:
                img[i] = colA
            if posB <= i < posB + 6:
                img[i] = colB
        return img
    prev = Frame(8, 34)
    cur = Frame(16, 30)
    # 速度(画素 = 現在位置 - 前の位置)
    vel = []
    for i in range(n):
        if 16 <= i < 22:
            vel.append(8)
        elif 30 <= i < 36:
            vel.append(-4)
        else:
            vel.append(0)
    repro = [prev[min(n - 1, max(0, i - vel[i]))] for i in range(n)]
    no_vel = [prev[i] for i in range(n)]
    err = lambda a: sum(1 for i in range(n) if max(abs(a[i][k] - cur[i][k]) for k in range(3)) > 0.05)
    e_r, e_n = err(repro), err(no_vel)
    assert 0 < e_r < e_n, (e_r, e_n)
    CW, X0 = 17.0, 60.0
    rows = [("前のフレーム", prev, GRAY, 110), ("いまのフレーム(物が動いた)", cur, BLUE, 168)]
    for lab, img, col, y in rows:
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=26.0)
        for i in range(n):
            g.Paint(i, 0, 0.3, Rgbh(img[i]))
        g.Flush()
    # 速度バッファ
    sc.Text(root, X0, 238, "速度バッファ(画素ごとの動き。右 = 赤、左 = 青)", size=13, weight=700, fill=PURPLE)
    gv = Grid(st, X0, 244, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=26.0)
    t0, dts = 1.5, 0.06
    for i in range(n):
        v = vel[i]
        c = "#f1f5f9" if v == 0 else (Mix("#fecaca", "#dc2626", min(1.0, v / 8)) if v > 0 else Mix("#bfdbfe", "#2563eb", min(1.0, -v / 8)))
        gv.Paint(i, 0, t0 + i * dts, c)
        if v:
            sc.Text(root, X0 + (i + 0.5) * CW, 262, "%+d" % v, size=9, weight=700, fill="#ffffff", anchor="middle", opacity=0).Show(t0 + i * dts)
    t_r = t0 + n * dts + 0.6
    sc.Text(root, X0, 306, "速度で前の位置を引き当てた画像(各画素: 前のフレームの「自分の位置 − 速度」の色)", size=13, weight=700, fill=GREEN)
    gr = Grid(st, X0, 312, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=26.0)
    for i in range(n):
        gr.Paint(i, 0, t_r + i * dts, Rgbh(repro[i]))
    gr.Flush()
    sc.Text(root, X0, 370, "速度を使わず、同じ位置を読んだ画像", size=13, weight=700, fill=RED)
    gn = Grid(st, X0, 376, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=26.0)
    for i in range(n):
        gn.Paint(i, 0, t_r + 3.4 + i * dts, Rgbh(no_vel[i]))
    gn.Flush()
    t_e = t_r + 3.4 + n * dts + 0.6
    st.Box(t_e, 60, 424, 860, 90, [("いまのフレームと食い違う画素: 速度あり %d 個 / 速度なし %d 個" % (e_r, e_n), 15, "#1e3a8a"), ("残る %d 個は、物が離れて、隠れていた所が見えた画素(ディスオクルージョン)。前の色が無いので、履歴を捨てる" % e_r, 13, TEXT), ("速度バッファは、TAA・モーション ブラーの土台。物の動きから、頂点シェーダーで計算して書く", 12, MUTED)], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "動く物の前の位置は、画素だけからは分からない"), (t0, t_r, "描くとき、前のフレームとの位置の差を、速度バッファに書く"), (t_r, t_e, "速度を引いて、前のフレームの色を引き当てる"), (t_e, 99, "速度なしだと、物の色が、前の位置のまま、ずれる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "速度", "食い違い: 速度あり %d / 速度なし %d" % (e_r, e_n))
    return Build(st, name, "graphics/postprocess/motion-blur/velocity-buffer.md", BEFORE, [2.0, 4.0, 7.0, 10.0, 15.0, 20.0])


# ===================================================================== lens flare
def LensFlareGhosts():
    name = "lens-flare-ghosts"
    st = Stage(name, "レンズ フレア(ゴースト): 光源から画面の中心を通る直線の上に、レンズの反射の像が、並ぶ", duration=21.0, subtitle="画面(16:9)の中の光源の位置が動くと、ゴーストの位置は、中心から見た対称の位置に動く。ゴーストの倍率 = −1.2, −0.6, 0.4, 0.9")
    sc, root = st.scene, st.root
    W, H = 640.0, 360.0
    X0, Y0 = 30.0, 100.0
    cx, cy = X0 + W / 2, Y0 + H / 2
    scales = [-1.2, -0.6, 0.4, 0.9]
    cols = [RED, AMBER, GREEN, BLUE]
    path = [(-0.7, 0.45), (-0.3, 0.2), (0.2, -0.25), (0.65, -0.4)]
    st.Panel(X0, Y0, W, H, "画面(中心から、光源・ゴーストの位置)", color=BLUE)
    root.add("circle", cx=cx, cy=cy, r=4, fill=INK)
    root.add("line", x1=X0, y1=cy, x2=X0 + W, y2=cy, stroke=LIGHT, stroke_width=1.2)
    root.add("line", x1=cx, y1=Y0, x2=cx, y2=Y0 + H, stroke=LIGHT, stroke_width=1.2)
    t0, per = 1.5, 4.5
    P = lambda p, s=1.0: (cx + p[0] * s * W / 2, cy - p[1] * s * H / 2)
    for m, p in enumerate(path):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        lx, ly = P(p)
        for k, s in enumerate(scales):
            gx, gy = P(p, s)
            g.add("line", x1=R(lx), y1=R(ly), x2=R(gx), y2=R(gy), stroke=cols[k], stroke_width=1.2, stroke_dasharray="4 4", opacity=0.7)
            g.add("circle", cx=R(gx), cy=R(gy), r=R(10 + 6 * abs(s)), fill=cols[k], fill_opacity=0.28, stroke=cols[k], stroke_width=2)
        g.add("circle", cx=R(lx), cy=R(ly), r=11, fill=AMBER, stroke="#ffffff", stroke_width=2.5)
        sc.Text(g, lx + 14, ly - 12, "光源", size=12, weight=700, fill="#92400e")
    st.Panel(690, 100, 240, 360, "ゴーストの位置", color=PURPLE)
    for m, p in enumerate(path):
        g = root.add("g", opacity=0)
        if m == 0:
            g.Set(0.0, "opacity", 1)
            g.Set(t0 + per, "opacity", 0)
        else:
            g.Show(t0 + m * per, t0 + (m + 1) * per if m < 3 else None)
        sc.Text(g, 706, 136, "光源 (%.2f, %.2f)" % p, size=14, weight=700, fill=INK)
        for k, s in enumerate(scales):
            sc.Text(g, 706, 174 + k * 36, "×%+.1f → (%.2f, %.2f)" % (s, p[0] * s, p[1] * s), size=13, weight=700, fill=cols[k])
        sc.Text(g, 706, 340, "光源が中心から遠いほど、", size=12, weight=500, fill=MUTED)
        sc.Text(g, 706, 358, "ゴーストも、遠くに離れる", size=12, weight=500, fill=MUTED)
    inside = [sum(1 for s in scales if abs(p[0] * s) <= 1 and abs(p[1] * s) <= 1) for p in path]
    st.Text(40, 480, "画面に入っているゴースト:", size=14)
    st.Counter(240, 484, [(t0 + m * per + 0.3, inside[m]) for m in range(4)], size=24, fill=PURPLE)
    st.Text(280, 484, "個(4 個中)", size=13, weight=500, fill=MUTED)
    t_e = t0 + 4 * per
    st.Box(t_e - 0.5, 480, 470, 450, 56, [("光源が画面の端にあるほど、ゴーストが広く散る。中心では、全部が重なる", 13, "#1e3a8a")], BLUE, "#eff6ff")
    st.Caption(30, 534, [(0.0, t0, "レンズの中で光が反射して、光源の像が、何個か、ずれて写る"), (t0, t_e, "ゴーストは、光源の位置 × 倍率(負なら反対側)"), (t_e, 99, "簡単な式で、位置が決まる。画面の端は、フェードで消す")], size=14, fill=MUTED, weight=500)
    for m, p in enumerate(path):
        st.Note(t0 + m * per, "フレア", "光源 (%.2f, %.2f): 画面内のゴースト %d 個" % (p[0], p[1], inside[m]))
    return Build(st, name, "graphics/postprocess/lens-effects/lens-flare.md", BEFORE, [2.0, 5.0, 9.0, 13.0, 17.0, 20.0])


# ===================================================================== CA compare
def ChromaticCompare():
    name = "chromatic-aberration-compare"
    st = Stage(name, "色収差の作り方: 3 色だけをずらす方法(速い)と、スペクトルを細かくたどる方法(きれい)", duration=20.0, subtitle="白と黒の縁。ずらす量は同じ(8 画素)。3 サンプル(R・G・B のみ)と 9 サンプル(波長を等間隔)の、縁の見え方を比べる")
    sc, root = st.scene, st.root
    n = 40
    edge = 20
    base = [1.0 if i >= edge else 0.0 for i in range(n)]
    def Samp(a, p):
        q = max(0.0, min(n - 1.0, p))
        i0 = int(math.floor(q)); t = q - i0
        return a[i0] * (1 - t) + a[min(n - 1, i0 + 1)] * t
    SH = 8.0
    # 3 サンプル
    three = []
    for i in range(n):
        three.append((Samp(base, i - SH), Samp(base, i), Samp(base, i + SH)))
    # 9 サンプル: 波長 0..1(0 = 赤、1 = 青)。位置は i + SH*(2w-1)。色の重み(R, G, B)は、波長で滑らかに
    def Weights(w):
        r = max(0.0, 1 - abs(w - 0.0) * 2.2) + 0.0
        g = max(0.0, 1 - abs(w - 0.5) * 2.2)
        b = max(0.0, 1 - abs(w - 1.0) * 2.2)
        return r, g, b
    K = 9
    ws = [k / (K - 1) for k in range(K)]
    tot = [sum(Weights(w)[c] for w in ws) for c in range(3)]
    nine = []
    for i in range(n):
        acc = [0.0, 0.0, 0.0]
        for w in ws:
            v = Samp(base, i + SH * (2 * w - 1) * -1)
            wr = Weights(w)
            for c in range(3):
                acc[c] += v * wr[c]
        nine.append(tuple(acc[c] / tot[c] for c in range(3)))
    def Steps(a):
        cols = []
        for t in a:
            key = tuple(round(v, 2) for v in t)
            if key not in cols:
                cols.append(key)
        return len(cols)
    s3, s9 = Steps(three), Steps(nine)
    assert s9 > s3
    CW, X0 = 20.0, 60.0
    rows = [("元の縁(白と黒)", [(v, v, v) for v in base], GRAY, 112), ("3 サンプル(R・G・B をずらす)", three, RED, 182), ("9 サンプル(波長をたどる)", nine, GREEN, 252)]
    t0, per = 1.5, 4.0
    for r_, (lab, vals, col, y) in enumerate(rows):
        sc.Text(root, X0, y - 4, lab, size=13, weight=700, fill=col)
        g = Grid(st, X0, y, n, 1, CW, base="#e5e7eb", stroke="#94a3b8", cell_h=34.0)
        for i in range(n):
            g.Paint(i, 0, 0.3 if r_ == 0 else t0 + (r_ - 1) * per + i * 0.05, Rgbh(vals[i]))
        g.Flush()
    t_c = t0 + 2 * per + 0.5
    cost3, cost9 = 3, 9
    st.Panel(30, 320, 900, 150, "比べる", color=PURPLE)
    lines = [("縁にできる色の段階", "3 サンプル: %d 段階(帯がはっきり)" % s3, "9 サンプル: %d 段階(なめらかな虹)" % s9), ("1 画素あたりの読み込み", "3 サンプル: %d 回" % cost3, "9 サンプル: %d 回(%d 倍)" % (cost9, cost9 // cost3))]
    for k, (a, b, c) in enumerate(lines):
        y = 358 + k * 44
        sc.Text(root, 50, y, a, size=14, weight=700, fill=INK, opacity=0).Show(t_c + k * 1.2)
        sc.Text(root, 330, y, b, size=14, weight=700, fill=RED, opacity=0).Show(t_c + k * 1.2)
        sc.Text(root, 640, y, c, size=14, weight=700, fill=GREEN, opacity=0).Show(t_c + k * 1.2)
    st.Text(50, 450, "ゲームでは、まず 3 サンプルで十分。大きなずれでは、帯が目立つので、サンプルを増やす", size=13, weight=700, fill=BLUE, opacity=0).Show(t_c + 3.0)
    st.Caption(30, 534, [(0.0, t0, "色収差は、色ごとに、ずれる量が違う"), (t0, t_c, "3 色だけずらすと、縁が 3 つの帯になる。多く取ると、連続した虹になる"), (t_c, 99, "ずらす量が小さければ 3 サンプル、大きければ多サンプル")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "色収差", "色の段階: 3 サンプル %d / 9 サンプル %d" % (s3, s9))
    return Build(st, name, "graphics/postprocess/lens-effects/chromatic-aberration.md", BEFORE, [2.0, 5.0, 8.0, 12.0, 16.0, 19.0])


NAMES = ["motion-blur-jitter", "camera-blur", "object-blur-rotation", "motion-blur-vs-taa", "tile-max", "velocity-buffer", "lens-flare-ghosts", "chromatic-aberration-compare"]
FIGS = [MotionBlurJitter, CameraBlur, ObjectBlurRotation, MotionBlurVsTaa, TileMax, VelocityBuffer, LensFlareGhosts, ChromaticCompare]
