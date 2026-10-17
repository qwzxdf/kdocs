import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402
from pp5 import FirstH  # noqa: E402

PAGE = "graphics/shadows/"


def PathD(pts, close=False):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts) + (" Z" if close else "")


def SlopeBias():
    name = "slope-bias"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="スロープ スケール バイアス:傾いた面ほど、必要なバイアスは大きい")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 360, 230, 80.0, 1.0, "面の傾き（光に対して、度）", "必要なバイアス")
    need = lambda a: min(1.0, math.tan(math.radians(a)) / 4.0)
    ax.Curve(need, BLUE, 4, n=80)
    ax.Curve(lambda a: 0.25, RED, 3, n=2, dash="6 4")
    scene.Text(root, ax.X(52), ax.Y(0.25) - 8, "定数バイアス（一定）", size=12, fill=RED)
    scene.Text(root, ax.X(8), ax.Y(0.9), "傾きに比例して増やす（青）", size=12, fill=BLUE)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK, stroke="#ffffff", stroke_width=1.5)
    Sweep(dot, ax, need, 0.8, 10.5, 0.0, 78.0, 28)
    # 右:テクセルと面
    sx, sy = 470, 300
    for k in range(4):
        root.add("line", x1=sx + k * 70, y1=130, x2=sx + k * 70, y2=sy + 10, stroke=LIGHT, stroke_width=1.5)
    surf = root.add("line", x1=sx, y1=sy, x2=sx + 270, y2=sy, stroke="#b8794b", stroke_width=6)
    err = root.add("line", x1=sx + 140, y1=sy, x2=sx + 140, y2=sy, stroke=RED, stroke_width=4)
    scene.Text(root, sx, 120, "シャドウ マップの 1 テクセル（縦線の間）", size=12, fill=GRAY)
    steps = 28
    t0, t1 = 0.8, 10.5
    prev = None
    for i in range(steps + 1):
        f = i / steps
        a = 78 * f
        th = math.radians(a)
        L = 270
        ey = sy - math.tan(th) * 35
        t = Lerp(t0, t1, f)
        # 面の傾き:左端を固定して、右端を上げる
        yr = sy - min(110, math.tan(th) * 70)
        vals = [(surf, "y1", R(sy + (sy - yr) * 0.5)), (surf, "y2", R(yr - (sy - yr) * 0.0)), (err, "y1", R(sy)), (err, "y2", R(sy - min(100, math.tan(th) * 35)))]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    LiveText(scene, root, 60, 350, t0, t1, steps, lambda i, f: "傾き %d° → 必要なバイアス ∝ tan = %.1f" % (78 * f, math.tan(math.radians(78 * f))), size=15, fill=INK)
    scene.Text(root, 60, 384, "テクセルの中で、面の深度は、傾きに比例して変わる（赤い線の長さ）。それ以上のバイアスが要る。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "傾き 0 → 78°")
    return dict(name=name, page=PAGE + "bias/slope-scale-bias.md", before=FirstH(PAGE + "bias/slope-scale-bias.md"), scene=scene, size=(780, 420), times=[1.0, 4.0, 7.0, 10.0])


def NormalOffset():
    name = "normal-offset"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="法線オフセット:受ける点を、法線方向へ少しずらしてから、深度を比べる")
    root = scene.root
    sx, sy = 60, 280
    slope = -0.22
    root.add("line", x1=sx, y1=sy, x2=sx + 640, y2=sy + slope * 640, stroke="#b8794b", stroke_width=6)
    T = 80
    for k in range(9):
        root.add("line", x1=sx + k * T, y1=110, x2=sx + k * T, y2=340, stroke=LIGHT, stroke_width=1.5, stroke_dasharray="4 3")
    pts = []
    n = 16
    for i in range(n):
        x = sx + 20 + i * 40
        y = sy + slope * (x - sx)
        # 法線(面に垂直、上向き)
        ln = math.hypot(1, slope)
        nx, ny = slope / ln, -1 / ln
        d = root.add("circle", cx=R(x), cy=R(y), r=6, fill=GREEN, stroke="#ffffff", stroke_width=1.5)
        pts.append((d, x, y, nx, ny, i))
        a = root.add("line", x1=R(x), y1=R(y), x2=R(x + nx * 22), y2=R(y + ny * 22), stroke=GRAY, stroke_width=1.5, opacity=0.6)
    seq = [(0.8, 0.0), (2.5, 0.0), (7.5, 1.0), (10.0, 1.0)]
    for (d, x, y, nx, ny, i) in pts:
        # テクセル中心との位置差が正の画素ほど、アクネ(赤)になりやすい
        frac = ((x - sx) % T) / T
        err = frac  # 0〜1
        steps = []
        for t, k in seq:
            steps.append((t, RED if err > k * 0.8 else GREEN))
        d.Steps("fill", steps)
        for idx, (t, k) in enumerate(seq):
            vx, vy = R(x + nx * 22 * k), R(y + ny * 22 * k)
            if idx == 0:
                d.Set(t, "cx", vx); d.Set(t, "cy", vy)
            else:
                d.Ramp(seq[idx - 1][0], t, "cx", vx); d.Ramp(seq[idx - 1][0], t, "cy", vy)
    scene.TextStack(root, 60, 70, [(0.0, 2.5, "面上の点（赤 = 自己遮蔽のアクネ、緑 = OK）。矢印は法線"), (2.5, 7.5, "法線方向に、ずらしていく…"), (7.5, 20, "光に近い側へ持ち上げたので、アクネが消えた")], size=15, fill=INK)
    scene.Text(root, 60, 380, "深度ではなく「位置」をずらすので、傾きによらず効く。ずらしすぎると、影の位置が、わずかにずれる。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "オフセット 0 → 1")
    return dict(name=name, page=PAGE + "bias/normal-offset.md", before=FirstH(PAGE + "bias/normal-offset.md"), scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.5])


def FrontFaceCull():
    name = "front-face-cull"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="前面カリング:裏面の深度を、シャドウ マップに入れる")
    root = scene.root
    panels = [(40, "表面を描く（通常）", False), (410, "裏面を描く（前面カリング）", True)]
    for px, title, back in panels:
        scene.Text(root, px + 160, 80, title, size=14, fill=RED if not back else GREEN, anchor="middle")
        root.add("rect", x=px + 90, y=130, width=140, height=150, fill="#b8794b", fill_opacity=0.5, stroke="#7a4b2a", stroke_width=2)
        root.add("circle", cx=px + 40, cy=100, r=12, fill=AMBER)
        root.add("line", x1=px + 40, y1=100, x2=px + 120, y2=130, stroke=AMBER, stroke_width=2, stroke_dasharray="5 4")
        root.add("line", x1=px, y1=330, x2=px + 330, y2=330, stroke="#a8a29e", stroke_width=3)
        # 記録される深度(線)
        ys = 130 if not back else 280
        g = root.add("g", opacity=0)
        g.Show(1.0 if not back else 5.0)
        g.add("line", x1=px + 90, y1=ys, x2=px + 230, y2=ys, stroke=RED if not back else GREEN, stroke_width=5)
        scene.Text(g, px + 160, ys + (-10 if not back else 24), "記録される深度" + ("（表面）" if not back else "（裏面）"), size=12, fill=RED if not back else GREEN, anchor="middle")
        # 受ける点(上面)
        d = root.add("circle", cx=px + 160, cy=130, r=7, fill="#ffffff", stroke=INK, stroke_width=3, opacity=0)
        d.Show(2.0 if not back else 6.0)
        txt = "上面の点:記録と同じ深度 → 誤差で、縞（アクネ）が出る" if not back else "上面の点:記録（裏面）よりずっと手前 → 余裕があり、縞が出ない"
        scene.TextStack(root, px, 366, [(2.5 if not back else 6.5, 20, txt)], size=12, fill=INK, weight=500)
    scene.Text(root, 40, 396, "代償:薄い板（厚みが無い物）では、裏面が表面に近く、余裕が足りない（光漏れしやすい）。", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "表面 → 裏面")
    return dict(name=name, page=PAGE + "bias/front-face-culling.md", before=FirstH(PAGE + "bias/front-face-culling.md"), scene=scene, size=(780, 420), times=[1.5, 3.5, 6.5, 10.5])


def DualParaboloid():
    name = "dual-paraboloid"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="デュアル パラボロイド:放物面の鏡で、半球を 1 枚の画像に集める")
    root = scene.root
    ox, oy = 280, 330
    sc = 200

    def Z(x):
        return (1 - x * x) / 2.0

    pts = [(ox + x * sc, oy - Z(x) * sc * 0.0 - (0.5 - Z(x)) * 0 + 0) for x in []]
    curve = []
    for k in range(-40, 41):
        x = k / 40
        curve.append((ox + x * sc * 0.85, oy - (0.5 + 0.5 * (1 - x * x) - 0.5) * sc * 0.0 - (0.5 * (1 - x * x)) * sc * 0.0))
    # 放物線(上向きの開口):y = oy - (c + 1/(2) (1 - ...)) を、頂点が原点の上に来る形で描く
    par = []
    for k in range(-48, 49):
        x = k / 48
        par.append((ox + x * 160, oy - 40 - (1 - x * x) * 0 - (x * x) * 0 - (0.5 - 0.5 * x * x) * 0 - (1 - x * x) * 70))
    # 簡単のため、放物線 y = -(x^2)*k + c  (向き:上が開口)
    par = [(ox + (k / 48) * 170, oy - 60 - 120 * (1 - (k / 48) ** 2)) for k in range(-48, 49)]
    root.add("path", d=PathD(par), fill="none", stroke=INK, stroke_width=4)
    scene.Text(root, ox, oy - 205, "放物面（鏡）", size=12, fill=GRAY, anchor="middle")
    root.add("circle", cx=ox, cy=oy - 20, r=8, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, ox + 14, oy - 12, "光（焦点）", size=12, fill=AMBER)
    mapy = 88
    root.add("line", x1=ox - 200, y1=mapy, x2=ox + 200, y2=mapy, stroke=BLUE, stroke_width=3)
    scene.Text(root, ox - 200, mapy - 10, "1 枚の画像（-1 〜 1）", size=12, fill=BLUE)
    ray = root.add("line", x1=ox, y1=oy - 20, x2=ox, y2=oy - 20, stroke=AMBER, stroke_width=3)
    up = root.add("line", x1=ox, y1=oy - 20, x2=ox, y2=mapy, stroke=GREEN, stroke_width=3)
    hit = root.add("circle", cx=ox, cy=oy - 20, r=6, fill=RED)
    steps = 30
    t0, t1 = 0.8, 11.0
    prev = None
    for i in range(steps + 1):
        f = i / steps
        th = math.radians(8 + 164 * f)  # 光から見た方向(左 8° ... 右 172°)
        # 焦点(ox, oy-20) から放物線との交点を求める(数値)
        best = None
        for s in range(1, 600):
            r = s * 0.6
            x = ox + r * math.cos(th)
            y = oy - 20 - r * math.sin(th)
            py = oy - 60 - 120 * (1 - ((x - ox) / 170) ** 2)
            if y <= py:
                best = (x, y)
                break
        if best is None:
            best = (ox + 170 * math.cos(th), oy - 80)
        hx, hy = best
        t = Lerp(t0, t1, f)
        vals = [(ray, "x2", R(hx)), (ray, "y2", R(hy)), (up, "x1", R(hx)), (up, "y1", R(hy)), (up, "x2", R(hx)), (hit, "cx", R(hx)), (hit, "cy", R(hy))]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    scene.TextStack(root, 40, 52, [(0.0, 20, "光から出る光線（橙）が、放物面で反射して、まっすぐ上（緑）へ → 画像の座標になる")], size=14, fill=INK)
    scene.Text(root, 40, 380, "半球（180°）を 1 枚に。もう 1 枚で反対側の半球 → 2 枚で全方向。キューブマップ（6 枚）より少ないが、継ぎ目で歪みやすい。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "方向を 8° → 172°")
    return dict(name=name, page=PAGE + "local-lights/dual-paraboloid.md", before=FirstH(PAGE + "local-lights/dual-paraboloid.md"), scene=scene, size=(780, 420), times=[1.5, 4.0, 7.0, 10.0])


def ManyLightsCache():
    name = "many-lights-cache"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="多数のライトの影:毎フレーム、少しずつ更新して、予算に収める")
    root = scene.root
    cols, rows = 6, 3
    cw, ch, ox, oy = 100, 90, 50, 100
    cells = []
    for j in range(rows):
        for i in range(cols):
            k = j * cols + i
            dyn = k in (1, 8, 14)
            r = root.add("rect", x=ox + i * (cw + 14), y=oy + j * (ch + 14), width=cw, height=ch, rx=8, fill="#e0f2fe", stroke="#38bdf8", stroke_width=2)
            scene.Text(root, ox + i * (cw + 14) + cw / 2, oy + j * (ch + 14) + 28, "ライト %d" % (k + 1), size=13, fill=INK, anchor="middle")
            scene.Text(root, ox + i * (cw + 14) + cw / 2, oy + j * (ch + 14) + 52, "動く" if dyn else "静止", size=12, fill=RED if dyn else GRAY, anchor="middle", weight=700 if dyn else 500)
            cells.append((r, k, dyn))
    t_frame = 0.8
    nframes = 14
    per_frame = 3
    nlights = rows * cols
    queue = 0
    for f in range(nframes):
        t = 0.8 + f * 0.75
        upd = set()
        for k, (r, kk, dyn) in enumerate(cells):
            if dyn:
                upd.add(kk)
        take = [k for k in range(nlights) if k not in upd]
        picks = [take[(queue + s) % len(take)] for s in range(max(0, per_frame - len(upd)))]
        queue += len(picks)
        for (r, kk, dyn) in cells:
            if kk in upd or kk in picks:
                r.Steps("fill", []) if False else None
    for (r, k, dyn) in cells:
        steps = []
        queue2 = 0
        for f in range(nframes):
            t = 0.8 + f * 0.75
            upd = {kk for (_, kk, d) in cells if d}
            take = [x for x in range(nlights) if x not in upd]
            picks = [take[(f * max(1, per_frame - len(upd)) + s) % len(take)] for s in range(max(0, per_frame - len(upd)))]
            steps.append((t, "#fde68a" if (k in upd or k in picks) else "#e0f2fe"))
        r.Steps("fill", steps)
    scene.TextStack(root, 50, 66, [(0.0, 20, "黄色 = このフレームで、シャドウ マップを描き直したライト。他は、前のフレームの結果を使い回す")], size=14, fill=INK)
    scene.Text(root, 50, 366, "動くライト（赤い文字）は、毎フレーム更新。静止したライトは、順番に（ラウンド ロビン）、数個ずつ更新する。", size=13, fill=GRAY, weight=500)
    scene.Text(root, 50, 390, "1 フレームに描くシャドウ マップの数に、上限を決める → コストが一定になる。", size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "フレームごとの更新")
    return dict(name=name, page=PAGE + "local-lights/many-lights.md", before=FirstH(PAGE + "local-lights/many-lights.md"), scene=scene, size=(780, 420), times=[1.0, 3.0, 5.0, 8.0])


def BlobPlanar():
    name = "blob-planar"
    scene = NewScene(name, 780, 440, duration=12.0, hold=0.0, title="簡易な影:ブロブ（丸い影）と、平面投影")
    root = scene.root
    # 左:ブロブ
    scene.Text(root, 190, 80, "ブロブ:高さで、大きさと濃さを変える", size=13, fill=INK, anchor="middle")
    root.add("rect", x=40, y=310, width=300, height=14, fill="#d6c7a1")
    blob = root.add("ellipse", cx=190, cy=316, rx=34, ry=8, fill="#000000", fill_opacity=0.6)
    ball = root.add("circle", cx=190, cy=300, r=22, fill=RED, stroke="#ffffff", stroke_width=2)
    seq = [(0.8, 0.0), (3.0, 0.0), (5.0, 1.0), (7.0, 0.0), (9.0, 0.0)]
    for idx, (t, h) in enumerate(seq):
        y = 300 - h * 160
        rx = 34 + h * 26
        op = 0.6 * (1 - h * 0.7)
        vals = [(ball, "cy", R(y)), (blob, "rx", R(rx)), (blob, "fill-opacity", R(op))]
        for node, attr, v in vals:
            if idx == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(seq[idx - 1][0], t, attr, v)
    scene.TextStack(root, 40, 360, [(0.0, 3.0, "地面にいる:小さく濃い影"), (3.0, 5.0, "ジャンプ…"), (5.0, 7.0, "高い:大きく薄い影"), (7.0, 20, "着地:また小さく濃い")], size=14, fill=INK)
    # 右:平面投影
    px = 420
    scene.Text(root, 570, 80, "平面投影:行列で、地面に押しつぶす", size=13, fill=INK, anchor="middle")
    gy = 310
    root.add("rect", x=px, y=gy, width=300, height=14, fill="#d6c7a1")
    box = [(px + 110, gy - 90), (px + 170, gy - 90), (px + 170, gy - 30), (px + 110, gy - 30)]
    root.add("polygon", points=" ".join("%s,%s" % p for p in box), fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    sh = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#000000", fill_opacity=0.5)
    sun = root.add("circle", cx=px + 40, cy=110, r=12, fill=AMBER)
    sun_seq = [(0.8, 40), (4.0, 40), (8.0, 250), (11.5, 250)]
    for idx, (t, sx_) in enumerate(sun_seq):
        sy_ = 110
        pts = []
        for (bx, by) in box:
            # 光 (sx_,sy_) から (bx,by) を通って、地面 y=gy へ
            k = (gy - sy_) / (by - sy_)
            pts.append((px + sx_ + (bx - px - sx_) * k, gy))
        # 影の多角形 = 地面上の 4 点 + 接地(箱の下辺)
        xs = [p[0] for p in pts]
        poly = "%s,%s %s,%s %s,%s %s,%s" % (R(min(xs)), gy, R(max(xs)), gy, R(max(xs)), gy + 6, R(min(xs)), gy + 6)
        # 影は地面上の線分(横から見た図):厚み 6 の帯にして表す
        if idx == 0:
            sh.Set(t, "points", poly)
            sun.Set(t, "cx", px + sx_)
        else:
            sh.Ramp(sun_seq[idx - 1][0], t, "points", poly)
            sun.Ramp(sun_seq[idx - 1][0], t, "cx", px + sx_)
    scene.TextStack(root, 420, 360, [(0.0, 20, "光の向きに沿って、物の頂点を地面へ投影した所が、影")], size=13, fill=INK)
    scene.Text(root, 40, 410, "どちらもシャドウ マップなしで描ける、安い影。地面が平らな場合に有効（段差や他の物には落ちない）。", size=12, weight=500, fill=GRAY)
    scene.Note(0.8, name, "ブロブ / 平面投影")
    return dict(name=name, page=PAGE + "special-cases/blob-planar.md", before=FirstH(PAGE + "special-cases/blob-planar.md"), scene=scene, size=(780, 440), times=[1.0, 4.0, 6.0, 10.0])


def StipplePattern():
    name = "stipple-shadow"
    scene = NewScene(name, 780, 400, duration=12.0, hold=0.0, title="半透明の影:ステッポリング（点描）で、濃さを点の数で表す")
    root = scene.root
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    cols, rows, cw, ox, oy = 16, 8, 24, 60, 90
    alphas = [0.1, 0.3, 0.5, 0.7, 0.9]
    t0, dt = 1.0, 2.2
    for j in range(rows):
        for i in range(cols):
            thr = (bayer[j % 4][i % 4] + 0.5) / 16
            r = root.add("rect", x=ox + i * cw, y=oy + j * cw, width=cw - 1, height=cw - 1, fill="#f1f5f9")
            r.Steps("fill", [(t0 + k * dt, "#1e293b" if a > thr else "#f1f5f9") for k, a in enumerate(alphas)])
    scene.TextStack(root, 60, 56, [(t0 + k * dt, t0 + (k + 1) * dt if k < 4 else 20, "影の濃さ（アルファ）%.1f → 黒くする画素の割合 ≒ %d %%" % (a, round(a * 100))) for k, a in enumerate(alphas)], size=16, fill=INK)
    # 右下:ぼかし後(平均)のイメージ
    scene.Text(root, 60, 330, "ディザ(4×4 の閾値表)で、画素ごとに「影にする・しない」を決める。", size=13, fill=GRAY, weight=500)
    scene.Text(root, 60, 354, "PCF でぼかすと、点が混ざって、薄い影に見える。アルファ ブレンドの影より安く、ソートも不要。", size=13, fill=GRAY, weight=500)
    sw = root.add("rect", x=520, y=300, width=200, height=34, fill="#f1f5f9", stroke="#94a3b8", stroke_width=1.5)
    sw.Steps("fill", [(t0 + k * dt, Hex([255 - 225 * a, 255 - 225 * a, 255 - 215 * a])) for k, a in enumerate(alphas)])
    scene.Text(root, 620, 292, "ぼかした結果", size=12, fill=GRAY, anchor="middle")
    scene.Note(t0, name, "アルファ 0.1 → 0.9")
    return dict(name=name, page=PAGE + "special-cases/translucent-shadows.md", before="### ステッポリングの例", scene=scene, size=(780, 400), times=[1.5, 3.5, 5.5, 9.5])


def EsmExp():
    name = "esm-exp"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="ESM:深度の差を、指数で影の濃さに変える")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 400, 230, 1.0, 1.0, "受ける点の深度 − 遮蔽物の深度", "光が届く割合")
    cs = [(0.8, 8.0), (3.5, 8.0), (6.5, 40.0), (9.0, 40.0), (11.5, 20.0)]
    f = lambda d, c: min(1.0, math.exp(-c * max(0.0, d)))
    p = root.add("path", d=ax.D(lambda d: f(d, 8.0), n=80), fill="none", stroke=BLUE, stroke_width=4)
    for idx in range(1, len(cs)):
        ta, ca = cs[idx - 1]
        tb, cb = cs[idx]
        p.Ramp(ta, tb, "d", ax.D(lambda d, cb=cb: f(d, cb), n=80))
    scene.TextStack(root, 500, 130, [(0.0, 3.5, "c = 8（小さい）"), (3.5, 6.5, "c を上げていくと…"), (6.5, 9.0, "c = 40（大きい）"), (9.0, 20, "c = 20（中間）")], size=20, fill=INK)
    scene.TextStack(root, 500, 164, [(0.0, 3.5, "影の縁がなだらか。ただし、接触部で、光が漏れる"), (6.5, 9.0, "影が硬く、くっきり。ただし、数値が不安定になる"), (9.0, 20, "ほどよい。実用では 20〜80 付近")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 250, "光が届く割合 = exp(−c × (d − z))", size=14, fill=BLUE)
    scene.Text(root, 500, 280, "遮蔽物（深度 z）のすぐ後ろ（d − z ≒ 0）は 1、", size=12, fill=GRAY, weight=500)
    scene.Text(root, 500, 302, "離れるほど 0 に近づく。事前にぼかせる（線形のフィルタ）。", size=12, fill=GRAY, weight=500)
    scene.Note(0.8, name, "c 8 → 40 → 20")
    return dict(name=name, page=PAGE + "vsm/esm.md", before=FirstH(PAGE + "vsm/esm.md"), scene=scene, size=(780, 420), times=[1.5, 4.5, 7.5, 11.0])


def EvsmWarp():
    name = "evsm-warp"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="EVSM:深度を、2 つの指数で変形して、光漏れを抑える")
    root = scene.root
    ax = Axes(scene, root, 60, 80, 400, 230, 1.0, 1.0, "深度（0 = 近い、1 = 遠い）", "変形後の値（正規化）")
    cs = [(0.8, 2.0), (3.5, 2.0), (7.0, 8.0), (9.5, 8.0), (11.5, 4.0)]
    pos = lambda d, c: (math.exp(c * d) - 1) / (math.exp(c) - 1)
    neg = lambda d, c: (1 - math.exp(-c * d)) / (1 - math.exp(-c))
    p1 = root.add("path", d=ax.D(lambda d: pos(d, 2.0), n=60), fill="none", stroke=BLUE, stroke_width=4)
    p2 = root.add("path", d=ax.D(lambda d: neg(d, 2.0), n=60), fill="none", stroke=RED, stroke_width=4)
    ax.Curve(lambda d: d, GRAY, 2.5, n=2, dash="5 4")
    for idx in range(1, len(cs)):
        ta, ca = cs[idx - 1]
        tb, cb = cs[idx]
        p1.Ramp(ta, tb, "d", ax.D(lambda d, cb=cb: pos(d, cb), n=60))
        p2.Ramp(ta, tb, "d", ax.D(lambda d, cb=cb: neg(d, cb), n=60))
    scene.Text(root, ax.X(0.62), ax.Y(0.18), "exp(+c d)（青）", size=12, fill=BLUE)
    scene.Text(root, ax.X(0.12), ax.Y(0.85), "−exp(−c d)（赤）", size=12, fill=RED)
    scene.TextStack(root, 500, 130, [(0.0, 3.5, "c = 2:ほぼ線形"), (3.5, 7.0, "c を上げる…"), (7.0, 9.5, "c = 8:近い所を強調（青）／遠い所を強調（赤）"), (9.5, 20, "c = 4:実用的な値")], size=15, fill=INK)
    scene.Text(root, 500, 250, "2 つの変形で、モーメントを持つ。", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 274, "片方は光漏れに強く、もう片方は逆側に強い。", size=13, fill=GRAY, weight=500)
    scene.Text(root, 500, 298, "両方の結果の「小さい方」を使う。", size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "c 2 → 8 → 4")
    return dict(name=name, page=PAGE + "vsm/evsm.md", before=FirstH(PAGE + "vsm/evsm.md"), scene=scene, size=(780, 420), times=[1.5, 4.5, 8.0, 11.0])


def RtShadowSamples():
    name = "rt-shadow-samples"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="レイトレの影:面光源に向けた複数のレイで、半影を作る")
    root = scene.root
    Lx0, Lx1, Ly = 250, 530, 80
    root.add("rect", x=Lx0, y=Ly - 8, width=Lx1 - Lx0, height=16, rx=8, fill=AMBER)
    scene.Text(root, Lx1 + 12, Ly + 4, "面光源", size=12, fill=AMBER)
    occ = (350, 180, 500, 196)
    root.add("rect", x=occ[0], y=occ[1], width=occ[2] - occ[0], height=occ[3] - occ[1], fill="#b8794b", stroke="#7a4b2a", stroke_width=2)
    gy = 340
    root.add("rect", x=40, y=gy, width=700, height=14, fill="#d6c7a1")
    P = (560, gy)
    root.add("circle", cx=P[0], cy=P[1], r=8, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, P[0] + 12, P[1] - 12, "調べる点（半影の中）", size=12, fill=BLUE)

    def Visible(lx):
        # P から (lx, Ly) への線分が、遮蔽物の矩形を通るか
        for s in range(41):
            f = s / 40
            x = P[0] + (lx - P[0]) * f
            y = P[1] + (Ly - P[1]) * f
            if occ[0] <= x <= occ[2] and occ[1] <= y <= occ[3]:
                return False
        return True

    plans = [(1, [0.5]), (4, [0.12, 0.37, 0.63, 0.88]), (16, [(k + 0.5) / 16 for k in range(16)])]
    t0, dt = 1.0, 3.6
    for k, (n, us) in enumerate(plans):
        tk = t0 + k * dt
        g = root.add("g", opacity=0)
        g.Show(tk, tk + dt)
        vis = 0
        for u in us:
            lx = Lx0 + (Lx1 - Lx0) * u
            ok = Visible(lx)
            vis += 1 if ok else 0
            g.add("line", x1=P[0], y1=P[1], x2=R(lx), y2=Ly, stroke=GREEN if ok else RED, stroke_width=2 if n > 1 else 3)
            g.add("circle", cx=R(lx), cy=Ly, r=4, fill=GREEN if ok else RED)
        v = vis / n
        scene.Text(g, 60, 76, "レイ %d 本:見えた %d 本 → 光 %d %%" % (n, vis, round(100 * v)), size=17, fill=INK)
        sw = g.add("rect", x=600, y=380, width=100, height=26, fill=Gray(v), stroke="#94a3b8", stroke_width=1.5)
        scene.Text(g, 580, 398, "結果", size=12, fill=GRAY, anchor="end")
    scene.Text(root, 40, 400, "レイが少ないと、0 か 1 のノイズ。増やすほど、なめらかな半影に近づく（デノイズで補う）。", size=12, weight=500, fill=GRAY)
    scene.Note(t0, name, "レイ 1 → 4 → 16")
    return dict(name=name, page=PAGE + "ray-traced.md", before="## 半影：面光源のサンプリング", scene=scene, size=(780, 420), times=[2.0, 5.5, 9.0, 11.5])


def LightFrustum():
    name = "light-frustum"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="光の行列:平行光は「箱」、スポットは「錐」でシーンを捉える")
    root = scene.root
    root.add("rect", x=40, y=300, width=700, height=14, fill="#d6c7a1")
    for (x, h) in ((220, 70), (360, 110), (480, 60), (590, 90)):
        root.add("rect", x=x, y=300 - h, width=34, height=h, fill="#b8794b", stroke="#7a4b2a", stroke_width=1.5)
    poly = root.add("polygon", points="0,0 0,0 0,0 0,0", fill=BLUE, fill_opacity=0.12, stroke=BLUE, stroke_width=3)
    src = root.add("circle", cx=390, cy=70, r=12, fill=AMBER, stroke="#ffffff", stroke_width=2)
    scene.Text(root, 410, 66, "光", size=13, fill=AMBER)
    # 箱(平行光) → 台形(スポット)
    box = [(180, 90), (600, 90), (600, 300), (180, 300)]
    cone = [(380, 90), (400, 90), (680, 300), (100, 300)]
    cone2 = [(385, 90), (395, 90), (600, 300), (180, 300)]
    pts_box = [(160, 90), (620, 90), (620, 305), (160, 305)]
    pts_cone = [(370, 90), (410, 90), (640, 305), (140, 305)]
    seq = [(0.8, pts_box), (4.0, pts_box), (7.0, pts_cone), (11.0, pts_cone)]
    for idx, (t, pts) in enumerate(seq):
        v = " ".join("%s,%s" % p for p in pts)
        if idx == 0:
            poly.Set(t, "points", v)
        else:
            poly.Ramp(seq[idx - 1][0], t, "points", v)
    scene.TextStack(root, 40, 56, [(0.0, 4.0, "平行光（太陽）:光線は平行 → 正射影（箱）。範囲が一定"), (4.0, 7.0, "光を近くへ（点光源・スポットライト）…"), (7.0, 20, "スポットライト:光線は 1 点から広がる → 透視投影（錐）")], size=15, fill=INK)
    scene.Text(root, 40, 360, "この箱 / 錐が、シャドウ マップに映る範囲。範囲を狭くするほど、1 テクセルあたりの解像度が上がる。", size=13, weight=500, fill=GRAY)
    scene.Note(0.8, name, "箱 → 錐")
    return dict(name=name, page=PAGE + "shadow-map-basics/light-matrix.md", before="### 平行光（太陽）：正射影", scene=scene, size=(780, 420), times=[1.0, 3.0, 5.5, 9.5])


def PerspectiveAliasing():
    name = "perspective-aliasing"
    scene = NewScene(name, 780, 420, duration=11.0, hold=0.0, title="遠近エイリアシング:近くはテクセルが粗く、遠くは細かすぎる")
    root = scene.root
    gy = 330
    root.add("rect", x=40, y=gy, width=700, height=14, fill="#d6c7a1")
    cam = (70, 150)
    root.add("circle", cx=cam[0], cy=cam[1], r=9, fill=BLUE)
    scene.Text(root, cam[0] - 10, cam[1] - 14, "カメラ", size=12, fill=BLUE)
    # シャドウ マップのテクセル(地面上で等間隔)
    T = 28
    for k in range(0, 24):
        x = 140 + k * T
        root.add("line", x1=x, y1=gy + 14, x2=x, y2=gy + 26, stroke=RED, stroke_width=2)
    scene.Text(root, 140, gy + 44, "赤い目盛り = シャドウ マップのテクセル（地面上で等間隔）", size=12, fill=RED, weight=500)
    # 画面の画素(画面を等間隔に分けたレイ)
    n = 16
    for i in range(n):
        ang = math.radians(8 + i * (62 / (n - 1)))
        dx, dy = math.cos(ang), math.sin(ang)
        t = (gy - cam[1]) / dy
        hx = cam[0] + dx * t
        ln = root.add("line", x1=cam[0], y1=cam[1], x2=R(hx), y2=gy, stroke=BLUE, stroke_width=1.5, opacity=0)
        ln.Show(1.0 + i * 0.3)
    scene.TextStack(root, 40, 56, [(0.0, 1.0, "画面の画素（青い線）は、等間隔に並ぶ"), (1.0, 6.0, "近く:1 画素が、地面の狭い範囲 → 1 テクセルに画素が何個も入る（粗い・ブロック状）"), (6.0, 20, "遠く:1 画素が、地面の広い範囲 → 画素にテクセルが何個も入る（細かすぎて、ちらつく）")], size=14, fill=INK)
    scene.Text(root, 40, 396, "対策:カスケード シャドウ マップ。近くは細かい別のマップ、遠くは粗いマップで、画素とテクセルの比を揃える。", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "画素のレイ")
    return dict(name=name, page=PAGE + "shadow-map-basics/aliasing-stabilize.md", before="## エイリアシングの 2 種類", scene=scene, size=(780, 420), times=[1.5, 3.5, 6.0, 9.5])


FIGS = [SlopeBias, NormalOffset, FrontFaceCull, DualParaboloid, ManyLightsCache, BlobPlanar, StipplePattern, EsmExp, EvsmWarp, RtShadowSamples, LightFrustum, PerspectiveAliasing]
