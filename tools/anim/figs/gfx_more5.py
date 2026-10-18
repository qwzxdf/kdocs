import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Axes, Hex, Lerp, LiveText, Mix, NewScene, R, RampFill, Sweep)  # noqa: E402
from gfx_more4 import Morph, XLabel  # noqa: E402

BEFORE = "## よくあるミス"


def Retarget(info, page):
    info["page"] = page
    return info


def FloatSpacing():
    name = "float-spacing"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="float は、値が大きいほど、隣り合う数の間隔が広がる")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 24.0, 2.0, ylabel="隣の値までの間隔 (2 の何乗か)", ymin=-23.0)
    XLabel(scene, ax, "値の大きさ (2 の何乗か)")
    for v in (0, 4, 8, 12, 16, 20, 24):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "2^%d" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda x: math.floor(x) - 23
    ax.Curve(fn, RED, width=4, n=240)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(fn(0)), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 11.0, 0.0, 24.0, n=96)
    sp = lambda v: 2.0 ** (math.floor(math.log2(v)) - 23)
    assert abs(sp(1.0) - 2 ** -23) < 1e-30 and sp(2 ** 24) == 2.0 and abs(sp(1000) - 2 ** -14) < 1e-30
    LiveText(scene, root, 390, 395, 1.0, 11.0, 4, lambda i, f: ["値 1 付近: 間隔 約 0.0000001（1.2e-7）", "値 1,000 付近: 間隔 約 0.00006（6.1e-5）", "値 100,000 付近: 間隔 約 0.008", "値 16,777,216 (2^24): 間隔 2 → 1 を足しても変わらない"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "値を 1 → 2^24")
    return dict(name=name, page="gamemath/numeric.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 4.0, 7.0, 10.5])


def SrgbGamma():
    name = "srgb-gamma"
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="リニアの明るさを画面に出すとき、暗い所に多くの階調を割り当てる(ガンマ)")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 1.0, 1.0, ylabel="表示用の値 (sRGB、近似 x^(1/2.2))")
    XLabel(scene, ax, "リニアの明るさ")
    for v in (0, 0.25, 0.5, 0.75, 1):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "%g" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    fn = lambda x: x ** (1 / 2.2)
    ax.Curve(lambda x: x, GRAY, width=3, dash="6 5")
    ax.Curve(fn, BLUE, width=4, n=100)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 10.0, 0.0, 1.0, n=60)
    assert abs(fn(0.5) - 0.73) < 0.005 and abs(fn(0.2) - 0.48) < 0.005
    LiveText(scene, root, 390, 392, 1.0, 10.0, 4, lambda i, f: ["リニア 0.05: 表示では約 0.26。暗部が持ち上がる", "リニア 0.2: 表示では約 0.48", "リニア 0.5（中間の明るさ）: 表示では約 0.73", "リニア 1: 表示でも 1"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "リニア 0 → 1")
    return dict(name=name, page="gamemath/color.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def NlerpSlerp():
    name = "nlerp-vs-slerp"
    phi = math.radians(150)
    scene = NewScene(name, 780, 420, duration=11.0, hold=1.5, title="2 つの向きの間を補間: lerp は途中が速く、slerp は一定の速さ（150 度離れた場合）")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 240, 1.0, 150.0, ylabel="回った角度 (度)")
    XLabel(scene, ax, "補間の t")
    for v in (0, 0.25, 0.5, 0.75, 1):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, "%g" % v, size=11, weight=500, fill=GRAY, anchor="middle")
    nl = lambda t: math.degrees(math.atan2(t * math.sin(phi), (1 - t) + t * math.cos(phi)))
    sl = lambda t: 150.0 * t
    ax.Curve(sl, GREEN, width=4, n=60)
    ax.Curve(nl, RED, width=4, n=100)
    scene.Text(root, ax.X(0.78), ax.Y(sl(0.78)) + 22, "slerp（一定）", size=13, weight=700, fill=GREEN)
    scene.Text(root, ax.X(0.05), ax.Y(nl(0.05)) - 24, "lerp + 正規化", size=13, weight=700, fill=RED)
    d1 = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=GREEN)
    d2 = root.add("circle", cx=ax.X(0), cy=ax.Y(0), r=7, fill=RED)
    Sweep(d1, ax, sl, 1.0, 10.0, 0.0, 1.0, n=50)
    Sweep(d2, ax, nl, 1.0, 10.0, 0.0, 1.0, n=50)
    assert abs(nl(0.5) - 75.0) < 1e-6 and nl(0.1) < 15.0 + 1e-9
    LiveText(scene, root, 390, 392, 1.0, 10.0, 3, lambda i, f: ["t が小さいうち: lerp は slerp より遅れる(0.1 で 約 %d 度)" % round(nl(0.1)), "t = 0.5 付近: lerp が急に回る(中央付近が速い)", "t = 1: 両方とも 150 度。経路は同じで、速さだけ違う"][i], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "t を 0 → 1")
    return dict(name=name, page="gamemath/rotation.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.0, 3.5, 6.0, 9.0])


def LevelCurve():
    ps = [1.0, 1.5, 2.0, 3.0]
    fns = [lambda x, p=p: (x / 50.0) ** p for p in ps]
    caps = ["指数 1.0（直線）: レベルごとに、同じだけ増える", "指数 1.5: 後半が、少しずつきつくなる", "指数 2.0: 2 乗。多くのゲームの基本形", "指数 3.0: 終盤が急。やり込み向け(序盤が、ほぼ 0 に見える)"]
    info = Morph("level-curve", "x.md", "必要な経験値のカーブ: 指数が大きいほど、終盤が重くなる", "レベル", "必要な経験値（最大を 1 に正規化）", 50.0, 1.05, fns, caps, color=PURPLE, ticks=[0, 10, 20, 30, 40, 50])
    return Retarget(info, "gamemath/balance.md")


def BigO():
    name = "big-o-curves"
    scene = NewScene(name, 780, 440, duration=13.0, hold=1.5, title="データが増えたとき、かかる時間が、どう増えるか")
    root = scene.root
    ax = Axes(scene, root, 70, 70, 640, 250, 20.0, 100.0, ylabel="操作の回数")
    XLabel(scene, ax, "データの数 n")
    for v in (0, 5, 10, 15, 20):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")
    curves = [("O(1)", lambda n: 1.0, GREEN), ("O(log n)", lambda n: math.log2(max(n, 1.0)) * 2, BLUE), ("O(n)", lambda n: 4.0 * n, AMBER), ("O(n log n)", lambda n: 4.0 * n * math.log2(max(n, 1.0)) / 4, PURPLE), ("O(n²)", lambda n: n * n / 4.0, RED)]
    for k, (lab, fn, col) in enumerate(curves):
        c = ax.Curve(fn, col, width=4, n=100, x0=1.0, opacity=0)
        c.Show(1.0 + k * 2.2)
        lx = {2: 15.5, 3: 12.5}.get(k, 19.0)
        scene.Text(root, ax.X(lx) - 6, ax.Y(min(fn(lx), 96)) - 8, lab, size=12, weight=700, fill=col, anchor="end", opacity=0).Show(1.0 + k * 2.2)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "n が増えたとき、操作の回数が、どう増えるか"), (1.0, 3.2, "O(1): 増えない（配列の添字アクセス）"), (3.2, 5.4, "O(log n): ほぼ増えない（二分探索）"), (5.4, 7.6, "O(n): 比例（線形探索）"), (7.6, 9.8, "O(n log n): 少し急（ソート）"), (9.8, 20, "O(n²): 急激に増える（二重ループ）。n が大きいとゲームが止まる")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "計算量を順に重ねる")
    return dict(name=name, page="basics/big-o.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 4.5, 7.0, 12.0])


def CacheStride():
    name = "cache-stride"
    scene = NewScene(name, 780, 460, duration=14.0, hold=1.5, title="同じ 16 個を読む: 順番に読むと速く、とびとびに読むと遅い")
    root = scene.root
    line = 4
    cap = 2

    def Simulate(seq):
        cache, res = [], []
        for a in seq:
            ln = a // line
            if ln in cache:
                cache.remove(ln)
                cache.append(ln)
                res.append(True)
            else:
                res.append(False)
                cache.append(ln)
                if len(cache) > cap:
                    cache.pop(0)
        return res

    seqA = list(range(16))
    seqB = [(i % 4) * 4 + i // 4 for i in range(16)]
    ra, rb = Simulate(seqA), Simulate(seqB)
    missA, missB = ra.count(False), rb.count(False)
    assert (missA, missB) == (4, 16)
    cs = 38
    step = 0.42
    for row, (seq, res, lab, y0, miss) in enumerate([(seqA, ra, "順番に読む（0, 1, 2, 3, ...）", 100, missA), (seqB, rb, "4 つ飛ばしで読む（0, 4, 8, 12, 1, 5, ...）", 250, missB)]):
        scene.Text(root, 70, y0 - 14, lab, size=14, weight=700, fill=INK)
        for i in range(16):
            x = 70 + i * (cs + 3) + (i // line) * 14
            root.add("rect", x=x, y=y0, width=cs, height=cs, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
            scene.Text(root, x + cs / 2, y0 + cs / 2 + 5, str(i), size=12, weight=500, fill=GRAY, anchor="middle")
        for k, a in enumerate(seq):
            x = 70 + a * (cs + 3) + (a // line) * 14
            ov = root.add("rect", x=x, y=y0, width=cs, height=cs, fill=(GREEN if res[k] else RED), opacity=0)
            ov.Set(1.0 + k * step, "opacity", 0.8)
        cnt = [(1.0 + k * step, sum(1 for r in res[:k + 1] if not r)) for k in range(16)]
        scene.Counter(root, 70, y0 + 80, cnt, size=22, fill=RED)
        scene.Text(root, 110, y0 + 80, "回、キャッシュ ミス（赤）。緑 = ヒット", size=13, weight=500, fill=GRAY)
    scene.Text(root, 70, 410, "4 個ずつが 1 つのキャッシュ ライン（隙間で区切り）。キャッシュは 2 ライン分だけ保持する想定", size=12, weight=500, fill=GRAY)
    scene.Note(1.0, name, "16 回の読み出し")
    return dict(name=name, page="basics/cache.md", before=BEFORE, scene=scene, size=(780, 460), times=[2.5, 4.5, 6.5, 8.0])


def OverdrawOrder():
    name = "overdraw-order"
    scene = NewScene(name, 780, 480, duration=14.0, hold=1.5, title="描く順で、書き込み回数が変わる: 手前から描くと、奥は捨てられる")
    root = scene.root
    quads = [("A（奥）", range(0, 8), 3), ("B（中）", range(2, 7), 2), ("C（手前）", range(3, 6), 1)]
    cs = 56
    ox = 150

    def Run(order, early_z):
        writes = [0] * 8
        depth = [9] * 8
        hist = []
        for qi in order:
            nm, rg, z = quads[qi]
            for p in rg:
                if early_z and z >= depth[p]:
                    continue
                writes[p] += 1
                depth[p] = min(depth[p], z)
            hist.append(list(writes))
        return hist

    runs = [("奥から描く（Z テストなし）", [0, 1, 2], False, 100), ("手前から描く（早期 Z で、奥を捨てる）", [2, 1, 0], True, 260)]
    totals = []
    for lab, order, ez, y0 in runs:
        hist = Run(order, ez)
        totals.append(sum(hist[-1]))
        scene.Text(root, ox - 80, y0 - 18, lab, size=14, weight=700, fill=INK)
        for p in range(8):
            root.add("rect", x=ox + p * cs, y=y0, width=cs - 4, height=cs - 4, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        for s in range(3):
            t0 = 1.0 + s * 3.0
            t1 = 1.0 + (s + 1) * 3.0 if s < 2 else 99
            for p in range(8):
                v = hist[s][p]
                tx = scene.Text(root, ox + p * cs + (cs - 4) / 2, y0 + cs / 2 + 4, str(v), size=18, weight=700, fill=(RED if v >= 2 else INK), anchor="middle", opacity=0)
                tx.Show(t0, t1 if t1 < 99 else None)
        for s in range(3):
            scene.Text(root, ox - 6, y0 + cs + 18, "", size=1, fill=GRAY)
        scene.Text(root, ox, y0 + cs + 22, "各マス = 1 画素に書き込んだ回数", size=12, weight=500, fill=GRAY)
    assert totals == [16, 8]
    scene.TextStack(root, 390, 440, [(0.0, 1.0, "3 枚の四角形が重なる(奥から A, B, C)"), (1.0, 4.0, "1 枚目を描いた"), (4.0, 7.0, "2 枚目を描いた"), (7.0, 20, "3 枚目まで描くと、書き込みは 16 回 vs 8 回(下は、全画素 1 回)")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "1 枚目 → 3 枚目")
    return dict(name=name, page="rendering/overdraw.md", before=BEFORE, scene=scene, size=(780, 480), times=[2.0, 5.0, 8.0, 12.0])


def LodSteps():
    name = "lod-steps"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="LOD: 距離が離れるほど、三角形の少ないモデルに切り替える")
    root = scene.root
    levels = [(20, 10000), (50, 2500), (120, 600), (300, 2)]
    ax = Axes(scene, root, 70, 70, 640, 250, 300.0, 4.3, ylabel="三角形の数 (10 の何乗か)")
    XLabel(scene, ax, "カメラからの距離 (m)")
    for v in (0, 50, 100, 150, 200, 250, 300):
        scene.Text(root, ax.X(v), ax.y + ax.h + 18, str(v), size=11, weight=500, fill=GRAY, anchor="middle")

    def fn(d):
        for lim, tri in levels:
            if d < lim:
                return math.log10(tri)
        return math.log10(2)

    ax.Curve(fn, RED, width=4, n=600)
    dot = root.add("circle", cx=ax.X(0), cy=ax.Y(fn(0)), r=7, fill=INK)
    Sweep(dot, ax, fn, 1.0, 11.0, 0.0, 299.0, n=150)
    scene.TextStack(root, 390, 395, [(0.0, 1.0, "距離に応じて、モデルを差し替える"), (1.0, 2.3, "0〜20 m: LOD0（10,000 三角形）"), (2.3, 5.0, "20〜50 m: LOD1（2,500）"), (5.0, 8.5, "50〜120 m: LOD2（600）"), (8.5, 20, "120 m〜: インポスター（板 1 枚 = 2 三角形）")], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "距離 0 → 300 m")
    return dict(name=name, page="rendering/lod.md", before=BEFORE, scene=scene, size=(780, 440), times=[1.0, 3.0, 6.0, 9.5])


def GBufferBandwidth():
    name = "gbuffer-bytes"
    scene = NewScene(name, 780, 440, duration=12.0, hold=1.5, title="G-Buffer が 1 フレームに必要とするメモリ帯域（1920×1080、60fps）")
    root = scene.root
    targets = [("アルベド", 4, BLUE), ("法線", 4, GREEN), ("材質(粗さ・金属)", 4, AMBER), ("エミッシブ", 4, PURPLE), ("深度", 4, RED)]
    px = 1920 * 1080
    base_x, base_y = 150, 100
    acc = 0
    for k, (lab, b, col) in enumerate(targets):
        acc += b
        w = b * 22
        y = base_y + k * 40
        scene.Text(root, base_x - 12, y + 20, lab, size=13, weight=500, fill=INK, anchor="end")
        r = root.add("rect", x=base_x, y=y, width=w, height=28, fill=col, opacity=0)
        r.Show(1.0 + k * 1.6)
        scene.Text(root, base_x + w + 10, y + 20, "%d バイト/画素" % b, size=12, weight=500, fill=GRAY, anchor="start", opacity=0).Show(1.0 + k * 1.6)
    per_px = sum(b for _, b, _ in targets)
    mb = per_px * px / 1e6
    gbs_w = per_px * px * 60 / 1e9
    gbs_rw = gbs_w * 2
    assert per_px == 20 and round(mb, 1) == 41.5 and round(gbs_w, 1) == 2.5 and round(gbs_rw, 1) == 5.0
    scene.TextStack(root, 390, 340, [(0.0, 1.0, "画面の 1 画素あたり、各ターゲットが書き込むバイト数"), (1.0, 8.5, "ターゲットを 1 つずつ足していく"), (8.5, 20, "合計 %d バイト/画素 × 207 万画素 = 約 %.1f MB / フレーム" % (per_px, mb))], size=14, fill=INK, anchor="middle")
    scene.TextStack(root, 390, 375, [(0.0, 8.5, ""), (8.5, 20, "60fps で 書き込み 約 %.1f GB/s。ライティングで読むと、合計 約 %.0f GB/s" % (gbs_w, gbs_rw))], size=14, fill=RED, anchor="middle")
    scene.Note(1.0, name, "ターゲットを足す")
    return dict(name=name, page="rendering/bandwidth.md", before=BEFORE, scene=scene, size=(780, 440), times=[2.0, 5.0, 8.0, 10.5])


def FrameBudget():
    name = "frame-budget-bar"
    scene = NewScene(name, 780, 360, duration=12.0, hold=1.5, title="60fps は 1 フレーム 16.7 ms。その中に、全部の処理を入れる")
    root = scene.root
    segs = [("入力", 0.5, GRAY), ("ゲーム更新", 3.0, BLUE), ("物理", 2.0, GREEN), ("描画の準備(CPU)", 4.0, AMBER), ("GPU 待ち", 1.5, RED)]
    total = sum(s[1] for s in segs)
    budget = 1000 / 60
    assert total == 11.0 and round(budget, 1) == 16.7
    x0, w, y = 70, 640, 130
    root.add("rect", x=x0, y=y, width=w, height=50, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
    acc = 0.0
    for k, (lab, ms, col) in enumerate(segs):
        sw = ms / budget * w
        sx = x0 + acc / budget * w
        r = root.add("rect", x=sx, y=y, width=sw, height=50, fill=col, opacity=0)
        r.Show(1.0 + k * 1.8)
        scene.Text(root, sx + sw / 2, y + 78 + (k % 2) * 20, "%s %.1f" % (lab, ms), size=12, weight=700, fill=col, anchor="middle", opacity=0).Show(1.0 + k * 1.8)
        acc += ms
    scene.Text(root, x0 + w, y - 10, "16.7 ms", size=12, weight=700, fill=GRAY, anchor="end")
    scene.TextStack(root, 390, 300, [(0.0, 1.0, "バーの全体が 1 フレーム(16.7 ms)"), (1.0, 10.0, "処理を 1 つずつ足していく"), (10.0, 20, "合計 %.1f ms。残り %.1f ms が余裕（ここを使い切らない）" % (total, budget - total))], size=14, fill=INK, anchor="middle")
    scene.Note(1.0, name, "処理を足す")
    return dict(name=name, page="optimize/frame-budget.md", before=BEFORE, scene=scene, size=(780, 360), times=[2.0, 5.0, 8.0, 11.0])


def FixedStep():
    name = "fixed-step-accum"
    scene = NewScene(name, 780, 420, duration=13.0, hold=1.5, title="固定タイムステップ: 描画の間隔がバラバラでも、物理は一定の刻みで進める")
    root = scene.root
    dts = [0.010, 0.020, 0.045, 0.016, 0.008, 0.030]
    step = 1 / 60
    acc, steps_total, per = 0.0, 0, []
    for dt in dts:
        acc += dt
        n = 0
        while acc >= step - 1e-12:
            acc -= step
            n += 1
        per.append(n)
        steps_total += n
    total_t = sum(dts)
    assert sum(per) == int(total_t / step + 1e-9)
    x0, w = 70, 640
    X = lambda t: x0 + t / total_t * w
    scene.Text(root, x0, 100, "物理の刻み（1/60 秒ごと）", size=13, weight=700, fill=BLUE)
    scene.Text(root, x0, 215, "描画フレーム（実際の経過時間）", size=13, weight=700, fill=AMBER)
    root.add("line", x1=x0, y1=140, x2=x0 + w, y2=140, stroke="#94a3b8", stroke_width=2)
    root.add("line", x1=x0, y1=255, x2=x0 + w, y2=255, stroke="#94a3b8", stroke_width=2)
    cum = 0.0
    done = 0
    for i, dt in enumerate(dts):
        cum += dt
        t = 1.0 + i * 1.7
        fr = root.add("rect", x=X(cum) - 4, y=235, width=8, height=40, fill=AMBER, opacity=0)
        fr.Show(t)
        scene.Text(root, X(cum), 295, "%d ms" % round(dt * 1000), size=11, weight=500, fill=GRAY, anchor="middle", opacity=0).Show(t)
        for k in range(per[i]):
            tk = (done + k + 1) * step
            tick = root.add("rect", x=X(tk) - 3, y=120, width=6, height=40, fill=BLUE, opacity=0)
            tick.Show(t + 0.3)
        done += per[i]
    items = [(0.0, 1.0, "実際の経過時間は、ばらつく（10〜45 ms）")] + [(1.0 + i * 1.7, 1.0 + (i + 1) * 1.7 if i < 5 else 99, "フレーム %d（%d ms）: 物理を %d 回進める" % (i + 1, round(dts[i] * 1000), per[i])) for i in range(6)]
    scene.TextStack(root, 390, 345, items, size=14, fill=INK, anchor="middle")
    scene.Text(root, 390, 385, "溜まった時間（アキュムレータ）から、1/60 秒ずつ引いて、引けた回数だけ物理を進める", size=12, weight=500, fill=GRAY, anchor="middle")
    scene.Note(1.0, name, "フレーム 1 → 6")
    return dict(name=name, page="engine/game-loop.md", before=BEFORE, scene=scene, size=(780, 420), times=[2.0, 4.0, 6.5, 11.0])


def HandleGeneration():
    name = "handle-generation"
    scene = NewScene(name, 780, 420, duration=14.0, hold=1.5, title="ハンドルの世代番号: 古いハンドルで、別の物を触らない")
    root = scene.root
    sx, sy, sw, sh = 150, 110, 120, 70
    for i in range(4):
        root.add("rect", x=sx + i * (sw + 10), y=sy, width=sw, height=sh, fill="#ffffff", stroke="#94a3b8", stroke_width=2)
        scene.Text(root, sx + i * (sw + 10) + sw / 2, sy - 8, "スロット %d" % i, size=12, weight=500, fill=GRAY, anchor="middle")
    x2 = sx + 2 * (sw + 10) + sw / 2
    states = [(0.0, 3.0, "空き  世代 1", GRAY), (3.0, 6.0, "敵 A  世代 1", GREEN), (6.0, 9.0, "空き  世代 2", GRAY), (9.0, 99, "敵 B  世代 2", BLUE)]
    for a, b, tx, col in states:
        t = scene.Text(root, x2, sy + 42, tx, size=14, weight=700, fill=col, anchor="middle", opacity=0)
        if a == 0.0:
            t.Set(0.0, "opacity", 1)
            t.Set(b, "opacity", 0)
        else:
            t.Show(a, b if b < 99 else None)
    hs = [(0.0, 3.0, "（まだ、ハンドルはない）", GRAY), (3.0, 6.0, "敵 A を作る → ハンドル hA = (スロット 2, 世代 1)", GREEN), (6.0, 9.0, "A を破壊 → スロット 2 の世代が 2 に上がる", RED), (9.0, 12.0, "敵 B を作る → スロット 2 を再利用。hB = (2, 世代 2)", BLUE), (12.0, 99, "古い hA = (2, 世代 1) で触ろうとする → 世代が違う → 拒否", RED)]
    items = [(a, b, tx) for a, b, tx, c in hs]
    scene.TextStack(root, 390, 280, items, size=15, fill=INK, anchor="middle")
    ok = scene.Text(root, 390, 330, "世代が一致しないので、B を壊さずに済む", size=14, weight=700, fill=GREEN, anchor="middle", opacity=0)
    ok.Show(12.0)
    scene.Note(3.0, name, "作る → 壊す → 再利用 → 古いハンドル")
    return dict(name=name, page="engine/handle.md", before=BEFORE, scene=scene, size=(780, 420), times=[1.5, 4.5, 7.5, 10.5, 13.0])


FIGS = [FloatSpacing, SrgbGamma, NlerpSlerp, LevelCurve, BigO, CacheStride, OverdrawOrder, LodSteps, GBufferBandwidth, FrameBudget, FixedStep, HandleGeneration]
