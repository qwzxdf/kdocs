"""STL ページの front matter の title / summary を、YAML として安全になるよう引用符で囲む。"""
import glob
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BS = chr(92)
DQ = chr(34)


def quote(v):
    if v.startswith(DQ) and v.endswith(DQ):
        return v
    return DQ + v.replace(BS, BS + BS).replace(DQ, BS + DQ) + DQ


def main():
    fixed = 0
    for p in glob.glob(str(ROOT / "docs" / "stl" / "**" / "*.md"), recursive=True):
        text = Path(p).read_text(encoding="utf-8")
        m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        block = m.group(1)
        nb = re.sub(r"(?m)^(summary): (.*)$", lambda mm: f"{mm.group(1)}: {quote(mm.group(2))}", block)
        if nb != block:
            text = text.replace(block, nb, 1)
            Path(p).write_text(text, encoding="utf-8", newline="")
            fixed += 1
        yaml.safe_load(nb)
    print("quoted", fixed)


if __name__ == "__main__":
    main()
