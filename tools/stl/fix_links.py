"""分けたページへのリンクを、新しいページに付け替える。moves.json を使う。

  python tools/stl/fix_links.py          # docs 全体のリンクを書き換える
  python tools/stl/fix_links.py --check  # 消えたページ・存在しない .md へのリンクを一覧する
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
MOVES = json.loads((ROOT / "tools" / "stl" / "moves.json").read_text(encoding="utf-8"))
LINK = re.compile(r"\]\(([^)#\s]*\.md)(#[^)\s]*)?\)")


def rel(from_file, to_rel):
    return os.path.relpath(DOCS / to_rel, from_file.parent).replace("\\", "/")


def fix(path, check):
    text = path.read_text(encoding="utf-8")
    changed = [False]
    bad = []

    def sub(m):
        target, anchor = m.group(1), m.group(2) or ""
        if target.startswith("http"):
            return m.group(0)
        resolved = (path.parent / target).resolve()
        try:
            key = resolved.relative_to(DOCS.resolve()).as_posix()
        except ValueError:
            return m.group(0)
        info = MOVES.get(key)
        if info:
            aid = anchor[1:]
            new = info["ids"].get(aid)
            if new is None and not resolved.exists():
                new = info.get("default")
            if new and new != key:
                changed[0] = True
                return "](" + rel(path, new) + anchor + ")"
        if not resolved.exists():
            bad.append(m.group(0))
        return m.group(0)

    new_text = LINK.sub(sub, text)
    if check:
        return bad
    if changed[0]:
        path.write_text(new_text, encoding="utf-8", newline="")
        print("fixed", path.relative_to(ROOT).as_posix())
    return bad


if __name__ == "__main__":
    check = "--check" in sys.argv
    allbad = []
    for p in DOCS.rglob("*.md"):
        for b in fix(p, check):
            allbad.append((p.relative_to(ROOT).as_posix(), b))
    if allbad:
        print("存在しないリンク:")
        for f, b in allbad:
            print(" ", f, b)


# ---------------------------------------------------------------- 壊れた相対リンクの自動修復
def repair():
    """節を別のフォルダへ移したあとに壊れた相対リンクを、ファイル名の末尾（basics/xxx.md など）から探して直す。"""
    files = {}
    for p in DOCS.rglob("*.md"):
        rel_ = p.relative_to(DOCS).as_posix()
        files.setdefault(p.name, []).append(rel_)
    for path in DOCS.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        changed = [False]

        def sub(m):
            target, anchor = m.group(1), m.group(2) or ""
            if target.startswith("http"):
                return m.group(0)
            resolved = (path.parent / target).resolve()
            if resolved.exists():
                return m.group(0)
            tail = target.replace("\\", "/")
            while tail.startswith("../") or tail.startswith("./"):
                tail = tail.split("/", 1)[1]
            cands = [c for c in files.get(Path(tail).name, []) if ("/" + c).endswith("/" + tail)]
            if len(cands) != 1:
                # 分けたページ（moves）から探す
                for key, info in MOVES.items():
                    if ("/" + key).endswith("/" + tail):
                        new = info["ids"].get(anchor[1:]) or info.get("default")
                        if new and (DOCS / new).exists():
                            cands = [new]
                            break
            if len(cands) == 1:
                changed[0] = True
                return "](" + rel(path, cands[0]) + anchor + ")"
            return m.group(0)

        new_text = LINK.sub(sub, text)
        if changed[0]:
            path.write_text(new_text, encoding="utf-8", newline="")
            print("repaired", path.relative_to(ROOT).as_posix())


if __name__ == "__main__" and "--repair" in sys.argv:
    repair()
