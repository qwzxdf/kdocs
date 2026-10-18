"""記事の濃さの調査: セクションごとの、長さの中央値・薄いページ・TODO・コードの少ないページ。"""
import collections
import glob
import io
import re
import statistics
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BS = chr(92)
rows = []
for f in glob.glob("docs/**/*.md", recursive=True):
    n = f.replace(BS, "/").replace("docs/", "")
    if n.startswith(("javascripts", "stylesheets", "_")):
        continue
    t = open(f, encoding="utf-8").read().replace("\r\n", "\n")
    t = re.sub(r"<svg.*?</svg>", "", t, flags=re.S)
    code = len(re.findall(r"^```", t, re.M)) // 2
    prose = len(re.sub(r"```.*?```", "", t, flags=re.S))
    rows.append((n, len(t), prose, code, "TODO" in t))

sec = collections.defaultdict(list)
for r in rows:
    parts = r[0].split("/")
    key = "/".join(parts[:2]) if parts[0] in ("stl", "libs", "engine", "design") and len(parts) > 2 else parts[0]
    sec[key].append(r)

print("section | pages | median | thin(<4000, not index) | TODO | code-less(not index)")
for k, v in sorted(sec.items(), key=lambda kv: statistics.median([x[1] for x in kv[1]])):
    nonidx = [x for x in v if not x[0].endswith("index.md")]
    print(k, len(v), int(statistics.median([x[1] for x in v])),
          sum(1 for x in nonidx if x[1] < 4000), sum(1 for x in v if x[4]),
          sum(1 for x in nonidx if x[3] == 0))

print()
print("thinnest 40 (not index):")
for r in sorted([r for r in rows if not r[0].endswith("index.md")], key=lambda r: r[1])[:40]:
    print(r[1], r[3], "TODO" if r[4] else "", r[0])
