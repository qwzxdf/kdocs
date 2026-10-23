# -*- coding: utf-8 -*-
"""docs/directx/concepts/cbuffer-packing.md の図(レジスタの升目)を作る。

使い方: python tools/make_cbuffer_fig.py
出力: 2 枚の <svg> を標準出力に出す(md には、そのまま貼る)。
座標は、DXC(-Od -Fc)の逆アセンブリで確かめた値(k-hlsl/tests/CBufferTest が突き合わせている)。
"""
import sys
from xml.sax.saxutils import escape

BLUE = ('rgba(76,139,245,0.22)', '#4c8bf5')
YELLOW = ('rgba(229,170,40,0.28)', '#e5aa28')
GRAY = ('rgba(148,163,184,0.18)', '#94a3b8')

X0 = 70        # 升目の左端
BW = 36        # 1 バイトの幅
ROW_H = 34


def figure(fig_id, title, rows, items, label, note_lines):
    """items: (offset, size, text, kind) kind = 'm' メンバー / 'h' 注目 / 'g' 隙間"""
    top = 52
    height = top + rows * ROW_H + 20 + 18 * len(note_lines) + 14
    w = X0 + 16 * BW + 16
    out = []
    out.append('<svg class="fig flow" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (w, height, escape(label)))
    out.append('<text x="14" y="22" class="fig-title">%s</text>' % escape(title))
    # 見出し(+0 +4 +8 +12)
    for c in range(4):
        out.append('<text x="%d" y="%d" text-anchor="middle" style="font-size:11px;font-weight:400">+%d</text>' % (X0 + (c * 4 + 2) * BW, top - 6, c * 4))
    for r in range(rows):
        y = top + r * ROW_H
        out.append('<text x="%d" y="%d" text-anchor="end" dominant-baseline="central" style="font-size:12px;font-weight:600">c%d</text>' % (X0 - 10, y + ROW_H / 2 - 1, r))
        out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>' % (X0, y, 16 * BW, ROW_H - 4))
    for off, size, text, kind in items:
        pos = off
        first = True
        while pos < off + size:
            row_end = (pos // 16 + 1) * 16
            end = min(off + size, row_end)
            fill, stroke = {'m': BLUE, 'h': YELLOW, 'g': GRAY}[kind]
            x = X0 + (pos % 16) * BW
            y = top + (pos // 16) * ROW_H
            wd = (end - pos) * BW
            dash = ' stroke-dasharray="4 3"' if kind == 'g' else ''
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="%s" stroke="%s" stroke-width="2"%s/>' % (x + 1, y, wd - 2, ROW_H - 4, fill, stroke, dash))
            if first or kind != 'g':
                weight = 400 if kind == 'g' else 600
                out.append('<text x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:%d">%s</text>' % (x + wd / 2, y + (ROW_H - 4) / 2, weight, escape(text if first else '(続き)')))
            first = False
            pos = end
    y = top + rows * ROW_H + 20
    for line in note_lines:
        out.append('<text x="14" y="%d" style="font-size:12px;font-weight:400">%s</text>' % (y, escape(line)))
        y += 18
    out.append('</svg>')
    return ''.join(out)


def fig1():
    items = [
        (0, 64, 'float4x4 world', 'm'),
        (64, 12, 'tint', 'm'), (76, 4, 'alpha', 'm'),
        (80, 8, 'uvScale', 'm'), (88, 8, '隙間 8', 'g'),
        (96, 12, 'lightDir', 'h'), (108, 4, 'inten', 'm'),
        (112, 4, 'shine', 'm'), (116, 12, '隙間 12', 'g'),
    ]
    return figure('cb1', 'PerObject のレイアウト（116 バイト、確保は 128 バイト）', 8, items,
                  'float3 lightDir が、行の境界をまたげないので次の行へ送られ、前に 8 バイトの隙間ができる',
                  ['lightDir（12 バイト）は、88〜100 で 96 の境界をまたぐので、96 から始まる。',
                   '手前の 88〜96 は使われずに残る。末尾の 116〜128 は、確保の大きさを 16 の倍数にするための余り。'])


def fig2():
    items = [
        (0, 4, 'c[0]', 'm'), (4, 12, '隙間 12', 'g'),
        (16, 4, 'c[1]', 'm'), (20, 12, '隙間 12', 'g'),
        (32, 4, 'c[2]', 'm'), (36, 4, 'd', 'h'), (40, 8, '', 'g'),
    ]
    return figure('cb2', 'float c[3]; float d; のレイアウト', 3, items,
                  '配列は要素ごとに 16 バイトの行を使う。最後の要素の後ろの余りには、次の変数が入れる',
                  ['配列 float c[3] は、要素ごとに 1 行（16 バイト）を使う。大きさは 16 × 2 + 4 = 36 バイトで、',
                   '最後の要素のあとの余りには、次の変数 d が入る。'])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(fig1())
    print()
    print(fig2())
