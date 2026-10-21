"""ビルド結果から、DirectX ページのコードに出てくる API 名のうち、リンク先が無いものを数える。

使い方: python tools/api_coverage.py site [dx11|dx12] [件数]
先に mkdocs build を実行しておく（hooks/codelink.py が付けた tk-* クラスを読む）。
"""
import collections
import glob
import html
import os
import re
import sys

site = sys.argv[1] if len(sys.argv) > 1 else "site"
series = sys.argv[2] if len(sys.argv) > 2 else "dx12"
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 80

TOKEN = re.compile(r'(<a class="code-link"[^>]*>)?<span class="(tk-ty|tk-fn|tk-mc|tk-en)">([^<]*)</span>')
missing = collections.Counter()
linked = collections.Counter()
pages = collections.defaultdict(set)
kind_of = {}
for path in glob.glob(os.path.join(site, "directx", series, "**", "index.html"), recursive=True):
    page = os.path.relpath(os.path.dirname(path), site).replace("\\", "/")
    text = open(path, encoding="utf-8").read()
    for m in TOKEN.finditer(text):
        name = html.unescape(m.group(3))
        (linked if m.group(1) else missing)[name] += 1
        if not m.group(1):
            pages[name].add(page)
            kind_of.setdefault(name, m.group(2))

def interesting(name):
    return re.match(r"^(D3D|DXGI|ID3D|IDXGI|CD3DX|XM|DirectX|Create|Set|Get|Get|Execute|Reset|Close|Map|Unmap|Signal|Wait|Present|Clear|Draw|Dispatch|Resource|Copy|IA|OM|RS|VS|PS|CS|GS|HS|DS|Update|Query|Begin|End|Open|Release|AddRef)", name) or name in kind_of and kind_of[name] in ("tk-fn",)

rows = [(n, c) for n, c in missing.most_common() if interesting(n) and n not in linked]
print(f"{series}: リンクできた名前 {len(linked)} 種類 / まだリンク先が無い名前 {len(rows)} 種類")
for name, count in rows[:limit]:
    print(f"{count:4d} {kind_of[name][3:]:3s} {name}  ({len(pages[name])} ページ)")
