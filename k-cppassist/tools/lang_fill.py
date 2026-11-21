"""strings.tsv の欄を埋める。引数: 訳を書いた .py(T = { 行番号: (es, pt, de, fr, ru) } か、COLS と T を書いたもの)。
行番号は lang_dump.py が出す番号(TSV の 2 行目が 0)。{0} などの数が日本語と合わない訳は、受け付けずに止まる。"""
import io, os, re, sys, runpy

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'KCppAssist.Vsix', 'Lang', 'strings.tsv')

def esc(s): return s.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
def unesc(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\'}.get(s[i + 1], '\\' + s[i + 1])); i += 2
        else: out.append(s[i]); i += 1
    return ''.join(out)

data = runpy.run_path(sys.argv[1])
T = data['T']; cols = data.get('COLS', ['es', 'pt', 'de', 'fr', 'ru'])
lines = io.open(SRC, encoding='utf-8').read().split('\n')
head = lines[0].split('\t')
idx = [head.index(c) for c in cols]
rows = [l.split('\t') for l in lines[1:] if l]
bad = []
for n, vals in T.items():
    r = rows[n]
    ja = unesc(r[0])
    want = sorted(set(re.findall(r'\{\d+\}', ja)))
    assert len(vals) == len(cols), (n, len(vals))
    for c, v in zip(idx, vals):
        if sorted(set(re.findall(r'\{\d+\}', v))) != want: bad.append((n, head[c], ja[:40], v[:40])); continue
        if ja.startswith('\n') != v.startswith('\n'): bad.append((n, head[c], 'leading newline', v[:40])); continue
        r[c] = esc(v)
if bad:
    for b in bad: print('BAD', b)
    sys.exit(1)
io.open(SRC, 'w', encoding='utf-8', newline='\n').write('\n'.join(['\t'.join(head)] + ['\t'.join(r) for r in rows]) + '\n')
print('filled', len(T), 'rows')
