import os
import posixpath
import re

import yaml

RATINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ratings.yml")
LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+\.md)(#[^)\s]*)?\)")
H1 = re.compile(r"^# (.+)$", re.M)

PERF_LABEL = {1: "軽い", 2: "普通", 3: "重い"}
PERF_TITLE = {1: "パフォーマンス:軽い（負荷が小さい）", 2: "パフォーマンス:普通（中程度の負荷）", 3: "パフォーマンス:重い（負荷が大きい）"}
QUAL_TITLE = {1: "品質:低め（簡易）", 2: "品質:標準", 3: "品質:高い"}

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
        parts.append('<span class="perf perf-%d" title="%s">⚡%s</span>' % (4 - perf, PERF_TITLE[perf], PERF_LABEL[perf]))
    qual = rating.get("quality")
    if qual in QUAL_TITLE:
        parts.append('<span class="qual qual-%d" title="%s">%s%s</span>' % (qual, QUAL_TITLE[qual], "★" * qual, "☆" * (3 - qual)))
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
        if not match or "perf-" in first:
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
