import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

PAGE = "graphics/shadows/"


def ShadowBiasSweep():
    name = "shadow-bias-sweep"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="バイアスを増やすと:シャドウ アクネ → ちょうどよい → ピーター パンニング")
    root = scene.root
    gx, gy, cw = 60, 250, 36
    n = 16
    root.add("rect", x=gx - 10, y=gy, width=n * cw + 20, height=44, fill="#d6c7a1")
    cells = []
    for i in range(n):
        cells.append(root.add("rect", x=gx + i * cw, y=gy, width=cw - 2, height=30, fill="#fde68a"))
    # 物体と影
    bx, bw, bh = 330, 90, 90
    root.add("rect", x=bx, y=gy - bh, width=bw, height=bh, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    shadow = root.add("rect", x=bx + bw, y=gy, width=150, height=30, fill="#334155", opacity=0.75)
    gap_label = scene.Text(root, bx + bw + 6, gy - 8, "", size=12, fill=RED)
    # バイアス 0〜1
    seq = [(0.8, 0.12), (2.0, 0.12), (4.4, 0.45), (7.2, 0.45), (9.8, 1.0), (11.2, 1.0)]
    err = [0.5 * ((i * 37) % 11) / 10 for i in range(n)]
    for i, c in enumerate(cells):
        steps = []
        for t, b in seq:
            steps.append((t, "#475569" if err[i] > b * 1.4 else "#fde68a"))
        c.Steps("fill", steps)
    for idx, (t, b) in enumerate(seq):
        gap = max(0.0, b - 0.55) * 160
        if idx == 0:
            shadow.Set(t, "x", R(bx + bw + gap)); shadow.Set(t, "width", R(150 - gap))
        else:
            shadow.Ramp(seq[idx - 1][0], t, "x", R(bx + bw + gap)); shadow.Ramp(seq[idx - 1][0], t, "width", R(150 - gap))
    # スライダ
    sx, sy, sw = 60, 120, 640
    root.add("rect", x=sx, y=sy, width=sw, height=10, rx=5, fill=LIGHT)
    root.add("rect", x=sx + sw * 0.0, y=sy - 6, width=sw * 0.3, height=22, rx=4, fill=RED, fill_opacity=0.12)
    root.add("rect", x=sx + sw * 0.3, y=sy - 6, width=sw * 0.3, height=22, rx=4, fill=GREEN, fill_opacity=0.18)
    root.add("rect", x=sx + sw * 0.6, y=sy - 6, width=sw * 0.4, height=22, rx=4, fill=AMBER, fill_opacity=0.18)
    scene.Text(root, sx + sw * 0.15, sy - 14, "小さすぎ", size=12, fill=RED, anchor="middle")
    scene.Text(root, sx + sw * 0.45, sy - 14, "ちょうどよい", size=12, fill=GREEN, anchor="middle")
    scene.Text(root, sx + sw * 0.8, sy - 14, "大きすぎ", size=12, fill=AMBER, anchor="middle")
    knob = root.add("circle", cx=sx, cy=sy + 5, r=11, fill=BLUE, stroke="#ffffff", stroke_width=2)
    for idx, (t, b) in enumerate(seq):
        x = sx + sw * (b * 0.95 + 0.02)
        if idx == 0:
            knob.Set(t, "cx", R(x))
        else:
            knob.Ramp(seq[idx - 1][0], t, "cx", R(x))
    scene.Text(root, 60, 215, "地面（光が当たる面）", size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 60, 340, [(0.0, 2.0, "バイアス 0:自分の影を自分に落とす（縞模様）"), (2.0, 4.4, "バイアスを上げると、縞が消えていく…"), (4.4, 7.2, "ちょうどよい:縞が消え、影は物の足元から始まる"), (7.2, 9.8, "さらに上げると、影が物から離れていく…"), (9.8, 20, "大きすぎ:影が浮く（ピーター パンニング）")], size=17, fill=INK)
    scene.TextStack(root, 60, 372, [(0.0, 20, "縞（アクネ）は、深度の比較の誤差が原因。バイアスはその誤差より少しだけ大きくする。")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "バイアス 0 → 0.45 → 1")
    return dict(name=name, page=PAGE + "bias/index.md", before="## アクネの原因", scene=scene, size=(780, 420), times=[1.2, 3.5, 6.0, 10.5])


def PcfKernel():
    name = "pcf-kernel"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="PCF:カーネルが広いほど、影の縁がやわらかくなる")
    root = scene.root
    n, cw, ox = 22, 28, 60
    edge = 10.4
    hard = [1.0 if (i + 0.5) < edge else 0.0 for i in range(n)]  # 1 = 光が当たる? 左が影(0)
    shadowed = [0.0 if (i + 0.5) < edge else 1.0 for i in range(n)]  # 1 = 光が届く
    rows = [("カーネル 1（比較 1 回）", 1, 100), ("カーネル 3", 3, 190), ("カーネル 5", 5, 280), ("カーネル 9", 9, 370)]
    t0, step = 1.0, 0.45
    for title, k, oy in rows:
        scene.Text(root, ox, oy - 30, title, size=14, fill=INK)
        scene.Text(root, ox + n * cw + 8, oy + 28, "", size=12, fill=GRAY)
        for i in range(n):
            root.add("rect", x=ox + i * cw, y=oy - 22, width=cw - 1, height=18, fill="#334155" if shadowed[i] == 0 else "#fde68a")
        res = []
        for i in range(n):
            lo, hi = i - k // 2, i + k // 2
            vals = [shadowed[min(n - 1, max(0, j))] for j in range(lo, hi + 1)]
            res.append(sum(vals) / len(vals))
        for i in range(n):
            r = root.add("rect", x=ox + i * cw, y=oy, width=cw - 1, height=36, fill="#f1f5f9")
            r.Steps("fill", [(t0 + i * step, Hex([(0.2 + 0.78 * res[i]) * 255, (0.25 + 0.7 * res[i]) * 255, (0.35 + 0.45 * res[i]) * 255]))])
        win = root.add("rect", x=ox, y=oy - 24, width=cw * k - 1, height=64, fill="none", stroke=AMBER, stroke_width=3, opacity=0)
        win.Steps("x", [(t0 + i * step, R(ox + (i - k // 2) * cw)) for i in range(n)])
        win.Set(t0, "opacity", 1)
        win.Set(t0 + n * step, "opacity", 0)
    scene.TextStack(root, 60, 425, [(0.0, t0, "上の帯:影の判定（暗 = 影、黄 = 光）。下の帯:PCF の結果"), (t0, t0 + n * step, "橙の枠の中の判定を平均して、真ん中の画素の明るさにする"), (t0 + n * step, 20, "カーネルを広げると、縁が広くなだらか。ただし、サンプルが増えてコストも上がる")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "カーネル 1 / 3 / 5 / 9")
    return dict(name=name, page=PAGE + "pcf.md", before="## カーネルの大きさと見た目", scene=scene, size=(780, 440), times=[2.0, 5.0, 8.0, 11.0])


def PcssPenumbra():
    name = "pcss-penumbra"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="PCSS:遮蔽物が地面から離れるほど、半影が広がる")
    root = scene.root
    xl, yl, L = 360, 70, 70
    yg = 330
    a = 38
    xo = 360
    root.add("rect", x=60, y=yg, width=660, height=14, fill="#d6c7a1")
    root.add("rect", x=xl - L / 2, y=yl - 8, width=L, height=16, rx=8, fill=AMBER)
    scene.Text(root, xl + L / 2 + 10, yl + 4, "面光源", size=13, fill=AMBER)

    def Geom(yo):
        def hit(px, py, qx, qy):
            return px + (qx - px) * (yg - py) / (qy - py)
        xr_out = hit(xl - L / 2, yl, xo + a, yo)
        xr_in = hit(xl + L / 2, yl, xo + a, yo)
        xl_out = hit(xl + L / 2, yl, xo - a, yo)
        xl_in = hit(xl - L / 2, yl, xo - a, yo)
        return xl_out, xl_in, xr_in, xr_out

    umbra = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#1e293b", opacity=0.9)
    pen_l = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#1e293b", opacity=0.35)
    pen_r = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#1e293b", opacity=0.35)
    occ = root.add("rect", x=xo - a, y=200, width=2 * a, height=14, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    rays = [root.add("line", x1=xl - L / 2, y1=yl, x2=0, y2=0, stroke=AMBER, stroke_width=1.5, stroke_dasharray="5 4"),
            root.add("line", x1=xl + L / 2, y1=yl, x2=0, y2=0, stroke=AMBER, stroke_width=1.5, stroke_dasharray="5 4")]
    seq = [(0.8, 290), (2.5, 290), (6.0, 120), (7.5, 120), (10.5, 250)]
    n = 18
    prev_t = None
    states = []
    for idx in range(len(seq) - 1):
        ta, ya = seq[idx]
        tb, yb = seq[idx + 1]
        for i in range(n + 1):
            f = i / n
            t = Lerp(ta, tb, f)
            if idx > 0 and i == 0:
                continue
            states.append((t, Lerp(ya, yb, f)))
    prev = None
    for k, (t, yo) in enumerate(states):
        xl_out, xl_in, xr_in, xr_out = Geom(yo)
        pu = "%s,%s %s,%s %s,%s %s,%s" % (R(xl_in), yg, R(xr_in), yg, R(xr_in), yg + 14, R(xl_in), yg + 14)
        pl = "%s,%s %s,%s %s,%s %s,%s" % (R(xl_out), yg, R(xl_in), yg, R(xl_in), yg + 14, R(xl_out), yg + 14)
        pr = "%s,%s %s,%s %s,%s %s,%s" % (R(xr_in), yg, R(xr_out), yg, R(xr_out), yg + 14, R(xr_in), yg + 14)
        vals = [(umbra, "points", pu), (pen_l, "points", pl), (pen_r, "points", pr), (occ, "y", R(yo - 7)),
                (rays[0], "x2", R(xr_out)), (rays[0], "y2", yg), (rays[1], "x2", R(xl_out)), (rays[1], "y2", yg)]
        for node, attr, v in vals:
            if k == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    LiveText(scene, root, 60, 395, 0.8, 10.5, 24, lambda i, f: "遮蔽物の高さ %d  →  半影の幅 %d" % (yg - (states[int(f * (len(states) - 1))][1]), abs(Geom(states[int(f * (len(states) - 1))][1])[3] - Geom(states[int(f * (len(states) - 1))][1])[2])), size=15, fill=INK)
    scene.TextStack(root, 60, 372, [(0.0, 2.5, "遮蔽物が地面に近い:半影が細い（くっきり）"), (2.5, 7.5, "遮蔽物を持ち上げる…半影が広がる"), (7.5, 20, "半影の幅 ∝ (受け手までの距離 − 遮蔽物までの距離) × 光源の大きさ ÷ 遮蔽物までの距離")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "遮蔽物を持ち上げて、下ろす")
    return dict(name=name, page=PAGE + "pcss.md", before="## 3 つの手順", scene=scene, size=(780, 420), times=[1.0, 4.5, 6.5, 9.5])


def CascadeSplits():
    name = "cascade-splits"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="カスケードの分割:一様 → 対数 → 実用（混ぜる）")
    root = scene.root
    cam = (390, 372)
    near, far = 0.0, 1.0
    n_c = 4
    depth_n, depth_f = 1.0, 100.0
    cols = ["#fecaca", "#fed7aa", "#bbf7d0", "#bfdbfe"]
    top_y, bot_y = 125, 366
    half_n, half_f = 20, 300

    def Y(frac):
        return bot_y - frac * (bot_y - top_y)

    def HW(frac):
        return half_n + (half_f - half_n) * frac

    def Splits(lam):
        out = []
        for i in range(n_c + 1):
            s = i / n_c
            lin = depth_n + (depth_f - depth_n) * s
            log = depth_n * (depth_f / depth_n) ** s
            out.append(lam * log + (1 - lam) * lin)
        return out

    polys = [root.add("polygon", points="0,0 0,0 0,0 0,0", fill=cols[i], stroke="#64748b", stroke_width=1.5) for i in range(n_c)]
    root.add("circle", cx=cam[0], cy=cam[1] + 6, r=8, fill=RED)
    scene.Text(root, cam[0] + 14, cam[1] + 12, "カメラ", size=12, fill=GRAY)
    seq = [(0.8, 0.0), (3.0, 0.0), (5.5, 1.0), (7.5, 1.0), (9.5, 0.6), (11.5, 0.6)]
    n = 10
    states = []
    for idx in range(len(seq) - 1):
        ta, la = seq[idx]
        tb, lb = seq[idx + 1]
        for i in range(n + 1):
            if idx > 0 and i == 0:
                continue
            f = i / n
            states.append((Lerp(ta, tb, f), Lerp(la, lb, f)))
    prev = None
    for k, (t, lam) in enumerate(states):
        sp = Splits(lam)
        for c in range(n_c):
            f0 = (sp[c] - depth_n) / (depth_f - depth_n)
            f1 = (sp[c + 1] - depth_n) / (depth_f - depth_n)
            y0, y1 = Y(f0), Y(f1)
            pts = "%s,%s %s,%s %s,%s %s,%s" % (R(cam[0] - HW(f0)), R(y0), R(cam[0] + HW(f0)), R(y0), R(cam[0] + HW(f1)), R(y1), R(cam[0] - HW(f1)), R(y1))
            if k == 0:
                polys[c].Set(t, "points", pts)
            else:
                polys[c].Ramp(prev, t, "points", pts)
        prev = t
    scene.TextStack(root, 40, 60, [(0.0, 3.0, "λ = 0:一様（近くが粗い）"), (3.0, 7.5, "λ = 1:対数（近くが細かい）"), (7.5, 20, "λ = 0.6:実用（両方を混ぜる）")], size=17, fill=INK)
    scene.TextStack(root, 40, 90, [(0.0, 3.0, "手前のカスケードも広く、解像度が足りない"), (3.0, 7.5, "近くに細かく割り当てるが、遠くが急に大きい"), (7.5, 20, "ほとんどのエンジンは、この中間を使う")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "λ 0 → 1 → 0.6")
    return dict(name=name, page=PAGE + "cascaded.md", before="## 分割の決め方", scene=scene, size=(780, 420), times=[1.5, 4.5, 8.0, 11.0])


def ContactShadowMarch():
    name = "contact-shadow-march"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="コンタクト シャドウ:接触部の短い影を、画面空間のレイマーチで補う")
    root = scene.root
    gy = 280
    root.add("rect", x=40, y=gy, width=700, height=18, fill="#d6c7a1")
    root.add("rect", x=300, y=gy - 110, width=70, height=110, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    scene.Text(root, 335, gy - 118, "物体", size=13, fill=GRAY, anchor="middle")
    root.add("circle", cx=670, cy=70, r=14, fill=AMBER)
    scene.Text(root, 690, 64, "光", size=13, fill=AMBER)
    # シャドウ マップの粗さで、接触部に隙間
    gap = root.add("rect", x=272, y=gy, width=28, height=18, fill=RED, opacity=0)
    gap.Show(1.0, 4.6)
    scene.TextStack(root, 60, gy + 38, [(1.0, 4.6, "接触部の影が欠けている →（シャドウ マップの解像度不足）")], size=13, fill=RED)
    P = (286, gy - 4)
    steps = 9
    step_len = 16
    probe = root.add("circle", cx=P[0], cy=P[1], r=6, fill=BLUE, stroke="#ffffff", stroke_width=2, opacity=0)
    probe.Show(4.6)
    ray_dir = (0.8, -0.6)
    hits = []
    for s in range(1, steps + 1):
        px, py = P[0] + ray_dir[0] * step_len * s * 1.0, P[1] + ray_dir[1] * step_len * s * 1.0
        hits.append((px, py))
    for s, (px, py) in enumerate(hits, start=1):
        t = 5.0 + s * 0.45
        inside_obj = 300 <= px <= 370 and gy - 110 <= py <= gy
        col = RED if inside_obj else GREEN
        c = root.add("circle", cx=R(px), cy=R(py), r=5, fill=col, opacity=0)
        c.Show(t)
    last_t = 5.0 + len(hits) * 0.45
    scene.TextStack(root, 40, 60, [(0.0, 1.0, "まず、シャドウ マップで影を求める"), (1.0, 4.6, "接触部に、影の隙間ができる"), (4.6, last_t, "その画素から、光の方向へ、画面上で少しずつ進む（レイマーチ）"), (last_t, 20, "深度バッファの物体に当たった → 影！ 隙間が埋まる")], size=16, fill=INK)
    scene.TextStack(root, 40, 350, [(last_t, 20, "緑 = 光が届く点、赤 = 物体の中に入った点（影）。進む距離は短くてよい（10〜20 歩）")], size=13, fill=GRAY, weight=500)
    filled = root.add("rect", x=272, y=gy, width=28, height=18, fill="#334155", opacity=0)
    filled.Show(last_t, 20)
    scene.Note(4.6, name, "画面空間のレイマーチ")
    return dict(name=name, page=PAGE + "contact-shadows.md", before="## 原理：画面空間のレイマーチ", scene=scene, size=(780, 400), times=[1.5, 4.0, 7.0, 10.5])


def SdfCone():
    name = "sdf-soft-shadow"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="SDF のソフト シャドウ:球で安全な距離を測りながら、最小の隙間を覚える")
    root = scene.root
    obj = (330, 276, 38)
    root.add("circle", cx=obj[0], cy=obj[1], r=obj[2], fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    P = (90, 300)
    Lp = (680, 130)
    root.add("circle", cx=P[0], cy=P[1], r=7, fill=BLUE)
    scene.Text(root, P[0] - 10, P[1] + 24, "影を調べたい点", size=12, fill=GRAY)
    root.add("circle", cx=Lp[0], cy=Lp[1], r=13, fill=AMBER)
    scene.Text(root, Lp[0] - 6, Lp[1] - 20, "光", size=13, fill=AMBER)
    root.add("line", x1=P[0], y1=P[1], x2=Lp[0], y2=Lp[1], stroke="#94a3b8", stroke_width=1.5, stroke_dasharray="4 4")
    dx, dy = Lp[0] - P[0], Lp[1] - P[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    k = 8.0
    t = 8.0
    res = 1.0
    steps = []
    while t < L - 20 and len(steps) < 14:
        x, y = P[0] + ux * t, P[1] + uy * t
        d = math.hypot(x - obj[0], y - obj[1]) - obj[2]
        res = min(res, k * d / t)
        steps.append((x, y, d, res))
        if d < 1:
            break
        t += max(d, 6)
    t0, dt = 1.0, 0.8
    for i, (x, y, d, r) in enumerate(steps):
        tt = t0 + i * dt
        g = root.add("g", opacity=0)
        g.Show(tt)
        g.add("circle", cx=R(x), cy=R(y), r=R(max(min(d, 120), 2)), fill="none", stroke=GREEN, stroke_width=2, stroke_dasharray="4 3")
        g.add("circle", cx=R(x), cy=R(y), r=4, fill=GREEN)
    scene.TextStack(root, 40, 52, [(t0 + i * dt, t0 + (i + 1) * dt if i < len(steps) - 1 else 20, "ステップ %d:最も近い物までの距離 d = %.0f → それだけ進む。隙間の比 k·d/t = %.2f（最小 %.2f）" % (i + 1, d, k * d / max(1, math.hypot(x - P[0], y - P[1])), r)) for i, (x, y, d, r) in enumerate(steps)], size=13, fill=INK)
    final = steps[-1][3]
    scene.TextStack(root, 40, 390, [(t0 + len(steps) * dt, 20, "→ 影の明るさ = %.2f（最も物体に近づいた所の比で決まる）" % max(0.0, min(1.0, final)))], size=16, fill=RED)
    scene.Text(root, 40, 410, "物体のそばを通るほど、比が小さくなって濃い影。遠ければ 1（影なし）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "スフィア トレーシング")
    return dict(name=name, page=PAGE + "sdf-shadows.md", before="## ソフト シャドウの仕組み", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 11.0])


def VsmChebyshev():
    name = "vsm-chebyshev"
    scene = NewScene(name, 780, 400, duration=11.0, hold=1.5, title="VSM:平均と分散から、「光が届く割合の上限」を求める")
    root = scene.root
    mu, var = 0.5, 0.012
    ax = Axes(scene, root, 60, 80, 460, 230, 1.0, 1.0, "受け手の深度 t", "光が届く割合 p")
    pmax = lambda t: 1.0 if t <= mu else var / (var + (t - mu) ** 2)
    ax.Curve(pmax, BLUE, 4, n=100)
    # 深度の分布(ガウス)を下に
    sig = math.sqrt(var)
    gauss = lambda t: math.exp(-((t - mu) ** 2) / (2 * var))
    gp = "M" + " L".join("%s,%s" % (ax.X(i / 100), R(ax.y + ax.h - 70 * gauss(i / 100))) for i in range(101))
    root.add("path", d=gp, fill="#bfdbfe", fill_opacity=0.6, stroke=PURPLE, stroke_width=2)
    scene.Text(root, ax.X(mu), ax.y + ax.h - 78, "保存した深度の分布（平均 μ、分散 σ²）", size=12, fill=PURPLE, anchor="middle")
    root.add("line", x1=ax.X(mu), y1=ax.y, x2=ax.X(mu), y2=ax.y + ax.h, stroke=PURPLE, stroke_width=1.5, stroke_dasharray="4 3")
    dot = root.add("circle", cx=ax.X(0.2), cy=ax.Y(1.0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    line = root.add("line", x1=ax.X(0.2), y1=ax.y, x2=ax.X(0.2), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2.5)
    n = 28
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(n + 1):
        tt = 0.2 + 0.7 * i / n
        t = Lerp(t0, t1, i / n)
        if i == 0:
            dot.Set(t, "cx", ax.X(tt)); dot.Set(t, "cy", ax.Y(pmax(tt))); line.Set(t, "x1", ax.X(tt)); line.Set(t, "x2", ax.X(tt))
        else:
            dot.Ramp(prev, t, "cx", ax.X(tt)); dot.Ramp(prev, t, "cy", ax.Y(pmax(tt))); line.Ramp(prev, t, "x1", ax.X(tt)); line.Ramp(prev, t, "x2", ax.X(tt))
        prev = t
    LiveText(scene, root, 550, 130, t0, t1, n, lambda i, f: "t = %.2f" % (0.2 + 0.7 * i / n), size=20)
    LiveText(scene, root, 550, 164, t0, t1, n, lambda i, f: "p ≦ %.2f" % pmax(0.2 + 0.7 * i / n), size=20, fill=BLUE)
    scene.Text(root, 550, 214, "t ≦ μ:光が届く（p = 1）", size=13, fill=GRAY, weight=500)
    scene.Text(root, 550, 238, "t が μ より遠いほど、p は小さく", size=13, fill=GRAY, weight=500)
    scene.Text(root, 550, 262, "p = σ² / (σ² + (t − μ)²)", size=14, fill=INK)
    scene.Text(root, 60, 370, "深度そのものではなく、平均と分散（深度と深度²）を保存する。ぼかしても意味が壊れないので、フィルタが使える。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "t 0.2 → 0.9")
    return dict(name=name, page=PAGE + "vsm/index.md", before="## 影の割合：チェビシェフの不等式", scene=scene, size=(780, 400), times=[1.0, 3.5, 6.0, 9.0])


def LightBleeding():
    name = "vsm-light-bleeding"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="光漏れ:重なった 2 枚の影を、1 つの分布にすると、漏れが出る")
    root = scene.root
    d1, d2 = 0.3, 0.6
    mu = (d1 + d2) / 2
    var = ((d1 - mu) ** 2 + (d2 - mu) ** 2) / 2
    ax = Axes(scene, root, 60, 90, 440, 220, 1.0, 1.0, "受け手の深度 t", "光が届く割合")
    true_v = lambda t: 1.0 if t <= d1 else (0.5 if t <= d2 else 0.0)
    vsm = lambda t: 1.0 if t <= mu else var / (var + (t - mu) ** 2)
    ax.Curve(true_v, GREEN, 4, n=200)
    ax.Curve(vsm, RED, 4, n=100)
    scene.Text(root, ax.X(0.62), ax.Y(0.5) - 14, "VSM の見積もり（赤）", size=12, fill=RED)
    scene.Text(root, ax.X(0.62), ax.Y(0.18), "本当（緑）", size=12, fill=GREEN)
    leak = root.add("rect", x=ax.X(d2), y=ax.Y(vsm(0.62)) if False else ax.Y(0.45), width=R(ax.X(1.0) - ax.X(d2)), height=R(ax.Y(0.0) - ax.Y(0.45)), fill=RED, fill_opacity=0.12, opacity=0)
    leak.Show(5.0)
    scene.TextStack(root, ax.X(d2) + 8, ax.Y(0.45) + 22, [(5.0, 20, "ここが漏れ（本当は 0）")], size=13, fill=RED)
    dot1 = root.add("circle", cx=ax.X(0.15), cy=ax.Y(1.0), r=7, fill=GREEN, stroke="#ffffff", stroke_width=1.5)
    dot2 = root.add("circle", cx=ax.X(0.15), cy=ax.Y(1.0), r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    n = 26
    t0, t1 = 0.8, 4.8
    prev = None
    for i in range(n + 1):
        tt = 0.15 + 0.8 * i / n
        t = Lerp(t0, t1, i / n)
        if i == 0:
            dot1.Set(t, "cx", ax.X(tt)); dot1.Set(t, "cy", ax.Y(true_v(tt)))
            dot2.Set(t, "cx", ax.X(tt)); dot2.Set(t, "cy", ax.Y(vsm(tt)))
        else:
            dot1.Ramp(prev, t, "cx", ax.X(tt)); dot1.Ramp(prev, t, "cy", ax.Y(true_v(tt)))
            dot2.Ramp(prev, t, "cx", ax.X(tt)); dot2.Ramp(prev, t, "cy", ax.Y(vsm(tt)))
        prev = t
    # 右:2 枚の遮蔽物の断面
    sx = 540
    scene.Text(root, sx, 90, "ぼかした 1 テクセルの中身", size=13, fill=GRAY)
    root.add("rect", x=sx, y=110, width=180, height=22, fill="#fecaca", stroke="#e5484d", stroke_width=2)
    scene.Text(root, sx + 90, 126, "手前の遮蔽物（深度 0.3）", size=12, fill=INK, anchor="middle")
    root.add("rect", x=sx + 40, y=150, width=140, height=22, fill="#fed7aa", stroke=AMBER, stroke_width=2)
    scene.Text(root, sx + 110, 166, "奥の遮蔽物（深度 0.6）", size=12, fill=INK, anchor="middle")
    scene.Text(root, sx, 210, "平均 μ = %.2f、分散 σ² = %.3f" % (mu, var), size=13, fill=INK)
    scene.Text(root, sx, 236, "→ 1 つの山として扱うので、", size=13, fill=GRAY, weight=500)
    scene.Text(root, sx, 258, "2 枚の間の空間の情報が失われる", size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 60, 360, [(0.0, 5.0, "受け手の深度を 0.15 → 0.95 へ動かして、本当の明るさと VSM を比べる"), (5.0, 20, "奥の遮蔽物より後ろ（t > 0.6）で、VSM は明るいと答える（光漏れ）")], size=14, fill=INK)
    scene.TextStack(root, 60, 390, [(5.0, 20, "対策:p を [0.3, 1] を引き伸ばして、小さい値を 0 にする（光漏れ低減）、または MSM・EVSM")], size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "本当と VSM を比べる")
    return dict(name=name, page=PAGE + "vsm/light-bleeding.md", before="## 弱点：光漏れ", scene=scene, size=(780, 420), times=[1.5, 3.0, 6.0, 9.5])


def CubemapFaces():
    name = "point-cubemap-faces"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="点光源の影:6 方向にシャドウ マップを描く（キューブ マップ）")
    root = scene.root
    cx, cy, r = 390, 238, 118
    faces = [("+X（右）", 0, "#fecaca"), ("+Z（奥）", -90, "#bbf7d0"), ("−X（左）", 180, "#bfdbfe"), ("−Z（手前）", 90, "#fde68a")]
    wedges = []
    for label, ang, col in faces:
        a0, a1 = math.radians(ang - 45), math.radians(ang + 45)
        pts = "%s,%s %s,%s %s,%s" % (cx, cy, R(cx + r * math.cos(a0)), R(cy + r * math.sin(a0)), R(cx + r * math.cos(a1)), R(cy + r * math.sin(a1)))
        w = root.add("polygon", points=pts, fill=col, fill_opacity=0.18, stroke="#94a3b8", stroke_width=1.5)
        wedges.append((w, label, ang, col))
    objs = [(cx + 100, cy - 20, "#e5484d"), (cx - 20, cy - 105, "#2ea043"), (cx - 95, cy + 35, "#2563eb"), (cx + 40, cy + 95, "#e5aa28")]
    for (x, y, col) in objs:
        root.add("circle", cx=x, cy=y, r=15, fill=col, stroke="#ffffff", stroke_width=2)
    root.add("circle", cx=cx, cy=cy, r=13, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, cx, cy + 36, "点光源", size=12, fill=AMBER, anchor="middle")
    t0, dt = 1.0, 2.0
    for i, (w, label, ang, col) in enumerate(wedges):
        t = t0 + i * dt
        w.Set(t, "fill-opacity", 0.18)
        w.Ramp(t, t + 0.3, "fill-opacity", 0.55)
        w.Set(t + dt - 0.3, "fill-opacity", 0.55)
        w.Ramp(t + dt - 0.3, t + dt, "fill-opacity", 0.18)
        a = math.radians(ang)
        lx, ly = cx + (r + 24) * math.cos(a), cy + (r + 24) * math.sin(a)
        scene.Text(root, lx, ly + 5, label, size=14, fill=INK, anchor="middle")
        scene.TextStack(root, 60, 70, [(t, t + dt, "面 %d:%s 向きに、90° の視野でシャドウ マップを描く" % (i + 1, label.split("（")[0]))], size=17, fill=INK)
    scene.TextStack(root, 60, 390, [(t0 + 4 * dt, 20, "上（+Y）と下（−Y）も加えて 6 面。描画は 6 回（視錐台カリングで、物が無い面は省ける）")], size=14, fill=INK)
    scene.TextStack(root, 60, 70, [(t0 + 4 * dt, 20, "まとめ:光を中心に、6 つの方向へ")], size=17, fill=GREEN)
    scene.Text(root, 60, 410, "上から見た図。影を引く時は、光から見た方向ベクトルで、6 面のうちの 1 枚を選ぶ。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "4 面 + 上下")
    return dict(name=name, page=PAGE + "local-lights/point-cubemap.md", before="## 点光源：キューブ マップ", scene=scene, size=(780, 420), times=[2.0, 4.0, 6.0, 10.5])


def ShadowVolumeStencil():
    name = "shadow-volume-stencil"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="ステンシル:視線が影の体積に入ったら +1、出たら −1。残りが 1 なら影")
    root = scene.root
    eye = (50, 130)
    gy = 330
    root.add("rect", x=30, y=gy, width=720, height=14, fill="#d6c7a1")
    vol = [(300, 150), (350, 150), (560, gy), (400, gy)]
    root.add("polygon", points=" ".join("%s,%s" % p for p in vol), fill="#1e293b", fill_opacity=0.25, stroke="#475569", stroke_width=2, stroke_dasharray="6 4")
    root.add("rect", x=290, y=135, width=70, height=18, fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    root.add("circle", cx=330, cy=60, r=13, fill=AMBER)
    scene.Text(root, 350, 64, "光", size=13, fill=AMBER)
    root.add("circle", cx=eye[0], cy=eye[1], r=8, fill=BLUE)
    scene.Text(root, eye[0] - 6, eye[1] - 14, "カメラ", size=12, fill=GRAY)

    def Intersect(p, q, a, b):
        rx, ry = q[0] - p[0], q[1] - p[1]
        sx, sy = b[0] - a[0], b[1] - a[1]
        den = rx * sy - ry * sx
        if abs(den) < 1e-9:
            return None
        t = ((a[0] - p[0]) * sy - (a[1] - p[1]) * sx) / den
        u = ((a[0] - p[0]) * ry - (a[1] - p[1]) * rx) / den
        if 0 < t < 1 and 0 <= u <= 1:
            return t
        return None

    cenx = sum(p[0] for p in vol) / 4
    ceny = sum(p[1] for p in vol) / 4
    targets = [(x, gy) for x in (180, 260, 340, 420, 480, 540, 620, 700)]
    t0, dt = 1.0, 1.4
    for i, tgt in enumerate(targets):
        tt = t0 + i * dt
        hits = []
        for k in range(4):
            a, b = vol[k], vol[(k + 1) % 4]
            t = Intersect(eye, tgt, a, b)
            if t is not None:
                ex, ey = tgt[0] - eye[0], tgt[1] - eye[1]
                sx, sy = b[0] - a[0], b[1] - a[1]
                nx, ny = sy, -sx
                mx, my = (a[0] + b[0]) / 2 - cenx, (a[1] + b[1]) / 2 - ceny
                if nx * mx + ny * my < 0:
                    nx, ny = -nx, -ny
                hits.append((t, +1 if ex * nx + ey * ny < 0 else -1))
        hits.sort()
        count = 0
        g = root.add("g", opacity=0)
        g.Show(tt, tt + dt)
        g.add("line", x1=eye[0], y1=eye[1], x2=tgt[0], y2=tgt[1], stroke=BLUE, stroke_width=2.5)
        for (t, d) in hits:
            px, py = eye[0] + (tgt[0] - eye[0]) * t, eye[1] + (tgt[1] - eye[1]) * t
            count += d
            g.add("circle", cx=R(px), cy=R(py), r=9, fill=GREEN if d > 0 else RED, stroke="#ffffff", stroke_width=2)
            scene.Text(g, R(px), R(py + 4), "+1" if d > 0 else "−1", size=10, fill="#ffffff", anchor="middle")
        inside = count > 0
        g.add("circle", cx=tgt[0], cy=tgt[1], r=7, fill=RED if inside else GREEN)
        scene.Text(g, 400, 380, "この画素:ステンシル = %d → %s" % (count, "影（0 でない）" if inside else "光が当たる（0）"), size=17, fill=RED if inside else GREEN, anchor="middle")
        mark = root.add("rect", x=tgt[0] - 40, y=gy + 14, width=80, height=8, fill="#334155" if inside else "#fde68a", opacity=0)
        mark.Set(tt + dt, "opacity", 1)
    scene.Text(root, 40, 52, "カメラから各画素への視線を、順に見る（緑 +1 = 体積に入る、赤 −1 = 体積から出る）", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "視線を左から順に")
    return dict(name=name, page=PAGE + "shadow-volumes.md", before="## ステンシルによる判定", scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 12.0])


def VirtualShadowPages():
    name = "vsm-pages"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="仮想シャドウ マップ:見えている所の「ページ」だけを、細かく用意する")
    root = scene.root
    cols, rows, cw, ox, oy = 16, 10, 30, 40, 76
    tiles = {}
    for j in range(rows):
        for i in range(cols):
            tiles[(i, j)] = root.add("rect", x=ox + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
    cam_path = [(3, 8), (6, 6), (9, 4), (12, 3)]
    t0, dt = 1.5, 2.6
    colors = ["#1d4ed8", "#38bdf8", "#bae6fd"]
    for ti in range(len(cam_path)):
        pass
    for key, r in tiles.items():
        i, j = key
        steps = []
        for k, (cx, cy) in enumerate(cam_path):
            d = math.hypot(i - cx, j - cy)
            if d < 2.2:
                col = colors[0]
            elif d < 4.2:
                col = colors[1]
            elif d < 6.5:
                col = colors[2]
            else:
                col = "#f1f5f9"
            steps.append((t0 + k * dt, col))
        r.Steps("fill", steps)
    cam = root.add("circle", cx=ox + 3.5 * cw, cy=oy + 8.5 * cw, r=10, fill=RED, stroke="#ffffff", stroke_width=2)
    cam.Steps("cx", [(t0 + k * dt, R(ox + (cx + 0.5) * cw)) for k, (cx, cy) in enumerate(cam_path)])
    cam.Steps("cy", [(t0 + k * dt, R(oy + (cy + 0.5) * cw)) for k, (cx, cy) in enumerate(cam_path)])
    scene.Text(root, ox + cols * cw + 18, 110, "凡例", size=13, fill=GRAY)
    for k, (col, label) in enumerate(zip(colors, ("カメラの近く:細かいページ", "中距離:中くらい", "遠く:粗い"))):
        root.add("rect", x=ox + cols * cw + 18, y=124 + k * 28, width=22, height=18, fill=col)
        scene.Text(root, ox + cols * cw + 48, 138 + k * 28, label, size=12, fill=INK, weight=500)
    root.add("rect", x=ox + cols * cw + 18, y=124 + 3 * 28, width=22, height=18, fill="#f1f5f9", stroke="#94a3b8", stroke_width=1)
    scene.Text(root, ox + cols * cw + 48, 138 + 3 * 28, "不要（メモリを使わない）", size=12, fill=INK, weight=500)
    scene.TextStack(root, 40, 60, [(0.0, 20, "光から見た平面（上から）。赤い点 = カメラの位置（見えている場所）")], size=13, fill=GRAY, weight=500)
    scene.TextStack(root, 40, 408, [(t0 + k * dt, t0 + (k + 1) * dt if k < 3 else 20, "カメラが動くと、必要なページが入れ替わる（使い終わったページは解放）") for k in range(4)], size=14, fill=INK)
    scene.Note(t0, name, "カメラ移動でページが変わる")
    return dict(name=name, page=PAGE + "virtual-shadow-maps.md", before="## 構造", scene=scene, size=(780, 420), times=[2.0, 4.5, 7.0, 10.5])


def TexelSnapping():
    name = "texel-snapping"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="テクセルのスナップ:カメラが動いても、影の縁が揺れない")
    root = scene.root
    T = 40
    edge_x = 400
    panels = [(100, "スナップなし:カメラ移動で、格子がずれる", False), (270, "スナップあり:格子が、テクセル単位で動く", True)]
    t0, t1 = 1.0, 10.0
    n = 36
    shift_max = 2.6 * T
    for oy, title, snap in panels:
        scene.Text(root, 50, oy - 28, title, size=14, fill=RED if not snap else GREEN)
        root.add("rect", x=50, y=oy, width=680, height=70, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        lines = []
        for k in range(-1, 18):
            lines.append((root.add("line", x1=50 + k * T, y1=oy, x2=50 + k * T, y2=oy + 70, stroke="#94a3b8", stroke_width=1.5), k))
        root.add("line", x1=edge_x, y1=oy - 8, x2=edge_x, y2=oy + 78, stroke=BLUE, stroke_width=3)
        shade = root.add("rect", x=50, y=oy + 20, width=edge_x - 50, height=30, fill="#334155", opacity=0.8)
        qshade = root.add("rect", x=50, y=oy + 20, width=edge_x - 50, height=30, fill="none", stroke=AMBER, stroke_width=4)
        prev = None
        for i in range(n + 1):
            f = i / n
            t = Lerp(t0, t1, f)
            shift = shift_max * f
            if snap:
                shift = math.floor(shift / T) * T
            origin = 50 - (shift % T) if not snap else 50
            # 格子の原点(テクセル境界)の絶対位置
            grid0 = 50 - (shift % T)
            if snap:
                grid0 = 50
            q = grid0 + math.ceil((edge_x - grid0) / T) * T  # 影の縁は、次のテクセル境界に量子化される
            for node, k in lines:
                x = grid0 + k * T
                if i == 0:
                    node.Set(t, "x1", R(x)); node.Set(t, "x2", R(x))
                else:
                    node.Ramp(prev, t, "x1", R(x)); node.Ramp(prev, t, "x2", R(x))
            if i == 0:
                qshade.Set(t, "width", R(q - 50))
            else:
                qshade.Ramp(prev, t, "width", R(q - 50))
            prev = t
    scene.Text(root, edge_x + 6, 98, "本当の影の縁", size=12, fill=BLUE)
    scene.Text(root, 50, 200, "橙の枠 = シャドウ マップで見える影の範囲（テクセル境界に切り上がる）", size=12, fill=AMBER, weight=500)
    scene.TextStack(root, 50, 372, [(0.0, 20, "上:縁がテクセル境界をまたぐたびに揺れる。下:整数テクセルで動くので揺れない。")], size=13, fill=GRAY, weight=500)
    scene.Note(t0, name, "カメラを右へ移動")
    return dict(name=name, page=PAGE + "cascaded.md", before="## テクセルのスナップ", scene=scene, size=(780, 420), times=[1.5, 4.0, 7.0, 10.0])


FIGS = [ShadowBiasSweep, PcfKernel, PcssPenumbra, CascadeSplits, ContactShadowMarch, SdfCone, VsmChebyshev, LightBleeding, CubemapFaces, ShadowVolumeStencil, VirtualShadowPages, TexelSnapping]
