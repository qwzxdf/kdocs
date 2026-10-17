import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def Main():
    names = sys.argv[1:]
    images = []
    for n in names:
        im = Image.open(os.path.join(OUT, n + ".png")).convert("RGB")
        w, h = im.size
        im = im.resize((w * 62 // 100, h * 62 // 100), Image.LANCZOS)
        images.append(im)
    width = max(im.size[0] for im in images)
    height = sum(im.size[1] for im in images) + 6 * len(images)
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for im in images:
        sheet.paste(im, (0, y))
        y += im.size[1] + 6
    path = os.path.join(OUT, "_contact.png")
    sheet.save(path)
    print(path, sheet.size)


if __name__ == "__main__":
    Main()
