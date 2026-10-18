import glob, io, re, sys, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sec = collections.defaultdict(lambda: [0, 0, 0, 0, []])
for f in glob.glob("docs/graphics/**/*.md", recursive=True):
    n = f.replace(chr(92), "/").replace("docs/graphics/", "")
    if n.endswith("index.md") or "comparison" in n or n.count("/") == 0:
        continue
    s = sec[n.split("/")[0]]
    t = open(f, encoding="utf-8").read()
    s[0] += 1
    hl = "```hlsl" in t
    d3 = bool(re.search(r"CreateTexture|CreateBuffer|Dispatch\(|DrawIndexed|DrawInstanced|OMSetRenderTargets|CSSetShader|PSSetShader|DXR|TraceRay", t))
    if hl: s[1] += 1
    if d3: s[2] += 1
    if not hl and not d3: s[4].append(n)
for k, v in sorted(sec.items()):
    print(k, "pages", v[0], "hlsl", v[1], "d3d11/api", v[2], "neither", len(v[4]))
