"""2 列の「見出し語 | 長い文」の表を、箇条書き・番号つきリストに直す（表の規則: CLAUDE.md）。

使い方: python tools/tables_to_lists.py <dir-or-file>... [--dry]
対象外: index.md、1 列目の半分以上がリンクの表、セルにパイプのエスケープを含む表、比較（3 列以上）。
"""
import glob
import os
import re
import sys

STEP = ("手順", "段階", "工程", "ステップ", "順序", "流れ")
SKIP_HEAD = ("ページ", "長所", "メリット", "利点", "関数", "名前", "型", "API")
SEP = re.compile(r"^\|[\s:|-]+\|?\s*$")


def convert(text):
    lines = text.split("\n")
    out, i, n, inc = [], 0, 0, False
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            inc = not inc
        if (not inc and l.startswith("|") and i + 1 < len(lines) and SEP.match(lines[i + 1])
                and not l.startswith("    ")):
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            block = lines[i:j]
            head = [c.strip() for c in block[0].strip().strip("|").split("|")]
            rows = [r.strip() for r in block[2:]]
            ok = len(head) == 2 and rows and not any(chr(92) + "|" in r for r in block)
            if ok:
                cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
                ok = all(len(c) == 2 for c in cells)
            if ok:
                links = sum(1 for c in cells if "](" in c[0])
                ok = links * 2 < len(cells) and not head[0].startswith(SKIP_HEAD) and "短所" not in head[1]
            if ok and any(len(c[1]) > 20 for c in cells):
                step = head[0].startswith(STEP)
                for k, (a, b) in enumerate(cells, 1):
                    body = "%s: %s" % (a, b) if a else b
                    out.append(("%d. " % k if step else "- ") + body)
                n += 1
                i = j
                continue
        out.append(l)
        i += 1
    return "\n".join(out), n


def main():
    dry = "--dry" in sys.argv
    files = []
    for a in sys.argv[1:]:
        if a.startswith("--"):
            continue
        files += [a] if a.endswith(".md") else glob.glob(os.path.join(a, "**", "*.md"), recursive=True)
    total = pages = 0
    for f in files:
        if f.replace("\\", "/").endswith("index.md"):
            continue
        raw = open(f, "rb").read().decode("utf-8")
        crlf = "\r\n" in raw
        new, n = convert(raw.replace("\r\n", "\n"))
        if n:
            total += n
            pages += 1
            if not dry:
                open(f, "wb").write((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
    print("tables: %d  pages: %d" % (total, pages))


main()
