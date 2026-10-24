# -*- coding: utf-8 -*-
"""C++ の構造体と HLSL の cbuffer の比較(khlsl/cppcompare・khlsl/cppstruct)を、言語サーバーに直接つないで確かめる。"""
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


ok = True


def check(cond, what):
    global ok
    print(('OK   ' if cond else 'FAIL ') + what)
    if not cond:
        ok = False


hp = os.path.join(here, 'cppcompare.hlsl')
cp = os.path.join(here, 'cppcompare.cpp')
req('initialize', {'capabilities': {}})
note('textDocument/didOpen', {'textDocument': {'uri': 'file:///' + hp.replace(chr(92), '/'), 'languageId': 'khlsl', 'version': 1, 'text': open(hp, encoding='utf-8').read()}})

# 1) ホバー用の下調べ
r = req('khlsl/cppstruct', {'cppPath': cp, 'word': 'PerObject', 'line': 5})
check(r['found'] and r['name'] == 'PerObject' and r['size'] == 108, 'cppstruct: PerObject の大きさ 108 (%s)' % r)
r = req('khlsl/cppstruct', {'cppPath': cp, 'word': 'alpha', 'line': 7})
check(r['found'] and r['name'] == 'PerObject', 'cppstruct: メンバーの行からも、含む struct を見つける')
r = req('khlsl/cppstruct', {'cppPath': cp, 'word': 'DirectX', 'line': 1})
check(not r['found'], 'cppstruct: struct の外では見つからない')

# 2) 比較
r = req('khlsl/cppcompare', {'cppPath': cp, 'cppStruct': 'PerObject'})
print(json.dumps({k: r[k] for k in ('mismatches', 'first', 'cppSize', 'hlslSize', 'hlslPaddedSize', 'ok')}, ensure_ascii=False))
for row in r['rows']:
    print(' ', row['path'], row['status'], row['cpp'] and row['cpp']['offset'], row['hlsl'] and row['hlsl']['offset'], row['note'][:60])
check('error' not in r, '比較できる')
check(r['first'] == 'lightDir', '最初のずれは lightDir (%s)' % r.get('first'))
byp = {x['path']: x for x in r['rows']}
check(byp['uvScale']['status'] == 'ok', 'uv_scale と uvScale は、同じ名前とみなす')
check(byp['lightDir']['status'] == 'offset' and byp['intensity']['status'] == 'shifted', 'lightDir がずれ、intensity は続き')
check(byp['world']['status'] == 'ok' and byp['tint']['status'] == 'ok', 'world と tint は一致')
check(not r['ok'] and r['cppSize'] == 108, '全体は不一致(C++ 108 バイト)')

# 3) HLSL を開いていないとき
note('textDocument/didClose', {'textDocument': {'uri': 'file:///' + hp.replace(chr(92), '/')}})
r = req('khlsl/cppcompare', {'cppPath': cp, 'cppStruct': 'PerObject'})
check('error' in r and 'HLSL' in r['error'], 'HLSL を開いていないときは、案内を返す')

req('shutdown', None)
note('exit', None)
sys.exit(0 if ok else 1)
