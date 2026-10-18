import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402

BEFORE = "## よくあるミス"


def Arr(scene, parent, x1, y1, x2, y2, color=INK, width=2.5, opacity=1):
    return parent.add("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=width, marker_end=scene.marker, opacity=opacity)


def Box(scene, parent, x, y, w, h, color, fill="#ffffff", sw=2.5):
    return parent.add("rect", x=x, y=y, width=w, height=h, fill=fill, stroke=color, stroke_width=sw)


def Win(scene, parent, x, y, items, size=18, weight=700, anchor="middle"):
    """(t0, t1, 文, 色) の区間ごとに出す文字。t1 が None なら最後まで。"""
    for t0, t1, tx, col in items:
        n = scene.Text(parent, x, y, tx, size=size, weight=weight, fill=col, anchor=anchor, opacity=0)
        if t0 <= 0:
            n.Set(0.0, "opacity", 1)
            if t1 is not None:
                n.Set(t1, "opacity", 0)
        else:
            n.Show(t0, t1)


def PointerDeref():
    name = "pointer-deref"
    scene = NewScene(name, 780, 400, duration=14.0, hold=1.5, title="ポインタ = 住所を入れた変数。*p で、その住所の中身を読み書きする")
    root = scene.root
    Box(scene, root, 100, 140, 150, 80, BLUE)
    scene.Text(root, 175, 130, "int hp（住所 0x100）", size=13, weight=700, fill=BLUE, anchor="middle")
    Win(scene, root, 175, 192, [(0, 8.0, "30", INK), (8.0, None, "50", RED)], size=30)
    g = root.add("g", opacity=0)
    Box(scene, g, 440, 140, 190, 80, GREEN)
    scene.Text(g, 535, 130, "int* p（住所 0x200）", size=13, weight=700, fill=GREEN, anchor="middle")
    scene.Text(g, 535, 190, "0x100", size=26, weight=700, fill=INK, anchor="middle")
    g.Show(3.0)
    Arr(scene, root, 436, 180, 256, 180, color=GREEN, width=3, opacity=0).Show(4.0)
    scene.TextStack(root, 390, 300, [(0.0, 3.0, "int hp = 30;  hp という箱に 30 が入っている"), (3.0, 6.0, "int* p = &hp;  p の箱には、hp の住所 0x100 を入れる"), (6.0, 8.0, "p は hp を「指している」"), (8.0, 20, "*p = 50;  p が指す先(hp)の中身が 50 になる")], size=15, fill=INK, anchor="middle")
    scene.Note(3.0, name, "住所を入れる → 指す先を書き換える")
    return dict(name=name, page="basics/pointer.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.0, 4.5, 7.0, 10.0])


def ReferenceAlias():
    name = "reference-alias"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="値渡しはコピーを直す。参照渡しは、元の変数そのものを直す")
    root = scene.root
    scene.Text(root, 60, 80, "値渡し  void Heal(int x)", size=15, weight=700, fill=RED)
    Box(scene, root, 100, 100, 110, 60, GRAY)
    scene.Text(root, 155, 94, "hp（元）", size=12, weight=700, fill=GRAY, anchor="middle")
    scene.Text(root, 155, 140, "30", size=24, weight=700, fill=INK, anchor="middle")
    g = root.add("g", opacity=0)
    Box(scene, g, 380, 100, 110, 60, RED)
    scene.Text(g, 435, 94, "x（コピー）", size=12, weight=700, fill=RED, anchor="middle")
    g.Show(2.0)
    Win(scene, root, 435, 140, [(2.0, 5.0, "30", INK), (5.0, None, "31", RED)], size=24)
    Arr(scene, root, 214, 130, 376, 130, color=RED, width=2, opacity=0).Show(2.0)
    scene.Text(root, 520, 135, "← 新しい箱に、値を複製", size=12, weight=500, fill=GRAY, opacity=0).Show(2.0)
    scene.Text(root, 60, 235, "参照渡し  void Heal(int& x)", size=15, weight=700, fill=GREEN)
    Box(scene, root, 100, 255, 110, 60, GREEN)
    scene.Text(root, 155, 249, "hp", size=12, weight=700, fill=GRAY, anchor="middle")
    scene.Text(root, 250, 249, "= x（別名）", size=12, weight=700, fill=GREEN, anchor="start", opacity=0).Show(8.0)
    Win(scene, root, 155, 295, [(0, 11.0, "30", INK), (11.0, None, "31", GREEN)], size=24)
    scene.TextStack(root, 390, 380, [(0.0, 2.0, "同じ関数 Heal を、2 通りの渡し方で呼ぶ"), (2.0, 5.0, "値渡し: x は別の箱。元の hp とは無関係"), (5.0, 8.0, "x を 31 にしても、元の hp は 30 のまま"), (8.0, 11.0, "参照渡し: x は hp の別名(同じ箱)"), (11.0, 20, "x を 31 にすると、hp も 31 になる")], size=14, fill=INK, anchor="middle")
    scene.Note(2.0, name, "値渡し → 参照渡し")
    return dict(name=name, page="basics/reference.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 3.0, 6.0, 12.0])


def IteratorInvalid():
    name = "iterator-invalidate"
    scene = NewScene(name, 780, 440, duration=15.0, hold=1.5, title="push_back で領域が引っ越すと、手持ちのイテレータは、解放された場所を指す")
    root = scene.root
    cs = 52
    old = root.add("g", opacity=1)
    for i in range(4):
        old.add("rect", x=100 + i * cs, y=110, width=cs - 4, height=44, fill=(BLUE if i < 3 else "#ffffff"), stroke="#94a3b8", stroke_width=1.5, opacity=0.9)
    for i, v in enumerate([10, 20, 30]):
        scene.Text(old, 100 + i * cs + (cs - 4) / 2, 138, str(v), size=15, weight=700, fill="#ffffff", anchor="middle")
    fill4 = root.add("g", opacity=0)
    fill4.add("rect", x=100 + 3 * cs, y=110, width=cs - 4, height=44, fill=GREEN, opacity=0.9)
    scene.Text(fill4, 100 + 3 * cs + (cs - 4) / 2, 138, "40", size=15, weight=700, fill="#ffffff", anchor="middle")
    fill4.Show(4.0)
    old.Set(0, "opacity", 1)
    old.Set(9.0, "opacity", 0.3)
    fill4.Set(9.0, "opacity", 0.3)
    scene.Text(root, 100, 100, "元の領域（容量 4）", size=12, weight=700, fill=GRAY)
    new = root.add("g", opacity=0)
    for i in range(8):
        new.add("rect", x=100 + i * cs, y=250, width=cs - 4, height=44, fill=(BLUE if i < 5 else "#ffffff"), stroke="#94a3b8", stroke_width=1.5, opacity=0.9)
    for i, v in enumerate([10, 20, 30, 40, 50]):
        scene.Text(new, 100 + i * cs + (cs - 4) / 2, 278, str(v), size=15, weight=700, fill="#ffffff", anchor="middle")
    scene.Text(new, 100, 240, "新しい領域（容量 8）に引っ越した", size=12, weight=700, fill=GREEN)
    new.Show(9.0)
    x_it = 100 + 1 * cs + (cs - 4) / 2
    Arr(scene, root, x_it, 200, x_it, 160, color=RED, width=3)
    scene.Text(root, x_it, 218, "it（20 を指す）", size=12, weight=700, fill=RED, anchor="middle")
    Win(scene, root, 600, 130, [(9.0, None, "解放済み → it は無効", RED)], size=14)
    scene.TextStack(root, 390, 375, [(0.0, 4.0, "it = v.begin() + 1;  要素 20 を指している"), (4.0, 9.0, "push_back(40): 容量に空きがあるので、同じ場所に追加。it は有効"), (9.0, 20, "push_back(50): 容量オーバー → 引っ越し。古い領域は解放され、it は壊れる")], size=14, fill=INK, anchor="middle")
    scene.Note(4.0, name, "追加 → 引っ越し")
    return dict(name=name, page="basics/iterator.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 8.5, 12.0])


def RaceCounter():
    name = "data-race-counter"
    scene = NewScene(name, 780, 460, duration=15.0, hold=1.5, title="2 つのスレッドが、同じカウンターを +1 する: ロックなしで 1 になる")
    root = scene.root
    ev = [("A", "読む(0)", 1.0, 0), ("B", "読む(0)", 2.5, 1), ("A", "書く(1)", 4.0, 2), ("B", "書く(1)", 5.5, 3)]
    scene.Text(root, 60, 85, "ロックなし", size=15, weight=700, fill=RED)
    for lane, ly in (("A", 120), ("B", 175)):
        root.add("line", x1=110, y1=ly + 18, x2=720, y2=ly + 18, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, 100, ly + 24, "スレッド " + lane, size=12, weight=700, fill=GRAY, anchor="end")
    vals = [0, 0, 1, 1]
    for lane, lab, t, k in ev:
        ly = 120 if lane == "A" else 175
        x = 140 + k * 140
        g = root.add("g", opacity=0)
        g.add("rect", x=x, y=ly, width=120, height=36, fill=(BLUE if lane == "A" else GREEN), opacity=0.9)
        scene.Text(g, x + 60, ly + 24, lab, size=13, weight=700, fill="#ffffff", anchor="middle")
        g.Show(t)
    Win(scene, root, 390, 255, [(0, 1.0, "共有カウンター = 0", INK), (1.0, 4.0, "共有カウンター = 0", INK), (4.0, 5.5, "共有カウンター = 1", INK), (5.5, 8.0, "共有カウンター = 1  ← 2 回足したのに 1", RED)], size=16)
    scene.Text(root, 60, 305, "std::mutex でロックあり", size=15, weight=700, fill=GREEN)
    ev2 = [("A", "ロック+読む+書く", 8.5, 0, 2), ("B", "待つ", 8.5, 0, 2), ("B", "ロック+読む+書く", 11.0, 2, 2)]
    for lane, ly in (("A", 335), ("B", 385)):
        root.add("line", x1=110, y1=ly + 18, x2=720, y2=ly + 18, stroke=LIGHT, stroke_width=1.5)
        scene.Text(root, 100, ly + 24, "スレッド " + lane, size=12, weight=700, fill=GRAY, anchor="end")
    for lane, lab, t, k, w in ev2:
        ly = 335 if lane == "A" else 385
        x = 140 + k * 140
        g = root.add("g", opacity=0)
        col = BLUE if lane == "A" else (GRAY if lab == "待つ" else GREEN)
        g.add("rect", x=x, y=ly, width=w * 130, height=36, fill=col, opacity=0.9)
        scene.Text(g, x + w * 65, ly + 24, lab, size=13, weight=700, fill="#ffffff", anchor="middle")
        g.Show(t)
    Win(scene, root, 390, 450, [(12.5, None, "共有カウンター = 2（正しい）", GREEN)], size=15)
    scene.Note(1.0, name, "ロックなし → ロックあり")
    return dict(name=name, page="basics/concurrency.md", before=BEFORE, scene=scene, size=(780, 460), times=[1.5, 3.0, 6.5, 13.0])


def BranchPredict():
    name = "branch-predict"
    scene = NewScene(name, 780, 440, duration=16.0, hold=1.5, title="分岐予測: 結果が揃っていると当たり、バラバラだと外れる")
    root = scene.root
    seed = 12345
    rnd = []
    for _ in range(24):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        rnd.append((seed >> 16) % 2 == 0)
    srt = sorted(rnd, reverse=True)

    def miss(seq):
        res, pred = [], True
        for v in seq:
            res.append(pred != v)
            pred = v
        return res

    mr, ms = miss(rnd), miss(srt)
    assert sum(ms) <= 2 and sum(mr) > sum(ms) + 4
    cs = 26
    step = 0.4
    for row, (seq, ms_, lab, y0) in enumerate([(rnd, mr, "並べ替えなし（バラバラ）", 100), (srt, ms, "並べ替えあり（true が先に固まる）", 260)]):
        scene.Text(root, 70, y0 - 12, lab, size=14, weight=700, fill=INK)
        for i, v in enumerate(seq):
            x = 70 + i * (cs + 3)
            root.add("rect", x=x, y=y0, width=cs, height=cs, fill=(BLUE if v else "#e2e8f0"), stroke="#94a3b8", stroke_width=1)
            if ms_[i]:
                ring = root.add("rect", x=x - 2, y=y0 - 2, width=cs + 4, height=cs + 4, fill="none", stroke=RED, stroke_width=3, opacity=0)
                ring.Set(1.0 + i * step, "opacity", 1)
        cnt = [(1.0 + i * step, sum(ms_[:i + 1])) for i in range(24)]
        scene.Counter(root, 70, y0 + 66, cnt, size=24, fill=RED)
        scene.Text(root, 108, y0 + 66, "回、予測を外した（赤い枠）", size=13, weight=500, fill=GRAY)
    scene.Text(root, 70, 400, "予測のルール: 「前回と同じ結果」になると決め打ち。青 = true、灰 = false", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "24 回の分岐")
    return dict(name=name, page="optimize/branching-virtual.md", before=BEFORE, scene=scene, size=(780, 440), times=[3.0, 6.0, 9.0, 12.0])


def ArenaBump():
    name = "arena-bump"
    scene = NewScene(name, 780, 400, duration=14.0, hold=1.5, title="フレーム アロケータ: ポインタを進めるだけで確保し、フレーム末に巻き戻す")
    root = scene.root
    unit, ox, oy = 40, 70, 150
    total = 16
    sizes = [("A", 2, BLUE), ("B", 4, GREEN), ("C", 1, AMBER), ("D", 3, PURPLE)]
    assert sum(s for _, s, _ in sizes) == 10
    for i in range(total):
        root.add("rect", x=ox + i * unit, y=oy, width=unit - 2, height=44, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    off = 0
    marker_x = root.add("rect", x=ox - 3, y=oy - 22, width=6, height=18, fill=RED)
    for k, (nm, sz, col) in enumerate(sizes):
        t = 1.5 + k * 2.3
        g = root.add("g", opacity=0)
        g.add("rect", x=ox + off * unit, y=oy, width=sz * unit - 2, height=44, fill=col, opacity=0.9)
        scene.Text(g, ox + off * unit + sz * unit / 2, oy + 28, "%s (%d)" % (nm, sz), size=14, weight=700, fill="#ffffff", anchor="middle")
        g.Show(t, 11.0)
        marker_x.Ramp(t - 0.6, t, "x", ox + (off + sz) * unit - 3)
        off += sz
    marker_x.Ramp(11.0, 11.8, "x", ox - 3)
    scene.Text(root, ox, oy - 34, "先頭からの使用量(赤い印 = 次に確保する位置)", size=12, weight=500, fill=GRAY)
    scene.TextStack(root, 390, 290, [(0.0, 1.5, "最初に大きな領域を 1 つ確保しておく(16 マス)"), (1.5, 3.8, "A を確保: 印を 2 マス進めるだけ"), (3.8, 6.1, "B を確保: 4 マス進める"), (6.1, 8.4, "C, D も同様。確保 1 回につき、足し算 1 回だけ"), (8.4, 11.0, "合計 10 マス使用"), (11.0, 20, "フレーム末: 印を先頭に戻す。解放は 1 回だけで、個別の free は不要")], size=14, fill=INK, anchor="middle")
    scene.Note(1.5, name, "A → D → リセット")
    return dict(name=name, page="optimize/frame-allocation.md", before=BEFORE, scene=scene, size=(780, 400), times=[2.0, 5.0, 9.0, 12.5])


def HashBuckets():
    name = "hash-buckets"

    def fnv(s):
        h = 2166136261
        for b in s.encode():
            h ^= b
            h = (h * 16777619) & 0xFFFFFFFF
        return h

    keys = ["hp", "mp", "atk", "def", "spd", "luk", "exp", "gold"]
    nb = 8
    bk = [[] for _ in range(nb)]
    placed = []
    for k in keys:
        b = fnv(k) % nb
        placed.append((k, b, len(bk[b])))
        bk[b].append(k)
    coll = sum(1 for _, _, d in placed if d > 0)
    scene = NewScene(name, 780, 460, duration=1.5 + 1.5 * len(keys) + 3.5, hold=1.5, title="ハッシュ表: キーを数値に変え、その番号のバケツへ入れる(衝突は同じバケツに並ぶ)")
    root = scene.root
    for b in range(nb):
        y = 90 + b * 38
        scene.Text(root, 110, y + 22, "バケツ %d" % b, size=12, weight=700, fill=GRAY, anchor="end")
        root.add("rect", x=120, y=y, width=60, height=30, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
    for i, (k, b, d) in enumerate(placed):
        t = 1.5 + i * 1.5
        g = root.add("g", opacity=0)
        x = 190 + d * 100
        g.add("rect", x=x, y=90 + b * 38, width=90, height=30, fill=(RED if d else BLUE), opacity=0.9)
        scene.Text(g, x + 45, 90 + b * 38 + 21, k, size=13, weight=700, fill="#ffffff", anchor="middle")
        g.Show(t)
    items = [(0.0, 1.5, "キーを FNV-1a でハッシュ → 8 で割った余りがバケツ番号")]
    for i, (k, b, d) in enumerate(placed):
        items.append((1.5 + i * 1.5, 1.5 + (i + 1) * 1.5, "\"%s\" → バケツ %d%s" % (k, b, "（先客あり: 衝突。同じバケツに連ねる）" if d else "")))
    items.append((1.5 + 1.5 * len(keys), 99, "8 個を入れて、衝突が %d 回。多いと検索が遅くなる" % coll))
    scene.TextStack(root, 600, 250, items, size=13, fill=INK, anchor="middle")
    scene.Note(1.5, name, "キーを 1 つずつ入れる")
    return dict(name=name, page="optimize/strings-hash.md", before=BEFORE, scene=scene, size=(780, 460), times=[2.5, 5.5, 9.0, 14.0])


def LoadGantt():
    name = "load-gantt"
    scene = NewScene(name, 780, 400, duration=13.0, hold=1.5, title="ロード時間: 順番に待つと 10 秒、並べて進めると 5 秒")
    root = scene.root
    px, ox = 62, 130
    tasks_serial = [("テクスチャ", 0, 3, BLUE), ("メッシュ", 3, 2, GREEN), ("デコード", 5, 2, PURPLE), ("シェーダー", 7, 3, AMBER)]
    tasks_par = [("テクスチャ", 0, 0, 3, BLUE), ("メッシュ", 1, 0, 2, GREEN), ("シェーダー", 2, 0, 3, AMBER), ("デコード", 1, 3, 2, PURPLE)]
    assert max(s + d for _, s, d, _ in tasks_serial) == 10 and max(s + d for _, _, s, d, _ in tasks_par) == 5
    scene.Text(root, 40, 85, "順番に実行（1 本のスレッド）", size=14, weight=700, fill=RED)
    for k, (nm, s, d, col) in enumerate(tasks_serial):
        g = root.add("g", opacity=0)
        g.add("rect", x=ox + s * px - 60, y=105, width=d * px - 3, height=38, fill=col, opacity=0.9)
        scene.Text(g, ox + s * px - 60 + d * px / 2, 130, "%s %ds" % (nm, d), size=12, weight=700, fill="#ffffff", anchor="middle")
        g.Show(1.0 + k * 1.2)
    scene.Text(root, 40, 205, "並べて実行（3 本のスレッド）", size=14, weight=700, fill=GREEN)
    for k, (nm, lane, s, d, col) in enumerate(tasks_par):
        g = root.add("g", opacity=0)
        g.add("rect", x=ox + s * px - 60, y=225 + lane * 44, width=d * px - 3, height=38, fill=col, opacity=0.9)
        scene.Text(g, ox + s * px - 60 + d * px / 2, 250 + lane * 44, "%s %ds" % (nm, d), size=12, weight=700, fill="#ffffff", anchor="middle")
        g.Show(6.5 + k * 0.4)
    scene.Text(root, ox - 60 + 10 * px, 160, "10 秒", size=14, weight=700, fill=RED, anchor="end", opacity=0).Show(5.5)
    scene.Text(root, ox - 60 + 5 * px, 360, "5 秒", size=14, weight=700, fill=GREEN, anchor="end", opacity=0).Show(9.0)
    scene.Text(root, 390, 385, "デコードは、テクスチャとメッシュが終わってから始める(依存関係)。シェーダーは独立", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "順番 → 並列")
    return dict(name=name, page="optimize/loading.md", before=BEFORE, scene=scene, size=(780, 400), times=[2.5, 5.5, 8.0, 11.0])


def AmdahlBars():
    name = "amdahl-bars"
    scene = NewScene(name, 780, 400, duration=12.0, hold=1.5, title="全体の 50% を占める所を 2 倍速くするほうが、30% の所より効く")
    root = scene.root
    base = [("A", 50, BLUE), ("B", 30, GREEN), ("C", 20, AMBER)]
    s1 = [50, 15, 20]
    s2 = [25, 30, 20]
    assert sum(s1) == 85 and sum(s2) == 75
    rows = [("今の状態（100）", [50, 30, 20], 100, 0), ("B を 2 倍速く → %d" % sum(s1), s1, 130, 3.0), ("A を 2 倍速く → %d" % sum(s2), s2, 220, 6.5)]
    scale = 5.4
    for lab, vals, y, t in rows:
        g = root.add("g", opacity=(1 if t == 0 else 0))
        scene.Text(g, 70, y - 8, lab, size=14, weight=700, fill=INK)
        x = 70
        for (nm, _, col), v in zip(base, vals):
            g.add("rect", x=x, y=y, width=v * scale, height=44, fill=col, opacity=0.9)
            scene.Text(g, x + v * scale / 2, y + 28, "%s %d" % (nm, v), size=13, weight=700, fill="#ffffff", anchor="middle")
            x += v * scale
        if t:
            g.Show(t)
    scene.TextStack(root, 390, 340, [(0.0, 3.0, "A 50、B 30、C 20(合計 100)の処理がある"), (3.0, 6.5, "B を半分にしても、全体は 85。15 しか減らない"), (6.5, 20, "A を半分にすると、全体は 75。25 減る → 重い所から直す")], size=14, fill=INK, anchor="middle")
    scene.Note(3.0, name, "B を直す → A を直す")
    return dict(name=name, page="optimize/measure.md", before=BEFORE, scene=scene, size=(780, 400), times=[1.0, 4.0, 8.0, 11.0])


def StateSort():
    name = "state-sort"
    scene = NewScene(name, 780, 420, duration=14.0, hold=1.5, title="マテリアルでソートすると、状態の切り替え回数が減る")
    root = scene.root
    seq = list("ABACBCABC")
    srt = sorted(seq)
    colmap = {"A": BLUE, "B": GREEN, "C": AMBER}

    def changes(s):
        return [i for i in range(1, len(s)) if s[i] != s[i - 1]]

    cu, cs_ = changes(seq), changes(srt)
    assert len(cu) == 8 and len(cs_) == 2
    cw, step = 56, 0.45
    for row, (s, ch, lab, y0) in enumerate([(seq, cu, "描く順（ソートなし）", 100), (srt, cs_, "マテリアルで並べ替えた順", 250)]):
        scene.Text(root, 70, y0 - 12, lab, size=14, weight=700, fill=INK)
        for i, m in enumerate(s):
            x = 70 + i * (cw + 6)
            root.add("rect", x=x, y=y0, width=cw, height=cw, fill=colmap[m], opacity=0.9)
            scene.Text(root, x + cw / 2, y0 + cw / 2 + 5, m, size=18, weight=700, fill="#ffffff", anchor="middle")
            if i in ch:
                mk = root.add("rect", x=x - 5, y=y0 - 2, width=4, height=cw + 4, fill=RED, opacity=0)
                mk.Set(1.0 + i * step, "opacity", 1)
        cnt = [(1.0 + i * step, sum(1 for c in ch if c <= i)) for i in range(len(s))]
        scene.Counter(root, 70, y0 + cw + 38, cnt, size=24, fill=RED)
        scene.Text(root, 98, y0 + cw + 38, "回、マテリアルを切り替えた（赤い線）", size=13, weight=500, fill=GRAY)
    scene.Note(1.0, name, "9 個の描画")
    return dict(name=name, page="rendering/draw-calls.md", before=BEFORE, scene=scene, size=(780, 420), times=[3.0, 5.0, 8.0, 11.0])


def MipMemory():
    name = "mip-memory"
    scene = NewScene(name, 780, 440, duration=14.0, hold=1.5, title="ミップを使うと、小さく表示される時、小さな絵だけ読める(全体は +33%)")
    root = scene.root
    sizes = [(1024 >> l) ** 2 * 4 for l in range(6)]
    assert sizes[0] == 4 * 1024 * 1024 and sizes[1] * 4 == sizes[0]
    total = sum(sizes)
    assert abs(total / sizes[0] - 4 / 3) < 0.01
    ox, oy, maxw = 250, 90, 400
    acc = 0
    for l, sz in enumerate(sizes):
        w = max(3.0, sz / sizes[0] * maxw)
        y = oy + l * 48
        t = 1.0 + l * 1.5
        scene.Text(root, ox - 12, y + 24, "ミップ %d（%d×%d）" % (l, 1024 >> l, 1024 >> l), size=12, weight=700, fill=GRAY, anchor="end")
        r = root.add("rect", x=ox, y=y, width=w, height=34, fill=[BLUE, GREEN, AMBER, PURPLE, RED, GRAY][l], opacity=0)
        r.Show(t)
        scene.Text(root, ox + w + 10, y + 23, ("%.2f MB" % (sz / 1024 / 1024) if sz >= 100 * 1024 else "%d KB" % (sz // 1024)), size=12, weight=500, fill=GRAY, anchor="start", opacity=0).Show(t)
        acc += sz
    scene.TextStack(root, 390, 400, [(0.0, 1.0, "1024×1024 の画像（1 画素 4 バイト）"), (1.0, 3.0, "ミップ 0: 4 MB"), (3.0, 9.5, "1 段下がるごとに、縦横が半分 → 容量は 1/4"), (9.5, 20, "全部足しても約 %.2f MB（元の 4/3 倍）。遠い物は、小さい層だけ読めばよい" % (total / 1024 / 1024))], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "ミップ 0 → 5")
    return dict(name=name, page="rendering/texture-streaming.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 4.5, 8.0, 12.0])


def UvSampling():
    name = "uv-sampling"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="UV 座標から、テクスチャの画素(テクセル)を選ぶ")
    root = scene.root
    n, ts = 8, 40
    ox, oy = 230, 90
    for r in range(n):
        for c in range(n):
            v = ((c * 3 + r * 5) % 8) / 8
            root.add("rect", x=ox + c * ts, y=oy + r * ts, width=ts, height=ts, fill=Mix("#dbeafe", "#1e40af", v), stroke="#ffffff", stroke_width=1)
    scene.Text(root, ox, oy - 10, "8×8 のテクスチャ。UV は (0,0) が左上、(1,1) が右下", size=12, weight=500, fill=GRAY)
    pts = [(0.30, 0.70), (0.55, 0.20), (0.93, 0.93)]
    items = []
    for k, (u, v) in enumerate(pts):
        c, r = min(n - 1, int(u * n)), min(n - 1, int(v * n))
        t0 = 1.0 + k * 3.8
        t1 = 1.0 + (k + 1) * 3.8 if k < 2 else None
        hi = root.add("rect", x=ox + c * ts, y=oy + r * ts, width=ts, height=ts, fill="none", stroke=AMBER, stroke_width=5, opacity=0)
        hi.Show(t0, t1)
        d = root.add("circle", cx=ox + u * n * ts, cy=oy + v * n * ts, r=7, fill=RED, opacity=0)
        d.Show(t0, t1)
        items.append((t0, t1 if t1 else 99, "UV (%.2f, %.2f) × 8 = (%.2f, %.2f) → テクセル (%d, %d)" % (u, v, u * n, v * n, c, r)))
    assert [(int(u * n), int(v * n)) for u, v in pts] == [(2, 5), (4, 1), (7, 7)]
    scene.TextStack(root, 390, 430, [(0.0, 1.0, "三角形の内側の点には、UV が補間されて届く")] + items, size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "UV を 3 つ調べる")
    return dict(name=name, page="3d/mesh-textures.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.5, 9.0, 12.0])


def LambertCurves():
    name = "lambert-curves"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="光の当たり方: 面と光の角度で、明るさが変わる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 180.0, 1.05, ylabel="明るさ")
    scene.Text(root, 710, 346, "光の向きと法線の角度 (度)", size=12, weight=500, fill=GRAY, anchor="end")
    for v in (0, 45, 90, 135, 180):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    lam = lambda a: max(0.0, math.cos(math.radians(a)))
    half = lambda a: (0.5 * math.cos(math.radians(a)) + 0.5) ** 2
    ax.Curve(lam, RED, width=4, n=120)
    ax.Curve(half, BLUE, width=4, n=120)
    scene.Text(root, ax.X(14), ax.Y(0.32), "赤: ランバート max(0, N·L)", size=13, weight=700, fill=RED)
    scene.Text(root, ax.X(14), ax.Y(0.18), "青: ハーフランバート", size=13, weight=700, fill=BLUE)
    d1 = root.add("circle", cx=ax.X(0), cy=ax.Y(1), r=7, fill=RED)
    d2 = root.add("circle", cx=ax.X(0), cy=ax.Y(1), r=7, fill=BLUE)
    Sweep(d1, ax, lam, 1.0, 11.0, 0.0, 180.0, n=72)
    Sweep(d2, ax, half, 1.0, 11.0, 0.0, 180.0, n=72)
    assert abs(half(90) - 0.25) < 1e-12 and lam(90) < 1e-12
    LiveText(scene, root, 390, 392, 1.0, 11.0, 4, lambda i, f: ["0 度（真正面から当たる）: どちらも最大 1", "45 度: ランバート 0.71、ハーフランバート 0.73", "90 度（真横）: ランバートは 0、ハーフは 0.25 でまだ見える", "90 度を超える（裏側）: ランバートは真っ黒のまま"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "角度 0 → 180")
    return dict(name=name, page="3d/lighting-normals.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.5, 9.5])


def EncodingSizes():
    name = "encoding-sizes"
    scene = NewScene(name, 780, 420, duration=12.0, hold=1.5, title="同じ 1 文字でも、文字コードで必要なバイト数が違う")
    root = scene.root
    chars = [("A", "半角英字"), ("あ", "ひらがな"), ("😀", "絵文字")]
    encs = [("UTF-8", "utf-8", BLUE), ("UTF-16", "utf-16-le", GREEN), ("UTF-32", "utf-32-le", AMBER)]
    got = {c: [len(c.encode(e)) for _, e, _ in encs] for c, _ in chars}
    assert got["A"] == [1, 2, 4] and got["あ"] == [3, 2, 4] and got["😀"] == [4, 4, 4]
    for k, (c, lab) in enumerate(chars):
        y0 = 90 + k * 95
        g = root.add("g", opacity=0)
        scene.Text(g, 70, y0 + 40, "%s  %s" % (c, lab), size=16, weight=700, fill=INK)
        for j, (en, _, col) in enumerate(encs):
            n = got[c][j]
            y = y0 + j * 28
            for b in range(n):
                g.add("rect", x=250 + b * 52, y=y, width=48, height=22, fill=col, opacity=0.9)
            scene.Text(g, 250 + n * 52 + 8, y + 17, "%s: %d バイト" % (en, n), size=12, weight=700, fill=col, anchor="start")
        g.Show(1.0 + k * 3.2)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "1 バイト = 1 つの四角"), (1.0, 4.2, "英字: UTF-8 が最小(1 バイト)"), (4.2, 7.4, "日本語: UTF-8 は 3 バイト、UTF-16 は 2 バイト"), (7.4, 20, "絵文字: どれも 4 バイト(UTF-16 では 2 つで 1 文字)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "A → あ → 絵文字")
    return dict(name=name, page="encoding/string-types.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 5.0, 8.0, 11.0])


FIGS = [PointerDeref, ReferenceAlias, IteratorInvalid, RaceCounter, BranchPredict, ArenaBump, HashBuckets, LoadGantt, AmdahlBars, StateSort, MipMemory, UvSampling, LambertCurves, EncodingSizes]
