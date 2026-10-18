"""長いコード ブロックを、数行ずつに割って、間に解説を入れる。
Split(path, key, cuts): key = 対象ブロックに含まれる行の一部(一意)。cuts = [(次の塊の先頭行の一部, 直前の塊の解説), ...]
最後の塊の解説は、元の文章が、そのまま続く。"""
import io
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "graphics")


def Split(path, key, cuts):
    full = os.path.join(ROOT, path)
    raw = io.open(full, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    L = raw.replace("\r\n", "\n").split("\n")
    start = end = None
    i = 0
    while i < len(L):
        if L[i].lstrip().startswith("```"):
            j = i + 1
            while not L[j].lstrip().startswith("```"):
                j += 1
            if any(key in x for x in L[i + 1:j]):
                start, end = i, j
                break
            i = j
        i += 1
    if start is None:
        raise SystemExit("block not found: %s %s" % (path, key))
    opener = L[start]
    body = L[start + 1:end]
    out = []
    pos = 0
    for marker, prose in cuts:
        k = next((n for n in range(pos + 1, len(body)) if marker in body[n]), None)
        if k is None:
            raise SystemExit("marker not found: %s %s" % (path, marker))
        chunk = body[pos:k]
        while chunk and chunk[-1].strip() == "":
            chunk.pop()
        out += [opener] + chunk + ["```", "", prose.strip(), ""]
        pos = k
        while pos < len(body) and body[pos].strip() == "":
            pos += 1
    out += [opener] + body[pos:] + ["```"]
    L[start:end + 1] = out
    text = "\n".join(L)
    io.open(full, "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
