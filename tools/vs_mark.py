"""原画（tools/vs_raw）から、切り出しと赤枠つきの画像を docs/vs/img に作る。撮り直さずに、枠だけ直せる。使い方: python tools/vs_mark.py"""
from PIL import Image
from vs_lib import RAW, OUT, mark

def raw(n): return Image.open(RAW / f'{n}.png').convert('RGB')

def put(name, img, marks=()):
    out = mark(img, marks) if marks else img
    out.save(OUT / f'{name}.png', optimize=True); print(name, out.size)

# (出力名, 原画, 切り出し(x0,y0,x1,y1) か None, 枠 (切り出し後の座標))
JOBS = [
    ('first-break', 'debug-break', None,
     [(0, 466, 1545, 496), (0, 812, 935, 1000), (940, 812, 1880, 1000), (488, 26, 578, 48)]),
    ('debug-autos', 'debug-break', (0, 812, 935, 1000), []),
    ('debug-callstack', 'debug-break', (940, 812, 1880, 1000), []),
    ('first-toolbar', 'error-list-c1083', (0, 18, 700, 56), [(310, 4, 392, 34), (396, 4, 482, 34), (485, 4, 690, 34)]),
    ('toolbar-config', 'error-list-c1083', (0, 18, 700, 56), []),
    ('cmake-preset-dropdown', 'cmake-folder', (300, 18, 900, 56), [(146, 5, 348, 33)]),
    ('error-list-c1083', 'error-list-c1083', None, [(0, 825, 1560, 940)]),
    ('error-list-lnk2019', 'error-list-lnk2019', None, [(0, 1875 - 1024 + 36, 1560, 1875 - 1024 + 140)]),
    ('props-cmdline', 'props-cmdline', None, [(232, 545, 1075, 645)]),
    ('props-cpp-standard', 'props-cpp-standard', None, [(586, 143, 1080, 163)]),
    ('props-general', 'props-general', None, [(15, 42, 455, 68), (460, 42, 945, 68)]),
]

if __name__ == '__main__':
    for name, src, crop, marks in JOBS:
        im = raw(src)
        if crop: im = im.crop(crop)
        put(name, im, marks)
