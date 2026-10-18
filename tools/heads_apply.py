"""描画セクションの見出しを英語にする(日本語の見出しのアンカーは {#id} で残す)。"""
import glob, io, json, re, sys
from pymdownx.slugs import slugify

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
JA = re.compile(r"[ぁ-んァ-ヶ一-龥ー]")
keys = json.load(open("/tmp/heads_keys.json", encoding="utf-8"))
en = {}
for n in (1, 2, 3):
    for line in open("tools/heads_en_%d.tsv" % n, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        i, t = line.split("\t", 1)
        en[keys[int(i)]] = t
assert len(en) == len(keys), (len(en), len(keys))
sl = slugify(case="lower")


def Split(t):
    attr = ""
    m = re.search(r"\s*(\{[^}]*\})\s*$", t)
    if m:
        attr = m.group(1)
        t = t[:m.start()]
    suf = ""
    m = re.search(r"((?:\s*<span[^>]*>[^<]*</span>)+)\s*$", t)
    if m:
        suf = m.group(1)
        t = t[:m.start()]
    return t.rstrip(), suf, attr


def Plain(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("*", "").replace("`", "")
    return t


total = missing = 0
for f in sorted(glob.glob("docs/graphics/**/*.md", recursive=True)):
    raw = open(f, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    used = set()
    out = []
    inc = False
    changed = False
    # 先に、既存の {#id} と 全見出しの 元の ID を集めて、重複を避ける
    for l in lines:
        m = re.search(r"\{[^}]*#([^\s}]+)", l) if re.match(r"^#{1,6} ", l) else None
        if m:
            used.add(m.group(1))
    seen_slug = {}
    for l in lines:
        if l.startswith("```"):
            inc = not inc
        m = None if inc else re.match(r"^(#{1,6}) (.+)$", l)
        if not m:
            out.append(l)
            continue
        hashes, text = m.group(1), m.group(2)
        core, suf, attr = Split(text)
        base = sl(Plain(core), "-")
        if not JA.search(core):
            out.append(l)
            continue
        if core not in en:
            missing += 1
            print("未翻訳:", f, l)
            out.append(l)
            continue
        new = en[core]
        # 元のアンカーを残す
        if "#" in attr:
            na = attr
        else:
            sid = base
            n = 0
            while sid in used:
                n += 1
                sid = "%s_%d" % (base, n)
            used.add(sid)
            if attr:
                na = "{#%s %s" % (sid, attr[1:])
            else:
                na = "{#%s}" % sid
        out.append("%s %s%s %s" % (hashes, new, suf, na))
        total += 1
        changed = True
    if changed:
        t = "\n".join(out)
        if crlf:
            t = t.replace("\n", "\r\n")
        open(f, "wb").write(t.encode("utf-8"))
print("変更した見出し", total, "未翻訳", missing)
