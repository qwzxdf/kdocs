import os
import re

import yaml
from bs4 import BeautifulSoup, NavigableString

SKIP_TAGS = {"code", "pre", "a", "abbr", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style",
             "button", "summary", "svg", "textarea", "kbd"}
SKIP_CLASSES = {"anim", "page-badges", "admonition-title", "mat-row", "formula", "headerlink"}

_entries = None


def _load(config):
    global _entries
    if _entries is not None:
        return _entries
    path = os.path.join(os.path.dirname(config["config_file_path"]), "glossary.yml")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    items = []
    for index, entry in enumerate(data):
        for term in entry["terms"]:
            items.append((term, index, entry["text"]))
    items.sort(key=lambda x: -len(x[0]))
    pattern_parts = []
    for term, index, text in items:
        escaped = re.escape(term)
        if re.fullmatch(r"[A-Za-z0-9_ .+-]+", term):
            escaped = r"(?<![A-Za-z0-9_])" + escaped + r"(?![A-Za-z0-9_])"
        pattern_parts.append(escaped)
    pattern = re.compile("|".join("(%s)" % p for p in pattern_parts))
    _entries = (pattern, items)
    return _entries


def _skipped(node):
    for parent in node.parents:
        name = getattr(parent, "name", None)
        if name in SKIP_TAGS:
            return True
        classes = parent.get("class") if hasattr(parent, "get") else None
        if classes and SKIP_CLASSES.intersection(classes):
            return True
    return False


def on_page_content(content, page, config, files):
    pattern, items = _load(config)
    soup = BeautifulSoup(content, "html.parser")
    used = set()
    changed = False
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString) or _skipped(node):
            continue
        text = str(node)
        pos = 0
        pieces = []
        for m in pattern.finditer(text):
            group = m.lastindex - 1
            _, index, description = items[group]
            if index in used:
                continue
            used.add(index)
            pieces.append(text[pos:m.start()])
            abbr = soup.new_tag("abbr", title=description)
            abbr["class"] = "glossary"
            abbr.string = m.group(0)
            pieces.append(abbr)
            pos = m.end()
        if not pieces:
            continue
        pieces.append(text[pos:])
        for piece in pieces:
            node.insert_before(NavigableString(piece) if isinstance(piece, str) else piece)
        node.extract()
        changed = True
    return str(soup) if changed else content
