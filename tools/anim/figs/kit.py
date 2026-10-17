import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Arrow, Caption, Hex, Lerp, Mix, NewScene, R, Smooth)  # noqa: E402,F401


def Blur(scene, ident, std):
    """静的なぼかしフィルタ(stdDeviation はアニメさせない)。"""
    f = scene.defs.add("filter", id=ident, x="-60%", y="-60%", width="220%", height="220%")
    f.add("feGaussianBlur", stdDeviation=std)
    return "url(#%s)" % ident


class Axes:
    """x/y の軸つきグラフ。X(v), Y(v) で座標に直す。"""

    def __init__(self, scene, parent, x, y, w, h, xmax, ymax, xlabel="", ylabel="", xmin=0.0, ymin=0.0, grid=True):
        self.scene, self.parent = scene, parent
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        parent.add("rect", x=x, y=y, width=w, height=h, fill="#ffffff", stroke="#94a3b8", stroke_width=1.5)
        if grid:
            for i in range(1, 4):
                parent.add("line", x1=x + w * i / 4, y1=y, x2=x + w * i / 4, y2=y + h, stroke=LIGHT, stroke_width=1)
                parent.add("line", x1=x, y1=y + h * i / 4, x2=x + w, y2=y + h * i / 4, stroke=LIGHT, stroke_width=1)
        if xlabel:
            scene.Text(parent, x + w, y + h + 20, xlabel, size=12, weight=500, fill=GRAY, anchor="end")
        if ylabel:
            scene.Text(parent, x, y - 8, ylabel, size=12, weight=500, fill=GRAY)

    def X(self, v):
        return R(self.x + (v - self.xmin) / (self.xmax - self.xmin) * self.w)

    def Y(self, v):
        return R(self.y + self.h - (v - self.ymin) / (self.ymax - self.ymin) * self.h)

    def D(self, fn, x0=None, x1=None, n=60):
        x0 = self.xmin if x0 is None else x0
        x1 = self.xmax if x1 is None else x1
        pts = []
        for i in range(n + 1):
            v = x0 + (x1 - x0) * i / n
            pts.append("%s,%s" % (self.X(v), self.Y(max(self.ymin, min(self.ymax, fn(v))))))
        return "M" + " L".join(pts)

    def Curve(self, fn, color, width=3, x0=None, x1=None, n=60, dash=None, opacity=1):
        extra = {"stroke_dasharray": dash} if dash else {}
        return self.parent.add("path", d=self.D(fn, x0, x1, n), fill="none", stroke=color, stroke_width=width, opacity=opacity, **extra)


def Sweep(node, axes, fn, t0, t1, v0, v1, n=24, attrs=("cx", "cy")):
    """点 node を曲線 fn に沿って v0→v1 へ動かす(時刻 t0→t1)。"""
    prev = None
    for i in range(n + 1):
        f = i / n
        v = Lerp(v0, v1, f)
        t = Lerp(t0, t1, f)
        pos = (axes.X(v), axes.Y(fn(v)))
        if i == 0:
            node.Set(t, attrs[0], pos[0])
            node.Set(t, attrs[1], pos[1])
        else:
            node.Ramp(prev, t, attrs[0], pos[0])
            node.Ramp(prev, t, attrs[1], pos[1])
        prev = t


def LiveText(scene, parent, x, y, t0, t1, n, make, size=15, fill=INK, weight=700, anchor="start"):
    """t0〜t1 を n 等分して、make(i, f) の文字列を順に出す。"""
    items = []
    for i in range(n):
        a = Lerp(t0, t1, i / n)
        b = Lerp(t0, t1, (i + 1) / n)
        items.append((a, b, make(i, i / max(1, n - 1))))
    return scene.TextStack(parent, x, y, items, size=size, fill=fill, weight=weight, anchor=anchor)


def Gray(v):
    """リニア値 v(0〜1)を表示用のグレー(sRGB)に直す。"""
    v = max(0.0, min(1.0, v))
    s = v ** (1 / 2.2)
    return Hex([s * 255] * 3)


def RampFill(node, attr, t0, t1, n, make):
    """色を n 分割で滑らかに変える。make(f) が色を返す。"""
    prev = None
    for i in range(n + 1):
        f = i / n
        t = Lerp(t0, t1, f)
        v = make(f)
        if i == 0:
            node.Set(t, attr, v)
        else:
            node.Ramp(prev, t, attr, v)
        prev = t


def Panel(scene, parent, x, y, w, h, title=None, fill="#ffffff"):
    parent.add("rect", x=x, y=y, width=w, height=h, fill=fill, stroke="#94a3b8", stroke_width=1.5, rx=4)
    if title:
        scene.Text(parent, x + w / 2, y - 8, title, size=13, weight=700, fill=GRAY, anchor="middle")
