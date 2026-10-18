"""描画ページの指標を集める: GPU コードが無いページ、コードが少ないページを出す。"""
import glob
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
rows = []
for f in glob.glob("docs/graphics/**/*.md", recursive=True):
    t = open(f, encoding="utf-8").read()
    t2 = re.sub(r"<svg.*?</svg>", "", t, flags=re.S)
    code = re.findall(r"```(\w*)[^\n]*\n(.*?)```", t2, flags=re.S)
    gpu = sum(1 for lang, body in code if lang in ("hlsl", "cpp", "glsl"))
    lines = sum(body.count("\n") for lang, body in code if lang in ("hlsl", "cpp", "glsl"))
    prose = len(re.sub(r"```.*?```", "", t2, flags=re.S))
    is_index = f.endswith("index.md") or "comparison" in f
    name = f.replace("docs/graphics/", "").replace(chr(92), "/")
    rows.append((name, prose, gpu, lines, is_index))

no = [r for r in rows if r[2] == 0 and not r[4]]
print("pages", len(rows), "no-gpu-code non-index", len(no))
for r in sorted(no, key=lambda r: r[1]):
    print(r[0], r[1])
print("---- few code (<15 lines), non-index")
for r in sorted([r for r in rows if r[2] > 0 and r[3] < 15 and not r[4]], key=lambda r: r[3]):
    print(r[0], r[1], r[2], r[3])
