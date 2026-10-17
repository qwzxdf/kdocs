import io
import os
import posixpath
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def ReadSections(path):
    text = io.open(path, encoding="utf-8").read()
    if text.startswith("---"):
        end = text.index("\n---", 3)
        text = text[end + 4:].lstrip("\n")
    lines = text.split("\n")
    sections = []
    current = None
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            current = {"title": line[3:].strip(), "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    return sections


def Find(sections, key):
    for s in sections:
        if s["title"].startswith(key):
            return s
    raise KeyError("section not found: %s" % key)


LINK = re.compile(r"(\]\()([^)\s#]+)(#[^)\s]*)?(\))")


def RebaseLinks(body, old_dir, new_dir):
    def Sub(m):
        target = m.group(2)
        if re.match(r"^[a-z]+:", target) or target.startswith("#") or not target.endswith(".md"):
            return m.group(0)
        absolute = posixpath.normpath(posixpath.join(old_dir, target))
        return m.group(1) + posixpath.relpath(absolute, new_dir) + (m.group(3) or "") + m.group(4)
    return LINK.sub(Sub, body)


def Render(page, sections, tags, old_dir="", new_dir="", default_refs=None):
    out = ["---", "title: %s" % page["title"], "tags:"]
    for t in tags:
        out.append("  - %s" % t)
    out += ["---", "", "# %s" % page["title"], "", page["intro"].strip(), ""]
    if page.get("tips"):
        out += ['!!! tip "ポイント"']
        out += ["    - %s" % t for t in page["tips"]]
        out.append("")
    for key in page.get("sections", []):
        if isinstance(key, tuple):
            key, new_title = key
        else:
            new_title = None
        s = Find(sections, key)
        out.append("## %s" % (new_title or s["title"]))
        body = "\n".join(s["lines"]).strip("\n")
        if old_dir != new_dir:
            body = RebaseLinks(body, old_dir, new_dir)
        out.append(body)
        out.append("")
    if page.get("extra"):
        out.append(page["extra"].strip("\n"))
        out.append("")
    if page.get("mistakes"):
        out.append("## よくあるミス")
        out.append("")
        for title, body in page["mistakes"]:
            out.append('??? failure "%s"' % title)
            out.append("    %s" % body)
            out.append("")
    if page.get("summary"):
        out += ["## これだけ覚える", "", '!!! abstract "まとめ"']
        out += ["    - [x] %s" % t for t in page["summary"]]
        out.append("")
    refs = page.get("refs") or default_refs
    if refs:
        out += ["## 参考", ""]
        out += ["- %s" % r for r in refs]
        out.append("")
    if page.get("related"):
        out += ["## 関連ページ", ""]
        out += ["- [%s](%s)" % (t, l) for t, l in page["related"]]
        out.append("")
    return "\n".join(out)


def Split(spec):
    source = os.path.join(DOCS, spec["source"])
    if not os.path.exists(source):
        for fallback in ("C:/Users/mega/AppData/Local/Temp/old_sh", "C:/Users/mega/AppData/Local/Temp/old_ao", "C:/Users/mega/AppData/Local/Temp/old_split"):
            alt = os.path.join(fallback, os.path.basename(spec["source"]))
            if os.path.exists(alt):
                source = alt
                break
    sections = ReadSections(source)
    folder = os.path.join(DOCS, spec["folder"])
    os.makedirs(folder, exist_ok=True)
    nav = ["nav:"]
    for page in spec["pages"]:
        text = Render(page, sections, spec.get("tags", ["描画"]), posixpath.dirname(spec["source"]), spec["folder"], spec.get("refs"))
        io.open(os.path.join(folder, page["file"]), "w", encoding="utf-8", newline="").write(text)
        nav.append("  - %s" % page["file"])
    io.open(os.path.join(folder, ".pages"), "w", encoding="utf-8", newline="").write("\n".join(nav) + "\n")
    return [p["file"] for p in spec["pages"]]


REFS_DEFAULT = []


def Page(file, title, intro, tips, sections, extra="", mistakes=None, summary=None, refs=None, related=None):
    return dict(file=file, title=title, intro=intro, tips=tips, sections=sections, extra=extra,
                mistakes=mistakes or [], summary=summary or [], refs=refs or REFS_DEFAULT, related=related or [])


def LoadSpec(path):
    ns = {"Page": Page}
    exec(compile(io.open(path, encoding="utf-8").read(), path, "exec"), ns)
    specs = ns["SPECS"]
    for spec in specs:
        if "refs" not in spec and ns.get("DEFAULT_REFS"):
            spec["refs"] = ns["DEFAULT_REFS"]
    return specs


if __name__ == "__main__":
    specs = []
    for path in sys.argv[1:]:
        specs += LoadSpec(path)
    for spec in specs:
        files = Split(spec)
        print(spec["folder"], len(files), "pages")
