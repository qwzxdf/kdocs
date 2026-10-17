import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storyboard import Hex, Scene, ReplaceBetween  # noqa: E402

W, H = 960, 540
DURATION, HOLD = 12.0, 1.5
GRID_X, GRID_Y = 28, 16
GRID_PIXELS = 416.0
CELL = GRID_PIXELS / GRID_X
SCALE = GRID_X / 16.0
PANEL_X = {"F": 32, "D": 512}
GRID_TOP = 50
SPHERE_COUNT = 10
LIGHT_Z = 7.0 * SCALE
LIGHT_RANGE = 9.5
TINT_MAX = 0.9
GAIN = 3.0
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"

LIGHTS = [
    {"pos": (2.0 * SCALE, 1.5 * SCALE), "rgb": (1.00, 0.20, 0.25), "name": "赤"},
    {"pos": (13.8 * SCALE, 1.3 * SCALE), "rgb": (1.00, 0.80, 0.10), "name": "黄"},
    {"pos": (8.0 * SCALE, 4.6 * SCALE), "rgb": (0.15, 0.90, 0.35), "name": "緑"},
    {"pos": (2.6 * SCALE, 7.6 * SCALE), "rgb": (0.20, 0.50, 1.00), "name": "青"},
    {"pos": (13.4 * SCALE, 7.6 * SCALE), "rgb": (0.80, 0.25, 1.00), "name": "紫"},
]
TEXT = "#1f2937"
RED = "#e5484d"


def FindSpheres():
    return [
        (5.0, 3.8, 3.2), (7.0, 4.8, 3.0),
        (22.0, 3.6, 3.2), (24.0, 4.6, 2.8),
        (12.5, 7.4, 3.3), (15.0, 8.0, 3.0),
        (5.6, 12.0, 3.0), (7.6, 10.4, 2.8),
        (23.0, 12.0, 3.2), (21.0, 10.2, 2.8),
    ]


def ShadeColors(sphere, gx, gy):
    sx, sy, r = sphere
    cx, cy = gx + 0.5, gy + 0.5
    dx, dy = (cx - sx) / r, (cy - sy) / r
    d2 = min(dx * dx + dy * dy, 0.999)
    nz = math.sqrt(1.0 - d2)
    normal = (dx, dy, nz)
    px, py, pz = cx, cy, r * 0.3 + nz * r
    weights = []
    dists = []
    for light in LIGHTS:
        lx, ly = light["pos"]
        dist = math.hypot(lx - cx, ly - cy)
        weights.append(min(TINT_MAX, max(0.0, 1.0 - dist / LIGHT_RANGE) * TINT_MAX * 1.25))
        dists.append(dist)
    colors = []
    for n in range(len(LIGHTS) + 1):
        rgb = [1.0, 1.0, 1.0]
        for j in range(n):
            for c in range(3):
                rgb[c] *= 1.0 - weights[j] * (1.0 - LIGHTS[j]["rgb"][c])
        colors.append(Hex([255.0 * v for v in rgb]))
    stripe_normal = Hex([(normal[0] + 1) * 127.5, (normal[1] + 1) * 127.5, (normal[2] + 1) * 127.5])
    return colors, stripe_normal, dists


def Build():
    spheres = FindSpheres()
    cover = []
    for sx, sy, r in spheres:
        cover.append([(x, y) for y in range(GRID_Y) for x in range(GRID_X)
                      if (x + 0.5 - sx) ** 2 + (y + 0.5 - sy) ** 2 <= (r + 0.3) ** 2])
    owner = {}
    for k, cs in enumerate(cover):
        for c in cs:
            owner[c] = k
    shade = {}
    for k in range(SPHERE_COUNT):
        for (x, y) in cover[k]:
            shade[(k, x, y)] = ShadeColors(spheres[k], x, y)

    scene = Scene("forward-vs-deferred", W, H, DURATION, HOLD, still=11.5)
    root = scene.root
    lights_n = len(LIGHTS)
    forward_start, forward_slot = 0.4, 0.9
    hit_offset, hit_step, hit_len, stagger = 0.12, 0.14, 0.11, 0.09
    pass1_start, pass1_slot = 0.8, 0.45
    pass2_start, pass2_slot, wave_len = 5.6, 0.9, 0.7
    forward_result_t, deferred_result_t = 9.7, 10.4
    diag = GRID_X + GRID_Y - 1

    def Px(panel, gx):
        return PANEL_X[panel] + gx * CELL

    def Py(gy):
        return GRID_TOP + gy * CELL

    def R(v):
        return round(v, 2)

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
    for panel in ("f", "d"):
        clip = defs.add("clipPath", id="fd-clip-" + panel)
        clip.add("rect", x=PANEL_X[panel.upper()], y=GRID_TOP, width=GRID_PIXELS, height=R(GRID_Y * CELL))

    for panel in ("F", "D"):
        for k, (sx, sy, r) in enumerate(spheres):
            clip = defs.add("clipPath", id="fd-sph-%s%d" % (panel, k))
            clip.add("circle", cx=R(Px(panel, sx)), cy=R(Py(sy)), r=R((r + 0.3) * CELL))

    for panel in ("F", "D"):
        root.add("rect", x=PANEL_X[panel], y=GRID_TOP, width=GRID_PIXELS, height=R(GRID_Y * CELL), fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)

    groups = {"F": [root.add("g", clip_path="url(#fd-clip-f)") for _ in range(SPHERE_COUNT)],
              "D": [root.add("g", clip_path="url(#fd-clip-d)") for _ in range(SPHERE_COUNT)]}

    flat_total = sum(len(c) for c in cover)
    visible_total = len(owner)

    forward_counter, forward_waste = [], []
    forward_count, forward_waste_count = 0, 0
    covered = set()

    ray_f = []
    for i, light in enumerate(LIGHTS):
        ray = root.add("line", x1=R(Px("F", light["pos"][0])), y1=R(Py(light["pos"][1])), x2=R(Px("F", light["pos"][0])), y2=R(Py(light["pos"][1])),
                       stroke=Hex([v * 255 for v in light["rgb"]]), stroke_width=3, stroke_dasharray="6 4", opacity=0)
        ray_f.append(ray)

    lamp_f, lamp_d = [], []
    for panel, store in (("F", lamp_f), ("D", lamp_d)):
        scene.Text(root, PANEL_X[panel], 324, "ライト", size=17)
        for i, light in enumerate(LIGHTS):
            color = Hex([v * 255 for v in light["rgb"]])
            store.append(root.add("circle", cx=PANEL_X[panel] + 74 + i * 36, cy=318, r=11, fill=color, stroke="#1f2937", stroke_width=1.5, opacity=0.22))

    caption_items_f1 = []

    for k in range(SPHERE_COUNT):
        t0 = forward_start + k * forward_slot
        sx, sy, r = spheres[k]
        gf = groups["F"][k]
        newly_overwritten = [c for c in cover[k] if c in covered]
        forward_waste_count += len(newly_overwritten) * lights_n
        if newly_overwritten:
            forward_waste.append((t0, forward_waste_count))
        scene.Note(t0, "Forward", "物体 %d を描く:%d マス(うち %d マスは前の物体を上書き)" % (k + 1, len(cover[k]), len(newly_overwritten)))
        cells_g = gf.add("g", clip_path="url(#fd-sph-F%d)" % k)
        for (x, y) in cover[k]:
            colors, _, dists = shade[(k, x, y)]
            rect = cells_g.add("rect", x=R(Px("F", x)), y=R(Py(y)), width=R(CELL + 0.3), height=R(CELL + 0.3), fill="none")
            items = [(t0, colors[0])]
            for i in range(lights_n):
                th = t0 + hit_offset + hit_step * i + stagger * min(1.0, dists[i] / LIGHT_RANGE)
                items.append((th, colors[i + 1]))
            rect.Steps("fill", items)
        if newly_overwritten:
            frame = cells_g.add("g", opacity=0)
            frame.Show(t0, t0 + forward_slot - 0.02)
            for (x, y) in newly_overwritten:
                frame.add("rect", x=R(Px("F", x)), y=R(Py(y)), width=R(CELL), height=R(CELL), fill="none", stroke=RED, stroke_width=1.2)
        for (x, y) in cover[k]:
            covered.add((x, y))
        outline = gf.add("circle", cx=R(Px("F", sx)), cy=R(Py(sy)), r=R((r + 0.3) * CELL), fill="none", stroke="#1e293b", stroke_width=2, opacity=0)
        outline.Set(t0, "opacity", 1)
        shade_ball = gf.add("circle", cx=R(Px("F", sx)), cy=R(Py(sy)), r=R((r + 0.3) * CELL), fill="url(#fd-sphere)", opacity=0)
        shade_ball.Set(t0 + hit_offset + hit_step * lights_n, "opacity", 1)
        badge = gf.add("circle", cx=R(Px("F", sx)), cy=R(Py(sy)), r=11, fill="#ffffff", stroke="#334155", stroke_width=1.5, opacity=0)
        badge.Set(t0, "opacity", 1)
        label = scene.Text(gf, R(Px("F", sx)), R(Py(sy)) + 5, str(k + 1), size=14, anchor="middle", opacity=0)
        label.Set(t0, "opacity", 1)
        for i, light in enumerate(LIGHTS):
            th = t0 + hit_offset + hit_step * i
            forward_count += len(cover[k])
            forward_counter.append((th, forward_count))
            ray = ray_f[i]
            ray.Set(th, "x2", R(Px("F", sx)))
            ray.Set(th, "y2", R(Py(sy)))
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
    scene.Text(box, PANEL_X["F"] + 16, 428, "物体%d × ライト%d = %d回の描画" % (SPHERE_COUNT, lights_n, SPHERE_COUNT * lights_n), size=17, fill="#1e3a8a")
    scene.Text(box, PANEL_X["F"] + 16, 458, "ピクセル計算 %s マス × ライト%d = %s回" % ("{:,}".format(flat_total), lights_n, "{:,}".format(forward_total)), size=17, fill="#1e3a8a")
    scene.Text(box, PANEL_X["F"] + 16, 490, "隠れて見えない部分も計算:無駄 約%d%%" % pct, size=19, fill=RED)
    scene.Text(box, PANEL_X["F"] + 16, 514, "(重なったマスの計算は、あとで上書きされて捨てられる)", size=13, weight=500, fill="#64748b")
    scene.Note(forward_result_t, "Forward", "結果ボックス:計算 %s 回、無駄 %d%%(最終カウンター %s / 無駄 %s)" % ("{:,}".format(forward_total), pct, "{:,}".format(forward_total), "{:,}".format(forward_waste_count)))

    deferred_counter = []
    deferred_count = 0
    for k in range(SPHERE_COUNT):
        t0 = pass1_start + k * pass1_slot
        sx, sy, r = spheres[k]
        gd = groups["D"][k]
        scene.Note(t0, "Deferred", "Pass 1:物体 %d を G-Buffer に書く(%d マス)" % (k + 1, len(cover[k])))
        clip_g = gd.add("g", clip_path="url(#fd-sph-D%d)" % k)
        stripes = clip_g.add("g", opacity=0)
        stripes.Set(t0, "opacity", 1)
        lit_g = clip_g.add("g")
        w3 = CELL / 3.0
        depth_value = 255.0 * max(0.1, min(0.95, 0.12 + 0.75 * (1.0 - (k + 1) / (SPHERE_COUNT + 1.0))))
        depth_color = Hex([depth_value] * 3)
        for (x, y) in cover[k]:
            colors, stripe_normal, _ = shade[(k, x, y)]
            ox, oy = Px("D", x), Py(y)
            stripes.add("rect", x=R(ox), y=R(oy), width=R(w3 + 0.2), height=R(CELL + 0.3), fill="#ffffff")
            stripes.add("rect", x=R(ox + w3), y=R(oy), width=R(w3 + 0.2), height=R(CELL + 0.3), fill=stripe_normal)
            stripes.add("rect", x=R(ox + 2 * w3), y=R(oy), width=R(w3 + 0.2), height=R(CELL + 0.3), fill=depth_color)
            if owner[(x, y)] == k:
                lit = lit_g.add("rect", x=R(ox), y=R(oy), width=R(CELL + 0.3), height=R(CELL + 0.3), fill="none")
                items = []
                for i in range(lights_n):
                    s_i = pass2_start + pass2_slot * i
                    tc = s_i + wave_len * (x + y + 1) / diag
                    items.append((tc, colors[i + 1]))
                lit.Steps("fill", items)
        outline = gd.add("circle", cx=R(Px("D", sx)), cy=R(Py(sy)), r=R((r + 0.3) * CELL), fill="none", stroke="#1e293b", stroke_width=2, opacity=0)
        outline.Set(t0, "opacity", 1)
        badge = gd.add("circle", cx=R(Px("D", sx)), cy=R(Py(sy)), r=11, fill="#ffffff", stroke="#334155", stroke_width=1.5, opacity=0)
        badge.Set(t0, "opacity", 1)
        label = scene.Text(gd, R(Px("D", sx)), R(Py(sy)) + 5, str(k + 1), size=14, anchor="middle", opacity=0)
        label.Set(t0, "opacity", 1)
        shade_ball = gd.add("circle", cx=R(Px("D", sx)), cy=R(Py(sy)), r=R((r + 0.3) * CELL), fill="url(#fd-sphere)", opacity=0)
        shade_ball.Set(pass2_start + pass2_slot * lights_n - 0.05, "opacity", 1)

    caption_d = []
    for k in range(SPHERE_COUNT):
        t0 = pass1_start + k * pass1_slot
        t1 = pass1_start + (k + 1) * pass1_slot if k < SPHERE_COUNT - 1 else pass2_start
        caption_d.append((t0, t1, "① Pass 1:物体を G-Buffer に書く(%d/%d)" % (k + 1, SPHERE_COUNT)))
    for i in range(lights_n):
        s_i = pass2_start + pass2_slot * i
        t1 = s_i + pass2_slot if i < lights_n - 1 else deferred_result_t
        caption_d.append((s_i, t1, "② Pass 2:絵のあるピクセルにライトを1つずつ(%d/%d)" % (i + 1, lights_n)))
    scene.TextStack(root, PANEL_X["D"], 412, caption_d, size=15, fill=TEXT)
    sub_d = [(pass1_start, pass2_start, "1マスに 色 | 法線 | 深度 の3種類を保存"),
             (pass2_start, deferred_result_t, "物体の数に関係なく、画面を1回なぞる × %d ライト" % lights_n)]
    scene.TextStack(root, PANEL_X["D"], 436, sub_d, size=15, fill="#7c3aed")

    group_total = 8
    group_count = {}
    for (gx, gy) in owner:
        gidx = (gx + gy) * group_total // diag
        group_count[gidx] = group_count.get(gidx, 0) + 1
    for i, light in enumerate(LIGHTS):
        line = root.add("line", x1=PANEL_X["D"], y1=GRID_TOP, x2=PANEL_X["D"], y2=R(GRID_TOP + GRID_Y * CELL), stroke=Hex([v * 255 for v in light["rgb"]]),
                        stroke_width=5, opacity=0, clip_path="url(#fd-clip-d)")
        s_i = pass2_start + pass2_slot * i
        line.Set(s_i, "opacity", 0.9)
        line.Set(s_i, "x1", R(Px("D", 0)))
        line.Set(s_i, "x2", R(Px("D", -GRID_Y)))
        line.Ramp(s_i, s_i + wave_len, "x1", R(Px("D", GRID_X + GRID_Y)))
        line.Ramp(s_i, s_i + wave_len, "x2", R(Px("D", GRID_X)))
        line.Set(s_i + wave_len + 0.01, "opacity", 0)
        lamp_d[i].Set(s_i, "opacity", 1)
        lamp_d[i].Set(s_i + pass2_slot, "opacity", 0.22)
        scene.Note(s_i, "Deferred", "Pass 2:ライト %s が画面 %s マスをなぞる(ここまで %s 回)" % (light["name"], "{:,}".format(visible_total), "{:,}".format((i + 1) * visible_total)))
        for gidx in sorted(group_count):
            tt = s_i + wave_len * ((gidx + 0.5) / group_total)
            deferred_count += group_count[gidx]
            deferred_counter.append((tt, deferred_count))
    deferred_total = deferred_count
    assert deferred_total == visible_total * lights_n

    scene.Text(root, PANEL_X["D"], 358, "ピクセル計算:", size=20)
    scene.Counter(root, PANEL_X["D"] + 130, 360, deferred_counter, size=26)
    scene.TextStack(root, PANEL_X["D"], 388, [(pass1_start, pass2_start, "いまは材質を貯めているだけ(光の計算はまだ 0)"),
                                              (pass2_start, deferred_result_t, "光の計算は画面のマス数(%s)が上限" % "{:,}".format(GRID_X * GRID_Y))], size=15, weight=500, fill="#64748b")

    box = root.add("g", opacity=0)
    box.Show(deferred_result_t)
    box.add("rect", x=PANEL_X["D"], y=398, width=416, height=128, rx=12, fill="#f5f3ff", stroke="#7c3aed", stroke_width=2.5)
    scene.Text(box, PANEL_X["D"] + 16, 428, "③ ライティングは画面ピクセルごとに1回", size=19, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 458, "%s px × ライト%d = %s回" % ("{:,}".format(visible_total), lights_n, "{:,}".format(deferred_total)), size=17, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 490, "物体が%d個でも100個でも、最大 %s px × %d まで" % (SPHERE_COUNT, "{:,}".format(GRID_X * GRID_Y), lights_n), size=16, fill="#4c1d95")
    scene.Text(box, PANEL_X["D"] + 16, 514, "(代わりに G-Buffer の書き込みと読み込みが増える)", size=13, weight=500, fill="#64748b")
    scene.Note(deferred_result_t, "Deferred", "結果ボックス:計算 %s 回" % "{:,}".format(deferred_total))

    for panel in ("F", "D"):
        g = root.add("g", opacity=0.25)
        for i in range(1, GRID_X):
            g.add("line", x1=R(Px(panel, i)), y1=GRID_TOP, x2=R(Px(panel, i)), y2=R(Py(GRID_Y)), stroke="#ffffff", stroke_width=0.5)
        for j in range(1, GRID_Y):
            g.add("line", x1=PANEL_X[panel], y1=R(Py(j)), x2=R(Px(panel, GRID_X)), y2=R(Py(j)), stroke="#ffffff", stroke_width=0.5)
        g.add("rect", x=PANEL_X[panel], y=GRID_TOP, width=GRID_PIXELS, height=R(GRID_Y * CELL), fill="none", stroke="#94a3b8", stroke_width=1.5)

    for panel in ("F", "D"):
        for i, light in enumerate(LIGHTS):
            color = Hex([v * 255 for v in light["rgb"]])
            lx, ly = light["pos"]
            root.add("circle", cx=R(Px(panel, lx)), cy=R(Py(ly)), r=15, fill=color, opacity=0.28)
            root.add("circle", cx=R(Px(panel, lx)), cy=R(Py(ly)), r=7, fill=color, stroke="#ffffff", stroke_width=2.5)
    root.add("circle", cx=480, cy=180, r=24, fill="#1f2937")
    scene.Text(root, 480, 188, "VS", size=22, fill="#ffffff", anchor="middle")

    scene.Note(0.0, "共通", "球体 %d 個(同じ配置、最初は全部白)、ライト %d 個(色付き)、画面 %d×%d = %s マス" % (SPHERE_COUNT, lights_n, GRID_X, GRID_Y, "{:,}".format(GRID_X * GRID_Y)))
    scene.Note(DURATION, "共通", "動きの終わり。以降 %.1f 秒は静止してからループ" % HOLD)
    return scene, spheres, cover


def Main():
    scene, spheres, cover = Build()
    svg = scene.Render()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    io.open(os.path.join(out_dir, "forward_deferred.svg"), "w", encoding="utf-8", newline="").write(svg)
    io.open(os.path.join(out_dir, "forward_deferred.report.txt"), "w", encoding="utf-8").write(scene.Report() + "\n")
    print("svg bytes", len(svg.encode("utf-8")), "animate", svg.count("<animate"))
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
