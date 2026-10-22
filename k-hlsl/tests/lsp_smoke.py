# -*- coding: utf-8 -*-
"""言語サーバーを stdio で起動して、主要な機能を一通り呼ぶスモーク テスト。"""
import json, subprocess, sys, os, time, threading, queue

exe = os.path.join(os.path.dirname(__file__), '..', 'src', 'KHlsl.Server', 'bin', 'Release', 'net472', 'KHlslServer.exe')
p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
q = queue.Queue()

def reader():
    f = p.stdout
    while True:
        h = b''
        while not h.endswith(b'\r\n\r\n'):
            c = f.read(1)
            if not c: return
            h += c
        n = int([x for x in h.decode().split('\r\n') if x.lower().startswith('content-length')][0].split(':')[1])
        q.put(json.loads(f.read(n).decode('utf-8')))
threading.Thread(target=reader, daemon=True).start()

nid = [0]
def send(m):
    b = json.dumps(m).encode('utf-8')
    p.stdin.write(b'Content-Length: %d\r\n\r\n' % len(b) + b); p.stdin.flush()
def req(method, params):
    nid[0] += 1; i = nid[0]
    send({'jsonrpc': '2.0', 'id': i, 'method': method, 'params': params})
    while True:
        m = q.get(timeout=30)
        if m.get('id') == i: return m.get('result')
def note(method, params): send({'jsonrpc': '2.0', 'method': method, 'params': params})

src = open(os.path.join(os.path.dirname(__file__), 'sample.hlsl'), encoding='utf-8').read()
uri = 'file:///' + os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample.hlsl')).replace(chr(92), '/')
print('init', list(req('initialize', {'capabilities': {}})['capabilities'].keys()))
note('textDocument/didOpen', {'textDocument': {'uri': uri, 'languageId': 'khlsl', 'version': 1, 'text': src}})

def pos_of(needle, after=0, delta=0):
    i = src.index(needle, after) + delta
    line = src.count('\n', 0, i); col = i - (src.rfind('\n', 0, i) + 1)
    return {'line': line, 'character': col}
td = {'uri': uri}

h = req('textDocument/hover', {'textDocument': td, 'position': pos_of('ResourceDescriptorHeap[', 0, 3)})
print('hover heap:', (h or {}).get('contents', {}).get('value', '')[:80].replace('\n', ' '))
h = req('textDocument/hover', {'textDocument': td, 'position': pos_of('WaveActiveSum', 0, 3)})
print('hover Wave:', (h or {}).get('contents', {}).get('value', '')[:90].replace('\n', ' '))
h = req('textDocument/hover', {'textDocument': td, 'position': pos_of('.SampleLevel', 0, 3)})
print('hover method:', (h or {}).get('contents', {}).get('value', '')[:90].replace('\n', ' '))
h = req('textDocument/hover', {'textDocument': td, 'position': pos_of('SV_DispatchThreadID', 0, 3)})
print('hover sem:', (h or {}).get('contents', {}).get('value', '')[:60].replace('\n', ' '))
h = req('textDocument/hover', {'textDocument': td, 'position': pos_of('Lighting(', 0, 2)})
print('hover user fn:', (h or {}).get('contents', {}).get('value', '')[:90].replace('\n', ' '))

# 補完: 'gTex.' の後
i = src.index('//COMPLETE_DOT'); 
src2 = src.replace('//COMPLETE_DOT', 'gTex.')
note('textDocument/didChange', {'textDocument': {'uri': uri, 'version': 2}, 'contentChanges': [{'text': src2}]})
line = src2.count('\n', 0, i); col = len('    gTex.')
c = req('textDocument/completion', {'textDocument': td, 'position': {'line': line, 'character': col}})
names = [x['label'] for x in (c or {}).get('items', [])]
print('complete gTex.:', len(names), names[:8])
src3 = src.replace('//COMPLETE_DOT', 'Wav')
note('textDocument/didChange', {'textDocument': {'uri': uri, 'version': 3}, 'contentChanges': [{'text': src3}]})
c = req('textDocument/completion', {'textDocument': td, 'position': {'line': line, 'character': len('    Wav')}})
names = [x['label'] for x in (c or {}).get('items', [])]
print('complete general:', len(names), 'WaveActiveSum' in names, 'ResourceDescriptorHeap' in names, 'Lighting' in names)

sh = req('textDocument/signatureHelp', {'textDocument': td, 'position': pos_of('lerp(', 0, 5)})
print('sighelp:', (sh or {}).get('signatures', [{}])[0].get('label'))
ds = req('textDocument/documentSymbol', {'textDocument': td})
print('symbols:', [x['name'] for x in ds][:14])
src4 = src.replace('float sum = WaveActiveSum(c.x);', 'float sum = WaveActiveSum(c.x) + undefinedVar;')
note('textDocument/didChange', {'textDocument': {'uri': uri, 'version': 4}, 'contentChanges': [{'text': src4}]})
note('textDocument/didSave', {'textDocument': td, 'text': src4})
t0 = time.time(); diag = None
while time.time() - t0 < 40:
    try: m = q.get(timeout=1)
    except queue.Empty: continue
    if m.get('method') == 'textDocument/publishDiagnostics' and m['params']['uri'] == uri: diag = m['params']['diagnostics']; break
    if m.get('method') == 'window/showMessage': print('showMessage', m['params']['message'][:80])
print('diagnostics:', None if diag is None else [(d['range']['start']['line'] + 1, d['severity'], d['message'][:70]) for d in diag])
req('shutdown', None); note('exit', None)
