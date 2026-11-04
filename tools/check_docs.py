"""docs/ の md を静的に検査する。

使い方: python tools/check_docs.py docs [--report]
エラー（終了コード 1）:
  - front matter に title が無い（index.md は除く。.pages の title を使うため）
（太字の `**` の残りは、ビルド結果の HTML でしか分からないので、check_anchors.py が調べる）
報告だけ（--report で一覧を出す。終了コードには影響しない）:
  - `TODO` の下書きが残るページ
  - `int main` があるのに、直後に実行結果が続かないコード
  - 質の警告（STL は除く。2-8・2-9 で直したページから、エラーに切り替える）:
    1 文あたりの読点が 1 を超える / 図が 0 枚 / セルが 40 字を超える表 /
    「説明」「理由」「手順」「長所」などの列がある表 / コードの 20 行以上でコメントが 1 割未満 /
    同じ段落が 1 ページに 2 回ある
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FENCE = re.compile(r'^(\s*)```(\w*)[^\n]*\n(.*?)^\1```[ \t]*$', re.S | re.M)


HEAD_WORDS = ('説明', '理由', '手順', '長所', '短所', '意味', '内容')
SEP = re.compile(r'^\|[\s:|-]+\|?\s*$')


def quality(body):
    """STL 以外のページの質の警告を返す（文字列のリスト）。"""
    out = []
    bare = re.sub(r'<svg.*?</svg>', '', body, flags=re.S)
    svg = len(re.findall(r'<svg', body)) + len(re.findall(r'class="anim', body))
    codes = [m.group(3) for m in FENCE.finditer(bare)]
    prose = FENCE.sub('', bare)
    lines = prose.split('\n')
    text = '\n'.join(l for l in lines if not l.lstrip().startswith(('|', '#', '<')))
    sent = text.count('。')
    if sent >= 20 and text.count('、') / sent > 1:
        out.append('読点が多い（%.2f/文）' % (text.count('、') / sent))
    if svg == 0 and sent >= 20:
        out.append('図が 0 枚')
    long_cells = 0
    for i, l in enumerate(lines):
        if l.lstrip().startswith('|') and not SEP.match(l.strip()):
            for c in l.strip().strip('|').split('|'):
                if len(c.strip()) > 40:
                    long_cells += 1
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if SEP.match(nxt.strip()) and any(w in l for w in HEAD_WORDS):
                out.append('列名が説明系の表: ' + l.strip()[:30])
    if long_cells:
        out.append('40 字を超えるセル %d 個' % long_cells)
    for c in codes:
        ls = [x for x in c.split('\n') if x.strip()]
        if len(ls) >= 20 and sum(1 for x in ls if re.search(r'//|/\*|\s#\s', x)) * 10 < len(ls):
            out.append('コメントが少ないコード（%d 行）' % len(ls))
            break
    paras = [q.strip() for q in re.split(r'\n\s*\n', prose) if len(q.strip()) > 40 and not q.lstrip().startswith(('|', '<'))]
    if len(paras) != len(set(paras)):
        out.append('同じ段落が 2 回ある')
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    report = '--report' in sys.argv
    errors = []
    todo = []
    noresult = []
    quality_warn = {}
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
            if not rel.replace(chr(92), '/').startswith(('stl/', 'javascripts', 'stylesheets')) and f != '_template.md':
                q = quality(body)
                if q:
                    quality_warn[rel] = q
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
    if report:
        print('\n質の警告: %d ページ' % len(quality_warn))
        for k in sorted(quality_warn):
            print('  %s: %s' % (k, ' / '.join(quality_warn[k])))
    else:
        print('質の警告: %d ページ（--report で一覧）' % len(quality_warn))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
