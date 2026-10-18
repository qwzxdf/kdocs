import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import AMBER, BLUE, GRAY, GREEN, INK, LIGHT, MUTED, PURPLE, RED, TEXT, Gray, Grid, Mix, R, Stage, Build, Fmt  # noqa: E402

BEFORE = "## よくあるミス"


def Profile():
    """断面の高さ。0 = 床。壁(高さ 3)と小さな段差(高さ 0.8)。"""
    n = 24
    h = [0.0] * n
    h[11] = 2.0
    for i in (12, 13, 14):
        h[i] = 4.5
    for i in (4, 5):
        h[i] = 0.8
    return h


def SsaoSamples():
    name = "ssao-samples"
    st = Stage(name, "SSAO: 周りの深度を調べて、「どれくらい囲まれているか」を数える", duration=16.0, subtitle="断面(横から見た図)で、ピクセル 1 つぶんの調べ方 → 全ピクセルに広げる")
    sc, root = st.scene, st.root
    h = Profile()
    n = len(h)
    cs, ox, oy = 20.0, 40.0, 330.0          # 列の幅、断面の左端、床の y
    zs = 44.0                              # 高さ 1 あたりの px
    RAD = 3.5
    BIAS = 0.05
    focus = 10                              # 調べるピクセルの列

    # ---- 左: 断面 ----
    st.Panel(30, 90, 490, 274, "① 断面と、深度バッファ(各列の見える高さ)", color=BLUE)
    for i in range(n):
        if h[i] > 0:
            root.add("rect", x=R(ox + i * cs), y=R(oy - h[i] * zs), width=cs, height=R(h[i] * zs), fill="#cbd5e1", stroke="#94a3b8", stroke_width=1)
    root.add("line", x1=ox, y1=oy, x2=ox + n * cs, y2=oy, stroke="#94a3b8", stroke_width=2)
    # 深度バッファの帯(高い = 近い = 明るい)
    st.Text(30, 392, "深度バッファ(明るい = カメラに近い)", size=13, fill=MUTED)
    depth_cells = []
    for i in range(n):
        v = 0.25 + 0.75 * (h[i] / 4.5)
        depth_cells.append(root.add("rect", x=R(ox + i * cs), y=398, width=cs - 1, height=26, fill=Gray(v), stroke="#94a3b8", stroke_width=1))
    frames = [root.add("rect", x=R(ox + i * cs), y=396, width=cs - 1, height=30, fill="none", stroke=AMBER, stroke_width=3.5, opacity=0) for i in range(n)]

    # 調べるピクセル
    def Surface(i):
        return (i + 0.5, h[i])

    px, pz = Surface(focus)
    X = lambda x: ox + x * cs
    Z = lambda z: oy - z * zs
    root.add("circle", cx=R(X(px)), cy=R(Z(pz)), r=8, fill=INK)
    st.Text(X(px), Z(pz) + 26, "調べるピクセル", size=13, fill=INK, anchor="middle")
    # 半球(2D なので半円)
    root.add("path", d="M%s,%s A%s,%s 0 0 1 %s,%s" % (R(X(px - RAD)), R(Z(pz)), R(RAD * cs), R(RAD * zs), R(X(px + RAD)), R(Z(pz))), fill="none", stroke="#93c5fd", stroke_width=2.5, stroke_dasharray="6 5")
    st.Text(X(px - RAD), Z(pz) + 20, "半径", size=12, weight=500, fill="#2563eb")

    # サンプル 8 個(半円の方向と距離を散らす)
    K = 8
    golden = 0.6180339887
    samples = []
    for k in range(K):
        ang = math.pi * (k + 0.5) / K
        r = RAD * (0.35 + 0.65 * ((k * golden) % 1.0))
        dx, dz = r * math.cos(ang), r * math.sin(ang)
        sx, sz = px + dx, pz + dz
        col = int(math.floor(sx))
        col = max(0, min(n - 1, col))
        hz = h[col]
        occluded = hz > sz + BIAS
        in_range = abs(hz - pz) < RAD
        state = "occ" if (occluded and in_range) else ("far" if occluded else "open")
        samples.append(dict(sx=sx, sz=sz, col=col, hz=hz, state=state))
    n_occ = sum(1 for s in samples if s["state"] == "occ")
    n_far = sum(1 for s in samples if s["state"] == "far")
    n_open = K - n_occ - n_far
    assert n_occ + n_far + n_open == K and n_occ >= 1 and n_far >= 1
    ao_focus = 1.0 - n_occ / K
    colors = {"open": GREEN, "occ": RED, "far": "#9ca3af"}
    names = {"open": "空き(光が来る)", "occ": "遮られている", "far": "遠すぎるので無視"}
    t0, step = 1.2, 0.55
    for k, s in enumerate(samples):
        t = t0 + k * step
        g = root.add("g", opacity=0)
        g.Show(t)
        g.add("line", x1=R(X(px)), y1=R(Z(pz)), x2=R(X(s["sx"])), y2=R(Z(s["sz"])), stroke=colors[s["state"]], stroke_width=1.5, stroke_dasharray="4 4")
        g.add("circle", cx=R(X(s["sx"])), cy=R(Z(s["sz"])), r=7, fill=colors[s["state"]], stroke="#ffffff", stroke_width=2)
        sc.Text(g, R(X(s["sx"])), R(Z(s["sz"])) - 11, str(k + 1), size=11, fill=INK, anchor="middle")
        # その点の深度を読む
        fr = frames[s["col"]]
        fr.Set(t, "opacity", 1)
        fr.Set(t + step, "opacity", 0)
        # 読んだ高さ(破線)
        rd = root.add("line", x1=R(X(s["sx"])), y1=R(Z(s["sz"])), x2=R(X(s["sx"])), y2=R(Z(s["hz"])), stroke=colors[s["state"]], stroke_width=2.5, opacity=0)
        rd.Show(t, t + step)
    st.Legend(42, 118, [(GREEN, "空き"), (RED, "遮蔽"), ("#9ca3af", "無視(遠すぎ)")])

    # ---- 右: 数える ----
    st.Panel(550, 90, 380, 274, "② サンプルごとの判定", color=PURPLE)
    st.Text(566, 114, "サンプル点の深度 と バッファの深度を比べる", size=12, weight=500, fill=MUTED)
    for k, s in enumerate(samples):
        y = 142 + k * 26
        tt = t0 + k * step
        g = root.add("g", opacity=0)
        g.Show(tt)
        g.add("circle", cx=578, cy=y - 5, r=8, fill=colors[s["state"]])
        sc.Text(g, 578, y - 1, str(k + 1), size=10, fill="#ffffff", anchor="middle")
        sc.Text(g, 596, y, "点の高さ %.2f  /  バッファ %.2f" % (s["sz"], s["hz"]), size=13, weight=500, fill=TEXT)
        verdict = {"open": "空き", "occ": "遮蔽", "far": "無視"}[s["state"]]
        sc.Text(g, 905, y, verdict, size=14, fill=colors[s["state"]], anchor="end")
    t_end = t0 + K * step
    cnt = [(t0 + k * step, k + 1) for k in range(K)]
    st.Text(566, 352, "深度の読み込み:", size=14)
    st.Counter(690, 354, cnt, size=22)
    ao_t = sc.Text(root, 910, 352, "AO = 1 − %d/%d = %.3f" % (n_occ, K, ao_focus), size=17, fill=PURPLE, anchor="end", opacity=0)
    ao_t.Show(t_end)

    # ---- 下: 全ピクセル ----
    st.Text(30, 456, "③ 全部の列で同じことを繰り返す → AO の帯", size=15, fill=TEXT)
    scells = Grid(st, ox, 468, n, 1, cs, base="#e5e7eb", stroke="#94a3b8")
    # 全列の AO を計算
    ao = []
    total_reads = 0
    for i in range(n):
        qx, qz = Surface(i)
        occ = 0
        for k in range(K):
            ang = math.pi * (k + 0.5) / K
            r = RAD * (0.35 + 0.65 * ((k * golden) % 1.0))
            sx, sz = qx + r * math.cos(ang), qz + r * math.sin(ang)
            col = max(0, min(n - 1, int(math.floor(sx))))
            hz = h[col]
            if hz > sz + BIAS and abs(hz - qz) < RAD:
                occ += 1
            total_reads += 1
        ao.append(1.0 - occ / K)
    assert total_reads == n * K and abs(ao[focus] - ao_focus) < 1e-9
    sweep_t0, sweep_dt = t_end + 0.8, 0.2
    series = []
    for i in range(n):
        t = sweep_t0 + i * sweep_dt
        scells.Paint(i, 0, t, Gray(0.15 + 0.85 * ao[i]))
        series.append((t, (i + 1) * K))
    scells.Flush()
    for i in range(n):
        t = sweep_t0 + i * sweep_dt
        fr = frames[i]
        # 走査中の列の枠
        pass
    mark = root.add("rect", x=R(ox), y=462, width=cs, height=cs + 12, fill="none", stroke=AMBER, stroke_width=3.5, opacity=0)
    for i in range(n):
        t = sweep_t0 + i * sweep_dt
        mark.Set(t, "x", R(ox + i * cs))
        mark.Set(t, "opacity", 1)
    mark.Set(sweep_t0 + n * sweep_dt, "opacity", 0)
    st.Text(560, 478, "深度の読み込み(合計):", size=14)
    st.Counter(750, 480, series, size=24, fill=PURPLE)
    sweep_end = sweep_t0 + n * sweep_dt
    floor_ao = [ao[i] for i in range(n) if h[i] == 0.0]
    near_wall = ao[focus]
    far_floor = ao[1]
    top_ao = ao[12]
    box = st.Box(sweep_end + 0.3, 550, 384, 380, 70, [("24 列 × 8 サンプル = %d 回の深度読み込み" % total_reads, 15, "#4c1d95"), ("壁際の床 %.2f / 離れた床 %.2f / 壁の上 %.2f" % (near_wall, far_floor, top_ao), 14, "#4c1d95")], PURPLE, "#f5f3ff")
    st.Caption(30, 520, [(0.0, t0, "調べたいピクセルの周りの、半円の中に、サンプル点を撒く"), (t0, t_end, "各サンプル点の位置の深度を読んで、「点がかべの中にあるか」を調べる"), (t_end, sweep_t0, "数えた結果で、このピクセルの AO が決まる"), (sweep_t0, sweep_end, "同じ処理を、すべてのピクセルに繰り返す(暗い = 囲まれている)"), (sweep_end, 99, "壁際の床だけが暗く、壁の上や離れた床は明るい → 隅が自然に暗くなる")], size=14, fill=MUTED, weight=500)
    st.Note(t0, "SSAO", "サンプル 8 個を順に判定: 遮蔽 %d / 無視 %d / 空き %d(AO %.3f)" % (n_occ, n_far, n_open, ao_focus))
    st.Note(sweep_t0, "SSAO", "全 %d 列を走査。深度の読み込みは合計 %d 回" % (n, total_reads))
    return Build(st, name, "graphics/ao/ssao-hemisphere.md", "## よくあるミス", [1.5, 4.0, 6.5, 9.0, 13.0, 15.0]), ao


NAMES = ["ssao-samples"]
FIGS = [lambda: SsaoSamples()[0]]
