"""既存の STL ページの本文を、ページごとの具体的な文章で書き直す道具。

front matter、バッジ、「このページを読む前に」、「コンパイラ対応」、「関連ページ」は残す。
使い方: rewrite(パス, intro=..., tips=[...], details=..., code=..., out=..., uses=..., mistakes=[(題, 本文)...], similar=[(名, 違い)...], memo=[...])
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _split(text):
    parts = re.split(r'\n(?=## )', text)
    head = parts[0]
    secs = {}
    order = []
    for p in parts[1:]:
        title = p.split('\n', 1)[0][3:].strip()
        secs[title] = p
        order.append(title)
    return head, secs, order


def rewrite(path, intro, tips, details, code, out, uses, mistakes, similar=None, memo=None,
            out_title='実行結果', extra=None):
    p = os.path.join(ROOT, 'docs', path)
    raw = open(p, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    text = raw.replace('\r\n', '\n')
    head, secs, order = _split(text)
    # head: front matter + 見出し + バッジ + 導入 + tip + info
    m = re.search(r'</div>\n', head)
    pre = head[:m.end()]
    info = re.search(r'!!! info "このページを読む前に".*', head, re.S)
    info = info.group(0).rstrip('\n') if info else ''
    tip = '!!! tip "ポイント"\n' + '\n'.join('    - ' + t for t in tips)
    body = pre + '\n' + intro.strip() + '\n\n' + tip + '\n\n' + info + '\n'
    body += '\n## 関数の詳しい説明\n\n' + details.strip() + '\n'
    body += '\n## 実際に動かしてみる\n\n```cpp\n' + code.strip('\n') + '\n```\n\n```text title="' + out_title + '"\n' + out.strip('\n') + '\n```\n'
    if extra:
        body += '\n' + extra.strip('\n') + '\n'
    body += '\n## ゲームでの使いどころ\n\n' + uses.strip() + '\n'
    body += '\n## よくあるミス\n\n'
    for t, b in mistakes:
        body += '??? failure "%s"\n' % t
        body += '\n'.join(('    ' + ln if ln else '') for ln in b.strip().split('\n')) + '\n\n'
    body = body.rstrip('\n') + '\n'
    if similar:
        body += '\n## 類似\n\n| 名前 | 違い |\n| --- | --- |\n' + '\n'.join('| %s | %s |' % s for s in similar) + '\n'
    elif '類似' in secs:
        body += '\n' + secs['類似'].rstrip('\n') + '\n'
    if 'コンパイラ対応' in secs:
        body += '\n' + secs['コンパイラ対応'].rstrip('\n') + '\n'
    if memo:
        body += '\n## これだけ覚える\n\n!!! abstract "まとめ"\n' + '\n'.join('    - [x] ' + t for t in memo) + '\n'
    elif 'これだけ覚える' in secs:
        body += '\n' + secs['これだけ覚える'].rstrip('\n') + '\n'
    if '関連ページ' in secs:
        body += '\n' + secs['関連ページ'].rstrip('\n') + '\n'
    open(p, 'w', encoding='utf-8', newline='').write(body.replace('\n', nl))
