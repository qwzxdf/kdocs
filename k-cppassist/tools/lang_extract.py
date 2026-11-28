"""今の C# の訳の表(Lang.cs・LangDescriptions.cs・LangMessages.cs・LangMore.cs)を、strings.tsv に移す(1 回だけ使う)。
TSV の 1 行 = 日本語の原文(実行時の文字そのもの) と各言語の訳。改行は \\n、タブは \\t、バックスラッシュは \\\\ で書く。"""
import re, io, os, sys

SRC = os.path.join(os.path.dirname(__file__), '..', 'src', 'KCppAssist.Core')
LANGS = ['ja', 'en', 'zh', 'ko', 'es', 'pt', 'de', 'fr', 'ru']

def unescape_cs(s):
    """C# の通常の文字列リテラルの中身 → 実行時の文字。"""
    out = []; i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            out.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}.get(n, '\\' + n)); i += 2
        else:
            out.append(c); i += 1
    return ''.join(out)

def tsv_escape(s):
    return s.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')

LIT = r'"((?:[^"\\]|\\.)*)"'
ROW = re.compile(r'\[' + LIT + r'\]\s*=\s*new\[\]\s*\{\s*' + LIT + r'\s*,\s*' + LIT + r'\s*,\s*' + LIT + r'\s*\}')
rows = {}
order = []
for f in ('Lang.cs', 'LangDescriptions.cs', 'LangMessages.cs', 'LangMore.cs'):
    t = open(os.path.join(SRC, f), encoding='utf-8-sig').read()
    for m in ROW.finditer(t):
        ja, en, zh, ko = (unescape_cs(m.group(i)) for i in range(1, 5))
        if ja not in rows: order.append(ja)
        rows[ja] = [ja, en, zh, ko, '', '', '', '', '']
out = io.open(os.path.join(SRC, 'Lang', 'strings.tsv'), 'w', encoding='utf-8', newline='\n')
out.write('\t'.join(LANGS) + '\n')
for ja in order: out.write('\t'.join(tsv_escape(x) for x in rows[ja]) + '\n')
out.close()
print('rows', len(order))
