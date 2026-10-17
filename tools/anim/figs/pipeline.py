import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Caption, Hex, Lerp, Mix, NewScene, R, Smooth)  # noqa: E402


def Timeline(scene, parent, x, y, items, end, size=14, fill=INK, weight=700, anchor="start"):
    stack = []
    for i, (t, text) in enumerate(items):
        t1 = items[i + 1][0] if i + 1 < len(items) else end
        stack.append((t, t1, text))
    return scene.TextStack(parent, x, y, stack, size=size, fill=fill, weight=weight, anchor=anchor)


def Rasterize():
    name = "raster-sweep"
    cols, rows, cell = 20, 12, 28
    ox, oy = 20, 56
    tri = [(3.2, 10.2), (16.5, 7.4), (8.6, 1.6)]

    def Edge(a, b, p):
        return (p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])

    def Inside(p):
        e = [Edge(tri[i], tri[(i + 1) % 3], p) for i in range(3)]
        return all(v >= 0 for v in e) or all(v <= 0 for v in e)

    scene = NewScene(name, 780, 450, duration=9.6, hold=1.5, title="ラスタライズ:ピクセルの中心が三角形の内側かを、1 つずつ調べる")
    root = scene.root
    root.add("rect", x=ox, y=oy, width=cols * cell, height=rows * cell, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    for i in range(1, cols):
        root.add("line", x1=ox + i * cell, y1=oy, x2=ox + i * cell, y2=oy + rows * cell, stroke=LIGHT, stroke_width=1)
    for j in range(1, rows):
        root.add("line", x1=ox, y1=oy + j * cell, x2=ox + cols * cell, y2=oy + j * cell, stroke=LIGHT, stroke_width=1)
    t_start, t_step = 0.8, 0.026
    total = cols * rows
    inside_cells = []
    for idx in range(total):
        y, x = divmod(idx, cols)
        t = t_start + idx * t_step
        if Inside((x + 0.5, y + 0.5)):
            inside_cells.append((x, y, t))
            rect = root.add("rect", x=ox + x * cell + 1, y=oy + y * cell + 1, width=cell - 2, height=cell - 2, fill=BLUE, opacity=0)
            rect.Set(t, "opacity", 0.75)
    root.add("polygon", points=" ".join("%s,%s" % (R(ox + p[0] * cell), R(oy + p[1] * cell)) for p in tri), fill="none", stroke=RED, stroke_width=3)
    for idx in range(total):
        y, x = divmod(idx, cols)
        t = t_start + idx * t_step
        dot = root.add("circle", cx=ox + (x + 0.5) * cell, cy=oy + (y + 0.5) * cell, r=3, fill="#94a3b8")
        if Inside((x + 0.5, y + 0.5)):
            dot.Set(t, "fill", "#ffffff")
    ring = root.add("circle", cx=ox + 0.5 * cell, cy=oy + 0.5 * cell, r=9, fill="none", stroke=AMBER, stroke_width=3, opacity=0)
    ring.Steps("cx", [(t_start + i * t_step, R(ox + (i % cols + 0.5) * cell)) for i in range(total)])
    ring.Steps("cy", [(t_start + i * t_step, R(oy + (i // cols + 0.5) * cell)) for i in range(total)])
    ring.Set(t_start, "opacity", 1)
    ring.Set(t_start + total * t_step, "opacity", 0)
    counts = []
    inside_n = 0
    for y in range(rows):
        inside_n += sum(1 for (cx, cy, _) in inside_cells if cy == y)
        counts.append((t_start + (y * cols + cols - 1) * t_step, (y + 1) * cols, inside_n))
    px = 620
    scene.Text(root, px, 80, "調べたピクセル", size=14, fill=GRAY)
    scene.Counter(root, px, 112, [(t, tested) for t, tested, _ in counts], size=30, start_value=0)
    scene.Text(root, px, 160, "内側（塗る）", size=14, fill=BLUE)
    scene.Counter(root, px, 192, [(t, ins) for t, _, ins in counts], size=30, fill=BLUE, start_value=0)
    scene.Text(root, px, 232, "外側（塗らない）", size=14, fill=GRAY)
    scene.Counter(root, px, 264, [(t, tested - ins) for t, tested, ins in counts], size=30, fill=GRAY, start_value=0)
    end_t = t_start + total * t_step
    Caption(scene, 20, 420, [(0.0, end_t + 0.1, "白い点 = ピクセルの中心。内側なら青く塗り、外側なら塗らない"),
                             (end_t + 0.1, 20, "内側の %d 個が、このあとピクセルシェーダーで色を計算される" % inside_n)], size=15)
    scene.Note(t_start, "ラスタ", "格子 %d×%d の中心を左上から順に判定(1 個 %.3f 秒)" % (cols, rows, t_step))
    scene.Note(end_t, "ラスタ", "内側 %d / 全体 %d" % (inside_n, total))
    return dict(name=name, page="3d/render-flow/rasterize.md", before="## 内側かどうかの判定（辺の式）", scene=scene, size=(780, 450), times=[1.5, 3.5, 6.0, 9.0])


def DepthTest():
    name = "depth-test-order"
    cells = 10
    cw = 30
    scene = NewScene(name, 780, 440, duration=10.0, hold=1.5, title="深度テスト:描く順番を変えても、手前の物が勝つ")
    root = scene.root
    A = dict(cells=range(1, 7), depth=0.8, color="#e5484d", label="A（奥 0.8）")
    B = dict(cells=range(4, 10), depth=0.3, color="#2563eb", label="B（手前 0.3）")
    panels = [(20, [A, B], "① A → B の順に描く", 0.8), (400, [B, A], "② B → A の順に描く", 0.8)]
    for px, order, title, t0 in panels:
        scene.Text(root, px, 66, title, size=16, fill=INK)
        scene.Text(root, px, 118, "色", size=13, fill=GRAY)
        scene.Text(root, px, 188, "深度", size=13, fill=GRAY)
        base_x = px + 36
        color_cells, depth_cells = [], []
        for c in range(cells):
            color_cells.append(root.add("rect", x=base_x + c * cw, y=96, width=cw - 2, height=34, fill="#f1f5f9", stroke="#cbd5e1", stroke_width=1))
            root.add("rect", x=base_x + c * cw, y=166, width=cw - 2, height=34, fill="#ffffff", stroke="#cbd5e1", stroke_width=1)
        states = {c: (None, 1.0) for c in range(cells)}
        events = []
        t = t0
        for obj in order:
            scene.Note(t, name, "%s を描く(%s)" % (obj["label"], title))
            events.append((t, "title", obj))
            t += 0.55
            for c in obj["cells"]:
                cur_color, cur_depth = states[c]
                passed = obj["depth"] < cur_depth
                events.append((t, "test", (c, obj, passed, cur_depth)))
                if passed:
                    states[c] = (obj["color"], obj["depth"])
                t += 0.28
            t += 0.5
        final_t = t
        depth_values = {c: [(0.0, "1.0")] for c in range(cells)}
        color_steps = {c: [] for c in range(cells)}
        marker_x, verdicts = [], []
        for (te, kind, data) in events:
            if kind == "test":
                c, obj, passed, cur_depth = data
                if passed:
                    depth_values[c].append((te, "%.1f" % obj["depth"]))
                    color_steps[c].append((te, obj["color"]))
                marker_x.append((te, R(base_x + c * cw + (cw - 2) / 2)))
                verdicts.append((te, "%s:%.1f %s %.1f → %s" % (obj["label"][0], obj["depth"], "<" if passed else "≧", cur_depth, "書く" if passed else "捨てる")))
        for c in range(cells):
            if color_steps[c]:
                color_cells[c].Steps("fill", color_steps[c])
            for i, (tv, txt) in enumerate(depth_values[c]):
                t_end = depth_values[c][i + 1][0] if i + 1 < len(depth_values[c]) else 20
                scene.TextStack(root, base_x + c * cw + (cw - 2) / 2, 189, [(tv if i else 0.0, t_end, txt)], size=13, fill=INK, anchor="middle")
        mk = root.add("polygon", points="0,0 -7,-12 7,-12", fill=AMBER, opacity=0)
        xs = [(te, x) for te, x in marker_x]
        mk.Steps("points", [(te, "%s,%s %s,%s %s,%s" % (x, 94, x - 7, 82, x + 7, 82)) for te, x in xs])
        mk.Set(xs[0][0], "opacity", 1)
        mk.Set(final_t - 0.3, "opacity", 0)
        verdict_items = [(te, te + 0.28, txt) for te, txt in verdicts]
        scene.TextStack(root, px, 240, verdict_items, size=14, fill=RED, anchor="start")
        scene.TextStack(root, px, 268, [(final_t, 20, "結果:重なった所（4〜6）は、手前の B が残る")], size=14, fill=GREEN)
    Caption(scene, 30, 330, [(0.0, 20, "各ピクセルで「今の深度 < 記録された深度」なら書く。奥の物は、すでに手前が描かれていれば捨てられる。")], size=14, weight=500, fill=GRAY)
    Caption(scene, 30, 354, [(0.0, 20, "→ どちらの順でも、最終的な絵は同じ。ただし ② は A の計算が無駄になる（手前から描くと速い理由）。")], size=14, weight=500, fill=GRAY)
    return dict(name=name, page="3d/render-flow/output-merger.md", before="### 深度バッファの中身", scene=scene, size=(780, 440), times=[2.0, 4.5, 7.0, 10.0])


def Perspective():
    name = "perspective-divide-move"
    scene = NewScene(name, 780, 410, duration=9.0, hold=1.5, title="透視除算:遠ざかるほど w が大きくなり、画面上で小さくなる")
    root = scene.root
    cam = (150, 330)
    root.add("polygon", points="150,330 40,60 260,60", fill="#e0f2fe", stroke="#38bdf8", stroke_width=1.5)
    root.add("circle", cx=cam[0], cy=cam[1], r=7, fill=RED)
    scene.Text(root, 164, 346, "カメラ", size=12, fill=GRAY)
    scene.Text(root, 40, 52, "視錐台（上から見た図）", size=12, fill=GRAY)
    box = root.add("rect", x=130, y=290, width=40, height=14, fill=AMBER, stroke=INK, stroke_width=1.5)
    sx, sy, sw, sh = 440, 70, 260, 260
    root.add("rect", x=sx, y=sy, width=sw, height=sh, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
    scene.Text(root, sx, sy - 8, "画面", size=12, fill=GRAY)
    obj = root.add("rect", x=sx + sw / 2 - 90, y=sy + sh / 2 - 90, width=180, height=180, fill=AMBER, stroke=INK, stroke_width=2)
    z0, z1, t0, t1 = 1.0, 9.0, 0.8, 7.0
    steps = 28
    items = []
    for i in range(steps + 1):
        f = i / steps
        z = Lerp(z0, z1, f)
        t = Lerp(t0, t1, f)
        y = 330 - 24 - (z - 1) * 28
        half = 90 / z
        if i == 0:
            obj.Set(t, "x", R(sx + sw / 2 - half)); obj.Set(t, "y", R(sy + sh / 2 - half)); obj.Set(t, "width", R(2 * half)); obj.Set(t, "height", R(2 * half)); box.Set(t, "y", R(y))
        else:
            obj.Ramp(tp, t, "x", R(sx + sw / 2 - half)); obj.Ramp(tp, t, "y", R(sy + sh / 2 - half)); obj.Ramp(tp, t, "width", R(2 * half)); obj.Ramp(tp, t, "height", R(2 * half)); box.Ramp(tp, t, "y", R(y))
        tp = t
    zs = [1, 2, 3, 4, 6, 9]
    lines = []
    for z in zs:
        f = (z - z0) / (z1 - z0)
        lines.append((Lerp(t0, t1, f), "w = %d  →  画面上の大きさ = 1 / %d = %.2f 倍" % (z, z, 1.0 / z)))
    Timeline(scene, root, 20, 384, lines, 20, size=16, fill=INK)
    scene.Text(root, 440, 350, "x / w, y / w で割るので、遠い物ほど小さい", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "箱が z=1 から z=9 へ遠ざかる(w=z)")
    return dict(name=name, page="3d/render-flow/vertex-stage.md", before="## 頂点シェーダーでできること", scene=scene, size=(780, 410), times=[1.0, 3.0, 5.0, 7.5])


def FramePasses():
    name = "frame-build-up"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="1 フレームが、パスごとに完成していく")
    root = scene.root
    sx, sy, sw, sh = 20, 52, 420, 280
    root.add("rect", x=sx, y=sy, width=sw, height=sh, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    clip = scene.defs.add("clipPath", id="fp-clip")
    clip.add("rect", x=sx, y=sy, width=sw, height=sh)
    grad = scene.defs.add("linearGradient", id="fp-sky", x1="0", y1="0", x2="0", y2="1")
    grad.add("stop", offset="0", stop_color="#4f9cf0")
    grad.add("stop", offset="1", stop_color="#cfe8ff")
    sph = scene.defs.add("radialGradient", id="fp-ball", cx="0.5", cy="0.5", r="0.5", fx="0.35", fy="0.3")
    sph.add("stop", offset="0", stop_color="#ffffff")
    sph.add("stop", offset="1", stop_color="#e5484d")
    glow = scene.defs.add("radialGradient", id="fp-glow", cx="0.5", cy="0.5", r="0.5")
    glow.add("stop", offset="0", stop_color="#fff3b0", stop_opacity="0.95")
    glow.add("stop", offset="1", stop_color="#fff3b0", stop_opacity="0")
    vig = scene.defs.add("radialGradient", id="fp-vig", cx="0.5", cy="0.5", r="0.75")
    vig.add("stop", offset="0.6", stop_color="#000000", stop_opacity="0")
    vig.add("stop", offset="1", stop_color="#000000", stop_opacity="0.45")
    g = root.add("g", clip_path="url(#fp-clip)")
    pass_t = [0.8 + i * 1.5 for i in range(6)]
    names = ["① シャドウ", "② 不透明", "③ 空", "④ 半透明", "⑤ ポスト", "⑥ UI"]
    details = ["光から見た深度を描く", "地面・箱・球（影を読む）", "最奥のピクセルだけに空", "ガラスを奥から手前へ", "ブルーム・トーンマップ", "HP バーと文字"]

    def Layer(opacity_to=1.0, t=0.0):
        n = g.add("g", opacity=0)
        n.Set(t, "opacity", opacity_to)
        return n

    sky = Layer(1, pass_t[2])
    sky.add("rect", x=sx, y=sy, width=sw, height=170, fill="url(#fp-sky)")
    sky.add("circle", cx=sx + 330, cy=sy + 55, r=18, fill="#fff3b0")
    op = Layer(1, pass_t[1])
    op.add("rect", x=sx, y=sy + 170, width=sw, height=110, fill="#7aa874")
    op.add("polygon", points="%d,%d %d,%d %d,%d %d,%d" % (sx + 110, sy + 230, sx + 205, sy + 230, sx + 245, sy + 250, sx + 150, sy + 250), fill="#3f5d3a", opacity="0.55")
    op.add("rect", x=sx + 90, y=sy + 150, width=70, height=80, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    op.add("circle", cx=sx + 270, cy=sy + 215, r=38, fill="url(#fp-ball)")
    sh_layer = Layer(1, pass_t[0])
    sh_layer.add("rect", x=sx + 300, y=sy + 8, width=110, height=70, fill="#334155", stroke="#94a3b8", stroke_width=1.5)
    sh_layer.add("rect", x=sx + 320, y=sy + 26, width=36, height=34, fill="#cbd5e1")
    sh_layer.add("rect", x=sx + 365, y=sy + 40, width=28, height=20, fill="#94a3b8")
    scene.Text(sh_layer, sx + 304, sy + 90, "シャドウ マップ", size=11, weight=500, fill=GRAY)
    gl = Layer(1, pass_t[3])
    gl.add("rect", x=sx + 190, y=sy + 120, width=110, height=140, fill="#7dd3fc", opacity=0.45, stroke="#0ea5e9", stroke_width=2)
    post = Layer(1, pass_t[4])
    post.add("circle", cx=sx + 330, cy=sy + 55, r=70, fill="url(#fp-glow)")
    post.add("rect", x=sx, y=sy, width=sw, height=sh, fill="url(#fp-vig)")
    ui = Layer(1, pass_t[5])
    ui.add("rect", x=sx + 14, y=sy + 14, width=130, height=14, fill="#1f2937", opacity=0.75)
    ui.add("rect", x=sx + 16, y=sy + 16, width=96, height=10, fill="#2ea043")
    scene.Text(ui, sx + 14, sy + 46, "HP 74 / 100", size=13, fill="#ffffff")
    ui.children[-1].attrs["style"] += ";stroke:#1f2937;stroke-width:3px;paint-order:stroke"
    lx = 470
    for i in range(6):
        y = 64 + i * 46
        frame = root.add("rect", x=lx - 8, y=y - 22, width=314, height=40, rx=8, fill="#eff6ff", stroke=BLUE, stroke_width=2.5, opacity=0)
        frame.Show(pass_t[i], pass_t[i] + 1.5 if i < 5 else 20)
        scene.Text(root, lx, y, names[i], size=17, fill=INK)
        scene.Text(root, lx + 100, y, details[i], size=12, weight=500, fill=GRAY)
        mark = scene.Text(root, lx + 292, y, "✓", size=18, fill=GREEN, opacity=0)
        mark.Show(pass_t[i] + 1.2)
        scene.Note(pass_t[i], name, names[i] + " " + details[i])
    Caption(scene, 20, 366, [(0.0, pass_t[0], "まず白紙のフレームから"), (pass_t[0], pass_t[1], "① 光から見た深度（影の材料）を別の画像に描く"),
                             (pass_t[1], pass_t[2], "② 影を読みながら、不透明な物を描く"), (pass_t[2], pass_t[3], "③ 何も描かれていない最奥に空を描く"),
                             (pass_t[3], pass_t[4], "④ 半透明は最後に、奥から手前の順"), (pass_t[4], pass_t[5], "⑤ 全画面を加工（光のにじみ・周辺減光・明るさ調整）"),
                             (pass_t[5], 20, "⑥ UI は加工の後に上から描く → Present で画面へ")], size=15)
    return dict(name=name, page="3d/render-flow/frame-passes.md", before="## パスごとに変わるもの", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.5, 10.5])


def Present():
    name = "double-buffer-swap"
    scene = NewScene(name, 780, 360, duration=11.0, hold=1.5, title="Present:裏で描いて、完成したら表と入れ替える")
    root = scene.root
    bx, fx, dx_ = 40, 300, 560
    by, bw, bh = 90, 200, 130
    for x, label in ((bx, "バック バッファ"), (fx, "フロント バッファ")):
        root.add("rect", x=x, y=by, width=bw, height=bh, rx=8, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
        scene.Text(root, x, by - 10, label, size=15, fill=INK)
    root.add("rect", x=dx_, y=by - 12, width=180, height=bh + 12, rx=10, fill="#0f172a")
    scene.Text(root, dx_, by - 20, "ディスプレイ", size=15, fill=INK)
    scene.Text(root, dx_ + 96, by - 20, "（フロントを読む）", size=12, weight=500, fill=GRAY)
    screen = root.add("rect", x=dx_ + 10, y=by, width=160, height=bh - 16, fill="#cbd5e1")
    frame_colors = ["#e5aa28", "#2563eb", "#2ea043", "#9664e6"]

    draws = [(0.4, 2.6, 0), (4.0, 6.2, 1), (7.6, 9.8, 2)]
    swaps = [(3.0, 3.8), (6.6, 7.4), (10.2, 10.9)]
    screen_steps = [(s1, frame_colors[i]) for i, (s0, s1) in enumerate(swaps)]
    screen.Steps("fill", screen_steps)
    moving = []
    for i in range(3):
        d0, d1, _ = draws[i]
        s0, s1 = swaps[i]
        box = root.add("rect", x=bx + 10, y=by + 10, width=0, height=bh - 20, fill=frame_colors[i], opacity=0)
        box.Set(d0, "opacity", 1)
        box.Ramp(d0, d1, "width", bw - 20)
        box.Ramp(s0, s1, "x", fx + 10)
        box.Set(10.95 if i == 2 else swaps[i + 1][1] + 0.05, "opacity", 0)
        lab = scene.Text(root, bx + bw / 2, by + bh / 2 + 6, "フレーム %d" % (i + 1), size=18, fill="#ffffff", anchor="middle", opacity=0)
        lab.Set(d1, "opacity", 1)
        lab.Ramp(s0, s1, "x", fx + bw / 2)
        lab.Set(10.95 if i == 2 else swaps[i + 1][1] + 0.05, "opacity", 0)
        moving.append((box, lab))
        scene.Note(d0, name, "GPU が フレーム %d をバック バッファに描く" % (i + 1))
        scene.Note(s0, name, "Present:フレーム %d をフロントへ入れ替え" % (i + 1))
    Caption(scene, 40, 272, [(0.0, 0.4, "GPU の描画が始まる前"), (0.4, 2.6, "GPU が フレーム 1 を、見えない裏（バック）に描いている"),
                             (2.6, 3.0, "描き終わり"), (3.0, 3.8, "Present:バックとフロントを入れ替える"),
                             (3.8, 4.0, ""), (4.0, 6.2, "ディスプレイは フレーム 1 を表示しながら、裏で フレーム 2 を描く"),
                             (6.2, 6.6, "描き終わり"), (6.6, 7.4, "Present:入れ替え"), (7.4, 7.6, ""), (7.6, 9.8, "フレーム 2 を表示中。裏で フレーム 3 を描く"),
                             (9.8, 10.2, "描き終わり"), (10.2, 20, "Present:入れ替え → 途中の絵は一度も見えない")], size=15)
    Caption(scene, 40, 306, [(0.0, 20, "VSync あり:ディスプレイの更新の合間まで待ってから入れ替える（裂けない）。")], size=13, weight=500, fill=GRAY)
    Caption(scene, 40, 328, [(0.0, 20, "VSync なし:すぐ入れ替わるので、更新の途中で絵が変わり、画面が裂けることがある。")], size=13, weight=500, fill=GRAY)
    scan = root.add("rect", x=dx_ + 10, y=by, width=160, height=3, fill="#ef4444", opacity=0.85)
    for k in range(5):
        t0 = 0.4 + k * 2.2
        scan.Set(t0, "y", by)
        scan.Ramp(t0, t0 + 2.0, "y", by + bh - 19)
    return dict(name=name, page="3d/render-flow/present.md", before="## スワップチェーン", scene=scene, size=(780, 360), times=[1.5, 3.4, 5.0, 8.5])


FIGS = [Rasterize, DepthTest, Perspective, FramePasses, Present]
