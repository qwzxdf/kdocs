"""std::views の 1 ページぶんを作るための関数（views_*.py から使う）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split import *  # noqa: F401,F403

RJ = "https://cpprefjp.github.io/reference/ranges/"
CR = "https://en.cppreference.com/w/cpp/ranges/"
RANGES = "[ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。"
V20 = ("20", "C++20")
V23 = ("23", "C++23")

GROUP = "ビュー（std::views）"


def V(name, order, rank, ver, summary, intro, tips, sig, args, ret, cx, example, game, mistakes, sim, memo,
      view_class=None, extra_fns=(), anim=None, info=RANGES, header="ranges", compiler=None, notes="", title=None):
    """ビュー 1 つのページ。name は views:: の後の名前（view_class はクラス名。省略時 name_view）。"""
    cls = view_class or f"{name}_view"
    ttl = title or f"std::views::{name}"
    body = [fn(f"views::{name}", sig, args, ret, cx, example, anim, notes=notes, ids=name)] + list(extra_fns)
    comp = compiler or ("C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。" if ver == V23 else "C++20 の機能です。主要なコンパイラすべてで使えます。")
    return dict(
        rel=f"algorithms/views/{name}.md", title=ttl, summary=summary, order=order, rank=rank, ver=ver, include=header,
        intro=intro, tips=tips, fns=body, info=info, group=GROUP,
        tail=dict(
            game=game, mistakes=mistakes, similar=sim, memo=memo, compiler=comp,
            links=[(f"cpprefjp: std::ranges::{cls}", RJ + f"{cls}.html"), (f"cppreference: std::ranges::{cls}", CR + cls)],
        ),
    )
