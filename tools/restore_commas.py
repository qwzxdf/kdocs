"""reduce_commas.py で減らしすぎたページの読点を、接続の切れ目だけ戻す。

使い方: python tools/restore_commas.py <ファイル>... [--target 0.65]
戻す場所: 「ところが」「そこで」「ただし」などの接続語の後ろと、「〜ので」「〜ですが」「〜ときは」「〜なら」「〜ないと」の後ろ。
本文だけが対象（コード、SVG、表、見出し、インライン コードの中は触らない）。1 文あたりが目標を超えたら止める。
"""
import re
import sys

PAT = [
    (r"(ところが|そこで|ただし|そのかわり|したがって|たとえば|一方)(?=[^、。\s])", r"\1、"),
    (r"(ので|ですが|ますが|ないと|ときは|ときに|場合は|ならば|なら|と、)(?=[ぁ-んァ-ヶ一-龥A-Za-z「（])", None),
]


def restore(text, target):
    lines = text.split("\n")
    out = []
    in_code = False
    in_svg = False
    body_commas = body_stops = 0
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_code = not in_code
        if "<svg" in ln:
            in_svg = True
        if not in_code and not in_svg:
            body_commas += ln.count("、")
            body_stops += ln.count("。")
        if "</svg>" in ln:
            in_svg = False
    ratio = body_commas / max(1, body_stops)
    in_code = False
    in_svg = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            out.append(ln)
            continue
        if "<svg" in ln:
            in_svg = True
        skip = in_code or in_svg or ln.lstrip().startswith(("|", "#", "---", "title:", "<"))
        if "</svg>" in ln:
            in_svg = False
        if skip or ratio >= target or "。" not in ln:
            out.append(ln)
            continue
        parts = re.split(r"(`[^`]*`)", ln)
        new = []
        for p in parts:
            if p.startswith("`"):
                new.append(p)
                continue
            p2 = re.sub(PAT[0][0], PAT[0][1], p)
            p2 = re.sub(r"(ので|ですが|ますが|ないと|ときは|ときに|場合は|ならば)(?=[ぁ-んァ-ヶ一-龥A-Za-z「（])", r"\1、", p2)
            ratio += (p2.count("、") - p.count("、")) / max(1, body_stops)
            new.append(p2)
        out.append("".join(new))
    return "\n".join(out), ratio


def main():
    target = 0.65
    if "--target" in sys.argv:
        target = float(sys.argv[sys.argv.index("--target") + 1])
    for p in [a for a in sys.argv[1:] if not a.startswith("--") and not a[0].isdigit() or a.endswith(".md")]:
        if not p.endswith(".md"):
            continue
        t = open(p, encoding="utf-8", newline="").read()
        crlf = "\r\n" in t
        t = t.replace("\r\n", "\n")
        t2, r = restore(t, target)
        if crlf:
            t2 = t2.replace("\n", "\r\n")
        open(p, "w", encoding="utf-8", newline="").write(t2)
        print(f"{p}: -> {r:.2f}")


if __name__ == "__main__":
    main()
