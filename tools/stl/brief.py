"""ページの要点（題・要約・導入・ポイント・関数の見出し・サンプルの長さ）を短く出す。書き直しの下調べ用。"""
import re
import sys
from pathlib import Path

STL = Path(__file__).resolve().parents[2] / "docs" / "stl"


def brief(p, full=False):
    t = p.read_text(encoding="utf-8")
    rank = (re.search(r"rank-(\w+)", t) or [0, "?"])[1]
    title = re.search(r"^title: (.*)", t, re.M).group(1)
    summ = re.search(r"^summary: \"?(.*?)\"?$", t, re.M).group(1)
    m = re.search(r"</div>\n\n(.*?)\n\n!!! tip", t, re.S)
    intro = m.group(1).replace("\n", " ") if m else ""
    fns = [m.group(2) or re.sub(r"\s*<span.*", "", m.group(1)) for m in re.finditer(r"(?m)^### (.*?)(?: \{#([\w-]+)[^}]*\})?$", t)]
    tips = re.findall(r"(?m)^    - (.*)$", t.split("!!! tip", 1)[-1].split("##", 1)[0]) if "!!! tip" in t else []
    code = re.findall(r"```cpp\n(.*?)```", t, re.S)
    out = re.findall(r"```text[^\n]*\n(.*?)```", t, re.S)
    nm = p.relative_to(STL).as_posix()
    s = f"## {nm} [{rank}] {title} :: {summ}\n  intro: {intro[:220]}\n  fns: {', '.join(fns)[:200]}\n  tips: {' / '.join(tips)[:240]}"
    if full:
        s += "\n  code: " + " ## ".join(c.strip().replace("\n", "⏎")[:300] for c in code[:2])
        s += "\n  out: " + " ## ".join(o.strip().replace("\n", "⏎")[:80] for o in out[:2])
    return s


if __name__ == "__main__":
    full = "--full" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--full"]
    for a in args:
        base = STL / a
        files = sorted(base.rglob("*.md")) if base.is_dir() else [base]
        for p in files:
            if p.name == "index.md":
                continue
            print(brief(p, full))
