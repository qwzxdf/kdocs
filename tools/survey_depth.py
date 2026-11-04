"""ページの質の指標を出して、点数が低い順（直す優先度が高い順）に並べる。

使い方: python tools/survey_depth.py [dir] [件数] [--all]
  dir   調べるフォルダ（既定は docs/graphics）。docs/stl は表の規則の対象外なので、除く。
  件数  表示する行数（既定 40）。
  --all index.md も含める（既定は除く）。

列
  sent   文の数（コードと SVG を除く。見本は約 200）
  svg    図の数（<svg>）と、動く図（class="anim"）の合計
  code   コード ブロックの行数 / コメントのある行の割合（%）
  tbl    表の行数（コードの外）。多いほど規則違反が疑わしい
  cm/s   1 文あたりの読点（目安 0.7 以下）
  ref    参考文献の節にある URL の数
  score  点数。低いほど優先して直す。完了の条件（CLAUDE.md の「ページの質の基準」）に近いほど高い
"""
import glob
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
root = args[0] if args else "docs/graphics"
limit = int(args[1]) if len(args) > 1 else 40
FENCE = re.compile(r"^(\s*)```[^\n]*\n(.*?)^\1```[ \t]*$", re.S | re.M)
COMMENT = re.compile(r"//|/\*|^\s*#\s|\s#\s|<!--")

rows = []
for f in glob.glob(root.rstrip("/") + "/**/*.md", recursive=True):
    f = f.replace(chr(92), "/")
    if f.startswith("docs/stl/") or (f.endswith("index.md") and "--all" not in sys.argv):
        continue
    t = open(f, encoding="utf-8").read().replace("\r\n", "\n")
    t = re.sub(r"^---\n.*?\n---\n", "", t, count=1, flags=re.S)
    svg = len(re.findall(r"<svg", t)) + len(re.findall(r'class="anim', t))
    t = re.sub(r"<svg.*?</svg>", "", t, flags=re.S)
    code_lines = cmt_lines = 0
    for m in FENCE.finditer(t):
        for l in m.group(2).split("\n"):
            if l.strip():
                code_lines += 1
                if COMMENT.search(l):
                    cmt_lines += 1
    body = FENCE.sub("", t)
    tbl = sum(1 for l in body.split("\n") if l.lstrip().startswith("|"))
    text = "\n".join(l for l in body.split("\n") if not l.lstrip().startswith(("|", "#", "<")))
    sent = text.count("。")
    commas = text.count("、")
    cps = commas / max(1, sent)
    tail = t.split("## 参考")[-1] if "## 参考" in t else ""
    refs = len(re.findall(r"https?://", tail))
    cmt_pct = 100 * cmt_lines // max(1, code_lines)
    score = (min(sent, 200) / 2                      # 文章量（200 文で 100 点）
             + min(svg, 2) * 15                      # 図（2 枚で 30 点）
             + min(code_lines, 100) * 0.3            # コード（100 行で 30 点）
             + min(cmt_pct, 60) * 0.2                # コメント率（60% で 12 点）
             + min(refs, 3) * 4                      # 参考文献（3 件で 12 点）
             - tbl * 0.5                             # 表の行（規則違反）
             - max(0.0, cps - 0.7) * 20)             # 読点の超過
    rows.append((round(score), f, sent, svg, code_lines, cmt_pct, tbl, round(cps, 2), refs))

rows.sort()
print("score file | sent svg code cmt%% tbl cm/s ref")
for r in rows[:limit]:
    print("%4d %s | %d %d %d %d%% %d %.2f %d" % r)
print("pages:", len(rows))
