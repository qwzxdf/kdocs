import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402
from gfx_more4 import Morph, XLabel  # noqa: E402
from gfx_more7 import Arr, Box, Win  # noqa: E402

BEFORE = "## よくあるミス"


def Retarget(info, page):
    info["page"] = page
    return info


def ImguiFrame():
    name = "imgui-frame-loop"
    scene = NewScene(name, 780, 420, duration=16.0, hold=1.5, title="ImGui は毎フレーム、画面を最初から組み立て直す(状態は自分の変数に持つ)")
    root = scene.root
    boxes = [("NewFrame()", 70), ("ImGui::Button(...)\nなど、UI の呼び出し", 300), ("Render()\n→ 描画データ", 530)]
    names = ["NewFrame()", "Button() などの呼び出し", "Render() → 描画"]
    for k, (nm, x) in enumerate(zip(names, (70, 300, 530))):
        root.add("rect", x=x, y=120, width=190, height=80, fill="#ffffff", stroke="#94a3b8", stroke_width=2.5)
        scene.Text(root, x + 95, 166, nm, size=14, weight=700, fill=INK, anchor="middle")
        if k < 2:
            Arr(scene, root, x + 192, 160, x + 296, 160, color=GRAY, width=3)
    hp = [100, 100, 99, 99]
    frames = 3
    for f in range(frames):
        for k, x in enumerate((70, 300, 530)):
            t0 = 1.0 + f * 4.5 + k * 1.2
            ov = root.add("rect", x=x, y=120, width=190, height=80, fill=AMBER, opacity=0)
            ov.Set(t0, "opacity", 0.35)
            ov.Set(t0 + 1.2, "opacity", 0)
    items = [(0.0, 1.0, "ゲームのループが 1 回まわるのが、1 フレーム")]
    texts = ["フレーム 1: ボタンは押されていない → Button() は false を返す。hp = 100", "フレーム 2: ボタンが押された → Button() が true を返す。if の中で hp-- して 99 に", "フレーム 3: 押されていない → false。hp は 99 のまま(変数に残っている)"]
    for f in range(frames):
        items.append((1.0 + f * 4.5, 1.0 + (f + 1) * 4.5 if f < 2 else 99, texts[f]))
    scene.TextStack(root, 390, 290, items, size=14, fill=INK, anchor="middle")
    scene.Text(root, 390, 340, "UI の部品は残らない。毎回「いま何を表示するか」を書き直す(即時モード)", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "フレーム 1 → 3")
    return dict(name=name, page="libs/imgui/basics.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.5, 4.0, 7.0, 11.0])


def LayerMatrix():
    name = "layer-matrix"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="レイヤーの組み合わせで、「何と何をぶつけるか」を先に決める")
    root = scene.root
    layers = ["床（NON_MOVING）", "キャラ（MOVING）", "破片（DEBRIS）"]

    def hit(a, b):
        if a == 0 and b == 0:
            return False
        if a == 1 or b == 1:
            return True
        return (a, b) in ((0, 2), (2, 0))

    pairs = {(a, b) for a in range(3) for b in range(3) if a <= b and hit(a, b)}
    assert len(pairs) == 4 and hit(1, 2) and not hit(2, 2)
    cs, ox, oy = 110, 250, 120
    for i, l in enumerate(layers):
        scene.Text(root, ox - 12, oy + i * cs * 0.6 + cs * 0.3 + 4, l, size=13, weight=700, fill=INK, anchor="end")
        scene.Text(root, ox + i * cs + cs / 2 - 4, oy - 12, l, size=11, weight=700, fill=INK, anchor="middle")
    for r in range(3):
        for c in range(3):
            root.add("rect", x=ox + c * cs, y=oy + r * cs * 0.6 - 0 + r * 0, width=cs - 4, height=cs * 0.6 - 4, fill="#ffffff", stroke="#cbd5e1", stroke_width=1.5)
    # 行ごとに表示
    for r in range(3):
        t0 = 1.0 + r * 3.0
        g = root.add("g", opacity=0)
        for c in range(3):
            ok = hit(r, c)
            g.add("rect", x=ox + c * cs, y=oy + r * cs * 0.6, width=cs - 4, height=cs * 0.6 - 4, fill=("#bbf7d0" if ok else "#f1f5f9"), stroke="#94a3b8", stroke_width=1.5)
            scene.Text(g, ox + c * cs + cs / 2 - 2, oy + r * cs * 0.6 + cs * 0.3 + 6, "ぶつかる" if ok else "通り抜け", size=14, weight=700, fill=(GREEN if ok else GRAY), anchor="middle")
        g.Show(t0)
    scene.TextStack(root, 390, 340, [(0.0, 1.0, "3 つのレイヤーの、行 × 列の組み合わせを調べる"), (1.0, 4.0, "床: 床どうしは調べない。キャラと破片とは、ぶつかる"), (4.0, 7.0, "キャラ: 全部とぶつかる"), (7.0, 20, "破片: キャラとは通り抜け、破片どうしも通り抜け(数が多いので、計算を減らす)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "行を 1 つずつ見る")
    return dict(name=name, page="libs/jolt/layers.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 4.5, 8.0, 11.0])


def RaycastHit():
    name = "raycast-hit"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="レイキャスト: 線を伸ばし、最初に当たった物を返す")
    root = scene.root
    O = (90.0, 300.0)
    D = (1.0, -0.25)
    ln = math.hypot(*D)
    D = (D[0] / ln, D[1] / ln)
    boxes = [("B1", 250, 200, 80, 80, BLUE), ("B2", 430, 150, 90, 80, GREEN)]

    def slab(b):
        _, x, y, w, h, _ = b
        t0, t1 = -1e9, 1e9
        for o, d, lo, hi in ((O[0], D[0], x, x + w), (O[1], D[1], y, y + h)):
            if abs(d) < 1e-12:
                continue
            a, c = (lo - o) / d, (hi - o) / d
            if a > c:
                a, c = c, a
            t0, t1 = max(t0, a), min(t1, c)
        return t0 if t0 <= t1 and t1 > 0 else None

    ts = [(slab(b), b) for b in boxes]
    hits = sorted([(t, b) for t, b in ts if t is not None], key=lambda z: z[0])
    assert len(hits) == 2 and hits[0][1][0] == "B1"
    for nm, x, y, w, h, col in boxes:
        root.add("rect", x=x, y=y, width=w, height=h, fill=col, opacity=0.85)
        scene.Text(root, x + w / 2, y + h / 2 + 5, nm, size=16, weight=700, fill="#ffffff", anchor="middle")
    root.add("circle", cx=O[0], cy=O[1], r=8, fill=INK)
    scene.Text(root, O[0], O[1] + 26, "レイの始点", size=12, weight=700, fill=INK, anchor="middle")
    t_first = hits[0][0]
    far = 560.0
    ray = root.add("line", x1=O[0], y1=O[1], x2=O[0], y2=O[1], stroke=RED, stroke_width=3.5)
    ray.Ramp(1.0, 5.0, "x2", O[0] + D[0] * t_first)
    ray.Ramp(1.0, 5.0, "y2", O[1] + D[1] * t_first)
    ghost = root.add("line", x1=O[0] + D[0] * t_first, y1=O[1] + D[1] * t_first, x2=O[0] + D[0] * far, y2=O[1] + D[1] * far, stroke=RED, stroke_width=2, stroke_dasharray="5 5", opacity=0)
    ghost.Show(6.5)
    hx, hy = O[0] + D[0] * t_first, O[1] + D[1] * t_first
    root.add("circle", cx=hx, cy=hy, r=9, fill=AMBER, opacity=0).Show(5.0)
    scene.TextStack(root, 390, 360, [(0.0, 1.0, "始点と向きから、直線を伸ばす"), (1.0, 5.0, "線を伸ばしていく"), (5.0, 6.5, "最初に B1 に当たった。距離 %.0f" % t_first), (6.5, 20, "B2 も線の先にあるが、手前の B1 に遮られる。通常は、最初の 1 つだけ返す")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "線を伸ばす")
    return dict(name=name, page="libs/jolt/queries.md", before=BEFORE, scene=scene, size=(780, 400), times=[2.0, 4.0, 5.5, 9.0])


def CharacterSlide():
    name = "character-slide"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="壁にぶつかったら、速度を壁に沿った成分だけにする(スライド)")
    root = scene.root
    wall_x = 440
    root.add("rect", x=wall_x, y=90, width=22, height=230, fill="#94a3b8")
    scene.Text(root, wall_x + 11, 80, "壁", size=13, weight=700, fill=GRAY, anchor="middle")
    P = (240.0, 240.0)
    v = (3.0, -1.5)
    n = (-1.0, 0.0)
    dot = v[0] * n[0] + v[1] * n[1]
    vt = (v[0] - dot * n[0], v[1] - dot * n[1])
    vn = (dot * n[0], dot * n[1])
    assert vt == (0.0, -1.5) and dot == -3.0
    k = 50
    root.add("circle", cx=P[0], cy=P[1], r=11, fill=INK)
    Arr(scene, root, P[0], P[1], P[0] + v[0] * k, P[1] + v[1] * k, color=RED, width=4, opacity=0).Show(1.0)
    scene.Text(root, P[0] + v[0] * k * 0.5 - 20, P[1] + v[1] * k * 0.5 - 18, "速度 v", size=13, weight=700, fill=RED, anchor="middle", opacity=0).Show(1.0)
    Arr(scene, root, P[0], P[1] + 6, P[0] + v[0] * k, P[1] + 6, color=GRAY, width=3, opacity=0).Show(4.0)
    scene.Text(root, P[0] + 70, P[1] + 34, "壁に向かう成分(捨てる)", size=12, weight=700, fill=GRAY, anchor="middle", opacity=0).Show(4.0)
    Arr(scene, root, P[0] - 6, P[1], P[0] - 6, P[1] + vt[1] * k, color=GREEN, width=4, opacity=0).Show(7.0)
    scene.Text(root, P[0] - 20, P[1] - 40, "壁に沿う成分(残す)", size=12, weight=700, fill=GREEN, anchor="end", opacity=0).Show(7.0)
    scene.TextStack(root, 390, 380, [(0.0, 1.0, "法線 n = (−1, 0) の壁に、v = (3, −1.5) で突っ込む"), (1.0, 4.0, "そのまま進むと、壁にめり込む"), (4.0, 7.0, "壁に向かう成分 (v·n)n を、取り除く"), (7.0, 20, "v − (v·n)n = (0, −1.5)。壁に沿って、滑るように動く")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "分解する")
    return dict(name=name, page="libs/jolt/character.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.5, 5.0, 8.0, 11.0])


def SpringDamping():
    w = 6.0
    zs = [0.05, 0.2, 0.7, 1.0]

    def x(t, z):
        if z < 1.0:
            wd = w * math.sqrt(1 - z * z)
            return math.exp(-z * w * t) * (math.cos(wd * t) + z / math.sqrt(1 - z * z) * math.sin(wd * t))
        return (1 + w * t) * math.exp(-w * t)

    fns = [lambda t, z=z: x(t, z) for z in zs]
    caps = ["減衰 0.05: ほとんど減らない。ずっとぶるぶる揺れる", "減衰 0.2: 数回揺れて落ち着く", "減衰 0.7: 1 回だけ少し行き過ぎて、すっと止まる", "減衰 1.0（臨界）: 行き過ぎずに、最速で止まる"]
    info = Morph("spring-damping", "x.md", "バネ制約の減衰: 小さいと揺れ続け、大きいと止まる(1 → 0 へ戻る動き)", "時間 (秒)", "位置（元の位置 = 0）", 4.0, 1.1, fns, caps, color=BLUE, ticks=[0, 1, 2, 3, 4], ymin=-0.9)
    return Retarget(info, "libs/jolt/constraints.md")


def GltfChain():
    name = "gltf-chain"
    scene = NewScene(name, 780, 440, duration=17.0, hold=1.5, title="glTF は、番号でたどる: シーン → ノード → メッシュ → データの場所")
    root = scene.root
    nodes = [("scene", "scenes[0].nodes = [0]", 70, 110), ("node", "nodes[0].mesh = 0", 280, 110), ("mesh", "meshes[0].primitives[0]", 490, 110), ("accessor", "attributes.POSITION = 2\n(頂点位置・float3 × N)", 490, 250), ("bufferView", "accessors[2].bufferView = 1\n(バイト範囲)", 280, 250), ("buffer", "bufferViews[1].buffer = 0\n(.bin の実体)", 70, 250)]
    for k, (nm, sub, x, y) in enumerate(nodes):
        g = root.add("g", opacity=0)
        g.add("rect", x=x, y=y, width=170, height=60, fill="#ffffff", stroke=[BLUE, GREEN, AMBER, PURPLE, RED, GRAY][k], stroke_width=3)
        scene.Text(g, x + 85, y + 26, nm, size=16, weight=700, fill=INK, anchor="middle")
        scene.Text(g, x + 85, y + 46, sub.split("\n")[0], size=10, weight=500, fill=GRAY, anchor="middle")
        g.Show(1.0 + k * 2.2)
    for k, (ax_, ay, bx, by) in enumerate([(240, 140, 276, 140), (450, 140, 486, 140), (575, 172, 575, 246), (486, 280, 450, 280), (276, 280, 240, 280)]):
        Arr(scene, root, ax_, ay, bx, by, color=RED, width=3, opacity=0).Show(1.0 + (k + 1) * 2.2 - 0.3)
    items = [(0.0, 1.0, "glTF の JSON は、配列の添字(番号)でつながっている")]
    caps = ["シーンは、ルートのノードの番号を持つ", "ノードは、メッシュの番号を持つ", "メッシュは、プリミティブを持つ", "プリミティブの属性(POSITION)が、アクセサの番号を指す", "アクセサは、バッファビューの番号を指す(どのバイト範囲か)", "バッファビューは、バッファ(.bin)の番号を指す。ここに実データがある"]
    for k, c in enumerate(caps):
        items.append((1.0 + k * 2.2, 1.0 + (k + 1) * 2.2 if k < 5 else 99, c))
    scene.TextStack(root, 390, 370, items, size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "番号をたどる")
    return dict(name=name, page="libs/tinygltf/structure.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.5, 5.0, 9.0, 14.0])


def FlameGraph():
    name = "flame-graph"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="フレーム グラフ: 幅 = かかった時間。幅の広い所が、直す候補")
    root = scene.root
    levels = [[("Frame 16.0 ms", 16.0, GRAY)], [("Update 6.0", 6.0, BLUE), ("Render 8.0", 8.0, GREEN), ("待ち 2.0", 2.0, "#cbd5e1")], [("AI 3.5", 3.5, BLUE), ("Physics 2.0", 2.0, BLUE), ("他 0.5", 0.5, BLUE), ("Culling 1.5", 1.5, GREEN), ("Draw 5.0", 5.0, RED), ("UI 1.5", 1.5, GREEN)]]
    assert sum(w for _, w, _ in levels[1]) == 16.0 and sum(w for _, w, _ in levels[2][:3]) == 6.0 and sum(w for _, w, _ in levels[2][3:]) == 8.0
    x0, W = 70, 640
    for lv, row in enumerate(levels):
        y = 290 - lv * 62
        g = root.add("g", opacity=0)
        acc = 0.0
        for nm, w, col in row:
            x = x0 + acc / 16.0 * W
            if lv == 2:
                pass
            g.add("rect", x=x, y=y, width=w / 16.0 * W - 2, height=54, fill=col, opacity=0.9)
            scene.Text(g, x + w / 16.0 * W / 2, y + 32, nm, size=12 if w > 1.8 else 9, weight=700, fill="#ffffff" if col != "#cbd5e1" else INK, anchor="middle")
            acc += w
        g.Show(1.0 + lv * 3.5)
    scene.TextStack(root, 390, 375, [(0.0, 1.0, "1 フレーム(16 ms)の、関数ごとの時間を積み上げる"), (1.0, 4.5, "一番下: フレーム全体"), (4.5, 8.0, "1 段上: Update / Render / 待ち に分ける"), (8.0, 20.0, "さらに内訳。Draw が 5.0 ms で最大 → まずここを調べる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "下から積む")
    return dict(name=name, page="vs/profiler.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 9.0, 12.5])


def AsanRedzone():
    name = "asan-redzone"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="AddressSanitizer: 配列の両側に「立入禁止」の領域を置き、触ったら止める")
    root = scene.root
    cs, ox, y = 70, 150, 150
    for i in range(8):
        zone = i < 1 or i >= 5
        x = ox + i * cs
        col = "#fecaca" if zone else "#dbeafe"
        root.add("rect", x=x, y=y, width=cs - 4, height=60, fill=col, stroke="#94a3b8", stroke_width=1.5)
        if not zone:
            scene.Text(root, x + (cs - 4) / 2, y + 36, "a[%d]" % (i - 1), size=14, weight=700, fill=BLUE, anchor="middle")
        else:
            scene.Text(root, x + (cs - 4) / 2, y + 36, "禁止", size=12, weight=700, fill=RED, anchor="middle")
    scene.Text(root, ox + 3 * cs, y - 14, "int a[4]（4 要素）", size=13, weight=700, fill=BLUE, anchor="middle")
    for k in range(5):
        t0 = 1.0 + k * 1.8
        t1 = t0 + 1.8 if k < 4 else None
        idx = k + 1
        mk = root.add("g", opacity=0)
        mk.add("path", d="M%d,%d l-10,-18 l20,0 z" % (ox + idx * cs + (cs - 4) / 2, y + 70), fill=(GREEN if k < 4 else RED))
        scene.Text(mk, ox + idx * cs + (cs - 4) / 2, y + 112, "a[%d] に書く" % k, size=13, weight=700, fill=(GREEN if k < 4 else RED), anchor="middle")
        mk.Show(t0, t1)
    boom = scene.Text(root, 390, 315, "ERROR: AddressSanitizer: stack-buffer-overflow（a[4] への書き込み）", size=15, weight=700, fill=RED, anchor="middle", opacity=0)
    boom.Show(9.8)
    scene.TextStack(root, 390, 360, [(0.0, 1.0, "配列の前後に、禁止領域(赤)が自動で置かれる"), (1.0, 9.0, "a[0]〜a[3] に書く: 範囲内なので問題なし"), (9.0, 20, "a[4] に書く: 禁止領域に触れた → その場でプログラムを止めて、行番号を表示")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "a[0] → a[4]")
    return dict(name=name, page="vs/asan.md", before=BEFORE, scene=scene, size=(780, 400), times=[2.0, 5.0, 8.0, 11.5])


def AosSoa():
    name = "aos-vs-soa"
    scene = NewScene(name, 780, 460, duration=14.0, hold=1.5, title="x だけ読むとき: 構造体の配列(AoS)は 4 ライン、成分ごとの配列(SoA)は 1 ライン")
    root = scene.root
    cs = 24
    fields = ["x", "y", "z", "hp"]
    ox = 150
    scene.Text(root, 40, 80, "AoS（1 体ずつ x y z hp が並ぶ）", size=14, weight=700, fill=RED)
    for ln in range(4):
        y0 = 95 + ln * 34
        scene.Text(root, ox - 10, y0 + 18, "ライン %d" % (ln + 1), size=11, weight=700, fill=GRAY, anchor="end")
        for i in range(16):
            f = fields[i % 4]
            root.add("rect", x=ox + i * (cs + 2), y=y0, width=cs, height=28, fill=(BLUE if f == "x" else "#e2e8f0"), stroke="#94a3b8", stroke_width=1)
            scene.Text(root, ox + i * (cs + 2) + cs / 2, y0 + 19, f, size=10, weight=700, fill=("#ffffff" if f == "x" else GRAY), anchor="middle")
        ring = root.add("rect", x=ox - 3, y=y0 - 2, width=16 * (cs + 2) + 4, height=32, fill="none", stroke=AMBER, stroke_width=4, opacity=0)
        ring.Show(1.0 + ln * 1.2)
    scene.Text(root, 40, 270, "SoA（x だけ、y だけ…と別の配列）", size=14, weight=700, fill=GREEN)
    scene.Text(root, ox - 10, 288, "ライン 1", size=11, weight=700, fill=GRAY, anchor="end")
    for i in range(16):
        root.add("rect", x=ox + i * (cs + 2), y=270 + 6, width=cs, height=28, fill=BLUE, stroke="#94a3b8", stroke_width=1)
        scene.Text(root, ox + i * (cs + 2) + cs / 2, 270 + 25, "x", size=10, weight=700, fill="#ffffff", anchor="middle")
    ring = root.add("rect", x=ox - 3, y=272, width=16 * (cs + 2) + 4, height=32, fill="none", stroke=AMBER, stroke_width=4, opacity=0)
    ring.Show(7.0)
    assert 16 * 4 * 4 == 256 and 256 // 64 == 4 and 16 * 4 // 64 == 1
    scene.Text(root, 390, 340, "16 体 × 4 成分 × 4 バイト = 256 バイト = 4 ライン。x だけなら 64 バイト = 1 ライン", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.TextStack(root, 390, 390, [(0.0, 1.0, "青 = 読みたい x。1 ライン(橙の枠) = 一度に運ばれる 64 バイト"), (1.0, 6.0, "AoS: 4 ライン運んで、使うのは 4 分の 1(25%)"), (6.0, 20, "SoA: 1 ライン運んで、全部使う(100%)。データ指向が速い理由")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "x を読む")
    return dict(name=name, page="design/patterns/data-oriented.md", before="## 実践のテクニック", scene=scene, size=(780, 460), times=[2.0, 4.5, 7.5, 11.0])


def StateWalk():
    name = "state-transition-walk"
    scene = NewScene(name, 780, 440, duration=17.0, hold=1.5, title="ステートマシン: 入力があったときだけ、決められた先へ移る")
    root = scene.root
    pos = {"待機": (200, 150), "走る": (560, 150), "ジャンプ": (560, 300), "攻撃": (200, 300)}
    trans = {("待機", "右キー"): "走る", ("走る", "ジャンプ"): "ジャンプ", ("ジャンプ", "着地"): "待機", ("待機", "攻撃"): "攻撃", ("攻撃", "終了"): "待機", ("走る", "キー離す"): "待機"}
    events = ["右キー", "ジャンプ", "着地", "攻撃", "終了"]
    cur, path = "待機", []
    for e in events:
        nxt = trans[(cur, e)]
        path.append((cur, e, nxt))
        cur = nxt
    assert path[-1][2] == "待機" and len(path) == 5
    drawn = set()
    for (a, e), b in trans.items():
        ax_, ay = pos[a]
        bx, by = pos[b]
        dx, dy = bx - ax_, by - ay
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        off = 9
        px, py = -uy * off, ux * off
        Arr(scene, root, ax_ + ux * 52 + px, ay + uy * 52 + py, bx - ux * 56 + px, by - uy * 56 + py, color="#cbd5e1", width=2.5)
    for nm, (x, y) in pos.items():
        root.add("circle", cx=x, cy=y, r=46, fill="#ffffff", stroke="#94a3b8", stroke_width=3)
        scene.Text(root, x, y + 5, nm, size=15, weight=700, fill=INK, anchor="middle")
    t = 1.0
    stay = 3.0
    for k, (a, e, b) in enumerate(path):
        t0 = t + k * stay
        # 遷移の赤い線
        ax_, ay = pos[a]
        bx, by = pos[b]
        dx, dy = bx - ax_, by - ay
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        px, py = -uy * 9, ux * 9
        Arr(scene, root, ax_ + ux * 52 + px, ay + uy * 52 + py, bx - ux * 56 + px, by - uy * 56 + py, color=RED, width=4, opacity=0).Show(t0, t0 + stay)
        hi = root.add("circle", cx=bx, cy=by, r=46, fill=AMBER, opacity=0)
        hi.Show(t0 + 0.8, t0 + stay + 0.8 if k < 4 else None)
    hi0 = root.add("circle", cx=pos["待機"][0], cy=pos["待機"][1], r=46, fill=AMBER, opacity=0)
    hi0.Show(0.0 + 0.01, 1.8)
    for nm, (x, y) in pos.items():
        scene.Text(root, x, y + 5, nm, size=15, weight=700, fill=INK, anchor="middle")
    items = [(0.0, 1.0, "最初は「待機」")]
    for k, (a, e, b) in enumerate(path):
        items.append((1.0 + k * stay, 1.0 + (k + 1) * stay if k < 4 else 99, "入力「%s」: %s → %s" % (e, a, b)))
    scene.TextStack(root, 390, 405, items, size=15, fill=INK, anchor="middle")
    scene.Note(1.0, name, "入力を 5 回")
    return dict(name=name, page="design/patterns/state-machine.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.5, 4.5, 7.5, 13.0])


def BindlessIndex():
    name = "bindless-index"
    scene = NewScene(name, 780, 420, duration=14.0, hold=1.5, title="ビンドレス: マテリアルが「テクスチャの番号」を持ち、シェーダーが番号で引く")
    root = scene.root
    objs = [("岩", 2, PURPLE), ("木", 0, GREEN), ("壁", 1, AMBER)]
    for k, (nm, idx, col) in enumerate(objs):
        y = 100 + k * 80
        root.add("rect", x=60, y=y, width=120, height=56, fill="#ffffff", stroke=col, stroke_width=3)
        scene.Text(root, 120, y + 34, "物体: " + nm, size=15, weight=700, fill=INK, anchor="middle")
        g = root.add("g", opacity=0)
        g.add("rect", x=300, y=y, width=150, height=56, fill="#ffffff", stroke=col, stroke_width=3)
        scene.Text(g, 375, y + 34, "textureIndex = %d" % idx, size=14, weight=700, fill=col, anchor="middle")
        g.Show(1.0 + k * 3.4)
        Arr(scene, root, 184, y + 28, 296, y + 28, color=col, width=3, opacity=0).Show(1.0 + k * 3.4)
        Arr(scene, root, 454, y + 28, 596, 100 + idx * 62 + 28, color=col, width=3, opacity=0).Show(2.0 + k * 3.4)
    heap_cols = [GREEN, AMBER, PURPLE, "#cbd5e1"]
    for i in range(4):
        y = 100 + i * 62
        root.add("rect", x=600, y=y, width=130, height=52, fill=heap_cols[i], opacity=0.9)
        scene.Text(root, 665, y + 32, "heap[%d] 画像" % i, size=13, weight=700, fill="#ffffff" if i < 3 else INK, anchor="middle")
    scene.Text(root, 665, 88, "記述子ヒープ(全テクスチャ)", size=12, weight=700, fill=GRAY, anchor="middle")
    scene.TextStack(root, 390, 380, [(0.0, 1.0, "全テクスチャを、1 つの配列(ヒープ)に入れておく"), (1.0, 4.4, "岩: 番号 2 → heap[2]"), (4.4, 7.8, "木: 番号 0 → heap[0]"), (7.8, 20, "壁: 番号 1 → heap[1]。物体ごとのテクスチャ切り替え命令が、要らなくなる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "岩 → 木 → 壁")
    return dict(name=name, page="rendering/gpu-driven-dx12/bindless.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 5.0, 8.5, 12.0])


def AsyncGantt():
    name = "async-compute-gantt"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="非同期コンピュート: 別の列で同時に走らせ、全体の時間を縮める")
    root = scene.root
    px, ox = 50, 130
    serial = [("影", 2, BLUE), ("G-Buffer", 4, GREEN), ("ライティング", 3, AMBER), ("合成", 1, GRAY), ("パーティクル", 2, PURPLE), ("SSAO", 2, RED)]
    assert sum(d for _, d, _ in serial) == 14
    t = 0
    scene.Text(root, 40, 85, "ふつう（1 列で順番に）", size=14, weight=700, fill=RED)
    for k, (nm, d, col) in enumerate(serial):
        g = root.add("g", opacity=0)
        g.add("rect", x=ox - 60 + t * px * 0.8, y=105, width=d * px * 0.8 - 3, height=38, fill=col, opacity=0.9)
        scene.Text(g, ox - 60 + t * px * 0.8 + d * px * 0.4, 129, nm, size=10, weight=700, fill="#ffffff", anchor="middle")
        g.Show(1.0 + k * 0.7)
        t += d
    scene.Text(root, ox - 60 + 14 * px * 0.8, 160, "14 ms", size=13, weight=700, fill=RED, anchor="end", opacity=0).Show(5.5)
    scene.Text(root, 40, 205, "非同期（グラフィックス列 + コンピュート列）", size=14, weight=700, fill=GREEN)
    gfx = [("影", 0, 2, BLUE), ("G-Buffer", 2, 4, GREEN), ("ライティング", 6, 3, AMBER), ("合成", 9, 1, GRAY)]
    cmp_ = [("パーティクル", 0, 2, PURPLE), ("SSAO", 6, 2, RED)]
    assert max(s + d for _, s, d, _ in gfx) == 10
    for k, (nm, s, d, col) in enumerate(gfx):
        g = root.add("g", opacity=0)
        g.add("rect", x=ox - 60 + s * px * 0.8, y=225, width=d * px * 0.8 - 3, height=38, fill=col, opacity=0.9)
        scene.Text(g, ox - 60 + s * px * 0.8 + d * px * 0.4, 249, nm, size=10, weight=700, fill="#ffffff", anchor="middle")
        g.Show(6.5 + k * 0.5)
    for k, (nm, s, d, col) in enumerate(cmp_):
        g = root.add("g", opacity=0)
        g.add("rect", x=ox - 60 + s * px * 0.8, y=272, width=d * px * 0.8 - 3, height=38, fill=col, opacity=0.9)
        scene.Text(g, ox - 60 + s * px * 0.8 + d * px * 0.4, 296, nm, size=10, weight=700, fill="#ffffff", anchor="middle")
        g.Show(8.5 + k * 0.5)
    scene.Text(root, ox - 60 + 10 * px * 0.8, 340, "10 ms", size=13, weight=700, fill=GREEN, anchor="end", opacity=0).Show(10.0)
    scene.Text(root, 40, 252, "GFX", size=11, weight=700, fill=GRAY, anchor="start")
    scene.Text(root, 40, 298, "計算", size=11, weight=700, fill=GRAY, anchor="start")
    scene.Text(root, 390, 385, "パーティクルは影と同時に、SSAO はライティングと同時に走らせる(GPU に空きがあるときだけ得をする)", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "1 列 → 2 列")
    return dict(name=name, page="rendering/async-compute.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.5, 5.5, 8.0, 11.5])


def TrampleFalloff():
    rs = [0.5, 1.0, 1.5, 2.5]

    def sm(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3 - 2 * x)

    fns = [lambda d, r=r: 1 - sm(d / r) for r in rs]
    caps = ["半径 0.5 m: 足元のすぐ近くだけが、倒れる", "半径 1.0 m: 自然な広がり", "半径 1.5 m: 広く倒れる", "半径 2.5 m: 大型の生き物が通った跡のよう"]
    info = Morph("trample-falloff", "x.md", "草が倒れる量: プレイヤーに近いほど強く、半径の外では 0", "プレイヤーからの距離 (m)", "倒れる量（1 = 地面に伏せる）", 3.0, 1.05, fns, caps, color=GREEN, ticks=[0, 0.5, 1, 1.5, 2, 2.5, 3])
    return Retarget(info, "graphics/terrain/vegetation/trample.md")


FIGS = [ImguiFrame, LayerMatrix, RaycastHit, CharacterSlide, SpringDamping, GltfChain, FlameGraph, AsanRedzone, AosSoa, StateWalk, BindlessIndex, AsyncGantt, TrampleFalloff]
