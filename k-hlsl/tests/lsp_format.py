# -*- coding: utf-8 -*-
"""整形(textDocument/formatting)のテスト。崩れた入力を整形して、期待どおりか、2 回目で変わらないかを確かめる。"""
import json, subprocess, sys, os, threading, queue

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

def apply(text, edits):
    lines = text.split('\n')
    for e in sorted(edits, key=lambda e: -e['range']['start']['line']):
        l = e['range']['start']['line']
        s, t = e['range']['start']['character'], e['range']['end']['character']
        lines[l] = lines[l][:s] + e['newText'] + lines[l][t:]
    return '\n'.join(lines)

caps = req('initialize', {'capabilities': {}})['capabilities']
print('caps', [k for k in caps if 'ormat' in k])
uri = 'file:///fmt-test.hlsl'
def fmt(text, tab=4, spaces=True):
    send({'jsonrpc': '2.0', 'method': 'textDocument/didOpen', 'params': {'textDocument': {'uri': uri, 'languageId': 'khlsl', 'version': 1, 'text': text}}})
    e = req('textDocument/formatting', {'textDocument': {'uri': uri}, 'options': {'tabSize': tab, 'insertSpaces': spaces}})
    return apply(text, e)

bad = r'''#include "common.hlsli"
cbuffer CB : register(b0)
{
float4x4 vp;
float3 pos;
};
struct VSOut { float4 pos : SV_Position; float2 uv : TEXCOORD0; };
float4 PSMain(VSOut i) : SV_Target
{
float4 c=0;
if(i.uv.x>0.5)
c=1;
else if (i.uv.y<0.5)
{
c+=2;
}
else
c-=1;
for(int k=0;k<4;k++)
{
if (k==2) continue;
c.x+=k*2;
}
[unroll]
for (int j = 0; j < 2; j++)
c += foo(j,
j + 1);
while (c.x > 1)
c.x -= 1;
do
c.x++;
while (c.x < 3);
switch (k)
{
case 0:
c = 1;
break;
case 1:
{
c = 2;
break;
}
default:
break;
}
static const float2 offs[2] = {
float2(0,0),
float2(1,1)
};
float a = b
+ c;
  /* block
     comment */
// line
return c;
}
[numthreads(8,8,1)]
void CS(uint3 id : SV_DispatchThreadID)
{
if (id.x > 1) {
return;
}
}
'''
good = r'''#include "common.hlsli"
cbuffer CB : register(b0)
{
    float4x4 vp;
    float3 pos;
};
struct VSOut { float4 pos : SV_Position; float2 uv : TEXCOORD0; };
float4 PSMain(VSOut i) : SV_Target
{
    float4 c = 0;
    if (i.uv.x > 0.5)
        c = 1;
    else if (i.uv.y < 0.5)
    {
        c += 2;
    }
    else
        c -= 1;
    for (int k = 0; k < 4; k++)
    {
        if (k == 2) continue;
        c.x += k * 2;
    }
    [unroll]
    for (int j = 0; j < 2; j++)
        c += foo(j,
                 j + 1);
    while (c.x > 1)
        c.x -= 1;
    do
        c.x++;
    while (c.x < 3);
    switch (k)
    {
    case 0:
        c = 1;
        break;
    case 1:
        {
            c = 2;
            break;
        }
    default:
        break;
    }
    static const float2 offs[2] = {
        float2(0, 0),
        float2(1, 1)
    };
    float a = b
        + c;
    /* block
       comment */
    // line
    return c;
}
[numthreads(8, 8, 1)]
void CS(uint3 id : SV_DispatchThreadID)
{
    if (id.x > 1) {
        return;
    }
}
'''
out = fmt(bad)
ok = out == good
print('format ok:', ok)
if not ok:
    import difflib
    sys.stdout.reconfigure(encoding='utf-8')
    for l in difflib.unified_diff(good.split('\n'), out.split('\n'), 'expected', 'actual', lineterm='', n=1): print(l)
again = fmt(good)
print('idempotent:', again == good)
if again != good:
    import difflib
    for l in difflib.unified_diff(good.split('\n'), again.split('\n'), 'good', 'again', lineterm='', n=1): print(l)
tabs = fmt('void f()\n{\nif (a)\nb();\n}\n', 4, False)
print('tabs:', repr(tabs))
crlf = fmt('void f()\r\n{\r\nif (a)\r\nb();\r\n}\r\n')
print('crlf:', repr(crlf))
sys.exit(0 if ok and again == good else 1)
