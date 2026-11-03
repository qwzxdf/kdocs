"""指定したページの読点を減らして、1 文あたりの読点の数を前後で出す。

使い方: python tools/reduce_commas.py <ファイル>... [--dry]
目安は、1 文あたり 0.7 個以下（CLAUDE.md の「ページの質の基準」9）。減らしすぎた所は、手で戻す。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fix_commas as fc


def PerSentence(text):
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = re.sub(r"<svg.*?</svg>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return body.count("、") / max(1, body.count("。"))


def main():
    dry = "--dry" in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        t, crlf = fc.Read(p)
        new = fc.Process(t)
        print("%s: %.2f -> %.2f" % (os.path.basename(p), PerSentence(t), PerSentence(new)))
        if not dry and new != t:
            io.open(p, "wb").write((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))


main()
