"""ページを移動して、全ページのリンク・autolinks.yml・glossary.yml・redirects.yml を、まとめて直す。

使い方:
    python tools/move_pages.py tools/move_maps/<名前>.py --dry   移動せずに、件数だけ出す
    python tools/move_pages.py tools/move_maps/<名前>.py         実行する（git mv も行う）

マップのファイルには、次を書く。
    MOVES  = {"rendering/shadows.md": "graphics/shadows/cost.md", ...}   docs からの相対パス
    TITLES = {"graphics/shadows/cost.md": "Shadow Cost", ...}           移動後の title（省略可）

リンクは、移動前の場所を基準に解決して、移動後の場所から相対パスに直す。
アンカー（#...）は、そのまま残す。
"""
import io
import os
import posixpath
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
LINK = re.compile(r"(\]\()([^)\s#]+)(#[^)\s]*)?(\))")


def load_map(path):
    ns = {}
    exec(compile(io.open(path, encoding="utf-8").read(), path, "exec"), ns)
    return ns["MOVES"], ns.get("TITLES", {})


def read(p):
    raw = io.open(p, "rb").read().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def write(p, text, crlf):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def fix_links(text, old_rel, new_rel, moves, stats):
    old_dir = posixpath.dirname(old_rel)
    new_dir = posixpath.dirname(new_rel)

    def sub(m):
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith(("/", "#")):
            return m.group(0)
        tgt_old = posixpath.normpath(posixpath.join(old_dir, target))
        tgt_new = moves.get(tgt_old, tgt_old)
        rel = posixpath.relpath(tgt_new, new_dir)
        if rel == target:
            return m.group(0)
        stats["links"] += 1
        return m.group(1) + rel + (m.group(3) or "") + m.group(4)

    return LINK.sub(sub, text)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    dry = "--dry" in sys.argv
    moves, titles = load_map(sys.argv[1])
    stats = {"links": 0, "files": 0, "moved": 0}
    # 1. 全 md を読み込んで、リンクを直す
    results = {}
    for dirpath, _, files in os.walk(DOCS):
        for name in files:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            old_rel = os.path.relpath(full, DOCS).replace("\\", "/")
            new_rel = moves.get(old_rel, old_rel)
            text, crlf = read(full)
            new_text = fix_links(text, old_rel, new_rel, moves, stats)
            if new_rel in titles:
                new_text, n = re.subn(r"(?m)^title:.*$", "title: " + titles[new_rel], new_text, count=1)
                assert n == 1, new_rel
            results[old_rel] = (new_rel, new_text, crlf, new_text != text)
    changed = sum(1 for v in results.values() if v[3])
    print("links fixed: %d  files changed: %d  moved: %d" % (stats["links"], changed, len(moves)))
    missing = [o for o in moves if o not in results]
    if missing:
        print("見つからない:", missing)
        return 1
    if dry:
        return 0
    # 2. 書き出し（移動は git mv）
    for old_rel, (new_rel, new_text, crlf, ch) in results.items():
        if old_rel != new_rel:
            os.makedirs(os.path.dirname(os.path.join(DOCS, new_rel)), exist_ok=True)
            subprocess.check_call(["git", "mv", os.path.join("docs", old_rel), os.path.join("docs", new_rel)], cwd=ROOT)
            write(os.path.join(DOCS, new_rel), new_text, crlf)
        elif ch:
            write(os.path.join(DOCS, old_rel), new_text, crlf)
    # 3. autolinks.yml・glossary.yml
    for name, pat in (("autolinks.yml", r"(?m)^(\s*)([^\s:#][^:\n]*\.md)(#[^:\n]*)?(:)"),
                      ("glossary.yml", r"(?m)(link:\s*)([^\s#]+\.md)(#\S*)?()")):
        p = os.path.join(ROOT, name)
        text, crlf = read(p)

        def sub(m):
            tgt = m.group(2)
            new = moves.get(tgt, tgt)
            return m.group(1) + new + (m.group(3) or "") + m.group(4)

        new_text = re.sub(pat, sub, text)
        if new_text != text:
            write(p, new_text, crlf)
            print(name, "updated")
    # 4. redirects.yml
    p = os.path.join(ROOT, "redirects.yml")
    existing = {}
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8").read().splitlines():
            if ": " in line and not line.startswith("#"):
                k, v = line.split(": ", 1)
                existing[k.strip()] = v.strip()
    for old, new in moves.items():
        existing[old] = new
    # 連鎖を解く（A→B、B→C なら A→C）
    for k in list(existing):
        seen = 0
        while existing[k] in existing and seen < 5:
            existing[k] = existing[existing[k]]
            seen += 1
    lines = ["# 移動したページ（古いパス: 新しいパス）。hooks/redirects.py が、古い URL に転送ページを作る"]
    lines += ["%s: %s" % (k, existing[k]) for k in sorted(existing)]
    write(p, "\n".join(lines) + "\n", False)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
