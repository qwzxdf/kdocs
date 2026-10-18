"""太字の整理。

  1. 描画(docs/graphics)では、太字を減らす
       - 見出し・表・箇条書きの太字は、はずす
       - 普通の段落では、1 行に 2 つまで残す
  2. 残った太字は、すべて <strong>…</strong> に直す(「）」の後ろに日本語が続くと、** が、そのまま、出るため)
  3. 描画以外の docs でも、** が、残っていれば、<strong> に直す(減らさない)

コード ブロック、インライン コード、図(<!-- fig: … -->)、HTML 行は、触らない。
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
CODE = re.compile(r"`[^`\n]*`")
BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")


def Process(line, reduce):
    stripped = line.lstrip()
    is_table = stripped.startswith("|")
    is_list = re.match(r"\s*(?:[-*]|\d+\.)\s", line) is not None or re.match(r"\s*- \[[ x]\]", line) is not None
    is_heading = stripped.startswith("#")
    codes = []

    def Hide(m):
        codes.append(m.group(0))
        return "\x00%d\x00" % (len(codes) - 1)

    work = CODE.sub(Hide, line)
    count = [0]

    def Repl(m):
        count[0] += 1
        if reduce and (is_table or is_list or is_heading or count[0] > 2):
            return m.group(1)
        return "<strong>%s</strong>" % m.group(1)

    work = BOLD.sub(Repl, work)
    for i, c in enumerate(codes):
        work = work.replace("\x00%d\x00" % i, c)
    return work


def Run(path, reduce):
    raw = io.open(path, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    out = []
    in_fence = False
    in_fig = False
    for line in lines:
        s = line.lstrip()
        if s.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if "<!-- fig:" in line and ":begin" in line:
            in_fig = True
        if in_fence or in_fig or (s.startswith("<") and not s.startswith("<strong>")) or "**" not in line:
            out.append(line)
        else:
            out.append(Process(line, reduce))
        if "<!-- fig:" in line and ":end" in line:
            in_fig = False
    text = "\n".join(out)
    if text != raw.replace("\r\n", "\n"):
        io.open(path, "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
        return True
    return False


# 引数が無ければ docs/graphics だけ。あれば、docs からの相対パスのファイルだけ(減らさずに、直す)。
n = 0
if len(sys.argv) > 1:
    for rel in sys.argv[1:]:
        if Run(os.path.join(ROOT, rel), reduce=rel.startswith("graphics/")):
            n += 1
else:
    for f in glob.glob(os.path.join(ROOT, "graphics", "**", "*.md"), recursive=True):
        if Run(f, reduce=True):
            n += 1
print("changed", n)
