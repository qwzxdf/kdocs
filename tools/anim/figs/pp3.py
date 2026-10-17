import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

PAGE = "graphics/postprocess/"


def Tent(levels, v):
    """レベル(昇順の値)の間で線形に重みを配る。v に近い 2 つのレベルに重みを返す。"""
    out = [0.0] * len(levels)
    if v <= levels[0]:
        out[0] = 1.0
        return out
    if v >= levels[-1]:
        out[-1] = 1.0
        return out
    for i in range(len(levels) - 1):
        if levels[i] <= v <= levels[i + 1]:
            f = (v - levels[i]) / (levels[i + 1] - levels[i])
            out[i] = 1 - f
            out[i + 1] = f
            return out
    return out


def DofFocusSweep():
    name = "dof-focus-sweep"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ピント位置を動かすと、ボケる物が変わる")
    root = scene.root
    objs = [("手前", 2.0, "#e5484d", 34, 170), ("中間", 5.0, "#2ea043", 28, 340), ("奥", 8.0, "#2563eb", 22, 510)]
    # 上:真上から見た図(奥行き軸)
    ax_x0, ax_x1, ax_y = 60, 720, 110
    root.add("line", x1=ax_x0, y1=ax_y, x2=ax_x1, y2=ax_y, stroke=INK, stroke_width=2)
    scene.Text(root, ax_x0, ax_y - 38, "カメラ → 奥行き", size=13, fill=GRAY, weight=500)
    depth_x = lambda d: ax_x0 + (d - 1) / 8.5 * (ax_x1 - ax_x0)
    for label, d, color, r, _ in objs:
        root.add("circle", cx=depth_x(d), cy=ax_y, r=10, fill=color)
        scene.Text(root, depth_x(d), ax_y + 28, label, size=12, fill=color, anchor="middle")
    plane = root.add("rect", x=depth_x(1) - 3, y=ax_y - 26, width=6, height=52, fill=AMBER)
    scene.Text(root, 60, ax_y + 56, "橙の線 = ピントが合う奥行き", size=12, fill=AMBER, weight=500)
    # 下:画面
    levels = [0.0, 3.0, 6.0, 10.0]
    filters = [None] + [Blur(scene, "df-b%d" % i, v) for i, v in enumerate(levels[1:])]
    screen_y = 190
    root.add("rect", x=60, y=screen_y, width=660, height=170, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    copies = []
    for label, d, color, r, cx in objs:
        group = []
        for li, lv in enumerate(levels):
            attrs = dict(cx=cx + 20, cy=screen_y + 85, r=r, fill=color, opacity=0)
            if filters[li]:
                attrs["filter"] = filters[li]
            group.append(root.add("circle", **attrs))
        copies.append(group)
    n = 32
    t0, t1 = 1.0, 9.5
    prev = None
    for i in range(n + 1):
        f = i / n
        t = Lerp(t0, t1, f)
        focus = Lerp(1.0, 9.0, f)
        x = depth_x(focus)
        if i == 0:
            plane.Set(t, "x", R(x - 3))
        else:
            plane.Ramp(prev, t, "x", R(x - 3))
        for oi, (label, d, color, r, cx) in enumerate(objs):
            coc = abs(d - focus) * 1.4
            w = Tent(levels, coc)
            for li in range(len(levels)):
                if i == 0:
                    copies[oi][li].Set(t, "opacity", R(w[li]))
                else:
                    copies[oi][li].Ramp(prev, t, "opacity", R(w[li]))
        prev = t
    LiveText(scene, root, 60, 384, t0, t1, n, lambda i, f: "ピント = 奥行き %.1f（%s）" % (Lerp(1.0, 9.0, f), "手前" if Lerp(1.0, 9.0, f) < 3.5 else ("中間" if Lerp(1.0, 9.0, f) < 6.5 else "奥")), size=15, fill=INK)
    scene.Note(t0, name, "ピントを手前 → 奥へ")
    return dict(name=name, page=PAGE + "dof/index.md", scene=scene, size=(780, 400), times=[1.2, 3.5, 6.0, 9.2])


def CocGraph():
    name = "coc-graph"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="錯乱円（CoC）:ピントから離れるほど大きく、遠方は頭打ち")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 460, 250, 12.0, 40.0, "被写体までの距離（m）", "CoC（ピクセル）")

    def Coc(d, f, a):
        return a * abs(d - f) / d * 1.6 * f

    f0, a0 = 3.0, 1.0
    fs = [3.0, 6.0, 3.0]
    keys = []
    p = root.add("path", d=ax.D(lambda d: Coc(max(d, 0.4), f0, a0), x0=0.4, n=60), fill="none", stroke=BLUE, stroke_width=4)
    line = root.add("line", x1=ax.X(f0), y1=ax.y, x2=ax.X(f0), y2=ax.y + ax.h, stroke=AMBER, stroke_width=3)
    n = 16
    seq = [(0.8, 4.4, 3.0, 6.0, 1.0, 1.0), (4.4, 7.6, 6.0, 6.0, 1.0, 1.0), (7.6, 11.4, 6.0, 6.0, 1.0, 2.0)]
    prev_t = None
    state = (f0, a0)
    for (ta, tb, fa, fb, aa, ab) in seq:
        prev = None
        for i in range(n + 1):
            fr = i / n
            t = Lerp(ta, tb, fr)
            f = Lerp(fa, fb, fr)
            a = Lerp(aa, ab, fr)
            d = ax.D(lambda x: Coc(max(x, 0.4), f, a), x0=0.4, n=60)
            if prev is None:
                if ta == 0.8:
                    p.Set(t, "d", d)
                    line.Set(t, "x1", ax.X(f)); line.Set(t, "x2", ax.X(f))
                else:
                    p.Set(t, "d", d)
                    line.Set(t, "x1", ax.X(f)); line.Set(t, "x2", ax.X(f))
            else:
                p.Ramp(prev, t, "d", d)
                line.Ramp(prev, t, "x1", ax.X(f)); line.Ramp(prev, t, "x2", ax.X(f))
            prev = t
    scene.TextStack(root, 550, 120, [(0.0, 4.4, "ピント距離を 3 m → 6 m"), (4.4, 7.6, "ピント 6 m に固定"), (7.6, 20, "絞りを開く（F 値を下げる）")], size=17, fill=INK)
    scene.TextStack(root, 550, 150, [(0.0, 4.4, "谷（ボケゼロ）が奥へ動く"), (4.4, 7.6, "手前は急に大きく、奥は緩やかに"), (7.6, 20, "全体が大きくなる ＝ 背景が大きくボケる")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 550, 210, "手前側はすぐ大きくなる", size=13, fill=RED, weight=500)
    scene.Text(root, 550, 236, "奥側は、無限遠で頭打ち", size=13, fill=GREEN, weight=500)
    scene.Text(root, 60, 372, "CoC ≒ 絞りの口径 × |距離 − ピント| / 距離 × 焦点距離（薄いレンズの式の近似）", size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "ピント移動 → 絞り変更")
    return dict(name=name, page=PAGE + "dof/coc.md", scene=scene, size=(780, 400), times=[1.0, 3.0, 6.0, 10.5])


def DofGatherWeight():
    name = "dof-gather-weight"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="ギャザー:サンプル側の CoC を見て、重みを決める")
    root = scene.root
    cells, cw, ox = 20, 30, 40
    boundary = 10
    fg, bg = "#e5484d", "#2563eb"
    coc_bg = 6
    rows = [("重みなし（全サンプルを同じ重み）", 100, False), ("サンプルの CoC を見る（届かないサンプルは重み 0）", 270, True)]
    centers = [11, 12, 13, 14, 15]
    t0, dt = 1.0, 2.2
    for title, oy, weighted in rows:
        scene.Text(root, ox, oy - 28, title, size=14, fill=INK)
        for i in range(cells):
            root.add("rect", x=ox + i * cw, y=oy, width=cw - 1, height=cw, fill=fg if i < boundary else bg)
        scene.Text(root, ox + 3, oy + cw + 16, "前景（ピントが合う・CoC 0）", size=12, fill=fg, weight=500)
        scene.Text(root, ox + boundary * cw + 3, oy + cw + 16, "背景（ぼける・CoC %d）" % coc_bg, size=12, fill=bg, weight=500)
        for k, c in enumerate(centers):
            t = t0 + k * dt
            g = root.add("g", opacity=0)
            g.Show(t, t + dt)
            radius = coc_bg
            samples, wsum, col = [], 0.0, [0.0, 0.0, 0.0]
            for s in range(-radius, radius + 1):
                x = c + s
                if not (0 <= x < cells):
                    continue
                is_fg = x < boundary
                scoc = 0 if is_fg else coc_bg
                w = 1.0
                if weighted and scoc < abs(s):
                    w = 0.0
                samples.append((x, w))
                base = (0xe5, 0x48, 0x4d) if is_fg else (0x25, 0x63, 0xeb)
                for ch in range(3):
                    col[ch] += base[ch] * w
                wsum += w
            col = [v / wsum for v in col]
            g.add("rect", x=ox + c * cw - 1, y=oy - 3, width=cw + 1, height=cw + 5, fill="none", stroke=AMBER, stroke_width=3)
            for x, w in samples:
                g.add("circle", cx=ox + x * cw + cw / 2, cy=oy + cw / 2, r=5, fill="#ffffff" if w > 0 else "#475569", stroke=INK, stroke_width=1.5)
                if w == 0:
                    scene.Text(g, ox + x * cw + cw / 2, oy + cw / 2 + 4, "×", size=12, fill="#ffffff", anchor="middle")
            g.add("rect", x=ox + cells * cw + 14, y=oy, width=70, height=cw, fill=Hex(col), stroke="#94a3b8", stroke_width=2)
            scene.Text(g, ox + cells * cw + 49, oy + cw + 16, "結果の色", size=12, fill=GRAY, anchor="middle", weight=500)
    scene.TextStack(root, 40, 396, [(0.0, t0, "背景の画素（橙の枠）が、半径 6 の範囲を集めて平均する"), (t0, t0 + 5 * dt, "枠が前景に近づくにつれ、前景の赤が背景に混ざる（上）。下は混ざらない"), (t0 + 5 * dt, 20, "→ 重みなしは前景の輪郭に背景/前景の色がにじむ。サンプルの CoC が届かなければ捨てる")], size=13, fill=INK, weight=500)
    scene.Note(t0, name, "枠を前景へ近づける")
    return dict(name=name, page=PAGE + "dof/gather.md", scene=scene, size=(780, 440), times=[1.5, 3.8, 6.0, 9.0])


def DofNearField():
    name = "dof-near-field"
    scene = NewScene(name, 780, 380, duration=11.0, hold=1.5, title="前景のボケは、輪郭の外へ広がる")
    root = scene.root
    levels = [0.0, 5.0, 10.0, 16.0]
    filters = [None] + [Blur(scene, "nf-b%d" % i, v) for i, v in enumerate(levels[1:])]
    panels = [(40, "自分の CoC だけ使う（輪郭が硬い）", False), (410, "周りの最大 CoC を使う（輪郭の外へ広がる）", True)]
    t0, t1 = 1.0, 8.5
    n = 20
    for px, title, spread in panels:
        scene.Text(root, px, 70, title, size=14, fill=RED if not spread else GREEN)
        root.add("rect", x=px, y=90, width=330, height=220, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        for k in range(11):
            root.add("rect", x=px + 10 + k * 30, y=90, width=14, height=220, fill="#cbd5e1")
        copies = []
        for li in range(len(levels)):
            attrs = dict(cx=px + 165, cy=200, r=52, fill=RED, opacity=0)
            if filters[li]:
                attrs["filter"] = filters[li]
            if not spread:
                clip = scene.defs.add("clipPath", id="nf-clip-%d-%d" % (px, li))
                clip.add("circle", cx=px + 165, cy=200, r=52)
                attrs["clip-path"] = "url(#nf-clip-%d-%d)" % (px, li)
            copies.append(root.add("circle", **attrs))
        prev = None
        for i in range(n + 1):
            f = i / n
            t = Lerp(t0, t1, f)
            coc = 16.0 * math.sin(math.pi * f) ** 0.8
            w = Tent(levels, coc)
            for li in range(len(levels)):
                if i == 0:
                    copies[li].Set(t, "opacity", R(w[li]))
                else:
                    copies[li].Ramp(prev, t, "opacity", R(w[li]))
            prev = t
    scene.TextStack(root, 40, 346, [(0.0, 20, "ピントを背景に合わせると、手前の赤い物がボケる。左は輪郭が硬いまま。右は外にも広がる（本物のボケ）。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "手前の物が次第にボケる")
    return dict(name=name, page=PAGE + "dof/near-far.md", scene=scene, size=(780, 380), times=[1.5, 3.5, 5.0, 7.5])


def DofScatterGather():
    name = "dof-scatter-gather"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="ギャザー（集める）とスキャッター（まき散らす）")
    root = scene.root
    n, cw, oy = 9, 30, 90
    panels = [(30, "ギャザー:画素が、周りから集める"), (410, "スキャッター:明るい画素が、周りへまく")]
    for px, title in panels:
        scene.Text(root, px, oy - 22, title, size=14, fill=INK)
        for j in range(n):
            for i in range(n):
                root.add("rect", x=px + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
    gx, gy = 30, oy
    cx0, cy0 = 4, 4
    rad = 3
    ring = [(dx, dy) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1) if 0 < dx * dx + dy * dy <= rad * rad + 1 and (dx + dy) % 2 == 0]
    root.add("rect", x=gx + cx0 * cw - 2, y=gy + cy0 * cw - 2, width=cw + 3, height=cw + 3, fill="none", stroke=AMBER, stroke_width=4)
    t_g = 1.0
    for k, (dx, dy) in enumerate(ring):
        t = t_g + k * 0.17
        c = root.add("circle", cx=gx + (cx0 + dx) * cw + cw / 2, cy=gy + (cy0 + dy) * cw + cw / 2, r=5, fill=BLUE, stroke="#ffffff", stroke_width=1.5, opacity=0)
        c.Show(t)
        ln = root.add("line", x1=gx + (cx0 + dx) * cw + cw / 2, y1=gy + (cy0 + dy) * cw + cw / 2, x2=gx + cx0 * cw + cw / 2, y2=gy + cy0 * cw + cw / 2, stroke=BLUE, stroke_width=1.5, opacity=0)
        ln.Show(t)
    sx, sy = 410, oy
    ax0, ay0 = 4, 4
    spot = root.add("rect", x=sx + ax0 * cw, y=sy + ay0 * cw, width=cw - 1, height=cw - 1, fill=AMBER)
    cells_scatter = []
    t_s = 6.5
    for j in range(n):
        for i in range(n):
            d = math.hypot(i - ax0, j - ay0)
            if 0 < d <= rad + 0.3:
                r = root.add("rect", x=sx + i * cw, y=sy + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
                r.Steps("fill", [(t_s + d * 0.35, "#fed7aa")])
                cells_scatter.append(r)
    scene.TextStack(root, 30, 390, [(0.0, 6.0, "ギャザー:1 画素ごとに、決まった数を集める（コストが一定。重なりの扱いが難しい）"), (6.0, 20, "スキャッター:明るい点の分だけ、円盤を描く（コスト = 点の数 × 面積。ボケの形がきれい）")], size=13, fill=INK, weight=500)
    scene.TextStack(root, 30, 412, [(8.5, 20, "実用:明るい点だけスキャッター ＋ 残りはギャザー（ハイブリッド）")], size=13, fill=GREEN, weight=700)
    scene.Note(1.0, name, "集める → まく")
    return dict(name=name, page=PAGE + "dof/scatter.md", scene=scene, size=(780, 420), times=[2.5, 5.0, 8.0, 11.0])


def Shape(nsides, rot, rad, cx, cy, n=120):
    """正 nsides 角形(nsides=0 は円)の周を n 点で近似した points 文字列。"""
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        if nsides == 0:
            r = rad
        else:
            seg = 2 * math.pi / nsides
            local = (a - rot) % seg - seg / 2
            r = rad * math.cos(math.pi / nsides) / math.cos(local)
        pts.append("%s,%s" % (R(cx + r * math.cos(a)), R(cy + r * math.sin(a))))
    return " ".join(pts)


def BokehShapesAnim():
    name = "bokeh-shapes-anim"
    scene = NewScene(name, 780, 380, duration=12.0, hold=1.5, title="絞りの羽根の形が、そのままボケの形になる")
    root = scene.root
    f1 = Blur(scene, "bk-glow", 3)
    shapes = [("円形の絞り", 0, 0.0), ("6 枚羽根", 6, -math.pi / 2), ("5 枚羽根", 5, -math.pi / 2), ("8 枚羽根", 8, -math.pi / 8)]
    root.add("rect", x=40, y=80, width=250, height=250, fill="#0f172a", rx=8)
    root.add("rect", x=330, y=80, width=410, height=250, fill="#0b1224", rx=8)
    scene.Text(root, 165, 70, "レンズの絞り（上から）", size=13, fill=GRAY, anchor="middle")
    scene.Text(root, 535, 70, "背景の点光源のボケ", size=13, fill=GRAY, anchor="middle")
    ap = root.add("polygon", points=Shape(0, 0, 90, 165, 205), fill="#e2e8f0", stroke="#ffffff", stroke_width=3)
    lights = [(400, 150, 38, "#fde68a"), (520, 240, 56, "#bfdbfe"), (650, 150, 44, "#fbcfe8"), (610, 270, 30, "#bbf7d0"), (440, 270, 34, "#fecaca")]
    bokeh = []
    for (lx, ly, r, col) in lights:
        bokeh.append((root.add("polygon", points=Shape(0, 0, r, lx, ly), fill=col, fill_opacity=0.75, stroke=col, stroke_width=2), lx, ly, r))
    t = 1.0
    seg = 2.8
    for i, (label, ns, rot) in enumerate(shapes):
        ta = 0.8 + i * seg
        if i > 0:
            ap.Ramp(ta, ta + 0.8, "points", Shape(ns, rot, 90, 165, 205))
            for node, lx, ly, r in bokeh:
                node.Ramp(ta, ta + 0.8, "points", Shape(ns, rot, r, lx, ly))
        scene.TextStack(root, 40, 360, [(ta, ta + seg if i < 3 else 20, label + (":ボケも同じ形（丸）" if ns == 0 else ":ボケも " + str(ns) + " 角形"))], size=17, fill=INK)
    scene.Note(0.8, name, "絞りの形を切り替える")
    return dict(name=name, page=PAGE + "dof/bokeh-shape.md", scene=scene, size=(780, 380), times=[1.5, 4.2, 7.0, 10.0])


def ChromaticShift():
    name = "chromatic-aberration-shift"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="色収差:画面の端ほど、赤と青がずれる")
    root = scene.root
    ox, oy, w, h = 40, 60, 700, 280
    root.add("rect", x=ox, y=oy, width=w, height=h, fill="#000000", rx=6)
    cx, cy = ox + w / 2, oy + h / 2
    rings = [40, 80, 120, 160, 200]
    clip = scene.defs.add("clipPath", id="ca-clip")
    clip.add("rect", x=ox, y=oy, width=w, height=h, rx=6)

    def Layer(color, sign):
        g = root.add("g", style="mix-blend-mode:screen", clip_path="url(#ca-clip)")
        nodes = []
        for r in rings:
            nodes.append((g.add("ellipse", cx=cx, cy=cy, rx=r * 1.7, ry=r * 0.85, fill="none", stroke=color, stroke_width=3), r))
        vl = []
        for k in (-3, -2, -1, 0, 1, 2, 3):
            vl.append((g.add("line", x1=cx + k * 100, y1=oy + 14, x2=cx + k * 100, y2=oy + h - 14, stroke=color, stroke_width=2, opacity=0.8), k * 100))
        return nodes, vl

    r_nodes, r_lines = Layer("#ff0000", +1)
    g_nodes, g_lines = Layer("#00ff00", 0)
    b_nodes, b_lines = Layer("#0000ff", -1)
    strength = [(0.8, 0.0), (3.5, 0.045), (6.0, 0.045), (8.8, 0.0)]
    for nodes, lines, sgn in ((r_nodes, r_lines, +1), (b_nodes, b_lines, -1)):
        for idx, (t, s) in enumerate(strength):
            f = 1 + sgn * s
            pt = strength[idx - 1][0] if idx else None
            for node, r in nodes:
                for attr, val in (("rx", r * 1.7 * f), ("ry", r * 0.85 * f)):
                    if idx == 0:
                        node.Set(t, attr, R(val))
                    else:
                        node.Ramp(pt, t, attr, R(val))
            for node, off in lines:
                for attr in ("x1", "x2"):
                    if idx == 0:
                        node.Set(t, attr, R(cx + off * f))
                    else:
                        node.Ramp(pt, t, attr, R(cx + off * f))
    scene.TextStack(root, 40, 366, [(0.0, 3.5, "ずれなし（元の画像）"), (3.5, 6.0, "中心は動かず、端ほど大きくずれる（赤は外へ、青は内へ）"), (6.0, 8.8, "端の白い線が、赤と青に分かれて見える"), (8.8, 20, "元に戻る")], size=14, fill=INK, weight=500)
    scene.Note(3.5, name, "赤を拡大・青を縮小")
    return dict(name=name, page=PAGE + "lens-effects/index.md", scene=scene, size=(780, 380), times=[1.0, 3.5, 5.0, 7.5])


def ChromaticCompare():
    name = "chromatic-aberration-compare"
    scene = NewScene(name, 780, 360, duration=10.0, hold=1.5, title="intensity を上げると、端の縁が赤と青に割れる")
    root = scene.root
    ox, oy, w, h = 40, 70, 700, 190
    root.add("rect", x=ox, y=oy, width=w, height=h, fill="#000000", rx=6)
    cx = ox + w / 2
    xs = [ox + 60, cx, ox + w - 60]
    labels = ["左の端", "中心", "右の端"]
    layers = []
    for color, sgn in (("#ff0000", 1), ("#00ff00", 0), ("#0000ff", -1)):
        g = root.add("g", style="mix-blend-mode:screen")
        rects = []
        for x in xs:
            rects.append((g.add("rect", x=x - 9, y=oy + 30, width=18, height=h - 60, fill=color), x))
        layers.append((rects, sgn))
    scene.Text(root, xs[0], oy + h + 22, labels[0], size=13, fill=GRAY, anchor="middle")
    scene.Text(root, xs[1], oy + h + 22, labels[1], size=13, fill=GRAY, anchor="middle")
    scene.Text(root, xs[2], oy + h + 22, labels[2], size=13, fill=GRAY, anchor="middle")
    seq = [(0.8, 0.0), (2.0, 0.0), (3.0, 0.02), (4.2, 0.02), (5.2, 0.0), (6.0, 0.0), (7.2, 0.06), (8.6, 0.06), (9.4, 0.0)]
    for rects, sgn in layers:
        for idx, (t, s) in enumerate(seq):
            for node, x in rects:
                off = (x - cx) * s * sgn * 1.0
                if idx == 0:
                    node.Set(t, "x", R(x - 9 + off))
                else:
                    node.Ramp(seq[idx - 1][0], t, "x", R(x - 9 + off))
    scene.TextStack(root, 40, 320, [(0.0, 2.5, "強さ 0:ずれなし"), (2.5, 4.7, "強さ 0.02（ちょうどよい）:端の縁にわずかな色ずれ"), (4.7, 6.6, "強さ 0:ずれなし"), (6.6, 9.0, "強さ 0.06（やりすぎ）:端で赤と青がはっきり分かれる"), (9.0, 20, "強さ 0:ずれなし")], size=15, fill=INK)
    scene.TextStack(root, 40, 346, [(0.0, 20, "ずれの量 ＝ 中心からの距離 × 強さ（中心は、いつもずれない）")], size=13, fill=GRAY, weight=500)
    scene.Note(3.0, name, "弱 → 強")
    return dict(name=name, page=PAGE + "lens-effects/chromatic-aberration.md", scene=scene, size=(780, 360), times=[1.0, 4.0, 6.0, 8.5])


def FilmGrainLuma():
    name = "film-grain-luma"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="フィルム グレイン:中間の明るさで最も強く、暗部と明部では弱い")
    root = scene.root
    ax = Axes(scene, root, 60, 70, 360, 150, 1.0, 1.0, "画素の明るさ", "粒の強さ")
    curve = lambda x: 4 * x * (1 - x)
    ax.Curve(curve, BLUE, 4, n=40)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    Sweep(dot, ax, curve, 0.8, 9.0, 0.0, 1.0, 30)
    cols, rows, cw, ch = 48, 4, 13, 20
    rnd = random.Random(7)
    ox, oy = 60, 270
    scene.Text(root, ox, oy - 12, "グラデーションに、粒を重ねる（毎フレーム、粒が入れ替わる）", size=13, fill=GRAY, weight=500)
    frames = 10
    for j in range(rows):
        for i in range(cols):
            x = i / (cols - 1)
            amp = 0.35 * curve(x)
            steps = []
            for k in range(frames):
                n = rnd.uniform(-1, 1) * amp
                steps.append((0.8 + k * 0.9, Gray(max(0.0, min(1.0, x + n)))))
            r = root.add("rect", x=ox + i * cw, y=oy + j * ch, width=cw, height=ch, fill=Gray(x))
            r.Steps("fill", steps)
    scene.Text(root, ox, oy + rows * ch + 20, "暗部（左）", size=12, fill=GRAY, weight=500)
    scene.Text(root, ox + cols * cw / 2, oy + rows * ch + 20, "中間（粒が最も強い）", size=12, fill=BLUE, weight=700, anchor="middle")
    scene.Text(root, ox + cols * cw, oy + rows * ch + 20, "明部（右）", size=12, fill=GRAY, weight=500, anchor="end")
    LiveText(scene, root, 450, 110, 0.8, 9.0, 18, lambda i, f: "明るさ %.2f → 強さ %.2f" % (f, curve(f)), size=17, fill=INK)
    scene.TextStack(root, 450, 150, [(0.0, 20, "本物のフィルムは、暗部・明部で粒が目立ちにくい")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "明るさ 0 → 1")
    return dict(name=name, page=PAGE + "lens-effects/film-grain.md", scene=scene, size=(780, 400), times=[1.0, 3.0, 5.0, 8.0])


def LensFlareGhosts():
    name = "lens-flare-ghosts"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="画面空間のゴースト:光源の像が、画面の中心を通る線上に並ぶ")
    root = scene.root
    ox, oy, w, h = 40, 60, 700, 300
    root.add("rect", x=ox, y=oy, width=w, height=h, fill="#0b1224", rx=6)
    fclip = scene.defs.add("clipPath", id="lf-clip")
    fclip.add("rect", x=ox, y=oy, width=w, height=h, rx=6)
    cx, cy = ox + w / 2, oy + h / 2
    root.add("circle", cx=cx, cy=cy, r=4, fill="#64748b")
    scene.Text(root, cx + 8, cy - 8, "画面の中心", size=11, fill=GRAY, weight=500)
    f1 = Blur(scene, "lf-glow", 5)
    ghosts = [(-0.6, 24, "#7dd3fc"), (0.35, 40, "#fbbf24"), (0.7, 18, "#a78bfa"), (1.4, 32, "#86efac"), (2.0, 14, "#f472b6")]
    path = [(0.8, (ox + 90, oy + 60)), (3.5, (ox + 300, oy + 120)), (6.5, (ox + 560, oy + 90)), (10.0, (ox + 620, oy + 230))]
    line = root.add("line", x1=path[0][1][0], y1=path[0][1][1], x2=cx - (path[0][1][0] - cx), y2=cy - (path[0][1][1] - cy), stroke="#334155", stroke_width=1.5, stroke_dasharray="4 4")
    light = root.add("circle", cx=path[0][1][0], cy=path[0][1][1], r=14, fill="#fff7d6", filter=f1)
    light2 = root.add("circle", cx=path[0][1][0], cy=path[0][1][1], r=6, fill="#ffffff")
    gs = []
    for (k, r, col) in ghosts:
        gs.append((root.add("circle", cx=cx, cy=cy, r=r, fill="none", stroke=col, stroke_width=4, opacity=0.8, clip_path="url(#lf-clip)"), k))
        gs[-1][0].attrs["cx"] = R(cx + (path[0][1][0] - cx) * -k)
        gs[-1][0].attrs["cy"] = R(cy + (path[0][1][1] - cy) * -k)
    for idx, (t, (lx, ly)) in enumerate(path):
        dx, dy = lx - cx, ly - cy
        if idx == 0:
            continue
        pt = path[idx - 1][0]
        light.Ramp(pt, t, "cx", lx); light.Ramp(pt, t, "cy", ly)
        light2.Ramp(pt, t, "cx", lx); light2.Ramp(pt, t, "cy", ly)
        line.Ramp(pt, t, "x1", lx); line.Ramp(pt, t, "y1", ly)
        line.Ramp(pt, t, "x2", R(cx - dx)); line.Ramp(pt, t, "y2", R(cy - dy))
        for node, k in gs:
            node.Ramp(pt, t, "cx", R(cx - dx * k)); node.Ramp(pt, t, "cy", R(cy - dy * k))
    scene.TextStack(root, 40, 384, [(0.0, 20, "ゴースト位置 ＝ 中心 − (光源 − 中心) × 係数。係数がマイナスなら光源側、プラスなら反対側にできる。")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "光源が動くと、ゴーストが追従")
    return dict(name=name, page=PAGE + "lens-effects/lens-flare.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.0, 9.5])


def VignetteParams():
    name = "vignette-params"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="ビネット:半径とやわらかさで、四隅の暗さが変わる")
    root = scene.root
    ox, oy, w, h = 60, 70, 420, 260
    root.add("rect", x=ox, y=oy, width=w, height=h, fill="#fde68a")
    root.add("rect", x=ox, y=oy + 150, width=w, height=110, fill="#86efac")
    root.add("rect", x=ox + 40, y=oy + 80, width=90, height=120, fill="#fca5a5")
    root.add("rect", x=ox + 250, y=oy + 60, width=110, height=140, fill="#93c5fd")
    root.add("circle", cx=ox + 340, cy=oy + 45, r=26, fill="#ffffff")
    def Grad(ident, r, inner, outer=1.0, alpha=0.85):
        gd = scene.defs.add("radialGradient", id=ident, cx=0.5, cy=0.5, r=r, gradientUnits="objectBoundingBox")
        gd.add("stop", offset=inner, stop_color="#000000", stop_opacity=0)
        gd.add("stop", offset=outer, stop_color="#000000", stop_opacity=alpha)
    Grad("vg-std", 0.55, 0.45)
    Grad("vg-small", 0.38, 0.40)
    Grad("vg-large", 0.85, 0.50)
    Grad("vg-soft", 0.60, 0.02)
    Grad("vg-hard", 0.55, 0.78, 0.82)
    states = [("vg-std", 0.0, 0.8), ("vg-small", 0.8, 3.8), ("vg-large", 3.8, 6.8), ("vg-std", 6.8, 8.0), ("vg-soft", 8.0, 10.5), ("vg-hard", 10.5, 12.5), ("vg-std", 12.5, 20.0)]
    for ident, ta, tb in states:
        ov = root.add("rect", x=ox, y=oy, width=w, height=h, fill="url(#%s)" % ident, opacity=1 if ta == 0.0 else 0)
        if ta == 0.0:
            ov.Set(tb, "opacity", 1)
            ov.Ramp(tb, tb + 0.4, "opacity", 0)
        else:
            ov.Ramp(ta - 0.4 if ta > 0.4 else 0, ta, "opacity", 1)
            if tb < 20:
                ov.Set(tb, "opacity", 1)
                ov.Ramp(tb, tb + 0.4, "opacity", 0)
    root.add("rect", x=ox, y=oy, width=w, height=h, fill="none", stroke="#94a3b8", stroke_width=1.5)
    scene.TextStack(root, 510, 120, [(0.0, 0.8, "標準の設定"), (0.8, 3.8, "半径を小さく"), (3.8, 6.8, "半径を大きく"), (6.8, 8.0, "標準に戻す"), (8.0, 10.5, "やわらかく（なだらか）"), (10.5, 12.5, "硬く（境目がくっきり）"), (12.5, 20, "標準に戻す")], size=17, fill=INK)
    scene.TextStack(root, 510, 150, [(0.8, 3.8, "暗くなる範囲が中心へ広がる"), (3.8, 6.8, "四隅だけが、わずかに暗い"), (8.0, 10.5, "暗さが、なめらかに増える"), (10.5, 12.5, "円の縁が見えてしまう（不自然）")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 510, 230, "radius ＝ 暗くなり始める距離", size=13, fill=GRAY, weight=500)
    scene.Text(root, 510, 254, "smoothness ＝ 暗さの変化のなだらかさ", size=13, fill=GRAY, weight=500)
    scene.Text(root, 510, 278, "強すぎると、画面の中心まで暗くなる", size=13, fill=RED, weight=500)
    scene.Note(0.8, name, "半径 → やわらかさ")
    return dict(name=name, page=PAGE + "lens-effects/vignette.md", scene=scene, size=(780, 400), times=[0.8, 3.5, 6.0, 11.0])


FIGS = [DofFocusSweep, CocGraph, DofGatherWeight, DofNearField, DofScatterGather, BokehShapesAnim, ChromaticShift, ChromaticCompare, FilmGrainLuma, LensFlareGhosts, VignetteParams]
