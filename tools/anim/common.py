import io
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storyboard import Hex, Mix, Rgb, Scene  # noqa: E402,F401

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DOCS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs")

INK = "#1f2937"
GRAY = "#64748b"
BLUE = "#2563eb"
PURPLE = "#7c3aed"
RED = "#e5484d"
GREEN = "#2ea043"
AMBER = "#e5aa28"
LIGHT = "#e2e8f0"


def NewScene(name, width=780, height=360, duration=10.0, hold=1.5, title=None):
    scene = Scene(name, width, height, duration, hold)
    defs = scene.root.add("defs")
    marker = defs.add("marker", id="arr-" + name, markerWidth=9, markerHeight=9, refX=8, refY=4.5, orient="auto")
    marker.add("path", d="M0,0 L9,4.5 L0,9 z", fill=INK)
    scene.defs = defs
    scene.marker = "url(#arr-%s)" % name
    if title:
        scene.Text(scene.root, 20, 28, title, size=17, fill=INK)
    return scene


def Arrow(scene, parent, x1, y1, x2, y2, color=INK, width=2.5, dash=None):
    extra = {"stroke_dasharray": dash} if dash else {}
    return parent.add("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=width, marker_end=scene.marker, **extra)


def Caption(scene, x, y, items, size=15, fill=INK, weight=700, anchor="start"):
    return scene.TextStack(scene.root, x, y, items, size=size, fill=fill, weight=weight, anchor=anchor)


def R(v):
    return round(v, 2)


def Place(page, name, svg, before=None, replace_fig=None):
    path = os.path.join(DOCS, page)
    text = io.open(path, encoding="utf-8").read()
    begin = "<!-- fig:%s:begin -->" % name
    end = "<!-- fig:%s:end -->" % name
    block = begin + "\n\n" + svg + "\n" + end
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        text = pattern.sub(lambda m: block, text)
    elif replace_fig:
        fig = re.compile(r"<svg[^>]*data-fig=\"%s\".*?</svg>" % re.escape(replace_fig), re.S)
        if not fig.search(text):
            raise ValueError("fig %s not found in %s" % (replace_fig, page))
        text = fig.sub(lambda m: block, text, count=1)
    else:
        idx = text.find("\n" + before)
        if idx < 0:
            raise ValueError("heading %r not found in %s" % (before, page))
        text = text[:idx + 1] + block + "\n\n" + text[idx + 1:]
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def Save(scene, name):
    os.makedirs(OUT, exist_ok=True)
    svg = scene.Render()
    io.open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="").write(svg)
    io.open(os.path.join(OUT, name + ".report.txt"), "w", encoding="utf-8").write(scene.Report() + "\n")
    return svg


def Lerp(a, b, t):
    return a + (b - a) * t


def Smooth(t):
    return t * t * (3 - 2 * t)
