"""新しく書くページ（1 つの関数・型 = 1 ページ）を、短い定義から作るための共通部品。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split import *  # noqa: F401,F403

RJ = "https://cpprefjp.github.io/reference/"
CR = "https://en.cppreference.com/w/cpp/"


def N(rel, title, summary, order, rank, ver, include, intro, tips, sig, args, ret, cx, ex, exout, game, mistake, sim, memo,
      rj, cr, info="", group="", compiler=None, perf=None, heading=None, ids=None, extra_fns=(), extra_body=""):
    """rel: STL からの相対パス（例: support/concepts/same_as.md）。
    ex が None のときは、実行例を載せない（sig と説明だけ）。"""
    ex_pair = (ex, exout) if ex else None
    body_fn = fn(heading or title, sig, args, ret, cx, ex_pair, ids=ids or Path(rel).stem)
    tail = dict(
        game=game,
        mistakes=[mistake] if mistake else [],
        similar=sim,
        memo=memo,
        links=[(f"cpprefjp: {title}", RJ + rj), (f"cppreference: {title}", CR + cr)],
    )
    if compiler:
        tail["compiler"] = compiler
    elif ver and ver[0] in ("20", "23", "26", "17"):
        tail["compiler"] = f"{ver[1]} の機能です。"
    else:
        tail["compiler"] = "C++11 以前から使えます。"
    return dict(
        rel=rel, title=title, summary=summary, order=order, rank=rank, ver=ver, include=include, intro=intro, tips=tips,
        fns=[body_fn] + list(extra_fns), extra=extra_body, tail=tail, info=info, group=group, perf=perf,
    )
