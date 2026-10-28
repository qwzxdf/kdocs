"""検索用のデータを作る。

mkdocs 標準の search プラグインは、ブラウザで lunr の索引を組み立てるので、初期化が遅い。
ここでは見出しごとの本文を、そのまま JSON に出す。ブラウザは索引を作らず、部分一致で走査する。

出力:
  search/meta.json        ページと見出しの一覧。小さいので最初に読む。本文ファイルの名前も入っている
  search/body.<hash>.json 見出しごとの本文。meta.json の secs と同じ並び。中身で名前が変わるので、長くキャッシュできる
"""
import hashlib
import json
import os
import re
from html.parser import HTMLParser

HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SKIP_TAGS = {"script", "style"}
MAX_BODY = 6000
SPACES = re.compile(r"\s+")

_pages = []
_secs = []
_bodies = []


class Section:
    def __init__(self, anchor, title):
        self.anchor = anchor
        self.title = title
        self.text = []


class Parser(HTMLParser):
    def __init__(self, page_title):
        super().__init__()
        self.sections = [Section("", page_title)]
        self.heading = None
        self.skip = 0
        self.permalink = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in SKIP_TAGS:
            self.skip += 1
        elif tag == "a" and "headerlink" in (attrs.get("class") or ""):
            self.permalink += 1
        elif tag in HEADINGS and attrs.get("id"):
            self.heading = Section(attrs["id"], "")
            self.sections.append(self.heading)

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        elif tag == "a" and self.permalink:
            self.permalink -= 1
        elif tag in HEADINGS:
            self.heading = None

    def handle_data(self, data):
        if self.skip or self.permalink:
            return
        if self.heading is not None:
            self.heading.title += data
        else:
            self.sections[-1].text.append(data)


def on_pre_build(config):
    _pages.clear()
    _secs.clear()
    _bodies.clear()


def on_page_context(context, page, config, nav):
    search = page.meta.get("search") or {}
    if isinstance(search, dict) and search.get("exclude"):
        return
    parser = Parser(page.title or "")
    parser.feed(page.content or "")
    parser.close()
    page_index = len(_pages)
    _pages.append([page.url, page.title or ""])
    for section in parser.sections:
        text = SPACES.sub(" ", " ".join(section.text).replace(" ", " ")).strip()[:MAX_BODY]
        title = SPACES.sub(" ", section.title).strip()
        _secs.append([page_index, section.anchor, title])
        _bodies.append(text)


def on_post_build(config):
    out = os.path.join(config["site_dir"], "search")
    os.makedirs(out, exist_ok=True)
    body = json.dumps(_bodies, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha1(body.encode("utf-8")).hexdigest()[:10]
    body_name = "body." + digest + ".json"
    for name in os.listdir(out):
        if name.startswith("body.") and name != body_name:
            os.remove(os.path.join(out, name))
    with open(os.path.join(out, body_name), "w", encoding="utf-8") as f:
        f.write(body)
    meta = {"body": body_name, "pages": _pages, "secs": _secs}
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))
