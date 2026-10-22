"""docs/stl の md の相対リンク（ファイルとアンカー）が切れていないかを、すばやく調べる。"""
import re, sys, glob, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / "docs"
files = [Path(p) for p in glob.glob(str(ROOT / "**/*.md"), recursive=True)]
ids = {}
def ids_of(p):
    if p not in ids:
        t = p.read_text(encoding="utf-8")
        ids[p] = set(re.findall(r"\{#([\w\-]+)", t)) | set(re.findall(r'id="([\w\-]+)"', t))
    return ids[p]
bad = 0
scope = sys.argv[1] if len(sys.argv) > 1 else "stl"
for f in files:
    if scope not in f.relative_to(ROOT).as_posix():
        continue
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"(?s)```.*?```", "", t)
    for m in re.finditer(r"\]\(([^)\s]+)\)", t):
        u = m.group(1)
        if re.match(r"(https?:|mailto:|#)", u):
            if u.startswith("#") and len(u) > 1 and u[1:] not in ids_of(f) and False:
                pass
            continue
        path, _, anc = u.partition("#")
        if not path:
            continue
        tgt = (f.parent / path).resolve()
        if tgt.is_dir():
            tgt = tgt / "index.md"
        if not tgt.exists():
            print(f"{f.relative_to(ROOT)}: リンク切れ {u}"); bad += 1
        elif anc and tgt.suffix == ".md" and anc not in ids_of(tgt):
            pass
print("リンク切れ", bad)
