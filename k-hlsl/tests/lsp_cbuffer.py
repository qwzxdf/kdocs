# -*- coding: utf-8 -*-
"""定数バッファのレイアウト機能(ホバー・CodeLens・khlsl/cbuffers)を、言語サーバーに直接つないで確かめる。"""
import json, subprocess, sys, os, threading, queue

here = os.path.dirname(os.path.abspath(__file__))
exe = os.path.join(here, '..', 'src', 'KHlsl.Server', 'bin', 'Release', 'net472', 'KHlslServer.exe')
p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
q = queue.Queue()


def reader():
    f = p.stdout
    while True:
        h = b''
        while not h.endswith(b'\r\n\r\n'):
            c = f.read(1)
            if not c:
                return
            h += c
        n = int([x for x in h.decode().split('\r\n') if x.lower().startswith('content-length')][0].split(':')[1])
        q.put(json.loads(f.read(n).decode('utf-8')))


threading.Thread(target=reader, daemon=True).start()
nid = [0]


def send(m):
    b = json.dumps(m).encode('utf-8')
    p.stdin.write(b'Content-Length: %d\r\n\r\n' % len(b) + b)
    p.stdin.flush()


def req(method, params):
    nid[0] += 1
    i = nid[0]
    send({'jsonrpc': '2.0', 'id': i, 'method': method, 'params': params})
    while True:
        m = q.get(timeout=30)
        if m.get('id') == i:
            return m.get('result')


def note(method, params):
    send({'jsonrpc': '2.0', 'method': method, 'params': params})


path = os.path.join(here, 'cbuffer.hlsl')
src = open(path, encoding='utf-8').read()
uri = 'file:///' + path.replace('\\', '/')
caps = req('initialize', {'capabilities': {}})['capabilities']
print('codeLensProvider:', caps.get('codeLensProvider'))
note('textDocument/didOpen', {'textDocument': {'uri': uri, 'languageId': 'khlsl', 'version': 1, 'text': src}})
td = {'uri': uri}
ok = True


def check(cond, what):
    global ok
    print(('OK   ' if cond else 'FAIL ') + what)
    if not cond:
        ok = False


def pos_of(needle, delta=0, after=0):
    i = src.index(needle, after) + delta
    line = src.count('\n', 0, i)
    col = i - (src.rfind('\n', 0, i) + 1)
    return {'line': line, 'character': col}


def hover(needle, delta=1, after=0):
    h = req('textDocument/hover', {'textDocument': td, 'position': pos_of(needle, delta, after)})
    return (h or {}).get('contents', {}).get('value', '')


md = hover('cbuffer PerFrame', len('cbuffer ') + 2)
print(md)
check('PerFrame' in md and '272 バイト' in md and 'c4.w' in md, 'cbuffer 名のホバーに大きさとレジスタ')

md = hover('float time;', len('float ') + 1)
check('オフセット 76' in md, 'メンバー time のホバー: オフセット 76')

md = hover('ConstantBuffer<Data> gData', len('ConstantBuffer<Data> ') + 1)
check('gData' in md and 'tint' in md, 'ConstantBuffer 変数のホバー')

md = hover('struct Light', len('struct ') + 1)
check('Light' in md and 'color' in md, 'struct 名のホバー')

lenses = req('textDocument/codeLens', {'textDocument': td})
for l in lenses:
    print('lens', l['range']['start']['line'], l['command']['title'])
check(len(lenses) == 3, 'CodeLens が 3 つ(PerFrame / Wasteful / gData)')
check(any('並べ替えで' in l['command']['title'] for l in lenses), 'Wasteful に並べ替えの提案')

res = req('khlsl/cbuffers', {'uri': uri, 'includeStructs': False})
names = [b['name'] for b in res['blocks']]
print(names)
check(names == ['PerFrame', 'Wasteful', 'gData'], 'khlsl/cbuffers のブロック名')
pf = res['blocks'][0]
check(pf['size'] == 272, 'PerFrame の大きさ: %s' % pf['size'])
w = [b for b in res['blocks'] if b['name'] == 'Wasteful'][0]
print(w['cpp'])
print(w.get('reorder', {}).get('hlsl'))
check('reorder' in w and w['reorder']['saved'] > 0, 'Wasteful の並べ替え')
check('static_assert(sizeof(Wasteful)' in w['cpp'], 'C++ の struct と static_assert')

req('shutdown', None)
note('exit', None)
sys.exit(0 if ok else 1)
