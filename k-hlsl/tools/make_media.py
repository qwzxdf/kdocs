# -*- coding: utf-8 -*-
"""拡張のアイコン(128x128)とプレビュー(200x200)を、標準ライブラリだけで描く。"""
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 5x7 のビットマップ フォント("K", "-", "H", "L", "S")
FONT = {
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
}


def png(path, w, h, pix):
    raw = b''.join(b'\x00' + bytes(sum(([r, g, b, a] for (r, g, b, a) in pix[y * w:(y + 1) * w]), [])) for y in range(h))

    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) \
        + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)


def draw(size):
    bg = (30, 34, 46, 255)
    accent = (86, 156, 214, 255)
    pix = [bg] * (size * size)
    # 角を丸くする
    r = size // 6
    for y in range(size):
        for x in range(size):
            dx = max(r - x, x - (size - 1 - r), 0)
            dy = max(r - y, y - (size - 1 - r), 0)
            if dx * dx + dy * dy > r * r:
                pix[y * size + x] = (0, 0, 0, 0)
    # 文字列 "K-HLSL" を 2 行(K-H / LSL ではなく "K-" "HLSL")で描く
    def text(s, x0, y0, scale, col):
        cx = x0
        for ch in s:
            g = FONT[ch]
            for gy, row in enumerate(g):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                px, py = cx + gx * scale + sx, y0 + gy * scale + sy
                                if 0 <= px < size and 0 <= py < size and pix[py * size + px][3]:
                                    pix[py * size + px] = col
            cx += 6 * scale
        return cx
    sc = max(2, size // 24)
    text('K-', size // 8, size // 5, sc * 2, accent)
    text('HLSL', size // 8, size // 5 + 9 * sc * 2 // 1, sc * 2 - (1 if size < 160 else 0), (220, 220, 220, 255))
    return pix


os.makedirs(os.path.join(ROOT, 'media'), exist_ok=True)
png(os.path.join(ROOT, 'media', 'icon.png'), 128, 128, draw(128))
png(os.path.join(ROOT, 'media', 'preview.png'), 200, 200, draw(200))
print('ok')
