import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

PAGE = "graphics/postprocess/"


def MotionBlurShutter():
    name = "motion-blur-shutter"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="シャッター角:露光の間に動いた分だけが、ブレになる")
    root = scene.root
    # 上:1 フレームの時間
    bx, by, bw = 60, 90, 640
    root.add("rect", x=bx, y=by, width=bw, height=24, fill=LIGHT, stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, bx, by - 10, "1 フレームの時間（左 = 始め、右 = 終わり）", size=13, fill=GRAY, weight=500)
    expo = root.add("rect", x=bx, y=by, width=0.0001, height=24, fill=AMBER)
    # 下:動く物体の軌跡
    ty = 230
    root.add("line", x1=bx, y1=ty + 30, x2=bx + bw, y2=ty + 30, stroke="#cbd5e1", stroke_width=2)
    speed_w = 480  # フレーム中に動く距離(px)
    n_ghost = 12
    ghosts = []
    for k in range(n_ghost + 1):
        f = k / n_ghost
        c = root.add("circle", cx=R(bx + 40 + f * speed_w), cy=ty, r=22, fill=BLUE, opacity=0)
        ghosts.append((c, f))
    ball = root.add("circle", cx=bx + 40, cy=ty, r=22, fill=INK, stroke="#ffffff", stroke_width=2)
    streak = root.add("rect", x=bx + 40, y=ty - 22, width=0.0001, height=44, fill=BLUE, fill_opacity=0.28)
    # 角度の推移: 0 → 180 → 360 → 180
    seq = [(0.8, 0.0), (2.0, 0.0), (4.5, 0.5), (6.0, 0.5), (8.5, 1.0), (9.5, 1.0), (11.5, 0.5)]
    for idx, (t, s) in enumerate(seq):
        if idx == 0:
            expo.Set(t, "width", 0.0001); streak.Set(t, "width", 0.0001)
        else:
            pt = seq[idx - 1][0]
            expo.Ramp(pt, t, "width", R(max(0.0001, s * bw)))
            streak.Ramp(pt, t, "width", R(max(0.0001, s * speed_w)))
        for c, f in ghosts:
            on = 1.0 if f <= s + 1e-9 else 0.0
            if idx == 0:
                c.Set(t, "opacity", on * 0.3) if on else None
            else:
                pt = seq[idx - 1][0]
                prev_s = seq[idx - 1][1]
                prev_on = 1.0 if f <= prev_s + 1e-9 else 0.0
                if on != prev_on:
                    # f が s を追い越す時刻
                    frac = (f - prev_s) / (s - prev_s) if s != prev_s else 1.0
                    tt = Lerp(pt, t, max(0.0, min(1.0, frac)))
                    c.Set(tt, "opacity", on * 0.3)
    angle = lambda s: int(round(s * 360))
    scene.TextStack(root, 60, 340, [(0.0, 2.0, "シャッター角 0°:ブレなし（球は 1 点）"), (2.0, 5.2, "ブレが伸びていく… シャッター角 180°（標準）"), (5.2, 7.0, "180°:露光 = フレームの半分。映画の標準"), (7.0, 9.5, "シャッター角 360°:最大。流れる長いブレ"), (9.5, 20, "180° に戻す")], size=17, fill=INK)
    scene.TextStack(root, 60, 368, [(0.0, 20, "ブレの長さ ＝ 速さ × 露光の長さ（シャッターが開いている間に動いた距離）")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "シャッター角 0 → 180 → 360 → 180")
    return dict(name=name, page=PAGE + "motion-blur/index.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.5, 9.0])


def ObjectBlurRotation():
    name = "object-blur-rotation"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="回転する物体:中心は動かず、外側ほど速い ＝ ブレも長い")
    root = scene.root
    cx, cy, R0 = 200, 210, 120
    panels = [(200, "速度ベクトル（画素ごと）"), (580, "結果のブレ")]
    for px, title in panels:
        scene.Text(root, px, 70, title, size=14, fill=GRAY, anchor="middle")
        root.add("circle", cx=px, cy=cy, r=R0, fill="#f1f5f9", stroke="#94a3b8", stroke_width=2)
    # 左:速度ベクトル(接線方向、長さ ∝ 半径)
    for k, (r, col) in enumerate(((30, GREEN), (70, AMBER), (110, RED))):
        for ang in (0, 120, 240):
            a = math.radians(ang + 20 * k)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            L = r * 0.55
            tx, ty = -math.sin(a), math.cos(a)
            g = root.add("g", opacity=0)
            g.Show(1.0 + k * 1.2)
            g.add("circle", cx=R(x), cy=R(y), r=4, fill=col)
            g.add("line", x1=R(x), y1=R(y), x2=R(x + tx * L), y2=R(y + ty * L), stroke=col, stroke_width=3)
            g.add("polygon", points="%s,%s %s,%s %s,%s" % (R(x + tx * L), R(y + ty * L), R(x + tx * (L - 9) - ty * 5), R(y + ty * (L - 9) + tx * 5), R(x + tx * (L - 9) + ty * 5), R(y + ty * (L - 9) - tx * 5)), fill=col)
    # 右:ブレの結果(スポークの扇)
    px = 580
    fan = root.add("g", opacity=0)
    fan.Show(5.0)
    for i in range(14):
        a0 = math.radians(-8 + i * 2.4)
        for s in range(4):
            a = a0 + math.radians(90 * s)
            fan.add("line", x1=px, y1=cy, x2=R(px + R0 * math.cos(a)), y2=R(cy + R0 * math.sin(a)), stroke=INK, stroke_width=3, opacity=0.1)
    sharp = root.add("g", opacity=1)
    sharp.Set(5.0, "opacity", 0)
    for s in range(4):
        a = math.radians(90 * s)
        sharp.add("line", x1=px, y1=cy, x2=R(px + R0 * math.cos(a)), y2=R(cy + R0 * math.sin(a)), stroke=INK, stroke_width=4)
    root.add("circle", cx=px, cy=cy, r=14, fill=INK)
    scene.TextStack(root, 40, 372, [(0.0, 1.0, "ホイールが回っている"), (1.0, 5.0, "速度 ＝ 角速度 × 中心からの距離。外側ほど矢印が長い"), (5.0, 20, "→ 中心はくっきり、外縁ほど長くブレる（物体の速度バッファで表現）")], size=15, fill=INK)
    scene.Note(1.0, name, "速度ベクトル → ブレ")
    return dict(name=name, page=PAGE + "motion-blur/object-blur.md", scene=scene, size=(780, 400), times=[1.5, 3.0, 4.5, 8.0])


def MotionBlurJitter():
    name = "motion-blur-jitter"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="ジッター:サンプル位置を毎フレームずらして、縞を細かいノイズに変える")
    root = scene.root
    rnd = random.Random(3)
    N, x0, x1 = 6, 80, 560
    rows = [(110, "① サンプル固定（6 点）:6 個の像に分かれる（縞）"), (220, "② 毎フレームずらす:ノイズ（フレームごとに変わる）"), (330, "③ ② を数フレーム平均（TAA）:なめらかな筋")]
    for y, title in rows:
        scene.Text(root, 40, y - 36, title, size=14, fill=INK)
        root.add("line", x1=x0 - 30, y1=y + 22, x2=x1 + 30, y2=y + 22, stroke="#e2e8f0", stroke_width=2)
    seg = (x1 - x0) / N
    # 1
    for k in range(N):
        c = root.add("circle", cx=R(x0 + (k + 0.5) * seg), cy=110, r=12, fill=BLUE, opacity=0)
        c.Show(1.0 + k * 0.2)
    # 2
    frames = 8
    t0, dt = 3.0, 1.1
    dots2 = []
    allpos = []
    for f in range(frames):
        allpos.append([x0 + (k + rnd.random()) * seg for k in range(N)])
    for k in range(N):
        c = root.add("circle", cx=R(allpos[0][k]), cy=220, r=12, fill=BLUE, opacity=0)
        c.Steps("cx", [(t0 + f * dt, R(allpos[f][k])) for f in range(frames)])
        c.Show(t0, t0 + frames * dt)
    # 3
    for f in range(frames):
        for k in range(N):
            c = root.add("circle", cx=R(allpos[f][k]), cy=330, r=12, fill=BLUE, opacity=0)
            c.Set(t0 + f * dt, "opacity", R(0.55 / math.sqrt(f + 1) + 0.0))
    scene.TextStack(root, 600, 230, [(t0 + f * dt, t0 + (f + 1) * dt, "フレーム %d" % (f + 1)) for f in range(frames)], size=18, fill=INK)
    scene.TextStack(root, 600, 340, [(t0 + f * dt, t0 + (f + 1) * dt, "平均 %d 枚" % (f + 1)) for f in range(frames)], size=18, fill=BLUE)
    scene.Text(root, 40, 405, "サンプル数が少ないと「縞」になるが、ずらせば細かいノイズになり、時間で平均すると、なめらかな筋に見える。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "ジッターを 8 フレーム")
    return dict(name=name, page=PAGE + "motion-blur/blur-pass.md", scene=scene, size=(780, 420), times=[1.5, 4.0, 7.0, 12.0])


def MotionBlurVsTaa():
    name = "motion-blur-vs-taa"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ブラーのノイズは、TAA が平均して消す")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 340, 200, 16.0, 1.0, "フレーム数", "ノイズの量")
    curve = lambda k: 1.0 / math.sqrt(max(1.0, k))
    ax.Curve(curve, GREEN, 4, x0=1.0, x1=16.0, n=30)
    dot = root.add("circle", cx=ax.X(1), cy=ax.Y(1), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    t0, t1, n = 0.8, 9.6, 15
    prev = None
    for i in range(n):
        k = 1 + i
        t = Lerp(t0, t1, i / (n - 1))
        if i == 0:
            dot.Set(t, "cx", ax.X(k)); dot.Set(t, "cy", ax.Y(curve(k)))
        else:
            dot.Ramp(prev, t, "cx", ax.X(k)); dot.Ramp(prev, t, "cy", ax.Y(curve(k)))
        prev = t
    rnd = random.Random(11)
    cols, rows, cw, ch, ox, oy = 28, 5, 13, 20, 420, 80
    scene.Text(root, ox, oy - 12, "ブラーの結果（その時点の画素）", size=13, fill=GRAY)
    frames = n
    for j in range(rows):
        for i in range(cols):
            steps = []
            for k in range(frames):
                amp = 0.42 * curve(k + 1)
                steps.append((t0 + k * (t1 - t0) / (n - 1), Gray(0.5 + rnd.uniform(-1, 1) * amp)))
            r = root.add("rect", x=ox + i * cw, y=oy + j * ch, width=cw - 1, height=ch - 1, fill=Gray(0.5))
            r.Steps("fill", steps)
    LiveText(scene, root, 420, 230, t0, t1, n, lambda i, f: "TAA の履歴 %d フレーム分" % (i + 1), size=17, fill=INK)
    LiveText(scene, root, 420, 258, t0, t1, n, lambda i, f: "ノイズ ≒ %.0f %%" % (100 * curve(i + 1)), size=15, fill=GREEN)
    scene.TextStack(root, 50, 330, [(0.0, 20, "モーション ブラーは少ないサンプル（ノイズ）で作り、TAA の履歴の平均でなめらかにする。")], size=14, fill=INK, weight=500)
    scene.TextStack(root, 50, 356, [(0.0, 20, "ノイズ ∝ 1 / √(平均したフレーム数)。4 枚で半分、16 枚で 1/4。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "フレーム 1 → 15")
    return dict(name=name, page=PAGE + "motion-blur/strength-taa.md", scene=scene, size=(780, 400), times=[1.0, 3.0, 6.0, 9.5])


def CelRamp():
    name = "cel-ramp"
    scene = NewScene(name, 780, 400, duration=10.0, hold=1.5, title="セル シェーディング:なめらかな明るさを、数段に区切る")
    root = scene.root
    ax = Axes(scene, root, 50, 70, 320, 220, 1.0, 1.0, "N·L（光との向き）", "明るさ")
    smooth = lambda x: x
    steps = lambda x: 0.15 if x < 0.3 else (0.55 if x < 0.7 else 1.0)
    ax.Curve(smooth, GRAY, 3, n=20, dash="5 4")
    ax.Curve(steps, BLUE, 4, n=200)
    for th, label in ((0.3, "影"), (0.7, "中間")):
        root.add("line", x1=ax.X(th), y1=ax.y, x2=ax.X(th), y2=ax.y + ax.h, stroke=LIGHT, stroke_width=2, stroke_dasharray="4 3")
    scene.Text(root, ax.X(0.15), ax.Y(0.15) - 8, "影", size=12, fill=BLUE, anchor="middle")
    scene.Text(root, ax.X(0.5), ax.Y(0.55) - 8, "中間", size=12, fill=BLUE, anchor="middle")
    scene.Text(root, ax.X(0.85), ax.Y(1.0) + 16, "明", size=12, fill=BLUE, anchor="middle")
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    t0, t1, n = 0.8, 9.0, 40
    prev = None
    for i in range(n + 1):
        x = i / n
        t = Lerp(t0, t1, x)
        if i == 0:
            dot.Set(t, "cx", ax.X(x)); dot.Set(t, "cy", ax.Y(steps(x)))
        else:
            dot.Ramp(prev, t, "cx", ax.X(x)); dot.Ramp(prev, t, "cy", ax.Y(steps(x)))
        prev = t
    # 右:球に見立てた 2 列
    px = 430
    scene.Text(root, px, 70, "球の表面（暗い側 → 明るい側）", size=13, fill=GRAY)
    for row, (label, fn, y) in enumerate((("なめらか", smooth, 100), ("セル（3 段）", steps, 190))):
        scene.Text(root, px, y - 8, label, size=13, fill=INK)
        for k in range(16):
            x = (k + 0.5) / 16
            root.add("rect", x=px + k * 18, y=y, width=17, height=52, fill=Gray(fn(x)))
    mk = root.add("polygon", points="%s,%s %s,%s %s,%s" % (px + 8, 288, px + 1, 300, px + 15, 300), fill=RED)
    prev = None
    for i in range(n + 1):
        x = i / n
        t = Lerp(t0, t1, x)
        pts = "%s,%s %s,%s %s,%s" % (R(px + x * 288), 288, R(px + x * 288 - 7), 300, R(px + x * 288 + 7), 300)
        if i == 0:
            mk.Set(t, "points", pts)
        else:
            mk.Ramp(prev, t, "points", pts)
        prev = t
    out = root.add("rect", x=430, y=320, width=130, height=40, fill=Gray(0.15), stroke="#94a3b8", stroke_width=1.5)
    prev = None
    for i in range(n + 1):
        x = i / n
        t = Lerp(t0, t1, x)
        v = Gray(steps(x))
        if i == 0:
            out.Set(t, "fill", v)
        else:
            out.Ramp(prev, t, "fill", v)
        prev = t
    scene.Text(root, 570, 345, "← 今の明るさ（段でぱっと切り替わる）", size=12, fill=GRAY, weight=500)
    scene.TextStack(root, 50, 352, [(0.0, 20, "ランプ（表）を引くだけ。段の数・境目で画風が変わる")], size=12, fill=GRAY, weight=500)
    scene.Note(t0, name, "N·L を 0 → 1")
    return dict(name=name, page=PAGE + "stylized/cel-shading.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.0, 8.5])


def Sphere(scene, g, cx, cy, r, mode):
    """mode: 'smooth' | 'bands' | 'outline' | 'both' | 'flat'。"""
    clip = scene.defs.add("clipPath", id="ts-%s-%d" % (mode, cx))
    clip.add("circle", cx=cx, cy=cy, r=r)
    if mode == "flat":
        g.add("circle", cx=cx, cy=cy, r=r, fill="#9ca3af")
        return
    if mode in ("smooth", "both_unused"):
        gd = scene.defs.add("radialGradient", id="ts-grad-%d" % cx, cx=0.35, cy=0.3, r=0.85)
        gd.add("stop", offset=0, stop_color="#fff3c4")
        gd.add("stop", offset=0.5, stop_color="#f59e0b")
        gd.add("stop", offset=1, stop_color="#451a03")
        g.add("circle", cx=cx, cy=cy, r=r, fill="url(#ts-grad-%d)" % cx)
        return
    if mode in ("bands", "both"):
        grp = g.add("g", clip_path="url(#ts-%s-%d)" % (mode, cx))
        grp.add("circle", cx=cx, cy=cy, r=r, fill="#78350f")
        grp.add("circle", cx=cx - r * 0.18, cy=cy - r * 0.2, r=r * 0.95, fill="#d97706")
        grp.add("circle", cx=cx - r * 0.38, cy=cy - r * 0.42, r=r * 0.6, fill="#fcd34d")
        if mode == "both":
            g.add("circle", cx=cx, cy=cy, r=r, fill="none", stroke="#0b0b0b", stroke_width=6)
        return
    if mode == "outline":
        g.add("circle", cx=cx, cy=cy, r=r, fill="#ffffff", stroke="#0b0b0b", stroke_width=6)


def ToonStages():
    name = "toon-stages"
    scene = NewScene(name, 780, 360, duration=10.0, hold=1.5, title="トゥーンの 3 工程:陰影を段にして、輪郭線を足す")
    root = scene.root
    titles = ["① 普通のライティング", "② ランプで段にする", "③ 輪郭線を作る", "④ 重ねる"]
    modes = ["smooth", "bands", "outline", "both"]
    starts = [0.0, 2.2, 4.6, 7.0]
    for i in range(4):
        px = 100 + i * 195
        g = root.add("g", opacity=1 if i == 0 else 0)
        if i:
            g.Show(starts[i])
        Sphere(scene, g, px, 170, 72, modes[i])
        scene.Text(root, px, 70, titles[i], size=14, fill=INK, anchor="middle")
        if i < 3:
            a = root.add("g", opacity=0)
            a.Show(starts[i + 1] - 0.4)
            Arrow(scene, a, px + 78, 170, px + 112, 170)
    notes = ["陰影がなめらか", "明るさを 3 段に区切る（セル シェーディング）", "深度・法線の差から、縁だけを取り出す", "段の絵 ＋ 輪郭線 ＝ アニメ調"]
    scene.TextStack(root, 40, 296, [(starts[i], starts[i + 1] if i < 3 else 20, notes[i]) for i in range(4)], size=16, fill=INK)
    scene.Note(0.0, name, "ライティング → 段 → 輪郭 → 合成")
    return dict(name=name, page=PAGE + "stylized/index.md", scene=scene, size=(780, 360), times=[1.0, 3.0, 5.5, 8.5])


def OutlineEdgeDetect():
    name = "outline-edge-detect"
    scene = NewScene(name, 780, 430, duration=11.5, hold=1.5, title="Sobel フィルタ:深度の差が大きい画素を、輪郭にする")
    root = scene.root
    cols, rows, cw, ox, oy = 12, 8, 36, 40, 80
    depth = {}
    for j in range(rows):
        for i in range(cols):
            inside = (i - 5.5) ** 2 / 14 + (j - 3.5) ** 2 / 6.5 < 1
            depth[(i, j)] = 0.3 if inside else 0.85
    cells = {}
    for j in range(rows):
        for i in range(cols):
            d = depth[(i, j)]
            cells[(i, j)] = root.add("rect", x=ox + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill=Gray(d ** 1.0))

    def Sobel(i, j):
        g = lambda a, b: depth[(min(cols - 1, max(0, a)), min(rows - 1, max(0, b)))]
        gx = (g(i + 1, j - 1) + 2 * g(i + 1, j) + g(i + 1, j + 1)) - (g(i - 1, j - 1) + 2 * g(i - 1, j) + g(i - 1, j + 1))
        gy = (g(i - 1, j + 1) + 2 * g(i, j + 1) + g(i + 1, j + 1)) - (g(i - 1, j - 1) + 2 * g(i, j - 1) + g(i + 1, j - 1))
        return math.hypot(gx, gy)

    thr = 0.8
    t0, step = 1.0, 0.1
    order = [(i, j) for j in range(rows) for i in range(cols)]
    ring = root.add("rect", x=ox, y=oy, width=cw * 3 - 1, height=cw * 3 - 1, fill="none", stroke=AMBER, stroke_width=3, opacity=0)
    ring.Steps("x", [(t0 + k * step, R(ox + (i - 1) * cw)) for k, (i, j) in enumerate(order)])
    ring.Steps("y", [(t0 + k * step, R(oy + (j - 1) * cw)) for k, (i, j) in enumerate(order)])
    ring.Set(t0, "opacity", 1)
    ring.Set(t0 + len(order) * step, "opacity", 0)
    edge_marks = []
    for k, (i, j) in enumerate(order):
        v = Sobel(i, j)
        if v > thr:
            m = root.add("rect", x=ox + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill=RED, opacity=0)
            m.Set(t0 + k * step, "opacity", 0.9)
    vals = [(t0 + k * step, "Sobel = %.2f %s" % (Sobel(i, j), "→ 輪郭（しきい値 %.1f 超え）" % thr if Sobel(i, j) > thr else "→ 輪郭ではない")) for k, (i, j) in enumerate(order)]
    scene.TextStack(root, 40, 400, [(t, t + step, txt) for t, txt in vals], size=16, fill=INK)
    scene.Text(root, 40, 60, "灰色が濃い = 手前（深度が小さい）。橙の枠（3×3）を動かして、周囲との差を調べる", size=13, weight=500, fill=GRAY)
    scene.Text(root, 500, 120, "手前の楕円と、奥の背景", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 150, "差が大きい所 = 物体の縁", size=15, fill=RED)
    scene.Text(root, 500, 184, "深度だけだと、同じ深さの折れ目は", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 206, "検出できない → 法線の差も使う", size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "3×3 のカーネルを走査")
    return dict(name=name, page=PAGE + "stylized/outline-edge.md", scene=scene, size=(780, 430), times=[2.0, 4.5, 7.5, 11.0])


def OutlineHullWidth():
    name = "outline-hull-width"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="反転ハル法:裏面を外へ膨らませ、輪郭線にする")
    root = scene.root
    cx, cy, r0 = 190, 200, 80
    shell = root.add("circle", cx=cx, cy=cy, r=r0, fill="#0b0b0b")
    root.add("circle", cx=cx, cy=cy, r=r0, fill="#f59e0b", stroke="none")
    scene.Text(root, cx, 80, "膨らませる幅を変える", size=14, fill=GRAY, anchor="middle")
    seq = [(0.8, 0), (2.0, 0), (4.5, 14), (6.0, 14), (7.5, 4), (8.5, 4)]
    for idx, (t, w) in enumerate(seq):
        if idx == 0:
            shell.Set(t, "r", r0 + w)
        else:
            shell.Ramp(seq[idx - 1][0], t, "r", r0 + w)
    scene.TextStack(root, 70, 340, [(0.0, 2.0, "幅 0:輪郭線は見えない"), (2.0, 6.0, "幅を広げると、線が太くなる"), (6.0, 7.5, "広すぎ"), (7.5, 20, "適度な幅（細め）")], size=15, fill=INK)
    # 右:距離補正
    scene.Text(root, 570, 80, "遠ざかると…", size=14, fill=GRAY, anchor="middle")
    for k, (label, comp, y) in enumerate((("ワールドの幅を固定", False, 150), ("距離で補正（画面で一定）", True, 290))):
        scene.Text(root, 440, y - 52, label, size=13, fill=INK)
        sh = root.add("circle", cx=520, cy=y, r=40 + 7, fill="#0b0b0b")
        body = root.add("circle", cx=520, cy=y, r=40, fill="#f59e0b")
        t_in, t_out = 8.5, 11.5
        scale = 0.4
        body.Ramp(t_in, t_out, "r", R(40 * scale))
        sh.Ramp(t_in, t_out, "r", R(40 * scale + (7 if comp else 7 * scale)))
    scene.TextStack(root, 440, 372, [(8.5, 20, "上は遠くで線が細くなる。下は画面で一定")], size=12, fill=GRAY, weight=500)
    scene.Note(0.8, name, "幅 0 → 14 → 4、遠ざかる")
    return dict(name=name, page=PAGE + "stylized/outline-hull.md", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.5, 11.0])


def HalftoneDots():
    name = "halftone-dots"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ハーフトーン:暗さを、点の大きさで表す")
    root = scene.root
    n, cw, ox = 20, 30, 40
    scene.Text(root, ox, 74, "元の明るさ（左 = 暗い、右 = 明るい）", size=13, fill=GRAY)
    for k in range(n):
        v = (k + 0.5) / n
        root.add("rect", x=ox + k * cw, y=84, width=cw - 1, height=40, fill=Gray(v))
    scene.Text(root, ox, 164, "網点（暗いほど大きな点）", size=13, fill=GRAY)
    maxr = cw * 0.56
    for j in range(3):
        for k in range(n):
            v = (k + 0.5) / n
            dark = 1 - v
            root.add("circle", cx=ox + k * cw + cw / 2, cy=190 + j * cw, r=R(maxr * math.sqrt(dark)), fill="#111827")
    probe = root.add("rect", x=ox, y=80, width=cw, height=48 + 3 * cw + 66, fill="none", stroke=AMBER, stroke_width=3)
    t0, t1 = 1.0, 9.5
    probe.Steps("x", [(t0 + k * (t1 - t0) / n, R(ox + k * cw)) for k in range(n)])
    zoom = root.add("circle", cx=640, cy=190, r=maxr * 2.6, fill="none", stroke="#cbd5e1", stroke_width=2, stroke_dasharray="4 4")
    dot = root.add("circle", cx=640, cy=190, r=1, fill="#111827")
    dot.Steps("r", [(t0 + k * (t1 - t0) / n, R(maxr * 2.6 * math.sqrt(1 - (k + 0.5) / n))) for k in range(n)])
    scene.Text(root, 640, 120, "この画素の点", size=13, fill=GRAY, anchor="middle")
    scene.TextStack(root, 640, 320, [(t0 + k * (t1 - t0) / n, t0 + (k + 1) * (t1 - t0) / n, "暗さ %d %% → 点の半径 %d %%" % (round((1 - (k + 0.5) / n) * 100), round(100 * math.sqrt(1 - (k + 0.5) / n)))) for k in range(n)], size=14, fill=INK, anchor="middle")
    scene.TextStack(root, 40, 372, [(0.0, 20, "点の面積 ＝ 暗さに比例（半径は平方根）。印刷物の網点と同じ見え方になる。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "明るさを走査")
    return dict(name=name, page=PAGE + "stylized/posterize-halftone.md", scene=scene, size=(780, 400), times=[1.5, 4.0, 6.5, 9.5])


FIGS = [MotionBlurShutter, ObjectBlurRotation, MotionBlurJitter, MotionBlurVsTaa, CelRamp, ToonStages, OutlineEdgeDetect, OutlineHullWidth, HalftoneDots]
