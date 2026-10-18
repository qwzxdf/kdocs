"""描画ページの加筆用ヘルパ。

  Add(path, md, before)   見出し(before)の直前に md を差し込む。同じ見出しが既にあれば、何もしない
  Refs(path, lines)       「## 参考」を、lines で置き換える
  Dedup(path)             連続した同じ段落を 1 つにする
  path は docs/graphics からの相対パス(例 "terrain/lod/cdlod.md")
"""
import io
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "graphics")


def Load(path):
    raw = io.open(os.path.join(ROOT, path), "rb").read().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def Save(path, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    io.open(os.path.join(ROOT, path), "wb").write(text.encode("utf-8"))


def Add(path, md, before="## よくあるミス", key=None):
    text, crlf = Load(path)
    md = md.strip("\n") + "\n\n"
    first = md.split("\n", 1)[0]
    if (key or first) in text:
        return False
    i = text.find("\n" + before)
    if i < 0:
        for alt in ("## これだけ覚える", "## 参考", "## 関連ページ"):
            i = text.find("\n" + alt)
            if i >= 0:
                break
    if i < 0:
        raise SystemExit("見出しが無い: %s %s" % (path, before))
    text = text[:i + 1] + md + text[i + 1:]
    Save(path, text, crlf)
    return True


def Refs(path, lines):
    text, crlf = Load(path)
    block = "## 参考\n\n" + "\n".join("- " + l for l in lines) + "\n"
    m = re.search(r"## 参考\n\n(?:- .*\n?)+", text)
    if m:
        text = text[:m.start()] + block + text[m.end():]
    else:
        i = text.find("\n## 関連ページ")
        text = text[:i + 1] + block + "\n" + text[i + 1:]
    Save(path, text, crlf)


def Dedup(path):
    text, crlf = Load(path)
    paras = text.split("\n\n")
    out = []
    for p in paras:
        if out and p.strip() and p == out[-1] and not p.startswith(("```", "|", "<")):
            continue
        out.append(p)
    s = "\n\n".join(out)
    s = re.sub(r"\n{4,}", "\n\n\n", s)
    if s != text:
        Save(path, s, crlf)
