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
"""

import os
import re

import yaml
from bs4 import BeautifulSoup, NavigableString
from mkdocs.utils import get_relative_url

_SKIP_PARENTS = {"a", "pre", "script", "style", "h1", "h2", "h3", "h4", "h5", "h6", "summary"}
_SKIP_CLASSES = {"page-badges", "mem", "md-nav", "headerlink"}
_ASCII_WORD = re.compile(r"[A-Za-z0-9_]")
_CODE_TITLE = re.compile(r"^(std::[\w:]+|<[\w]+>)$")

_text_terms = []   # [(term, src_path)] longest first
_term_to_src = {}
_compiled = []
_code_terms = {}   # normalized code name -> src_path


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
        for term in terms or []:
            term = str(term)
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

    def url_for(src):
        target = files.get_file_from_path(src)
        if target is None or target.src_uri == page.file.src_uri:
            return None
        return get_relative_url(target.url, page.url)

    def make_link(href, text=None):
        a = soup.new_tag("a", href=href)
        a["class"] = "autolink"
        if text is not None:
            a.string = text
        return a

    # 1. Inline code whose name is a known C++ name.
    for code in soup.find_all("code"):
        if _skipped(code):
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
        for node in list(soup.find_all(string=True)):
            if not isinstance(node, NavigableString) or node.parent.name == "code":
                continue
            if _skipped(node):
                continue
            text = str(node)
            pieces = []
            last = 0
            for m in pattern.finditer(text):
                src = _term_to_src[m.group(0)]
                if src in used:
                    continue
                href = url_for(src)
                if href is None:
                    continue
                used.add(src)
                pieces.append(text[last:m.start()])
                pieces.append(make_link(href, m.group(0)))
                last = m.end()
            if pieces:
                pieces.append(text[last:])
                node.replace_with(*pieces)

    return str(soup)
