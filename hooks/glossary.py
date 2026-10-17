import os
import re

import yaml
from mkdocs.utils import get_relative_url
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
            items.append((term, index, entry["text"], entry.get("link")))
    items.sort(key=lambda x: -len(x[0]))
    pattern_parts = []
    for term, index, text, link in items:
        escaped = re.escape(term)
        if re.fullmatch(r"[A-Za-z0-9_ .+-]+", term):
            escaped = r"(?<![A-Za-z0-9_])" + escaped + r"(?![A-Za-z0-9_])"
        elif re.fullmatch(r"[ァ-ヴー]+", term):
            escaped = r"(?<![ァ-ヴー])" + escaped
            if len(term) <= 3:
                escaped += r"(?![ァ-ヴー])"
        pattern_parts.append(escaped)
    _entries = (pattern_parts, items)
    return _entries


_sub_cache = {}


def _sub_pattern(parts, candidates):
    pat = _sub_cache.get(candidates)
    if pat is None:
        pat = re.compile("|".join("(%s)" % parts[i] for i in candidates))
        _sub_cache[candidates] = pat
    return pat


def _skipped(node):
    for parent in node.parents:
        name = getattr(parent, "name", None)
        if name == "a" and "autolink" in (parent.get("class") or []):
            continue
        if name in SKIP_TAGS:
            return True
        classes = parent.get("class") if hasattr(parent, "get") else None
        if classes and SKIP_CLASSES.intersection(classes):
            return True
    return False


def _in_autolink(node):
    for parent in node.parents:
        if getattr(parent, "name", None) == "a":
            return True
    return False


def _href(spec, page, files):
    path, _, anchor = spec.partition("#")
    target = files.get_file_from_path(path)
    if target is None or target.src_uri == page.file.src_uri:
        return None
    return get_relative_url(target.url, page.url) + ("#" + anchor if anchor else "")


def on_page_content(content, page, config, files):
    parts, items = _load(config)
    soup = BeautifulSoup(content, "html.parser")
    used = set()
    changed = False
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString) or _skipped(node):
            continue
        text = str(node)
        candidates = tuple(i for i, item in enumerate(items) if item[0] in text)
        if not candidates:
            continue
        pattern = _sub_pattern(parts, candidates)
        pos = 0
        pieces = []
        for m in pattern.finditer(text):
            group = candidates[m.lastindex - 1]
            _, index, description, link = items[group]
            if index in used:
                continue
            used.add(index)
            pieces.append(text[pos:m.start()])
            abbr = soup.new_tag("abbr", title=description)
            abbr["class"] = "glossary"
            abbr.string = m.group(0)
            href = _href(link, page, files) if link and not _in_autolink(node) else None
            if href:
                anchor = soup.new_tag("a", href=href)
                anchor["class"] = "glossary-link"
                anchor.append(abbr)
                pieces.append(anchor)
            else:
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
