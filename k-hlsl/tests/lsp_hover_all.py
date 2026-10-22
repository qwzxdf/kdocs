# -*- coding: utf-8 -*-
"""指定した HLSL ファイルの中の、組み込み API の名前すべてに、ホバーの説明が出るかを確かめる。

使い方: python tests/lsp_hover_all.py tests/dxr.hlsl
"""
import json
import os
import queue
import re
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exe = os.path.join(ROOT, 'src', 'KHlsl.Server', 'bin', 'Release', 'net472', 'KHlslServer.exe')
db = json.load(open(os.path.join(ROOT, 'src', 'KHlsl.Server', 'hlsl.json'), encoding='utf-8'))
path = os.path.abspath(sys.argv[1])
src = open(path, encoding='utf-8').read()
uri = 'file:///' + path.replace(chr(92), '/')

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
        m = q.get(timeout=60)
        if m.get('id') == i:
            return m.get('result')


req('initialize', {'capabilities': {}})
send({'jsonrpc': '2.0', 'method': 'textDocument/didOpen',
      'params': {'textDocument': {'uri': uri, 'languageId': 'hlsl', 'version': 1, 'text': src}}})

api = set()
for i in db['intrinsics']:
    api.add(i['n'])
for lst in db['methods'].values():
    for m in lst:
        api.add(m['n'])
for t in db['types']:
    api.add(t['n'])
for c in db['constants']:
    api.add(c['n'])
for a in db['attributes']:
    api.add(a['n'])
for s in db['special']:
    api.add(s['n'])
api = {n for n in api if '::' not in n and len(n) > 1}

# ソースの中で、API の名前に当たる語を、最初の 1 回ずつ
seen = {}
# コメントの中は、ホバーの対象にならないので、空白にして探す
scan = re.sub(r'//[^\n]*', lambda mm: ' ' * len(mm.group(0)), src)
scan = re.sub(r'/\*.*?\*/', lambda mm: re.sub(r'[^\n]', ' ', mm.group(0)), scan, flags=re.S)
for m in re.finditer(r'[A-Za-z_]\w*', scan):
    w = m.group(0)
    if w in api and w not in seen:
        seen[w] = m.start()
# dx:: の語
for m in re.finditer(r'dx::\w+(?:::\w+)?', scan):
    seen.setdefault(m.group(0), m.start() + 4)

miss = []
for w, off in sorted(seen.items()):
    line = src.count('\n', 0, off)
    col = off - (src.rfind('\n', 0, off) + 1)
    h = req('textDocument/hover', {'textDocument': {'uri': uri}, 'position': {'line': line, 'character': col + 1}})
    if not h or not h.get('contents', {}).get('value'):
        miss.append(w)
print('ホバーを確かめた API: %d 個、説明が出なかった物: %d 個' % (len(seen), len(miss)))
if miss:
    print('  ' + ', '.join(miss))
req('shutdown', None)
send({'jsonrpc': '2.0', 'method': 'exit'})
sys.exit(1 if miss else 0)
