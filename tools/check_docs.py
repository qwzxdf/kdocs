"""docs/ の md を静的に検査する。

使い方: python tools/check_docs.py docs [--report]
エラー（終了コード 1）:
  - front matter に title が無い（index.md は除く。.pages の title を使うため）
（太字の `**` の残りは、ビルド結果の HTML でしか分からないので、check_anchors.py が調べる）
報告だけ（--report で一覧を出す。終了コードには影響しない）:
  - `TODO` の下書きが残るページ
  - `int main` があるのに、直後に実行結果が続かないコード
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FENCE = re.compile(r'^(\s*)```(\w*)[^\n]*\n(.*?)^\1```[ \t]*$', re.S | re.M)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    report = '--report' in sys.argv
    errors = []
    todo = []
    noresult = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.md'):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding='utf-8').read().replace('\r\n', '\n')
            rel = os.path.relpath(p, root)
            m = re.match(r'---\n(.*?)\n---\n', s, re.S)
            if f != 'index.md' and (not m or not re.search(r'^title:', m.group(1), re.M)):
                errors.append('%s: front matter に title が無い' % rel)
            body = s[m.end():] if m else s
            if '!!! warning "TODO"' in body:
                todo.append(rel)
            for fm in FENCE.finditer(body):
                if fm.group(2) in ('cpp', 'c') and re.search(r'\bint main\b', fm.group(3)):
                    after = body[fm.end():fm.end() + 80]
                    if 'title="実行結果' not in after and not re.match(r'\s*```text', after):
                        noresult.append(rel)
                        break
    for e in errors:
        print(e)
    print('エラー: %d 件' % len(errors))
    if report:
        print('\nTODO の下書き: %d ページ' % len(todo))
        for t in sorted(todo):
            print('  ' + t)
        print('\nint main があるのに実行結果が続かない: %d ページ' % len(noresult))
        for t in sorted(noresult):
            print('  ' + t)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
