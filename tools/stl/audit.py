"""FORMAT.md の最低条件を満たしているかを数える。使い方: python tools/stl/audit.py [--list] [folder ...]"""
import re
import sys
from pathlib import Path

STL = Path(__file__).resolve().parents[2] / "docs" / "stl"
MIN = {"must": 2000, "often": 2000, "sometimes": 1300, "rare": 700}


def sec(t, name):
    m = re.search(r"(?ms)^## " + re.escape(name) + r"\n(.*?)(?=^## |\Z)", t)
    return m.group(1) if m else None


def check(p):
    t = p.read_text(encoding="utf-8")
    rank = (re.search(r"rank-(\w+)", t) or [0, "rare"])[1]
    body = re.sub(r"```.*?```", "", t, flags=re.S)
    probs = []
    if len(body) < MIN.get(rank, 800):
        probs.append(f"短い({len(body)}<{MIN.get(rank, 800)})")
    m = re.search(r"</div>\n\n(.*?)\n\n!!! tip", t, re.S)
    intro = m.group(1) if m else ""
    if re.match(r"^`[^`]+`( は|\（)", intro) or re.match(r"^<strong>`", intro):
        probs.append("導入が定義文")
    if '!!! info' not in t:
        probs.append("読む前に無し")
    g = sec(t, "ゲームでの使いどころ")
    if g is not None and re.search(r"(?m)^\|", g):
        probs.append("ゲームが表")
    if g is None:
        probs.append("ゲーム無し")
    if t.count("??? failure") < 2:
        probs.append("ミス<2")
    mm = sec(t, "これだけ覚える")
    if mm is None or not 3 <= mm.count("- [x]") <= 5:
        probs.append("まとめ数")
    return rank, probs, len(body)


if __name__ == "__main__":
    lst = "--list" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--list"]
    files = []
    for a in (args or ["."]):
        b = STL / a
        files += sorted(b.rglob("*.md")) if b.is_dir() else [b]
    bad = 0
    tot = 0
    from collections import Counter
    c = Counter()
    for p in files:
        if p.name == "index.md" or p.parent == STL:
            continue
        tot += 1
        rank, probs, n = check(p)
        if probs:
            bad += 1
            for x in probs:
                c[x.split("(")[0]] += 1
            if lst:
                print(f"{p.relative_to(STL).as_posix()} [{rank}] {n}: {', '.join(probs)}")
    print(f"{tot} ページ中 {bad} ページが未達", dict(c))
