import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

PAGE = "graphics/postprocess/"


def Shade(v):
    return Hex([(0.95 - 0.85 * v) * 255] * 3)


def FxaaEdge():
    name = "fxaa-edge"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="FXAA:画像だけを見て、コントラストの高い画素を、縁に沿ってぼかす")
    root = scene.root
    cols, rows, cell, ox, oy = 8, 5, 56, 60, 80
    line = lambda x: 0.55 * x + 0.9
    base = {(i, j): (1.0 if (j + 0.5) < line(i + 0.5) else 0.0) for i in range(cols) for j in range(rows)}
    cells = {}
    for (i, j), v in base.items():
        cells[(i, j)] = root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 1, height=cell - 1, fill=Shade(v))

    def Fxaa(i, j):
        v = base[(i, j)]
        nb = [base.get((i + dx, j + dy), v) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if any(abs(x - v) > 0.5 for x in nb):
            return 0.5 * v + 0.5 * sum(nb) / 4
        return v

    edge = [(i, j) for (i, j) in base if any(abs(base.get((i + dx, j + dy), base[(i, j)]) - base[(i, j)]) > 0.5 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for (i, j) in edge:
        o = root.add("rect", x=ox + i * cell + 2, y=oy + j * cell + 2, width=cell - 5, height=cell - 5, fill="none", stroke=AMBER, stroke_width=4, opacity=0)
        o.Show(2.0)
    for (i, j) in edge:
        cells[(i, j)].Steps("fill", [(6.0, Shade(Fxaa(i, j)))])
    scene.TextStack(root, 60, 56, [(0.0, 2.0, "元の画像（階段状の縁）"), (2.0, 6.0, "① 周りの明るさを比べて、コントラストが高い画素（橙）を探す"), (6.0, 20, "② その画素を、縁に垂直な方向の隣と混ぜる → 階段がやわらぐ")], size=15, fill=INK)
    scene.Text(root, 60, 396, "深度も法線も要らない。最終画像だけで動く（安い）。ただし、縁以外の細かい模様（文字・テクスチャ）も、少しぼけやすい。", size=12, weight=500, fill=GRAY)
    scene.Note(2.0, name, "検出 → ぼかし")
    return dict(name=name, page=PAGE + "antialiasing/fxaa.md", before="## ", scene=scene, size=(780, 400), times=[1.0, 4.0, 7.0, 10.0]) if False else dict(name=name, page=PAGE + "antialiasing/fxaa.md", before=FirstH(PAGE + "antialiasing/fxaa.md"), scene=scene, size=(780, 400), times=[1.0, 4.0, 7.0, 10.0])


def FirstH(page):
    import io
    t = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "docs", page), encoding="utf-8").read()
    for line in t.split(chr(10)):
        if line.startswith("## "):
            return line
    raise ValueError(page)


def MsaaSamples():
    name = "msaa-samples"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="MSAA:1 画素に複数のサンプルを置き、三角形に覆われた数で縁の濃さが決まる")
    root = scene.root
    cols, rows, cell, ox, oy = 7, 4, 70, 40, 90
    line = lambda x: 0.62 * x + 0.5
    inside = lambda x, y: y < line(x)
    spots = [(0.125, 0.625), (0.375, 0.125), (0.625, 0.875), (0.875, 0.375)]
    for j in range(rows):
        for i in range(cols):
            root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 1, height=cell - 1, fill="#f8fafc")
    xe = (rows - 0.5) / 0.62
    root.add("line", x1=ox, y1=R(oy + line(0) * cell), x2=R(ox + xe * cell), y2=oy + rows * cell, stroke=BLUE, stroke_width=3.5)
    scene.Text(root, ox + cols * cell, oy + rows * cell + 22, "青い線の上側が三角形", size=12, fill=BLUE, anchor="end")
    t0, step = 1.0, 0.18
    order = [(i, j) for j in range(rows) for i in range(cols)]
    cov = {}
    for k, (i, j) in enumerate(order):
        n_in = 0
        for (u, v) in spots:
            ins = inside(i + u, j + v)
            n_in += 1 if ins else 0
            d = root.add("circle", cx=R(ox + (i + u) * cell), cy=R(oy + (j + v) * cell), r=6, fill=RED if ins else "#ffffff", stroke=INK, stroke_width=1.5, opacity=0)
            d.Show(t0 + k * step)
        cov[(i, j)] = n_in / 4
    t_end = t0 + len(order) * step + 0.5
    for (i, j), c in cov.items():
        r = root.add("rect", x=ox + i * cell + 3, y=oy + j * cell + 3, width=cell - 7, height=cell - 7, fill=Shade(c), opacity=0, rx=3)
        r.Show(t_end)
    scene.TextStack(root, 40, 56, [(0.0, t_end, "各画素の 4 つのサンプルが、三角形の内側（赤）か外側（白）かを調べる"), (t_end, 20, "覆われたサンプルの割合で、画素の色を混ぜる（0/4〜4/4）")], size=15, fill=INK)
    scene.Text(root, 40, 396, "シェーディング（ライティング）は、画素ごとに 1 回だけ。深度・カバレッジだけを、サンプルごとに持つ。縁だけが滑らかになる。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "サンプルを順に判定")
    return dict(name=name, page=PAGE + "antialiasing/msaa.md", before=FirstH(PAGE + "antialiasing/msaa.md"), scene=scene, size=(780, 420), times=[2.5, 5.0, 8.0, 11.5])


def BloomThreshold():
    name = "bloom-threshold"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="しきい値:どの明るさから、光らせるか（ソフト ニー）")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 400, 230, 4.0, 3.0, "入力の輝度", "光らせる量")
    T = 1.0

    def Hard(x):
        return max(0.0, x - T)

    def Soft(x, knee):
        if knee <= 1e-6:
            return Hard(x)
        s = min(max(x - T + knee, 0.0), 2 * knee)
        s = s * s / (4 * knee + 1e-5)
        return max(s, x - T) if x > T + knee else s

    ax.Curve(Hard, GRAY, 3, n=80, dash="5 4")
    soft = root.add("path", d=ax.D(lambda x: Soft(x, 0.0), n=80), fill="none", stroke=BLUE, stroke_width=4)
    ax.parent.add("line", x1=ax.X(T), y1=ax.y, x2=ax.X(T), y2=ax.y + ax.h, stroke=RED, stroke_width=1.5, stroke_dasharray="4 3")
    scene.Text(root, ax.X(T) + 6, ax.y + 14, "しきい値 = 1", size=12, fill=RED)
    seq = [(0.8, 0.0), (3.5, 0.0), (7.0, 0.8), (10.5, 0.8)]
    for idx in range(1, len(seq)):
        ta, ka = seq[idx - 1]
        tb, kb = seq[idx]
        soft.Ramp(ta, tb, "d", ax.D(lambda x, kb=kb: Soft(x, kb), n=80))
    scene.TextStack(root, 500, 130, [(0.0, 3.5, "ニー = 0（ハード）"), (3.5, 7.0, "ニーを広げていくと…"), (7.0, 20, "ニー = 0.8（ソフト）")], size=18, fill=INK)
    scene.TextStack(root, 500, 162, [(0.0, 3.5, "しきい値の前後で、急に光り始める → ちらつく"), (7.0, 20, "しきい値の手前から、なだらかに光り始める → ちらつかない")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 250, "点線 = ハード（max(0, x − T)）", size=12, fill=GRAY, weight=500)
    scene.Text(root, 500, 274, "青 = ソフト ニー（なめらか）", size=12, fill=BLUE, weight=500)
    scene.Note(0.8, name, "ニー 0 → 0.8")
    return dict(name=name, page=PAGE + "bloom/threshold.md", before=FirstH(PAGE + "bloom/threshold.md"), scene=scene, size=(780, 400), times=[1.5, 4.5, 6.5, 10.0])


def WhiteBalance():
    name = "white-balance"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ホワイト バランス:光源の色かぶりを打ち消して、白を白に戻す")
    root = scene.root
    items = [("グレーの紙", (0.5, 0.5, 0.5)), ("白い壁", (0.92, 0.92, 0.92)), ("赤い服", (0.8, 0.2, 0.2)), ("青い服", (0.2, 0.3, 0.8))]
    cast = (1.25, 1.0, 0.7)  # 暖色の光(赤↑青↓)

    def Col(base, k):
        # k:0 = 色かぶりのまま、1 = 完全に補正
        mul = [cast[c] ** (1 - k) for c in range(3)]
        return Hex([min(1.0, base[c] * mul[c]) ** (1 / 2.2) * 255 for c in range(3)])

    sw = []
    for i, (label, base) in enumerate(items):
        x = 80 + i * 170
        r = root.add("rect", x=x, y=110, width=130, height=110, fill=Col(base, 0), stroke="#94a3b8", stroke_width=2)
        scene.Text(root, x + 65, 100, label, size=13, fill=INK, anchor="middle")
        sw.append((r, base))
    seq = [(0.8, 0.0), (2.5, 0.0), (6.5, 1.0), (9.0, 1.0)]
    n = 18
    states = []
    for idx in range(len(seq) - 1):
        ta, ka = seq[idx]
        tb, kb = seq[idx + 1]
        for i in range(n + 1):
            if idx > 0 and i == 0:
                continue
            states.append((Lerp(ta, tb, i / n), Lerp(ka, kb, i / n)))
    prev = None
    for k, (t, kk) in enumerate(states):
        for r, base in sw:
            v = Col(base, kk)
            if k == 0:
                r.Set(t, "fill", v)
            else:
                r.Ramp(prev, t, "fill", v)
        prev = t
    bar_x, bar_y, bar_w = 80, 290, 620
    root.add("rect", x=bar_x, y=bar_y, width=bar_w, height=14, rx=7, fill="url(#wb-grad)")
    g = scene.defs.add("linearGradient", id="wb-grad", x1=0, y1=0, x2=1, y2=0)
    g.add("stop", offset=0, stop_color="#60a5fa")
    g.add("stop", offset=0.5, stop_color="#ffffff")
    g.add("stop", offset=1, stop_color="#fb923c")
    scene.Text(root, bar_x, bar_y - 10, "色温度（青い光 ← → 暖かい光）", size=12, fill=GRAY, weight=500)
    knob = root.add("circle", cx=bar_x + bar_w * 0.82, cy=bar_y + 7, r=11, fill=INK, stroke="#ffffff", stroke_width=2)
    for idx in range(1, len(seq)):
        ta, ka = seq[idx - 1]
        tb, kb = seq[idx]
        knob.Ramp(ta, tb, "cx", R(bar_x + bar_w * (0.82 - 0.32 * kb)))
    scene.TextStack(root, 80, 360, [(0.0, 2.5, "暖色の光の下:グレーの紙が、橙がかって見える"), (2.5, 6.5, "色温度を青い側へ動かして、色かぶりを打ち消す…"), (6.5, 20, "グレーの紙が、無彩色に戻った。他の色も、自然な色に")], size=15, fill=INK)
    scene.Note(0.8, name, "色かぶりを補正")
    return dict(name=name, page=PAGE + "color-grading/white-balance.md", before=FirstH(PAGE + "color-grading/white-balance.md"), scene=scene, size=(780, 400), times=[1.0, 3.5, 5.0, 8.5])


def BasicAdjustments():
    name = "basic-adjustments"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="基本の調整:露出・コントラスト・彩度")
    root = scene.root
    base_cols = [(0.9, 0.2, 0.2), (0.95, 0.6, 0.1), (0.3, 0.7, 0.3), (0.2, 0.5, 0.9), (0.6, 0.3, 0.8), (0.5, 0.5, 0.5)]
    sw = []
    for i, c in enumerate(base_cols):
        r = root.add("rect", x=60 + i * 110, y=100, width=96, height=96, fill="#888888", stroke="#94a3b8", stroke_width=1.5)
        sw.append((r, c))

    def Apply(c, exp, con, sat):
        out = []
        lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        for ch in c:
            v = ch * (2 ** exp)
            v = (v - 0.5) * con + 0.5
            v = lum * (2 ** exp) * (1 - sat) + v * sat if False else v
            out.append(v)
        L = 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
        out = [L + (o - L) * sat for o in out]
        return Hex([max(0.0, min(1.0, o)) ** (1 / 2.2) * 255 for o in out])

    phases = [("露出 +1 EV", (0.0, 1.0, 1.0, 1.0)), ("コントラスト 1.6", (0.0, 0.0, 1.6, 1.0)), ("彩度 0（白黒）→ 1.6", (0.0, 0.0, 1.0, 0.0)), ("彩度 1.6（派手）", (0.0, 0.0, 1.0, 1.6))]
    params = [(0.8, (0, 1, 1)), (2.0, (0, 1, 1))]
    seq = [(0.8, (0.0, 1.0, 1.0)), (2.2, (0.0, 1.0, 1.0)), (4.0, (1.0, 1.0, 1.0)), (5.0, (1.0, 1.0, 1.0)), (6.5, (0.0, 1.0, 1.0)), (7.5, (0.0, 1.6, 1.0)), (9.0, (0.0, 1.6, 1.0)), (10.0, (0.0, 1.0, 0.0)), (11.0, (0.0, 1.0, 0.0)), (12.3, (0.0, 1.0, 1.6)), (13.5, (0.0, 1.0, 1.6))]
    for idx, (t, p) in enumerate(seq):
        for r, c in sw:
            v = Apply(c, p[0], p[1], p[2])
            if idx == 0:
                r.Set(t, "fill", v)
            else:
                r.Ramp(seq[idx - 1][0], t, "fill", v)
    ax = Axes(scene, root, 60, 250, 200, 140, 1.0, 1.0, "入力", "出力")
    cur = root.add("path", d=ax.D(lambda x: x, n=30), fill="none", stroke=BLUE, stroke_width=3.5)
    for idx, (t, p) in enumerate(seq):
        d = ax.D(lambda x, p=p: ((x * (2 ** p[0])) - 0.5) * p[1] + 0.5, n=30)
        if idx == 0:
            cur.Set(t, "d", d)
        else:
            cur.Ramp(seq[idx - 1][0], t, "d", d)
    scene.TextStack(root, 330, 290, [(0.0, 2.2, "元の色"), (2.2, 5.0, "露出 +1 EV:全体が 2 倍明るい"), (5.0, 6.5, "元に戻す"), (6.5, 9.0, "コントラスト 1.6:明暗の差が広がる"), (9.0, 11.0, "彩度 0:白黒になる"), (11.0, 20, "彩度 1.6:色が鮮やかになる")], size=17, fill=INK)
    scene.Text(root, 60, 420, "露出は掛け算、コントラストは 0.5 を中心に広げる、彩度は輝度との差を広げる", size=12, weight=500, fill=GRAY)
    scene.Note(0.8, name, "露出 → コントラスト → 彩度")
    return dict(name=name, page=PAGE + "color-grading/basic-adjustments.md", before=FirstH(PAGE + "color-grading/basic-adjustments.md"), scene=scene, size=(780, 440), times=[1.5, 4.0, 8.0, 12.5])


def CameraBlur():
    name = "camera-blur"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="カメラ ブラー:カメラの動きだけから、画面全体の速度が決まる")
    root = scene.root
    panels = [(190, "前へ進む:中心から外へ、放射状（外ほど速い）", "fwd"), (590, "横を向く:画面全体が、同じ向きに同じ速さ", "pan")]
    t0 = 1.0
    for px, title, kind in panels:
        cclip = scene.defs.add("clipPath", id="cb-clip-%d" % px)
        cclip.add("rect", x=px - 170, y=100, width=340, height=240)
        root.add("rect", x=px - 170, y=100, width=340, height=240, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, px, 88, title, size=12, fill=INK, anchor="middle")
        for gi in range(7):
            for gj in range(5):
                x = px - 150 + gi * 50
                y = 120 + gj * 50
                if kind == "fwd":
                    dx, dy = x - px, y - 220
                    d = math.hypot(dx, dy)
                    if d < 8:
                        continue
                    L = min(40, d * 0.28)
                    ux, uy = dx / d, dy / d
                else:
                    L, ux, uy = 28, 1.0, 0.0
                g = root.add("g", opacity=0, clip_path="url(#cb-clip-%d)" % px)
                g.Show(t0 + (gi + gj) * 0.18)
                g.add("line", x1=R(x), y1=R(y), x2=R(x + ux * L), y2=R(y + uy * L), stroke=BLUE, stroke_width=2.5)
                g.add("polygon", points="%s,%s %s,%s %s,%s" % (R(x + ux * L), R(y + uy * L), R(x + ux * (L - 8) - uy * 4), R(y + uy * (L - 8) + ux * 4), R(x + ux * (L - 8) + uy * 4), R(y + uy * (L - 8) - ux * 4)), fill=BLUE)
    scene.TextStack(root, 40, 380, [(0.0, 20, "物体の速度は使わず、深度から求めた位置を、前フレームのカメラ行列で投影し直して、差を取る。")], size=13, fill=INK, weight=500)
    scene.Text(root, 40, 404, "安く済むが、動く物体のブレは出ない（物体の動きは、速度バッファが必要）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "前進 / 回転")
    return dict(name=name, page=PAGE + "motion-blur/camera-blur.md", before=FirstH(PAGE + "motion-blur/camera-blur.md"), scene=scene, size=(780, 420), times=[1.5, 3.5, 5.5, 8.0])


def TileMax():
    name = "tile-max"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="タイル最大速度:タイルごとに、最も速い速度を求めて、ブラーの半径を決める")
    root = scene.root
    cols, rows, cell, ox, oy = 12, 6, 48, 40, 80
    rnd = random.Random(9)
    vel = {}
    for j in range(rows):
        for i in range(cols):
            fast = (3 <= i <= 6 and 1 <= j <= 3)
            L = rnd.uniform(10, 30) if fast else rnd.uniform(0, 8)
            ang = rnd.uniform(-0.4, 0.4) if fast else rnd.uniform(0, 6.28)
            vel[(i, j)] = (L * math.cos(ang), L * math.sin(ang))
    for j in range(rows):
        for i in range(cols):
            root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 1, height=cell - 1, fill="#f8fafc")
            vx, vy = vel[(i, j)]
            cx, cy = ox + i * cell + cell / 2, oy + j * cell + cell / 2
            L = math.hypot(vx, vy)
            if L > 1:
                root.add("line", x1=R(cx), y1=R(cy), x2=R(cx + vx * 0.9), y2=R(cy + vy * 0.9), stroke=GRAY, stroke_width=2)
    tile = 3
    tiles = [(0, 0), (1, 0), (2, 0), (3, 0)]
    t0, dt = 1.5, 2.8
    for k in range(4):
        ti, tj = k, 0 if k < 4 else 1
        tj = 0 if k < 2 else 1
        ti = (k % 2)
        ti, tj = [(0, 0), (1, 0), (1, 1), (0, 1)][k]
        ti, tj = [(0, 0), (1, 0), (1, 1), (2, 1)][k]
        tx, ty = ox + ti * tile * cell, oy + tj * tile * cell
        best, bi = -1, None
        for jj in range(tile):
            for ii in range(tile):
                key = (ti * tile + ii, tj * tile + jj)
                if key in vel:
                    L = math.hypot(*vel[key])
                    if L > best:
                        best, bi = L, key
        g = root.add("g", opacity=0)
        g.Show(t0 + k * dt, t0 + (k + 1) * dt)
        g.add("rect", x=tx, y=ty, width=tile * cell - 1, height=tile * cell - 1, fill="none", stroke=AMBER, stroke_width=4)
        cx, cy = ox + bi[0] * cell + cell / 2, oy + bi[1] * cell + cell / 2
        vx, vy = vel[bi]
        g.add("line", x1=R(cx), y1=R(cy), x2=R(cx + vx * 0.9), y2=R(cy + vy * 0.9), stroke=RED, stroke_width=4)
        scene.Text(g, tx + 6, ty + tile * cell - 8, "最大 %d" % round(best), size=13, fill=RED)
        out = root.add("g", opacity=0)
        out.Show(t0 + (k + 1) * dt - 0.4)
        out.add("rect", x=ox + 12 * cell + 20 + 0, y=oy + 30 + k * 42, width=70, height=34, fill=Mix("#f1f5f9", "#fca5a5", min(1.0, best / 30)), stroke="#94a3b8", stroke_width=1.5)
        scene.Text(out, ox + 12 * cell + 55, oy + 52 + k * 42, "%d" % round(best), size=14, fill=INK, anchor="middle")
    scene.TextStack(root, 40, 56, [(0.0, 1.5, "各画素の速度（灰色の矢印）"), (1.5, 13.5, "3×3 画素のタイルごとに、最大の速度（赤い矢印）を取り出す"), (13.5, 20, "タイルの最大速度で、ブラーのサンプル範囲を決める")], size=15, fill=INK)
    scene.Text(root, 40, 396, "速い物のタイルは、広くぼかす。静止した所は、ぼかさない（無駄な計算を省ける）。隣のタイルとも最大を取る（NeighborMax）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "タイルを順に")
    return dict(name=name, page=PAGE + "motion-blur/tile-max.md", before=FirstH(PAGE + "motion-blur/tile-max.md"), scene=scene, size=(780, 420), times=[2.0, 4.5, 7.5, 11.0])


def VelocityBuffer():
    name = "velocity-buffer"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="速度バッファ:今のフレームと前のフレームの位置の差を、画素に書く")
    root = scene.root
    root.add("rect", x=40, y=90, width=340, height=240, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, 210, 80, "画面（描画した絵）", size=13, fill=GRAY, anchor="middle")
    root.add("rect", x=400, y=90, width=340, height=240, fill="#808080", stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, 570, 80, "速度バッファ（色 = 速度の向きと大きさ）", size=13, fill=GRAY, anchor="middle")
    ghost = root.add("circle", cx=110, cy=210, r=30, fill="#fca5a5", fill_opacity=0.4, stroke=RED, stroke_width=2, stroke_dasharray="4 3")
    ball = root.add("circle", cx=110, cy=210, r=30, fill=RED, stroke="#ffffff", stroke_width=2)
    arrow = root.add("line", x1=110, y1=210, x2=110, y2=210, stroke=INK, stroke_width=3.5)
    vel_disc = root.add("circle", cx=470, cy=210, r=30, fill="#808080")
    vel_arrow = root.add("line", x1=470, y1=210, x2=470, y2=210, stroke=INK, stroke_width=3)
    seq = [(1.0, 110, 0), (3.0, 110, 0), (5.0, 220, 1), (7.0, 330, 2), (9.5, 330, 0)]
    xs = [110, 160, 250, 330, 330]
    # ball moves right, ghost (previous frame position) lags behind
    pos = [(0.8, 110), (4.0, 200), (7.5, 320), (9.5, 320), (10.8, 110)]
    for idx, (t, x) in enumerate(pos):
        prev_x = pos[idx - 1][1] if idx > 0 else x
        gx = x - (60 if x > 120 and idx < 4 else 0)
        vals = [(ball, "cx", x), (ghost, "cx", max(110, gx)), (arrow, "x1", max(110, gx)), (arrow, "x2", x),
                (vel_disc, "cx", 470 + (x - 110) * 0.62), (vel_arrow, "x1", 470 + (x - 110) * 0.62 - (60 * 0.62 if x > 120 and idx < 4 else 0)), (vel_arrow, "x2", 470 + (x - 110) * 0.62)]
        for node, attr, v in vals:
            if idx == 0:
                node.Set(t, attr, R(v))
            else:
                node.Ramp(pos[idx - 1][0], t, attr, R(v))
    # 速度ディスクの色(速度が出ている間は赤橙)
    vel_disc.Steps("fill", [(0.0, "#808080"), (1.5, "#ff9030"), (9.5, "#808080")])
    scene.TextStack(root, 40, 366, [(0.0, 20, "各画素に、「前のフレームの位置 → 今の位置」の差（2D ベクトル）を書く")], size=14, fill=INK, weight=500)
    scene.Text(root, 40, 392, "動いていない物は 0（灰色）。動く物の画素だけ、速度が入る。モーション ブラーや TAA の再投影が、この速度を読む。", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "ボールが動く")
    return dict(name=name, page=PAGE + "motion-blur/velocity-buffer.md", before=FirstH(PAGE + "motion-blur/velocity-buffer.md"), scene=scene, size=(780, 420), times=[1.5, 3.5, 6.0, 9.0])


def GammaSrgb():
    name = "gamma-srgb"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="ガンマ:リニアな光の量を、表示用に持ち上げる（暗部に多く割り当てる）")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 330, 230, 1.0, 1.0, "リニアな明るさ（光の量）", "表示する値（sRGB）")
    ax.Curve(lambda x: x, GRAY, 3, n=30, dash="5 4")
    ax.Curve(lambda x: x ** (1 / 2.2), BLUE, 4, n=60)
    scene.Text(root, ax.X(0.6), ax.Y(0.45), "そのまま", size=12, fill=GRAY)
    scene.Text(root, ax.X(0.12), ax.Y(0.78), "ガンマ補正", size=13, fill=BLUE)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    t0, t1, n = 0.8, 9.5, 26
    Sweep(dot, ax, lambda x: x ** (1 / 2.2), t0, t1, 0.0, 1.0, n)
    # 右:2 本の帯
    bx = 430
    scene.Text(root, bx, 110, "リニアの値をそのまま表示", size=13, fill=RED)
    scene.Text(root, bx, 210, "ガンマ補正して表示", size=13, fill=GREEN)
    for k in range(16):
        v = k / 15
        root.add("rect", x=bx + k * 19, y=120, width=19, height=50, fill=Hex([v * 255] * 3))
        root.add("rect", x=bx + k * 19, y=220, width=19, height=50, fill=Hex([(v ** (1 / 2.2)) * 255] * 3))
    mk1 = root.add("rect", x=bx, y=116, width=19, height=58, fill="none", stroke=AMBER, stroke_width=3)
    mk2 = root.add("rect", x=bx, y=216, width=19, height=58, fill="none", stroke=AMBER, stroke_width=3)
    mk1.Steps("x", [(Lerp(t0, t1, i / 15), R(bx + i * 19)) for i in range(16)])
    mk2.Steps("x", [(Lerp(t0, t1, i / 15), R(bx + i * 19)) for i in range(16)])
    LiveText(scene, root, 60, 350, t0, t1, n, lambda i, f: "リニア %.2f → 表示 %.2f" % (f, f ** (1 / 2.2)), size=16, fill=INK)
    scene.Text(root, 60, 384, "中間灰（実際の光の 18 %）は、表示では 0.46 に持ち上げられる。人間の目は、暗部の差に敏感なので、暗部を細かく持つ。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "0 → 1")
    return dict(name=name, page=PAGE + "tonemapping/gamma-srgb.md", before=FirstH(PAGE + "tonemapping/gamma-srgb.md"), scene=scene, size=(780, 420), times=[1.5, 3.5, 6.0, 9.0])


def ExposureEv():
    name = "exposure-ev"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="露出（EV）:+1 EV で光の量が 2 倍、−1 EV で半分")
    root = scene.root
    objs = [("暗い物(0.05)", 0.05), ("中間の物(0.18)", 0.18), ("明るい物(0.6)", 0.6), ("光源(3.0)", 3.0)]
    sw = []
    for i, (label, v) in enumerate(objs):
        x = 70 + i * 165
        r = root.add("rect", x=x, y=110, width=130, height=100, fill=Hex([min(1.0, v) ** (1 / 2.2) * 255] * 3), stroke="#94a3b8", stroke_width=2)
        scene.Text(root, x + 65, 100, label, size=12, fill=INK, anchor="middle")
        sw.append((r, v))
    seq = [(0.8, 0.0), (2.0, 0.0), (5.0, 3.0), (6.5, 3.0), (9.5, -3.0), (11.0, -3.0), (12.5, 0.0)]
    for idx, (t, ev) in enumerate(seq):
        for r, v in sw:
            col = Hex([min(1.0, v * 2 ** ev) ** (1 / 2.2) * 255] * 3)
            if idx == 0:
                r.Set(t, "fill", col)
            else:
                r.Ramp(seq[idx - 1][0], t, "fill", col)
    bx, by, bw = 90, 290, 600
    root.add("rect", x=bx, y=by, width=bw, height=12, rx=6, fill=LIGHT)
    for k in range(-3, 4):
        x = bx + (k + 3) / 6 * bw
        root.add("rect", x=x - 1, y=by - 6, width=2, height=24, fill=GRAY)
        scene.Text(root, x, by + 36, "%+d EV" % k if k else "0 EV", size=12, fill=GRAY, anchor="middle", weight=500)
    knob = root.add("circle", cx=bx + bw / 2, cy=by + 6, r=11, fill=BLUE, stroke="#ffffff", stroke_width=2)
    for idx, (t, ev) in enumerate(seq):
        v = R(bx + (ev + 3) / 6 * bw)
        if idx == 0:
            knob.Set(t, "cx", v)
        else:
            knob.Ramp(seq[idx - 1][0], t, "cx", v)
    scene.TextStack(root, 90, 360, [(0.0, 2.0, "露出 0 EV:中間の物が、中間の灰色"), (2.0, 5.0, "露出を上げる…"), (5.0, 6.5, "+3 EV（8 倍）:明るい物が白飛び"), (6.5, 9.5, "露出を下げる…"), (9.5, 11.0, "−3 EV（1/8）:暗い物が真っ黒（つぶれる）"), (11.0, 20, "0 EV に戻す")], size=15, fill=INK)
    scene.Note(0.8, name, "EV 0 → +3 → −3 → 0")
    return dict(name=name, page=PAGE + "tonemapping/exposure.md", before=FirstH(PAGE + "tonemapping/exposure.md"), scene=scene, size=(780, 400), times=[1.5, 4.0, 6.0, 10.0])


def HuePreserve():
    name = "hue-preserve"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="色相の保存:チャンネルごとに圧縮すると、明るい橙が、黄色く白っぽくなる")
    root = scene.root
    base = (1.0, 0.35, 0.05)
    levels = [1, 2, 4, 8, 16]

    def Reinhard(x):
        return x / (1 + x)

    def PerChannel(m):
        return [Reinhard(base[c] * m) for c in range(3)]

    def Luma(m):
        L = 0.2126 * base[0] * m + 0.7152 * base[1] * m + 0.0722 * base[2] * m
        s = Reinhard(L) / L
        return [min(1.0, base[c] * m * s) for c in range(3)]

    rows = [("チャンネルごと（色相が黄色い方へずれる・白くなる）", 120, PerChannel, RED), ("輝度で圧縮（色相を保つ）", 290, Luma, GREEN)]
    t0, dt = 1.0, 1.8
    for title, y, fn, col in rows:
        scene.Text(root, 60, y - 24, title, size=14, fill=col)
        for k, m in enumerate(levels):
            c = fn(m)
            g = root.add("g", opacity=0)
            g.Show(t0 + k * dt)
            g.add("rect", x=60 + k * 135, y=y, width=115, height=80, fill=Hex([min(1.0, ch) ** (1 / 2.2) * 255 for ch in c]), stroke="#94a3b8", stroke_width=1.5)
            scene.Text(g, 60 + k * 135 + 57, y + 100, "明るさ ×%d" % m, size=12, fill=GRAY, anchor="middle")
    scene.TextStack(root, 60, 56, [(0.0, 20, "同じ色（鮮やかな橙）を、明るさだけ 1・2・4・8・16 倍にして、トーン マップする")], size=14, fill=INK)
    scene.Text(root, 60, 396, "チャンネルごとの圧縮は、大きい成分ほど強く縮むので、色相がずれ、白に近づく。炎・爆発・ネオンで、色が抜ける原因になる。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "明るさ 1 → 16 倍")
    return dict(name=name, page=PAGE + "tonemapping/hue-preservation.md", before=FirstH(PAGE + "tonemapping/hue-preservation.md"), scene=scene, size=(780, 420), times=[2.0, 4.0, 7.0, 10.5])


FIGS = [FxaaEdge, MsaaSamples, BloomThreshold, WhiteBalance, BasicAdjustments, CameraBlur, TileMax, VelocityBuffer, GammaSrgb, ExposureEv, HuePreserve]
