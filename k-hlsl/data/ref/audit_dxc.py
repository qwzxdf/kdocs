# -*- coding: utf-8 -*-
"""DXC の gen_intrin_main.txt(組み込み関数・オブジェクトのメソッドの定義表)と、K-HLSL のデータを突き合わせる。

使い方: python data/ref/audit_dxc.py
  data/ref/gen_intrin_main.txt は、https://github.com/microsoft/DirectXShaderCompiler/blob/main/utils/hct/gen_intrin_main.txt
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

db = json.load(open(os.path.join(ROOT, 'src', 'KHlsl.Server', 'hlsl.json'), encoding='utf-8'))
mine_funcs = {i['n'] for i in db['intrinsics']}
mine_methods = {}
for g, lst in db['methods'].items():
    for m in lst:
        mine_methods.setdefault(m['n'], set()).add(g)
mine_methods_all = set(mine_methods)
mine_types = {t['n'] for t in db['types']}

ns_stack = []
entries = {}  # namespace -> set(name)
rx_ns = re.compile(r'^\s*namespace\s+(\w+)\s*\{')
rx_end = re.compile(r'^\s*\}\s*(?://.*)?$')
rx_decl = re.compile(r'^[^/]*?\b(\w+)\s*\(')
for raw in open(os.path.join(HERE, 'gen_intrin_main.txt'), encoding='utf-8'):
    line = raw.split('//')[0].rstrip()
    if not line.strip():
        continue
    m = rx_ns.match(line)
    if m:
        ns_stack.append(m.group(1))
        continue
    if rx_end.match(line) and ns_stack:
        ns_stack.pop()
        continue
    if not ns_stack:
        continue
    d = rx_decl.match(line)
    if not d:
        continue
    name = d.group(1)
    entries.setdefault(ns_stack[-1], set()).add(name)

print('名前空間:', ', '.join('%s(%d)' % (k, len(v)) for k, v in sorted(entries.items())))

# 全体の関数
global_ns = [k for k in entries if k in ('Intrinsics', 'Wave', 'Quad')] or ['Intrinsics']
print()
missing_f = sorted(n for ns in global_ns for n in entries[ns] if n not in mine_funcs and not n.startswith('__'))
print('--- グローバル関数のうち、K-HLSL に無い物 (%d)' % len(missing_f))
print(', '.join(missing_f))

# メソッド: 名前空間名がオブジェクトの型に対応する
print()
all_methods = set()
for ns, names in entries.items():
    if ns in global_ns:
        continue
    all_methods |= names
missing_m = sorted(n for n in all_methods if n not in mine_methods_all and n not in mine_funcs)
print('--- オブジェクトのメソッドのうち、K-HLSL に無い物 (%d)' % len(missing_m))
for ns, names in sorted(entries.items()):
    if ns in global_ns:
        continue
    miss = sorted(n for n in names if n not in mine_methods_all and n not in mine_funcs)
    if miss:
        print('  %s: %s' % (ns, ', '.join(miss)))

# K-HLSL にあって DXC に無い関数(ただし dx:: / 旧 API は除く)
dxc_all = set()
for names in entries.values():
    dxc_all |= names
extra = sorted(n for n in mine_funcs if n not in dxc_all and '::' not in n)
print()
print('--- K-HLSL にあって、DXC の表に無い関数 (%d)' % len(extra))
print(', '.join(extra))
extra_m = sorted(n for n in mine_methods_all if n not in dxc_all)
print()
print('--- K-HLSL にあって、DXC の表に無いメソッド (%d)' % len(extra_m))
print(', '.join(extra_m))

# ---- 必要な Shader Model(min_sm)の突き合わせ ----
rx_sm = re.compile(r'min_sm\s*=\s*([0-9.]+)')
sm_of = {}
ns2 = []
for raw in open(os.path.join(HERE, 'gen_intrin_main.txt'), encoding='utf-8'):
    line = raw.split('//')[0].rstrip()
    m = rx_ns.match(line)
    if m:
        ns2.append(m.group(1)); continue
    if rx_end.match(line) and ns2:
        ns2.pop(); continue
    d = rx_decl.match(line)
    if not d or not ns2:
        continue
    name = d.group(1)
    sm = rx_sm.search(line)
    key = name
    # 同じ名前の複数のオーバーロードは、いちばん小さい SM を採る
    v = float(sm.group(1)) if sm else None
    if key in sm_of:
        sm_of[key] = min(x for x in (sm_of[key], v) if x is not None) if (sm_of[key] is not None or v is not None) else None
    else:
        sm_of[key] = v

def to_f(x):
    try:
        return float(x)
    except Exception:
        return None

print()
print('--- 必要な Shader Model が、DXC の表と違う物')
bad_sm = []
for i in db['intrinsics']:
    n = i['n']
    if n in sm_of and sm_of[n] is not None and to_f(i['m']) is not None and abs(to_f(i['m']) - sm_of[n]) > 1e-9:
        bad_sm.append('%s: K-HLSL=%s DXC=%s' % (n, i['m'], sm_of[n]))
for g, lst in db['methods'].items():
    for mm in lst:
        n = mm['n']
        if n in sm_of and sm_of[n] is not None and to_f(mm['m']) is not None and abs(to_f(mm['m']) - sm_of[n]) > 1e-9:
            bad_sm.append('%s.%s: K-HLSL=%s DXC=%s' % (g, n, mm['m'], sm_of[n]))
print(chr(10).join(bad_sm) if bad_sm else '(なし)')
