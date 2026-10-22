# -*- coding: utf-8 -*-
"""K-HLSL のデータにある名前が、DXC に実在するかを、DXC 自身に聞いて確かめる。

- メソッド: `obj.NAME();` を呼んで、"no member named" になれば、無い物
- 型: 宣言して、"unknown type name" になれば、無い物
- 定数: `NAME` を参照して、"undeclared identifier" になれば、無い物
- 属性: `[NAME]` を付けて、"unknown attribute" になれば、無い物

使い方: python data/ref/verify_dxc.py [dxc.exe のパス]
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DXC = sys.argv[1] if len(sys.argv) > 1 else r'C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\dxc.exe'
db = json.load(open(os.path.join(ROOT, 'src', 'KHlsl.Server', 'hlsl.json'), encoding='utf-8'))

OBJECTS = {
    'tex': 'Texture2D<float4> o;', 'texlod': 'Texture2D<float4> o;', 'gather': 'Texture2D<float4> o;',
    'ms': 'Texture2DMS<float4> o;', 'rwtex': 'RWTexture2D<float4> o;', 'buf': 'Buffer<float4> o;',
    'sbuf': 'StructuredBuffer<float4> o;', 'sbufrw': 'RWStructuredBuffer<float4> o;',
    'append': 'AppendStructuredBuffer<float4> o;', 'consume': 'ConsumeStructuredBuffer<float4> o;',
    'bab': 'ByteAddressBuffer o;', 'babrw': 'RWByteAddressBuffer o;', 'stream': 'TriangleStream<float4> o;',
    'patch': 'InputPatch<float4, 3> o;', 'feedback': 'FeedbackTexture2D<SAMPLER_FEEDBACK_MIN_MIP> o;',
    'rayquery': 'RayQuery<RAY_FLAG_NONE> o;', 'hitobject': 'dx::HitObject o;',
}


def run(code, target='lib_6_9'):
    path = os.path.join(tempfile.gettempdir(), 'khlsl_verify.hlsl')
    open(path, 'w', encoding='utf-8').write(code)
    p = subprocess.run([DXC, '-T', target, '-HV', '2021', '-enable-16bit-types', '-Fo', 'NUL', '-ferror-limit=0', path],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return p.stderr + p.stdout


def chunks(names, size=25):
    names = list(names)
    for i in range(0, len(names), size):
        yield names[i:i + size]


def find_missing(pattern, names, build):
    missing = set()
    for group in chunks(names):
        out = run(build(group))
        for m in re.finditer(pattern, out):
            missing.add(m.group(1))
    return missing


bad = {}

# 関数は、DXC が、引数の数が違う呼び出しにも "undeclared identifier" と返すので、この方法では確かめられない。
# 関数の名前は、audit_dxc.py で、DXC の定義表(gen_intrin_main.txt)と突き合わせる。

# メソッド
for grp, lst in db['methods'].items():
    if grp not in OBJECTS:
        continue
    names = [m['n'] for m in lst]
    decl = OBJECTS[grp]
    miss = find_missing(r"no member named '(\w+)'", names,
                        lambda g, decl=decl: decl + '\nvoid f() {\n' + ''.join('  o.%s();\n' % n for n in g) + '}\n')
    miss &= set(names)
    if miss:
        bad['メソッド ' + grp] = miss

# 型
types = [t['n'] for t in db['types'] if '::' not in t['n']]
type_miss = set()
for t in types:
    code = '%s v;\n' % t
    for cand in ('%s<float4>' % t, '%s<float4, 3>' % t, '%s<0>' % t, t):
        out = run('void f() { %s v; }\n' % cand)
        if not re.search(r"unknown type name|undeclared identifier|use of undeclared", out):
            break
    else:
        type_miss.add(t)
bad['型'] = type_miss

# 定数
consts = [c['n'] for c in db['constants']]
bad['定数'] = find_missing(r"use of undeclared identifier '(\w+)'", consts,
                         lambda g: 'void f() {\n' + ''.join('  int v%d = (int)%s;\n' % (i, n) for i, n in enumerate(g)) + '}\n') & set(consts)

# 属性
attrs = [a['n'] for a in db['attributes'] if '::' not in a['n']]
bad['属性'] = find_missing(r"unknown attribute '(\w+)'", attrs,
                         lambda g: ''.join('[%s] void f%d() {}\n' % (n, i) for i, n in enumerate(g))) & set(attrs)

# 既知の物: SM 6.10 はプレビュー(インストール済みの DXC 1.9 は未対応)、旧式の sampler 型は DXC が受け付けない
KNOWN = {
    'メソッド rayquery': {'CandidateTriangleObjectPositions', 'CommittedTriangleObjectPositions'},
    '型': {'sampler1D', 'sampler2D', 'sampler3D', 'samplerCUBE'},
}
total = 0
for k, v in bad.items():
    known = v & KNOWN.get(k, set())
    unexpected = v - known
    if known:
        print('%s(既知): %s' % (k, ', '.join(sorted(known))))
    if unexpected:
        print('%s: %s' % (k, ', '.join(sorted(unexpected))))
        total += len(unexpected)
print()
print('DXC に無かった名前(既知を除く): %d 件' % total)
sys.exit(1 if total else 0)
