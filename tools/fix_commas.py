"""読点「、」の、多すぎる文章を、整える。

文節ごとに「、」を打った文(「〜は、〜を、〜に、」)から、読点を間引く。
  - 前の読点(または文頭)から、短いうちは、読点を打たない(MIN 文字未満なら、外す)。
  - 文頭の接続語(しかし、ただし、つまり…)の後ろの読点は、残す。
  - コード ブロック、インライン コード、リンクの宛先、HTML・SVG、図のコメントは、触らない。
使い方: python tools/fix_commas.py --survey            密度の一覧
        python tools/fix_commas.py --apply 6.0         密度が 6.0(100 字あたり)以上のファイルを直す
        python tools/fix_commas.py --apply 6.0 --dry   直さず、件数だけ
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
MIN = 14
CONJ = ("しかし", "ただし", "つまり", "また", "そして", "さらに", "なお", "ただ", "ところが", "すると", "そのため", "そこで",
        "たとえば", "例えば", "ここでは", "逆に", "一方", "もし", "実際", "特に", "まず", "次に", "最後に", "いずれも",
        "どちらも", "そのうえ", "ただし", "要するに", "結果として", "その結果", "このとき", "そのとき", "だから", "なぜなら",
        "たとえ", "もっとも", "ちなみに", "とくに", "同様に", "一般に", "通常", "普通", "このように", "そうすると")
INLINE = re.compile(r"`[^`\n]*`|\]\([^)\n]*\)|<[^>\n]+>")


def Fix(line):
    holders = []

    def Hide(m):
        holders.append(m.group(0))
        return "\x00%d\x00" % (len(holders) - 1)

    work = INLINE.sub(Hide, line)
    out = []
    for sentence in re.split(r"(?<=。)", work):
        parts = sentence.split("、")
        if len(parts) <= 1:
            out.append(sentence)
            continue
        res = parts[0]
        run = len(re.sub(r"\x00\d+\x00", "x", parts[0]))
        for i, part in enumerate(parts[1:], 1):
            head = res.lstrip(" -|>0123456789.*")
            conj_head = any(head.startswith(c) for c in CONJ) and run <= len(max(CONJ, key=len)) + 1 and "、" not in res[-1:] and run == len(re.sub(r"\x00\d+\x00", "x", res.split("、")[-1]))
            nxt = len(re.sub(r"\x00\d+\x00", "x", part.split("、")[0]))
            keep = conj_head and res.count("、") == 0
            clause_end = re.search(r"(て|で|し|く|ば|が|ので|のに|たら|ても|ると|ため|ながら|です|ます|ない|いる|ある|する|れる|った|いた|んだ|けど|から|まで|のは|が)$", res)
            subject_end = res.endswith("は") and run >= 18
            if not keep and nxt >= 4 and ((run >= MIN and clause_end) or subject_end or run >= 36):
                keep = True
            if not keep and not re.match(r"[ぁ-ん]", res[-1:]):
                keep = True                                  # 名詞を並べる読点(置き場所、順序)は、残す
            if keep:
                res += "、" + part
                run = len(re.sub(r"\x00\d+\x00", "x", part))
            else:
                res += (" " if re.match(r"[A-Za-z0-9`<\x00]", part[:1]) else "") + part
                run += len(re.sub(r"\x00\d+\x00", "x", part))
        out.append(res)
    text = "".join(out)
    for i, h in enumerate(holders):
        text = text.replace("\x00%d\x00" % i, h)
    return text


def Process(text):
    lines = text.split("\n")
    out = []
    fence = False
    fig = False
    front = 0
    for i, line in enumerate(lines):
        s = line.lstrip()
        if i == 0 and line.strip() == "---":
            front = 1
        elif front == 1:
            if line.strip() == "---":
                front = 2
            out.append(line)
            continue
        if s.startswith("```"):
            fence = not fence
            out.append(line)
            continue
        if "<!-- fig:" in line and ":begin" in line:
            fig = True
        if fence or fig or "、" not in line or s.startswith(("<svg", "<text", "<rect", "<path", "<line", "<g ", "<defs", "<marker", "</")):
            out.append(line)
        else:
            out.append(Fix(line))
        if "<!-- fig:" in line and ":end" in line:
            fig = False
    return "\n".join(out)


def Density(text):
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = re.sub(r"<svg.*?</svg>", "", body, flags=re.S)
    body = re.sub(r"`[^`\n]*`", "", body)
    chars = len(re.findall(r"[ぁ-んァ-ヶ一-龥]", body))
    return (body.count("、") * 100.0 / chars) if chars else 0.0


def Files():
    return sorted(glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True))


def Read(p):
    raw = io.open(p, "rb").read().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def main():
    if "--survey" in sys.argv:
        rows = []
        for p in Files():
            t, _ = Read(p)
            rows.append((Density(t), os.path.relpath(p, ROOT).replace(os.sep, "/")))
        rows.sort(reverse=True)
        import statistics
        print("median", round(statistics.median(r[0] for r in rows), 2))
        for d, n in rows[:40]:
            print(round(d, 2), n)
        for th in (4, 5, 6, 7, 8):
            print("density >=", th, sum(1 for r in rows if r[0] >= th))
        return
    if "--apply" in sys.argv:
        th = float(sys.argv[sys.argv.index("--apply") + 1])
        dry = "--dry" in sys.argv
        n = 0
        before = after = 0
        for p in Files():
            t, crlf = Read(p)
            d = Density(t)
            if d < th:
                continue
            new = Process(t)
            if new != t:
                n += 1
                before += t.count("、")
                after += new.count("、")
                if not dry:
                    io.open(p, "wb").write((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
        print("files", n, "commas", before, "->", after)


if __name__ == "__main__":
    main()
