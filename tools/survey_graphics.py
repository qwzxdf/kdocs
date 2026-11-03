"""graphics/ の各ページを、質の基準（CLAUDE.md）で点数にして、低い順に並べる。

使い方: python tools/survey_graphics.py [dir] [件数]
点数が低いほど、直す優先度が高い。
"""
import glob
import re
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "docs/graphics"
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 40
rows = []
for f in glob.glob(root + "/**/*.md", recursive=True):
    f = f.replace(chr(92), "/")
    if f.endswith("index.md"):
        continue
    L = open(f, encoding="utf-8").read().split("\n")
    inc, code, prose, tbl, cmt, codeln = False, 0, 0, 0, 0, 0
    for l in L:
        if l.lstrip().startswith("```"):
            inc = not inc
            continue
        if inc:
            codeln += 1
            if "//" in l:
                cmt += 1
        elif l.startswith("|"):
            tbl += 1
        elif l.strip() and not l.startswith("#"):
            prose += len(l)
    text = "\n".join(L)
    refs = len(re.findall(r"https?://", text.split("## 参考")[-1])) if "## 参考" in text else 0
    commas = text.count("、") / max(1, prose / 100)
    score = prose / 100 + cmt * 0.3 + refs * 3 - tbl * 0.5 - commas * 2
    rows.append((round(score), f, len(L), prose // 100, tbl, codeln, cmt, refs))
rows.sort()
print("score file lines prose/100 tableLines codeLines comments refs")
for r in rows[:limit]:
    print(*r)
print("pages:", len(rows))
