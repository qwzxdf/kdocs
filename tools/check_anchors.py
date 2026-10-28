"""ビルド結果（site/）の HTML で、アンカー リンク（#xxx）の切れと、太字の `**` の残りを調べる。

使い方: python tools/check_anchors.py site
問題があれば一覧を出して、終了コード 1 で終わる。
"""
import os
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

ID = re.compile(r'\b(?:id|name)="([^"]+)"')
HREF = re.compile(r'<a\s[^>]*?href="([^"]*#[^"]*)"')
SKIP = re.compile(r'<(pre|code|script|style)\b.*?</\1>', re.S)
TAG = re.compile(r'<[^>]*>')
PAIR = re.compile(r'\*\*[^*\s](?:[^*]*[^*\s])?\*\*')   # **語** の形だけ（char** のようなポインターは除く）


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'site'
    ids = {}
    links = {}
    stars = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.html'):
                continue
            p = os.path.normpath(os.path.join(dp, f))
            with open(p, encoding='utf-8') as fh:
                h = fh.read()
            ids[p] = set(ID.findall(h))
            links[p] = HREF.findall(h)
            if '**' in h:
                text = TAG.sub('', SKIP.sub('', h))
                if PAIR.search(text):
                    stars.append(p)
    bad = []
    for p, hs in links.items():
        for href in hs:
            if href.startswith(('http:', 'https:', 'mailto:')):
                continue
            path, frag = href.split('#', 1)
            frag = urllib.parse.unquote(frag)
            if not frag:
                continue
            if path == '':
                target = p
            else:
                t = os.path.normpath(os.path.join(os.path.dirname(p), urllib.parse.unquote(path)))
                if os.path.isdir(t):
                    t = os.path.join(t, 'index.html')
                target = t
            if target in ids and frag not in ids[target]:
                bad.append((p, href))
    for p in sorted(stars):
        print('%s: 太字の ** が残っている' % os.path.relpath(p, root))
    for p, h in sorted(bad):
        print('%s -> %s' % (os.path.relpath(p, root), h))
    print('アンカー切れ: %d 件、** の残り: %d ページ（%d ページを検査）' % (len(bad), len(stars), len(ids)))
    return 1 if (bad or stars) else 0


if __name__ == '__main__':
    sys.exit(main())
