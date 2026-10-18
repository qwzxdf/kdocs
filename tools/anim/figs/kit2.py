"""手の込んだ図(forward vs deferred 並み)を作るための部品。

960×540 の舞台に、パネル・ピクセル格子・カウンター・結果ボックス・凡例を置く。
座標を手で書かず、計算結果(depth・AO・色など)から図を作ること。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import (AMBER, BLUE, GRAY, GREEN, INK, LIGHT, PURPLE, RED, Hex, Lerp, Mix, NewScene, R)  # noqa: E402,F401

W, H = 960, 540
TEXT = "#1f2937"
MUTED = "#64748b"
LINE = "#94a3b8"


def Fmt(v):
    return "{:,}".format(v)


class Stage:
    """960×540 の舞台。title は左上の見出し。"""

    def __init__(self, name, title, duration=14.0, hold=1.5, subtitle=None):
        self.name = name
        self.scene = NewScene(name, W, H, duration=duration, hold=hold)
        self.root = self.scene.root
        self.duration = duration
        self.scene.Text(self.root, 30, 32, title, size=22, fill=TEXT)
        if subtitle:
            self.scene.Text(self.root, 30, 52, subtitle, size=13, weight=500, fill=MUTED)

    def Text(self, x, y, text, size=14, weight=700, fill=TEXT, anchor="start", **kw):
        return self.scene.Text(self.root, x, y, text, size=size, weight=weight, fill=fill, anchor=anchor, **kw)

    def Note(self, t, who, text):
        self.scene.Note(t, who, text)

    def Caption(self, x, y, items, size=15, fill=TEXT, weight=700, anchor="start"):
        return self.scene.TextStack(self.root, x, y, items, size=size, fill=fill, weight=weight, anchor=anchor)

    def Counter(self, x, y, series, size=26, fill=TEXT, anchor="start"):
        return self.scene.Counter(self.root, x, y, series, size=size, fill=fill, anchor=anchor)

    def Panel(self, x, y, w, h, title=None, color=LINE, fill="#ffffff", sub=None):
        self.root.add("rect", x=x, y=y, width=w, height=h, fill=fill, stroke=color, stroke_width=1.8, rx=6)
        if title:
            self.scene.Text(self.root, x, y - 10, title, size=15, fill=color if color != LINE else TEXT)
        if sub:
            self.scene.Text(self.root, x + w, y - 8, sub, size=12, weight=500, fill=MUTED, anchor="end")

    def Box(self, t, x, y, w, h, lines, stroke, fill):
        """結果ボックス。lines = [(text, size, color), ...]。t 秒に出る。"""
        g = self.root.add("g", opacity=0)
        g.Show(t)
        g.add("rect", x=x, y=y, width=w, height=h, rx=12, fill=fill, stroke=stroke, stroke_width=2.5)
        yy = y + 24
        for text, size, color in lines:
            self.scene.Text(g, x + 16, yy, text, size=size, fill=color)
            yy += size + 9
        return g

    def Legend(self, x, y, items, size=12):
        """items = [(color, text), ...] を横に並べる。"""
        cx = x
        for color, text in items:
            self.root.add("circle", cx=cx + 6, cy=y - 4, r=6, fill=color)
            self.scene.Text(self.root, cx + 16, y, text, size=size, weight=500, fill=MUTED)
            cx += 26 + len(text) * size * 0.95
        return cx


class Grid:
    """ピクセル格子。Paint(i, j, t, color) で色の変化を貯め、Flush() でまとめて出す。"""

    def __init__(self, stage, x, y, nx, ny, cell, base="#ffffff", parent=None, stroke=None, cell_h=None):
        self.stage, self.x, self.y, self.nx, self.ny, self.cell = stage, x, y, nx, ny, cell
        self.cell_h = cell_h or cell
        self.parent = parent or stage.root
        self.nodes = {}
        self.steps = {}
        self.base = base
        for j in range(ny):
            for i in range(nx):
                node = self.parent.add("rect", x=R(x + i * cell), y=R(y + j * self.cell_h), width=R(cell + 0.3), height=R(self.cell_h + 0.3), fill=base)
                self.nodes[(i, j)] = node
                self.steps[(i, j)] = []
        if stroke:
            self.parent.add("rect", x=x, y=y, width=nx * cell, height=ny * self.cell_h, fill="none", stroke=stroke, stroke_width=1.5)

    def Paint(self, i, j, t, color):
        self.steps[(i, j)].append((t, color))

    def Flush(self):
        for key, items in self.steps.items():
            if items:
                items.sort(key=lambda z: z[0])
                self.nodes[key].Steps("fill", items)

    def Frame(self, i, j, color=RED, width=2.5):
        return self.parent.add("rect", x=R(self.x + i * self.cell), y=R(self.y + j * self.cell_h), width=self.cell, height=self.cell_h, fill="none", stroke=color, stroke_width=width, opacity=0)

    def Lines(self, color="#ffffff", opacity=0.3):
        g = self.parent.add("g", opacity=opacity)
        for i in range(1, self.nx):
            g.add("line", x1=R(self.x + i * self.cell), y1=self.y, x2=R(self.x + i * self.cell), y2=R(self.y + self.ny * self.cell), stroke=color, stroke_width=0.5)
        for j in range(1, self.ny):
            g.add("line", x1=self.x, y1=R(self.y + j * self.cell), x2=R(self.x + self.nx * self.cell), y2=R(self.y + j * self.cell), stroke=color, stroke_width=0.5)
        g.add("rect", x=self.x, y=self.y, width=self.nx * self.cell, height=self.ny * self.cell, fill="none", stroke=LINE, stroke_width=1.5)
        return g


def Gray(v):
    v = max(0.0, min(1.0, v))
    return Hex([255 * v] * 3)


def Build(stage, name, page, before, times):
    return dict(name=name, page=page, before=before, scene=stage.scene, size=(W, H), times=times)
