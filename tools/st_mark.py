"""スクリーンショットに、番号つきの赤い枠を描く（docs/git/img/）。

初心者が「画像のどこを見ればいいか」を迷わないための印。本体ウィンドウを 1200 × 800 で撮った画像用。
座標は、その画像の中のピクセル。一度だけ実行する（もう一度実行すると、同じ枠がもう一度描かれるだけ）。
使い方: python tools/st_mark.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMG = Path(__file__).resolve().parent.parent / 'docs' / 'git' / 'img'
RED = (220, 38, 38)

TOOLBAR = (4, 58, 1196, 114)
SIDEBAR = (4, 120, 211, 445)
LIST = (214, 118, 1196, 466)
DETAIL = (214, 470, 1196, 796)
UPPER = (214, 145, 704, 406)      # Index にステージしたファイル
LOWER = (214, 409, 704, 668)      # 作業ツリーのファイル
DIFF = (708, 145, 1196, 668)
COMMIT = (214, 672, 1196, 796)

STATUS = [(UPPER, 1), (LOWER, 2), (DIFF, 3), (COMMIT, 4)]
MARKS = {
    'st-history': [(TOOLBAR, 1), (SIDEBAR, 2), (LIST, 3), (DETAIL, 4)],
    'st-status-unstaged': STATUS,
    'st-status-staged': STATUS,
    'st-commit-message': STATUS,
    'st-first-status': STATUS,
    'st-first-staged': STATUS,
    'st-first-message': STATUS,
    'st-conflict-status': STATUS,
    'st-search': [((214, 117, 1068, 143), 1, (180, 130)), ((1098, 119, 1197, 143), 2, (1085, 160)), ((214, 146, 1196, 456), 3)],
}


def draw(name, boxes):
    p = IMG / f'{name}.png'
    im = Image.open(p).convert('RGB')
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype('arialbd.ttf', 20)
    for b in boxes:
        (x0, y0, x1, y1), n = b[0], b[1]
        d.rectangle((x0, y0, x1, y1), outline=RED, width=3)
        r = 14
        cx, cy = x1 - r - 6, y1 - r - 6          # 枠の右下の内側（見出しやボタンに重ならない）
        if len(b) == 3:
            cx, cy = b[2]
        elif (x0, y0, x1, y1) == COMMIT:
            cx, cy = 900, 768                       # 右下の「コミット」ボタンに重ならない所
        if name == 'st-history' and n == 1:
            cx, cy = 640, 86                        # ツールバーは、左右のボタンの間の空きに置く
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED)
        d.text((cx, cy), str(n), fill='white', font=font, anchor='mm')
    im.quantize(colors=256, dither=Image.Dither.NONE).save(p, optimize=True)
    print(name, len(boxes))


if __name__ == '__main__':
    for k, v in MARKS.items():
        if k != 'st-search' and '--all' not in __import__('sys').argv:
            continue
        draw(k, v)
