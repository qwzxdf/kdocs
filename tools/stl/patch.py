"""既存の STL ページの文章（導入・ポイント・読む前に・補足・しくみ・ゲーム・ミス・類似・まとめ）だけを差し替える。

シグネチャ、引数の表、サンプル、動く図はそのまま残す。書式は tools/stl/FORMAT.md。

使い方（tools/stl/p/xxx.py の中で）:
    from patch import P
    P("utilities/make_shared.md", intro="...", tips=[...], ...)
    run()   # 末尾で 1 回
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "docs" / "stl"

# 節の並び。ここに無い見出しは、「ゲームでの使いどころ」の前に入れる。
ORDER = ["関数の詳しい説明", "しくみ", "フラグ・オプション", "実際に動かしてみる", "ゲームでの使いどころ",
         "よくあるミス", "類似", "コンパイラ対応", "これだけ覚える", "関連ページ"]
_PENDING = []


def P(rel, **kw):
    _PENDING.append((rel, kw))


def _split_front(text):
    m = re.match(r"(---\n.*?\n---\n)", text, re.S)
    return m.group(1), text[m.end():]


def _sections(body):
    """先頭（# タイトルから最初の ## まで）と、各 ## 節を返す。"""
    parts = re.split(r"(?m)^(?=## )", body)
    head = parts[0]
    secs = []
    for p in parts[1:]:
        name = re.match(r"## (.*)", p).group(1).strip()
        secs.append([name, p])
    return head, secs


def _tip_block(tips):
    return '!!! tip "ポイント"\n' + "\n".join(f"    - {t}" for t in tips) + "\n"


def _info_block(info):
    lines = info.strip().split("\n")
    return '!!! info "このページを読む前に"\n' + "\n".join(f"    {l}" if l else "" for l in lines) + "\n"


def _replace_head(head, intro, tips, info):
    m = re.search(r'</div>\n\n', head)
    assert m, "page-badges が無い"
    pre = head[:m.end()]
    rest = head[m.end():]
    old_info = re.search(r'!!! info "[^"]*"\n(?:    .*\n|\n)*', rest)
    old_tip = re.search(r'!!! tip "[^"]*"\n(?:    .*\n)+', rest)
    # 既存の note ブロック（!!! warning など）はそのまま残す
    keep = rest
    if old_tip:
        keep = rest[old_tip.end():]
        keep = re.sub(r'^\n*!!! info "[^"]*"\n(?:    .*\n|\n)*', "", keep)
    else:
        keep = re.sub(r'^.*?(?=\n\n!!! |\Z)', "", keep, count=1, flags=re.S)
    if intro is None:
        intro_txt = rest[:old_tip.start()] if old_tip else rest
        intro_txt = intro_txt.rstrip("\n") + "\n\n"
    else:
        intro_txt = intro.strip("\n") + "\n\n"
    if tips is None:
        tip_txt = old_tip.group(0) + "\n" if old_tip else ""
    else:
        tip_txt = _tip_block(tips) + "\n"
    if info is None:
        info_txt = old_info.group(0).rstrip("\n") + "\n\n" if old_info else ""
    else:
        info_txt = _info_block(info) + "\n"
    keep = keep.lstrip("\n")
    return pre + intro_txt + tip_txt + info_txt + keep


def _insert_notes(secs, anchor, notes):
    for s in secs:
        text = s[1]
        m = re.search(r"(?m)^### .*\{#" + re.escape(anchor) + r"[ }]", text)
        if not m:
            continue
        end_m = re.search(r"(?m)^### ", text[m.end():])
        end = m.end() + end_m.start() if end_m else len(text)
        seg = text[m.start():end]
        fence = re.search(r"```.*?\n```\n", seg, re.S)
        pos = fence.end() if fence else len(seg)
        # 引数の表の終わりまで進む
        rest = seg[pos:]
        mt = re.match(r"\n*((?:\|.*\n)+)", rest)
        if mt:
            pos += mt.end()
        seg2 = seg[:pos] + "\n" + notes.strip("\n") + "\n" + seg[pos:]
        s[1] = text[:m.start()] + seg2 + text[end:]
        return True
    return False


def _put(secs, name, body):
    body = f"## {name}\n\n" + body.strip("\n") + "\n\n"
    for s in secs:
        if s[0] == name:
            s[1] = body
            return
    # 挿入位置: ORDER で後ろにある最初の既存の節の前
    idx = ORDER.index(name) if name in ORDER else ORDER.index("ゲームでの使いどころ")
    later = set(ORDER[idx + 1:])
    for i, s in enumerate(secs):
        if s[0] in later or (name not in ORDER and s[0] in ORDER[ORDER.index("ゲームでの使いどころ"):]):
            secs.insert(i, [name, body])
            return
    secs.append([name, body])


def _table(rows, head=("名前", "違い")):
    out = [f"| {head[0]} | {head[1]} |", "| --- | --- |"]
    for a, b in rows:
        out.append(f"| {a} | {b} |")
    return "\n".join(out)


def fix_pipes(text):
    """表のセル内の `a | b`（コード内のパイプ）を \\| にする。"""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("|"):
            line = re.sub(r"`([^`]*)`", lambda m: "`" + m.group(1).replace(" | ", " \\| ").replace("\\\\|", "\\|") + "`"
                          if " | " in m.group(1) and "\\|" not in m.group(1) else m.group(0), line)
        out.append(line)
    return "\n".join(out)


def _fail_blocks(items):
    blocks = []
    for t, c in items:
        body = "\n".join(f"    {l}" if l else "" for l in c.strip("\n").split("\n"))
        blocks.append(f'??? failure "{t}"\n' + body)
    return "\n\n".join(blocks)


def apply(rel, intro=None, tips=None, info=None, notes=None, sections=None, game=None, mistakes=None,
          similar=None, memo=None, compiler=None, info0=None, more=None):
    path = STL / rel
    text = path.read_text(encoding="utf-8")
    if info0 is not None and info is None and '!!! info' not in text:
        info = info0
    if more is not None and mistakes is None and text.count("??? failure") < 2:
        need = 2 - text.count("??? failure")
        extra = _fail_blocks(more[:need])
        sec_m = re.search(r"(?ms)^## よくあるミス\n\n(.*?)(?=^## )", text)
        if sec_m:
            text = text[:sec_m.end(1)].rstrip("\n") + "\n\n" + extra + "\n\n" + text[sec_m.end():]
        else:
            mistakes = list(more)
    front, body = _split_front(text)
    head, secs = _sections(body)
    if intro is not None or tips is not None or info is not None:
        head = _replace_head(head, intro, tips, info)
    if notes:
        for a, n in notes.items():
            ok = _insert_notes(secs, a, n)
            assert ok, f"{rel}: 関数 {a} が無い"
    if sections:
        for name, b in sections.items():
            _put(secs, name, b)
    if game is not None:
        _put(secs, "ゲームでの使いどころ", game)
    if mistakes is not None:
        assert len(mistakes) >= 2, f"{rel}: ミスは 2 件以上"
        b = "\n\n".join(f'??? failure "{t}"\n' + "\n".join(f"    {l}" if l else "" for l in c.strip("\n").split("\n"))
                        for t, c in mistakes)
        _put(secs, "よくあるミス", b)
    if similar is not None:
        _put(secs, "類似", similar if isinstance(similar, str) else _table(similar))
    if compiler is not None:
        _put(secs, "コンパイラ対応", compiler)
    if memo is not None:
        assert len(memo) == 3, f"{rel}: まとめは 3 項目"
        _put(secs, "これだけ覚える", '!!! abstract "まとめ"\n' + "\n".join(f"    - [x] {m}" for m in memo))
    new = front + head + "".join(s[1] for s in secs)
    new = fix_pipes(new).rstrip("\n") + "\n"
    path.write_text(new, encoding="utf-8", newline="")


def run():
    n = 0
    for rel, kw in _PENDING:
        apply(rel, **kw)
        n += 1
    print("patched", n)
    _PENDING.clear()


if __name__ == "__main__":
    sys.exit("p/*.py から使う")
