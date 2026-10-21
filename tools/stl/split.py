"""1 ページにまとまっている STL ページを、名前ごとのページに分けるための道具。

元のページの「### 見出し {#id}」の節をそのまま取り出して、新しいページに並べる。
導入・ポイント・おわりの節は、呼び出し側が文字列で渡す。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "docs" / "stl"

RANK_LABEL = {"must": "必須", "often": "よく使う", "sometimes": "たまに", "rare": "知ってるだけ"}
PERF = {4: "◎ 速い", 3: "○ 普通", 2: "△ やや重い", 1: "× 重い"}
TAGS = {
    "containers": "コンテナ",
    "algorithms": "アルゴリズム",
    "utilities": "ユーティリティ",
    "memory": "メモリ",
    "io": "入出力・文字列",
    "numeric": "数値",
    "concurrency": "並行処理",
    "support": "型・言語サポート",
}


def read(rel):
    return (STL / rel).read_text(encoding="utf-8")


def sections(text):
    """'### ... {#id}' の節を {id: 本文} で返す（次の ### か ## の手前まで）。"""
    out = {}
    parts = re.split(r"(?m)^(?=#{2,3} )", text)
    for p in parts:
        m = re.match(r"### .*\{#([\w-]+)[^}]*\}", p)
        if m:
            out[m.group(1)] = p.rstrip("\n") + "\n"
    return out


def top_section(text, heading):
    """'## 見出し' の節を返す（次の ## の手前まで）。"""
    m = re.search(r"(?m)^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S)
    return m.group(1).strip("\n") + "\n" if m else ""


def page(
    rel,
    title,
    summary,
    order,
    rank,
    ver,
    include,
    intro,
    tips,
    body,
    tail,
    perf=None,
    info="",
    group="",
):
    """ページ 1 枚ぶんの文字列を作る。ver は ('20', 'C++20') など。"""
    folder = rel.split("/")[0]
    tag = TAGS[folder]
    fm = ["---", f"title: {title}", "summary: " + chr(34) + summary.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34)) + chr(34), f"order: {order}"]
    if group:
        fm.append(f"group: {group}")
    fm += ["tags:", f"  - {tag}", "---", ""]
    badges = [f'<span class="rank rank-{rank}">{RANK_LABEL[rank]}</span>']
    if perf:
        badges.append(f'<span class="perf perf-{perf}">{PERF[perf]}</span>')
    if ver:
        badges.append(f'<span class="ver ver-{ver[0]}">{ver[1]}</span>')
    inc = include if include.startswith("`") else f"`#include <{include}>`"
    badges.append(inc)
    out = fm + [f"# {title}", "", '<div class="page-badges" markdown>'] + badges + ["</div>", ""]
    out += [intro.strip("\n"), ""]
    if tips:
        out += ['!!! tip "ポイント"'] + [f"    - {t}" for t in tips] + [""]
    if info:
        out += ['!!! info "このページを読む前に"', f"    {info}", ""]
    out += [body.strip("\n"), "", tail.strip("\n"), ""]
    text = "\n".join(out)
    return text


def write(rel, text):
    p = STL / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="")
    print("wrote", rel, len(text))


MOVES_FILE = ROOT / "tools" / "stl" / "moves.json"


def record_moves(old_rel, mapping, default=None):
    """old_rel の節 id が、どの新しいページに移ったかを moves.json に足す。
    mapping: {id: new_rel}。default: 見出しの id に当てはまらないリンクの行き先。"""
    data = json.loads(MOVES_FILE.read_text(encoding="utf-8")) if MOVES_FILE.exists() else {}
    e = data.setdefault(old_rel, {"default": default, "ids": {}})
    if default:
        e["default"] = default
    e["ids"].update(mapping)
    MOVES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def tail(game, mistakes, similar, memo, links, compiler="C++20 の機能です。主要なコンパイラすべてで使えます。", perf_note=None, ub=None):
    """おわりの節をまとめて作る。
    game: [(場面, 書き方)]  mistakes: [(見出し, 本文)]  similar: [(名前, 違い)]
    memo: [まとめ]  links: [(ラベル, URL)]  ub: [(やったこと, 結果)]"""
    t = ["## ゲームでの使いどころ", "", "| 場面 | 書き方 |", "| --- | --- |"]
    t += [f"| {a} | {b} |" for a, b in game]
    if perf_note:
        t += ["", "## パフォーマンス", "", perf_note]
    if ub:
        t += ["", "## 未定義動作・例外", "", "| やったこと | 結果 |", "| --- | --- |"]
        t += [f"| {a} | {b} |" for a, b in ub]
    if mistakes:
        t += ["", "## よくあるミス", ""]
        for h, b in mistakes:
            body = "\n".join(("    " + l) if l else "" for l in b.strip("\n").split("\n"))
            t += [f'??? failure "{h}"', body, ""]
        t.pop()
    if similar:
        t += ["", "## 類似", "", "| 名前 | 違い |", "| --- | --- |"] + [f"| {a} | {b} |" for a, b in similar]
    t += ["", "## コンパイラ対応", "", compiler, "", "## これだけ覚える", "", '!!! abstract "まとめ"']
    t += [f"    - [x] {s}" for s in memo]
    t += ["", "## 関連ページ", ""] + [f"- [{a}]({b})" for a, b in links]
    return "\n".join(t)


def take(src_sections, ids):
    """節を順に並べる。"""
    return "\n".join(src_sections[i] for i in ids)


def body_of(sec, ids, extra=""):
    return "## 関数の詳しい説明\n\n" + take(sec, ids) + ("\n" + extra if extra else "")


def cpp(name, cpprefjp=None):
    """cpprefjp / cppreference へのリンク（cppreference は引数に URL のパスを渡す）。"""
    return None


def run(specs, delete=()):
    """specs: ページの dict のリスト。先に元のページの節を全部読み、そのあと書き込む。
    dict のキー: rel, title, summary, order, rank, ver, include, intro, tips, body (文字列) または
    src + ids (+ extra)、tail(dict)、perf、info、group"""
    cache = {}
    for s in specs:
        if "src" in s and s["src"] not in cache:
            cache[s["src"]] = sections(read(s["src"]))
    moves = {}
    for s in specs:
        if "src" in s:
            body = body_of(cache[s["src"]], s["ids"], s.get("extra", ""))
            for i in s["ids"]:
                moves.setdefault(s["src"], {})[i] = s["rel"]
        elif "fns" in s:
            body = "## 関数の詳しい説明" + chr(10)*2 + chr(10).join(s["fns"]) + (chr(10) + s["extra"] if s.get("extra") else "")
        else:
            body = s["body"]
        text = page(
            s["rel"], s["title"], s["summary"], s.get("order", 500), s["rank"], s.get("ver"), s["include"],
            s["intro"], s.get("tips", []), body, tail(**s["tail"]), perf=s.get("perf"),
            info=s.get("info", ""), group=s.get("group", ""),
        )
        write(s["rel"], text)
    for old, mp in moves.items():
        first = next(s["rel"] for s in specs if s.get("src") == old)
        record_moves("stl/" + old, {k: "stl/" + v for k, v in mp.items()}, "stl/" + first)
    for d in delete:
        p = STL / d
        if p.exists():
            p.unlink()
            print("deleted", d)


def fn(name, sig, args=None, ret="", cx="", example=None, anim=None, notes="", ids=None, ver=None, heading=None, extra_examples=()):
    """関数 1 つぶんの節を作る。
    name: 見出しに出す名前  sig: 宣言 (cpp)  args: [(名前, 型, 意味, 省略時)]  ret: 戻り値  cx: 計算量
    example: (コード, 実行結果)  anim: アニメーションのブロック(data-label, 本文)  notes: 補足(markdown)"""
    aid = ids or re.sub(r"[^\w]+", "_", name.split("::")[-1]).strip("_")
    h = f"### {heading or name}"
    if ver:
        h += f' <span class="ver ver-{ver[0]}">{ver[1]}</span>'
        h += f' {{#{aid} data-toc-label="{heading or name}"}}'
    else:
        h += f" {{#{aid}}}"
    out = [h, "", "```cpp", sig.strip("\n"), "```", ""]
    if args:
        has_def = any(len(a) > 3 for a in args)
        if has_def:
            out += ["| 引数 | 型 | 意味 | 省略すると |", "| --- | --- | --- | --- |"]
            out += [f"| `{a[0]}` | {a[1]} | {a[2]} | {a[3] if len(a) > 3 else ''} |" for a in args]
        else:
            out += ["| 引数 | 型 | 意味 |", "| --- | --- | --- |"]
            out += [f"| `{a[0]}` | {a[1]} | {a[2]} |" for a in args]
        out.append("")
    if ret:
        out.append(f"- 戻り値: {ret}")
    if cx:
        out.append(f"- 計算量: {cx}")
    if ret or cx:
        out.append("")
    if anim:
        label, lines = anim
        out += [f'<div class="anim" data-label="{label}">'] + lines + ["</div>", ""]
    if notes:
        out += [notes.strip("\n"), ""]
    exs = [example] if example else []
    exs += list(extra_examples)
    for code, res in exs:
        out += ["```cpp", code.strip("\n"), "```", "", '```text title="実行結果"', res.strip("\n"), "```", ""]
    return "\n".join(out).rstrip("\n") + "\n"


def drop_sections(rel, ids):
    """既存ページから、### {#id} の節を取り除く。"""
    p = STL / rel
    text = p.read_text(encoding="utf-8")
    for i in ids:
        text = re.sub(r"(?ms)^### [^\n]*\{#" + re.escape(i) + r"[ }][^\n]*\n.*?(?=^#{2,3} |\Z)", "", text)
    p.write_text(text, encoding="utf-8", newline="")


def drop_lines(rel, needles):
    """既存ページから、needles のどれかを含む行を取り除く。"""
    p = STL / rel
    lines = p.read_text(encoding="utf-8").split("\n")
    lines = [l for l in lines if not any(n in l for n in needles)]
    p.write_text("\n".join(lines), encoding="utf-8", newline="")


def sub_in(rel, pairs):
    p = STL / rel
    text = p.read_text(encoding="utf-8")
    for o, n in pairs:
        if o not in text:
            print("MISSING in", rel, ":", o[:50])
        text = text.replace(o, n)
    p.write_text(text, encoding="utf-8", newline="")
