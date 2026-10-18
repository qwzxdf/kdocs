import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402

BEFORE = "## よくあるミス"


def Arr(scene, parent, x1, y1, x2, y2, color=INK, width=2.5, opacity=1):
    return parent.add("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=width, marker_end=scene.marker, opacity=opacity)


def Utf8Pack():
    name = "utf8-pack"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="「あ」(U+3042) を UTF-8 の 3 バイトに詰める")
    root = scene.root
    cp = 0x3042
    bits = format(cp, "016b")
    assert bits == "0011000001000010" and "あ".encode("utf-8") == b"\xe3\x81\x82"
    groups = [(0, 4), (4, 10), (10, 16)]
    cols = [BLUE, GREEN, AMBER]
    cs = 26
    ox = 100
    scene.Text(root, ox, 90, "コードポイント U+3042 を 2 進数に(16 ビット)", size=13, weight=700, fill=GRAY)
    for gi, (a, b) in enumerate(groups):
        for i in range(a, b):
            g = root.add("g", opacity=0)
            g.add("rect", x=ox + i * (cs + 2) + gi * 8, y=100, width=cs, height=cs, fill=cols[gi], opacity=0.85)
            scene.Text(g, ox + i * (cs + 2) + gi * 8 + cs / 2, 119, bits[i], size=14, weight=700, fill="#ffffff", anchor="middle")
            g.Show(1.0)
    prefixes = ["1110", "10", "10"]
    byte_x = [100, 330, 560]
    expected = ["e3", "81", "82"]
    for k in range(3):
        a, b = groups[k]
        pre = prefixes[k]
        payload = bits[a:b]
        s = pre + payload
        assert len(s) == 8 and format(int(s, 2), "02x") == expected[k]
        t = 4.0 + k * 2.6
        g = root.add("g", opacity=0)
        for i, ch in enumerate(s):
            is_pre = i < len(pre)
            g.add("rect", x=byte_x[k] + i * 25, y=230, width=23, height=26, fill=(GRAY if is_pre else cols[k]), opacity=0.85)
            scene.Text(g, byte_x[k] + i * 25 + 11.5, 249, ch, size=13, weight=700, fill="#ffffff", anchor="middle")
        scene.Text(g, byte_x[k] + 100, 285, "= %s" % expected[k].upper(), size=18, weight=700, fill=cols[k], anchor="middle")
        g.Show(t)
        Arr(scene, root, ox + (a + b) / 2 * (cs + 2) + k * 8, 132, byte_x[k] + 100, 224, color=cols[k], width=2, opacity=0).Show(t)
    scene.Text(root, 100, 215, "3 バイト形式の枠（灰色 = 目印のビット、色付き = 中身）", size=13, weight=700, fill=GRAY)
    scene.TextStack(root, 390, 350, [(0.0, 1.0, "文字に番号(コードポイント)が付いている"), (1.0, 4.0, "16 ビットを 4 + 6 + 6 に分ける"), (4.0, 6.6, "先頭バイト: 目印 1110 + 上位 4 ビット = E3"), (6.6, 9.2, "2 バイト目: 目印 10 + 次の 6 ビット = 81"), (9.2, 20, "3 バイト目: 目印 10 + 残りの 6 ビット = 82。「あ」 = E3 81 82")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "ビットを詰める")
    return dict(name=name, page="encoding/conversion.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.0, 8.0, 12.0])


def MojibakeDecode():
    name = "mojibake-decode"
    text = "こんにちは"
    data = text.encode("utf-8")
    wrong = data.decode("cp932", errors="replace")
    assert data.decode("utf-8") == text and wrong != text
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="同じバイト列でも、読み方を間違えると別の文字になる")
    root = scene.root
    scene.Text(root, 70, 90, "ファイルに入っているバイト列（UTF-8 で保存した「こんにちは」）", size=13, weight=700, fill=GRAY)
    for i, b in enumerate(data):
        x = 70 + i * 42
        root.add("rect", x=x, y=105, width=38, height=32, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, x + 19, 127, "%02X" % b, size=13, weight=700, fill=INK, anchor="middle")
    a = scene.Text(root, 70, 205, "UTF-8 として読む → " + text, size=22, weight=700, fill=GREEN, opacity=0)
    a.Show(3.0)
    scene.Text(root, 70, 235, "正しい。ソースも保存形式も UTF-8 なら、こう読まれる", size=12, weight=500, fill=GRAY, opacity=0).Show(3.0)
    b = scene.Text(root, 70, 300, "Shift_JIS (CP932) として読む → " + wrong, size=22, weight=700, fill=RED, opacity=0)
    b.Show(7.0)
    scene.Text(root, 70, 330, "バイトは同じ。読む側の文字コードが違うだけで、文字化けになる(データは壊れていない)", size=12, weight=500, fill=GRAY, opacity=0).Show(7.0)
    scene.Note(3.0, name, "読み方を変える")
    return dict(name=name, page="encoding/mojibake.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 4.0, 8.0, 11.0])


def HizPyramid():
    name = "hiz-pyramid"
    scene = NewScene(name, 780, 460, duration=15.0, hold=1.5, title="Hi-Z: 4 マスの最も奥の深度を取って、半分の大きさに縮める")
    root = scene.root
    d0 = [[0.20, 0.30, 0.80, 0.90], [0.25, 0.35, 0.70, 0.95], [0.50, 0.40, 0.60, 0.65], [0.55, 0.45, 0.50, 0.75]]
    d1 = [[max(d0[2 * r][2 * c], d0[2 * r][2 * c + 1], d0[2 * r + 1][2 * c], d0[2 * r + 1][2 * c + 1]) for c in range(2)] for r in range(2)]
    d2 = [[max(max(row) for row in d1)]]
    assert d1 == [[0.35, 0.95], [0.55, 0.75]] and d2 == [[0.95]]
    levels = [(d0, 56, 70, "元の深度（4×4）"), (d1, 90, 380, "2×2（各 4 マスの最大）"), (d2, 120, 600, "1×1（全体の最大）")]
    for lv, (grid, cs, ox, lab) in enumerate(levels):
        n = len(grid)
        oy = 100 + (4 * 56 - n * cs) / 2
        g = root.add("g", opacity=0)
        for r in range(n):
            for c in range(n):
                v = grid[r][c]
                g.add("rect", x=ox + c * cs, y=oy + r * cs, width=cs - 3, height=cs - 3, fill=Mix("#e2e8f0", "#475569", v), stroke="#94a3b8", stroke_width=1.5)
                scene.Text(g, ox + c * cs + (cs - 3) / 2, oy + r * cs + cs / 2 + 4, "%.2f" % v, size=14 if cs < 100 else 18, weight=700, fill=("#ffffff" if v > 0.5 else INK), anchor="middle")
        scene.Text(g, ox, 85, lab, size=13, weight=700, fill=GRAY)
        g.Show(1.0 + lv * 3.0)
    scene.TextStack(root, 390, 350, [(0.0, 1.0, "深度の値: 小さいほど手前、大きいほど奥"), (1.0, 4.0, "元の深度バッファ（一部）"), (4.0, 7.0, "4 マスずつ、最も大きい(奥の)値を残す"), (7.0, 10.0, "もう一度縮めると、画面全体で最も奥の値 0.95"), (10.0, 14.0, "物体の最も手前の深度が 0.97 → 0.95 より奥 → 完全に隠れている → 捨てる"), (14.0, 20.0, "")], size=14, fill=INK, anchor="middle")
    scene.TextStack(root, 390, 385, [(0.0, 10.0, ""), (10.0, 20.0, "物体の最も手前が 0.50 なら、0.95 より手前 → 隠れていない可能性 → 描く")], size=14, fill=RED, anchor="middle")
    scene.Note(1.0, name, "縮める")
    return dict(name=name, page="rendering/hiz.md", before=BEFORE, scene=scene, size=(780, 460), times=[2.0, 5.0, 8.0, 12.0])


def TiledLights():
    name = "tiled-light-count"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="Tiled: 画面をタイルに分け、タイルごとに、光が届く数を数える")
    root = scene.root
    cols_n, rows_n, ts = 8, 5, 64
    ox, oy = 130, 90
    lights = [(2.0, 1.5, 1.3, BLUE), (5.5, 3.0, 1.7, GREEN), (6.2, 1.2, 1.0, AMBER)]

    def hit(c, r, lt):
        cx, cy, rad, _ = lt
        nx = max(c, min(cx, c + 1))
        ny = max(r, min(cy, r + 1))
        return (cx - nx) ** 2 + (cy - ny) ** 2 <= rad * rad

    counts = [[[sum(1 for lt in lights[:s + 1] if hit(c, r, lt)) for c in range(cols_n)] for r in range(rows_n)] for s in range(3)]
    for r in range(rows_n):
        for c in range(cols_n):
            root.add("rect", x=ox + c * ts, y=oy + r * ts, width=ts - 2, height=ts - 2, fill="#ffffff", stroke="#cbd5e1", stroke_width=1.5)
    for s in range(3):
        t0 = 1.0 + s * 3.8
        t1 = 1.0 + (s + 1) * 3.8 if s < 2 else None
        for r in range(rows_n):
            for c in range(cols_n):
                v = counts[s][r][c]
                if v:
                    ov = root.add("rect", x=ox + c * ts, y=oy + r * ts, width=ts - 2, height=ts - 2, fill=RED, opacity=0)
                    ov.Set(t0, "opacity", 0.15 + 0.22 * v)
                    if t1:
                        ov.Set(t1, "opacity", 0)
                tx = scene.Text(root, ox + c * ts + ts / 2 - 1, oy + r * ts + ts / 2 + 6, str(v), size=18, weight=700, fill=INK, anchor="middle", opacity=0)
                tx.Show(t0, t1)
    for s, (cx, cy, rad, col) in enumerate(lights):
        t0 = 1.0 + s * 3.8
        circ = root.add("circle", cx=ox + cx * ts, cy=oy + cy * ts, r=rad * ts, fill="none", stroke=col, stroke_width=3, opacity=0)
        circ.Show(t0)
        dot = root.add("circle", cx=ox + cx * ts, cy=oy + cy * ts, r=6, fill=col, opacity=0)
        dot.Show(t0)
    tot = sum(counts[2][r][c] for r in range(rows_n) for c in range(cols_n))
    scene.Text(root, ox, 75, "各マス = 1 タイル。数字 = そのタイルに届く光の数", size=13, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 430, [(0.0, 1.0, "光が 3 個ある画面"), (1.0, 4.8, "光 1 個目の円に触れるタイルが、+1"), (4.8, 8.6, "2 個目を足す。重なったタイルは 2"), (8.6, 20, "3 個目まで。各タイルは、数えた光だけ計算すればよい")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "光を 1 個ずつ足す")
    return dict(name=name, page="rendering/light-culling.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 9.5, 12.5])


def HaltonJitter():
    name = "halton-jitter"

    def Halton(i, b):
        f, r = 1.0, 0.0
        while i > 0:
            f /= b
            r += f * (i % b)
            i //= b
        return r

    pts = [(Halton(i, 2), Halton(i, 3)) for i in range(1, 9)]
    assert pts[0] == (0.5, 1 / 3) and abs(pts[1][0] - 0.25) < 1e-12 and abs(pts[1][1] - 2 / 3) < 1e-12
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="TAA のジッター: フレームごとに、1 画素の中の別の位置で描く(Halton 2,3)")
    root = scene.root
    x0, y0, s = 240, 90, 300
    root.add("rect", x=x0, y=y0, width=s, height=s, fill="#f8fafc", stroke="#94a3b8", stroke_width=2)
    root.add("line", x1=x0 + s / 2, y1=y0, x2=x0 + s / 2, y2=y0 + s, stroke=LIGHT, stroke_width=1)
    root.add("line", x1=x0, y1=y0 + s / 2, x2=x0 + s, y2=y0 + s / 2, stroke=LIGHT, stroke_width=1)
    scene.Text(root, x0, y0 - 10, "1 画素の内側（正方形）。点 = そのフレームのサンプル位置", size=12, weight=500, fill=GRAY)
    for i, (u, v) in enumerate(pts):
        t = 1.0 + i * 1.2
        d = root.add("g", opacity=0)
        d.add("circle", cx=x0 + u * s, cy=y0 + (1 - v) * s, r=9, fill=[BLUE, GREEN, AMBER, RED, PURPLE, BLUE, GREEN, AMBER][i], opacity=0.9)
        scene.Text(d, x0 + u * s, y0 + (1 - v) * s + 4, str(i + 1), size=11, weight=700, fill="#ffffff", anchor="middle")
        d.Show(t)
    scene.TextStack(root, 390, 420, [(0.0, 1.0, "毎フレーム、カメラをほんの少し(1 画素以内)ずらす"), (1.0, 5.0, "1〜4 フレーム目: 離れた位置を順に使う"), (5.0, 20, "8 フレームで、画素の中をまんべんなく巡る。これを平均して高精細にする")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "フレーム 1 → 8")
    return dict(name=name, page="rendering/taa-upscaling.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 3.5, 6.0, 10.0])


def PrefixCompact():
    name = "prefix-compact"
    scene = NewScene(name, 780, 440, duration=15.0, hold=1.5, title="カリング結果の詰め直し: 見える物の番号を、隙間なく並べる")
    root = scene.root
    flags = [1, 0, 1, 1, 0, 0, 1, 0]
    pre = [sum(flags[:i]) for i in range(8)]
    visible = [i for i in range(8) if flags[i]]
    assert pre == [0, 1, 1, 2, 3, 3, 3, 4] and visible == [0, 2, 3, 6]
    cs, ox = 58, 160
    rows = [("物体の番号", 95, GRAY), ("見える? (1 = 見える)", 160, BLUE), ("手前までの合計(出力位置)", 225, GREEN)]
    for lab, y, col in rows:
        scene.Text(root, ox - 12, y + 26, lab, size=12, weight=700, fill=col, anchor="end")
    for i in range(8):
        x = ox + i * cs
        root.add("rect", x=x, y=95, width=cs - 4, height=40, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        scene.Text(root, x + (cs - 4) / 2, 121, str(i), size=15, weight=700, fill=GRAY, anchor="middle")
        g1 = root.add("g", opacity=0)
        g1.add("rect", x=x, y=160, width=cs - 4, height=40, fill=(BLUE if flags[i] else "#f1f5f9"), stroke="#94a3b8", stroke_width=1.5, opacity=0.85)
        scene.Text(g1, x + (cs - 4) / 2, 186, str(flags[i]), size=15, weight=700, fill=("#ffffff" if flags[i] else GRAY), anchor="middle")
        g1.Show(1.0)
        g2 = root.add("g", opacity=0)
        g2.add("rect", x=x, y=225, width=cs - 4, height=40, fill=("#dcfce7" if flags[i] else "#f1f5f9"), stroke="#94a3b8", stroke_width=1.5)
        scene.Text(g2, x + (cs - 4) / 2, 251, str(pre[i]), size=15, weight=700, fill=(GREEN if flags[i] else GRAY), anchor="middle")
        g2.Show(4.0)
    scene.Text(root, ox - 12, 316, "出力（描く物の一覧）", size=12, weight=700, fill=AMBER, anchor="end")
    for k in range(4):
        x = ox + k * cs
        root.add("rect", x=x, y=290, width=cs - 4, height=40, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        g3 = root.add("g", opacity=0)
        g3.add("rect", x=x, y=290, width=cs - 4, height=40, fill=AMBER, opacity=0.85)
        scene.Text(g3, x + (cs - 4) / 2, 316, str(visible[k]), size=15, weight=700, fill="#ffffff", anchor="middle")
        g3.Show(7.5 + k * 1.2)
    scene.TextStack(root, 390, 385, [(0.0, 1.0, "GPU が 8 個の物体を同時に調べる"), (1.0, 4.0, "見える物は 1、隠れた物は 0"), (4.0, 7.5, "手前までの 1 の合計を計算する(プレフィックス サム)。これが出力位置"), (7.5, 20, "見える物だけが、自分の出力位置に番号を書き込む。描画命令の数は 4 つ")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "フラグ → 合計 → 詰め直し")
    return dict(name=name, page="rendering/gpu-driven-dx12/culling.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 8.5, 11.5])


def GridCell():
    name = "grid-cell-lookup"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="位置からマスの番号を求める: セルの大きさで割って、切り捨てる")
    root = scene.root
    cell, cols_n, rows_n, ts = 10.0, 6, 4, 70
    ox, oy = 150, 90
    for r in range(rows_n):
        for c in range(cols_n):
            root.add("rect", x=ox + c * ts, y=oy + r * ts, width=ts - 2, height=ts - 2, fill="#ffffff", stroke="#cbd5e1", stroke_width=1.5)
            scene.Text(root, ox + c * ts + ts / 2 - 1, oy + r * ts + ts / 2 + 4, "(%d,%d)" % (c, r), size=11, weight=500, fill=LIGHT if False else "#94a3b8", anchor="middle")
    pts = [(37.4, 12.9), (8.0, 31.5), (59.9, 0.1)]
    items = []
    for k, (px, py) in enumerate(pts):
        cx, cy = math.floor(px / cell), math.floor(py / cell)
        t0 = 1.0 + k * 3.8
        t1 = 1.0 + (k + 1) * 3.8 if k < 2 else None
        ov = root.add("rect", x=ox + cx * ts, y=oy + cy * ts, width=ts - 2, height=ts - 2, fill=AMBER, opacity=0)
        ov.Show(t0, t1)
        dt = root.add("circle", cx=ox + px / cell * ts, cy=oy + py / cell * ts, r=8, fill=RED, opacity=0)
        dt.Show(t0, t1)
        items.append((t0, t1 if t1 else 99, "(%.1f, %.1f) ÷ 10 = (%.2f, %.2f) → 切り捨て → マス (%d, %d)" % (px, py, px / cell, py / cell, cx, cy)))
    assert [(math.floor(x / cell), math.floor(y / cell)) for x, y in pts] == [(3, 1), (0, 3), (5, 0)]
    scene.Text(root, ox, oy - 12, "原点 (0, 0) は左上。y は下向き。セル 1 つ = 10 × 10", size=12, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 415, [(0.0, 1.0, "ゲームの座標から、配列の番号を求める")] + items, size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "点を 3 つ調べる")
    return dict(name=name, page="gamemath/grids.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 9.0, 12.0])


def DotProjection():
    name = "dot-projection"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="内積 = a を b に落とした影の長さ(b の長さが 1 のとき)")
    root = scene.root
    ox, oy, blen, alen = 200, 220, 300, 160
    root.add("line", x1=ox - 150, y1=oy, x2=ox + blen + 40, y2=oy, stroke=LIGHT, stroke_width=1.5)
    Arrow(scene, root, ox, oy, ox + blen, oy, color=BLUE, width=4)
    scene.Text(root, ox + blen, oy + 24, "b（長さ 1 とする）", size=13, weight=700, fill=BLUE, anchor="end")
    a_line = root.add("line", x1=ox, y1=oy, x2=ox + alen, y2=oy, stroke=RED, stroke_width=4)
    guide = root.add("line", x1=ox + alen, y1=oy, x2=ox + alen, y2=oy, stroke=GRAY, stroke_width=2, stroke_dasharray="5 4")
    shadow = root.add("circle", cx=ox + alen, cy=oy, r=8, fill=GREEN)
    tip = root.add("circle", cx=ox + alen, cy=oy, r=7, fill=RED)
    scene.Text(root, ox - 10, oy - 98, "a（長さ 1 とする）", size=13, weight=700, fill=RED, anchor="end")
    n = 48
    prev = 1.0
    for i in range(n + 1):
        th = math.pi * i / n
        t = 1.0 + 10.0 * i / n
        ax_, ay_ = ox + alen * math.cos(th), oy - alen * math.sin(th)
        if i == 0:
            continue
        for node, attrs in ((a_line, {"x2": ax_, "y2": ay_}), (guide, {"x1": ax_, "y1": ay_, "x2": ax_}), (tip, {"cx": ax_, "cy": ay_}), (shadow, {"cx": ax_})):
            for k, v in attrs.items():
                node.Ramp(prev, t, k, v)
        prev = t
    assert abs(math.cos(math.radians(60)) - 0.5) < 1e-12
    LiveText(scene, root, 390, 385, 1.0, 11.0, 4, lambda i, f: ["0〜45 度: 内積は 1 → 0.7。ほぼ同じ向き", "45〜90 度: 0.7 → 0。影が短くなる", "90〜135 度: 0 → −0.7。直角を超えると負(後ろ向き)", "135〜180 度: −0.7 → −1。完全に反対向き"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "a を 0 → 180 度回す")
    return dict(name=name, page="gamemath/vector-recipes.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 3.5, 6.5, 9.5])


def MoveCopy():
    name = "move-vs-copy"
    scene = NewScene(name, 780, 460, duration=14.0, hold=1.5, title="コピーは中身を複製する。ムーブは中身を持ち主ごと引っ越す")
    root = scene.root

    def Obj(x, y, label, col, opacity_kw=None):
        g = root.add("g", **({"opacity": 0} if opacity_kw else {}))
        g.add("rect", x=x, y=y, width=110, height=50, fill="#ffffff", stroke=col, stroke_width=2.5)
        scene.Text(g, x + 55, y + 22, label, size=13, weight=700, fill=col, anchor="middle")
        scene.Text(g, x + 55, y + 40, "ptr / size", size=11, weight=500, fill=GRAY, anchor="middle")
        return g

    def Buf(x, y, col, show_t=None):
        g = root.add("g", **({"opacity": 0} if show_t is not None else {}))
        for i, v in enumerate([10, 20, 30]):
            g.add("rect", x=x + i * 40, y=y, width=36, height=36, fill=col, opacity=0.85)
            scene.Text(g, x + i * 40 + 18, y + 24, str(v), size=13, weight=700, fill="#ffffff", anchor="middle")
        if show_t is not None:
            g.Show(show_t)
        return g

    scene.Text(root, 40, 80, "コピー  B = A", size=15, weight=700, fill=RED)
    Obj(60, 100, "A", GRAY)
    Buf(330, 107, GRAY)
    Arrow(scene, root, 170, 125, 326, 125, color=GRAY, width=2)
    ob = Obj(60, 175, "B", RED, True)
    ob.Show(3.0)
    Buf(330, 182, RED, 3.0)
    Arr(scene, root, 170, 200, 326, 200, color=RED, width=2, opacity=0).Show(3.0)
    scene.Text(root, 520, 205, "新しい領域を確保して、3 個を複製", size=12, weight=700, fill=RED, opacity=0).Show(3.0)
    scene.Text(root, 40, 275, "ムーブ  D = std::move(C)", size=15, weight=700, fill=GREEN)
    Obj(60, 295, "C", GRAY)
    Buf(330, 302, GREEN)
    ac = Arr(scene, root, 170, 320, 326, 320, color=GRAY, width=2, opacity=1)
    ac.Set(8.0, "opacity", 0)
    od = Obj(60, 370, "D", GREEN, True)
    od.Show(8.0)
    Arr(scene, root, 170, 395, 330, 340, color=GREEN, width=2, opacity=0).Show(8.0)
    scene.Text(root, 520, 330, "ポインタだけを付け替える(複製なし)", size=12, weight=700, fill=GREEN, opacity=0).Show(8.0)
    scene.Text(root, 520, 355, "C は空になる(使わない)", size=12, weight=500, fill=GRAY, opacity=0).Show(8.0)
    scene.TextStack(root, 390, 440, [(0.0, 3.0, "同じ 3 個の配列を、2 通りで渡す"), (3.0, 8.0, "コピー: 領域の確保 + 要素の複製が必要。要素が多いほど遅い"), (8.0, 20, "ムーブ: ポインタの付け替えだけ。要素数に関係なく一定")], size=14, fill=INK, anchor="middle")
    scene.Note(3.0, name, "コピー → ムーブ")
    return dict(name=name, page="basics/move.md", before=BEFORE, scene=scene, size=(780, 460), times=[1.0, 4.0, 7.0, 11.0])


def VtableCall():
    name = "vtable-call"
    scene = NewScene(name, 780, 400, duration=14.0, hold=1.5, title="仮想関数の呼び出し: オブジェクト → 表 → 関数 と 2 回たどる")
    root = scene.root
    root.add("rect", x=50, y=120, width=170, height=90, fill="#ffffff", stroke=BLUE, stroke_width=2.5)
    scene.Text(root, 135, 110, "Slime のオブジェクト", size=13, weight=700, fill=BLUE, anchor="middle")
    scene.Text(root, 135, 150, "vptr（表への矢印）", size=13, weight=700, fill=INK, anchor="middle")
    scene.Text(root, 135, 190, "hp = 30", size=13, weight=500, fill=GRAY, anchor="middle")
    root.add("rect", x=310, y=120, width=170, height=90, fill="#ffffff", stroke=GREEN, stroke_width=2.5)
    scene.Text(root, 395, 110, "Slime の vtable（表）", size=13, weight=700, fill=GREEN, anchor="middle")
    scene.Text(root, 395, 150, "Update → Slime::Update", size=12, weight=700, fill=INK, anchor="middle")
    scene.Text(root, 395, 190, "Draw → Slime::Draw", size=12, weight=500, fill=GRAY, anchor="middle")
    root.add("rect", x=570, y=120, width=160, height=90, fill="#ffffff", stroke=AMBER, stroke_width=2.5)
    scene.Text(root, 650, 110, "実際のコード", size=13, weight=700, fill=AMBER, anchor="middle")
    scene.Text(root, 650, 160, "Slime::Update()", size=14, weight=700, fill=INK, anchor="middle")
    Arr(scene, root, 222, 150, 306, 150, color=RED, width=3, opacity=0).Show(4.0)
    Arr(scene, root, 482, 150, 566, 150, color=RED, width=3, opacity=0).Show(7.0)
    scene.Text(root, 50, 260, "enemy->Update()  ← 型は Enemy* でも、中身は Slime", size=14, weight=700, fill=GRAY)
    scene.TextStack(root, 390, 330, [(0.0, 1.0, "Enemy* で Slime を指している"), (1.0, 4.0, "① オブジェクトの先頭の vptr を読む"), (4.0, 7.0, "② vtable の「Update」の欄を読む"), (7.0, 11.0, "③ そこに書かれた関数 Slime::Update を呼ぶ(実行時に決まる)"), (11.0, 20, "普通の関数より、メモリを 2 回余計に読む。この差が、仮想関数のコスト")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "① → ② → ③")
    return dict(name=name, page="basics/virtual.md", before=BEFORE, scene=scene, size=(780, 400), times=[0.5, 2.5, 5.5, 9.0])


FIGS = [Utf8Pack, MojibakeDecode, HizPyramid, TiledLights, HaltonJitter, PrefixCompact, GridCell, DotProjection, MoveCopy, VtableCall]
