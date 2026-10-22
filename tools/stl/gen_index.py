"""docs/stl/index.md を、各ページの front matter とバッジから作る。

使い方:
  python tools/stl/gen_index.py --migrate   # 今の index.md から summary / order を各ページの front matter に写す（最初の 1 回）
  python tools/stl/gen_index.py             # index.md を作り直す
  python tools/stl/gen_index.py --pages     # 各フォルダの .pages も作り直す

各ページの front matter:
  summary: 一言で（index の「一言で」の列）
  order:   同じ重要度の中での並び（小さいほど上）。省略可
  group:   index での小見出し（同じ group が続く）。省略可
重要度（rank）・速さ（perf）・バージョン（ver）は、ページ上部のバッジから読む。
"""
import re
import sys

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "docs" / "stl"
INDEX = STL / "index.md"

# (フォルダ, index の見出し, 速さの列を付けるか, 表の 1 列目の名前)
CATEGORIES = [
    ("containers", "コンテナ", "データをまとめて持つ入れ物", True, "コンテナ"),
    ("algorithms", "アルゴリズム", "並べ替え・検索・変換", False, "アルゴリズム"),
    ("utilities", "ユーティリティ", "optional, unique_ptr, format などの便利な部品", True, "機能"),
    ("memory", "メモリ", "確保の仕組み、アロケータ、C 由来の関数", False, "名前"),
    ("io", "入出力・文字列", "ファイル、パス、文字列と数値の変換", False, "名前"),
    ("numeric", "数値", "数学関数、定数、整数型、ビット操作", False, "名前"),
    ("concurrency", "並行処理", "スレッドとデータの守り方", True, "名前"),
    ("support", "型・言語サポート", "イテレータの道具、関数オブジェクト、型の性質、例外", False, "名前"),
]
RANK_ORDER = {"must": 0, "often": 1, "sometimes": 2, "rare": 3}
RANK_LABEL = {"must": "必須", "often": "よく使う", "sometimes": "たまに", "rare": "知ってるだけ"}
PERF_LABEL = {"4": "◎", "3": "○", "2": "△", "1": "×"}

FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def read_front(text):
    m = FM.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    meta = {k: (str(v) if not isinstance(v, (list, dict)) else v) for k, v in meta.items()}
    return meta, text[m.end():]


def page_info(path):
    text = path.read_text(encoding="utf-8")
    meta, body = read_front(text)
    badges = re.search(r'<div class="page-badges".*?</div>', body, re.S)
    b = badges.group(0) if badges else ""
    rank = re.search(r"rank rank-(\w+)", b)
    perf = re.search(r"perf perf-(\d)", b)
    ver = re.search(r'<span class="ver ver-(\d+)">([^<]*)</span>', b)
    title = meta.get("title", path.stem)
    return {
        "path": path,
        "rel": path.relative_to(STL).as_posix(),
        "title": title,
        "summary": meta.get("summary", ""),
        "order": int(meta["order"]) if meta.get("order", "").lstrip("-").isdigit() else 500,
        "group": meta.get("group", ""),
        "rank": rank.group(1) if rank else "sometimes",
        "perf": perf.group(1) if perf else None,
        "ver": (ver.group(1), ver.group(2)) if ver else None,
        "has_rank": bool(rank),
    }


def insert_front(path, kv):
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    assert m, path
    block = m.group(1)
    lines = block.split("\n")
    for k, v in kv.items():
        lines = [l for l in lines if not l.startswith(k + ":")]
    # title の次に入れる（tags は後ろ）
    out = []
    done = False
    for l in lines:
        out.append(l)
        if l.startswith("title:") and not done:
            for k, v in kv.items():
                out.append(f"{k}: {v}")
            done = True
    new = "---\n" + "\n".join(out) + "\n---\n" + text[m.end():]
    path.write_text(new, encoding="utf-8", newline="")


def migrate():
    old = INDEX.read_text(encoding="utf-8")
    row = re.compile(r"^    \| \[(.+?)\]\((.+?)\) \| <span class=\"rank rank-(\w+)\">[^<]*</span> \|(?: <span class=\"perf perf-(\d)\">.</span> \|| — \|)? (.*) \|$")
    order = {}
    n = 0
    for line in old.split("\n"):
        m = row.match(line)
        if not m:
            continue
        label, rel, rank, perf, rest = m.groups()
        p = STL / rel
        if not p.exists():
            print("missing", rel)
            continue
        n += 1
        summary = re.sub(r' *<span class="ver [^>]*>[^<]*</span>', "", rest).strip()
        info = page_info(p)
        if info["rank"] != rank:
            print("rank differs", rel, info["rank"], rank)
        insert_front(p, {"summary": summary, "order": str(n)})
    print("migrated", n)


def table_for(items, with_perf, first_col):
    head = f"| {first_col} | 重要度 |" + (" 速さ |" if with_perf else "") + " 一言で |"
    sep = "| --- | --- |" + (" --- |" if with_perf else "") + " --- |"
    lines = [head, sep]
    for it in items:
        name = it["title"]
        if re.match(r"^(std::|<|[a-z_]+\()", name) and "（" not in name:
            label = f"`{name}`"
        else:
            label = name
        rel = it["rel"]
        rank = it["rank"]
        cell = f'<span class="rank rank-{rank}">{RANK_LABEL[rank]}</span>'
        cols = [f"[{label}]({rel})", cell]
        if with_perf:
            if it["perf"]:
                cols.append(f'<span class="perf perf-{it["perf"]}">{PERF_LABEL[it["perf"]]}</span>')
            else:
                cols.append("—")
        summ = it["summary"].replace("|", "\\|")
        if it["ver"] and it["ver"][0] in ("17", "20", "23", "26"):
            summ += f' <span class="ver ver-{it["ver"][0]}">{it["ver"][1]}</span>'
        cols.append(summ)
        lines.append("| " + " | ".join(cols) + " |")
    return lines


def generate():
    old = INDEX.read_text(encoding="utf-8")
    head = old.split("??? abstract", 1)[0]
    tail = "\nSTL を読むための前提知識は [基礎](../basics/index.md) にまとめています。\n"
    out = [head.rstrip("\n"), ""]
    for folder, name, desc, with_perf, first in CATEGORIES:
        items = [page_info(p) for p in sorted((STL / folder).rglob("*.md")) if p.name != "index.md"]
        # 索引ページ（フォルダの index.md）も載せる
        items += [page_info(p) for p in sorted((STL / folder).rglob("index.md"))]
        items.sort(key=lambda i: (i["group"] == "", i["group"], RANK_ORDER[i["rank"]], i["order"], i["title"]))
        # group が空のものを先に
        nogroup = [i for i in items if not i["group"]]
        groups = {}
        for i in items:
            if i["group"]:
                groups.setdefault(i["group"], []).append(i)
        nogroup.sort(key=lambda i: (RANK_ORDER[i["rank"]], i["order"], i["title"]))
        out.append(f'??? abstract "{name}（{len(items)}）: {desc}"')
        if folder == "algorithms":
            out.append("    C++20 以降は `std::ranges::` 版を使うのが基本です。")
            out.append("")
        body = []
        if nogroup:
            body += table_for(nogroup, with_perf, first)
        for g, its in groups.items():
            its.sort(key=lambda i: (RANK_ORDER[i["rank"]], i["order"], i["title"]))
            if body:
                body.append("")
            body.append(f"**{g}**")
            body.append("")
            body += table_for(its, with_perf, first)
        out += ["    " + l if l else "" for l in body]
        out.append("")
    out.append(tail.strip("\n"))
    INDEX.write_text("\n".join(out) + "\n", encoding="utf-8", newline="")
    print("index written")


def write_pages():
    for folder, name, desc, with_perf, first in CATEGORIES:
        d = STL / folder
        subdirs = [x for x in sorted(d.rglob("*")) if x.is_dir()]
        for sub in [d] + subdirs:
            files = [p for p in sub.glob("*.md")]
            items = [page_info(p) for p in files if p.name != "index.md"]
            items.sort(key=lambda i: (RANK_ORDER[i["rank"]], i["order"], i["title"]))
            names = [i["path"].name for i in items]
            lines = []
            old_pages = sub / ".pages"
            old_title = None
            if old_pages.exists():
                m = re.search(r"(?m)^title:.*$", old_pages.read_text(encoding="utf-8"))
                old_title = m.group(0) if m else None
            if old_title:
                lines.append(old_title)
            elif sub != d:
                lines.append(f"title: {sub.name}")
            lines.append("nav:")
            if (sub / "index.md").exists():
                lines.append("  - index.md")
            lines += [f"  - {n}" for n in names]
            # 下のフォルダは ... に任せる
            lines.append("  - ...")
            (sub / ".pages").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    print("pages written")


if __name__ == "__main__":
    if "--migrate" in sys.argv:
        migrate()
    elif "--pages" in sys.argv:
        write_pages()
    else:
        generate()
