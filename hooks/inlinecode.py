import html
import re

from bs4 import BeautifulSoup

KEYWORDS = {
    "const", "constexpr", "consteval", "constinit", "auto", "static", "inline", "virtual",
    "override", "final", "noexcept", "explicit", "operator", "template", "typename",
    "class", "struct", "enum", "namespace", "using", "new", "delete", "return", "if",
    "else", "for", "while", "switch", "case", "default", "break", "continue", "this",
    "nullptr", "true", "false", "sizeof", "alignof", "decltype", "mutable", "volatile",
    "co_await", "co_return", "co_yield", "requires", "concept", "typedef", "extern",
}
BUILTIN_TYPES = {
    "void", "bool", "char", "short", "int", "long", "float", "double", "signed",
    "unsigned", "wchar_t", "char8_t", "char16_t", "char32_t", "size_t", "ptrdiff_t",
    "int8_t", "int16_t", "int32_t", "int64_t", "uint8_t", "uint16_t", "uint32_t",
    "uint64_t", "intptr_t", "uintptr_t",
}

TOKEN = re.compile(
    r"""(?P<str>"(?:\\.|[^"\\])*")
       |(?P<num>\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fFuUlL]*\b)
       |(?P<ident>[A-Za-z_][A-Za-z0-9_]*)
       |(?P<op>::|->|\.\.\.|<<|>>|<=|>=|==|!=|&&|\|\||[+\-*/%&|^~!=<>?:])
       |(?P<punct>[()\[\]{},;.])
       |(?P<space>\s+)
       |(?P<other>.)""",
    re.X,
)

CJK = re.compile(r"[　-鿿＀-￯]")
CALL = re.compile(r"[A-Za-z_]\w*\s*(<[^>]*>)?\s*\(")
SCOPE = re.compile(r"[A-Za-z_]\w*::[A-Za-z_]")
TYPE_WORD = re.compile(r"(XM[A-Za-z0-9_]+|[A-Z][a-z]+[A-Z0-9][A-Za-z0-9]*|[A-Z][a-z]+[0-9])")
IDENT_ONLY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
FILE_EXT = (
    "h|hpp|hxx|hh|inl|c|cc|cpp|cxx|hlsl|hlsli|fx|cso|json|yaml|yml|toml|xml|md|txt|png|jpg|jpeg|dds|tga|bmp|"
    "glb|gltf|fbx|obj|ini|cfg|cmake|bat|ps1|sh|sln|vcxproj|props|filters|lib|dll|exe|pdb|ttf|otf|ttc|bin|"
    "py|js|css|html|csv|wav|ogg|mp3|ktx2|hdr|exr|mesh|mtl|editorconfig|gitignore|gitattributes|clang-format"
)
FILE_RE = re.compile(r"^(?P<dir>(?:[A-Za-z0-9_.\-]+/)*)(?P<name>[A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*?)(?P<ext>\.(?:%s))$" % FILE_EXT)


def _file_html(text):
    m = FILE_RE.match(text)
    if not m or len(text) > 80:
        return None
    out = ""
    if m.group("dir"):
        out += _span("pd", m.group("dir"))
    if m.group("name"):
        out += _span("pf", m.group("name"))
    out += _span("pe", m.group("ext"))
    return out


def _looks_cpp(text):
    if not text or CJK.search(text) or len(text) > 120:
        return False
    if text.startswith(("/", "-", ".", "#")) or "\\" in text:
        return False
    if CALL.search(text) or SCOPE.search(text):
        return True
    if IDENT_ONLY.fullmatch(text) and TYPE_WORD.fullmatch(text):
        return True
    return False


def _span(cls, text):
    return '<span class="%s">%s</span>' % (cls, html.escape(text, quote=False))


def _next_nonspace(tokens, i):
    for j in range(i + 1, len(tokens)):
        if tokens[j][0] != "space":
            return tokens[j]
    return ("end", "")


def _highlight(text):
    tokens = [(m.lastgroup, m.group()) for m in TOKEN.finditer(text)]
    out = []
    prev = ("start", "")
    for i, (kind, value) in enumerate(tokens):
        nxt = _next_nonspace(tokens, i)
        if kind == "str":
            out.append(_span("s", value))
        elif kind == "num":
            out.append(_span("m", value))
        elif kind == "ident":
            after_scope = prev[1] in ("::", ".", "->")
            if value in KEYWORDS:
                out.append(_span("k", value))
            elif value in BUILTIN_TYPES:
                out.append(_span("kt", value))
            elif nxt[1] == "(":
                out.append(_span("nf", value))
            elif nxt[1] == "::":
                out.append(_span("nc" if value[0].isupper() else "nn", value))
            elif value.isupper() and len(value) > 1 or re.fullmatch(r"k[A-Z]\w*", value):
                out.append(_span("no", value))
            elif value[0].isupper():
                out.append(_span("nc", value))
            elif after_scope:
                out.append(_span("nv", value))
            else:
                out.append(_span("nv", value))
        elif kind == "op":
            out.append(_span("o", value))
        elif kind == "punct":
            out.append(_span("p", value))
        else:
            out.append(html.escape(value, quote=False))
        if kind != "space":
            prev = (kind, value)
    return "".join(out)


def on_page_content(content, page, config, files):
    if "<code" not in content:
        return content
    soup = BeautifulSoup(content, "html.parser")
    changed = False
    for code in soup.find_all("code"):
        if code.find_parent(["pre", "a", "h1", "h2", "h3", "h4", "h5", "h6"]):
            continue
        if code.get("class") or code.find(True):
            continue
        text = code.get_text()
        file_html = _file_html(text)
        if file_html is None and not _looks_cpp(text):
            continue
        code["class"] = ["highlight", "inline-cpp"]
        code.clear()
        code.append(BeautifulSoup(file_html if file_html is not None else _highlight(text), "html.parser"))
        changed = True
    return str(soup) if changed else content
