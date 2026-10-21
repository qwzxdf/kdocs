"""静止した図（構造・流れ）用の SVG を作る小さな道具。

使い方（ページごとの生成スクリプトから）:
    import svgfig as g
    body = g.box(16, 52, 150, 44, "名前") + g.arrow(166, 74, 206, 74, "m1")
    print(g.svg(720, 120, "図の説明", "m1", body, "図の題名"))
出てきた <svg> を md に貼る（svg の前後は空行）。矢印の marker の id は、ページの中で一意にする。
色は青（BOX）、注目の黄（HOT）、灰（GRAY）。文字色はサイトの CSS に任せる。
"""
import json
from xml.sax.saxutils import escape

BOX = 'fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"'
HOT = 'fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"'
GRAY = 'fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"'


def box(x, y, w, h, label, style=BOX, size=13, rx=9):
  cx, cy = x + w / 2, y + h / 2
  return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {style}/>'
          f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
          f'style="font-size:{size}px;font-weight:600">{escape(label)}</text>')


def text(x, y, s, size=12, anchor="middle", weight=400):
  return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
          f'style="font-size:{size}px;font-weight:{weight}">{escape(s)}</text>')


def arrow(x1, y1, x2, y2, mid):
  return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" '
          f'stroke-width="2" marker-end="url(#{mid})"/>')


def svg(w, h, label, mid, body, title):
  return (f'<svg class="fig flow" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
          f'<defs><marker id="{mid}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
          f'<path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>'
          f'<text x="14" y="22" class="fig-title">{escape(title)}</text>{body}</svg>')
