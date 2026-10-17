import io
import os
import posixpath
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
LINK = re.compile(r"(\]\()([^)\s#]+\.md)(#[^)\s]*)?(\))")

# 古いページ → 新しいページ（フォルダの index）
MOVED = {}
# 用語集で、用語に応じて、さらに細かいページへ振り分ける:(古いページ, [(用語に含まれる語, 新しいページ)])
GLOSSARY_OVERRIDES = {}


def Load(module_name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retarget_maps", module_name + ".py")
    ns = {}
    exec(compile(io.open(path, encoding="utf-8").read(), path, "exec"), ns)
    MOVED.update(ns.get("MOVED", {}))
    for k, v in ns.get("GLOSSARY", {}).items():
        GLOSSARY_OVERRIDES.setdefault(k, []).extend(v)


def RelLink(from_file, target_docs_path):
    base = posixpath.dirname(from_file)
    return posixpath.relpath(target_docs_path, base)


def FixMarkdown():
    changed = 0
    for dirpath, _, files in os.walk(DOCS):
        for name in files:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, DOCS).replace("\\", "/")
            text = io.open(full, encoding="utf-8").read()

            def Sub(m):
                target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), m.group(2)))
                if target in MOVED:
                    return m.group(1) + RelLink(rel, MOVED[target]) + m.group(4)
                return m.group(0)

            new = LINK.sub(Sub, text)
            if new != text:
                io.open(full, "w", encoding="utf-8", newline="").write(new)
                changed += 1
    return changed


def FixGlossary(path):
    lines = io.open(path, encoding="utf-8").read().split("\n")
    out = []
    terms_line = ""
    changed = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- terms:"):
            terms_line = stripped
        m = re.match(r"^(\s*link:\s*)(\S+\.md)(\S*)\s*$", line)
        if m and m.group(2) in MOVED:
            old = m.group(2)
            new = MOVED[old]
            for needle, target in GLOSSARY_OVERRIDES.get(old, []):
                if needle in terms_line:
                    new = target
                    break
            line = m.group(1) + new
            changed += 1
        out.append(line)
    io.open(path, "w", encoding="utf-8", newline="").write("\n".join(out))
    return changed


if __name__ == "__main__":
    for module in sys.argv[1:]:
        Load(module)
    print("markdown files changed:", FixMarkdown())
    for name in ("glossary.yml", "autolinks.yml"):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            print(name, "lines changed:", FixGlossary(p))
