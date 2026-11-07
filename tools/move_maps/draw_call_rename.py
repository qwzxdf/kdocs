# graphics/draw-submission/ を graphics/draw-call/ に改名する
import os
A = "graphics/draw-submission/"
B = "graphics/draw-call/"
ROOT = os.path.join(os.getcwd(), "docs")   # リポジトリ直下で実行する
MOVES = {}
for dp, dn, fn in os.walk(os.path.join(ROOT, A)):
    for f in fn:
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/")
            MOVES[rel] = rel.replace(A, B, 1)
TITLES = {B + "index.md": "Draw Call"}
