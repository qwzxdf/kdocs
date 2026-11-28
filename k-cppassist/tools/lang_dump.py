"""strings.tsv を、番号つきで見る。引数: 始まり 終わり [列...](既定は ja en)。欄が空の行だけなら --empty 列名。"""
import io, os, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'KCppAssist.Core', 'Lang', 'strings.tsv')
lines = io.open(SRC, encoding='utf-8').read().split('\n')
head = lines[0].split('\t')
rows = [l.split('\t') for l in lines[1:] if l]
args = sys.argv[1:]
empty = None
if '--empty' in args:
    k = args.index('--empty'); empty = args[k + 1]; del args[k:k + 2]
a = int(args[0]) if args else 0
b = int(args[1]) if len(args) > 1 else len(rows)
cols = args[2:] or ['ja', 'en']
out = io.open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)
for n in range(a, min(b, len(rows))):
    r = rows[n]
    if empty and r[head.index(empty)]: continue
    out.write('%d\t%s\n' % (n, '\t'.join(r[head.index(c)] for c in cols)))
