"""表形式のデータから、「元ページの節を取り出して 1 ページにする」ための共通部品。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split import *  # noqa: F401,F403

RJ = "https://cpprefjp.github.io/reference/"
CR = "https://en.cppreference.com/w/cpp/"


def make(folder, old_rel, rows, *, include, info, compiler, group, rj_dir, cr_dir, ver_default=None, perf=None, rj_ext=".html"):
    """rows: dict のリスト。
    キー: nm(ファイル名) title summary order rank intro tips ids game mistakes sim memo [ver] [rj] [cr] [body] [fns]"""
    src = sections(read(old_rel))
    specs = []
    moves = {}
    for r in rows:
        ver = r.get("ver", ver_default)
        if "fns" in r:
            fns = r["fns"]
        elif "ids" in r:
            fns = [take(src, r["ids"])]
            for i in r["ids"]:
                moves[i] = f"stl/{folder}/{r['nm']}.md"
        else:
            fns = []
        rj = r.get("rj", r["nm"])
        cr = r.get("cr", r["nm"])
        spec = dict(
            rel=f"{folder}/{r['nm']}.md", title=r["title"], summary=r["summary"], order=r["order"], rank=r["rank"], perf=r.get("perf", perf),
            ver=ver, include=r.get("include", include), intro=r["intro"], tips=r["tips"], info=r.get("info", info), group=group,
            tail=dict(
                game=r["game"], mistakes=r["mistakes"], similar=r["sim"], memo=r["memo"],
                links=[(f"cpprefjp: {r['title']}", RJ + rj_dir + rj + rj_ext), (f"cppreference: {r['title']}", CR + cr_dir + cr)],
                compiler=r.get("compiler", compiler),
            ),
        )
        if "body" in r:
            spec["body"] = r["body"]
        else:
            spec["fns"] = fns
        specs.append(spec)
    return specs, moves
