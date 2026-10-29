"""Turns known terms in page text into links to their explanation pages.

Terms come from two places:
  1. Page titles that look like C++ names (``std::vector``, ``<cmath>`` ...).
     They are registered automatically, so a new page is linkable as soon as
     it exists.
  2. ``autolinks.yml`` at the repository root, for Japanese terms and aliases.

Rules:
  - Only the first occurrence of each term on a page is linked.
  - A page never links to itself.
  - Text inside headings, existing links, code blocks and navigation is left
    alone. Inline code (``std::vector<int>``) is linked when its name matches.
  - Short lowercase STL names in autolinks.yml (``set``, ``list``) only match
    inline code, because they are also ordinary English words.
  - A target may carry an anchor (``basics/big-o.md#o1``).
  - Terms listed under ``_repeat`` in autolinks.yml (``O(1)`` ...) are linked on
    every occurrence, not only the first.
"""

import os
import re

import yaml
from bs4 import BeautifulSoup, NavigableString
from mkdocs.utils import get_relative_url

_SKIP_PARENTS = {"a", "pre", "script", "style", "h1", "h2", "h3", "h4", "h5", "h6", "summary"}
_SKIP_CLASSES = {"page-badges", "mem", "md-nav", "headerlink", "perf", "qual", "diff"}
_ASCII_WORD = re.compile(r"[A-Za-z0-9_]")
_CODE_TITLE = re.compile(r"^(std::[\w:]+|<[\w]+>)$")

_text_terms = []   # [(term, src_path)] longest first
_term_to_src = {}
_compiled = []
_code_terms = {}   # normalized code name -> src_path
_exact_terms = {}  # inline code text that is matched as a whole ("O(1)")
_repeat = set()


def _load_yaml(config):
    path = os.path.join(os.path.dirname(config["config_file_path"]), "autolinks.yml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _title_names(title):
    """'std::thread / std::jthread' -> ['std::thread', 'std::jthread']."""
    title = re.sub(r"[（(].*?[）)]", "", title).strip()
    names = []
    for part in title.split("/"):
        part = part.strip().replace("&lt;", "<").replace("&gt;", ">")
        if _CODE_TITLE.match(part):
            names.append(part)
    return names


def _normalize_code(text):
    """'std::vector<int>' -> 'std::vector', 'push_back()' -> 'push_back'."""
    text = text.strip()
    if not text.startswith("<"):
        text = text.split("<", 1)[0]
    text = text.split("(", 1)[0]
    return text.strip()


def _register_code(name, src):
    for key in {name, name.removeprefix("std::")}:
        if key and key not in _code_terms:
            _code_terms[key] = src


def on_files(files, config):
    _text_terms.clear()
    _code_terms.clear()
    _exact_terms.clear()
    _repeat.clear()

    for f in files.documentation_pages():
        if f.src_uri.startswith("_"):
            continue
        with open(f.abs_src_path, encoding="utf-8") as fp:
            head = fp.read(600)
        m = re.search(r"(?m)^title:\s*(.+)$", head)
        if m:
            for name in _title_names(m.group(1)):
                _register_code(name, f.src_uri)

    for src, terms in _load_yaml(config).items():
        if src == "_repeat":
            _repeat.update(str(t) for t in terms or [])
            continue
        for term in terms or []:
            term = str(term)
            if term in _repeat:
                _exact_terms[term] = src
            if _CODE_TITLE.match(term) or re.fullmatch(r"[\w:]+", term):
                _register_code(term, src)
            # Short STL names (set, list, map...) are ordinary English words too,
            # so they are linked only when written as inline code.
            if src.startswith("stl/") and re.fullmatch(r"[a-z_][a-z0-9_]*", term):
                continue
            _text_terms.append((term, src))

    _text_terms.sort(key=lambda t: len(t[0]), reverse=True)
    _term_to_src.clear()
    _term_to_src.update({term: src for term, src in _text_terms})
    _compiled.clear()
    return files


def _text_pattern():
    if not _compiled:
        parts = []
        for term, _ in _text_terms:
            escaped = re.escape(term)
            if term[0].isascii() and term[0].isalnum():
                escaped = rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])"
            elif re.fullmatch(r"[ァ-ヴー]+", term):
                escaped = r"(?<![ァ-ヴー])" + escaped
                if len(term) <= 3:
                    escaped += r"(?![ァ-ヴー])"
            parts.append(escaped)
        _compiled.append(re.compile("|".join(parts)) if parts else None)
    return _compiled[0]


def _skipped(node):
    for parent in node.parents:
        if parent.name in _SKIP_PARENTS:
            return True
        classes = parent.get("class") or []
        if any(c in _SKIP_CLASSES for c in classes):
            return True
    return False


def on_page_content(html, page, config, files):
    if page.file.src_uri.startswith("_"):
        return html
    soup = BeautifulSoup(html, "html.parser")
    used = set()

    def url_for(spec):
        path, _, anchor = spec.partition("#")
        target = files.get_file_from_path(path)
        if target is None or target.src_uri == page.file.src_uri:
            return None
        href = get_relative_url(target.url, page.url)
        return href + ("#" + anchor if anchor else "")

    def make_link(href, text=None):
        a = soup.new_tag("a", href=href)
        a["class"] = "autolink"
        if text is not None:
            a.string = text
        return a

    # 1. Inline code whose name is a known C++ name.
    for code in [t for t in soup.descendants if getattr(t, "name", None) == "code"]:
        if _skipped(code):
            continue
        exact = code.get_text().strip()
        if exact in _exact_terms:
            href = url_for(_exact_terms[exact])
            if href is not None:
                code.wrap(make_link(href))
            continue
        key = _normalize_code(code.get_text())
        src = _code_terms.get(key)
        if src is None or src in used:
            continue
        href = url_for(src)
        if href is None:
            continue
        used.add(src)
        code.wrap(make_link(href))

    # 2. Plain text terms: one pass over the text, one regex for all terms.
    pattern = _text_pattern()
    if pattern is not None:
        for node in [n for n in soup.descendants if isinstance(n, NavigableString)]:
            if not isinstance(node, NavigableString) or node.parent.name == "code":
                continue
            if _skipped(node):
                continue
            text = str(node)
            pieces = []
            last = 0
            for m in pattern.finditer(text):
                term = m.group(0)
                src = _term_to_src[term]
                repeat = term in _repeat
                if not repeat and src in used:
                    continue
                href = url_for(src)
                if href is None:
                    continue
                if not repeat:
                    used.add(src)
                pieces.append(text[last:m.start()])
                pieces.append(make_link(href, m.group(0)))
                last = m.end()
            if pieces:
                pieces.append(text[last:])
                node.replace_with(*pieces)

    return str(soup)


def on_page_markdown(markdown, page, config, files):
    """Boost pages named after a C++ entity so that `string` finds std::string first."""
    title = page.meta.get("title") or ""
    if _title_names(str(title)) or page.file.src_uri.startswith("stl/"):
        search = page.meta.get("search")
        if not isinstance(search, dict):
            search = {}
        search.setdefault("boost", 3)
        page.meta["search"] = search
    return markdown
