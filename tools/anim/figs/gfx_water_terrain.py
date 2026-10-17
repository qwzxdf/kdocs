import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Blur, Caption, Gray, Hex, Lerp, LiveText, Mix, NewScene, Panel, R, RampFill, Smooth, Sweep)  # noqa: E402

G = "graphics/"


def PathD(pts):
    return "M" + " L".join("%s,%s" % (R(x), R(y)) for x, y in pts)


def SineSum():
    name = "sine-sum"
    scene = NewScene(name, 780, 470, duration=13.0, hold=1.5, title="サイン波を足すと、不規則な波になる")
    root = scene.root
    waves = [(46, 110, 0.0, BLUE), (22, 62, 1.1, GREEN), (12, 34, 2.3, PURPLE)]  # 振幅, 波長, 位相, 色
    x0, x1 = 60, 720
    rows = [110, 190, 270]
    for k, (a, wl, ph, col) in enumerate(waves):
        root.add("line", x1=x0, y1=rows[k], x2=x1, y2=rows[k], stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, x0, rows[k] - 46, ["① 大きくゆっくりした波", "② 中くらいの波", "③ 小さく細かい波"][k], size=12, fill=col)
        pts = [(x, rows[k] - a * 0.55 * math.sin(2 * math.pi * (x - x0) / wl + ph)) for x in range(x0, x1 + 1, 4)]
        p = root.add("path", d=PathD(pts), fill="none", stroke=col, stroke_width=3, opacity=0)
        p.Show(1.0 + k * 3.0)
    base = 370
    root.add("line", x1=x0, y1=base, x2=x1, y2=base, stroke=LIGHT, stroke_width=1.5)
    scene.Text(root, x0, base - 52, "合計（水面の高さ）", size=13, fill=RED)

    def Sum(n, x):
        return sum(waves[k][0] * 0.55 * math.sin(2 * math.pi * (x - x0) / waves[k][1] + waves[k][2]) for k in range(n))

    tot = root.add("path", d=PathD([(x, base - Sum(1, x)) for x in range(x0, x1 + 1, 4)]), fill="none", stroke=RED, stroke_width=4)
    tot.Ramp(3.8, 4.8, "d", PathD([(x, base - Sum(2, x)) for x in range(x0, x1 + 1, 4)]))
    tot.Ramp(6.8, 7.8, "d", PathD([(x, base - Sum(3, x)) for x in range(x0, x1 + 1, 4)]))
    scene.TextStack(root, 400, 450, [(0.0, 3.8, "1 本だけ:規則的なうねり"), (3.8, 6.8, "2 本足す:不規則さが出る"), (6.8, 20, "3 本足す:それらしい水面。向き・波長をばらつかせると、さらに自然")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "1 → 2 → 3 本")
    return dict(name=name, page=G + "water/waves/sine-waves.md", before="## サイン波の重ね合わせ", scene=scene, size=(780, 470), times=[1.5, 4.5, 7.0, 12.0])


def NormalBlend():
    name = "normal-blend"
    scene = NewScene(name, 780, 420, duration=8.0, hold=0.0, title="法線マップを 2 枚、逆向きに流して重ねると、繰り返しが見えない")
    root = scene.root
    x0, x1 = 60, 720
    rows = [("法線マップ A（右へ流す）", 120, BLUE, 38, 1), ("法線マップ B（左へ、別の大きさで流す）", 220, GREEN, 61, -1), ("重ねた結果（見た目の凹凸）", 330, RED, None, 0)]
    frames = 32
    period = 8.0

    def Ha(x, ph):
        return 20 * math.sin(2 * math.pi * (x - x0 + ph) / 120) + 8 * math.sin(2 * math.pi * (x - x0 + ph * 1.0) / 47 + 1)

    def Hb(x, ph):
        return 16 * math.sin(2 * math.pi * (x - x0 - ph) / 190 + 2) + 9 * math.sin(2 * math.pi * (x - x0 - ph * 1.0) / 73)

    for title, y, col, _, _ in rows:
        root.add("line", x1=x0, y1=y, x2=x1, y2=y, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, x0, y - 44, title, size=13, fill=col)
    pa = root.add("path", d=PathD([(x, 120 - Ha(x, 0)) for x in range(x0, x1 + 1, 5)]), fill="none", stroke=BLUE, stroke_width=3)
    pb = root.add("path", d=PathD([(x, 220 - Hb(x, 0)) for x in range(x0, x1 + 1, 5)]), fill="none", stroke=GREEN, stroke_width=3)
    ps = root.add("path", d=PathD([(x, 330 - Ha(x, 0) - Hb(x, 0)) for x in range(x0, x1 + 1, 5)]), fill="none", stroke=RED, stroke_width=4)
    for f in range(1, frames + 1):
        t = period * f / frames
        ph = 120 * f / frames
        pa.Ramp(period * (f - 1) / frames, t, "d", PathD([(x, 120 - Ha(x, ph)) for x in range(x0, x1 + 1, 5)]))
        pb.Ramp(period * (f - 1) / frames, t, "d", PathD([(x, 220 - Hb(x, ph * 190 / 120)) for x in range(x0, x1 + 1, 5)]))
        ps.Ramp(period * (f - 1) / frames, t, "d", PathD([(x, 330 - Ha(x, ph) - Hb(x, ph * 190 / 120)) for x in range(x0, x1 + 1, 5)]))
    scene.Text(root, 60, 400, "2 枚の周期が違うので、足した形は、なかなか繰り返さない。遠くは、法線マップの効果を弱める（ちらつき防止）。", size=13, weight=500, fill=GRAY)
    scene.Note(0.0, name, "A と B を逆向きに移動")
    return dict(name=name, page=G + "water/waves/normals.md", before="## 細かい凹凸", scene=scene, size=(780, 420), times=[0.5, 2.5, 4.5, 6.5])


def FftSpectrum():
    name = "fft-spectrum"
    scene = NewScene(name, 780, 440, duration=10.0, hold=0.0, title="FFT 海面:周波数ごとの波を、足し合わせる")
    root = scene.root
    K = 8
    amps = [34, 26, 18, 12, 8, 5, 3, 2]
    phs = [0.3, 1.7, 2.9, 4.1, 0.9, 2.2, 5.0, 3.6]
    ax = Axes(scene, root, 50, 80, 260, 130, 8.0, 40.0, "波の細かさ（周波数）", "")
    for k in range(K):
        h = amps[k] / 40 * ax.h
        root.add("rect", x=R(ax.x + k * ax.w / K + 6), y=R(ax.y + ax.h - h), width=R(ax.w / K - 12), height=R(h), fill=PURPLE)
    scene.Text(root, 50, 70, "スペクトル（海の状態で決まる）", size=12, fill=GRAY)
    x0, x1, base = 360, 730, 150
    root.add("line", x1=x0, y1=base, x2=x1, y2=base, stroke=LIGHT, stroke_width=1.5)
    scene.Text(root, x0, 70, "合成した水面の高さ（時間とともに動く）", size=12, fill=GRAY)
    T = 10.0
    frames = 40

    def H(x, t):
        return sum(amps[k] * 0.55 * math.cos(2 * math.pi * (k + 1) * (x - x0) / (x1 - x0) * 1.0 - 2 * math.pi * (k + 1) * t / T + phs[k]) for k in range(K)) / 1.7

    p = root.add("path", d=PathD([(x, base - H(x, 0)) for x in range(x0, x1 + 1, 4)]), fill="none", stroke=BLUE, stroke_width=4)
    for f in range(1, frames + 1):
        p.Ramp(T * (f - 1) / frames, T * f / frames, "d", PathD([(x, base - H(x, T * f / frames)) for x in range(x0, x1 + 1, 4)]))
    # 成分の波(4 本)
    for k in range(4):
        y = 300 + k * 0
    rows = [300, 340, 380]
    for r_i, k in enumerate((0, 2, 4)):
        yy = rows[r_i]
        root.add("line", x1=x0, y1=yy, x2=x1, y2=yy, stroke=LIGHT, stroke_width=1)
        pc = root.add("path", d=PathD([(x, yy - amps[k] * 0.4 * math.cos(2 * math.pi * (k + 1) * (x - x0) / (x1 - x0) + phs[k])) for x in range(x0, x1 + 1, 4)]), fill="none", stroke=PURPLE, stroke_width=2)
        for f in range(1, frames + 1):
            pc.Ramp(T * (f - 1) / frames, T * f / frames, "d", PathD([(x, yy - amps[k] * 0.4 * math.cos(2 * math.pi * (k + 1) * (x - x0) / (x1 - x0) - 2 * math.pi * (k + 1) * (T * f / frames) / T + phs[k])) for x in range(x0, x1 + 1, 4)]))
        scene.Text(root, 50, yy + 4, "成分 %d" % (k + 1), size=12, fill=PURPLE)
    scene.Text(root, 50, 250, "下の細い線 = 成分の波（高い周波数ほど弱く、速く動く）", size=12, fill=GRAY, weight=500)
    scene.Text(root, 50, 425, "各周波数の波の位相を、時間で回して、逆 FFT でまとめて足す。波がたくさん足されるので、本物の海に近い。", size=12, weight=500, fill=GRAY)
    scene.Note(0.0, name, "位相を回す")
    return dict(name=name, page=G + "water/waves/fft-ocean.md", before="## FFT 海面", scene=scene, size=(780, 440), times=[0.5, 2.5, 5.0, 7.5])


def WaterFresnel():
    name = "water-fresnel"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="水のフレネル:浅い角度ほど、反射が強くなる")
    root = scene.root
    sy = 250
    root.add("rect", x=40, y=sy, width=420, height=130, fill="#bae6fd", fill_opacity=0.8)
    root.add("line", x1=40, y1=sy, x2=460, y2=sy, stroke="#0284c7", stroke_width=3)
    sky = root.add("rect", x=40, y=80, width=420, height=170, fill="#e0f2fe", fill_opacity=0.5)
    scene.Text(root, 50, 104, "空", size=12, fill=GRAY)
    scene.Text(root, 50, 372, "水の中", size=12, fill="#0284c7")

    def F(th):
        c = math.cos(th)
        return 0.02 + 0.98 * (1 - c) ** 5

    hit = (250, sy)
    eye = root.add("circle", cx=100, cy=140, r=10, fill=BLUE)
    r_in = root.add("line", x1=100, y1=140, x2=hit[0], y2=hit[1], stroke=BLUE, stroke_width=3)
    r_refl = root.add("line", x1=hit[0], y1=hit[1], x2=400, y2=100, stroke=AMBER, stroke_width=3, opacity=1)
    r_trans = root.add("line", x1=hit[0], y1=hit[1], x2=300, y2=360, stroke=GREEN, stroke_width=3, opacity=1)
    ax = Axes(scene, root, 520, 90, 220, 160, 90.0, 1.0, "見る角度（水面から）", "反射の割合")
    ax.Curve(lambda a: F(math.radians(90 - a)), RED, 3, n=60)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(1), r=6, fill=RED, stroke="#ffffff", stroke_width=1.5)
    bar = root.add("rect", x=520, y=300, width=220, height=26, fill=GREEN)
    barr = root.add("rect", x=520, y=300, width=0.001, height=26, fill=AMBER)
    steps = 26
    t0, t1 = 0.8, 11.0
    prev = None
    for i in range(steps + 1):
        f = i / steps
        a = 8 + 80 * f  # 水面から測った角度
        th = math.radians(90 - a)
        L = 170
        ex, ey = hit[0] - L * math.cos(math.radians(a)), hit[1] - L * math.sin(math.radians(a))
        rx, ry = hit[0] + L * math.cos(math.radians(a)), hit[1] - L * math.sin(math.radians(a))
        tx_ = hit[0] + 100 * math.cos(math.radians(a)) * 0.6
        ty_ = hit[1] + 110
        fr = F(th)
        t = Lerp(t0, t1, f)
        vals = [(eye, "cx", R(ex)), (eye, "cy", R(ey)), (r_in, "x1", R(ex)), (r_in, "y1", R(ey)), (r_refl, "x2", R(rx)), (r_refl, "y2", R(ry)), (r_refl, "opacity", R(0.15 + 0.85 * fr)),
                (r_trans, "x2", R(tx_)), (r_trans, "y2", R(ty_)), (r_trans, "opacity", R(1.0 - 0.85 * fr)), (dot, "cx", ax.X(a)), (dot, "cy", ax.Y(fr)), (barr, "width", R(max(0.001, 220 * fr)))]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    scene.Text(root, 520, 292, "反射（橙）と屈折（緑）の割合", size=12, fill=GRAY)
    LiveText(scene, root, 520, 350, t0, t1, steps, lambda i, f: "角度 %d° → 反射 %d %%" % (8 + 80 * f, round(100 * F(math.radians(90 - (8 + 80 * f))))), size=15, fill=INK)
    scene.Text(root, 40, 406, "真上から見ると、水の底が見える（反射 2 %）。斜めから見ると、空を映す鏡になる。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "見る角度を 8° → 88°")
    return dict(name=name, page=G + "water/shading/fresnel.md", before="## フレネル", scene=scene, size=(780, 420), times=[1.0, 4.0, 7.5, 10.5])


def ShoreFoamDepth():
    name = "shore-foam-depth"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="岸辺の泡:水面と地面の距離が小さい所に、泡が出る")
    root = scene.root
    # 砂浜の断面
    sand = [(40, 330), (200, 300), (360, 255), (520, 205), (700, 150)]
    root.add("polygon", points=" ".join("%s,%s" % p for p in sand + [(700, 380), (40, 380)]), fill="#e7d9b4", stroke="#b59b60", stroke_width=2)

    def SandY(x):
        for (xa, ya), (xb, yb) in zip(sand, sand[1:]):
            if xa <= x <= xb:
                return ya + (yb - ya) * (x - xa) / (xb - xa)
        return sand[-1][1]

    def Level(t):
        return 235 - 40 * math.sin(2 * math.pi * t / 12.0)

    # 水面:y = level より下を青、砂の上に出ている部分を除く
    water = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#38bdf8", fill_opacity=0.55)
    foam = root.add("polygon", points="0,0 0,0 0,0 0,0", fill="#ffffff", fill_opacity=0.95, stroke="#e5e7eb", stroke_width=1)
    wl = root.add("line", x1=40, y1=235, x2=700, y2=235, stroke="#0284c7", stroke_width=3)
    frames = 48
    prev = None
    texts = []
    for i in range(frames + 1):
        t = 12.0 * i / frames
        lv = Level(t)
        # 水面と砂の交点
        xs = 40
        for x in range(40, 701):
            if SandY(x) <= lv:
                xs = x
                break
        else:
            xs = 700
        wpts = "%s,%s %s,%s %s,%s %s,%s" % (40, R(lv), R(xs), R(lv), R(xs), R(SandY(xs)), 40, 380) if False else "40,%s %s,%s 700,%s 700,380 40,380" % (R(lv), R(xs), R(lv), R(lv))
        xa = xs
        for x in range(xs, 40, -1):
            if SandY(x) > lv + 26:
                break
            xa = x
        xm = (xa + xs) / 2
        fpts = "%s,%s %s,%s %s,%s %s,%s %s,%s" % (R(xa), R(lv), R(xs), R(lv), R(xs), R(SandY(xs)), R(xm), R(SandY(xm)), R(xa), R(SandY(xa)))
        wpts = "40,%s %s,%s %s,%s 700,%s 700,380 40,380" % (R(lv), R(max(40, xs - 0)), R(lv), R(xs), R(lv), R(lv))
        # 水面 = 地面より上の部分だけ(交点より左)
        wpts = "40,%s %s,%s %s,%s 40,380" % (R(lv), R(xs), R(lv), R(xs), 380)
        for node, v in ((water, wpts), (foam, fpts), ):
            if i == 0:
                node.Set(t, "points", v)
            else:
                node.Ramp(prev, t, "points", v)
        if i == 0:
            wl.Set(t, "y1", R(lv)); wl.Set(t, "y2", R(lv))
        else:
            wl.Ramp(prev, t, "y1", R(lv)); wl.Ramp(prev, t, "y2", R(lv))
        prev = t
    scene.TextStack(root, 40, 60, [(0.0, 20, "水位が上がる・下がるにつれて、水面と砂浜の交わる所（白い帯）が動く")], size=14, fill=INK)
    scene.Text(root, 40, 404, "水面とシーンの深度の差が小さいほど、泡を濃くする。波が引くと、泡の帯も一緒に岸から離れる。", size=13, weight=500, fill=GRAY)
    scene.Note(0.0, name, "水位が上下")
    return dict(name=name, page=G + "water/shore-foam/shore-depth.md", before="## 岸辺の泡：深度差", scene=scene, size=(780, 420), times=[1.0, 3.0, 6.0, 9.0])


def FlowMapBlend():
    name = "flowmap-blend"
    scene = NewScene(name, 780, 420, duration=8.0, hold=0.0, title="フローマップ:位相をずらした 2 枚を、三角波で入れ替えながら流す")
    root = scene.root
    x0, x1 = 80, 700
    L = 160
    rows = [("流した模様 A（位相 t）", 110, BLUE), ("流した模様 B（位相 t + 0.5）", 200, GREEN), ("混ぜた結果", 310, RED)]
    for title, y, col in rows:
        root.add("line", x1=x0, y1=y + 24, x2=x1, y2=y + 24, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, x0, y - 24, title, size=13, fill=col)
    T = 4.0
    pattern = [20, 70, 105, 140]

    def Dots(row_y, col, phase_off, op_fn):
        out = []
        for k in range(6):
            c = root.add("circle", cx=x0 + 20 + k * L / 2, cy=row_y + 10, r=9, fill=col, opacity=0)
            out.append(c)
        return out

    frames = 32
    for row_i, (title, y, col) in enumerate(rows[:2]):
        dots = Dots(y, col, 0.5 * row_i, None)
        for c_i, c in enumerate(dots):
            base_x = x0 + 20 + c_i * L / 2 * 1.0
            for f in range(frames + 1):
                t = 8.0 * f / frames
                phase = ((t / T) + 0.5 * row_i) % 1.0
                w = 1 - abs(2 * phase - 1)
                x = base_x + phase * L
                if x > x1:
                    x -= (x1 - x0) * 1.0
                if f == 0:
                    c.Set(t, "cx", R(x)); c.Set(t, "opacity", R(w))
                else:
                    c.Ramp(8.0 * (f - 1) / frames, t, "cx", R(x)); c.Ramp(8.0 * (f - 1) / frames, t, "opacity", R(w))
    for c_i in range(6):
        c = root.add("circle", cx=x0 + 20 + c_i * L / 2, cy=320, r=9, fill=RED, opacity=1)
        base_x = x0 + 20 + c_i * L / 2
        for f in range(frames + 1):
            t = 8.0 * f / frames
            phase = (t / T) % 1.0
            x = base_x + phase * L
            if f == 0:
                c.Set(t, "cx", R(x)); c.Set(t, "opacity", 1.0)
            else:
                c.Ramp(8.0 * (f - 1) / frames, t, "cx", R(x)); c.Ramp(8.0 * (f - 1) / frames, t, "opacity", 1.0)
    scene.TextStack(root, 40, 380, [(0.0, 20, "A と B は、それぞれ、位相が 1 になる瞬間に位置が元に戻る（ジャンプ）。そのとき重みは 0 なので、見えない。")], size=13, fill=INK, weight=500)
    scene.Text(root, 40, 404, "重みは三角波（0 → 1 → 0）。A と B の位相を 0.5 ずらすので、常にどちらかが見えて、途切れず流れる。", size=13, weight=500, fill=GRAY)
    scene.Note(0.0, name, "2 周期")
    return dict(name=name, page=G + "water/interaction/flow-map.md", before="## フローマップ", scene=scene, size=(780, 420), times=[0.5, 2.0, 3.5, 6.0])


def CausticsRays():
    name = "caustics-rays"
    scene = NewScene(name, 780, 460, duration=10.0, hold=0.0, title="コースティクス:波がレンズになり、光が集まって明るい所ができる")
    root = scene.root
    sy, fy = 130, 340
    x0, x1 = 60, 720
    root.add("rect", x=x0, y=sy, width=x1 - x0, height=fy - sy, fill="#bae6fd", fill_opacity=0.4)
    root.add("rect", x=x0, y=fy, width=x1 - x0, height=26, fill="#d6c7a1")
    nb = 33
    bars = [root.add("rect", x=R(x0 + i * (x1 - x0) / nb), y=fy + 26, width=R((x1 - x0) / nb + 0.5), height=24, fill="#f1f5f9") for i in range(nb)]
    scene.Text(root, x0, fy + 68, "海底の明るさ（光線の密度）", size=12, fill=GRAY)
    T = 10.0
    frames = 40
    nr = 90
    n_rel = 1.33

    def Surf(x, t):
        return 14 * math.sin(2 * math.pi * (x - x0) / 150 - 2 * math.pi * t / T) + 7 * math.sin(2 * math.pi * (x - x0) / 62 + 2 * math.pi * t / T * 2)

    def Slope(x, t):
        h = 0.5
        return (Surf(x + h, t) - Surf(x - h, t)) / (2 * h)

    def Floor(t):
        hist = [0] * nb
        for k in range(nr):
            x = x0 + (k + 0.5) * (x1 - x0) / nr
            s = Slope(x, t)
            th1 = math.atan(s)
            # 法線 (−s, 1) に対する入射角 θ1=atan(s)、屈折して下へ
            th2 = math.asin(max(-1, min(1, math.sin(th1) / n_rel)))
            dev = th1 - th2
            xe = x + math.tan(dev) * (fy - sy - Surf(x, t))
            b = int((xe - x0) / (x1 - x0) * nb)
            if 0 <= b < nb:
                hist[b] += 1
        return hist

    # 水面
    surf = root.add("path", d=PathD([(x, sy + Surf(x, 0)) for x in range(x0, x1 + 1, 4)]), fill="none", stroke="#0284c7", stroke_width=3)
    hists = [Floor(T * f / frames) for f in range(frames + 1)]
    vmax = max(max(h) for h in hists)
    for i, b in enumerate(bars):
        steps = []
        for f in range(frames + 1):
            v = min(1.0, hists[f][i] / max(1.0, vmax * 0.5))
            steps.append((T * f / frames, Hex([241 - 40 * v + 14 * v, 245 - 10 * v, 249 - 190 * v + 90 * v]) if False else Mix("#1e293b", "#fef9c3", v)))
        b.Steps("fill", steps)
    for f in range(1, frames + 1):
        surf.Ramp(T * (f - 1) / frames, T * f / frames, "d", PathD([(x, sy + Surf(x, T * f / frames)) for x in range(x0, x1 + 1, 4)]))
    # 光線(数本)
    for k in range(0, 22):
        x = x0 + (k + 0.5) * (x1 - x0) / 22
        ln = root.add("line", x1=R(x), y1=60, x2=R(x), y2=R(sy + Surf(x, 0)), stroke=AMBER, stroke_width=1.5, opacity=0.7)
    scene.TextStack(root, 60, 52, [(0.0, 20, "上から平行な光が降る。波の傾きで、屈折の向きが変わる")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 60, 440, "光線が集まった所が明るい（細い線の模様）。波が動くと、模様も揺れる。本格的には、法線から光線を追う。", size=13, weight=500, fill=GRAY)
    scene.Note(0.0, name, "波が動く")
    return dict(name=name, page=G + "water/underwater/caustics.md", before="## コースティクス", scene=scene, size=(780, 460), times=[0.5, 2.5, 5.0, 7.5])


def SnellWindow():
    name = "snell-window"
    scene = NewScene(name, 780, 420, duration=12.0, hold=0.0, title="水中から見上げる:一定の角度の内側は空、外側は水面が鏡になる")
    root = scene.root
    sy = 190
    root.add("rect", x=40, y=80, width=700, height=sy - 80, fill="#e0f2fe", fill_opacity=0.5)
    root.add("rect", x=40, y=sy, width=700, height=130, fill="#7dd3fc", fill_opacity=0.35)
    root.add("line", x1=40, y1=sy, x2=740, y2=sy, stroke="#0284c7", stroke_width=3)
    scene.Text(root, 50, 104, "空", size=12, fill=GRAY)
    ex, ey = 390, 300
    root.add("circle", cx=ex, cy=ey, r=11, fill=BLUE, stroke="#ffffff", stroke_width=2)
    scene.Text(root, ex + 16, ey + 5, "水中の目", size=12, fill=BLUE)
    crit = math.degrees(math.asin(1 / 1.33))
    # 窓(臨界角のコーン)
    half = math.tan(math.radians(crit)) * (ey - sy)
    root.add("polygon", points="%s,%s %s,%s %s,%s" % (ex, ey, R(ex - half), sy, R(ex + half), sy), fill=AMBER, fill_opacity=0.12, stroke=AMBER, stroke_width=1.5, stroke_dasharray="5 4")
    scene.Text(root, ex, sy - 8, "スネルの窓（約 %d°）" % round(crit), size=12, fill=AMBER, anchor="middle")
    ray = root.add("line", x1=ex, y1=ey, x2=ex, y2=sy, stroke=GREEN, stroke_width=3)
    outr = root.add("line", x1=ex, y1=sy, x2=ex, y2=100, stroke=GREEN, stroke_width=3)
    steps = 32
    t0, t1 = 0.8, 11.0
    prev = None
    for i in range(steps + 1):
        f = i / steps
        th = math.radians(70 * f)
        hx = ex + math.tan(th) * (ey - sy)
        if math.degrees(th) < crit:
            # 屈折して空へ
            s = 1.33 * math.sin(th)
            th2 = math.asin(min(1, s))
            ox, oy, col, op = hx + 140 * math.tan(th2) * 0.6, 100, GREEN, 1
            ox = hx + math.tan(th2) * (sy - 100)
        else:
            ox, oy, col, op = hx + math.tan(th) * (ey - sy) * 0.0 + (hx - ex) * 0.0 + math.tan(th) * 150, ey + 0, RED, 1
            ox, oy = hx + math.sin(th) * 160, sy + math.cos(th) * 160
        t = Lerp(t0, t1, f)
        vals = [(ray, "x2", R(hx)), (outr, "x1", R(hx)), (outr, "x2", R(ox)), (outr, "y2", R(oy)), (outr, "stroke", RED if math.degrees(th) >= crit else GREEN)]
        for node, attr, v in vals:
            if attr == "stroke":
                continue
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    flip_t = Lerp(t0, t1, crit / 70)
    outr.Steps("stroke", [(0.0, GREEN), (flip_t, RED)])
    scene.TextStack(root, 40, 52, [(0.0, flip_t, "窓の内側を見る:屈折して、空が見える"), (flip_t, 20, "窓の外側を見る:全反射して、水中（海底）の景色が映る")], size=16, fill=INK)
    scene.Text(root, 40, 406, "見上げる角度が大きくなる（横を向く）と、ある角度から先は、水面が鏡になる。これが水中の「天井」の見え方。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "視線を上から横へ")
    return dict(name=name, page=G + "water/underwater/surface-back.md", before="## 水面の裏側", scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.5])


def HeightmapLift():
    name = "heightmap-lift"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="格子メッシュ:高さマップの値で、頂点を持ち上げる")
    root = scene.root
    heights = [0.15, 0.3, 0.55, 0.9, 0.7, 0.4, 0.6, 0.35, 0.2]
    n = len(heights)
    x0, step = 90, 70
    # 上:高さマップ(1D 画像)
    scene.Text(root, 40, 78, "高さマップ（明るい = 高い）", size=13, fill=GRAY)
    for i, h in enumerate(heights):
        root.add("rect", x=x0 + i * step - 24, y=90, width=48, height=34, fill=Gray(h))
        scene.Text(root, x0 + i * step, 140, "%.2f" % h, size=11, fill=GRAY, anchor="middle")
    base = 340
    root.add("line", x1=60, y1=base, x2=730, y2=base, stroke=LIGHT, stroke_width=1.5)
    scene.Text(root, 60, 190, "メッシュの頂点（最初は平ら）", size=13, fill=GRAY)
    pts = []
    for i, h in enumerate(heights):
        pts.append(root.add("circle", cx=x0 + i * step, cy=base, r=7, fill=BLUE, stroke="#ffffff", stroke_width=1.5))
    segs = []
    for i in range(n - 1):
        segs.append(root.add("line", x1=x0 + i * step, y1=base, x2=x0 + (i + 1) * step, y2=base, stroke=BLUE, stroke_width=3))
    fillp = root.add("polygon", points=" ".join("%s,%s" % (x0 + i * step, base) for i in range(n)) + " %s,%s %s,%s" % (x0 + (n - 1) * step, base + 30, x0, base + 30), fill="#e7d9b4", fill_opacity=0.9)
    t0, dt = 1.0, 0.5
    for i, h in enumerate(heights):
        ta = t0 + i * dt
        tb = ta + 1.2
        y = base - h * 150
        pts[i].Ramp(ta, tb, "cy", R(y))
        if i < n - 1:
            segs[i].Ramp(ta, tb, "y1", R(y))
        if i > 0:
            segs[i - 1].Ramp(ta, tb, "y2", R(y))
    # 塗りつぶし(ポリゴンは頂点列でフレーム補間)
    frames = 24
    prev_t = None
    for f in range(frames + 1):
        t = t0 + (n * dt + 1.2) * f / frames
        ys = []
        for i, h in enumerate(heights):
            ta, tb = t0 + i * dt, t0 + i * dt + 1.2
            u = max(0.0, min(1.0, (t - ta) / (tb - ta)))
            ys.append(base - h * 150 * Smooth(u) if False else base - h * 150 * u)
        v = " ".join("%s,%s" % (x0 + i * step, R(ys[i])) for i in range(n)) + " %s,%s %s,%s" % (x0 + (n - 1) * step, base + 30, x0, base + 30)
        if f == 0:
            fillp.Set(t, "points", v)
        else:
            fillp.Ramp(prev_t, t, "points", v)
        prev_t = t
    scene.Text(root, 40, 400, "頂点シェーダーで、高さマップの値を読み、頂点の高さにする。格子（頂点とインデックス）は、同じものを使い回せる。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "頂点を順に持ち上げる")
    return dict(name=name, page=G + "terrain/heightmap-mesh/grid-mesh.md", before="## 格子メッシュ", scene=scene, size=(780, 420), times=[1.0, 3.0, 5.5, 10.0])


def LodMorph():
    name = "lod-morph"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="モーフィング:粗い LOD になる前に、頂点を粗い位置へ寄せていく")
    root = scene.root
    base = 340
    n = 17
    x0, step = 70, 40
    hs = [60 + 55 * math.sin(i * 0.7) + 25 * math.sin(i * 1.9 + 1) for i in range(n)]

    def Pts(m):
        out = []
        for i in range(n):
            y = hs[i]
            if i % 2 == 1:
                mid = (hs[i - 1] + hs[i + 1]) / 2
                y = hs[i] + (mid - hs[i]) * m
            out.append((x0 + i * step, base - y))
        return out

    line = root.add("path", d=PathD(Pts(0)), fill="none", stroke=INK, stroke_width=3)
    verts = [root.add("circle", cx=x0 + i * step, cy=base - hs[i], r=6 if i % 2 == 0 else 5, fill=BLUE if i % 2 == 0 else RED, stroke="#ffffff", stroke_width=1.5, opacity=1) for i in range(n)]
    frames = 20
    t0, t1 = 1.5, 8.5
    prev = None
    for f in range(frames + 1):
        t = Lerp(t0, t1, f / frames)
        m = f / frames
        pts = Pts(m)
        if f == 0:
            line.Set(t, "d", PathD(pts))
        else:
            line.Ramp(prev, t, "d", PathD(pts))
        for i, v in enumerate(verts):
            if f == 0:
                v.Set(t, "cy", R(pts[i][1]))
            else:
                v.Ramp(prev, t, "cy", R(pts[i][1]))
        prev = t
    # 最後に奇数頂点を消す
    for i, v in enumerate(verts):
        if i % 2 == 1:
            v.Set(9.0, "opacity", 1)
            v.Ramp(9.0, 9.6, "opacity", 0)
    scene.TextStack(root, 40, 70, [(0.0, 1.5, "細かい LOD:全部の頂点（赤 = 粗い LOD で消える頂点）"), (1.5, 8.5, "距離が LOD の境に近づくほど、赤い頂点が、隣り合う 2 つの平均の位置へ動く"), (8.5, 20, "動ききった所で、赤い頂点を消す → 見た目が変わらない（ポップしない）")], size=14, fill=INK)
    LiveText(scene, root, 40, 392, t0, t1, 14, lambda i, f: "モーフ係数 %.2f（0 = 元の位置、1 = 平均の位置）" % (i / 13), size=14, fill=INK)
    scene.Note(t0, name, "モーフ 0 → 1")
    return dict(name=name, page=G + "terrain/lod/morphing.md", before="## モーフィング", scene=scene, size=(780, 420), times=[1.0, 4.0, 7.0, 10.0])


def LodCracks():
    name = "lod-cracks"
    scene = NewScene(name, 780, 420, duration=10.0, hold=1.5, title="継ぎ目:LOD が違うと、境界で頂点が合わず、隙間ができる")
    root = scene.root
    base = 350
    xb = 390
    # 左:細かい(頂点が 2 倍)、右:粗い
    left = [(xb - 8 * 40 + i * 40, 150 + 40 * math.sin(i * 0.9)) for i in range(9)]  # 左は x=70..390
    right = [(xb, 150 + 40 * math.sin(8 * 0.9)), (xb + 160, 120 + 30), (xb + 320, 170)]
    # 境界の頂点:左の細かい最後の 2 点と右の粗い点
    fine_pts = [(xb - 80, 180), (xb - 40, 205), (xb, 160)]
    coarse = [(xb - 80, 180), (xb, 160)]
    fine_path = root.add("path", d=PathD([(70, 210), (110, 190), (150, 215), (190, 195), (230, 200), (270, 185), (310, 180)] + fine_pts), fill="none", stroke=BLUE, stroke_width=3.5)
    fine_path.Ramp(4.0, 6.0, "d", PathD([(70, 210), (110, 190), (150, 215), (190, 195), (230, 200), (270, 185), (310, 180), (xb - 80, 180), (xb - 40, 170), (xb, 160)]))
    root.add("path", d=PathD([(xb, 160), (xb + 160, 150), (xb + 330, 185)]), fill="none", stroke=GREEN, stroke_width=3.5)
    root.add("line", x1=xb, y1=100, x2=xb, y2=base, stroke=LIGHT, stroke_width=2, stroke_dasharray="4 4")
    scene.Text(root, 200, 100, "細かい LOD", size=13, fill=BLUE, anchor="middle")
    scene.Text(root, 560, 100, "粗い LOD", size=13, fill=GREEN, anchor="middle")
    # 隙間:粗い側の辺(xb-80,180)→(xb,160)、細かい側の頂点(xb-40,205)
    root.add("line", x1=xb - 80, y1=180, x2=xb, y2=160, stroke=GREEN, stroke_width=2.5, stroke_dasharray="5 4")
    v = root.add("circle", cx=xb - 40, cy=205, r=8, fill=RED, stroke="#ffffff", stroke_width=2)
    gap = root.add("line", x1=xb - 40, y1=205, x2=xb - 40, y2=170, stroke=RED, stroke_width=3, opacity=1)
    scene.TextStack(root, xb - 30, 250, [(0.0, 6.0, "隙間（背景が見える）")], size=12, fill=RED)
    v.Set(4.0, "cy", 205)
    v.Ramp(4.0, 6.0, "cy", 170)
    gap.Set(4.0, "y1", 205)
    gap.Ramp(4.0, 6.0, "y1", 170)
    gap.Set(6.0, "opacity", 1)
    gap.Ramp(6.0, 6.2, "opacity", 0)
    scene.TextStack(root, 40, 300, [(0.0, 4.0, "赤い頂点は、細かい側にだけある。粗い側の辺（緑の点線）から、ずれている → 隙間"), (4.0, 6.0, "対策 1:赤い頂点を、粗い辺の上へ動かす"), (6.0, 20, "隙間が消えた（頂点が辺の上にあるので、ぴったり合う）")], size=14, fill=INK)
    scene.Text(root, 40, 340, "対策 2:境界にスカート（垂れ幕）を付けて、隙間を隠す方法もある。", size=13, weight=500, fill=GRAY)
    scene.Note(4.0, name, "頂点を動かす")
    return dict(name=name, page=G + "terrain/lod/cracks.md", before="## 継ぎ目", scene=scene, size=(780, 420), times=[1.0, 3.5, 5.0, 9.0])


def SplatWeights():
    name = "splat-weights"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="スプラットの重み:高さと傾きで、草・岩・雪を混ぜる")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 340, 220, 1.0, 1.0, "高さ（0 = 低い、1 = 高い）", "重み")

    def Wgrass(h):
        return max(0.0, 1 - h / 0.55) ** 1.2

    def Wsnow(h):
        return max(0.0, (h - 0.55) / 0.45) ** 1.2

    def Wrock(h):
        return max(0.0, 1 - Wgrass(h) - Wsnow(h))

    cols = [("草", "#2ea043", Wgrass), ("岩", "#78716c", Wrock), ("雪", "#9ca3af", Wsnow)]
    for label, col, fn in cols:
        ax.Curve(fn, col if label != "雪" else "#64748b", 4, n=60)
    scene.Text(root, ax.X(0.08), ax.Y(0.9), "草", size=13, fill="#2ea043")
    scene.Text(root, ax.X(0.5), ax.Y(0.25), "岩", size=13, fill="#78716c")
    scene.Text(root, ax.X(0.9), ax.Y(0.9), "雪", size=13, fill="#64748b")
    line = root.add("line", x1=ax.X(0), y1=ax.y, x2=ax.X(0), y2=ax.y + ax.h, stroke=AMBER, stroke_width=2.5)
    # 右:山の断面 + 色
    mx, base = 440, 330
    pts = [(mx, base), (mx + 70, base - 60), (mx + 150, base - 140), (mx + 220, base - 200), (mx + 290, base - 140), (mx + 330, base)]
    root.add("polygon", points=" ".join("%s,%s" % p for p in pts), fill="#d6d3d1", stroke="#78716c", stroke_width=2)
    out = root.add("rect", x=440, y=350, width=120, height=34, fill="#2ea043", stroke="#94a3b8", stroke_width=2)
    scene.Text(root, 440, 342, "この高さの地面の色", size=12, fill=GRAY)
    mark = root.add("circle", cx=mx + 20, cy=base - 20, r=7, fill=RED, stroke="#ffffff", stroke_width=1.5)
    steps = 30
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(steps + 1):
        h = i / steps
        t = Lerp(t0, t1, h)
        wg, wr, ws = Wgrass(h), Wrock(h), Wsnow(h)
        rgb = [wg * c1 + wr * c2 + ws * c3 for c1, c2, c3 in zip((0x2e, 0xa0, 0x43), (0x78, 0x71, 0x6c), (0xf1, 0xf5, 0xf9))]
        col = Hex(rgb)
        # 山の左斜面上の位置
        px = mx + 330 * 0.0 + h * 220
        py = base - h * 200
        vals = [(line, "x1", ax.X(h)), (line, "x2", ax.X(h)), (out, "fill", col), (mark, "cx", R(px)), (mark, "cy", R(py))]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    LiveText(scene, root, 50, 346, t0, t1, steps, lambda i, f: "高さ %.2f:草 %.2f  岩 %.2f  雪 %.2f" % (f, Wgrass(f), Wrock(f), Wsnow(f)), size=14, fill=INK)
    scene.Text(root, 50, 380, "傾き（急斜面は岩）なども使う。合計は 1", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "高さ 0 → 1")
    return dict(name=name, page=G + "terrain/texturing/weights.md", before="## 重みを決める", scene=scene, size=(780, 420), times=[1.0, 3.5, 6.5, 9.2])


def TriplanarStretch():
    name = "triplanar-weights"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="トライプラナー:斜面の向きで、3 方向のテクスチャを混ぜる")
    root = scene.root
    ax = Axes(scene, root, 50, 80, 330, 220, 90.0, 1.0, "斜面の傾き（0° = 平ら、90° = 垂直な崖）", "重み")

    def Wt(a):
        s = abs(math.sin(math.radians(a))) ** 4
        c = abs(math.cos(math.radians(a))) ** 4
        return c / (s + c), s / (s + c)

    ax.Curve(lambda a: Wt(a)[0], BLUE, 4, n=60)
    ax.Curve(lambda a: Wt(a)[1], RED, 4, n=60)
    scene.Text(root, ax.X(8), ax.Y(0.9), "上から（XZ）", size=13, fill=BLUE)
    scene.Text(root, ax.X(62), ax.Y(0.9), "横から（XY）", size=13, fill=RED)
    dot1 = root.add("circle", cx=ax.X(0), cy=ax.Y(1.0), r=6, fill=BLUE, stroke="#ffffff", stroke_width=1.5)
    dot2 = root.add("circle", cx=ax.X(0), cy=ax.Y(0.0), r=6, fill=RED, stroke="#ffffff", stroke_width=1.5)
    # 右:斜面
    sx, sy, L = 480, 330, 200
    ground = root.add("line", x1=sx - 80, y1=sy, x2=sx + 220, y2=sy, stroke="#a8a29e", stroke_width=2)
    slope = root.add("line", x1=sx, y1=sy, x2=sx + L, y2=sy, stroke="#b8794b", stroke_width=10)
    steps = 30
    t0, t1 = 0.8, 9.5
    prev = None
    for i in range(steps + 1):
        f = i / steps
        a = 88 * f
        wa = Wt(a)
        t = Lerp(t0, t1, f)
        ex, ey = sx + L * math.cos(math.radians(a)) * 0.8, sy - L * math.sin(math.radians(a)) * 0.9
        vals = [(dot1, "cx", ax.X(a)), (dot1, "cy", ax.Y(wa[0])), (dot2, "cx", ax.X(a)), (dot2, "cy", ax.Y(wa[1])), (slope, "x2", R(ex)), (slope, "y2", R(ey))]
        for node, attr, v in vals:
            if i == 0:
                node.Set(t, attr, v)
            else:
                node.Ramp(prev, t, attr, v)
        prev = t
    LiveText(scene, root, 50, 346, t0, t1, steps, lambda i, f: "傾き %d° → 上から %.2f、横から %.2f" % (round(88 * f), Wt(88 * f)[0], Wt(88 * f)[1]), size=14, fill=INK)
    scene.Text(root, 50, 380, "平らな所は、上から貼ったテクスチャ。崖に近づくと、横から貼ったテクスチャに切り替わる → 縦に伸びない。", size=13, weight=500, fill=GRAY)
    scene.Note(t0, name, "傾き 0 → 88°")
    return dict(name=name, page=G + "terrain/texturing/triplanar.md", before="## トライプラナー", scene=scene, size=(780, 420), times=[1.0, 3.5, 6.5, 9.2])


def TilingHide():
    name = "tiling-hide"
    scene = NewScene(name, 780, 400, duration=9.0, hold=1.5, title="繰り返しを隠す:周期の違う 2 つのパターンを、重ねる")
    root = scene.root
    x0, x1 = 60, 720
    rows = [("パターン A（周期 110）", 110, 110, BLUE), ("パターン B（周期 163、別のスケール）", 200, 163, GREEN), ("重ねた結果", 310, None, RED)]
    for title, y, per, col in rows:
        root.add("line", x1=x0, y1=y + 30, x2=x1, y2=y + 30, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, x0, y - 30, title, size=13, fill=col)
    xs_a = [x0 + 40 + k * 110 for k in range(6)]
    xs_b = [x0 + 90 + k * 163 for k in range(4)]
    t0 = 1.0
    for k, x in enumerate(xs_a):
        c = root.add("circle", cx=x, cy=140, r=14, fill=BLUE, opacity=0)
        c.Show(t0 + k * 0.25)
    for k, x in enumerate(xs_b):
        c = root.add("circle", cx=x, cy=230, r=14, fill=GREEN, opacity=0)
        c.Show(t0 + 1.8 + k * 0.25)
    # 結果:2 つの足し合わせ(強さ)
    import random as _r
    pts = []
    for x in range(x0, x1 + 1, 4):
        v = 0.0
        for xa in xs_a:
            v += math.exp(-((x - xa) ** 2) / (2 * 16 ** 2))
        for xb in xs_b:
            v += math.exp(-((x - xb) ** 2) / (2 * 16 ** 2)) * 1.0
        pts.append((x, 340 - 40 * v))
    root.add("path", d=PathD(pts), fill="none", stroke=RED, stroke_width=4, opacity=0).Show(t0 + 4.0)
    peaks = []
    for x in range(x0 + 8, x1 - 8, 4):
        pass
    scene.TextStack(root, 60, 376, [(0.0, 5.0, "A も B も、それぞれ等間隔（規則的な繰り返し）"), (5.0, 20, "重ねると、山の位置と高さが不揃い → 繰り返しが目立たない（周期が公約数を持たないほど良い）")], size=14, fill=INK)
    scene.Note(t0, name, "A → B → 重ねる")
    return dict(name=name, page=G + "terrain/texturing/tiling.md", before="## 繰り返し", scene=scene, size=(780, 400), times=[1.5, 3.5, 6.0, 8.5])


def GrassWind():
    name = "grass-wind"
    scene = NewScene(name, 780, 400, duration=8.0, hold=0.0, title="風:先端ほど大きく、位置ごとに位相をずらして揺らす")
    root = scene.root
    base = 330
    root.add("rect", x=40, y=base, width=700, height=20, fill="#a16207", fill_opacity=0.5)
    blades = []
    n = 24
    T = 8.0
    frames = 32
    for i in range(n):
        x = 70 + i * 28
        h = 90 + 25 * math.sin(i * 1.7)
        ph = i * 0.45
        ln = root.add("path", d="M%s,%s Q%s,%s %s,%s" % (x, base, x, base - h * 0.6, x, base - h), fill="none", stroke="#16a34a", stroke_width=5, stroke_linecap="round")
        for f in range(frames + 1):
            t = T * f / frames
            sway = 28 * math.sin(2 * math.pi * t / T + ph) + 8 * math.sin(4 * math.pi * t / T + ph * 2)
            d = "M%s,%s Q%s,%s %s,%s" % (x, base, R(x + sway * 0.25), R(base - h * 0.6), R(x + sway), R(base - h))
            if f == 0:
                ln.Set(t, "d", d)
            else:
                ln.Ramp(T * (f - 1) / frames, t, "d", d)
    scene.TextStack(root, 40, 60, [(0.0, 20, "根元は動かず（頂点カラーで 0）、先端ほど大きく揺れる。隣と位相がずれて、波のように見える")], size=14, fill=INK)
    scene.Text(root, 40, 380, "頂点シェーダーで、位置と時間から、サイン波とノイズで先端をずらす。風向き・強さは、全体で共有する。", size=13, weight=500, fill=GRAY)
    scene.Note(0.0, name, "風で揺れる")
    return dict(name=name, page=G + "terrain/vegetation/wind.md", before="## 風", scene=scene, size=(780, 400), times=[0.5, 2.0, 4.0, 6.0])


def FbmOctaves():
    name = "fbm-octaves"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="fBm:周波数を倍・振幅を半分で、ノイズを重ねる")
    root = scene.root
    x0, x1, base = 60, 720, 300
    rnd = random.Random(31)
    pts_n = [[rnd.uniform(-1, 1) for _ in range(40)] for _ in range(6)]

    def Noise(o, x):
        f = 2 ** o
        u = (x - x0) / (x1 - x0) * 4 * f
        i = int(u)
        fr = u - i
        a, b = pts_n[o][i % 40], pts_n[o][(i + 1) % 40]
        fr = fr * fr * (3 - 2 * fr)
        return a + (b - a) * fr

    def H(n, x):
        return sum(Noise(o, x) * (0.5 ** o) for o in range(n)) * 75

    root.add("line", x1=x0, y1=base, x2=x1, y2=base, stroke=LIGHT, stroke_width=1.5)
    p = root.add("path", d=PathD([(x, base - H(1, x)) for x in range(x0, x1 + 1, 3)]), fill="none", stroke=BLUE, stroke_width=4)
    seq = [(2.5, 1), (4.5, 2), (6.5, 3), (8.5, 5)]
    for (t, n) in seq[1:]:
        p.Ramp(t - 0.9, t, "d", PathD([(x, base - H(n, x)) for x in range(x0, x1 + 1, 3)]))
    scene.TextStack(root, 60, 70, [(0.0, 3.4, "オクターブ 1:大きなうねりだけ"), (3.4, 5.4, "オクターブ 2:中くらいの起伏が加わる"), (5.4, 7.4, "オクターブ 3:小さな起伏"), (7.4, 20, "オクターブ 5:細かい凹凸まで。自然な地形に近い")], size=18, fill=INK)
    scene.TextStack(root, 60, 100, [(0.0, 20, "各オクターブで、周波数は 2 倍、振幅は 0.5 倍")], size=13, fill=GRAY, weight=500)
    scene.Text(root, 60, 380, "足すオクターブが多いほど細かいが、コストも増える。山脈にはリッジ ノイズ、うねりにはドメイン ワーピングを組み合わせる。", size=13, weight=500, fill=GRAY)
    scene.Note(2.5, name, "オクターブ 1 → 5")
    return dict(name=name, page=G + "terrain/generation/fbm.md", before="## fBm", scene=scene, size=(780, 420), times=[1.0, 4.0, 6.0, 10.0])


def ErosionDroplet():
    name = "erosion-droplet"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="侵食:水滴が斜面を流れ、削って、低い所に積もらせる")
    root = scene.root
    x0, x1 = 60, 720
    base = 340

    def H0(x):
        return 40 + 170 * math.exp(-((x - 230) ** 2) / (2 * 90 ** 2)) + 60 * math.exp(-((x - 500) ** 2) / (2 * 70 ** 2))

    def Erode(x, k):
        # k = 0..1:山の斜面を削り、谷に堆積
        cut = 55 * k * math.exp(-((x - 290) ** 2) / (2 * 50 ** 2))
        dep = 45 * k * math.exp(-((x - 395) ** 2) / (2 * 35 ** 2))
        return H0(x) - cut + dep

    xs = list(range(x0, x1 + 1, 4))
    poly = root.add("polygon", points=" ".join("%s,%s" % (x, R(base - Erode(x, 0))) for x in xs) + " %s,%s %s,%s" % (x1, base + 20, x0, base + 20), fill="#d6c7a1", stroke="#a16207", stroke_width=2)
    seq = [(1.0, 0.0), (4.0, 0.4), (7.0, 0.8), (10.0, 1.0)]
    for idx in range(1, len(seq)):
        ta, ka = seq[idx - 1]
        tb, kb = seq[idx]
        poly.Ramp(ta + 0.3, tb, "points", " ".join("%s,%s" % (x, R(base - Erode(x, kb))) for x in xs) + " %s,%s %s,%s" % (x1, base + 20, x0, base + 20))
    drop = root.add("circle", cx=200, cy=base - Erode(200, 0) - 10, r=9, fill="#38bdf8", stroke="#ffffff", stroke_width=2)
    n = 18
    for round_i in range(3):
        ta = 1.0 + round_i * 3.0
        k = [0.0, 0.4, 0.8][round_i]
        prev = None
        for i in range(n + 1):
            f = i / n
            x = 190 + f * 260
            y = base - Erode(x, k) - 10
            t = ta + f * 2.6
            if round_i == 0 and i == 0:
                drop.Set(t, "cx", R(x)); drop.Set(t, "cy", R(y))
            elif i == 0:
                drop.Set(t, "cx", R(x)); drop.Set(t, "cy", R(y))
            else:
                drop.Ramp(prev, t, "cx", R(x)); drop.Ramp(prev, t, "cy", R(y))
            prev = t
    scene.TextStack(root, 60, 60, [(0.0, 1.0, "山と谷のある地形"), (1.0, 3.8, "水滴 1:斜面を流れて、土を削る（急な所ほど多く）"), (3.8, 6.8, "水滴 2:さらに削る。削った土は、水滴が運ぶ"), (6.8, 9.8, "水滴 3:勾配が緩くなる所で、土を積もらせる"), (9.8, 20, "数十万の水滴で、谷と尾根が刻まれた自然な地形になる")], size=15, fill=INK)
    scene.Text(root, 60, 400, "削る量は傾きと水量、積もる量は運んだ土の量で決まる。重いので、事前計算が普通。", size=13, weight=500, fill=GRAY)
    scene.Note(1.0, name, "水滴 3 つ")
    return dict(name=name, page=G + "terrain/generation/erosion.md", before="## 侵食", scene=scene, size=(780, 420), times=[0.8, 3.0, 6.0, 11.0])


def DomainWarp():
    name = "domain-warp"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="ドメイン ワーピング:座標を別のノイズでゆがませると、有機的な形になる")
    root = scene.root
    x0, y0, w, h = 120, 80, 320, 280
    root.add("rect", x=x0, y=y0, width=w, height=h, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    nl = 9

    def Warp(u, v, k):
        dx = k * (22 * math.sin(v * 5.3 + 1.0) + 9 * math.sin(u * 9.1 + v * 3.0))
        dy = k * (22 * math.sin(u * 4.7 + 2.0) + 9 * math.sin(v * 8.3 + u * 2.5))
        return dx, dy

    lines = []
    for i in range(nl):
        u = i / (nl - 1)
        for kind in ("v", "h"):
            p = root.add("path", d="M0,0", fill="none", stroke=BLUE if kind == "v" else GREEN, stroke_width=2.5)
            lines.append((p, u, kind))

    def D(u, kind, k):
        pts = []
        for j in range(25):
            s = j / 24
            uu, vv = (u, s) if kind == "v" else (s, u)
            dx, dy = Warp(uu, vv, k)
            pts.append((x0 + uu * w + dx, y0 + vv * h + dy))
        return PathD(pts)

    seq = [(0.8, 0.0), (2.5, 0.0), (6.0, 1.0), (8.5, 1.0), (11.5, 0.35)]
    for p, u, kind in lines:
        for idx, (t, k) in enumerate(seq):
            if idx == 0:
                p.Set(t, "d", D(u, kind, k))
            else:
                p.Ramp(seq[idx - 1][0], t, "d", D(u, kind, k))
    scene.TextStack(root, 480, 140, [(0.0, 2.5, "元の座標（まっすぐな格子）"), (2.5, 6.0, "別のノイズで、座標をずらしていく…"), (6.0, 8.5, "ゆがみの強さ 1:うねった、有機的な形"), (8.5, 20, "強さを下げると、ゆがみが弱まる")], size=16, fill=INK)
    scene.Text(root, 480, 190, "f(p) → f(p + g(p))", size=18, fill=BLUE)
    scene.Text(root, 480, 220, "ノイズ f の入力 p を、別のノイズ g でずらす。", size=13, fill=GRAY, weight=500)
    scene.Text(root, 480, 244, "規則的な模様が崩れ、川や雲のような形になる。", size=13, fill=GRAY, weight=500)
    scene.Note(0.8, name, "強さ 0 → 1 → 0.35")
    return dict(name=name, page=G + "terrain/generation/domain-warp.md", before="## ドメイン ワーピング", scene=scene, size=(780, 420), times=[1.0, 4.0, 7.0, 11.0])


FIGS = [SineSum, NormalBlend, FftSpectrum, WaterFresnel, ShoreFoamDepth, FlowMapBlend, CausticsRays, SnellWindow, HeightmapLift, LodMorph, LodCracks, SplatWeights, TriplanarStretch, TilingHide, GrassWind, FbmOctaves, ErosionDroplet, DomainWarp]
