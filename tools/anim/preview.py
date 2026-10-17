import io
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def Preview(name, times, width, height, columns=2):
    svg = io.open(os.path.join(OUT, name + ".svg"), encoding="utf-8").read()
    svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d"' % (width, height), 1)
    cells = []
    for i, t in enumerate(times):
        cells.append('<div style="display:inline-block;margin:0;line-height:0">%s</div>' % svg.replace('data-fig="%s"' % name, 'data-fig="%s-%d"' % (name, i), 1).replace("id=\"arr-%s\"" % name, "id=\"arr-%s\"" % name))
    script = "var all=document.querySelectorAll('svg');var T=%s;all.forEach(function(s,i){s.pauseAnimations();s.setCurrentTime(T[i]);});" % list(times)
    cols_width = width * columns
    html = '<!doctype html><meta charset="utf-8"><body style="margin:0;width:%dpx">%s<script>%s</script>' % (cols_width, "".join(cells), script)
    path = os.path.join(OUT, name + ".preview.html")
    io.open(path, "w", encoding="utf-8").write(html)
    rows = (len(times) + columns - 1) // columns
    png = os.path.join(OUT, name + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=%d,%d" % (cols_width, height * rows),
                    "--virtual-time-budget=3000", "--screenshot=" + png, "file:///" + path.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return png


if __name__ == "__main__":
    name = sys.argv[1]
    width, height = int(sys.argv[2]), int(sys.argv[3])
    times = [float(v) for v in sys.argv[4:]]
    print(Preview(name, times, width, height))
