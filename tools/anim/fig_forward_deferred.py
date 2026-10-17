import io
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storyboard import Hex, Mix, Rgb, Scene, ReplaceBetween  # noqa: E402

W, H = 960, 540
DURATION, HOLD = 12.0, 1.5
GRID_X, GRID_Y = 16, 9
CELL = 26
PANEL_X = {"F": 32, "D": 512}
GRID_TOP = 50
SPHERE_COUNT = 10
LIGHT_Z = 7.0
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"

LIGHTS = [
    {"pos": (2.0, 1.5), "rgb": (1.00, 0.20, 0.25), "name": "赤"},
    {"pos": (13.8, 1.3), "rgb": (1.00, 0.80, 0.10), "name": "黄"},
    {"pos": (8.0, 4.6), "rgb": (0.15, 0.90, 0.35), "name": "緑"},
    {"pos": (2.6, 7.6), "rgb": (0.20, 0.50, 1.00), "name": "青"},
    {"pos": (13.4, 7.6), "rgb": (0.80, 0.25, 1.00), "name": "紫"},
]
HUES = ["#e5484d", "#f08a24", "#e5b800", "#46a758", "#12a594", "#0091ff", "#3e63dd", "#8e4ec6", "#d6409f", "#8b8d98"]
AMBIENT = 0.12
GAIN = 4.2
TEXT = "#1f2937"
RED = "#e5484d"


def FindSpheres():
    rng = random.Random(11)
    cells = np.array([(x + 0.5, y + 0.5) for y in range(GRID_Y) for x in range(GRID_X)])

    def Masks(spheres):
        return [((cells[:, 0] - sx) ** 2 + (cells[:, 1] - sy) ** 2) <= r * r for sx, sy, r in spheres]

    def Score(spheres):
        masks = Masks(spheres)
        union = np.zeros(len(cells), dtype=bool)
        owner = -np.ones(len(cells), dtype=int)
        for k, m in enumerate(masks):
            union |= m
            owner[m] = k
        visible = [int((owner == k).sum()) for k in range(SPHERE_COUNT)]
        total = sum(int(m.sum()) for m in masks)
        penalty = (len(cells) - int(union.sum())) * 20.0
        penalty += sum(max(0, 7 - v) * 6.0 + max(0, v - 28) * 2.0 for v in visible)
        penalty += abs(total - 335) * 0.5
        centers = [(s[0], s[1]) for s in spheres]
        for i in range(SPHERE_COUNT):
            for j in range(i):
                d = math.dist(centers[i], centers[j])
                if d < 2.2:
                    penalty += (2.2 - d) * 10.0
        return penalty

    best = None
    for restart in range(30):
        spheres = [(rng.uniform(1.0, 15.0), rng.uniform(0.8, 8.2), rng.uniform(2.3, 3.8)) for _ in range(SPHERE_COUNT)]
        score = Score(spheres)
        for _ in range(4000):
            k = rng.randrange(SPHERE_COUNT)
            sx, sy, r = spheres[k]
            cand = list(spheres)
            cand[k] = (min(15.5, max(0.5, sx + rng.gauss(0, 0.8))), min(8.5, max(0.5, sy + rng.gauss(0, 0.8))), min(3.9, max(2.3, r + rng.gauss(0, 0.2))))
            cs = Score(cand)
            if cs <= score:
                spheres, score = cand, cs
            if score == 0:
                break
        if best is None or score < best[0]:
            best = (score, spheres)
        if score == 0:
            break
    if best[0] > 0:
        raise RuntimeError("no layout, best penalty %.1f" % best[0])
    return best[1]


def Tone(c):
    return 1.0 - math.exp(-c)


def ShadeColors(sphere, k, gx, gy, albedo):
    sx, sy, r = sphere
    cx, cy = gx + 0.5, gy + 0.5
    dx, dy = (cx - sx) / r, (cy - sy) / r
    d2 = min(dx * dx + dy * dy, 0.999)
    nz = math.sqrt(1.0 - d2)
    normal = (dx, dy, nz)
    px, py, pz = cx, cy, r * 0.3 + nz * r
    arg = Rgb(albedo)
    base = [v / 255.0 for v in arg]
    contribs = []
    for light in LIGHTS:
        lx, ly = light["pos"]
        vx, vy, vz = lx - px, ly - py, LIGHT_Z - pz
        dist = math.sqrt(vx * vx + vy * vy + vz * vz)
        ndl = max(0.0, (normal[0] * vx + normal[1] * vy + normal[2] * vz) / dist)
        intensity = ndl / (1.0 + (dist / 4.5) ** 2) * GAIN
        contribs.append([light["rgb"][c] * intensity for c in range(3)])
    colors = []
    for n in range(len(LIGHTS) + 1):
        rgb = []
        for c in range(3):
            total = AMBIENT + sum(contribs[j][c] for j in range(n))
            rgb.append(255.0 * Tone(base[c] * total * 1.25))
        colors.append(Hex(rgb))
    stripe_normal = Hex([(normal[0] + 1) * 127.5, (normal[1] + 1) * 127.5, (normal[2] + 1) * 127.5])
    depth = 0.12 + 0.75 * (1.0 - (nz * r * 0.3 + (SPHERE_COUNT - k) * 0.5) / (r * 0.3 + SPHERE_COUNT * 0.5 + 0.01))
    depth = max(0.1, min(0.95, depth))
    stripe_depth = Hex([depth * 255] * 3)
    return colors, stripe_normal, stripe_depth


def Build():
    spheres = FindSpheres()
    albedos = [Mix("#b8bcc4", h, 0.30) for h in HUES]
    cover = []
    for sx, sy, r in spheres:
        cover.append([(x, y) for y in range(GRID_Y) for x in range(GRID_X)
                      if (x + 0.5 - sx) ** 2 + (y + 0.5 - sy) ** 2 <= r * r])
    owner = {}
    for k, cs in enumerate(cover):
        for c in cs:
            owner[c] = k
    shade = {}
    for k in range(SPHERE_COUNT):
        for (x, y) in cover[k]:
            shade[(k, x, y)] = ShadeColors(spheres[k], k, x, y, albedos[k])

    scene = Scene("forward-vs-deferred", W, H, DURATION, HOLD, still=11.5)
    root = scene.root
    lights_n = len(LIGHTS)
    forward_start, forward_slot = 0.4, 0.9
    hit_offset, hit_step, hit_len = 0.12, 0.14, 0.11
    pass1_start, pass1_slot = 0.8, 0.45
    pass2_start, pass2_slot, wave_len = 5.6, 0.9, 0.7
    forward_result_t, deferred_result_t = 9.7, 10.4

    def Px(panel, gx):
        return PANEL_X[panel] + gx * CELL

    def Py(gy):
        return GRID_TOP + gy * CELL

    root.add("line", x1=480, y1=16, x2=480, y2=H - 16, stroke="#cbd5e1", stroke_width=2)
    scene.Text(root, PANEL_X["F"], 32, "Forward", size=26, fill="#2563eb")
    scene.Text(root, PANEL_X["D"], 32, "Deferred", size=26, fill="#7c3aed")
    scene.Text(root, PANEL_X["F"] + 150, 32, "物体ごとに光を計算", size=15, weight=500, fill="#64748b")
    scene.Text(root, PANEL_X["D"] + 170, 32, "まず絵を貯めて、あとで光を計算", size=15, weight=500, fill="#64748b")

    defs = root.add("defs")
    grad = defs.add("radialGradient", id="fd-sphere", cx="0.5", cy="0.5", r="0.5", fx="0.36", fy="0.3")
    grad.add("stop", offset="0", stop_color="#ffffff", stop_opacity="0.5")
    grad.add("stop", offset="0.45", stop_color="#ffffff", stop_opacity="0")
    grad.add("stop", offset="0.8", stop_color="#000000", stop_opacity="0.08")
    grad.add("stop", offset="1", stop_color="#000000", stop_opacity="0.4")
    clip = root.add("clipPath", id="fd-clip-f")
    clip.add("rect", x=PANEL_X["F"], y=GRID_TOP, width=GRID_X * CELL, height=GRID_Y * CELL)
    clip = root.add("clipPath", id="fd-clip-d")
    clip.add("rect", x=PANEL_X["D"], y=GRID_TOP, width=GRID_X * CELL, height=GRID_Y * CELL)

    for panel in ("F", "D"):
        g = root.add("g")
        g.add("rect", x=PANEL_X[panel], y=GRID_TOP, width=GRID_X * CELL, height=GRID_Y * CELL, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        for i in range(1, GRID_X):
            g.add("line", x1=Px(panel, i), y1=GRID_TOP, x2=Px(panel, i), y2=Py(GRID_Y), stroke="#e2e8f0", stroke_width=1)
        for j in range(1, GRID_Y):
            g.add("line", x1=PANEL_X[panel], y1=Py(j), x2=Px(panel, GRID_X), y2=Py(j), stroke="#e2e8f0", stroke_width=1)

    groups = {"F": [root.add("g", clip_path="url(#fd-clip-f)") for _ in range(SPHERE_COUNT)], "D": [root.add("g", clip_path="url(#fd-clip-d)") for _ in range(SPHERE_COUNT)]}

    flat_total = sum(len(c) for c in cover)
    visible_total = len(owner)
    assert visible_total == GRID_X * GRID_Y

    forward_counter, forward_waste = [], []
    forward_count, forward_waste_count = 0, 0
    covered = set()
    ray_f = []
    for i, light in enumerate(LIGHTS):
        ray = root.add("line", x1=Px("F", light["pos"][0]), y1=Py(light["pos"][1]), x2=Px("F", light["pos"][0]), y2=Py(light["pos"][1]),
                       stroke=Hex([v * 255 for v in light["rgb"]]), stroke_width=3, stroke_dasharray="6 4", opacity=0)
        ray_f.append(ray)

    lamp_f, lamp_d = [], []
    for panel, store in (("F", lamp_f), ("D", lamp_d)):
        scene.Text(root, PANEL_X[panel], 324, "ライト", size=17)
        for i, light in enumerate(LIGHTS):
            color = Hex([v * 255 for v in light["rgb"]])
            lamp = root.add("circle", cx=PANEL_X[panel] + 74 + i * 36, cy=318, r=11, fill=color, stroke="#1f2937", stroke_width=1.5, opacity=0.22)
            store.append(lamp)

    caption_items_f1, caption_items_d1 = [], []

    for k in range(SPHERE_COUNT):
        t0 = forward_start + k * forward_slot
        sx, sy, r = spheres[k]
        gf = groups["F"][k]
        newly_overwritten = [c for c in cover[k] if c in covered]
        forward_waste_count += len(newly_overwritten) * lights_n
        if newly_overwritten:
            forward_waste.append((t0, forward_waste_count))
        scene.Note(t0, "Forward", "物体 %d を描く:%d マス(うち %d マスは前の物体を上書き)" % (k + 1, len(cover[k]), len(newly_overwritten)))
        for (x, y) in cover[k]:
            colors, _, _ = shade[(k, x, y)]
            rect = gf.add("rect", x=Px("F", x), y=Py(y), width=CELL, height=CELL, fill=colors[0],
                          opacity=0, stroke=RED, stroke_width=2.4, stroke_opacity=0)
            rect.Set(t0, "opacity", 1)
            if (x, y) in covered:
                rect.Set(t0, "stroke-opacity", 1)
                rect.Set(t0 + forward_slot - 0.02, "stroke-opacity", 0)
            for i, light in enumerate(LIGHTS):
                th = t0 + hit_offset + hit_step * i
                flash = Mix(colors[i], Hex([v * 255 for v in light["rgb"]]), 0.85)
                rect.Set(th, "fill", flash)
                rect.Set(th + 0.09, "fill", colors[i + 1])
        for (x, y) in cover[k]:
            covered.add((x, y))
        outline = gf.add("circle", cx=Px("F", sx), cy=Py(sy), r=r * CELL, fill="none", stroke="#1e293b", stroke_width=2, opacity=0)
        outline.Set(t0, "opacity", 1)
        shade_ball = gf.add("circle", cx=Px("F", sx), cy=Py(sy), r=r * CELL, fill="url(#fd-sphere)", opacity=0)
        shade_ball.Set(t0 + hit_offset + hit_step * lights_n, "opacity", 1)
        badge = gf.add("circle", cx=Px("F", sx), cy=Py(sy), r=11, fill="#ffffff", stroke="#334155", stroke_width=1.5, opacity=0)
        badge.Set(t0, "opacity", 1)
        label = scene.Text(gf, Px("F", sx), Py(sy) + 5, str(k + 1), size=14, anchor="middle", opacity=0)
        label.Set(t0, "opacity", 1)
        for i, light in enumerate(LIGHTS):
            th = t0 + hit_offset + hit_step * i
            forward_count += len(cover[k])
            forward_counter.append((th, forward_count))
            ray = ray_f[i]
            ray.Set(th, "x2", Px("F", sx))
            ray.Set(th, "y2", Py(sy))
            ray.Set(th, "opacity", 0.95)
            ray.Set(th + hit_len, "opacity", 0)
            lamp_f[i].Set(th, "opacity", 1)
            lamp_f[i].Set(th + hit_len, "opacity", 0.22)
            scene.Note(th, "Forward", "  ライト %s が物体 %d の %d マスに当たる(計算 %s 回目まで)" % (light["name"], k + 1, len(cover[k]), "{:,}".format(forward_count)))
        caption_items_f1.append((t0, t0 + forward_slot if k < SPHERE_COUNT - 1 else forward_result_t,
                                 "%s 物体 %d/%d:その形のピクセルすべてにライト %d つ" % (CIRCLED[k], k + 1, SPHERE_COUNT, lights_n)))
    forward_total = forward_count
    assert forward_total == flat_total * lights_n

    scene.TextStack(root, PANEL_X["F"], 412, caption_items_f1, size=15, fill=TEXT)
    scene.TextStack(root, PANEL_X["F"], 436, [(forward_start, forward_result_t, "赤枠 = 前の物体を上書き(前の計算が無駄に)")], size=15, fill=RED)

    scene.Text(root, PANEL_X["F"], 358, "ピクセル計算:", size=20)
    scene.Counter(root, PANEL_X["F"] + 130, 360, [(t, v) for t, v in forward_counter], size=26)
    scene.Text(root, PANEL_X["F"], 388, "うち、あとで上書きされて無駄:", size=15, fill=RED)
    scene.Counter(root, PANEL_X["F"] + 232, 388, forward_waste, size=18, fill=RED)

    pct = int(round(100.0 * (flat_total - visible_total) / flat_total))

    box = root.add("g", opacity=0)
    box.Show(forward_result_t)
    box.add("rect", x=PANEL_X["F"], y=398, width=416, height=128, rx=12, fill="#eff6ff", stroke="#2563eb", stroke_width=2.5)
    scene.Text(box, PANEL_X["F"] + 16, 428, "物体%d × ライト%d = %d回の描画" % (SPHERE_COUNT, lights_n, SPHERE_COUNT * lights_n), size=19, fill="#1e3a8a")
    scene.Text(box, PANEL_X["F"] + 16, 458, "ピクセル計算 %d マス × ライト%d = %s回" % (flat_total, lights_n, "{:,}".format(forward_total)), size=19, fill="#1e3a8a")
    scene.Text(box, PANEL_X["F"] + 16, 490, "隠れて見えない部分も計算:無駄 約%d%%" % pct, size=19, fill=RED)
    scene.Text(box, PANEL_X["F"] + 16, 514, "(重なったマスの計算は、あとで上書きされて捨てられる)", size=13, weight=500, fill="#64748b")
    scene.Note(forward_result_t, "Forward", "結果ボックス:計算 %s 回、無駄 %d%%(最終カウンター %s / 無駄 %s)" % ("{:,}".format(forward_total), pct, "{:,}".format(forward_total), "{:,}".format(forward_waste_count)))

    # ---------------- Deferred ----------------
    deferred_counter = []
    deferred_count = 0
    for k in range(SPHERE_COUNT):
        t0 = pass1_start + k * pass1_slot
        sx, sy, r = spheres[k]
        gd = groups["D"][k]
        scene.Note(t0, "Deferred", "Pass 1:物体 %d を G-Buffer に書く(%d マス)" % (k + 1, len(cover[k])))
        for (x, y) in cover[k]:
            colors, stripe_normal, stripe_depth = shade[(k, x, y)]
            g = gd.add("g", opacity=0)
            g.Set(t0, "opacity", 1)
            w3 = CELL / 3.0
            ox = Px("D", x)
            oy = Py(y)
            g.add("rect", x=ox, y=oy, width=round(w3, 2), height=CELL, fill=albedos[k])
            g.add("rect", x=round(ox + w3, 2), y=oy, width=round(w3, 2), height=CELL, fill=stripe_normal)
            g.add("rect", x=round(ox + 2 * w3, 2), y=oy, width=round(w3, 2), height=CELL, fill=stripe_depth)
            if owner[(x, y)] == k:
                lit = gd.add("rect", x=ox, y=oy, width=CELL, height=CELL, fill=colors[0], opacity=0)
                for i, light in enumerate(LIGHTS):
                    s_i = pass2_start + pass2_slot * i
                    tc = s_i + wave_len * (x + y + 1) / (GRID_X + GRID_Y - 1)
                    if i == 0:
                        lit.Set(tc, "opacity", 1)
                    flash = Mix(colors[i], Hex([v * 255 for v in light["rgb"]]), 0.85)
                    lit.Set(tc, "fill", flash)
                    lit.Set(tc + 0.09, "fill", colors[i + 1])
        outline = gd.add("circle", cx=Px("D", sx), cy=Py(sy), r=r * CELL, fill="none", stroke="#1e293b", stroke_width=2, opacity=0)
        outline.Set(t0, "opacity", 1)
        badge = gd.add("circle", cx=Px("D", sx), cy=Py(sy), r=11, fill="#ffffff", stroke="#334155", stroke_width=1.5, opacity=0)
        badge.Set(t0, "opacity", 1)
        label = scene.Text(gd, Px("D", sx), Py(sy) + 5, str(k + 1), size=14, anchor="middle", opacity=0)
        label.Set(t0, "opacity", 1)
        shade_ball = gd.add("circle", cx=Px("D", sx), cy=Py(sy), r=r * CELL, fill="url(#fd-sphere)", opacity=0)
        shade_ball.Set(pass2_start + pass2_slot * lights_n - 0.05, "opacity", 1)

    pass1_end = pass1_start + SPHERE_COUNT * pass1_slot
    caption_d = []
    for k in range(SPHERE_COUNT):
        t0 = pass1_start + k * pass1_slot
        t1 = pass1_start + (k + 1) * pass1_slot if k < SPHERE_COUNT - 1 else pass2_start
        caption_d.append((t0, t1, "① Pass 1:物体を G-Buffer に書く(%d/%d)" % (k + 1, SPHERE_COUNT)))
    for i in range(lights_n):
        s_i = pass2_start + pass2_slot * i
        t1 = s_i + pass2_slot if i < lights_n - 1 else deferred_result_t
        caption_d.append((s_i, t1, "② Pass 2:全ピクセルにライトを1つずつ(%d/%d)" % (i + 1, lights_n)))
    scene.TextStack(root, PANEL_X["D"], 412, caption_d, size=15, fill=TEXT)
    sub_d = [(pass1_start, pass2_start, "1マスに 色 | 法線 | 深度 の3種類を保存"),
             (pass2_start, deferred_result_t, "物体の数に関係なく、画面全体を1回なぞる × %d ライト" % lights_n)]
    scene.TextStack(root, PANEL_X["D"], 436, sub_d, size=15, fill="#7c3aed")

    wave_lines = []
    for i, light in enumerate(LIGHTS):
        line = root.add("line", x1=PANEL_X["D"], y1=GRID_TOP, x2=PANEL_X["D"], y2=GRID_TOP + GRID_Y * CELL, stroke=Hex([v * 255 for v in light["rgb"]]),
                        stroke_width=5, opacity=0, clip_path="url(#fd-clip-d)")
        s_i = pass2_start + pass2_slot * i
        line.Set(s_i, "opacity", 0.9)
        line.Set(s_i, "x1", Px("D", 0))
        line.Set(s_i, "x2", Px("D", -GRID_Y))
        line.Ramp(s_i, s_i + wave_len, "x1", Px("D", GRID_X + GRID_Y - 1))
        line.Ramp(s_i, s_i + wave_len, "x2", Px("D", GRID_X - 1))
        line.Set(s_i + wave_len + 0.01, "opacity", 0)
        wave_lines.append(line)
        lamp_d[i].Set(s_i, "opacity", 1)
        lamp_d[i].Set(s_i + pass2_slot, "opacity", 0.22)
        scene.Note(s_i, "Deferred", "Pass 2:ライト %s が画面 %d マスをなぞる(ここまで %s 回)" % (light["name"], GRID_X * GRID_Y, "{:,}".format((i + 1) * GRID_X * GRID_Y)))
        groups_count = {}
        for gx in range(GRID_X):
            for gy in range(GRID_Y):
                gidx = (gx + gy) // 3
                groups_count[gidx] = groups_count.get(gidx, 0) + 1
        for gidx in sorted(groups_count):
            tt = s_i + wave_len * (3 * gidx + 1.5) / (GRID_X + GRID_Y - 1)
            deferred_count += groups_count[gidx]
            deferred_counter.append((tt, deferred_count))
    deferred_total = deferred_count
    assert deferred_total == GRID_X * GRID_Y * lights_n

    scene.Text(root, PANEL_X["D"], 358, "ピクセル計算:", size=20)
    scene.Counter(root, PANEL_X["D"] + 130, 360, deferred_counter, size=26)
    scene.TextStack(root, PANEL_X["D"], 388, [(pass1_start, pass2_start, "いまは材質を貯めているだけ(光の計算はまだ 0)"),
                                              (pass2_start, deferred_result_t, "光の計算は画面のマス数が上限")], size=15, weight=500, fill="#64748b")

    box = root.add("g", opacity=0)
    box.Show(deferred_result_t)
    box.add("rect", x=PANEL_X["D"], y=398, width=416, height=128, rx=12, fill="#f5f3ff", stroke="#7c3aed", stroke_width=2.5)
    scene.Text(box, PANEL_X["D"] + 16, 428, "③ ライティングは画面ピクセルごとに1回", size=19, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 458, "%d px × ライト%d = %s回" % (GRID_X * GRID_Y, lights_n, "{:,}".format(deferred_total)), size=19, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 490, "物体が%d個でも100個でも、この回数は変わらない" % SPHERE_COUNT, size=17, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 514, "(代わりに G-Buffer の書き込みと読み込みが増える)", size=13, weight=500, fill="#64748b")
    scene.Note(deferred_result_t, "Deferred", "結果ボックス:計算 %s 回" % "{:,}".format(deferred_total))

    for panel in ("F", "D"):
        g = root.add("g", opacity=0.35)
        for i in range(1, GRID_X):
            g.add("line", x1=Px(panel, i), y1=GRID_TOP, x2=Px(panel, i), y2=Py(GRID_Y), stroke="#ffffff", stroke_width=1)
        for j in range(1, GRID_Y):
            g.add("line", x1=PANEL_X[panel], y1=Py(j), x2=Px(panel, GRID_X), y2=Py(j), stroke="#ffffff", stroke_width=1)
        g.add("rect", x=PANEL_X[panel], y=GRID_TOP, width=GRID_X * CELL, height=GRID_Y * CELL, fill="none", stroke="#94a3b8", stroke_width=1.5)

    # ---------------- 共通: ライト、VS ----------------
    for panel in ("F", "D"):
        for i, light in enumerate(LIGHTS):
            color = Hex([v * 255 for v in light["rgb"]])
            lx, ly = light["pos"]
            root.add("circle", cx=Px(panel, lx), cy=Py(ly), r=15, fill=color, opacity=0.28)
            root.add("circle", cx=Px(panel, lx), cy=Py(ly), r=7, fill=color, stroke="#ffffff", stroke_width=2.5)
    root.add("circle", cx=480, cy=180, r=24, fill="#1f2937")
    scene.Text(root, 480, 188, "VS", size=22, fill="#ffffff", anchor="middle")

    scene.Note(0.0, "共通", "球体 %d 個(同じ配置)、ライト %d 個(色付き)、画面 %d×%d = %d マス" % (SPHERE_COUNT, lights_n, GRID_X, GRID_Y, GRID_X * GRID_Y))
    scene.Note(DURATION, "共通", "動きの終わり。以降 %.1f 秒は静止してからループ" % HOLD)
    return scene, spheres, cover


def Main():
    scene, spheres, cover = Build()
    svg = scene.Render()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    io.open(os.path.join(out_dir, "forward_deferred.svg"), "w", encoding="utf-8", newline="").write(svg)
    io.open(os.path.join(out_dir, "forward_deferred.report.txt"), "w", encoding="utf-8").write(scene.Report() + "\n")
    print("svg bytes", len(svg.encode("utf-8")))
    lum = []
    for k in range(SPHERE_COUNT):
        pass

    print("sphere cover", [len(c) for c in cover], "sum", sum(len(c) for c in cover))
    snap_dir = os.environ.get("FD_SNAP")
    if snap_dir:
        for t in (1.2, 2.8, 4.0, 7.0, 9.8, 11.0):
            html = '<!doctype html><meta charset="utf-8"><body style="margin:0">' + scene.SnapshotAt(t).replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540"', 1)
            io.open(os.path.join(snap_dir, "snap_%04d.html" % int(t * 10)), "w", encoding="utf-8").write(html)
    if len(sys.argv) > 1:
        ReplaceBetween(sys.argv[1], "<!-- fig:forward-deferred:begin -->", "<!-- fig:forward-deferred:end -->", svg)
        print("replaced in", sys.argv[1])


if __name__ == "__main__":
    Main()
