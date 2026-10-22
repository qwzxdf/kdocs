"""STL の新しいページ（1 名前 = 1 ページ）を、短い定義から作る部品。

P(...) で 1 ページ。hub= に「まとめページ」の相対パス（docs/stl から）を渡すと、
「このページを読む前に」のリンクと、まとめページの表への追記を自動で行う。
本文中の `(@/basics/x.md)` は、docs からのパスとして相対パスに直す。
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split import STL, fn, page, tail, write  # noqa: E402

RJ = "https://cpprefjp.github.io/reference/"
CR = "https://en.cppreference.com/w/cpp/"
RANK = {"must": "必須", "often": "よく使う", "sometimes": "たまに", "rare": "知ってるだけ"}
BAR = chr(124)
BS = chr(92)
GROUPS = {
    "support/functional/": "関数オブジェクトと呼び出し（<functional>）",
    "memory/new_delete/": "new / delete まわり",
    "support/exceptions/": "標準の例外",
    "support/iterator/": "イテレータの道具（<iterator>）",
    "support/type_traits/": "型の性質（<type_traits>）",
    "support/concepts/": "コンセプト（<concepts>）",
    "utilities/chrono/": "時間（std::chrono）",
    "numeric/cmath/": "数学関数（<cmath>）",
}
import json

_MF = Path(__file__).resolve().parent / "moves.json"
_MOVES = json.loads(_MF.read_text(encoding="utf-8")) if _MF.exists() else {}
HUB_ROWS = {}  # hub 相対パス -> [(rel, 表示名, rank, 説明, ver)]


def _rel_link(from_rel, to_rel):
    return os.path.relpath(STL / to_rel, (STL / from_rel).parent).replace(BS, "/")


def esc(text):
    """表のセルに入れる文字列の、縦棒をエスケープする。"""
    return text.replace(BAR, BS + BAR)


def P(rel, name, summary, rank, include, intro, tips, game, miss, sim, memo, *,
      secs=None, sig=None, args=None, ret="", cx="", code=None, out=None, notes="",
      ver=None, hub=None, hubname=None, group="", rj=None, cr=None, compiler=None,
      order=900, perf=None, info=None, title=None, ids=None, heading=None, extra="", hubrow=True):
    """secs: [fn(...) の文字列] を渡すと、sig/args/ret/cx の代わりに使う。
    ver: ('20','C++20')。miss: (見出し, 本文) か None。sim: [(名前, 違い)]。game: [(場面, 書き方)]。"""
    title = title or name
    if not group:
        group = next((g for k, g in GROUPS.items() if rel.startswith(k)), "")
    stem = Path(rel).stem
    if secs is None:
        secs = [fn(heading or name, sig, args, ret, cx, None, notes=notes, ids=ids or stem)]
    body = "## 関数の詳しい説明\n\n" + "\n".join(secs)
    if code:
        body += "\n\n## 実際に動かしてみる\n\n```cpp\n" + code.strip("\n") + "\n```\n"
        if out:
            body += '\n```text title="実行結果"\n' + out.strip("\n") + "\n```\n"
    if extra:
        body += "\n" + extra.strip("\n") + "\n"
    if compiler is None:
        compiler = f"{ver[1]} から使えます。" if ver else "C++11 以前から使えます。"
    links = []
    if rj:
        links.append((f"cpprefjp: {title}", RJ + rj))
    if cr:
        links.append((f"cppreference: {title}", CR + cr))
    if not links:
        links.append((f"cppreference: {title}", "https://en.cppreference.com/w/cpp"))
    tl = tail(game, [miss] if miss else [], sim, memo, links, compiler=compiler)
    if info is None and hub:
        hname = hubname or Path(hub).stem
        info = f"[{hname}]({_rel_link(rel, hub)}) の概要を先に読むと分かりやすいです。"
    text = page(rel, title, summary, order, rank, ver, include, intro, tips, body, tl, perf=perf, info=info or "", group=group)
    docs = STL.parent
    here = (STL / rel).parent
    text = re.sub(r"\(@/([^)#]*)", lambda m: "(" + os.path.relpath(docs / m.group(1), here).replace(BS, "/"), text)
    write(rel, text)
    if hub and hubrow:
        HUB_ROWS.setdefault(hub, []).append((rel, title, rank, summary, ver))


def flush_hubs():
    """P() で作ったページを、まとめページの最初の表の最後の行の後ろに足す（すでに載っていれば足さない）。"""
    for hub, rows in HUB_ROWS.items():
        p = STL / hub
        text = p.read_text(encoding="utf-8")
        lines = text.split("\n")
        start = next((i for i, l in enumerate(lines) if l.startswith(BAR) and ("重要度" in l or "何をする" in l)), None)
        if start is None:
            print("HUB table not found:", hub)
            continue
        end = start + 1
        while end + 1 < len(lines) and lines[end + 1].startswith(BAR):
            end += 1
        cols = lines[start].count(BAR) - 1
        add = []
        for rel, title, rank, summary, ver in rows:
            link = _rel_link(hub, rel)
            if f"]({link})" in text:
                continue
            first = f"[`{title}`]({link})"
            rk = f'<span class="rank rank-{rank}">{RANK[rank]}</span>'
            vs = f' <span class="ver ver-{ver[0]}">{ver[1]}</span>' if ver else ""
            summ = esc(summary) + vs
            if cols == 2:
                add.append(f"{BAR} {first} {BAR} {summ} {BAR}")
            else:
                add.append(f"{BAR} {first} {BAR} {rk} {BAR} {summ} {BAR}" + f" {BAR}" * (cols - 3))
        lines[end + 1:end + 1] = add
        p.write_text("\n".join(lines), encoding="utf-8", newline="")
        print("hub", hub, "+", len(add))
    HUB_ROWS.clear()


def add_secs(rel, secs_text, after=None):
    """既存ページの「関数の詳しい説明」の最後（## 実際に動かしてみる などの手前）に、節を足す。"""
    p = STL / rel
    t = p.read_text(encoding="utf-8")
    first = re.search(r"\{#([\w-]+)", secs_text)
    moved = _MOVES.get("stl/" + rel, {}).get("ids", {}) if _MOVES else {}
    if first and first.group(1) in moved:
        return
    if first and re.search(r"\{#" + re.escape(first.group(1)) + r"[ }]", t):
        return
    m = re.search(r"(?m)^## (実際に動かしてみる|ゲームでの使いどころ|パフォーマンス|よくあるミス|類似|コンパイラ対応)", t)
    pos = m.start() if m else len(t)
    t = t[:pos].rstrip("\n") + "\n\n" + secs_text.strip("\n") + "\n\n" + t[pos:]
    p.write_text(t, encoding="utf-8", newline="")
    print("add_secs", rel)


def add_list(hub, heading, items):
    """まとめページに表のない場合に、「## heading」の節（リンクの表）を、「ゲームでの使いどころ」の手前に足す。
    items: [(相対パス, 表示名, 一言)]。すでにリンクがあるものは足さない。"""
    p = STL / hub
    t = p.read_text(encoding="utf-8")
    rows = []
    for rel, name, one in items:
        link = _rel_link(hub, rel)
        if f"]({link})" in t:
            continue
        rows.append(f"{BAR} [`{name}`]({link}) {BAR} {one} {BAR}")
    if not rows:
        return
    block = f"## {heading}\n\n{BAR} 名前 {BAR} 何をする {BAR}\n{BAR} --- {BAR} --- {BAR}\n" + "\n".join(rows) + "\n\n"
    m = re.search(r"(?m)^## (ゲームでの使いどころ|よくあるミス)", t)
    pos = m.start() if m else len(t)
    p.write_text(t[:pos] + block + t[pos:], encoding="utf-8", newline="")
    print("add_list", hub, len(rows))


AUTO_INC = [
    (r"std::vector", "vector"), (r"std::list", "list"), (r"std::deque", "deque"), (r"std::forward_list", "forward_list"),
    (r"std::string_view", "string_view"), (r"std::string", "string"), (r"std::(ptrdiff_t|size_t)", "cstddef"),
    (r"std::(is_\w+_v|remove_reference_t|is_same)", "type_traits"), (r"std::map", "map"), (r"std::numeric_limits", "limits"),
    (r"std::(i|o)stringstream", "sstream"), (r"std::ranges::(copy|find|sort)", "algorithm"),
    (r"std::(back_inserter|move_iterator|counted_iterator|istreambuf_iterator|ostreambuf_iterator|default_sentinel|move_sentinel|front_insert_iterator|insert_iterator|back_insert_iterator)", "iterator"),
    (r"std::(cout|cin|cerr|clog)", "iostream"), (r"std::(setw|setfill|setprecision|setbase|setiosflags|resetiosflags|quoted|get_money|put_money|get_time|put_time)", "iomanip"),
    (r"std::osyncstream", "syncstream"), (r"std::(ifstream|ofstream|fstream)", "fstream"), (r"std::(tm|time_t)", "ctime"), (r"std::(ostream|istream)", "ostream"),
    (r"std::tuple", "tuple"), (r"std::array", "array"), (r"std::views::|std::ranges::", "ranges"), (r"std::println|std::print", "print"),
]


def Q(rel, name, summary, rank, include, intro, tips, sig, args, ret, body, out, *, use, miss, sim=(), cx="定数", ver=None, hub=None, info=None, rj=None, cr=None,
      memo=None, pre="", **kw):
    """C ライブラリなど、型どおりの関数 1 つのページを短く書くための近道。
    body: main の中身（インデントなし、各行を \n でつなぐ）。pre: main の前に置くコード（関数や構造体）。
    use: ゲームでの使いどころ（1 つ）。miss: (見出し, 本文)。sim: [(名前, 違い)]。"""
    incs = include if isinstance(include, (list, tuple)) else [include]
    heads = set(list(incs) + list(kw.pop("extra_inc", [])))
    for pat, h in AUTO_INC:
        if re.search(pat, body + pre):
            heads.add(h)
    heads = sorted(heads)
    code = "".join(f"#include <{h}>\n" for h in heads) + ("\n" + pre.strip("\n") + "\n" if pre else "") + "\nint main() {\n" + "\n".join(("  " + l) if l else "" for l in body.split("\n")) + "\n}"
    code = code.replace("#include <print>\n", "#include <print>\n") if "print" in heads else code
    P(rel, name, summary, rank, incs[0], intro, tips, [("使いどころ", use)], miss, list(sim), memo or [summary.rstrip("。"), tips[0].rstrip("。"), "戻り値と失敗時の動きを確かめて使う"],
      sig=sig, args=args, ret=ret, cx=cx, code=code, out=out, ver=ver, hub=hub, info=info, rj=rj, cr=cr, **kw)
