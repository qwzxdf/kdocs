"""src/KCppAssist.Vsix/Lang/strings.tsv から LangData.cs を作る。訳を足したら、これを実行してからビルドする。
TSV: 1 行目は列名(ja en zh ko es pt de fr ru)。\\n \\t \\\\ はエスケープ。空の欄は、実行時に英語(なければ日本語)になる。"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'KCppAssist.Core')

def tsv_unescape(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\'}.get(s[i + 1], '\\' + s[i + 1])); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)

def cs(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t') + '"'

def load():
    lines = io.open(os.path.join(SRC, 'Lang', 'strings.tsv'), encoding='utf-8').read().split('\n')
    head = lines[0].split('\t')
    rows = []
    seen = set()
    for n, l in enumerate(lines[1:], 2):
        if not l: continue
        cols = [tsv_unescape(c) for c in l.split('\t')]
        assert len(cols) == len(head), ('line', n, len(cols), l[:60])
        assert cols[0] not in seen, ('duplicate key at line', n, cols[0][:60])
        seen.add(cols[0])
        rows.append(cols)
    return head, rows

if __name__ == '__main__':
    head, rows = load()
    body = '\n'.join('            [%s] = new[] { %s },' % (cs(r[0]), ', '.join(cs(c) for c in r[1:])) for r in rows)
    out = '''// このファイルは tools/lang_gen.py が Lang/strings.tsv から作る。手で書き換えない。
using System.Collections.Generic;

namespace KCppAssist
{
    internal static class LangData
    {
        /// <summary>列の並び(日本語のあと)。L.Column がこの順の番号を返す。</summary>
        public static readonly string[] Columns = { %s };

        /// <summary>日本語の原文 → 各言語の訳(空なら、英語か日本語にする)。</summary>
        public static readonly Dictionary<string, string[]> Rows = new Dictionary<string, string[]>(System.StringComparer.Ordinal)
        {
%s
        };
    }
}
''' % (', '.join(cs(h) for h in head[1:]), body)
    io.open(os.path.join(SRC, 'LangData.cs'), 'w', encoding='utf-8-sig', newline='\r\n').write(out)
    filled = {h: sum(1 for r in rows if r[i]) for i, h in enumerate(head)}
    print('rows', len(rows), 'filled', filled)
