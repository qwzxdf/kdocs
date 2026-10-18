import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402

G = "graphics/"


def XLabel(scene, ax, text):
    scene.Text(scene.root, ax.x + ax.w, ax.y + ax.h + 36, text, size=12, weight=500, fill=GRAY, anchor="end")


def BeerRgb():
    name = "beer-rgb"
    scene = NewScene(name, 780, 460, duration=11.0, hold=1.5, title="距離が伸びると、青から先に減り、遠くの物は赤みを帯びる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 230, 10.0, 1.05, ylabel="透過率 T = exp(−σd)")
    XLabel(scene, ax, "距離 d (相対値)")
    sig = {"R": 0.12, "G": 0.29, "B": 0.69}  # 波長の −4 乗に比例する比率(680/550/440 nm)
    cols = {"R": RED, "G": GREEN, "B": BLUE}
    for k, key in enumerate("RGB"):
        fn = lambda d, s=sig[key]: math.exp(-s * d)
        c = ax.Curve(fn, cols[key], width=4, n=80, opacity=0)
        c.Show(0.8 + k * 0.4)
        dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=6, fill=cols[key])
        Sweep(dot, ax, fn, 2.0, 9.5, 0.0, 10.0, n=60)
        scene.Text(root, ax.X(9.4), ax.Y(fn(9.4)) - 10, key, size=13, weight=700, fill=cols[key])
    root.add("rect", x=70, y=345, width=640, height=34, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    sw = root.add("rect", x=72, y=347, width=636, height=30, fill="#ffffff")
    RampFill(sw, "fill", 2.0, 9.5, 40, lambda f: Hex([255 * math.exp(-sig[c] * 10 * f) for c in "RGB"]))
    scene.Text(root, 70, 338, "白い物を d 離れて見たときの色(散乱光を足す前)", size=12, weight=500, fill=GRAY)
    LiveText(scene, root, 390, 420, 2.0, 9.5, 4, lambda i, f: ["近い: 3 色ともほぼ 1(白のまま)", "中くらい: 青が先に減る", "遠い: 緑も減って、赤が残る", "→ 夕日が赤いのと同じ理屈"][i], size=14, fill=INK, anchor="middle")
    scene.Note(2.0, name, "距離を 0 → 10")
    return dict(name=name, page=G + "atmosphere/aerial-fog/physical.md", before="### 空気遠近法 LUT の作り方", scene=scene, size=(780, 460), times=[1.5, 4.0, 6.5, 9.5])


def DecayWeights():
    name = "decay-weights"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="decay が 1 に近いほど、光線は遠くまで伸びる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 64.0, 1.05, ylabel="サンプルの重み decay^i")
    XLabel(scene, ax, "サンプル番号 i(光源へ向かう方向)")
    line = root.add("path", d="M0,0", fill="none", stroke=AMBER, stroke_width=4)
    decays = [0.90, 0.95, 0.97, 0.99]
    prev = 0.0
    for k, dc in enumerate(decays):
        t = 1.2 + k * 2.4
        d = ax.D(lambda i, dc=dc: dc ** i, n=64)
        if k == 0:
            line.Set(0, "d", d)
        else:
            line.Ramp(prev, t, "d", d)
        prev = t + 0.8
        line.Set(prev, "d", d)
    LiveText(scene, root, 390, 392, 1.0, 10.0, 4, lambda i, f: ["decay = 0.90: 10 個先で 0.35。光線は短い", "decay = 0.95: 20 個先で 0.36", "decay = 0.97: 33 個先で 0.37", "decay = 0.99: 64 個先でも 0.53。画面の端まで伸びる"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "decay を上げる")
    return dict(name=name, page=G + "atmosphere/god-rays/tuning.md", before="## よくあるミス", scene=scene, size=(780, 420), times=[1.0, 3.8, 6.5, 9.5])


def FroxelSlices():
    name = "froxel-depth-split"
    scene = NewScene(name, 780, 340, duration=9.0, hold=1.5, title="スライスを奥行きに並べる 2 通り: 等間隔と、手前を細かく")
    root = scene.root
    x0, x1, far = 60, 720, 100.0
    n = 16
    for row, (y, label, fn, col) in enumerate([(110, "等間隔(1 枚 6.3 m)", lambda i: far * i / n, GRAY), (220, "指数(手前が細かい)", lambda i: far * (math.exp(4.0 * i / n) - 1) / (math.exp(4.0) - 1), BLUE)]):
        root.add("line", x1=x0, y1=y, x2=x1, y2=y, stroke="#94a3b8", stroke_width=2)
        grp = root.add("g", opacity=0)
        for i in range(n + 1):
            xx = x0 + (x1 - x0) * fn(i) / far
            grp.add("line", x1=xx, y1=y - 22, x2=xx, y2=y + 22, stroke=col, stroke_width=2.5)
        scene.Text(grp, x0, y - 38, label, size=14, weight=700, fill=col)
        grp.Show(1.0 + row * 2.5)
    scene.Text(root, x0, 275, "カメラ 0 m", size=12, weight=500, fill=GRAY)
    scene.Text(root, x1, 275, "100 m", size=12, weight=500, fill=GRAY, anchor="end")
    scene.TextStack(root, 390, 315, [(0.0, 1.0, "16 枚のスライスを、0〜100 m に並べる"), (1.0, 3.5, "等間隔: 遠くも近くも同じ粗さ"), (3.5, 20, "指数: 目に近い所を細かく、遠くを粗く(遠くは、もともと小さく見える)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "等間隔 → 指数")
    return dict(name=name, page=G + "atmosphere/volumetric-fog/quality.md", before="## よくあるミス", scene=scene, size=(780, 340), times=[0.5, 2.0, 5.0, 8.0])


def CloudBayer():
    name = "cloud-bayer"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="4×4 の更新: 1 フレームに 1/16 だけ描き、16 フレームで全部そろう")
    root = scene.root
    order = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
    cs, ox, oy = 62, 150, 90
    for idx in range(16):
        k = order.index(idx)
        cx, cy = ox + (idx % 4) * cs, oy + (idx // 4) * cs
        root.add("rect", x=cx, y=cy, width=cs - 4, height=cs - 4, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        done = root.add("rect", x=cx, y=cy, width=cs - 4, height=cs - 4, fill=Mix("#bfdbfe", "#3b82f6", 0.5), opacity=0)
        done.Set(1.0 + k * 0.75 + 0.5, "opacity", 1)
        cur = root.add("rect", x=cx, y=cy, width=cs - 4, height=cs - 4, fill=AMBER, opacity=0)
        cur.Show(1.0 + k * 0.75, 1.0 + k * 0.75 + 0.75)
        scene.Text(root, cx + (cs - 4) / 2, cy + cs / 2 + 4, str(k + 1), size=13, weight=700, fill=INK, anchor="middle")
    scene.Text(root, ox, oy - 12, "画面を 4×4 のブロックに分け、番号の順に 1 つずつ更新", size=13, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "各ブロックの数字は、更新される順番"), (1.0, 5.0, "1〜4 フレーム目: 離れた位置から順に描く"), (5.0, 9.0, "5〜8 フレーム目: 隙間が埋まっていく"), (9.0, 13.0, "9〜16 フレーム目: 全ブロックが更新される"), (13.0, 20, "残りは前フレームの結果を再投影して使う(= 時間蓄積)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "フレーム 1 → 16")
    return dict(name=name, page=G + "atmosphere/clouds/temporal.md", before="### 破綻とその対策", scene=scene, size=(780, 440), times=[1.5, 4.5, 8.0, 12.5])


def ProbeRoundRobin():
    name = "probe-roundrobin"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="プローブの更新を絞る: 1 フレームに 4 個だけ、順番に更新")
    root = scene.root
    cols, rows, cs = 6, 4, 62
    ox, oy = 150, 80
    for idx in range(cols * rows):
        f = idx // 4
        cx, cy = ox + (idx % cols) * cs, oy + (idx // cols) * cs
        # 更新順: 横に 4 個ずつ(行をまたいでよい)
        cell = root.add("circle", cx=cx + cs / 2, cy=cy + cs / 2, r=20, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
        tint = root.add("circle", cx=cx + cs / 2, cy=cy + cs / 2, r=20, fill=BLUE, opacity=0)
        tint.Set(1.0 + f * 1.4 + 0.7, "opacity", 0.45)
        flash = root.add("circle", cx=cx + cs / 2, cy=cy + cs / 2, r=24, fill=AMBER, opacity=0)
        flash.Show(1.0 + f * 1.4, 1.0 + f * 1.4 + 0.7)
    scene.Text(root, ox, oy - 12, "6×4 = 24 個のプローブ(橙: このフレームで更新、青: 更新済み)", size=13, weight=500, fill=GRAY)
    LiveText(scene, root, 390, 360, 1.0, 9.4, 6, lambda i, f: "フレーム %d: プローブ %d〜%d を更新" % (i + 1, i * 4 + 1, i * 4 + 4), size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "フレーム 1 → 6")
    return dict(name=name, page=G + "gi/probes/dynamic-update.md", before="## よくあるミス", scene=scene, size=(780, 400), times=[1.5, 3.5, 6.0, 9.0])


def SkyGradient():
    name = "sky-gradient-day"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="太陽の高さに合わせて、天頂と地平線の 2 色を入れ替える")
    root = scene.root
    keys = [("昼", "#2563eb", "#bfdbfe"), ("夕方", "#1e3a8a", "#fb923c"), ("夕暮れ", "#1e1b4b", "#a855f7"), ("夜", "#020617", "#1e293b")]
    bands, x, y, w, h = 10, 140, 70, 500, 260
    for b in range(bands):
        f = b / (bands - 1)  # 0 = 天頂, 1 = 地平線
        r = root.add("rect", x=x, y=y + h * b / bands, width=w, height=h / bands + 1, fill=Mix(keys[0][1], keys[0][2], f ** 1.5))
        for k in range(1, len(keys)):
            t0, t1 = 1.0 + (k - 1) * 3.2 + 0.8, 1.0 + k * 3.2
            r.Ramp(t0, t1, "fill", Mix(keys[k][1], keys[k][2], f ** 1.5))
    root.add("rect", x=x, y=y, width=w, height=h, fill="none", stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, x + w + 12, y + 14, "天頂", size=12, weight=500, fill=GRAY)
    scene.Text(root, x + w + 12, y + h, "地平線", size=12, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 375, [(0.0, 1.0, "空は、天頂色と地平線色の 2 色を混ぜるだけ"), (1.0, 4.2, "昼: 天頂は濃い青、地平線は薄い水色"), (4.2, 7.4, "夕方: 地平線がオレンジに"), (7.4, 10.6, "夕暮れ: 紫を経て暗くなる"), (10.6, 20, "夜: 天頂も地平線もほぼ黒")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "昼 → 夜")
    return dict(name=name, page=G + "atmosphere/sky-models/gradient.md", before="## よくあるミス", scene=scene, size=(780, 420), times=[0.5, 3.0, 6.0, 9.0])


FIGS = [BeerRgb, DecayWeights, FroxelSlices, CloudBayer, ProbeRoundRobin, SkyGradient]
