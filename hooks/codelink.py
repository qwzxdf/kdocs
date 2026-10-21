"""Colors identifiers in code blocks (VS Dark+ / Viasfora style) and links API names.

Pygments marks most C++ identifiers as plain names (``n``). This hook looks at the
neighbouring tokens and re-labels each identifier as a type, function, macro,
enumerator, namespace or variable, so that CSS can color them like Visual Studio.
It also colors nested brackets by depth (rainbow, like Viasfora).

An identifier is turned into a link when its name is registered. Names come from:
  1. ``###`` / ``####`` headings that are a single identifier (``### D3D12CreateDevice``)
     or ``Class::Method``. The anchor is the heading's ``{#id}`` or its slug.
  2. ``api:`` in a page's front matter (the page itself explains these names).
  3. ``autolinks.yml`` entries that are plain identifiers.

Rules:
  - Links are made only on pages under ``LINK_SCOPE`` and point only into ``LINK_SCOPE``.
  - ``directx/dx11`` and ``directx/dx12`` never link to each other (``SHARED`` and
    ``directx/concepts`` are reachable from both).
  - In one code block, a name is linked only the first time.
"""

import os
import re

import yaml
from bs4 import BeautifulSoup
from mkdocs.utils import get_relative_url

LINK_SCOPE = ("directx/",)
SHARED = {"directx/dx11/dxgi.md"}
LANGS = ("language-cpp", "language-c", "language-hlsl", "language-cuda")

CONTROL = {
    "if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue",
    "return", "goto", "try", "catch", "throw", "co_return", "co_yield", "co_await",
}
KEYWORDS_EXTRA = {"__uuidof", "__declspec", "__stdcall", "__cdecl", "__forceinline", "__vectorcall"}
WIN_TYPES = {
    "UINT", "UINT8", "UINT16", "UINT32", "UINT64", "INT", "INT8", "INT16", "INT32", "INT64",
    "HRESULT", "BOOL", "BYTE", "WORD", "DWORD", "QWORD", "WCHAR", "CHAR", "LPCWSTR", "LPWSTR",
    "LPCSTR", "LPSTR", "LPVOID", "LPCVOID", "PVOID", "HANDLE", "HWND", "HINSTANCE", "HMODULE",
    "LRESULT", "WPARAM", "LPARAM", "RECT", "POINT", "SIZE", "REFIID", "REFGUID", "GUID", "IID",
    "FLOAT", "DOUBLE", "SIZE_T", "UINT_PTR", "LONG", "ULONG", "LONG_PTR", "ATOM", "MSG",
    "LARGE_INTEGER", "FILETIME", "LUID", "WNDCLASSEX", "WNDCLASS", "PAINTSTRUCT", "TCHAR",
}
TYPE_SUFFIX = re.compile(r"_(DESC\d*|DATA(_\w+)?|PARAMETER\d*|RANGE\d*|INFO\d*|BOX|VIEWPORT|MAPPED_SUBRESOURCE"
                         r"|FOOTPRINT\w*|REGION\w*|BARRIER\w*|STATE_SUBOBJECT|PROPERTIES|ELEMENT_DESC)$")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9_]*$")
PASCAL = re.compile(r"^[A-Z][a-z0-9]")
INTERFACE = re.compile(r"^I[A-Z][A-Za-z0-9]+$")
ENUM_K = re.compile(r"^k[A-Z]\w*$")
BRACKETS = {"(": 1, "[": 1, "{": 1, ")": -1, "]": -1, "}": -1}
NAME_CLASSES = ("n", "nf", "nc", "nv", "no", "nb", "nl", "nn", "nx", "nd", "bp", "vc", "py")

_registry = {}  # name or "Type::Method" -> [(src_uri, anchor or None)]
_bare = {}      # method name -> [(src_uri, anchor)]  (used only when the name is unique)


def _slug(text):
    text = re.sub(r"[^\w\- ]", "", text, flags=re.U).strip().lower()
    return re.sub(r"[\s\-]+", "-", text)


def _clean_heading(raw):
    """Returns (name, anchor) when the heading is one API name, else (None, None)."""
    anchor = None
    m = re.search(r"\{([^}]*)\}\s*$", raw)
    if m:
        raw = raw[: m.start()]
        a = re.search(r"#([\w\-]+)", m.group(1))
        anchor = a.group(1) if a else None
    raw = re.sub(r"<span[^>]*>.*?</span>", "", raw).replace("`", "").strip()
    base = re.sub(r"\s*[（(].*$", "", raw).strip()
    if not re.fullmatch(r"[A-Za-z_][\w]*(::[A-Za-z_][\w~]*)*", base):
        return None, None
    return base, anchor or _slug(raw)


def _add(name, src, anchor, table=None):
    entries = (_registry if table is None else table).setdefault(name, [])
    if (src, anchor) not in entries:
        entries.append((src, anchor))


def _in_scope(src):
    return src.startswith(LINK_SCOPE)


def on_files(files, config):
    _registry.clear()
    _bare.clear()
    root = os.path.dirname(config["config_file_path"])
    for f in files.documentation_pages():
        src = f.src_uri
        if src.startswith("_") or not _in_scope(src):
            continue
        with open(f.abs_src_path, encoding="utf-8") as fp:
            text = fp.read()
        apis = []
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end > 0:
                try:
                    meta = yaml.safe_load(text[3:end]) or {}
                except yaml.YAMLError:
                    meta = {}
                apis = [str(a) for a in (meta.get("api") or [])]
                for name in apis:
                    _add(name, src, None)
        in_fence = False
        for line in text.split("\n"):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^(#{2,4})\s+(.*\S)\s*$", line)
            if not m:
                continue
            name, anchor = _clean_heading(m.group(2))
            if name is None:
                continue
            if "::" in name:
                _add(name, src, anchor)
                _add(name.split("::")[-1], src, anchor, _bare)
            elif apis and name not in apis:
                _add(apis[0] + "::" + name, src, anchor)
                _add(name, src, anchor, _bare)
            else:
                _add(name, src, anchor)
    path = os.path.join(root, "autolinks.yml")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}
        for src, terms in data.items():
            if src.startswith("_") or not _in_scope(src):
                continue
            for term in terms or []:
                term = str(term)
                if IDENT.match(term) and not term.islower():
                    _add(term, src.split("#")[0], src.split("#")[1] if "#" in src else None)
    return files


def _series(src):
    for s in ("dx11", "dx12"):
        if src.startswith("directx/%s/" % s):
            return s
    return None


def _choose(cands, page_src):
    mine = _series(page_src)
    best = None
    for src, anchor in cands:
        theirs = _series(src)
        if mine and theirs and mine != theirs and src not in SHARED:
            continue
        score = 0
        if src == page_src:
            score = 3
        elif os.path.dirname(src) == os.path.dirname(page_src):
            score = 2
        elif theirs == mine:
            score = 1
        if best is None or score > best[0]:
            best = (score, src, anchor)
    return best[1:] if best else None


def _pick(name, page_src, qualifier=None):
    """qualifier: the interface of the receiver (``device->Foo``), when known."""
    if qualifier:
        keys = [qualifier + "::" + name]
        stripped = re.sub(r"\d+$", "", qualifier)
        if stripped != qualifier:
            keys.append(stripped + "::" + name)
        for key in keys:
            hit = _choose(_registry.get(key) or [], page_src)
            if hit:
                return hit
    hit = _choose(_registry.get(name) or [], page_src)
    if hit:
        return hit
    cands = [c for c in _bare.get(name) or []]
    reachable = {c for c in cands if _choose([c], page_src)}
    if len(reachable) == 1:
        return _choose(list(reachable), page_src)
    return None


VAR_COMPTR = re.compile(r"ComPtr\s*<\s*([A-Za-z_]\w*)\s*>\s*([A-Za-z_]\w*)")
VAR_PTR = re.compile(r"\b(I[A-Z]\w*)\s*(?:const\s*)?[*&]+\s*([A-Za-z_]\w*)")


def _collect_vars(code, vars_):
    text = code.get_text()
    for m in VAR_COMPTR.finditer(text):
        vars_[m.group(2)] = ("ComPtr", m.group(1))
    for m in VAR_PTR.finditer(text):
        vars_.setdefault(m.group(2), ("ptr", m.group(1)))


def _classify(toks):
    """toks: [(tag, text, classes)] in order. Returns a list of new classes (or None)."""
    n = len(toks)
    out = [None] * n
    sig = [i for i, t in enumerate(toks) if t[2] != "w"]
    pos = {i: k for k, i in enumerate(sig)}

    def at(i, d):
        k = pos[i] + d
        return toks[sig[k]] if 0 <= k < len(sig) else (None, "", "")

    for i, (tag, text, cls) in enumerate(toks):
        if cls == "k" and text in CONTROL:
            out[i] = "kc"
            continue
        if cls == "n" and text in KEYWORDS_EXTRA:
            out[i] = "k"
            continue
        if cls not in NAME_CLASSES or not IDENT.match(text):
            continue
        prev, nxt = at(i, -1), at(i, 1)
        p, q = prev[1], nxt[1]
        k0 = pos[i] - 1
        prev_label = out[sig[k0]] if k0 >= 0 else None
        if p in ("&", "*", "&&") and k0 - 1 >= 0:
            prev_label = out[sig[k0 - 1]]
        nxt_is_name = nxt[2] in NAME_CLASSES and IDENT.match(nxt[1] or "") is not None
        kind = None
        if prev_label == "tk-ty" and q not in ("(", "::") and not ALLCAPS.match(text):
            kind = "tk-v"
        elif nxt_is_name and not (q in CONTROL):
            kind = "tk-ty"
        elif p == "::":
            if q == "(":
                kind = "tk-fn"
            elif q == "::":
                kind = "tk-ns" if text[0].islower() else "tk-ty"
            elif q == "<":
                kind = "tk-ty"
            elif ALLCAPS.match(text) or ENUM_K.match(text):
                kind = "tk-en"
            elif PASCAL.match(text):
                kind = "tk-ty"
            else:
                kind = "tk-v"
        elif q == "(":
            if text.startswith("CD3DX12_") or re.match(r"^XM[A-Z0-9]+$", text):
                kind = "tk-ty"
            elif ALLCAPS.match(text) and len(text) > 1:
                kind = "tk-mc"
            else:
                kind = "tk-fn"
        elif q == "::":
            kind = "tk-ns" if text[0].islower() else "tk-ty"
        elif text in WIN_TYPES or re.match(r"^XM[A-Z0-9]+$", text) or text.startswith("CD3DX12_"):
            kind = "tk-ty"
        elif ALLCAPS.match(text) and len(text) > 1:
            if TYPE_SUFFIX.search(text) or p == "const":
                kind = "tk-ty"
            else:
                kind = "tk-en"
        elif ENUM_K.match(text):
            kind = "tk-en"
        elif INTERFACE.match(text):
            kind = "tk-ty"
        elif q == "<" and PASCAL.match(text):
            kind = "tk-ty"
        elif PASCAL.match(text):
            kind = "tk-ty" if q in ("&", "*", ">", ",", "&&", ")", ";", "{") else "tk-ty"
        else:
            kind = "tk-v"
        out[i] = kind
    return out


QUALIFIED = re.compile(r"[A-Za-z_]\w*(::~?[A-Za-z_]\w*)+")


def _new_span(soup, cls, text):
    tag = soup.new_tag("span")
    tag["class"] = [cls]
    tag.string = text
    return tag


def _expand(soup, code):
    """Pygments joins ``();`` and ``A::B`` into one token. Split them so each part can be colored."""
    for s in list(code.find_all("span")):
        if s.get("id") is not None or s.find(True):
            continue
        cls = (s.get("class") or [""])[0]
        text = s.get_text()
        if cls == "p" and len(text) > 1:
            s.replace_with(*[_new_span(soup, "p", ch) for ch in text])
        elif cls in ("nf", "nc", "n", "nl", "nx", "nn") and QUALIFIED.fullmatch(text):
            parts = text.split("::")
            new = []
            for k, part in enumerate(parts):
                if k:
                    new.append(_new_span(soup, "o", "::"))
                new.append(_new_span(soup, "n", part))
            s.replace_with(*new)


def _process_block(soup, code, page_src, page_url, files, link, vars_):
    _expand(soup, code)
    leaves = [s for s in code.find_all("span") if s.get("id") is None and not s.find(True)]
    toks = []
    for s in leaves:
        cls = (s.get("class") or [""])[0]
        toks.append((s, s.get_text(), cls))
    labels = _classify(toks)
    depth = 0
    used = set()
    sig = [k for k, t in enumerate(toks) if t[2] != "w"]
    pos = {k: j for j, k in enumerate(sig)}
    for idx, ((span, text, cls), label) in enumerate(zip(toks, labels)):
        if label:
            span["class"] = [label]
        if cls == "p" and text in BRACKETS:
            if BRACKETS[text] > 0:
                span["class"] = ["p", "rb%d" % (depth % 3)]
                depth += 1
            else:
                depth = max(0, depth - 1)
                span["class"] = ["p", "rb%d" % (depth % 3)]
        if link and label in ("tk-ty", "tk-fn", "tk-mc", "tk-en"):
            qualifier = None
            j = pos[idx]
            if label == "tk-fn" and j >= 2 and toks[sig[j - 1]][1] in (".", "->"):
                op, recv = toks[sig[j - 1]][1], toks[sig[j - 2]][1]
                kind, inner = vars_.get(recv, (None, None))
                if kind == "ComPtr" and op == ".":
                    qualifier = "ComPtr"
                elif kind in ("ComPtr", "ptr"):
                    qualifier = inner
            key = (qualifier or "") + "::" + text
            if key in used:
                continue
            target = _pick(text, page_src, qualifier)
            if target is None:
                continue
            tsrc, anchor = target
            f = files.get_file_from_path(tsrc)
            if f is None:
                continue
            if tsrc == page_src and anchor is None:
                continue
            href = get_relative_url(f.url, page_url) if tsrc != page_src else ""
            href += ("#" + anchor) if anchor else ""
            a = soup.new_tag("a", href=href or "#")
            a["class"] = "code-link"
            span.wrap(a)
            used.add(key)


def on_page_content(html, page, config, files):
    if "highlight" not in html:
        return html
    soup = BeautifulSoup(html, "html.parser")
    link = page.file.src_uri.startswith(LINK_SCOPE)
    changed = False
    blocks = []
    for div in soup.find_all("div", class_="highlight"):
        classes = div.parent.get("class") or [] if div.parent else []
        wrapper = " ".join(classes + (div.get("class") or []))
        if not any(l in wrapper for l in LANGS):
            continue
        code = div.find("code")
        if code is not None:
            blocks.append(code)
    vars_ = {}
    for code in blocks:
        _collect_vars(code, vars_)
    for code in blocks:
        _process_block(soup, code, page.file.src_uri, page.url, files, link, vars_)
        changed = True
    return str(soup) if changed else html
