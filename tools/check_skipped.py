"""tools/content の Add が、既存の見出しと重なって、スキップされていないかを調べる(書き込みはしない)。"""
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pg

skipped = []


def FakeAdd(path, md, before="## よくあるミス", key=None):
    text, _ = pg.Load(path)
    md = md.strip("\n")
    first = md.split("\n", 1)[0]
    # 本文の 2 つ目以降の見出しや、最初の長い行も、入っているか
    codes = re.findall(r"```\w*[^\n]*\n(.*?)```", md, flags=re.S)
    probe = [c.strip().split("\n")[0] for c in codes if c.strip()][:1]
    in_text = (key or first) in text
    body_in = all(c.strip().split("\n")[0][:50] in text for c in codes if c.strip())
    if in_text and not body_in:
        skipped.append((os.path.basename(CUR), path, first))
    return False


pg.Add = FakeAdd
pg.Refs = lambda *a, **k: None
pg.Dedup = lambda *a, **k: None
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "*.py"))):
    if os.path.basename(f).startswith("split"):
        continue
    CUR = f
    src = open(f, encoding="utf-8").read()
    try:
        exec(compile(src, f, "exec"), {"__name__": "x", "__file__": f})
    except SystemExit:
        pass
    except Exception as e:
        print("ERR", f, e)
print("skipped:", len(skipped))
for s in skipped:
    print(s)
