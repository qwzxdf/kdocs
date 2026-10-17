import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

G = "graphics/"


def HbaoHorizon():
    name = "hbao-horizon"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="HBAO:一方向に、地平線（最も高い遮蔽）の角度を探す")
    root = scene.root
    gy = 330
    px, py = 200, gy
    root.add("rect", x=40, y=gy, width=700, height=16, fill="#d6c7a1")
    # 高さ場
    terrain = [(0, 0), (60, 0), (110, 10), (160, 0), (230, 40), (290, 70), (330, 70), (380, 20), (430, 0), (500, 0)]
    pts = [(px + x, gy - h) for x, h in terrain]
    root.add("polygon", points=" ".join("%s,%s" % p for p in [(pts[0][0], gy)] + pts + [(pts[-1][0], gy)]), fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("circle", cx=px, cy=py, r=8, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, px - 28, py + 34, "着色点", size=12, fill=BLUE)
    steps = [(x, h) for x, h in terrain[1:]]
    best = -1.0
    ang_items = []
    t0, dt = 1.2, 0.9
    horizon = root.add("line", x1=px, y1=py, x2=px + 100, y2=py, stroke=RED, stroke_width=3.5)
    xs = [(0.0, px + 100)]
    ys = [(0.0, py)]
    texts = []
    k = 0
    for i, (x, h) in enumerate(steps):
        ang = math.atan2(h, x)
        updated = ang > best
        if updated:
            best = ang
        t = t0 + i * dt
        c = root.add("circle", cx=px + x, cy=gy - h, r=6, fill=GREEN if updated else GRAY, opacity=0)
        c.Show(t)
        ln = root.add("line", x1=px, y1=py, x2=px + x, y2=gy - h, stroke=GREEN if updated else "#cbd5e1", stroke_width=2, opacity=0)
        ln.Show(t, t + dt)
        L = 240
        xs.append((t, R(px + L * math.cos(best))))
        ys.append((t, R(py - L * math.sin(best))))
        texts.append((t, t + dt, "サンプル %d:仰角 %d° %s → これまでの最大 %d°" % (i + 1, round(math.degrees(ang)), "（更新!）" if updated else "（低い）", round(math.degrees(best)))))
    horizon.Steps("x2", xs)
    horizon.Steps("y2", ys)
    end_t = t0 + len(steps) * dt
    scene.TextStack(root, 40, 66, texts + [(end_t, 20, "地平線の角度 h = %d° → この方向の遮蔽 ≒ sin h = %.2f" % (round(math.degrees(best)), math.sin(best)))], size=16, fill=INK)
    scene.Text(root, 40, 396, "赤い線 = これまでに見つけた地平線。遮蔽される範囲は、地平線より下の角度（扇形）。方向を何本か（4〜8）繰り返して平均する。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "サンプルを遠くへ進める")
    return dict(name=name, page=G + "ao/hbao.md", before="## 式", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def AoRangeCheck():
    name = "ao-range-check"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="範囲チェック:遠く離れた物は、遮蔽に数えない（ハローを防ぐ）")
    root = scene.root
    # 側面図:手前の箱と、ずっと奥の壁
    gx = 60
    root.add("rect", x=gx, y=250, width=300, height=18, fill="#d6c7a1")
    root.add("rect", x=gx + 130, y=140, width=70, height=110, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    scene.Text(root, gx + 165, 130, "手前の物", size=12, fill=GRAY, anchor="middle")
    P = (gx + 40, 250)
    root.add("rect", x=gx + 6, y=140, width=14, height=110, fill="#94a3b8")
    # 簡略:奥の面の点 P のまわりで、サンプルを取る(深度はカメラから見て)
    scene.Text(root, 60, 82, "カメラの視線(左→右)。着色点 P は奥の壁の上。", size=13, fill=GRAY, weight=500)
    root.add("rect", x=420, y=100, width=320, height=210, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    scene.Text(root, 580, 92, "結果:P のまわりの暗さ", size=13, fill=GRAY, anchor="middle")
    # P の周りに半径 r の円(画面)
    cx, cy = 530, 205
    root.add("rect", x=455, y=140, width=50, height=140, fill="#b8794b")
    root.add("rect", x=505, y=140, width=215, height=140, fill="#cbd5e1")
    scene.Text(root, 480, 158, "手前", size=11, fill="#ffffff", anchor="middle")
    scene.Text(root, 640, 158, "奥の壁", size=11, fill=GRAY, anchor="middle")
    halo = root.add("rect", x=505, y=140, width=60, height=140, fill="#000000", opacity=0)
    halo.Set(2.0, "opacity", 0.0)
    halo.Ramp(2.0, 3.0, "opacity", 0.55)
    halo.Set(6.5, "opacity", 0.55)
    halo.Ramp(6.5, 7.5, "opacity", 0.0)
    scene.TextStack(root, 440, 346, [(0.0, 2.0, "範囲チェックなし"), (2.0, 6.5, "手前の「そば」が暗い（ハロー）"), (6.5, 20, "あり:奥の壁に影が落ちない")], size=15, fill=INK)
    # 左:サンプル
    depth_line = root.add("line", x1=gx + 40, y1=250, x2=gx + 40, y2=250, stroke=RED, stroke_width=0)
    for i, (sx, sy, near) in enumerate([(gx + 140, 215, True), (gx + 165, 190, True), (gx + 150, 165, True)]):
        c = root.add("circle", cx=sx, cy=sy, r=7, fill=RED, opacity=0)
        c.Show(1.0 + i * 0.4, 20)
        ln = root.add("line", x1=P[0], y1=P[1] - 10, x2=sx, y2=sy, stroke=RED, stroke_width=1.5, stroke_dasharray="4 3", opacity=0)
        ln.Show(1.0 + i * 0.4, 20)
    scene.TextStack(root, 60, 300, [(0.0, 2.0, "P のまわりのサンプルが、手前の物に当たる"), (2.0, 6.5, "深度が P よりずっと近い → 遮蔽と数える（誤り）"), (6.5, 20, "深度差 > 半径 なら数えない（範囲チェック）")], size=13, fill=INK)
    scene.TextStack(root, 60, 326, [(6.5, 20, "rangeCheck = smoothstep(0, 1, 半径 / |深度差|)")], size=12, fill=GRAY, weight=500)
    scene.Note(2.0, name, "範囲チェックなし → あり")
    return dict(name=name, page=G + "ao/ssao-hemisphere.md", before="### 範囲チェックの意味", scene=scene, size=(780, 420), times=[1.0, 4.0, 5.5, 9.0])


def BilateralBlur():
    name = "bilateral-blur"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="バイラテラル ブラー:深度の違う画素は、混ぜない")
    root = scene.root
    n, cw, ox = 20, 30, 60
    edge = 10
    depth = [0.3 if i < edge else 0.8 for i in range(n)]
    rnd = random.Random(5)
    ao = [max(0.0, min(1.0, (0.3 if i < edge else 0.9) + rnd.uniform(-0.22, 0.22))) for i in range(n)]
    rows = [("入力の AO（ノイズあり）", 90), ("深度（左 = 手前、右 = 奥）", 160), ("普通のぼかし（箱）", 260), ("バイラテラル（深度で重み付け）", 350)]
    for title, y in rows:
        scene.Text(root, ox, y - 10, title, size=13, fill=INK)
    for i in range(n):
        root.add("rect", x=ox + i * cw, y=90, width=cw - 1, height=34, fill=Gray(ao[i]))
        root.add("rect", x=ox + i * cw, y=160, width=cw - 1, height=24, fill="#2563eb" if depth[i] < 0.5 else "#93c5fd")
    k = 2
    box, bil = [], []
    for i in range(n):
        idx = [min(n - 1, max(0, j)) for j in range(i - k, i + k + 1)]
        box.append(sum(ao[j] for j in idx) / len(idx))
        ws = [1.0 if abs(depth[j] - depth[i]) < 0.1 else 0.0 for j in idx]
        bil.append(sum(ao[j] * w for j, w in zip(idx, ws)) / sum(ws))
    t0, step = 1.0, 0.5
    for rowy, vals, color in ((260, box, RED), (350, bil, GREEN)):
        for i in range(n):
            r = root.add("rect", x=ox + i * cw, y=rowy, width=cw - 1, height=34, fill="#f1f5f9")
            r.Steps("fill", [(t0 + i * step, Gray(vals[i]))])
    for rowy, kk, color in ((260, k, RED), (350, k, GREEN)):
        win = root.add("rect", x=ox, y=rowy - 4, width=(2 * kk + 1) * cw - 1, height=42, fill="none", stroke=color, stroke_width=3, opacity=0)
        win.Steps("x", [(t0 + i * step, R(ox + (i - kk) * cw)) for i in range(n)])
        win.Set(t0, "opacity", 1)
        win.Set(t0 + n * step, "opacity", 0)
    # 重みの表示
    wrow = root.add("g", opacity=1)
    scene.TextStack(root, ox, 420, [(0.0, t0, "窓(5 画素)を左から右へ動かして、各画素を平均する"), (t0, t0 + n * step, "上:全部混ぜる → 境界(10 番目付近)で、AO がにじむ。下:深度が近い画素だけ混ぜる → 境界がくっきり"), (t0 + n * step, 20, "→ 境界の AO の段差が残り、ハロー（にじみ）が出ない")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "窓を動かす")
    return dict(name=name, page=G + "ao/filtering/bilateral-blur.md", before="### 通常のぼかしの問題", scene=scene, size=(780, 440), times=[2.0, 5.0, 8.0, 12.0])


def AoUpsample():
    name = "ao-upsample"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="アップサンプル:低解像度の 4 点から、深度の近い点を重く混ぜる")
    root = scene.root
    # 低解像度の格子 4 点と、高解像度の画素 1 点
    pos = [(250, 160), (430, 160), (250, 300), (430, 300)]
    depth = [0.3, 0.3, 0.3, 0.85]
    ao = [0.35, 0.40, 0.30, 0.95]
    labels = ["A", "B", "C", "D"]
    root.add("rect", x=190, y=110, width=300, height=240, fill="#ffffff", stroke="#cbd5e1", stroke_width=1.5, stroke_dasharray="4 3")
    for (x, y), d, a, lab in zip(pos, depth, ao, labels):
        root.add("circle", cx=x, cy=y, r=26, fill=Gray(a), stroke="#475569", stroke_width=2)
        scene.Text(root, x, y + 5, lab, size=14, fill="#ffffff" if a < 0.5 else INK, anchor="middle")
        scene.Text(root, x, y + 46, "深度 %.2f" % d, size=12, fill=BLUE if d < 0.5 else "#60a5fa", anchor="middle", weight=500)
    target_depth = 0.32
    px, py = 380, 215
    root.add("circle", cx=px, cy=py, r=10, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, 340, 98, "橙の点 = フル解像度の画素（深度 %.2f）" % target_depth, size=12, fill=AMBER, anchor="middle")
    bil = []
    for (x, y), d, a in zip(pos, depth, ao):
        spatial = math.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * 120 ** 2))
        dw = math.exp(-((d - target_depth) ** 2) / (2 * 0.05 ** 2))
        bil.append((spatial, dw, spatial * dw))
    naive = sum(a * b[0] for a, b in zip(ao, bil)) / sum(b[0] for b in bil)
    good = sum(a * b[2] for a, b in zip(ao, bil)) / sum(b[2] for b in bil)
    t0, dt = 1.0, 1.4
    for i, ((x, y), (sp, dw, w)) in enumerate(zip(pos, bil)):
        t = t0 + i * dt
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("line", x1=px, y1=py, x2=x, y2=y, stroke=GREEN if dw > 0.5 else RED, stroke_width=1 + 6 * (w / max(b[2] for b in bil)), opacity=0.8)
        scene.Text(g, x, y - 36, "重み %.2f" % w, size=13, fill=GREEN if dw > 0.5 else RED, anchor="middle")
    t_end = t0 + 4 * dt
    res1 = root.add("rect", x=520, y=140, width=100, height=50, fill=Gray(naive), opacity=0)
    res1.Show(t_end, 20)
    res2 = root.add("rect", x=520, y=250, width=100, height=50, fill=Gray(good), opacity=0)
    res2.Show(t_end + 1.5, 20)
    scene.TextStack(root, 520, 130, [(t_end, 20, "距離だけの補間")], size=13, fill=RED)
    scene.TextStack(root, 520, 240, [(t_end + 1.5, 20, "距離 × 深度の近さ")], size=13, fill=GREEN)
    scene.TextStack(root, 520, 214, [(t_end, 20, "AO = %.2f" % naive)], size=15, fill=INK)
    scene.TextStack(root, 520, 324, [(t_end + 1.5, 20, "AO = %.2f（D に引きずられない）" % good)], size=15, fill=INK)
    scene.TextStack(root, 40, 392, [(0.0, t_end, "低解像度の AO 4 点（A〜D）から、中央の画素の AO を求める。各点の重み = 距離 × 深度の近さ"), (t_end, 20, "深度が違う D（奥）の重みは、ほぼ 0。境界がにじまない")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "4 点の重み")
    return dict(name=name, page=G + "ao/filtering/upsample.md", before="### ジョイント バイラテラル", scene=scene, size=(780, 420), times=[2.0, 4.0, 6.5, 10.0])


def RtaoRays():
    name = "rtao-rays"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="RTAO:半球に短いレイを飛ばして、当たった割合が遮蔽")
    root = scene.root
    gy = 320
    px, py = 390, gy
    root.add("rect", x=40, y=gy, width=700, height=16, fill="#d6c7a1")
    root.add("rect", x=px + 70, y=gy - 120, width=90, height=120, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("rect", x=px - 190, y=gy - 60, width=60, height=60, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("circle", cx=px, cy=py, r=8, fill=BLUE, stroke="#ffffff", stroke_width=2)
    rnd = random.Random(2)
    N = 16
    maxd = 190
    hits = 0
    items = []
    t0, dt = 1.0, 0.55
    for i in range(N):
        a = math.radians(10 + 160 * (i + 0.5) / N + rnd.uniform(-4, 4))
        dx, dy = math.cos(a), -math.sin(a)
        hit = None
        for d in range(5, maxd, 3):
            x, y = px + dx * d, py + dy * d
            if (px + 70 <= x <= px + 160 and gy - 120 <= y <= gy) or (px - 190 <= x <= px - 130 and gy - 60 <= y <= gy):
                hit = d
                break
        ex, ey = px + dx * (hit if hit else maxd), py + dy * (hit if hit else maxd)
        if hit:
            hits += 1
        ln = root.add("line", x1=px, y1=py - 4, x2=R(ex), y2=R(ey), stroke=RED if hit else GREEN, stroke_width=2, opacity=0)
        ln.Show(t0 + i * dt)
        dot = root.add("circle", cx=R(ex), cy=R(ey), r=4, fill=RED if hit else GREEN, opacity=0)
        dot.Show(t0 + i * dt)
        items.append((t0 + i * dt, hits))
    scene.TextStack(root, 40, 66, [(t0 + i * dt, t0 + (i + 1) * dt, "レイ %d / %d:%s   当たり %d 本" % (i + 1, N, "遮蔽物に当たった（赤）" if (items[i][1] > (items[i - 1][1] if i else 0)) else "届いた（緑）", items[i][1])) for i in range(N)], size=16, fill=INK)
    ao = 1 - hits / N
    scene.TextStack(root, 40, 66, [(t0 + N * dt, 20, "遮蔽 = %d / %d → AO = 1 − %.2f = %.2f" % (hits, N, hits / N, ao))], size=18, fill=RED)
    scene.Text(root, 40, 396, "レイの長さは短く（AO の半径）。1 画素 1〜2 本 ＋ デノイズで使う。画面外の物体の遮蔽も、正確に得られる。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "16 本のレイ")
    return dict(name=name, page=G + "ao/world-space/rtao.md", before="### 手順", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 11.0])


def DfaoCone():
    name = "dfao-cone"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="距離場 AO:円錐を進めて、距離と円錐の幅を比べる")
    root = scene.root
    gy = 330
    px, py = 120, gy
    root.add("rect", x=40, y=gy, width=700, height=16, fill="#d6c7a1")
    obj = (430, 205, 42)
    root.add("circle", cx=obj[0], cy=obj[1], r=obj[2], fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("circle", cx=px, cy=py, r=8, fill=BLUE, stroke="#ffffff", stroke_width=2)
    ang = math.radians(12)
    dx, dy = math.cos(ang), -math.sin(ang)
    half = math.radians(16)
    for sgn in (-1, 1):
        a = ang + sgn * half
        root.add("line", x1=px, y1=py, x2=px + 560 * math.cos(a), y2=py - 560 * math.sin(a), stroke="#cbd5e1", stroke_width=1.5, stroke_dasharray="5 4")
    occl = 0.0
    t = 24.0
    steps = []
    while t < 520 and len(steps) < 9:
        x, y = px + dx * t, py + dy * t
        d = max(0.0, math.hypot(x - obj[0], y - obj[1]) - obj[2])
        cone_r = t * math.tan(half)
        contrib = max(0.0, 1 - d / cone_r) * (1 - occl)
        occl += contrib
        steps.append((x, y, d, cone_r, contrib, occl))
        t += max(d * 0.9, cone_r * 0.55, 26)
    t0, dt = 1.0, 1.1
    for i, (x, y, d, cr, c, o) in enumerate(steps):
        tt = t0 + i * dt
        g = root.add("g", opacity=0)
        g.Show(tt)
        g.add("circle", cx=R(x), cy=R(y), r=R(min(cr, 160)), fill="none", stroke=AMBER, stroke_width=2)
        g.add("circle", cx=R(x), cy=R(y), r=R(max(min(d, 160), 1)), fill="none", stroke=GREEN, stroke_width=2, stroke_dasharray="4 3")
        g.add("circle", cx=R(x), cy=R(y), r=4, fill=INK)
    scene.TextStack(root, 40, 60, [(t0 + i * dt, t0 + (i + 1) * dt if i < len(steps) - 1 else 20, "ステップ %d:最も近い物までの距離 d = %d、円錐の半径 = %d → 遮蔽を %.2f 足す（合計 %.2f）" % (i + 1, round(d), round(cr), c, o)) for i, (x, y, d, cr, c, o) in enumerate(steps)], size=14, fill=INK)
    scene.TextStack(root, 40, 394, [(t0 + len(steps) * dt, 20, "→ この円錐の遮蔽 ≒ %.2f。円錐を数方向に飛ばして、平均が AO になる" % steps[-1][5])], size=15, fill=RED)
    scene.Text(root, 40, 412, "緑の点線の円 = 距離場の距離 d、橙の円 = 円錐の断面。d が円錐より小さいほど、遮蔽される。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "円錐トレース")
    return dict(name=name, page=G + "ao/world-space/dfao.md", before="### 円錐トレース", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def SsgiBounce():
    name = "ssgi-bounce"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="SSGI:画面の中の明るい物から、色を借りて、間接光にする")
    root = scene.root
    # 側面:赤い壁、白い床
    root.add("rect", x=60, y=320, width=640, height=18, fill="#e5e7eb", stroke="#94a3b8", stroke_width=1.5)
    root.add("rect", x=540, y=140, width=22, height=182, fill="#e5484d")
    scene.Text(root, 551, 128, "赤い壁（光が当たっている）", size=12, fill=RED, anchor="middle")
    root.add("circle", cx=620, cy=70, r=14, fill=AMBER)
    scene.Text(root, 640, 66, "光", size=12, fill=AMBER)
    px, py = 400, 316
    root.add("circle", cx=px, cy=py, r=9, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, px - 30, py + 38, "着色点（床）", size=12, fill=BLUE)
    t0, dt = 1.0, 0.55
    rnd = random.Random(4)
    samples = []
    cnt_red = 0
    for i in range(14):
        a = math.radians(rnd.uniform(5, 175))
        d = rnd.uniform(60, 190)
        x, y = px + math.cos(a) * d, py - math.sin(a) * d
        if x > 540 and 140 < y < 320:
            col, wt = "#e5484d", 1
        elif y > 320:
            continue
        else:
            col, wt = "#cbd5e1", 0
        samples.append((x, y, col))
    for i, (x, y, col) in enumerate(samples):
        t = t0 + i * dt
        ln = root.add("line", x1=px, y1=py - 6, x2=R(x), y2=R(y), stroke=col if col != "#cbd5e1" else "#cbd5e1", stroke_width=1.8, opacity=0)
        ln.Show(t)
        c = root.add("circle", cx=R(x), cy=R(y), r=5, fill=col, stroke="#64748b", stroke_width=1, opacity=0)
        c.Show(t)
        if col == "#e5484d":
            cnt_red += 1
    # 赤みが増していく床
    floor = root.add("rect", x=300, y=322, width=200, height=14, fill="#e5e7eb", opacity=1)
    n = len(samples)
    prev = None
    reds = 0
    for i, (x, y, col) in enumerate(samples):
        if col == "#e5484d":
            reds += 1
        t = t0 + i * dt
        mix = Mix("#e5e7eb", "#f87171", min(1.0, reds / 5))
        floor.Set(t, "fill", mix)
    t_end = t0 + n * dt
    scene.TextStack(root, 40, 60, [(0.0, t0, "着色点から、画面（深度バッファ）に沿って、サンプルを取る"), (t0, t_end, "サンプルの色を、明るさ・向きの重みで集める"), (t_end, 20, "赤い壁のサンプルが混ざり → 床がほんのり赤い（カラー ブリーディング）")], size=16, fill=INK)
    scene.Text(root, 40, 396, "画面に映っていない物は拾えない（画面外・背面の光は、無し）。拾った色は、前フレームの結果を使うと、多重バウンスにもなる。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "サンプルを集める")
    return dict(name=name, page=G + "gi/ssgi.md", before="### 手順", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def ProbeBilinear():
    name = "probe-bilinear"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="プローブの補間:周りの 4 つ（3D では 8 つ）を、距離で重み付けして混ぜる")
    root = scene.root
    x0, y0, s = 110, 100, 260
    cols = {"00": "#e5484d", "10": "#2563eb", "01": "#2ea043", "11": "#e5aa28"}
    root.add("rect", x=x0, y=y0, width=s, height=s, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    probes = [(0, 0, "00"), (1, 0, "10"), (0, 1, "01"), (1, 1, "11")]
    for (u, v, k) in probes:
        root.add("circle", cx=x0 + u * s, cy=y0 + v * s, r=20, fill=cols[k], stroke="#ffffff", stroke_width=3)
    pt = root.add("circle", cx=x0 + 0.2 * s, cy=y0 + 0.25 * s, r=10, fill="#ffffff", stroke=INK, stroke_width=3)
    path = [(0.8, 0.2, 0.25), (3.2, 0.8, 0.2), (5.6, 0.75, 0.8), (8.0, 0.25, 0.75), (10.4, 0.5, 0.5)]
    swatch = root.add("rect", x=470, y=100, width=130, height=90, fill="#888888", stroke="#94a3b8", stroke_width=2)

    def Col(u, v):
        w = {"00": (1 - u) * (1 - v), "10": u * (1 - v), "01": (1 - u) * v, "11": u * v}
        rgb = [0.0, 0.0, 0.0]
        for k, wk in w.items():
            c = cols[k].lstrip("#")
            for i in range(3):
                rgb[i] += int(c[2 * i:2 * i + 2], 16) * wk
        return Hex(rgb), w

    n = 14
    states = []
    for idx in range(len(path) - 1):
        ta, ua, va = path[idx]
        tb, ub, vb = path[idx + 1]
        for i in range(n + 1):
            if idx > 0 and i == 0:
                continue
            f = i / n
            states.append((Lerp(ta, tb, f), Lerp(ua, ub, f), Lerp(va, vb, f)))
    prev = None
    for k, (t, u, v) in enumerate(states):
        col, w = Col(u, v)
        if k == 0:
            pt.Set(t, "cx", R(x0 + u * s)); pt.Set(t, "cy", R(y0 + v * s)); swatch.Set(t, "fill", col)
        else:
            pt.Ramp(prev, t, "cx", R(x0 + u * s)); pt.Ramp(prev, t, "cy", R(y0 + v * s)); swatch.Ramp(prev, t, "fill", col)
        prev = t
    LiveText(scene, root, 470, 224, 0.8, 10.4, 30, lambda i, f: "重み 赤 %.2f  青 %.2f" % (Col(*states[int(f * (len(states) - 1))][1:])[1]["00"], Col(*states[int(f * (len(states) - 1))][1:])[1]["10"]), size=14, fill=INK)
    LiveText(scene, root, 470, 246, 0.8, 10.4, 30, lambda i, f: "     緑 %.2f  黄 %.2f" % (Col(*states[int(f * (len(states) - 1))][1:])[1]["01"], Col(*states[int(f * (len(states) - 1))][1:])[1]["11"]), size=14, fill=INK)
    scene.Text(root, 470, 90, "混ざった色（その点の間接光）", size=12, fill=GRAY)
    scene.Text(root, 40, 396, "近いプローブほど重い。重みの合計は 1。物体が動いても、プローブ間を滑らかに補間するので、色がちらつかない。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "点を動かす")
    return dict(name=name, page=G + "gi/probes/interpolation.md", before="### 3D 格子", scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.5])


def ProbeLightLeak():
    name = "probe-light-leak"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="ライト リーク:壁の向こうのプローブが、混ざってしまう")
    root = scene.root
    panels = [(40, "可視性なし（そのまま補間）", False), (400, "可視性あり（壁の向こうは除く）", True)]
    for px, title, vis in panels:
        scene.Text(root, px, 68, title, size=14, fill=RED if not vis else GREEN)
        root.add("rect", x=px, y=90, width=330, height=220, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
        root.add("rect", x=px + 162, y=90, width=10, height=220, fill="#475569")
        scene.Text(root, px + 90, 108, "暗い部屋", size=11, fill=GRAY, anchor="middle")
        scene.Text(root, px + 250, 108, "明るい部屋", size=11, fill=GRAY, anchor="middle")
        root.add("rect", x=px, y=90, width=162, height=220, fill="#0f172a", fill_opacity=0.22)
        probes = [(px + 40, 150, 0.1), (px + 40, 260, 0.1), (px + 290, 150, 0.9), (px + 290, 260, 0.9)]
        for (x, y, v) in probes:
            root.add("circle", cx=x, cy=y, r=11, fill=Gray(v), stroke=INK, stroke_width=2)
        p = root.add("circle", cx=px + 120, cy=200, r=9, fill="#ffffff", stroke=INK, stroke_width=3)
        sw = root.add("rect", x=px + 90, y=330, width=150, height=30, fill="#888888", stroke="#94a3b8", stroke_width=1.5)
        for k in range(11):
            f = k / 10
            t = 1.0 + f * 8.0
            xx = 120 + f * 0.0
            # 点は壁の手前(暗い側)をゆっくり右へ
            cx = px + 60 + 90 * f
            w = [max(0.01, 1 - abs(cx - probes[i][0]) / 300) for i in range(4)]
            if vis:
                w = [w[i] if probes[i][0] < px + 162 else 0.0 for i in range(4)]
            val = sum(w[i] * probes[i][2] for i in range(4)) / sum(w)
            if k == 0:
                p.Set(t, "cx", R(cx)); sw.Set(t, "fill", Gray(val))
            else:
                p.Ramp(1.0 + (k - 1) / 10 * 8.0, t, "cx", R(cx)); sw.Ramp(1.0 + (k - 1) / 10 * 8.0, t, "fill", Gray(val))
        scene.Text(root, px + 165, 352, "→", size=1, fill="#ffffff")
        scene.Text(root, px + 20, 352, "結果:", size=13, fill=INK)
    scene.TextStack(root, 40, 386, [(0.0, 1.0, "暗い部屋の中の点を、壁へ近づける"), (1.0, 20, "左:壁の向こうの明るいプローブが混ざり、暗い部屋が明るくなる（漏れ）。右:壁越しは重み 0 → 暗いまま")], size=13, fill=GRAY, weight=500)
    scene.Note(1.0, name, "点を壁に近づける")
    return dict(name=name, page=G + "gi/probes/placement.md", before="### ライト リーク", scene=scene, size=(780, 400), times=[1.0, 4.0, 7.0, 10.5])


def DdgiProbeRays():
    name = "ddgi-probe-rays"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="DDGI:プローブからレイを飛ばし、結果を少しずつ混ぜ込む")
    root = scene.root
    root.add("rect", x=40, y=80, width=420, height=250, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    root.add("rect", x=40, y=80, width=420, height=12, fill="#94a3b8")
    root.add("rect", x=40, y=318, width=420, height=12, fill="#94a3b8")
    root.add("rect", x=448, y=80, width=12, height=250, fill="#e5484d")
    root.add("rect", x=40, y=80, width=12, height=250, fill="#2ea043")
    root.add("rect", x=230, y=260, width=70, height=58, fill="#cbd5e1", stroke="#64748b", stroke_width=1.5)
    P = (250, 190)
    root.add("circle", cx=P[0], cy=P[1], r=10, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, P[0] + 14, P[1] - 12, "プローブ", size=12, fill=BLUE)
    hits = [(448, 150, "#e5484d"), (448, 230, "#e5484d"), (52, 140, "#2ea043"), (52, 240, "#2ea043"), (330, 92, "#94a3b8"), (160, 92, "#94a3b8"), (265, 260, "#cbd5e1"), (215, 318, "#94a3b8")]
    t0, dt = 1.0, 0.7
    for i, (x, y, col) in enumerate(hits):
        t = t0 + i * dt
        ln = root.add("line", x1=P[0], y1=P[1], x2=x, y2=y, stroke=col, stroke_width=2.5, opacity=0)
        ln.Show(t, t0 + len(hits) * dt + 1.5)
        c = root.add("circle", cx=x, cy=y, r=6, fill=col, stroke=INK, stroke_width=1.5, opacity=0)
        c.Show(t, t0 + len(hits) * dt + 1.5)
    t_blend = t0 + len(hits) * dt + 0.6
    # 右:履歴との混合
    ax = Axes(scene, root, 520, 100, 220, 170, 12.0, 1.0, "フレーム", "プローブの値")
    target = 0.8
    hist, v = [], 0.2
    for k in range(13):
        hist.append(v)
        v = v + (target - v) * 0.2
    pts = " L".join("%s,%s" % (ax.X(k), ax.Y(hist[k])) for k in range(13))
    root.add("line", x1=ax.x, y1=ax.Y(target), x2=ax.x + ax.w, y2=ax.Y(target), stroke=GRAY, stroke_width=1.5, stroke_dasharray="4 3")
    scene.Text(root, ax.x + ax.w, ax.Y(target) - 6, "今のフレームの結果", size=11, fill=GRAY, anchor="end")
    curve = root.add("path", d="M" + pts, fill="none", stroke=GREEN, stroke_width=4, opacity=0)
    curve.Show(t_blend)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(hist[0]), r=6, fill=RED, opacity=0)
    dot.Show(t_blend)
    prev = None
    for k in range(13):
        t = t_blend + k * 0.45
        if k == 0:
            dot.Set(t, "cx", ax.X(0)); dot.Set(t, "cy", ax.Y(hist[0]))
        else:
            dot.Ramp(prev, t, "cx", ax.X(k)); dot.Ramp(prev, t, "cy", ax.Y(hist[k]))
        prev = t
    scene.TextStack(root, 40, 60, [(0.0, t0, "プローブから、ランダムな方向へ"), (t0, t_blend, "レイが当たった所の色（明るさ・色）を集める"), (t_blend, 20, "集めた結果を、前フレームの値と混ぜる（ヒステリシス）")], size=16, fill=INK)
    scene.Text(root, 40, 370, "赤い壁・緑の壁の色が、プローブに入る。毎フレーム少しずつ混ぜるので、ちらつかず、光の変化にも追従する。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "レイ → 混合")
    return dict(name=name, page=G + "gi/ddgi.md", before="## 全体の流れ", scene=scene, size=(780, 420), times=[2.0, 4.5, 8.0, 12.0])


def VoxelConeTrace():
    name = "voxel-cone-trace"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="コーン トレース:遠いほど、粗いミップ（大きなボクセル）を読む")
    root = scene.root
    ox, oy = 40, 200
    # 3 段のボクセル(大きさが倍々)
    for lvl, (sz, col) in enumerate(((20, "#e5e7eb"), (40, "#dbeafe"), (80, "#bfdbfe"))):
        pass
    cone_a = math.radians(14)
    # 背景のボクセル格子(細かい)
    for i in range(0, 700, 20):
        root.add("line", x1=ox + i, y1=100, x2=ox + i, y2=320, stroke="#f1f5f9", stroke_width=1)
    for j in range(100, 321, 20):
        root.add("line", x1=ox, y1=j, x2=ox + 700, y2=j, stroke="#f1f5f9", stroke_width=1)
    # 光る壁
    root.add("rect", x=ox + 560, y=130, width=40, height=150, fill="#e5aa28")
    scene.Text(root, ox + 580, 120, "光る面", size=12, fill=AMBER, anchor="middle")
    root.add("circle", cx=ox, cy=oy, r=8, fill=BLUE)
    root.add("polygon", points="%s,%s %s,%s %s,%s" % (ox, oy, R(ox + 560), R(oy - 560 * math.tan(cone_a)), R(ox + 560), R(oy + 560 * math.tan(cone_a))), fill=BLUE, fill_opacity=0.08, stroke=BLUE, stroke_width=1.5)
    vclip = scene.defs.add("clipPath", id="vx-clip")
    vclip.add("rect", x=40, y=92, width=700, height=240)
    steps = []
    d = 30.0
    while d < 580 and len(steps) < 7:
        w = max(20.0, 2 * d * math.tan(cone_a))
        lvl = max(0, round(math.log2(w / 20.0)))
        size = 20 * (2 ** lvl)
        steps.append((d, size, lvl))
        d += size * 0.9 + 6
    t0, dt = 1.0, 1.1
    for i, (d, size, lvl) in enumerate(steps):
        t = t0 + i * dt
        g = root.add("g", opacity=0, clip_path="url(#vx-clip)")
        g.Show(t)
        g.add("rect", x=R(ox + d - size / 2), y=R(oy - size / 2), width=size, height=size, fill=["#fde68a", "#fcd34d", "#fbbf24", "#f59e0b"][min(3, lvl)], fill_opacity=0.5, stroke=AMBER, stroke_width=2)
        scene.Text(g, R(ox + d), R(oy + size / 2 + 16), "ミップ %d" % lvl, size=11, fill=INK, anchor="middle")
    texts = []
    for i, (d, size, lvl) in enumerate(steps):
        texts.append((t0 + i * dt, t0 + (i + 1) * dt if i < len(steps) - 1 else 20, "ステップ %d:円錐の幅 ≒ %d → ミップ %d（1 辺 %d）を読む" % (i + 1, round(max(20, 2 * d * math.tan(cone_a))), lvl, size)))
    scene.TextStack(root, 40, 60, texts, size=15, fill=INK)
    scene.Text(root, 40, 396, "近くは細かいボクセル、遠くは粗いミップ。少ない読み取りで、広い範囲の光を集められる（拡散は 5〜6 本の円錐）。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "円錐を進める")
    return dict(name=name, page=G + "gi/voxel-gi.md", before="### ④ コーン トレース", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def RestirReservoir():
    name = "restir-reservoir"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="リザーバー:候補を流して見ながら、良さそうな 1 つだけ覚える")
    root = scene.root
    rnd = random.Random(8)
    cands = [("A", 0.1, "#94a3b8"), ("B", 0.3, "#60a5fa"), ("C", 2.4, "#e5484d"), ("D", 0.2, "#94a3b8"), ("E", 0.5, "#fbbf24"), ("F", 1.1, "#2ea043"), ("G", 0.15, "#94a3b8"), ("H", 0.4, "#a78bfa")]
    # 重み(明るさ)
    t0, dt = 1.2, 1.2
    x0, y0 = 60, 130
    wsum = 0.0
    chosen = None
    rolls = [0.5, 0.2, 0.05, 0.9, 0.6, 0.3, 0.8, 0.7]
    states = []
    for i, (lab, w, col) in enumerate(cands):
        wsum += w
        p = w / wsum
        take = rolls[i] < p
        if take or chosen is None:
            chosen = i
        states.append((i, w, wsum, p, take, chosen))
    for i, (lab, w, col) in enumerate(cands):
        x = x0 + i * 80
        t = t0 + i * dt
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=x, y=y0, width=62, height=R(20 + w * 40), fill=col, stroke=INK, stroke_width=1.5)
        scene.Text(g, x + 31, y0 - 8, "候補 %s" % lab, size=13, fill=INK, anchor="middle")
        scene.Text(g, x + 31, y0 + 20 + w * 40 + 18, "明るさ %.1f" % w, size=11, fill=GRAY, anchor="middle")
    # リザーバー(選ばれたもの)
    root.add("rect", x=60, y=290, width=200, height=70, fill="#ffffff", stroke=INK, stroke_width=2.5, rx=6)
    scene.Text(root, 160, 282, "リザーバー（1 つだけ保持）", size=13, fill=GRAY, anchor="middle")
    holder = root.add("rect", x=70, y=300, width=60, height=50, fill="#e2e8f0")
    holder.Steps("fill", [(t0 + i * dt + 0.5, cands[s[5]][2]) for i, s in enumerate(states)])
    scene.TextStack(root, 140, 335, [(t0 + i * dt + 0.5, t0 + (i + 1) * dt + 0.5, "= 候補 %s" % cands[s[5]][0]) for i, s in enumerate(states)], size=18, fill=INK)
    scene.TextStack(root, 300, 300, [(t0 + i * dt, t0 + (i + 1) * dt, "候補 %s 到着:採用の確率 = %.1f / (累計 %.1f) = %.0f %%" % (cands[i][0], s[1], s[2], s[3] * 100)) for i, s in enumerate(states)], size=15, fill=INK)
    scene.TextStack(root, 300, 328, [(t0 + i * dt, t0 + (i + 1) * dt, "サイコロ → %s" % ("採用! リザーバーを入れ替える" if s[4] else "不採用（今のまま）")) for i, s in enumerate(states)], size=15, fill=GREEN if True else INK)
    scene.TextStack(root, 60, 390, [(t0 + len(cands) * dt + 0.5, 20, "最後に残った 1 つが、重みに比例して選ばれた「良い」サンプル。全部を覚えなくても、1 つだけで済む。")], size=14, fill=INK)
    scene.Text(root, 60, 70, "候補を 1 つずつ流す。明るい（寄与の大きい）候補ほど、残りやすい。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "ストリーミング選択")
    return dict(name=name, page=G + "gi/rt-gi/restir.md", before="## ReSTIR GI", scene=scene, size=(780, 420), times=[2.0, 4.5, 8.0, 12.0])


def RadianceCascades():
    name = "radiance-cascades"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="Radiance Cascades:近くは細かい位置、遠くは細かい方向")
    root = scene.root
    levels = [(0, 7, 4, "#bae6fd", "カスケード 0:プローブ間隔 狭い・方向 4 本・短い距離"), (1, 3, 8, "#fde68a", "カスケード 1:間隔 2 倍・方向 8 本・中距離"), (2, 1, 16, "#fbcfe8", "カスケード 2:間隔 4 倍・方向 16 本・遠距離")]
    root.add("rect", x=40, y=80, width=700, height=250, fill="#f8fafc", stroke="#94a3b8", stroke_width=1.5)
    center = (390, 205)
    rclip = scene.defs.add("clipPath", id="rc-clip")
    rclip.add("rect", x=40, y=80, width=700, height=250)
    for k, (lvl, n, rays, col, label) in enumerate(levels):
        t = 1.0 + k * 3.4
        g = root.add("g", opacity=0)
        g.Show(t)
        spacing = 700 / (2 ** (3 - lvl) * 1.0) / 8 * (2 ** lvl) if False else (50 * (2 ** lvl))
        cols_n = int(660 // spacing)
        rows_n = int(230 // spacing)
        gx0 = 390 - (cols_n // 2) * spacing
        gy0 = 205 - (rows_n // 2) * spacing
        for i in range(cols_n + 1):
            for j in range(rows_n + 1):
                x, y = gx0 + i * spacing, gy0 + j * spacing
                if 50 < x < 730 and 90 < y < 320:
                    g.add("circle", cx=R(x), cy=R(y), r=R(6 - lvl), fill=col, stroke="#64748b", stroke_width=1)
        # 代表プローブの光線(区間ごと:このカスケードが受け持つ距離だけ)
        r0, r1 = [(0, 55), (55, 125), (125, 270)][lvl]
        for r_ in range(rays):
            a_ = 2 * math.pi * r_ / rays
            x0_, y0_ = center[0] + r0 * math.cos(a_), center[1] + r0 * math.sin(a_)
            x1_, y1_ = center[0] + r1 * math.cos(a_), center[1] + r1 * math.sin(a_)
            g.add("line", x1=R(x0_), y1=R(y0_), x2=R(x1_), y2=R(y1_), stroke=["#0284c7", "#d97706", "#db2777"][lvl], stroke_width=2.2, clip_path="url(#rc-clip)")
        scene.TextStack(root, 390, 352, [(t, t + 3.4 if k < 2 else 20, label)], size=14, fill=INK, anchor="middle")
    scene.TextStack(root, 40, 60, [(0.0, 1.0, "近い光は多くのプローブで、遠い光は少ないプローブで"), (1.0, 20, "プローブの数は 1/4 ずつ、方向の数は 2〜4 倍ずつ。階層を重ねて、全体の光を作る")], size=15, fill=INK)
    scene.Text(root, 40, 396, "合計のレイ数がほぼ一定。ノイズが少なく、安定している（2D の GI で特に成功している）。", size=13, weight=500, fill=GRAY)
    scene.Note(1.0, name, "カスケード 0 → 1 → 2")
    return dict(name=name, page=G + "gi/rt-gi/radiance-cascades.md", before="### 発想", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.5, 11.5])


def ShBands():
    name = "sh-bands"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="SH:方向の関数を、低い次数から足して近づけていく")
    root = scene.root
    cx, cy, R0 = 250, 215, 120

    def f(th):
        return max(0.0, math.cos(th - 0.6)) ** 2 * 0.9 + 0.25 * math.exp(-((th - 3.6) ** 2) / 0.1) + 0.12

    N = 256
    th = [2 * math.pi * k / N for k in range(N)]
    vals = [f(t) for t in th]
    # フーリエ係数
    a0 = sum(vals) / N
    ac = [2 * sum(v * math.cos(m * t) for v, t in zip(vals, th)) / N for m in range(0, 7)]
    bc = [2 * sum(v * math.sin(m * t) for v, t in zip(vals, th)) / N for m in range(0, 7)]

    def Approx(order, t):
        s = a0
        for m in range(1, order + 1):
            s += ac[m] * math.cos(m * t) + bc[m] * math.sin(m * t)
        return max(0.0, s)

    def D(fn):
        pts = []
        for k in range(121):
            t = 2 * math.pi * k / 120
            r = R0 * fn(t) / 1.1
            pts.append("%s,%s" % (R(cx + r * math.cos(t)), R(cy - r * math.sin(t))))
        return "M" + " L".join(pts) + " Z"

    root.add("circle", cx=cx, cy=cy, r=R0, fill="none", stroke=LIGHT, stroke_width=1.5)
    root.add("path", d=D(f), fill="none", stroke=GRAY, stroke_width=3, stroke_dasharray="6 4")
    scene.Text(root, cx, cy + R0 + 36, "点線 = 本当の関数（周りの光の分布）", size=12, fill=GRAY, anchor="middle")
    ap = root.add("path", d=D(lambda t: Approx(0, t)), fill=BLUE, fill_opacity=0.18, stroke=BLUE, stroke_width=4)
    seq = [(1.0, 0, 0), (3.5, 1, 1), (6.5, 2, 2), (9.5, 4, 4)]
    for idx in range(1, len(seq)):
        ta, oa, _ = seq[idx - 1]
        tb, ob, _ = seq[idx]
        ap.Ramp(tb - 1.0, tb, "d", D(lambda t, ob=ob: Approx(ob, t)))
    labels = ["L0（1 係数）:平均の明るさだけ（丸）", "L1（4 係数）:だいたいの明るい向き", "L2（9 係数）:拡散の間接光には、これで十分", "L4:細かい形まで（鏡面には、まだ足りない）"]
    stack = [(0.0, 2.5, labels[0]), (2.5, 5.5, labels[1]), (5.5, 8.5, labels[2]), (8.5, 20, labels[3])]
    scene.TextStack(root, 440, 150, stack, size=16, fill=INK)
    scene.Text(root, 440, 200, "（図は 2D の円で表現。実際の SH は球面）", size=12, fill=GRAY, weight=500)
    scene.Text(root, 440, 240, "拡散の光は滑らか（低周波）なので、", size=13, fill=INK, weight=500)
    scene.Text(root, 440, 262, "少数の係数で、ほぼ正確に表せる。", size=13, fill=INK, weight=500)
    scene.Note(1.0, name, "次数 0 → 1 → 2 → 4")
    return dict(name=name, page=G + "gi/theory/spherical-harmonics.md", before="## 球面調和関数（SH）", scene=scene, size=(780, 420), times=[1.0, 4.0, 7.0, 11.0])


def MonteCarlo():
    name = "monte-carlo-converge"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="モンテカルロ:サンプルを増やすほど、平均が真の値に近づく")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 330, 220, 1.0, 1.0, "x", "f(x)")
    f = lambda x: math.sin(math.pi * x)
    ax.Curve(f, BLUE, 4, n=60)
    rnd = random.Random(21)
    pts = [rnd.random() for _ in range(64)]
    t0, dt = 1.0, 0.12
    for i, x in enumerate(pts):
        d = root.add("circle", cx=ax.X(x), cy=ax.Y(f(x)), r=4, fill=RED, opacity=0)
        d.Show(t0 + i * dt)
        ln = root.add("line", x1=ax.X(x), y1=ax.Y(0), x2=ax.X(x), y2=ax.Y(f(x)), stroke=RED, stroke_width=1, opacity=0)
        ln.Show(t0 + i * dt)
    # 右:推定値のグラフ
    ax2 = Axes(scene, root, 450, 80, 290, 220, 64.0, 1.0, "サンプル数", "推定した積分")
    truth = 2 / math.pi
    root.add("line", x1=ax2.x, y1=ax2.Y(truth), x2=ax2.x + ax2.w, y2=ax2.Y(truth), stroke=GREEN, stroke_width=2, stroke_dasharray="5 4")
    scene.Text(root, ax2.x + ax2.w, ax2.Y(truth) - 6, "真の値 2/π ≒ 0.64", size=11, fill=GREEN, anchor="end")
    est = []
    s = 0.0
    for i, x in enumerate(pts):
        s += f(x)
        est.append(s / (i + 1))
    dot = root.add("circle", cx=ax2.X(1), cy=ax2.Y(est[0]), r=5, fill=RED, opacity=0)
    dot.Show(t0)
    path_d = "M" + " L".join("%s,%s" % (ax2.X(i + 1), ax2.Y(min(1.0, est[i]))) for i in range(len(pts)))
    root.add("path", d=path_d, fill="none", stroke=RED, stroke_width=2.5, opacity=0).Show(t0 + len(pts) * dt)
    prev = None
    for i in range(len(pts)):
        t = t0 + i * dt
        if i == 0:
            dot.Set(t, "cx", ax2.X(1)); dot.Set(t, "cy", ax2.Y(min(1.0, est[0])))
        else:
            dot.Ramp(prev, t, "cx", ax2.X(i + 1)); dot.Ramp(prev, t, "cy", ax2.Y(min(1.0, est[i])))
        prev = t
    LiveText(scene, root, 50, 346, t0, t0 + len(pts) * dt, 16, lambda i, f: "サンプル %d 個:推定 %.2f（真の値 0.64）" % (int(f * 63) + 1, est[int(f * 63)]), size=16, fill=INK)
    scene.TextStack(root, 50, 376, [(0.0, 20, "誤差はサンプル数の平方根に反比例。4 倍に増やして、誤差が半分。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "サンプルを 1 個ずつ追加")
    return dict(name=name, page=G + "gi/theory/monte-carlo.md", before="## モンテカルロ積分", scene=scene, size=(780, 420), times=[2.0, 4.0, 6.5, 12.0])


FIGS = [HbaoHorizon, AoRangeCheck, BilateralBlur, AoUpsample, RtaoRays, DfaoCone, SsgiBounce, ProbeBilinear, ProbeLightLeak, DdgiProbeRays, VoxelConeTrace, RestirReservoir, RadianceCascades, ShBands, MonteCarlo]
