import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

PAGE = "graphics/postprocess/"


def Halton(i, base):
    f, r = 1.0, 0.0
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def Coverage(inside, px, py, samples):
    """画素 (px, py) の中の標本点 samples [(u, v)] のうち、物体の内側にある割合。"""
    hit = sum(1 for (u, v) in samples if inside(px + u, py + v))
    return hit / len(samples)


def Shade(v):
    """物体=暗い(0.1)、背景=明るい(0.95)。coverage v → 灰色。"""
    return Hex([(0.95 - 0.85 * v) * 255] * 3)


def TaaJitter():
    name = "taa-jitter"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="TAA のジッター:毎フレーム標本の位置をずらして、平均する")
    root = scene.root
    n, cell, ox, oy = 5, 52, 40, 80
    inside = lambda x, y: x + 0.55 * y < 3.1
    frames = 8
    jit = [(Halton(i + 1, 2), Halton(i + 1, 3)) for i in range(frames)]
    t0, dt = 1.0, 1.15
    pix = []
    for j in range(n):
        for i in range(n):
            pix.append((i, j, root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 1, height=cell - 1, fill="#f1f5f9")))
    for (i, j, r) in pix:
        acc, steps = 0, []
        for k in range(frames):
            u, v = jit[k]
            hit = 1 if inside(i + u, j + v) else 0
            acc += hit
            steps.append((t0 + k * dt, Shade(acc / (k + 1))))
        r.Steps("fill", steps)
    dots = []
    for (i, j, r) in pix:
        d = root.add("circle", cx=ox + i * cell + 26, cy=oy + j * cell + 26, r=4, fill=RED, stroke="#ffffff", stroke_width=1.5, opacity=0)
        d.Steps("cx", [(t0 + k * dt, R(ox + i * cell + jit[k][0] * (cell - 1))) for k in range(frames)])
        d.Steps("cy", [(t0 + k * dt, R(oy + j * cell + jit[k][1] * (cell - 1))) for k in range(frames)])
        d.Show(t0, t0 + frames * dt)
    pts = [(R(ox + p[0] * cell), R(oy + p[1] * cell)) for p in [(0, 0), (n, 0), (n, 0)]]
    # 辺:x + 0.55 y = 3.1 → 画素座標の線
    x_top, x_bot = 3.1, 3.1 - 0.55 * n
    root.add("line", x1=R(ox + x_top * cell), y1=oy, x2=R(ox + x_bot * cell), y2=oy + n * cell, stroke=BLUE, stroke_width=2.5, stroke_dasharray="6 4")
    scene.Text(root, ox, oy - 14, "三角形の縁（青い破線）より左が物体", size=13, weight=500, fill=GRAY)
    scene.TextStack(root, 340, 110, [(t0 + k * dt, t0 + (k + 1) * dt, "フレーム %d:標本点 (%.2f, %.2f)" % (k + 1, jit[k][0], jit[k][1])) for k in range(frames)], size=17, fill=INK)
    scene.TextStack(root, 340, 150, [(t0 + k * dt, t0 + (k + 1) * dt, "ここまでの平均を表示（%d 枚）" % (k + 1)) for k in range(frames)], size=14, fill=GRAY, weight=500)
    scene.TextStack(root, 340, 210, [(0.0, t0, "1 フレーム目は、ギザギザ（0 か 1）"), (t0 + frames * dt, 20, "→ 縁の画素が、中間の灰色になった（なめらか）")], size=15, fill=RED)
    scene.TextStack(root, 340, 240, [(t0 + frames * dt, 20, "動かなければ、フレームを重ねるだけでアンチエイリアス")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 40, 372, "赤い点 = そのフレームの標本の位置（全画素で同じだけずらす）。ずらした結果を平均する。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "ハルトン列で 8 フレーム")
    return dict(name=name, page=PAGE + "antialiasing/index.md", scene=scene, size=(780, 400), times=[0.5, 2.5, 5.5, 11.0])


def SmaaEdgeWeights():
    name = "smaa-edge-weights"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="SMAA:縁を見つけ、本当の線の面積を求めて、画素を混ぜる")
    root = scene.root
    cols, rows, cell, ox, oy = 8, 4, 62, 40, 90
    line = lambda x: 0.55 * x + 0.5  # y = line(x) より上が物体(暗)
    inside = lambda x, y: y < line(x)
    sub = [((a + 0.5) / 8, (b + 0.5) / 8) for a in range(8) for b in range(8)]
    aliased, ideal = {}, {}
    for j in range(rows):
        for i in range(cols):
            aliased[(i, j)] = 1.0 if inside(i + 0.5, j + 0.5) else 0.0
            ideal[(i, j)] = Coverage(inside, i, j, sub)
    cells = {}
    for j in range(rows):
        for i in range(cols):
            cells[(i, j)] = root.add("rect", x=ox + i * cell, y=oy + j * cell, width=cell - 1, height=cell - 1, fill=Shade(aliased[(i, j)]))
    edges = root.add("g", opacity=0)
    for j in range(rows):
        for i in range(cols):
            a = aliased[(i, j)]
            if i + 1 < cols and aliased[(i + 1, j)] != a:
                edges.add("line", x1=ox + (i + 1) * cell, y1=oy + j * cell, x2=ox + (i + 1) * cell, y2=oy + (j + 1) * cell, stroke=AMBER, stroke_width=5)
            if j + 1 < rows and aliased[(i, j + 1)] != a:
                edges.add("line", x1=ox + i * cell, y1=oy + (j + 1) * cell, x2=ox + (i + 1) * cell, y2=oy + (j + 1) * cell, stroke=AMBER, stroke_width=5)
    edges.Show(2.5)
    true_line = root.add("line", x1=ox, y1=R(oy + line(0) * cell), x2=ox + cols * cell, y2=R(oy + line(cols) * cell), stroke=BLUE, stroke_width=3.5, opacity=0)
    true_line.Show(5.0)
    nums = root.add("g", opacity=0)
    nums.Show(6.0, 8.5)
    for j in range(rows):
        for i in range(cols):
            v = ideal[(i, j)]
            if 0.03 < v < 0.97:
                scene.Text(nums, ox + i * cell + cell / 2, oy + j * cell + cell / 2 + 5, "%.2f" % v, size=13, fill=RED, anchor="middle")
    for (i, j), r in cells.items():
        if abs(ideal[(i, j)] - aliased[(i, j)]) > 0.02:
            r.Steps("fill", [(8.5, Shade(ideal[(i, j)]))])
    scene.TextStack(root, 40, 370, [(0.0, 2.5, "元の画像:縁がギザギザ（階段）"), (2.5, 5.0, "① 隣り合う画素の明るさの差で、縁（橙）を見つける"), (5.0, 6.0, "② 縁の形（階段のパターン）から、本当の線（青）を推定する"), (6.0, 8.5, "③ 各画素の中で、線が覆う面積（0〜1）を求める"), (8.5, 20, "④ その面積で、隣の画素と混ぜる → なめらかな縁")], size=15, fill=INK)
    scene.Note(2.5, name, "縁検出 → 線の推定 → 面積 → 混ぜる")
    return dict(name=name, page=PAGE + "antialiasing/smaa.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 7.0, 10.0])


def TaaHistoryClamp():
    name = "taa-history-clamp"
    scene = NewScene(name, 780, 380, duration=11.0, hold=1.5, title="履歴のクランプ:近傍の範囲に収めて、ゴーストを消す")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 480, 240, 14.0, 1.0, "フレーム", "明るさ")
    steps = 14
    cur = [0.2 if k < 4 else 0.9 for k in range(steps + 1)]
    band = 0.08
    hist_plain, hist_clamp = [0.2], [0.2]
    alpha = 0.12
    for k in range(1, steps + 1):
        hist_plain.append(hist_plain[-1] + (cur[k] - hist_plain[-1]) * alpha)
        h = min(max(hist_clamp[-1], cur[k] - band), cur[k] + band)
        hist_clamp.append(h + (cur[k] - h) * alpha)
    # 近傍の範囲(帯)
    pts_hi = " L".join("%s,%s" % (ax.X(k), ax.Y(cur[k] + band)) for k in range(steps + 1))
    pts_lo = " L".join("%s,%s" % (ax.X(k), ax.Y(cur[k] - band)) for k in reversed(range(steps + 1)))
    root.add("path", d="M" + pts_hi + " L" + pts_lo + " Z", fill=AMBER, fill_opacity=0.25, stroke="none")
    root.add("path", d="M" + " L".join("%s,%s" % (ax.X(k), ax.Y(cur[k])) for k in range(steps + 1)), fill="none", stroke=INK, stroke_width=3)
    scene.Text(root, ax.X(0.3), ax.Y(0.2) + 22, "今のフレームの色（物体が明るくなる）", size=12, fill=INK, weight=500)
    scene.Text(root, ax.X(7.6), ax.Y(0.98) + 16, "近傍の範囲（橙の帯）", size=12, fill=AMBER)
    p_plain = root.add("path", d="M" + " L".join("%s,%s" % (ax.X(k), ax.Y(hist_plain[k])) for k in range(steps + 1)), fill="none", stroke=RED, stroke_width=4, opacity=0)
    p_clamp = root.add("path", d="M" + " L".join("%s,%s" % (ax.X(k), ax.Y(hist_clamp[k])) for k in range(steps + 1)), fill="none", stroke=GREEN, stroke_width=4, opacity=0)
    d1 = root.add("circle", cx=ax.X(0), cy=ax.Y(0.2), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5, opacity=0)
    d2 = root.add("circle", cx=ax.X(0), cy=ax.Y(0.2), r=7, fill=GREEN, stroke="#ffffff", stroke_width=1.5, opacity=0)
    for node, series, t0 in ((d1, hist_plain, 1.0), (d2, hist_clamp, 6.2)):
        node.Show(t0)
        prev = None
        for k in range(steps + 1):
            t = t0 + k * 0.38
            if k == 0:
                node.Set(t, "cx", ax.X(0)); node.Set(t, "cy", ax.Y(series[0]))
            else:
                node.Ramp(prev, t, "cx", ax.X(k)); node.Ramp(prev, t, "cy", ax.Y(series[k]))
            prev = t
    p_plain.Show(1.0)
    p_clamp.Show(6.2)
    scene.TextStack(root, 560, 120, [(1.0, 6.2, "クランプなし"), (6.2, 20, "クランプあり")], size=18, fill=INK)
    scene.TextStack(root, 560, 150, [(1.0, 6.2, "履歴（赤）が古い明るさに残り、"), (6.2, 20, "履歴（緑）は範囲の端へ寄せられ、")], size=14, fill=GRAY, weight=500)
    scene.TextStack(root, 560, 172, [(1.0, 6.2, "ゆっくり追いつく ＝ ゴースト"), (6.2, 20, "すぐ新しい色に追いつく")], size=14, fill=GRAY, weight=500)
    scene.TextStack(root, 50, 350, [(0.0, 6.2, "物体が明るくなった時、履歴が古い色のままだと、尾を引く"), (6.2, 20, "履歴を「近傍の最小〜最大」にクランプすると、尾を引かない")], size=14, fill=INK, weight=500)
    scene.Note(1.0, name, "クランプなし → あり")
    return dict(name=name, page=PAGE + "antialiasing/taa.md", scene=scene, size=(780, 380), times=[2.0, 5.5, 8.0, 11.0])


def TaaGhosting():
    name = "taa-ghosting"
    scene = NewScene(name, 780, 360, duration=10.0, hold=1.5, title="ゴースト:動く物体の後ろに、古い履歴が尾を引く")
    root = scene.root
    cells, cw, oy = 14, 24, 120
    panels = [(40, "履歴の拒否なし", True), (420, "拒否あり（クランプ・速度）", False)]
    t0, dt = 1.0, 0.55
    for px, title, ghost in panels:
        scene.Text(root, px, oy - 26, title, size=15, fill=RED if ghost else GREEN)
        for i in range(cells):
            root.add("rect", x=px + i * cw, y=oy, width=cw - 1, height=cw * 2, fill="#f1f5f9")
        for i in range(cells):
            c = root.add("rect", x=px + i * cw, y=oy, width=cw - 1, height=cw * 2, fill=INK, opacity=0)
            t = t0 + i * dt
            c.Set(t, "opacity", 1.0)
            if ghost:
                c.Ramp(t + dt, t + dt + 3.2, "opacity", 0.0)
            else:
                c.Set(t + dt, "opacity", 0.0)
    scene.TextStack(root, 40, 230, [(0.0, 20, "物体が右へ動く(1 マス / フレーム)")], size=14, fill=GRAY, weight=500)
    scene.TextStack(root, 40, 270, [(0.0, 5.0, "左:通ったマスに、薄い影が残る（履歴を捨てない）"), (5.0, 20, "→ 長い尾が見える（ゴースト）")], size=15, fill=RED)
    scene.TextStack(root, 420, 270, [(0.0, 5.0, "右:履歴が合わなければ捨てる"), (5.0, 20, "→ 尾が出ない")], size=15, fill=GREEN)
    scene.Text(root, 40, 330, "対策:近傍クランプ・速度による再投影・深度や法線での拒否。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "物体が右へ動く")
    return dict(name=name, page=PAGE + "antialiasing/taa-challenges.md", scene=scene, size=(780, 360), times=[3.0, 5.5, 7.5, 10.0])


def AaCompare():
    name = "aa-compare"
    scene = NewScene(name, 780, 360, duration=11.0, hold=1.5, title="縁のなめらかさを並べて比べる（同じ斜めの縁）")
    root = scene.root
    cols, rows, cell = 7, 6, 20
    line = lambda x: 0.6 * x + 0.8
    inside = lambda x, y: y < line(x)
    sub8 = [((a + 0.5) / 8, (b + 0.5) / 8) for a in range(8) for b in range(8)]
    msaa = [(0.125, 0.625), (0.375, 0.125), (0.625, 0.875), (0.875, 0.375)]
    taa = [(Halton(i + 1, 2), Halton(i + 1, 3)) for i in range(8)]
    base = {(i, j): 1.0 if inside(i + 0.5, j + 0.5) else 0.0 for j in range(rows) for i in range(cols)}

    def Fxaa(i, j):
        v = base[(i, j)]
        nb = [base.get((i + dx, j + dy), v) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if any(abs(x - v) > 0.5 for x in nb):
            return 0.5 * v + 0.5 * sum(nb) / 4
        return v

    methods = [
        ("なし", lambda i, j: base[(i, j)], "ギザギザ", "0 ms"),
        ("FXAA", Fxaa, "少しぼけて、なめらか", "とても軽い"),
        ("SMAA", lambda i, j: Coverage(inside, i, j, sub8), "縁に忠実", "軽い"),
        ("MSAA 4x", lambda i, j: Coverage(inside, i, j, msaa), "4 段階", "重い"),
        ("TAA", lambda i, j: Coverage(inside, i, j, taa), "最もなめらか", "軽い（履歴）"),
    ]
    for m, (label, fn, memo, cost) in enumerate(methods):
        px = 18 + m * 150
        t = 0.8 + m * 1.9
        g = root.add("g", opacity=0)
        g.Show(t)
        for j in range(rows):
            for i in range(cols):
                g.add("rect", x=px + i * cell, y=90 + j * cell, width=cell, height=cell, fill=Shade(fn(i, j)))
        g.add("rect", x=px, y=90, width=cols * cell, height=rows * cell, fill="none", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(g, px + cols * cell / 2, 78, label, size=15, fill=INK, anchor="middle")
        scene.Text(g, px + cols * cell / 2, 90 + rows * cell + 22, memo, size=12, fill=GRAY, anchor="middle", weight=500)
        scene.Text(g, px + cols * cell / 2, 90 + rows * cell + 40, cost, size=12, fill=BLUE, anchor="middle", weight=500)
    scene.TextStack(root, 20, 330, [(0.8, 20, "どれも同じ縁。左から、なし・FXAA・SMAA・MSAA・TAA（TAA は 8 フレーム分の平均）")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "5 方式を順に表示")
    return dict(name=name, page=PAGE + "antialiasing/comparison.md", scene=scene, size=(780, 360), times=[1.5, 3.5, 5.5, 10.0])


def Lut(kind, x):
    """x(0〜1)を通す、LUT のトーン カーブ。(r, g, b)"""
    if kind == 0:  # ウォーム
        return (min(1.0, x ** 0.85 * 1.05 + 0.03 * (1 - x)), x, max(0.0, x ** 1.25 * 0.92))
    return (max(0.0, x ** 1.2 * 0.9), x ** 0.95, min(1.0, x ** 0.8 * 1.05 + 0.06 * (1 - x)))  # クール


def ColorLutLookup():
    name = "color-lut-lookup"
    scene = NewScene(name, 780, 380, duration=12.0, hold=1.5, title="LUT:入力の色を表に引いて、出力の色に置き換える")
    root = scene.root
    ax = Axes(scene, root, 190, 80, 330, 230, 1.0, 1.0, "入力", "出力")
    cols = [RED, GREEN, BLUE]
    paths = []
    for c in range(3):
        d0 = ax.D(lambda v, c=c: Lut(0, v)[c], n=30)
        p = root.add("path", d=d0, fill="none", stroke=cols[c], stroke_width=3.5)
        d1 = ax.D(lambda v, c=c: Lut(1, v)[c], n=30)
        p.Ramp(5.6, 6.6, "d", d1)
        paths.append(p)
    scene.TextStack(root, 190, 330, [(0.0, 5.6, "LUT A（暖色）:赤が持ち上がり、青が沈む"), (6.6, 20, "LUT B（寒色）:青が持ち上がり、赤が沈む")], size=14, fill=INK)
    # 入力のバー
    scene.Text(root, 30, 70, "入力（グレー）", size=13, fill=GRAY)
    bar_x, bar_y, bar_h = 30, 90, 220
    for k in range(20):
        v = k / 19
        root.add("rect", x=bar_x, y=bar_y + (19 - k) * bar_h / 20, width=36, height=bar_h / 20 + 0.5, fill=Gray(v ** 2.2 if False else v))
    marker = root.add("polygon", points="70,0 84,-7 84,7", fill=AMBER)
    mline = root.add("line", x1=ax.X(0), y1=ax.y, x2=ax.X(0), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2)
    n = 22
    for (ta, tb, kind) in ((0.8, 5.0, 0), (7.2, 11.4, 1)):
        prev = None
        for i in range(n + 1):
            f = i / n
            t = Lerp(ta, tb, f)
            x = f
            ys = bar_y + (1 - x) * bar_h
            if i == 0 and kind == 0:
                marker.Set(t, "points", "70,%s 84,%s 84,%s" % (R(ys), R(ys - 7), R(ys + 7)))
                mline.Set(t, "x1", ax.X(x)); mline.Set(t, "x2", ax.X(x))
            else:
                if i == 0:
                    marker.Set(t, "points", "70,%s 84,%s 84,%s" % (R(ys), R(ys - 7), R(ys + 7)))
                    mline.Set(t, "x1", ax.X(x)); mline.Set(t, "x2", ax.X(x))
                else:
                    marker.Ramp(prev, t, "points", "70,%s 84,%s 84,%s" % (R(ys), R(ys - 7), R(ys + 7)))
                    mline.Ramp(prev, t, "x1", ax.X(x)); mline.Ramp(prev, t, "x2", ax.X(x))
            prev = t
    out = root.add("rect", x=560, y=90, width=170, height=110, fill=Gray(0.0), stroke="#94a3b8", stroke_width=2)
    scene.Text(root, 645, 80, "出力の色", size=13, fill=GRAY, anchor="middle")
    inn = root.add("rect", x=560, y=225, width=170, height=60, fill=Gray(0.0), stroke="#94a3b8", stroke_width=2)
    scene.Text(root, 645, 216, "入力の色", size=13, fill=GRAY, anchor="middle")
    for (ta, tb, kind) in ((0.8, 5.0, 0), (7.2, 11.4, 1)):
        RampFill(out, "fill", ta, tb, n, lambda f, kind=kind: Hex([c * 255 for c in Lut(kind, f)]))
        RampFill(inn, "fill", ta, tb, n, lambda f: Hex([f * 255] * 3))
    scene.Note(0.8, name, "LUT A → LUT B")
    return dict(name=name, page=PAGE + "color-grading/index.md", scene=scene, size=(780, 380), times=[1.5, 3.5, 5.3, 9.5])


def ColorLggCurves():
    name = "color-lgg-curves"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="リフト・ガンマ・ゲイン:暗部・中間・明部を別々に動かす")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 300, 260, 1.0, 1.0, "入力", "出力")
    root.add("line", x1=ax.X(0), y1=ax.Y(0), x2=ax.X(1), y2=ax.Y(1), stroke=LIGHT, stroke_width=2.5, stroke_dasharray="5 4")
    chans = [RED, GREEN, BLUE]

    def Apply(x, c, lift, gamma, gain):
        v = max(0.0, min(1.0, x * gain[c] + lift[c] * (1 - x)))
        return v ** (1.0 / gamma)

    def Params(phase, a):
        lift, gamma, gain = (0, 0, 0), 1.0, (1, 1, 1)
        if phase == 0:
            lift = (-0.10 * a, 0.0, 0.14 * a)
        elif phase == 1:
            gamma = 1.0 + 0.7 * a
        else:
            gain = (1.0 + 0.18 * a, 1.0, 1.0 - 0.28 * a)
        return lift, gamma, gain

    paths = []
    for c in range(3):
        l, g, ga = Params(0, 0)
        paths.append(root.add("path", d=ax.D(lambda v, c=c, l=l, g=g, ga=ga: Apply(v, c, l, g, ga), n=24), fill="none", stroke=chans[c], stroke_width=3.2))
    swatches = []
    for k in range(10):
        swatches.append(root.add("rect", x=420 + k * 32, y=110, width=31, height=70, fill=Gray(k / 9)))
    scene.Text(root, 420, 100, "グレーの階調が、どう変わるか", size=13, fill=GRAY)
    phases = [("リフト（暗部）", "暗部だけが青緑に寄る（赤が減り、青が増える）", 0.8, 4.0, "#7dd3fc", (0.0, 0.3)),
              ("ガンマ（中間）", "中間の明るさだけが明るくなる（暗部・明部は動かない）", 4.8, 8.4, "#bef264", (0.35, 0.65)),
              ("ゲイン（明部）", "明部だけが橙に寄る（赤が増え、青が減る）", 9.2, 12.8, "#fdba74", (0.7, 1.0))]
    n = 14
    for ph, (label, desc, ta, tb, zc, zone) in enumerate(phases):
        zr = root.add("rect", x=ax.X(zone[0]), y=ax.y, width=R(ax.X(zone[1]) - ax.X(zone[0])), height=ax.h, fill=zc, opacity=0)
        zr.Set(ta, "opacity", 0.35)
        zr.Set(tb + 0.4, "opacity", 0)
        scene.TextStack(root, 420, 230, [(ta, tb + 0.4, label)], size=20, fill=INK)
        scene.TextStack(root, 420, 262, [(ta, tb + 0.4, desc)], size=13, fill=GRAY, weight=500)
        prev = None
        for i in range(n + 1):
            f = i / n
            t = Lerp(ta, tb, f)
            a = math.sin(math.pi * f)
            lift, gamma, gain = Params(ph, a)
            for c in range(3):
                d = ax.D(lambda v, c=c: Apply(v, c, lift, gamma, gain), n=24)
                if i == 0 and ph == 0:
                    paths[c].Set(t, "d", d)
                elif i == 0:
                    paths[c].Set(t, "d", d)
                else:
                    paths[c].Ramp(prev, t, "d", d)
            for k, sw in enumerate(swatches):
                x = k / 9
                col = Hex([Apply(x, c, lift, gamma, gain) ** 1.0 * 255 for c in range(3)])
                col = Hex([(Apply(x, c, lift, gamma, gain) ** (1 / 2.2)) * 255 for c in range(3)])
                if i == 0:
                    sw.Set(t, "fill", col)
                else:
                    sw.Ramp(prev, t, "fill", col)
            prev = t
    scene.Text(root, 50, 372, "赤・緑・青の 3 本の曲線を、別々に曲げて、色味を作る。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "リフト → ガンマ → ゲイン")
    return dict(name=name, page=PAGE + "color-grading/lift-gamma-gain.md", scene=scene, size=(780, 420), times=[2.4, 6.6, 11.0, 13.0])


def LutHalfTexel():
    name = "lut-half-texel"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="半テクセル補正:LUT の格子点は、テクセルの「中心」にある")
    root = scene.root
    N = 4
    entries = [0.0, 0.15, 0.62, 1.0]
    x0, y0, w, h = 60, 110, 600, 60
    tw = w / N
    for i, e in enumerate(entries):
        root.add("rect", x=x0 + i * tw, y=y0, width=tw - 1, height=h, fill=Gray(e), stroke=INK, stroke_width=1.5)
        scene.Text(root, x0 + i * tw + tw / 2, y0 + h + 20, "格子点 %d = %.2f" % (i, e), size=13, fill=INK, anchor="middle", weight=500)
        root.add("circle", cx=x0 + i * tw + tw / 2, cy=y0 + h / 2, r=4, fill=AMBER)
    scene.Text(root, x0, y0 - 12, "1D の LUT（4 個）。橙の点が各テクセルの中心", size=13, fill=GRAY, weight=500)

    def Sample(u):
        c = [(i + 0.5) / N for i in range(N)]
        if u <= c[0]:
            return entries[0]
        if u >= c[-1]:
            return entries[-1]
        for i in range(N - 1):
            if c[i] <= u <= c[i + 1]:
                f = (u - c[i]) / (c[i + 1] - c[i])
                return entries[i] + (entries[i + 1] - entries[i]) * f

    ks = [0, 1, 2, 3]
    t0, dt = 1.0, 2.6
    for k in ks:
        v = k / (N - 1)
        t = t0 + k * dt
        un = v
        uc = (v * (N - 1) + 0.5) / N
        g = root.add("g", opacity=0)
        g.Show(t, t + dt)
        g.add("line", x1=R(x0 + un * w), y1=y0 - 6, x2=R(x0 + un * w), y2=y0 + h + 6, stroke=RED, stroke_width=3)
        g.add("line", x1=R(x0 + uc * w), y1=y0 - 6, x2=R(x0 + uc * w), y2=y0 + h + 6, stroke=GREEN, stroke_width=3)
        en, ec = Sample(un), Sample(uc)
        scene.Text(g, 60, 260, "入力 v = %d/3 → 引くべきは 格子点 %d（%.2f）" % (k, k, entries[k]), size=17, fill=INK)
        scene.Text(g, 60, 296, "補正なし u = v = %.3f → %.2f（誤差 %.2f）" % (un, en, abs(en - entries[k])), size=16, fill=RED)
        scene.Text(g, 60, 326, "補正あり u = (v·(N−1) + 0.5) / N = %.3f → %.2f（誤差 %.2f）" % (uc, ec, abs(ec - entries[k])), size=16, fill=GREEN)
    scene.Text(root, 60, 372, "u = v のままだと、格子点の位置が半テクセルずれて、中間の値が混ざる。端の 0 と 1 以外で誤差が出る。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "4 つの格子点で比較")
    return dict(name=name, page=PAGE + "color-grading/lut-3d.md", scene=scene, size=(780, 400), times=[1.5, 4.0, 6.5, 9.5])


def LutBlendZones():
    name = "lut-blend-zones"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="時間帯の LUT 遷移:隣り合う 2 つを、重みで混ぜる")
    root = scene.root
    anchors = [(6, "朝", "#f4b183"), (12, "昼", "#7ec8f2"), (18, "夕", "#ff7f50"), (24, "夜", "#1d2b64")]

    def Weights(t):
        out = []
        for a, _, _ in anchors:
            d = min(abs(t - a), 24 - abs(t - a))
            out.append(max(0.0, 1 - d / 6.0))
        s = sum(out)
        return [w / s for w in out]

    ax = Axes(scene, root, 50, 90, 520, 200, 24.0, 1.0, "", "")
    scene.Text(root, 50, 62, "重み（縦）と時刻（横）", size=12, weight=500, fill=GRAY)
    for i, (a, label, col) in enumerate(anchors):
        ax.Curve(lambda v, a=a: max(0.0, 1 - min(abs(v - a), 24 - abs(v - a)) / 6.0), col, 4, n=48)
        scene.Text(root, ax.X(a) if a < 24 else ax.X(23.2), ax.y - 8, label, size=14, fill=col, anchor="middle")
    for hh in (0, 6, 12, 18, 24):
        scene.Text(root, ax.X(hh), ax.y + ax.h + 18, "%d 時" % hh, size=11, weight=500, fill=GRAY, anchor="middle")
    line = root.add("line", x1=ax.X(0), y1=ax.y, x2=ax.X(0), y2=ax.y + ax.h, stroke=INK, stroke_width=2.5)
    swatch = root.add("rect", x=610, y=110, width=130, height=90, fill=anchors[3][2], stroke="#94a3b8", stroke_width=2)
    scene.Text(root, 675, 100, "混ぜた色", size=13, fill=GRAY, anchor="middle")
    n = 36
    t0, t1 = 0.8, 11.2
    prev = None
    for i in range(n + 1):
        f = i / n
        t = Lerp(t0, t1, f)
        hh = 24.0 * f
        w = Weights(hh)
        col = Hex([sum(w[k] * ({0: 1, 1: 1, 2: 1}[0] * [int(anchors[k][2][1:3], 16), int(anchors[k][2][3:5], 16), int(anchors[k][2][5:7], 16)][c]) for k in range(4)) for c in range(3)])
        if i == 0:
            line.Set(t, "x1", ax.X(hh)); line.Set(t, "x2", ax.X(hh)); swatch.Set(t, "fill", col)
        else:
            line.Ramp(prev, t, "x1", ax.X(hh)); line.Ramp(prev, t, "x2", ax.X(hh)); swatch.Ramp(prev, t, "fill", col)
        prev = t
    LiveText(scene, root, 610, 240, t0, t1, n, lambda i, f: "%02d 時" % int(24.0 * i / n), size=22)
    LiveText(scene, root, 610, 270, t0, t1, n, lambda i, f: " / ".join("%s %.0f%%" % (anchors[k][1], 100 * Weights(24.0 * i / n)[k]) for k in range(4) if Weights(24.0 * i / n)[k] > 0.005), size=12, fill=GRAY, weight=500)
    scene.Text(root, 50, 350, "各時刻で、隣り合う 2 つの LUT の重みの合計が 1。太陽の高さなどから重みを決める。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "0 時 → 24 時")
    return dict(name=name, page=PAGE + "color-grading/lut-authoring.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.5, 9.5])


FIGS = [TaaJitter, SmaaEdgeWeights, TaaHistoryClamp, TaaGhosting, AaCompare, ColorLutLookup, ColorLggCurves, LutHalfTexel, LutBlendZones]
