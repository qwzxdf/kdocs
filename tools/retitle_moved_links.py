"""移動したページへのリンクの文字が、古い題名のままなら、新しい題名にそろえる。
使い方: python tools/retitle_moved_links.py tools/move_maps/<名前>.py <古い題名の一覧.txt>
古い題名の一覧は「移動前のパス<TAB>古い題名」の行。"""
import io
import os
import posixpath
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s#]+\.md)(#[^)\s]*)?\)")


def main():
    ns = {}
    exec(compile(io.open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec"), ns)
    moves, titles = ns["MOVES"], ns["TITLES"]
    old_titles = {}
    for line in io.open(sys.argv[2], encoding="utf-8").read().splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            old_titles[moves[k]] = v.strip()
    n = files = 0
    for dp, _, fs in os.walk(DOCS):
        for name in fs:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dp, name)
            rel = os.path.relpath(full, DOCS).replace("\\", "/")
            raw = io.open(full, "rb").read().decode("utf-8")
            crlf = "\r\n" in raw
            text = raw.replace("\r\n", "\n")
            base = posixpath.dirname(rel)

            def sub(m):
                nonlocal n
                tgt = posixpath.normpath(posixpath.join(base, m.group(2)))
                if tgt in old_titles and m.group(1) == old_titles[tgt] and tgt in titles:
                    n += 1
                    return "[" + titles[tgt] + "](" + m.group(2) + (m.group(3) or "") + ")"
                return m.group(0)

            new = LINK.sub(sub, text)
            if new != text:
                files += 1
                io.open(full, "wb").write((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
    print("links retitled: %d  files: %d" % (n, files))


if __name__ == "__main__":
    main()
