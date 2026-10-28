"""`**語**` が、前後の文字のせいで太字にならない所を、`<strong>語</strong>` に直す。

Markdown では、開きの `**` の直後が記号（「、（ など）で、直前が文字のとき、
閉じの `**` の直前が記号で、直後が文字のとき、太字にならない。
使い方: python tools/fix_bold_flank.py docs [--apply]
"""
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def punct(c):
    return unicodedata.category(c).startswith(('P', 'S'))


def word(c):
    return not c.isspace() and not punct(c)


def fix_line(line):
    out = []
    pos = 0
    changed = 0
    for m in re.finditer(r'\*\*([^*\n]+?)\*\*', line):
        a, b = m.start(), m.end()
        inner = m.group(1)
        before = line[a - 1] if a > 0 else ' '
        after = line[b] if b < len(line) else ' '
        bad_open = punct(inner[0]) and word(before)
        bad_close = punct(inner[-1]) and word(after)
        if bad_open or bad_close:
            out.append(line[pos:a])
            out.append('<strong>' + inner + '</strong>')
            pos = b
            changed += 1
    out.append(line[pos:])
    return ''.join(out), changed


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    apply = '--apply' in sys.argv
    total = 0
    files = 0
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.md'):
                continue
            p = os.path.join(dp, f)
            raw = open(p, encoding='utf-8', newline='').read()
            nl = '\r\n' if '\r\n' in raw else '\n'
            lines = raw.replace('\r\n', '\n').split('\n')
            infence = False
            n = 0
            for i, ln in enumerate(lines):
                if ln.lstrip().startswith('```'):
                    infence = not infence
                    continue
                if infence or '**' not in ln:
                    continue
                # インライン コードの `...` も、記号として扱う（`**` 自体がコードの中にある行は、触らない）
                if any('**' in m.group(0) for m in re.finditer(r'`[^`]*`', ln)):
                    continue
                t, c = fix_line(ln)
                n += c
                new = [t]
                lines[i] = ''.join(new)
            if n:
                total += n
                files += 1
                print('%s: %d' % (os.path.relpath(p, root), n))
                if apply:
                    open(p, 'w', encoding='utf-8', newline='').write(nl.join(lines))
    print('合計 %d か所、%d ファイル%s' % (total, files, '（書き換えた）' if apply else '（--apply で書き換える）'))


if __name__ == '__main__':
    main()
