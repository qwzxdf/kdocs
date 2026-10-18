import os
import posixpath
import re

import yaml

RATINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ratings.yml")
LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+\.md)(#[^)\s]*)?\)")
H1 = re.compile(r"^# (.+)$", re.M)

PERF_LABEL = {1: "とても軽い", 2: "軽い", 3: "普通", 4: "重い", 5: "とても重い"}
PERF_TITLE = {
    1: "重さ:とても軽い（ほぼ無料。フレームの 0.1 ms 未満）",
    2: "重さ:軽い（0.1〜0.3 ms）",
    3: "重さ:普通（0.3〜1 ms）",
    4: "重さ:重い（1〜3 ms。使いどころを選ぶ）",
    5: "重さ:とても重い（3 ms 超。品質設定で切る）",
}
QUAL_TITLE = {
    1: "品質:かんたんな近似（粗い）",
    2: "品質:簡易",
    3: "品質:標準",
    4: "品質:高い",
    5: "品質:基準になる正確さ",
}
DIFF_TITLE = {
    1: "難易度:入門（式も要らない）",
    2: "難易度:やさしい（基本の数学・1 回の描画で書ける）",
    3: "難易度:ふつう（複数パス・行列・サンプリングの理解）",
    4: "難易度:難しい（確率・積分・時間方向・技術の組み合わせ）",
    5: "難易度:上級（論文レベル・自前の実装が大変）",
}

_ratings = {}


def on_config(config):
    global _ratings
    _ratings = {}
    if os.path.exists(RATINGS_FILE):
        with open(RATINGS_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for key, value in data.items():
            _ratings[key] = value or {}
    return config


def Badges(rating):
    parts = []
    perf = rating.get("perf")
    if perf in PERF_LABEL:
        parts.append('<span class="perf perf-lv%d" title="%s">⚡%s</span>' % (perf, PERF_TITLE[perf], PERF_LABEL[perf]))
    qual = rating.get("quality")
    if qual in QUAL_TITLE:
        parts.append('<span class="qual qual-%d" title="%s">%s%s</span>' % (qual, QUAL_TITLE[qual], "★" * qual, "☆" * (5 - qual)))
    diff = rating.get("diff")
    if diff in DIFF_TITLE:
        parts.append('<span class="diff diff-%d" title="%s">難易度 %s%s</span>' % (diff, DIFF_TITLE[diff], "◆" * diff, "◇" * (5 - diff)))
    return " ".join(parts)


def on_page_markdown(markdown, page, config, files):
    if not _ratings:
        return markdown
    src = page.file.src_uri
    base = posixpath.dirname(src)

    own = _ratings.get(src)
    if own:
        badges = Badges(own)
        if badges:
            markdown = H1.sub(lambda m: "# %s %s" % (m.group(1), badges), markdown, count=1)

    lines = markdown.split("\n")
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
        if in_fence or not stripped.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 3:
            continue
        first = cells[1]
        match = LINK.search(first)
        if not match or "perf-lv" in first or "qual-" in first or "diff-" in first:
            continue
        target = posixpath.normpath(posixpath.join(base, match.group(2)))
        rating = _ratings.get(target)
        if not rating:
            continue
        badges = Badges(rating)
        if not badges:
            continue
        cells[1] = first[:match.end()] + " " + badges + first[match.end():]
        lines[i] = "|".join(cells)
    return "\n".join(lines)
