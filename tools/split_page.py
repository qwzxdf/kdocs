import io
import os
import posixpath
import re
import shutil
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


def AddRating(key, rate):
    if rate is None:
        return
    path = os.path.join(ROOT, "ratings.yml")
    text = io.open(path, encoding="utf-8").read()
    if re.search(r"^%s:" % re.escape(key), text, re.M):
        return
    perf, quality = (list(rate) + [None, None])[:2]
    parts = []
    if perf:
        parts.append("perf: %d" % perf)
    if quality:
        parts.append("quality: %d" % quality)
    if not text.endswith("\n"):
        text += "\n"
    io.open(path, "w", encoding="utf-8", newline="").write(text + "%s: {%s}\n" % (key, ", ".join(parts)))


def DropRating(key):
    path = os.path.join(ROOT, "ratings.yml")
    lines = io.open(path, encoding="utf-8").read().split("\n")
    keep = [l for l in lines if not l.startswith(key + ":")]
    if len(keep) != len(lines):
        io.open(path, "w", encoding="utf-8", newline="").write("\n".join(keep))


def FixParentPages(spec):
    parent = os.path.join(DOCS, posixpath.dirname(spec["folder"]), ".pages")
    if not os.path.exists(parent):
        return
    name = posixpath.basename(spec["folder"])
    text = io.open(parent, encoding="utf-8", newline="").read()
    label = spec["pages"][0]["title"]
    new = re.sub(r"^(\s*-\s*)%s\.md[ \t]*(\r?)$" % re.escape(name), lambda m: "%s%s: %s%s" % (m.group(1), label, name, m.group(2)), text, flags=re.M)
    if new != text:
        io.open(parent, "w", encoding="utf-8", newline="").write(new)


def Table(rows, head=("ページ", "内容")):
    out = ["## ページ一覧", "", "| %s | %s |" % head, "| --- | --- |"]
    out += ["| [%s](%s) | %s |" % (t, f, d) for t, f, d in rows]
    return "\n".join(out)


ARCHIVE = os.path.join(os.environ.get("TEMP", "/tmp"), "kdocs_split_archive")


def Split(spec):
    source = os.path.join(DOCS, spec["source"])
    archive = os.path.join(ARCHIVE, spec["source"].replace("/", "__"))
    if not os.path.exists(source):
        source = archive
    sections = ReadSections(source)
    folder = os.path.join(DOCS, spec["folder"])
    os.makedirs(folder, exist_ok=True)
    nav = ["nav:"]
    for page in spec["pages"]:
        text = Render(page, sections, spec.get("tags", ["描画"]), posixpath.dirname(spec["source"]), spec["folder"], spec.get("refs"))
        io.open(os.path.join(folder, page["file"]), "w", encoding="utf-8", newline="").write(text)
        nav.append("  - %s" % page["file"])
        AddRating(posixpath.join(spec["folder"], page["file"]), page.get("rate"))
    io.open(os.path.join(folder, ".pages"), "w", encoding="utf-8", newline="").write("\n".join(nav) + "\n")
    FixParentPages(spec)
    DropRating(spec["source"])
    if os.path.exists(os.path.join(DOCS, spec["source"])):
        os.makedirs(ARCHIVE, exist_ok=True)
        shutil.move(os.path.join(DOCS, spec["source"]), archive)
    return [p["file"] for p in spec["pages"]]


REFS_DEFAULT = []


def Page(file, title, intro, tips, sections, extra="", mistakes=None, summary=None, refs=None, related=None, rate=None):
    return dict(rate=rate, file=file, title=title, intro=intro, tips=tips, sections=sections, extra=extra,
                mistakes=mistakes or [], summary=summary or [], refs=refs or REFS_DEFAULT, related=related or [])


def LoadSpec(path):
    ns = {"Page": Page, "Table": Table}
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
