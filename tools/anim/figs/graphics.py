import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Caption, Hex, Lerp, Mix, NewScene, R, Smooth)  # noqa: E402
from figs.pipeline import Timeline  # noqa: E402


def Waves():
    name = "water-gerstner"
    period, frames = 6.0, 36
    scene = NewScene(name, 780, 390, duration=period, hold=0.0, title="水面の波:サイン波と Gerstner 波の動き（粒子の軌道も見る）")
    root = scene.root
    clip = scene.defs.add("clipPath", id="wv-clip")
    clip.add("rect", x=50, y=0, width=680, height=390)
    k = 2 * math.pi / 165.0
    amp = 22.0
    qa = 0.8 / k
    rows = [("サイン波:波頂が丸い。粒子は上下だけ動く", 120, False), ("Gerstner 波:波頂が尖り、谷が広い。粒子は円運動", 290, True)]
    for label, base, gers in rows:
        scene.Text(root, 50, base - 52, label, size=15, fill=INK)
        root.add("line", x1=50, y1=base, x2=730, y2=base, stroke=LIGHT, stroke_width=1.5)
        g = root.add("g", clip_path="url(#wv-clip)")
        fill_path = g.add("path", d="M50,%d" % base, fill="#bfdbfe", fill_opacity=0.55, stroke=BLUE, stroke_width=3)
        px0 = 390
        orbit = g.add("circle", cx=px0, cy=base, r=amp, fill="none", stroke=GRAY, stroke_width=1, stroke_dasharray="3 3", opacity=1 if gers else 0)
        if not gers:
            g.add("line", x1=px0, y1=base - amp, x2=px0, y2=base + amp, stroke=GRAY, stroke_width=1, stroke_dasharray="3 3")
        dot = g.add("circle", cx=px0, cy=base, r=6, fill=RED, stroke="#ffffff", stroke_width=1.5)
        for f in range(frames + 1):
            phase = -2 * math.pi * f / frames
            pts = []
            for i in range(0, 146):
                x0 = -20 + i * 5.5
                th = k * x0 + phase
                if gers:
                    X, Y = x0 + qa * math.cos(th), amp * math.sin(th)
                else:
                    X, Y = x0, amp * math.sin(th)
                pts.append((X, base - Y))
            d = "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts) + " L800,%d L-20,%d Z" % (base + 50, base + 50)
            t = period * f / frames
            if f == 0:
                fill_path.attrs["d"] = d
            else:
                fill_path.Ramp(tp, t, "d", d)
            th = k * px0 + phase
            if gers:
                X, Y = px0 + qa * math.cos(th), amp * math.sin(th)
            else:
                X, Y = px0, amp * math.sin(th)
            if f == 0:
                dot.attrs["cx"], dot.attrs["cy"] = R(X), R(base - Y)
                dot.tracks.clear()
            else:
                dot.Ramp(tp, t, "cx", R(X))
                dot.Ramp(tp, t, "cy", R(base - Y))
            tp = t
    scene.Note(0.0, name, "波が右へ進む(周期 %.0f 秒でループ)" % period)
    return dict(name=name, page="graphics/water/waves/gerstner.md", before="## Gerstner 波", scene=scene, size=(780, 390), times=[0.0, 1.5, 3.0, 4.5])


def ShadowMap():
    name = "shadow-map-probe"
    scene = NewScene(name, 780, 420, duration=12.5, hold=1.5, title="シャドウ マップ:光から見た最短の深度と比べて、影かどうかを決める")
    root = scene.root
    L = (110, 112)
    ground_y = 320
    box = (330, 210, 400, 262)
    root.add("line", x1=40, y1=ground_y, x2=740, y2=ground_y, stroke=INK, stroke_width=3)
    root.add("rect", x=box[0], y=box[1], width=box[2] - box[0], height=box[3] - box[1], fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("circle", cx=L[0], cy=L[1], r=14, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, L[0] + 22, L[1] + 5, "光", size=15, fill=INK)

    def Hit(gx):
        dx, dy = gx - L[0], ground_y - L[1]
        best = None
        for (x1, y1, x2, y2) in ((box[0], box[1], box[2], box[1]), (box[0], box[1], box[0], box[3]), (box[2], box[1], box[2], box[3]), (box[0], box[3], box[2], box[3])):
            ex, ey = x2 - x1, y2 - y1
            den = dx * ey - dy * ex
            if abs(den) < 1e-9:
                continue
            t = ((x1 - L[0]) * ey - (y1 - L[1]) * ex) / den
            u = ((x1 - L[0]) * dy - (y1 - L[1]) * dx) / den
            if 0 < t < 1 and 0 <= u <= 1 and (best is None or t < best):
                best = t
        return best if best is not None else 1.0

    xs = list(range(150, 731, 15))
    n = len(xs)
    t1_start, t1_step = 0.8, 0.07
    for i, gx in enumerate(xs):
        t = t1_start + i * t1_step
        h = Hit(gx)
        hx, hy = L[0] + (gx - L[0]) * h, L[1] + (ground_y - L[1]) * h
        ray = root.add("line", x1=L[0], y1=L[1], x2=R(hx), y2=R(hy), stroke=AMBER, stroke_width=1.5, opacity=0)
        ray.Show(t, 4.0)
        dot = root.add("circle", cx=R(hx), cy=R(hy), r=3.5, fill=RED if h < 1 else GREEN, opacity=0)
        dot.Show(t, 4.0)
    scene.Note(t1_start, name, "① 光から見た深度:各方向で最初に当たった点を記録")
    t2_start, t2_step = 4.4, 0.17
    probe = root.add("circle", cx=xs[0], cy=ground_y, r=8, fill="#ffffff", stroke=INK, stroke_width=3, opacity=0)
    probe.Show(t2_start, 12.5)
    probe_ray = root.add("line", x1=L[0], y1=L[1], x2=xs[0], y2=ground_y, stroke=AMBER, stroke_width=3, opacity=0)
    probe_ray.Show(t2_start, 12.5)
    probe.Steps("cx", [(t2_start + i * t2_step, gx) for i, gx in enumerate(xs)])
    probe_ray.Steps("x2", [(t2_start + i * t2_step, gx) for i, gx in enumerate(xs)])
    colors = []
    texts = []
    for i, gx in enumerate(xs):
        t = t2_start + i * t2_step
        h = Hit(gx)
        shadow = h < 1
        seg = root.add("rect", x=gx - 7.5, y=ground_y - 4, width=15, height=8, fill="#334155" if shadow else "#fde68a", opacity=0)
        seg.Show(t)
        colors.append((t, RED if shadow else AMBER))
        total = math.hypot(gx - L[0], ground_y - L[1]) / 10.0
        stored = total * h
        texts.append((t, "この点までの距離 d = %.1f　シャドウ マップの値 m = %.1f　→ %s" % (total, stored, "d > m なので影" if shadow else "d = m なので光が当たる")))
    probe_ray.Steps("stroke", colors)
    Timeline(scene, root, 40, 372, texts, 12.5, size=15, fill=INK)
    Caption(scene, 40, 52, [(0.0, 4.4, "① 光から見て、各方向で一番近い物までの距離を記録する（シャドウ マップ）"),
                            (4.4, 12.5, "② 画面の点を光から見た距離と、記録された距離で比べる")], size=14, fill=GRAY, weight=500)
    scene.Text(root, 40, 402, "記録より遠ければ（間に何かある）影、同じなら光が当たる。", size=13, weight=500, fill=GRAY)
    return dict(name=name, page="graphics/shadows/shadow-map-basics/index.md", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 12.0])


def Sorting():
    name = "alpha-sort-order"
    scene = NewScene(name, 780, 390, duration=10.0, hold=1.5, title="半透明は奥から手前の順に描く。順番を間違えると、透けなくなる")
    root = scene.root
    objs = [("奥（赤）", "#e5484d", 0, 0), ("中（緑）", "#2ea043", 46, 34), ("手前（青）", "#2563eb", 92, 68)]
    size = 130
    panels = [(40, "正しい順:奥 → 中 → 手前", [0, 1, 2], False), (420, "間違った順:手前 → 中 → 奥（深度を書く）", [2, 1, 0], True)]
    for pi, (px, title, order, wrong) in enumerate(panels):
        scene.Text(root, px, 66, title, size=15, fill=INK)
        root.add("rect", x=px, y=84, width=300, height=220, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        root.add("circle", cx=px + 250, cy=116, r=20, fill="none", stroke="#cbd5e1", stroke_width=2)
        for step, idx in enumerate(order):
            t = 1.0 + step * 2.2
            label, color, ox, oy = objs[idx]
            x0, y0 = px + 20 + ox, 100 + oy
            shape = root.add("g", opacity=0)
            if wrong and step > 0:
                mask_id = "as-mask-%d-%d" % (pi, step)
                mask = scene.defs.add("mask", id=mask_id, maskUnits="userSpaceOnUse", x=px, y=84, width=300, height=220)
                mask.add("rect", x=px, y=84, width=300, height=220, fill="#ffffff")
                for prev in order[:step]:
                    _, _, qx, qy = objs[prev]
                    mask.add("rect", x=px + 20 + qx, y=100 + qy, width=size, height=size, fill="#000000")
                inner = shape.add("g", mask="url(#%s)" % mask_id)
                inner.add("rect", x=x0, y=y0, width=size, height=size, fill=color, fill_opacity=0.55, stroke=color, stroke_width=1.5)
            else:
                shape.add("rect", x=x0, y=y0, width=size, height=size, fill=color, fill_opacity=0.55, stroke=color, stroke_width=1.5)
            shape.Show(t)
            scene.Note(t, name, "%s:%d 番目に %s" % (title.split(":")[0], step + 1, label))
        Caption(scene, px, 326, [(1.0, 3.2, "1 番目:%s を描く" % objs[order[0]][0]), (3.2, 5.4, "2 番目:%s を描く" % objs[order[1]][0]),
                                 (5.4, 20, "3 番目:%s を描く" % objs[order[2]][0])], size=14, fill=INK)
    Caption(scene, 40, 356, [(0.0, 7.7, ""), (7.7, 20, "左:重なりに赤・緑・青が全部透けて見える。")], size=14, fill=GREEN)
    Caption(scene, 420, 356, [(0.0, 7.7, ""), (7.7, 20, "右:手前が先に深度を書くので、奥の物が消えて透けない。")], size=14, fill=RED)
    return dict(name=name, page="graphics/translucency/blending-sorting/sorting.md", before="## ブレンド順序の決め方（まとめ）", scene=scene, size=(780, 390), times=[1.5, 4.0, 6.5, 9.5])


def Scattering():
    name = "sunset-path"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="夕焼け:太陽が低いほど、光が大気を長く通って青が散り尽くす")
    root = scene.root
    ground_y, top_y = 320, 150
    obs = (390, ground_y)
    sky = root.add("rect", x=40, y=top_y, width=700, height=ground_y - top_y, fill="#6fb3ff")
    root.add("rect", x=40, y=ground_y, width=700, height=40, fill="#3f5d3a")
    scene.Text(root, 46, top_y - 8, "大気の層（上端）", size=12, fill=GRAY)
    root.add("line", x1=40, y1=top_y, x2=740, y2=top_y, stroke="#94a3b8", stroke_width=1.5, stroke_dasharray="5 4")
    root.add("circle", cx=obs[0], cy=obs[1], r=7, fill=RED)
    scene.Text(root, obs[0] + 12, obs[1] + 22, "観測者", size=13, fill="#ffffff")
    sun = root.add("circle", cx=500, cy=100, r=22, fill="#fff3b0", stroke="#f59e0b", stroke_width=2)
    path = root.add("line", x1=500, y1=top_y, x2=obs[0], y2=obs[1], stroke="#ffffff", stroke_width=5)
    alt = math.radians
    t0, t1, steps = 1.0, 8.5, 30
    day, dusk = "#6fb3ff", "#ff8a4c"
    scene.Text(root, 540, 80, "光が大気を通る距離", size=12, fill=GRAY)
    root.add("rect", x=540, y=90, width=190, height=14, fill="#f1f5f9", stroke="#94a3b8")
    bar = root.add("rect", x=540, y=90, width=17, height=14, fill="#ff6b3d")
    lines = []
    for i in range(steps + 1):
        f = i / steps
        deg = Lerp(80.0, 5.0, f)
        a = alt(deg)
        sx = obs[0] + 330 * math.cos(a)
        sy = obs[1] - 330 * math.sin(a)
        ex = obs[0] + (ground_y - top_y) / math.tan(a)
        col_path = Mix("#ffffff", "#ff4d2e", Smooth(f))
        bw = 17 * (1.0 / math.sin(a)) / (1.0 / math.sin(alt(80)))
        col_sky = Mix(day, dusk, Smooth(f))
        t = Lerp(t0, t1, f)
        if i == 0:
            sun.Set(t, "cx", R(sx)); sun.Set(t, "cy", R(sy))
            path.Set(t, "x1", R(min(ex, 735)))
            path.Set(t, "stroke", col_path)
            sky.Set(t, "fill", col_sky)
            bar.Set(t, "width", R(min(190, bw)))
        else:
            sun.Ramp(tp, t, "cx", R(sx)); sun.Ramp(tp, t, "cy", R(sy))
            path.Ramp(tp, t, "x1", R(min(ex, 735)))
            path.Ramp(tp, t, "stroke", col_path)
            sky.Ramp(tp, t, "fill", col_sky)
            bar.Ramp(tp, t, "width", R(min(190, bw)))
        tp = t
    for deg in (80, 60, 40, 20, 10, 5):
        f = (80 - deg) / 75.0
        length = 1.0 / math.sin(alt(deg))
        lines.append((Lerp(t0, t1, f), "太陽の高さ %d°:大気を通る距離 = %.1f 倍" % (deg, length / (1.0 / math.sin(alt(80))))))
    Timeline(scene, root, 40, 392 - 0, lines, 20, size=15, fill=INK)
    Caption(scene, 40, 52, [(0.0, 5.0, "昼:光は大気を短く通る → 青い光が散って空は青い"), (5.0, 20, "夕方:長く通る間に青が散り尽くし、赤だけが残って届く")], size=14, fill=GRAY, weight=500)
    scene.Note(t0, name, "太陽が高さ 80° から 5° まで下がる")
    return dict(name=name, page="graphics/atmosphere/scattering/index.md", scene=scene, size=(780, 400), times=[0.5, 3.5, 6.5, 9.5])


def Clouds():
    name = "cloud-raymarch"
    scene = NewScene(name, 780, 380, duration=10.5, hold=1.5, title="雲のレイマーチ:視線を少しずつ進んで、密度から光を積み上げる")
    root = scene.root
    blobs = [(430, 170, 70, 38, 1.0), (500, 150, 60, 34, 0.9), (360, 190, 50, 28, 0.7), (460, 200, 65, 30, 0.8)]
    for cx, cy, rx, ry, d in blobs:
        root.add("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, fill="#cbd5e1", opacity=0.8)
    root.add("rect", x=40, y=60, width=520, height=260, fill="none", stroke="#94a3b8", stroke_width=1.5)
    start = (70, 300)
    end = (550, 90)
    root.add("circle", cx=start[0], cy=start[1], r=8, fill=RED)
    scene.Text(root, start[0] + 14, start[1] - 8, "カメラ", size=13, fill=GRAY)
    scene.Text(root, 52, 78, "雲（上から見た断面）", size=12, fill=GRAY)
    root.add("line", x1=start[0], y1=start[1], x2=end[0], y2=end[1], stroke="#94a3b8", stroke_width=1.5, stroke_dasharray="4 4")
    steps = 32
    dxy = ((end[0] - start[0]) / steps, (end[1] - start[1]) / steps)

    def Density(x, y):
        s = 0.0
        for cx, cy, rx, ry, d in blobs:
            q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            s += d * math.exp(-1.5 * q)
        return min(1.0, s)

    t0, step = 0.8, 0.26
    transmittance, light = 1.0, 0.0
    series_t, series_l = [], []
    for i in range(steps):
        if transmittance < 0.05:
            break
        x, y = start[0] + dxy[0] * (i + 0.5), start[1] + dxy[1] * (i + 0.5)
        d = Density(x, y)
        t = t0 + i * step
        dot = root.add("circle", cx=R(x), cy=R(y), r=3 + 6 * d, fill=Mix("#ffffff", "#475569", d), stroke="#475569", stroke_width=1, opacity=0)
        dot.Show(t)
        step_t = math.exp(-d * 0.55)
        light += transmittance * (1 - step_t) * 1.0
        transmittance *= step_t
        series_t.append((t, transmittance))
        series_l.append((t, light))
    bx = 610
    scene.Text(root, bx, 82, "光が通り抜ける割合（透過率）", size=12, fill=GRAY)
    root.add("rect", x=bx, y=96, width=140, height=22, fill="#f1f5f9", stroke="#94a3b8")
    bar_t = root.add("rect", x=bx, y=96, width=140, height=22, fill=BLUE)
    scene.Text(root, bx, 168, "積み上がった光（雲の明るさ）", size=12, fill=GRAY)
    root.add("rect", x=bx, y=182, width=140, height=22, fill="#f1f5f9", stroke="#94a3b8")
    bar_l = root.add("rect", x=bx, y=182, width=140, height=22, fill=AMBER)
    bar_l.attrs["width"] = 0
    prev_t = 0.0
    for (t, v) in series_t:
        bar_t.Ramp(max(prev_t, 0.0), t, "width", R(140 * v)) if t > prev_t else None
        prev_t = t
    prev_t = 0.0
    for (t, v) in series_l:
        bar_l.Ramp(prev_t, t, "width", R(140 * min(1.0, v / 1.6))) if t > prev_t else None
        prev_t = t
    Timeline(scene, root, bx, 250, [(t, "透過率 T = %.2f" % v) for t, v in series_t], 20, size=15, fill=BLUE)
    Timeline(scene, root, bx, 278, [(t, "ステップ %d（最大 %d）" % (i + 1, steps)) for i, (t, _) in enumerate(series_t)], 20, size=13, fill=GRAY, weight=500)
    final_t = series_t[-1][0] + step
    Caption(scene, 40, 352, [(0.0, 2.0, "視線を一定のステップで進む"), (2.0, final_t, "雲の中では密度が高く、透過率が急に下がり、光が積み上がる"),
                             (final_t, 20, "透過率が 0 に近づいたので、ここで打ち切る → このピクセルの色が決まる")], size=15, fill=INK)
    scene.Note(t0, name, "%d ステップで視線を進む" % steps)
    return dict(name=name, page="graphics/atmosphere/clouds/raymarch.md", scene=scene, size=(780, 380), times=[1.5, 4.5, 7.5, 10.0])


def Lod():
    name = "terrain-quadtree"
    scene = NewScene(name, 780, 440, duration=10.0, hold=1.5, title="四分木 LOD:カメラに近いほど、タイルを 4 つに分けて細かくする")
    root = scene.root
    mx, my, ms = 30, 52, 336
    root.add("rect", x=mx, y=my, width=ms, height=ms, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    maxlevel = 3
    keyframes = 10
    path = [(60, 300), (150, 270), (230, 200), (280, 120), (260, 70), (200, 100), (140, 180), (110, 250), (100, 300), (60, 300)]
    cam_pts = [(mx + x, my + y) for x, y in path]
    nodes = []
    for level in range(maxlevel + 1):
        cells = 2 ** level
        size = ms / cells
        for gy in range(cells):
            for gx in range(cells):
                nodes.append((level, gx, gy, mx + gx * size, my + gy * size, size))

    def Leaves(cam):
        selected = set()

        def Visit(level, gx, gy):
            size = ms / (2 ** level)
            cx, cy = mx + (gx + 0.5) * size, my + (gy + 0.5) * size
            dist = math.hypot(cam[0] - cx, cam[1] - cy)
            if level < maxlevel and dist < size * 0.95:
                for dy in (0, 1):
                    for dx in (0, 1):
                        Visit(level + 1, gx * 2 + dx, gy * 2 + dy)
            else:
                selected.add((level, gx, gy))

        Visit(0, 0, 0)
        return selected

    t0, t1 = 0.8, 9.0
    times = [Lerp(t0, t1, i / (keyframes - 1)) for i in range(keyframes)]
    level_color = ["#bfdbfe", "#bbf7d0", "#fde68a", "#fecaca"]
    leaf_sets = [Leaves(c) for c in cam_pts]
    for (level, gx, gy, x, y, size) in nodes:
        rect = root.add("rect", x=R(x + 1), y=R(y + 1), width=R(size - 2), height=R(size - 2), fill=level_color[level], stroke="#64748b", stroke_width=1, opacity=0)
        items = [(times[i], "1" if (level, gx, gy) in leaf_sets[i] else "0") for i in range(keyframes)]
        rect.Steps("opacity", items)
    cam = root.add("circle", cx=cam_pts[0][0], cy=cam_pts[0][1], r=9, fill=RED, stroke="#ffffff", stroke_width=2)
    for i in range(1, keyframes):
        cam.Ramp(times[i - 1], times[i], "cx", R(cam_pts[i][0]))
        cam.Ramp(times[i - 1], times[i], "cy", R(cam_pts[i][1]))
    scene.Text(root, mx, my + ms + 30, "カメラ（赤）が動くと、近いタイルが分割され、遠いタイルは粗いまま", size=14, fill=INK)
    px = 410
    scene.Text(root, px, 90, "いま描くタイルの数", size=14, fill=GRAY)
    Timeline(scene, root, px, 130, [(times[i], "%d 枚" % len(leaf_sets[i])) for i in range(keyframes)], 20, size=34, fill=INK)
    for lv in range(4):
        root.add("rect", x=px, y=170 + lv * 30, width=22, height=18, fill=level_color[lv], stroke="#64748b")
        scene.Text(root, px + 32, 184 + lv * 30, "レベル %d（%s）" % (lv, ["いちばん粗い", "粗い", "細かい", "いちばん細かい"][lv]), size=14, fill=INK)
    scene.Text(root, px, 320, "全部を最高の細かさで描くと 64 枚。", size=14, fill=GRAY, weight=500)
    scene.Text(root, px, 344, "カメラの近くだけ細かくして、数を抑える。", size=14, fill=GRAY, weight=500)
    scene.Note(t0, name, "カメラが地形の上を 1 周する。タイル数の最小 %d / 最大 %d" % (min(len(s) for s in leaf_sets), max(len(s) for s in leaf_sets)))
    return dict(name=name, page="graphics/terrain/lod/cdlod.md", scene=scene, size=(780, 440), times=[1.0, 3.0, 5.0, 8.0])


def Ssao():
    name = "ssao-samples"
    scene = NewScene(name, 780, 380, duration=10.0, hold=1.5, title="SSAO:点の周りの半球にサンプルを撒いて、物の中に入った割合で暗くする")
    root = scene.root
    floor_y, wall_x, wall_top = 270, 470, 150
    root.add("polygon", points="40,%d 470,%d 470,%d 740,%d 740,340 40,340" % (floor_y, floor_y, wall_top, wall_top), fill="#cbd5e1", stroke=INK, stroke_width=3)
    rng = random.Random(3)
    samples = []
    while len(samples) < 16:
        a, r = rng.uniform(0, math.pi), 85 * math.sqrt(rng.uniform(0.15, 1.0))
        samples.append((math.cos(a) * r, -math.sin(a) * r))

    def Solid(x, y):
        return y > floor_y or (x > wall_x and y > wall_top)

    points = [("A", 452), ("B", 170)]
    results = {}
    for label, px in points:
        root.add("path", d="M%d,%d A85,85 0 0 1 %d,%d" % (px - 85, floor_y, px + 85, floor_y), fill="#bfdbfe", fill_opacity=0.35, stroke=BLUE, stroke_width=1.5, stroke_dasharray="4 3")
        root.add("circle", cx=px, cy=floor_y, r=6, fill=INK)
        scene.Text(root, px - 4, floor_y + 26, label, size=15, fill=INK)
        blocked = 0
        series = []
        for i, (sx, sy) in enumerate(samples):
            t = 1.0 + i * 0.4 + (0.2 if label == "B" else 0.0)
            hit = Solid(px + sx, floor_y + sy)
            blocked += 1 if hit else 0
            dot = root.add("circle", cx=R(px + sx), cy=R(floor_y + sy), r=6, fill=RED if hit else GREEN, stroke="#ffffff", stroke_width=1.5, opacity=0)
            dot.Show(t)
            series.append((t, blocked, i + 1))
        results[label] = (blocked, series)
    for label, px in points:
        blocked, series = results[label]
        scene.Text(root, px - 90, 62, "点 %s" % label, size=15, fill=INK)
        Timeline(scene, root, px - 90, 86, [(t, "物の中:%d / %d" % (b, n)) for t, b, n in series], 20, size=15, fill=RED)
        final_t = series[-1][0] + 0.5
        ao = 1.0 - blocked / len(samples)
        bar = root.add("rect", x=px - 90, y=104, width=0, height=16, fill=Hex([255 * ao] * 3), stroke=INK, stroke_width=1.5, opacity=0)
        bar.Set(final_t, "opacity", 1)
        bar.Ramp(final_t, final_t + 0.6, "width", R(140))
        scene.Text(root, px - 90, 142, "", size=1)
        f = scene.Text(root, px - 90, 144, "明るさ %.2f（%s）" % (ao, "暗くなる" if ao < 0.8 else "ほぼそのまま明るい"), size=15, fill=INK, opacity=0)
        f.Show(final_t + 0.4)
        scene.Note(final_t, name, "点 %s:%d / %d が物の中 → 明るさ %.2f" % (label, blocked, len(samples), ao))
    Caption(scene, 40, 360, [(0.0, 20, "赤 = 物の中に入ったサンプル、緑 = 空いている。壁の近く（A）ほど赤が多く、暗くなる。")], size=14, fill=GRAY, weight=500)
    return dict(name=name, page="graphics/ao/ssao-hemisphere.md", before="## 判定", scene=scene, size=(780, 380), times=[2.5, 4.5, 7.0, 10.0])


def Ssr():
    name = "ssr-march"
    scene = NewScene(name, 780, 360, duration=9.5, hold=1.5, title="SSR:反射した向きへ少しずつ進み、深度バッファの物にぶつかるまで探す")
    root = scene.root
    floor_y = 270
    root.add("line", x1=40, y1=floor_y, x2=740, y2=floor_y, stroke=INK, stroke_width=4)
    root.add("rect", x=40, y=floor_y, width=700, height=50, fill="#dbeafe", opacity=0.6)
    scene.Text(root, 46, floor_y + 30, "鏡のような床", size=13, fill=GRAY)
    cam = (70, 170)
    F = (300, floor_y)
    box = (500, 150, 580, floor_y)
    root.add("rect", x=box[0], y=box[1], width=box[2] - box[0], height=box[3] - box[1], fill=RED, stroke="#7f1d1d", stroke_width=2)
    root.add("circle", cx=cam[0], cy=cam[1], r=9, fill=INK)
    scene.Text(root, cam[0] - 10, cam[1] - 16, "カメラ", size=13, fill=GRAY)
    view = root.add("line", x1=cam[0], y1=cam[1], x2=cam[0], y2=cam[1], stroke=INK, stroke_width=2.5, stroke_dasharray="6 4")
    view.Ramp(0.5, 1.3, "x2", F[0])
    view.Ramp(0.5, 1.3, "y2", F[1])
    dx, dy = F[0] - cam[0], F[1] - cam[1]
    length = math.hypot(dx, dy)
    rdir = (dx / length, -dy / length)
    stepl = 26.0
    hit_index = None
    pts = []
    for i in range(1, 30):
        x, y = F[0] + rdir[0] * stepl * i, F[1] + rdir[1] * stepl * i
        inside = box[0] <= x <= box[2] and box[1] <= y <= box[3]
        pts.append((x, y, inside))
        if inside:
            hit_index = i
            break
    root.add("circle", cx=F[0], cy=F[1], r=6, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, F[0] - 20, F[1] + 26, "この床のピクセル", size=13, fill=INK)
    t0, step = 1.6, 0.42
    prev = F
    for i, (x, y, inside) in enumerate(pts):
        t = t0 + i * step
        seg = root.add("line", x1=R(prev[0]), y1=R(prev[1]), x2=R(x), y2=R(y), stroke=GREEN if not inside else RED, stroke_width=2.5, opacity=0)
        seg.Show(t)
        dot = root.add("circle", cx=R(x), cy=R(y), r=6 if not inside else 9, fill=GREEN if not inside else RED, stroke="#ffffff", stroke_width=2, opacity=0)
        dot.Show(t)
        prev = (x, y)
    hit_t = t0 + (len(pts) - 1) * step
    Timeline(scene, root, 40, 340, [(t0 + i * step, "ステップ %d:%s" % (i + 1, "物にぶつかった！" if ins else "まだ手前（何もない）")) for i, (_, _, ins) in enumerate(pts)], 20, size=15, fill=INK)
    swatch = root.add("rect", x=F[0] - 10, y=F[1] + 6, width=20, height=12, fill=RED, stroke=INK, opacity=0)
    swatch.Show(hit_t + 0.7)
    Caption(scene, 40, 52, [(0.0, 1.5, "① カメラから床のピクセルへ視線が届く"), (1.5, hit_t + 0.4, "② 反射した向きへ、一定の間隔で進みながら、物があるか調べる"),
                            (hit_t + 0.4, 20, "③ ぶつかった所の色を、床に映す（床のピクセルが赤くなる）")], size=14, fill=GRAY, weight=500)
    scene.Note(hit_t, name, "ステップ %d で衝突" % len(pts))
    return dict(name=name, page="graphics/reflections/ssr-basics/linear-march.md", scene=scene, size=(780, 360), times=[1.2, 3.0, 5.5, 9.0])


def Culling():
    name = "frustum-culling-sweep"
    scene = NewScene(name, 780, 420, duration=9.0, hold=0.0, title="視錐台カリング:カメラが回ると、視野に入った物だけ描く")
    root = scene.root
    cam = (390, 340)
    root.add("rect", x=40, y=50, width=700, height=330, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    rng = random.Random(21)
    objs = []
    while len(objs) < 18:
        a = rng.uniform(math.radians(-170), math.radians(-10))
        r = rng.uniform(70, 250)
        x, y = cam[0] + r * math.cos(a), cam[1] + r * math.sin(a)
        if 55 < x < 725 and 70 < y < 330:
            objs.append((x, y))
    frames = 45
    fov = math.radians(70)
    far = 270

    def Angle(f):
        s = f / frames
        return math.radians(-90) + math.radians(55) * math.sin(2 * math.pi * s)

    cone = root.add("polygon", points="", fill=BLUE, fill_opacity=0.15, stroke=BLUE, stroke_width=2)
    cone.attrs["points"] = "0,0 0,0 0,0"
    states = [[] for _ in objs]
    counts = []
    for f in range(frames + 1):
        ang = Angle(f)
        a1, a2 = ang - fov / 2, ang + fov / 2
        pts = [cam] + [(cam[0] + far * math.cos(a1 + (a2 - a1) * i / 6), cam[1] + far * math.sin(a1 + (a2 - a1) * i / 6)) for i in range(7)]
        pstr = " ".join("%s,%s" % (R(x), R(y)) for x, y in pts)
        t = 9.0 * f / frames
        if f == 0:
            cone.attrs["points"] = pstr
        else:
            cone.Ramp(tp, t, "points", pstr)
        tp = t
        n = 0
        for i, (x, y) in enumerate(objs):
            d = math.hypot(x - cam[0], y - cam[1])
            rel = (math.atan2(y - cam[1], x - cam[0]) - ang + math.pi) % (2 * math.pi) - math.pi
            vis = d < far and abs(rel) < fov / 2 + math.atan2(10, max(d, 1))
            states[i].append((t, GREEN if vis else "#cbd5e1"))
            n += 1 if vis else 0
        counts.append((t, n))
    for i, (x, y) in enumerate(objs):
        c = root.add("circle", cx=R(x), cy=R(y), r=10, fill="#cbd5e1", stroke=INK, stroke_width=1.5)
        c.Steps("fill", states[i][1:])
    root.add("circle", cx=cam[0], cy=cam[1], r=9, fill=RED, stroke="#ffffff", stroke_width=2)
    scene.Text(root, cam[0] - 18, cam[1] + 28, "カメラ", size=13, fill=GRAY)
    Timeline(scene, root, 56, 76, [(t, "描く物:%d / %d" % (n, len(objs))) for t, n in counts], 20, size=18, fill=INK)
    Caption(scene, 40, 404, [(0.0, 20, "緑 = 視野に入っている（描く）、灰色 = 外（描かない）。外の物は、頂点シェーダーにも回らない。")], size=14, fill=GRAY, weight=500)
    return dict(name=name, page="rendering/culling.md", before="## オクルージョン カリング", scene=scene, size=(780, 420), times=[0.5, 2.2, 4.5, 6.8])


def Bloom():
    name = "bloom-stages"
    scene = NewScene(name, 780, 340, duration=10.0, hold=1.5, title="ブルーム:明るい所だけ抜き出し → ぼかして → 元に足す")
    root = scene.root
    pw, ph = 155, 120
    xs = [20, 215, 410, 605]
    titles = ["① 元の絵", "② 明るい所だけ", "③ ぼかす", "④ 元に足す"]
    lights = [(36, 38, 11), (100, 74, 8), (64, 96, 6)]
    for fid, dev in (("bl-a", 3), ("bl-b", 7)):
        flt = scene.defs.add("filter", id=fid, x="-80%", y="-80%", width="260%", height="260%")
        flt.add("feGaussianBlur", stdDeviation=dev)
    for i, x in enumerate(xs):
        t_show = 0.6 + i * 2.0
        g = root.add("g", opacity=0 if i else 1)
        if i:
            g.Show(t_show)
        scene.Text(g, x, 62, titles[i], size=16, fill=INK)
        g.add("rect", x=x, y=76, width=pw, height=ph, fill="#0f172a", stroke="#94a3b8", stroke_width=2)
        if i in (0, 3):
            g.add("rect", x=x + 14, y=76 + 66, width=56, height=46, fill="#475569")
            g.add("rect", x=x + 88, y=76 + 80, width=52, height=32, fill="#64748b")
        if i in (0, 1):
            for lx, ly, lr in lights:
                g.add("circle", cx=x + lx, cy=76 + ly, r=lr, fill="#fff7d1")
        if i == 2:
            weak = g.add("g", filter="url(#bl-a)")
            strong = g.add("g", filter="url(#bl-b)", opacity=0)
            for layer in (weak, strong):
                for lx, ly, lr in lights:
                    layer.add("circle", cx=x + lx, cy=76 + ly, r=lr, fill="#fff7d1")
            strong.Ramp(4.8, 6.4, "opacity", 1)
        if i == 3:
            glow = g.add("g", filter="url(#bl-b)", opacity=0.95)
            for lx, ly, lr in lights:
                glow.add("circle", cx=x + lx, cy=76 + ly, r=lr * 1.5, fill="#ffe27a")
            for lx, ly, lr in lights:
                g.add("circle", cx=x + lx, cy=76 + ly, r=lr, fill="#ffffff")
        if i < 3:
            a_ = root.add("line", x1=x + pw + 4, y1=76 + ph / 2, x2=xs[i + 1] - 6, y2=76 + ph / 2, stroke=INK, stroke_width=2.5, marker_end=scene.marker, opacity=0)
            a_.Show(t_show + 1.0)
    Caption(scene, 20, 236, [(0.0, 2.6, "まず、ふつうに描いた絵（明るい光の周りは、にじんでいない）"), (2.6, 4.6, "② 閾値より明るいピクセルだけを残す（あとは黒）"),
                             (4.6, 7.2, "③ 縮小しながらぼかして、光のにじみを作る（ぼかしが強くなる）"), (7.2, 20, "④ ぼかした光を元の絵に足す → 明るい物が光って見える")], size=15, fill=INK)
    scene.Text(root, 20, 272, "ぼかしは、縮小 → ぼかし → 拡大を重ねると、広くて安いにじみになる。", size=13, weight=500, fill=GRAY)
    scene.Text(root, 20, 296, "足す前に閾値で選ぶので、暗い所は光らない。", size=13, weight=500, fill=GRAY)
    return dict(name=name, page="graphics/postprocess/bloom.md", before="## 実装の流れ", scene=scene, size=(780, 340), times=[1.0, 3.2, 6.0, 9.5])


def MvpOrder():
    name = "trs-order"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="行列の掛ける順番:回転してから移動と、移動してから回転は、結果が違う")
    root = scene.root
    shape = [(0, 0), (60, 0), (60, 14), (14, 14), (14, 30), (44, 30), (44, 44), (14, 44), (14, 70), (0, 70)]
    panels = [(40, "回転 → 移動（左から右へ掛ける）", "rt"), (420, "移動 → 回転（左から右へ掛ける）", "tr")]
    ang_final = math.radians(50)
    shift = 85
    for px, title, mode in panels:
        scene.Text(root, px, 66, title, size=15, fill=INK)
        cx, cy = px + 60, 215
        root.add("rect", x=px, y=80, width=320, height=250, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        root.add("line", x1=cx - 30, y1=cy, x2=cx + 280, y2=cy, stroke=LIGHT, stroke_width=1.5)
        root.add("line", x1=cx, y1=cy - 150, x2=cx, y2=cy + 60, stroke=LIGHT, stroke_width=1.5)
        root.add("circle", cx=cx, cy=cy, r=5, fill=RED)
        scene.Text(root, cx - 12, cy + 24, "原点", size=12, fill=RED)

        def Pts(angle, tx):
            out = []
            for (x, y) in shape:
                px_, py_ = x * 0.9, -y * 0.9
                if mode == "rt":
                    rx = px_ * math.cos(angle) - py_ * math.sin(angle)
                    ry = px_ * math.sin(angle) + py_ * math.cos(angle)
                    out.append((cx + rx + tx, cy + ry))
                else:
                    ux, uy = px_ + tx, py_
                    rx = ux * math.cos(angle) - uy * math.sin(angle)
                    ry = ux * math.sin(angle) + uy * math.cos(angle)
                    out.append((cx + rx, cy + ry))
            return " ".join("%s,%s" % (R(a), R(b)) for a, b in out)

        ghost = root.add("polygon", points=Pts(0, 0), fill="none", stroke="#94a3b8", stroke_width=1.5, stroke_dasharray="4 3")
        poly = root.add("polygon", points=Pts(0, 0), fill=AMBER, stroke=INK, stroke_width=2)
        n = 20
        times = (1.0, 4.0, 4.8, 7.8)
        for i in range(1, n + 1):
            f = i / n
            t = Lerp(times[0], times[1], f)
            a = Smooth(f) * ang_final
            tx = 0 if mode == "rt" else 0
            if mode == "rt":
                poly.Ramp(Lerp(times[0], times[1], (i - 1) / n), t, "points", Pts(a, 0))
            else:
                poly.Ramp(Lerp(times[0], times[1], (i - 1) / n), t, "points", Pts(0, Smooth(f) * shift))
        for i in range(1, n + 1):
            f = i / n
            t = Lerp(times[2], times[3], f)
            if mode == "rt":
                poly.Ramp(Lerp(times[2], times[3], (i - 1) / n), t, "points", Pts(ang_final, Smooth(f) * shift))
            else:
                poly.Ramp(Lerp(times[2], times[3], (i - 1) / n), t, "points", Pts(Smooth(f) * ang_final, shift))
        Caption(scene, px, 352, [(0.0, 1.0, "最初は原点にある"), (1.0, 4.0, "回転する（原点を中心に）" if mode == "rt" else "右へ移動する"),
                                 (4.0, 4.8, ""), (4.8, 7.8, "右へ移動する" if mode == "rt" else "回転する（原点を中心に！）"),
                                 (7.8, 20, "最終位置:原点の近くで回り、右へ" if mode == "rt" else "最終位置:原点の周りを大きく回った所")], size=14, fill=INK)
    Caption(scene, 40, 384, [(0.0, 20, "ふつうは「拡大 → 回転 → 移動」の順（左から右）。移動を先にすると、物が原点の周りを回ってしまう。")], size=14, fill=GRAY, weight=500)
    return dict(name=name, page="3d/transforms-mvp.md", before="## 手で変換して、確かめる", scene=scene, size=(780, 400), times=[0.5, 3.0, 6.0, 9.5])


def GiBounce():
    name = "gi-color-bleeding"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="間接光:光が壁で跳ね返って、隣の面に色がにじむ")
    root = scene.root
    rx, ry, rw, rh = 80, 60, 480, 270
    root.add("rect", x=rx, y=ry, width=rw, height=rh, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    root.add("rect", x=rx - 8, y=ry, width=16, height=rh, fill=RED)
    scene.Text(root, rx + 6, ry - 8, "赤い壁", size=13, fill=RED)
    root.add("rect", x=rx, y=ry + rh, width=rw, height=14, fill="#94a3b8")
    glow = scene.defs.add("linearGradient", id="gi-bleed", x1="0", y1="0", x2="1", y2="0")
    glow.add("stop", offset="0", stop_color="#ff5a5f", stop_opacity="0.75")
    glow.add("stop", offset="1", stop_color="#ff5a5f", stop_opacity="0")
    bleed = root.add("rect", x=rx, y=ry + rh - 10, width=180, height=10, fill="url(#gi-bleed)", opacity=0)
    bleed.Set(6.0, "opacity", 1)
    lamp = (330, ry + 12)
    root.add("circle", cx=lamp[0], cy=lamp[1], r=12, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, lamp[0] + 18, lamp[1] + 6, "光源", size=13, fill=INK)
    W = (rx, 190)
    FL = (420, ry + rh)
    FN = (rx + 90, ry + rh)

    def Ray(x1, y1, x2, y2, t0, t1, color, width=3, dash=None):
        line = root.add("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=width, pathLength=1, stroke_dasharray="1 1", stroke_dashoffset=1, opacity=0)
        line.Set(t0, "opacity", 1)
        line.Ramp(t0, t1, "stroke-dashoffset", 0)
        ang = math.atan2(y2 - y1, x2 - x1)
        tip = (x2, y2)
        left = (x2 - 12 * math.cos(ang - 0.45), y2 - 12 * math.sin(ang - 0.45))
        right = (x2 - 12 * math.cos(ang + 0.45), y2 - 12 * math.sin(ang + 0.45))
        head = root.add("polygon", points="%s,%s %s,%s %s,%s" % (R(tip[0]), R(tip[1]), R(left[0]), R(left[1]), R(right[0]), R(right[1])), fill=color, opacity=0)
        head.Set(t1, "opacity", 1)
        return line

    Ray(lamp[0], lamp[1] + 12, FL[0], FL[1] - 2, 1.0, 2.0, AMBER)
    patch = root.add("rect", x=FL[0] - 34, y=ry + rh - 10, width=68, height=10, fill="#fde68a", opacity=0)
    patch.Set(2.0, "opacity", 1)
    Ray(lamp[0] - 10, lamp[1] + 10, W[0] + 6, W[1], 2.8, 3.8, AMBER)
    for k, (x2) in enumerate((rx + 50, rx + 130, rx + 210)):
        Ray(W[0] + 6, W[1], x2, ry + rh - 2, 4.4 + k * 0.4, 5.2 + k * 0.4, "#ff5a5f", width=2.5)
    Caption(scene, 80, 358, [(0.0, 1.0, "光源から出た光"), (1.0, 2.8, "① 床に当たる（直接光）→ 明るくなる"), (2.8, 4.4, "② 赤い壁に当たる"),
                             (4.4, 6.0, "③ 壁は赤い光だけを反射して、四方に跳ね返す"), (6.0, 20, "④ 壁の近くの床が、赤っぽくなる（色のにじみ）")], size=15, fill=INK)
    scene.Text(root, 80, 384, "間接光は、直接光が当たった面が「次の光源」になる。リアルタイムでは、プローブやボクセルで近似する。", size=13, weight=500, fill=GRAY)
    scene.Text(root, 590, 90, "光の跳ね返り", size=14, fill=GRAY)
    Timeline(scene, root, 590, 130, [(0.0, "0 回"), (1.0, "1 回（直接）"), (2.8, "1 回（壁へ）"), (4.4, "2 回（壁 → 床）")], 20, size=22, fill=INK)
    return dict(name=name, page="graphics/gi/theory/taxonomy.md", scene=scene, size=(780, 400), times=[1.5, 3.4, 5.0, 8.5])


FIGS = [Waves, ShadowMap, Sorting, Scattering, Clouds, Lod, Ssao, Ssr, Culling, MvpOrder, GiBounce]
