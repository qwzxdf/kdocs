"""描画の「ページ一覧」・「関連ページ」の、ページへのリンクの文字を、そのページの題名(title)にそろえる。"""
import glob
import io
import posixpath
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
JA = re.compile(r"[ぁ-んァ-ヶ一-龥ー]")
titles = {}
for f in glob.glob("docs/**/*.md", recursive=True):
    p = f.replace(chr(92), "/")[5:]
    head = open(f, encoding="utf-8").read(600)
    m = re.search(r"^title:\s*(.+)$", head, re.M)
    if m:
        titles[p] = m.group(1).strip().strip('"')

ROW = re.compile(r"^(\|\s*)\[([^\]]+)\]\(([^)#\s]+\.md)\)")
ITEM = re.compile(r"^(\s*- )\[([^\]]+)\]\(([^)#\s]+\.md)\)")
n = 0
for f in sorted(glob.glob("docs/graphics/**/*.md", recursive=True)):
    p = f.replace(chr(92), "/")[5:]
    base = posixpath.dirname(p)
    raw = open(f, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    inc = False
    ch = False
    for i, l in enumerate(lines):
        if l.startswith("```"):
            inc = not inc
        if inc:
            continue
        m = ROW.match(l) or ITEM.match(l)
        if not m:
            continue
        text, target = m.group(2), posixpath.normpath(posixpath.join(base, m.group(3)))
        t = titles.get(target)
        if not t or not JA.search(text) or text == t:
            continue
        if re.search(r"[<*`]", text):
            continue
        lines[i] = l[:m.start(2)] + t + l[m.end(2):]
        ch = True
        n += 1
    if ch:
        s = "\n".join(lines)
        if crlf:
            s = s.replace("\n", "\r\n")
        open(f, "wb").write(s.encode("utf-8"))
print("置き換えたリンク", n)
