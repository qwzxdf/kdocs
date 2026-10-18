import os
import re

import yaml
from mkdocs.utils import get_relative_url
from bs4 import BeautifulSoup, NavigableString

SKIP_TAGS = {"code", "pre", "a", "abbr", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style",
             "button", "summary", "svg", "textarea", "kbd"}
SKIP_CLASSES = {"anim", "page-badges", "admonition-title", "mat-row", "formula", "headerlink", "perf", "qual", "diff"}

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


def _group_key(term):
    c = term[0]
    if re.match(r"[0-9]", c) or not (c.isalpha() or "ぁ" <= c <= "ん" or "ァ" <= c <= "ヴ"):
        return ("0", "記号・数字")
    if re.match(r"[A-Za-z]", c):
        return ("1", c.upper())
    if "ァ" <= c <= "ヴ" or c == "ー":
        return ("2", _kana_row(c))
    if "ぁ" <= c <= "ん":
        return ("3", "ひらがな")
    return ("4", "漢字・その他")


_ROWS = [("ア行", "ァ", "オ"), ("カ行", "カ", "ゴ"), ("サ行", "サ", "ゾ"), ("タ行", "タ", "ド"),
         ("ナ行", "ナ", "ノ"), ("ハ行", "ハ", "ポ"), ("マ行", "マ", "モ"), ("ヤ行", "ャ", "ヨ"),
         ("ラ行", "ラ", "ロ"), ("ワ行", "ヮ", "ヴ")]


def _kana_row(c):
    for name, lo, hi in _ROWS:
        if lo <= c <= hi:
            return name
    return "ア行"


def _cell(text):
    return text.replace("|", "&#124;").replace("<", "&lt;")


def _label(text):
    return _cell(text).replace("*", "&#42;").replace("_", "&#95;")


def _glossary_markdown(config):
    path = os.path.join(os.path.dirname(config["config_file_path"]), "glossary.yml")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    groups = {}
    for entry in data:
        groups.setdefault(_group_key(entry["terms"][0]), []).append(entry)
    keys = sorted(groups)
    lines = [
        '<div class="glossary-tools"><input id="glossary-filter" type="search" placeholder="用語を絞り込む（例：ヒープ、SSAO）" aria-label="用語を絞り込む"></div>',
        "",
        " ・ ".join("[%s](#g-%d)" % (k[1], i) for i, k in enumerate(keys)),
        "",
    ]
    for i, key in enumerate(keys):
        lines.append("## %s {#g-%d}" % (key[1], i))
        lines.append("")
        lines.append("| 用語 | 説明 | 詳しく |")
        lines.append("| --- | --- | --- |")
        for entry in sorted(groups[key], key=lambda e: e["terms"][0].lower()):
            names = entry["terms"]
            label = "<strong>%s</strong>" % _label(names[0])
            if len(names) > 1:
                label += "<br><small>%s</small>" % "・".join(_label(n) for n in names[1:])
            link = entry.get("link")
            more = "[→](%s)" % link if link else ""
            lines.append("| %s | %s | %s |" % (label, _cell(entry["text"]), more))
        lines.append("")
    return "\n".join(lines)


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri != "glossary.md" or "{{GLOSSARY}}" not in markdown:
        return markdown
    return markdown.replace("{{GLOSSARY}}", _glossary_markdown(config))


def on_page_content(content, page, config, files):
    if page.file.src_uri == "glossary.md":
        return content
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
