"""翻訳の鍵の検査。コードの中で翻訳に通す日本語の文(L.T / L.F / Loc 属性 / QuickFix の Action など)が、
Lang/strings.tsv の ja の列にあるかを調べる。ない文があると、その言語の画面で日本語のまま出る(日本語の文を直したときに起きる)。

  python tools/lang_check.py            # 新しく足りなくなった文があれば、一覧を出して終了コード 1
  python tools/lang_check.py --update   # いまの足りない文を、lang_check.known.txt に記録する(既知の分)

lang_check.known.txt にある文は、既知として黙認する。
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
TSV = os.path.join(SRC, 'KCppAssist.Core', 'Lang', 'strings.tsv')
KNOWN = os.path.join(HERE, 'lang_check.known.txt')

LIT = r'"((?:[^"\\]|\\.)*)"'
# 翻訳に通る呼び出し。最初の引数が文字列リテラルのもの
CALLS = [
    r'\bL\.T\(\s*' + LIT,
    r'\bL\.F\(\s*' + LIT,
    r'\[Loc(?:Category|DisplayName|Description)\(\s*' + LIT,
    r'\bAction\(\s*' + LIT,              # QuickFix の項目(中で L.T を通す)
    r'\bAction\(\s*L\.F\(\s*' + LIT,
]
JA = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')


def unescape(s):
    out = []; i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            out.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}.get(n, '\\' + n)); i += 2
        else:
            out.append(c); i += 1
    return ''.join(out)


def tsv_unescape(s):
    return unescape(s)


def load_keys():
    keys = set()
    with io.open(TSV, encoding='utf-8') as f:
        for n, l in enumerate(f.read().split('\n')):
            if n == 0 or not l:
                continue
            keys.add(tsv_unescape(l.split('\t')[0]))
    return keys


def code_files():
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj', 'Lang')]
        for f in files:
            if f.endswith('.cs') and f != 'LangData.cs' and not f.startswith('Lang'):
                yield os.path.join(root, f)


def main():
    keys = load_keys()
    missing = {}
    for p in code_files():
        text = io.open(p, encoding='utf-8-sig').read()
        for pat in CALLS:
            for m in re.finditer(pat, text):
                s = unescape(m.group(1))
                if not JA.search(s) or s in keys:
                    continue
                missing.setdefault(s, os.path.relpath(p, SRC))
    known = set()
    if os.path.exists(KNOWN):
        known = set(tsv_unescape(l) for l in io.open(KNOWN, encoding='utf-8').read().split('\n') if l)
    if '--update' in sys.argv:
        with io.open(KNOWN, 'w', encoding='utf-8', newline='\n') as f:
            for s in sorted(missing):
                f.write(s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t') + '\n')
        print('known missing:', len(missing))
        return 0
    new = [(s, p) for s, p in missing.items() if s not in known]
    for s, p in sorted(new, key=lambda x: x[1]):
        print('NEW (not in strings.tsv): %s  [%s]' % (s[:80].replace('\n', '\\n'), p))
    print('lang_check: %d missing (%d known, %d new)' % (len(missing), len(missing) - len(new), len(new)))
    return 1 if new else 0


sys.exit(main())
