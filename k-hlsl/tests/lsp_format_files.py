# -*- coding: utf-8 -*-
"""手元の .hlsl を整形して、(1) 空白以外が変わらない (2) 2 回目で変わらない、を確かめる。"""
import sys, glob, re, os
sys.argv = [sys.argv[0]] + sys.argv[1:]
exec(open(os.path.join(os.path.dirname(__file__), 'lsp_format.py'), encoding='utf-8').read().split("bad = r'''")[0])
files = []
for pat in sys.argv[1:]: files += glob.glob(pat, recursive=True)
bad = 0
for f in files:
    t = open(f, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
    a = fmt(t); b = fmt(a)
    same = re.sub(r'\s+', '', a) == re.sub(r'\s+', '', t)
    idem = a == b
    print(('OK ' if same and idem else 'NG '), f, '' if same else 'content-changed', '' if idem else 'not-idempotent')
    bad += not (same and idem)
sys.exit(1 if bad else 0)
