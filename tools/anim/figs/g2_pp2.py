import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, LINE, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402
from g2_pp import Halton  # noqa: E402
from storyboard import Hex, Rgb  # noqa: E402

BEFORE = "## よくあるミス"


# ===================================================================== AA 比較
def AaCompare():
    name = "aa-compare"
    st = Stage(name, "アンチエイリアスの比較: 縁はなめらかに、細かい模様はぼかさずに", duration=19.0, subtitle="左半分は斜めの縁、右半分は 1 画素ごとの縞(細かい模様)。5 つの方法で、縁のずれと、縞の残り方を比べる")
    sc, root = st.scene, st.root
    NX, NY, CS = 24, 10, 12.0
    BG, FG = 0.95, 0.15
    inside = lambda x, y: y > 0.55 * x + 0.8
    stripe = lambda x: 0.85 if int(math.floor(x)) % 2 == 0 else 0.25

    def Sample(x, y):
        """画面上の位置 (x, y) の「本当の色」。左 12 列は縁、右 12 列は縞。"""
        if x < 12:
            return FG if inside(x, y) else BG
        return stripe(x)

    def Truth(i, j, m=8):
        return sum(Sample(i + (a + 0.5) / m, j + (b + 0.5) / m) for a in range(m) for b in range(m)) / (m * m)

    truth = [[Truth(i, j) for i in range(NX)] for j in range(NY)]
    none = [[Sample(i + 0.5, j + 0.5) for i in range(NX)] for j in range(NY)]
    # MSAA 4x(縁だけ 4 サンプル。模様は 1 回)
    ms_off = [(0.125, 0.625), (0.375, 0.125), (0.625, 0.875), (0.875, 0.375)]
    msaa = [[(sum(Sample(i + dx, j + dy) for dx, dy in ms_off) / 4 if i < 12 else Sample(i + 0.5, j + 0.5)) for i in range(NX)] for j in range(NY)]
    # FXAA(簡略): 周りとの輝度差が大きい画素を、周りの平均に寄せる
    def Fxaa(img):
        out = [row[:] for row in img]
        for j in range(NY):
            for i in range(NX):
                c = img[j][i]
                nb = [img[min(NY - 1, max(0, j + dj))][min(NX - 1, max(0, i + di))] for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                lo, hi = min(nb + [c]), max(nb + [c])
                if hi - lo > 0.12:
                    out[j][i] = 0.7 * c + 0.3 * sum(nb) / 4
        return out

    fxaa = Fxaa(none)
    # TAA(8 フレーム、ジッターで測り直して平均)
    jit = [(Halton(k + 1, 2) - 0.5, Halton(k + 1, 3) - 0.5) for k in range(8)]
    taa = [[sum(Sample(i + 0.5 + jx * 0.9, j + 0.5 + jy * 0.9) for jx, jy in jit) / 8 for i in range(NX)] for j in range(NY)]

    def EdgeErr(img):
        return sum(abs(img[j][i] - truth[j][i]) for j in range(NY) for i in range(12)) / (NY * 12)

    def Contrast(img):
        vals = [abs(img[j][i] - img[j][i + 1]) for j in range(NY) for i in range(12, NX - 1)]
        return sum(vals) / len(vals)

    c_truth = Contrast(truth)
    methods = [("なし(1 回測る)", none, GRAY, 1), ("FXAA(後から、ぼかす)", fxaa, RED, 1), ("MSAA 4x(縁だけ 4 回)", msaa, BLUE, 4), ("TAA(8 フレーム平均)", taa, PURPLE, 1)]
    stats = []
    for lab, img, col, n in methods:
        stats.append((EdgeErr(img), Contrast(img) / Contrast(none)))
    # 条件: FXAA は縞をつぶす、MSAA/なし は縞を残す、縁は FXAA/MSAA/TAA で改善
    assert stats[1][1] < 0.8 and stats[2][1] > 0.99 and stats[0][0] > stats[2][0] and stats[0][0] > stats[1][0], stats
    pos = [(30, 100), (335, 100), (640, 100), (30, 262), (335, 262)]
    t0, dts = 1.0, 0.18
    allm = methods + [("正解(1 画素を 64 回測る)", truth, GREEN, 64)]
    for k, (lab, img, col, n) in enumerate(allm):
        x, y = pos[k]
        st.Panel(x, y, NX * CS, NY * CS, lab, color=col)
        g = Grid(st, x, y, NX, NY, CS, base="#e5e7eb")
        for j in range(NY):
            for i in range(NX):
                g.Paint(i, j, t0 + (i * dts) + (0.0), Gray(img[j][i]))
        g.Flush()
        if k < 4:
            sc.Text(root, x, y + NY * CS + 18, "1 画素あたり測る回数: %d" % n, size=12, weight=500, fill=MUTED, opacity=0).Show(t0 + NX * dts)
        else:
            sc.Text(root, x, y + NY * CS + 18, "1 画素あたり測る回数: 64", size=12, weight=500, fill=MUTED, opacity=0).Show(t0 + NX * dts)
        # 境目
        root.add("line", x1=x + 12 * CS, y1=y, x2=x + 12 * CS, y2=y + NY * CS, stroke=RED, stroke_width=1.5, stroke_dasharray="4 4")
    st.Text(30, 392, "左半分 = 斜めの縁 / 右半分 = 1 画素ごとの縞", size=12, weight=500, fill=MUTED)
    # 結果の棒
    t_end = t0 + NX * dts + 0.8
    st.Panel(640, 262, 290, 140, "縁のずれ(小さいほど良い)", color=BLUE)
    maxe = max(s[0] for s in stats)
    for k, (lab, img, col, n) in enumerate(methods):
        y = 286 + k * 28
        sc.Text(root, 650, y + 14, ["なし", "FXAA", "MSAA", "TAA"][k], size=12, weight=700, fill=col)
        w = stats[k][0] / maxe * 150
        b = root.add("rect", x=700, y=y, width=0.5, height=18, fill=col, opacity=0.85)
        b.Set(t_end, "width", 0.5)
        b.Ramp(t_end, t_end + 1.0, "width", R(max(w, 1)))
        sc.Text(root, 700 + w + 6, y + 14, "%.3f" % stats[k][0], size=11, weight=700, fill=col, opacity=0).Show(t_end + 1.0)
    st.Panel(30, 420, 900, 96, "細かい模様(縞)の、くっきり度(「なし」を 100% とする)", color=PURPLE)
    for k, (lab, img, col, n) in enumerate(methods):
        x = 50 + k * 220
        sc.Text(root, x, 462, ["なし", "FXAA", "MSAA", "TAA"][k], size=13, weight=700, fill=col)
        sc.Text(root, x + 60, 466, "%d%%" % round(100 * stats[k][1]), size=22, weight=700, fill=(RED if stats[k][1] < 0.8 else GREEN), opacity=0).Show(t_end + 1.5)
        sc.Text(root, x, 490, ["そのまま", "縞がつぶれる", "模様は 1 回測る", "ぶれなければ残る"][k], size=11, weight=500, fill=MUTED, opacity=0).Show(t_end + 1.5)
    st.Caption(30, 534, [(0.0, t0, "同じ絵を、5 通りの方法で処理する"), (t0, t_end - 0.8, "左から右へ、画面をなぞる"), (t_end - 0.8, 99, "FXAA は縁を直すが、模様もぼかす。MSAA は縁だけ直す。TAA は縁も模様も、フレームを重ねて直す")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "AA", "縁のずれ: なし %.3f / FXAA %.3f / MSAA %.3f / TAA %.3f" % tuple(s[0] for s in stats))
    st.Note(t_end, "AA", "縞のくっきり度: FXAA %d%% / MSAA %d%%" % (round(100 * stats[1][1]), round(100 * stats[2][1])))
    return Build(st, name, "graphics/postprocess/antialiasing/comparison.md", BEFORE, [1.5, 3.5, 5.5, 8.0, 12.0, 17.0])


# ===================================================================== Tonemap
def TonemapCurves():
    name = "tonemap-curves"
    st = Stage(name, "トーンマップの比較: 明るさ(HDR)を、画面に出せる 0〜1 に押し込む", duration=20.0, subtitle="オレンジ色の物体を、暗い所から、白より 16 倍明るい所まで 32 段階で並べる。4 つの方法で、画面に出す")
    sc, root = st.scene, st.root
    N, CW, X0 = 32, 24.0, 70.0
    base = (1.0, 0.45, 0.1)
    exps = [0.05 * (16.0 / 0.05) ** (i / (N - 1)) for i in range(N)]

    def Reinhard(c):
        return c / (1 + c)

    def Aces(x):
        return max(0.0, min(1.0, (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)))

    def Hable(x):
        A, B, C, D, E, F = 0.15, 0.50, 0.10, 0.20, 0.02, 0.30
        f = lambda v: ((v * (A * v + C * B) + D * E) / (v * (A * v + B) + D * F)) - E / F
        return max(0.0, min(1.0, f(2.0 * x) / f(11.2)))

    ops = [("切り捨て(1 で頭打ち)", lambda c: min(1.0, c), GRAY), ("Reinhard", Reinhard, BLUE), ("ACES", Aces, RED), ("Hable(Uncharted 2)", Hable, GREEN)]

    def Gam(v):
        return v ** (1 / 2.2)

    rows = []
    for lab, f, col in ops:
        row = [[Gam(f(base[k] * e)) for k in range(3)] for e in exps]
        rows.append(row)

    def Lum(c):
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    def Hue(c):
        mx, mn = max(c), min(c)
        if mx - mn < 1e-6:
            return 0.0
        r, g, b = c
        if mx == r:
            h = ((g - b) / (mx - mn)) % 6
        elif mx == g:
            h = (b - r) / (mx - mn) + 2
        else:
            h = (r - g) / (mx - mn) + 4
        return h * 60.0

    stats = []
    for row in rows:
        clipped = sum(1 for c in row if min(c) > 0.97)
        usable = sum(1 for c in row if 0.05 < Lum(c) < 0.95)
        hue_hi = Hue(row[-3])
        stats.append((clipped, usable, hue_hi))
    hue0 = Hue([base[k] / max(base) for k in range(3)])
    assert stats[0][0] > stats[2][0] and stats[2][1] > stats[0][1]
    t0, per = 1.0, 3.6
    for r, (lab, f, col) in enumerate(ops):
        y = 100 + r * 66
        sc.Text(root, X0, y - 4, lab, size=14, weight=700, fill=col)
        g = Grid(st, X0, y, N, 1, CW, base="#e5e7eb", stroke="#94a3b8")
        for i in range(N):
            c = rows[r][i]
            g.Paint(i, 0, t0 + r * per + i * 0.06, Hex([255 * v for v in c]))
        g.Flush()
        gx = root.add("g", opacity=0)
        gx.Show(t0 + r * per + N * 0.06 + 0.1)
        sc.Text(gx, X0 + N * CW + 8, y + 14, "白飛び %d 段" % stats[r][0], size=12, weight=700, fill=(RED if stats[r][0] > 6 else TEXT))
        sc.Text(gx, X0 + N * CW + 8, y + 32, "使える段 %d / 32" % stats[r][1], size=12, weight=500, fill=MUTED)
    st.Text(X0, 82, "← 暗い      露出(0.05 〜 16 倍)      明るい →", size=12, weight=500, fill=MUTED)
    t_end = t0 + 4 * per + 0.4
    # 色相
    st.Panel(30, 372, 900, 144, "明るい所での色の変化(色相。元のオレンジ = %d°)" % round(hue0), color=PURPLE)
    for r, (lab, f, col) in enumerate(ops):
        x = 50 + r * 220
        c = rows[r][-3]
        sw = root.add("circle", cx=x + 26, cy=432, r=24, fill=Hex([255 * v for v in c]), stroke="#334155", stroke_width=2, opacity=0)
        sw.Show(t_end)
        gx = root.add("g", opacity=0)
        gx.Show(t_end)
        sc.Text(gx, x + 62, 424, lab.split("(")[0], size=13, weight=700, fill=col)
        sc.Text(gx, x + 62, 446, "色相 %d°(差 %d°)" % (round(stats[r][2]), round(abs(stats[r][2] - hue0))), size=12, weight=500, fill=TEXT)
        sc.Text(gx, x + 62, 468, ["白く潰れる", "くすんで暗い", "鮮やか(少し黄寄り)", "なだらか"][r], size=12, weight=700, fill=MUTED)
    st.Box(t_end + 1.0, 560, 484, 370, 30, [("切り捨ては白飛び、ACES・Hable は粘る", 13, "#1e3a8a")], BLUE, "#eff6ff") if False else None
    st.Caption(30, 534, [(0.0, t0, "同じ明るさの並びを、4 つの方法で画面に出す"), (t0, t_end - 0.4, "上から順に: 切り捨て、Reinhard、ACES、Hable"), (t_end - 0.4, 99, "切り捨てだと、明るい所が全部白に潰れる。曲線で圧縮すると、明るい所の差も残る")], size=14, fill=MUTED, weight=500)
    for r, (lab, f, col) in enumerate(ops):
        st.Note(t0 + r * per, "トーンマップ", "%s: 白飛び %d 段、使える段 %d / 32" % (lab, stats[r][0], stats[r][1]))
    return Build(st, name, "graphics/postprocess/tonemapping/index.md", BEFORE, [2.0, 4.5, 8.0, 12.0, 16.0, 19.0])


NAMES = ["aa-compare", "tonemap-curves"]
FIGS = [AaCompare, TonemapCurves]
