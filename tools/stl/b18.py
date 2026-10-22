"""バッチ 18: 1 ページにまとまっていた別々のクラス・関数を、1 つずつのページに分ける。"""
from mk import *  # noqa: F401,F403
from split import drop_sections, record_moves, sub_in  # noqa: F401

import re

IOI = "[`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。"


def move(old, ids_to_new, default=None):
    """旧ページから節を消して、リンクの付け替え表に記録する。"""
    drop_sections(old, list(ids_to_new))
    record_moves("stl/" + old, {k: "stl/" + v for k, v in ids_to_new.items()}, "stl/" + default if default else None)


# ================= iostream のオブジェクト =================
for nm, base, t_, what, intro in [
    ("clog", "cerr", "ostream", "標準のログ出力（cerr と同じ出力先で、バッファあり）。", "`std::clog` は、`cerr` と同じ標準エラー出力に出しますが、**バッファにためてから**出します。1 回ごとにすぐ出す `cerr` よりも速いので、大量のログを出すときに向きます。代わりに、クラッシュの直前のログが出ずに失われることがあります。"),
    ("wcerr", "cerr", "wostream", "`wchar_t` の標準エラー出力。", "`std::wcerr` は、`cerr` の `wchar_t` 版です。`wchar_t` の文字列（`L\"...\"`）を、標準エラー出力に出します。1 つのプログラムで `cerr` と `wcerr` を混ぜて使うと、文字化けや動作不良の原因になることがあります。"),
    ("wclog", "cerr", "wostream", "`wchar_t` の標準ログ出力（バッファあり）。", "`std::wclog` は、`clog` の `wchar_t` 版です。`wchar_t` の文字列を、バッファありの標準エラー出力に出します。`clog` と混ぜて使わないようにします。"),
    ("wcin", "cin", "wistream", "`wchar_t` の標準入力。", "`std::wcin` は、`cin` の `wchar_t` 版です。`wchar_t` の文字列（`std::wstring`）を、標準入力から読みます。`cin` と混ぜて使うと、文字化けや動作不良の原因になることがあります。"),
    ("wcout", "cout", "wostream", "`wchar_t` の標準出力。", "`std::wcout` は、`cout` の `wchar_t` 版です。`wchar_t` の文字列（`L\"...\"`）を、標準出力に出します。`cout` と混ぜて使うと、文字化けや動作不良の原因になることがあります。")]:
    wide = nm.startswith("w")
    code_ = {"clog": '#include <iostream>\n\nint main() {\n  std::clog << "log: start\\n";\n}',
             "wcerr": '#include <iostream>\n\nint main() {\n  std::wcerr << L"error\\n";\n}',
             "wclog": '#include <iostream>\n\nint main() {\n  std::wclog << L"log\\n";\n}',
             "wcin": '#include <iostream>\n#include <string>\n\nint main() {\n  std::wstring name;\n  std::wcin >> name;\n  std::wcout << name << L"\\n";\n}',
             "wcout": '#include <iostream>\n\nint main() {\n  std::wcout << L"hello " << 42 << L"\\n";\n}'}[nm]
    out_ = {"clog": "log: start", "wcerr": "error", "wclog": "log", "wcin": None, "wcout": "hello 42"}[nm]
    P("io/" + nm + ".md", "std::" + nm, what, "rare", "iostream", intro,
      [f"`{base}` の{'`wchar_t` 版' if wide else '仲間'}。", "出力先・入力元は同じ標準ストリーム。" if wide else "出力先は `cerr` と同じ。", "ゲームでは `std::println` やログライブラリを使うことが多い。"],
      [("ログ・エラーの出力" if "log" in nm or "err" in nm else "ワイド文字の入力・出力", f"`std::{nm} << ...;`" if nm != "wcin" else "`std::wcin >> name;`")],
      ("`" + base + "` と混ぜて使う" if wide else "クラッシュ時のログを期待する", f"`{base}` と `{nm}` を 1 つのプログラムで混ぜると、向き（orientation）が食い違って、出力が壊れることがあります。どちらかに統一します。" if wide else "バッファにためるので、クラッシュ直前のログが失われることがあります。確実に残したいログは `cerr` か、`flush` を使います。"),
      [(f"[`{base}`]({base}.md)", "char 版" if wide else "バッファなしの標準エラー出力"), ("[`std::println`](../utilities/print.md)", "新しい書き方")],
      [what.rstrip("。"), f"{base} の{'wchar_t 版' if wide else '仲間'}", "混ぜて使わない" if wide else "バッファあり"],
      sig=f"extern std::{t_} {nm};", args=[], ret=f"`{t_}`", cx="操作による",
      code=code_, out=out_, ver=None, info=IOI, rj=f"iostream/{nm}.html", cr=f"io/{nm}")
move("io/cerr.md", {"clog": "io/clog.md", "wcerr": "io/wcerr.md", "wclog": "io/wclog.md"}, "io/cerr.md")
move("io/cin.md", {"wcin": "io/wcin.md"}, "io/cin.md")
move("io/cout.md", {"wcout": "io/wcout.md"}, "io/cout.md")
sub_in("io/cerr.md", [("`std::clog` は同じ出力先ですが、バッファありです。", "[`std::clog`](clog.md) は同じ出力先ですが、バッファありです。")])

# ================= format =================
FMI = "[`std::format`](format.md) と [`std::format_to`](format_to.md) を先に読んでください。"
P("utilities/format_to_n.md", "std::format_to_n", "最大 n 文字だけ、出力先に書式化して書き込む。", "rare", "format",
  "固定長の `char` 配列に書式化したいとき、`format_to` は、配列の大きさを超えて書き込む危険があります。`format_to_n` は、書き込む文字数の上限を指定でき、はみ出しません。戻り値の `size` は、上限がなければ何文字になったかを教えてくれるので、切り捨てが起きたかが分かります。",
  ["上限を超える分は書き込まれない。", "終端の `'\\0'` は自分で付ける。", "`result.size` が「本来の長さ」。`size > n` なら切り捨てられた。"],
  [("固定長のバッファに、はみ出さず書式化する", "`std::format_to_n(buf, sizeof buf - 1, \"Score:{}\", s);`")], ("終端文字を付け忘れる", "`format_to_n` は終端を書きません。`*result.out = '\\0';` で自分で付けます。"),
  [("[`format_to`](format_to.md)", "上限なし"), ("[`formatted_size`](formatted_size.md)", "長さだけ求める")], ["最大 n 文字だけ書き込む", "終端は自分で付ける", "size で切り捨てを検出"],
  sig="template <class OutputIt, class... Args>\nformat_to_n_result<OutputIt> format_to_n(OutputIt out, std::iter_difference_t<OutputIt> n, std::format_string<Args...> fmt, Args&&... args);",
  args=[("out", "出力イテレータ", "書き込み先"), ("n", "整数", "書き込む最大の文字数"), ("fmt", "書式文字列", "コンパイル時の定数"), ("args...", "値", "`{}` に入れる値")], ret="`out`（書き終えた位置）と `size`（本来の文字数）をもつ構造体", cx="O(書く文字数)",
  code="""#include <format>
#include <print>

int main() {
  char buf[8] = {};
  auto result = std::format_to_n(buf, sizeof(buf) - 1, "Score:{}", 123456);
  std::println("[{}] 本来は {} 文字", buf, result.size);
}""", out="[Score:1] 本来は 12 文字", ver=("20", "C++20"), info=FMI, rj="format/format_to_n.html", cr="utility/format/format_to_n")
P("utilities/formatted_size.md", "std::formatted_size", "書式化した結果が何文字になるかだけを返す（文字列は作らない）。", "rare", "format",
  "書式化した文字列を、固定長のバッファに入れるとき、先に必要な大きさが分かれば、ちょうどの大きさで確保できます。`formatted_size` は、実際に文字列を作らずに、何文字になるかだけを返します。",
  ["文字列は作らない（メモリ確保もしない）。", "戻り値は終端の `'\\0'` を含まない文字数。", "確保してから `format_to` で書き込む、という使い方をする。"],
  [("書式化結果の大きさを先に求める", "`std::string s(std::formatted_size(\"{}-{}\", a, b), '\\0');`")], ("終端文字ぶんを足し忘れる", "戻り値は終端を含みません。C の文字列にするなら 1 足します。"),
  [("[`format_to_n`](format_to_n.md)", "上限つきで書き込む"), ("[`format`](format.md)", "文字列を作る")], ["書式化結果の文字数だけ返す", "文字列は作らない", "終端は含まない"],
  sig="template <class... Args>\nstd::size_t formatted_size(std::format_string<Args...> fmt, Args&&... args);", args=[("fmt", "書式文字列", "コンパイル時の定数"), ("args...", "値", "`{}` に入れる値")], ret="書式化した結果の文字数", cx="O(書く文字数)",
  code="""#include <format>
#include <print>

int main() {
  std::println("{}", std::formatted_size("HP {}/{}", 45, 120));
}""", out="9", ver=("20", "C++20"), info=FMI, rj="format/formatted_size.html", cr="utility/format/formatted_size")
move("utilities/format_to.md", {"format_to_n": "utilities/format_to_n.md", "formatted_size": "utilities/formatted_size.md"}, "utilities/format_to.md")

P("utilities/println.md", "std::println", "書式つきで出力して、最後に改行する。", "must", "print",
  "`std::print` で出力するたびに、`\\n` を自分で書くのは手間です。`std::println` は、`print` と同じ書式で出力し、最後に自動で改行を付けます。ゲームのデバッグ出力の大半は、これで足ります。",
  ["`print` と同じ書式（`{}` に値を入れる）。", "最後に改行が付く。", "第 1 引数に `FILE*` を渡すと、出力先を選べる（`stderr` など）。"],
  [("デバッグ表示", "`std::println(\"HP: {}\", hp);`"), ("エラー出力", "`std::println(stderr, \"error: {}\", code);`")], ("書式と引数の数を合わせない", "`{}` の数と引数の数が合わないと、コンパイルエラーになります（実行時ではなく）。"),
  [("[`print`](print.md)", "改行なし"), ("[`format`](format.md)", "文字列として作る"), ("[`std::cout`](../io/cout.md)", "従来の出力")], ["書式つきで出力して改行する", "print の改行つき版", "stderr も指定できる"],
  sig="template <class... Args>\nvoid println(std::format_string<Args...> fmt, Args&&... args);\ntemplate <class... Args>\nvoid println(std::FILE* stream, std::format_string<Args...> fmt, Args&&... args);",
  args=[("stream", "FILE*", "出力先。省略すると `stdout`。`stderr` も指定できる"), ("fmt", "書式文字列", "`{}` を含む文字列。**コンパイル時の定数**"), ("args...", "値", "`{}` に順番に入れる値")], ret="なし", cx="O(出力の長さ)",
  code="""#include <cstdio>
#include <print>

int main() {
  std::println("通常の出力");
  std::println(stderr, "エラー出力: {}", 404);  // stderr は実行結果欄には出ないことがある
}""", out="通常の出力", ver=("23", "C++23"), info="[`std::print`](print.md) を先に読んでください。", rj="print/println.html", cr="io/println")
move("utilities/print.md", {"println": "utilities/println.md"}, "utilities/print.md")

P("utilities/variant_size.md", "std::variant_size", "variant が持てる型の数をコンパイル時に取り出す。", "rare", "variant",
  "`variant<int, double, std::string>` が、何種類の型を持てるかを、テンプレートの中で知りたいことがあります。`variant_size_v<V>` が、その数（この例では 3）を返します。型のリストを `index_sequence` で順に処理するときの終点にも使えます。",
  ["`variant_size_v<V>` で数が取れる（`size_t`）。", "`variant_alternative_t<I, V>` と組み合わせると、全部の選択肢を順に調べられる。", "`std::tuple_size` の variant 版。"],
  [("variant の全ての選択肢に処理をする", "`std::make_index_sequence<std::variant_size_v<V>>{}`")], ("`index()` と混同する", "`index()` は今入っている型の番号、`variant_size` は持てる型の数です。"),
  [("[`variant_alternative`](variant_alternative.md)", "N 番目の型"), ("[`std::variant`](variant.md)", "variant の本体")], ["持てる型の数を取り出す", "variant_size_v", "コンパイル時の値"],
  sig="template <class T>\nstruct variant_size;\ntemplate <class T>\ninline constexpr size_t variant_size_v = variant_size<T>::value;", args=[("T", "variant 型", "調べる variant")], ret="型の数（`size_t`）", cx="コンパイル時のみ",
  code="""#include <print>
#include <variant>

int main() {
  using V = std::variant<int, double, char>;
  std::println("{}", std::variant_size_v<V>);
}""", out="3", ver=("17", "C++17"), info="[`std::variant`](variant.md) を先に読んでください。", rj="variant/variant_size.html", cr="utility/variant/variant_size")
move("utilities/variant.md", {"variant_size": "utilities/variant_size.md"}, "utilities/variant.md")

P("support/iterator/end.md", "std::end", "コンテナや配列の終わり（最後の次）を指すイテレータを返す。", "often", "iterator",
  "`c.end()` はコンテナ専用で、C の配列には書けません。`std::end(c)` は、コンテナなら `c.end()`、配列なら先頭 + 要素数を返します。配列でもコンテナでも、同じ書き方で終端を取れるので、ジェネリックなコードで使います。",
  ["コンテナでも C の配列でも同じ書き方で使える。", "`std::begin` とセットで使う。", "C++20 では `std::ranges::end` も使える。"],
  [("配列とコンテナの両方を受け取る関数で走査する", "`for (auto it = std::begin(c); it != std::end(c); ++it)`")], ("ポインタに使う", "配列の要素数が分からないポインタ（`int*`）には使えません。配列の型（`int[3]`）のときだけです。"),
  [("[`begin`](begin.md)", "先頭を返す"), ("[`ranges::end`](../ranges/begin.md)", "C++20 の版")], ["終端のイテレータを返す", "配列にも使える", "begin とセット"],
  sig="template <class C>\nconstexpr auto end(C& c) -> decltype(c.end());\ntemplate <class T, std::size_t N>\nconstexpr T* end(T (&array)[N]) noexcept;", args=[("c", "コンテナ", "対象のコンテナ"), ("array", "配列", "対象の配列")], ret="終わりを指すイテレータ", cx="定数",
  code="""#include <iterator>
#include <print>

int main() {
  int a[] = {1, 2, 3};
  std::println("{}", std::end(a) - std::begin(a));
}""", out="3", ver=("11", "C++11"), info="[`std::begin`](begin.md) を先に読んでください。", rj="iterator/end.html", cr="iterator/end")
move("support/iterator/begin.md", {"end": "support/iterator/end.md"}, "support/iterator/begin.md")

P("support/elements_of.md", "std::ranges::elements_of", "generator の中で、別の範囲の要素を全部取り出す目印。", "rare", "generator",
  "`generator` の中で、別の `generator` や `vector` の要素を、全部出したいことがあります。`for` で 1 つずつ `co_yield` するのは冗長です。`co_yield std::ranges::elements_of(range)` と書くと、範囲の要素を全部取り出せます。再帰的な木の探索で、子の結果をまとめて出すのに便利です。",
  ["`co_yield` の中で使う。", "別の `generator` を渡すと、再帰が効率よく展開される。", "C++23 の機能。"],
  [("木を深さ優先でたどる", "`co_yield std::ranges::elements_of(Walk(child));`")], ("`generator` の外で使う", "コルーチンの中（`co_yield`）でだけ使えます。"),
  [("[`std::generator`](generator.md)", "generator の本体")], ["別の範囲の要素を全部取り出す", "co_yield と使う", "再帰の展開に便利"],
  sig="template <ranges::range R, class Allocator = allocator<void>>\nelements_of(R&&, Allocator = {}) -> elements_of<R&&, Allocator>;", args=[("range", "範囲", "展開する範囲")], ret="`co_yield` に渡す目印", cx="要素数に比例",
  code="""#include <generator>
#include <print>
#include <ranges>

std::generator<int> Inner() {
  co_yield 1;
  co_yield 2;
}

std::generator<int> Outer() {
  co_yield 0;
  co_yield std::ranges::elements_of(Inner());
  co_yield 3;
}

int main() {
  int sum = 0;
  for (int x : Outer()) sum += x;
  std::println("{}", sum);
}""", out="6", ver=("23", "C++23"), info="[`std::generator`](generator.md) を先に読んでください。", rj="generator/elements_of.html", cr="coroutine/elements_of")
move("support/generator.md", {"elements_of": "support/elements_of.md"}, "support/generator.md")

P("support/functional/cref.md", "std::cref", "const 参照を、値のように渡せる reference_wrapper にする。", "rare", "functional",
  "`std::thread` や `std::bind` に引数を渡すと、値としてコピーされます。読むだけの大きなオブジェクトをコピーしたくないとき、`std::cref(x)` で包むと、const 参照として渡せます。`std::ref` の const 版です。",
  ["`std::reference_wrapper<const T>` を返す。", "`.get()` で参照を取り出せる。", "書き換えたいなら [`ref`](ref.md)。"],
  [("スレッドに大きな設定データを読み取り専用で渡す", "`std::thread t(Worker, std::cref(config));`")], ("元のオブジェクトが先に消える", "参照を渡しているだけです。スレッドが終わるまで、元のオブジェクトは生きている必要があります。"),
  [("[`ref`](ref.md)", "書き換え可能な参照"), ("[`bind_front`](bind_front.md)", "引数を固定する")], ["const 参照を値のように渡す", "ref の const 版", "元が先に消えないように"],
  sig="template <class T>\nstd::reference_wrapper<const T> cref(const T& t) noexcept;", args=[("t", "const T&", "参照で渡したいオブジェクト")], ret="`reference_wrapper<const T>`", cx="定数",
  code="""#include <functional>
#include <print>

int main() {
  int x = 1;
  auto r = std::cref(x);
  x = 2;
  std::println("{}", r.get());
}""", out="2", ver=("11", "C++11"), info="[`std::ref`](ref.md) を先に読んでください。", rj="functional/cref.html", cr="utility/functional/ref")
move("support/functional/ref.md", {"cref": "support/functional/cref.md"}, "support/functional/ref.md")

for nm, ret_t, intro, body, out_, extra in [
    ("as_bytes", "span<const byte>", "どんな型の `span` も、**読み取り専用のバイト列**（`span<const std::byte>`）として見たいことがあります。ファイルに書き出す、ネットワークに送る、GPU に渡す、といった「型を気にせずバイト列として扱う」場面で、`as_bytes` が使えます。", 'int values[] = {1, 2};\nauto bytes = std::as_bytes(std::span(values));\nstd::println("{} バイト", bytes.size());', "8 バイト", "ファイルに書く関数の引数を `std::span<const std::byte>` にしておくと、どんな型でも渡せます。"),
    ("as_writable_bytes", "span<byte>", "`as_bytes` の、書き込み可能版です。ファイルから読み込んだバイト列を、そのまま構造体の配列に流し込むときなどに使います。", 'int values[] = {1};\nauto bytes = std::as_writable_bytes(std::span(values));\nbytes[0] = std::byte{7};\nstd::println("{}", values[0]);', "7", "リトルエンディアンの環境での例です。バイト順は環境によって変わります。")]:
    P("containers/" + nm + ".md", "std::" + nm, f"span を、{'読み取り専用' if nm == 'as_bytes' else '書き込み可能'}のバイト列（{'span<const std::byte>' if nm == 'as_bytes' else 'span<std::byte>'}）として見る。", "rare", "span", intro,
      ["元の型を問わずバイト列として見られる。", "コピーはしない（元のメモリを見る）。", "`std::byte` は整数ではないので、計算には `std::to_integer` を使う。"],
      [("ファイルに構造体の配列を書き出す", "`Write(std::as_bytes(std::span(items)));`")], ("バイト順を考えない", "ファイルに書いたバイト列は、環境のバイト順（エンディアン）に依存します。別の環境で読むなら、形式を決めておきます。"),
      [("[`span`](span.md)", "span の本体"), ("[`as_writable_bytes`](as_writable_bytes.md)" if nm == "as_bytes" else "[`as_bytes`](as_bytes.md)", "もう片方")], ["span をバイト列として見る", "コピーしない", "バイト順に注意"],
      sig=f"template <class T, std::size_t N>\nstd::{ret_t} {nm}(std::span<T, N> s) noexcept;", args=[("s", "span", "元の span")], ret="バイト列として見た span", cx="定数",
      code="#include <cstddef>\n#include <print>\n#include <span>\n\nint main() {\n" + "\n".join("  " + l for l in body.split("\n")) + "\n}", out=out_, ver=("20", "C++20"), info="[`std::span`](span.md) を先に読んでください。", rj=f"span/{nm}.html", cr=f"container/span/{nm}", notes=extra)
move("containers/span.md", {"as_bytes": "containers/as_bytes.md", "as_writable_bytes": "containers/as_writable_bytes.md"}, "containers/span.md")

P("io/syncbuf.md", "std::syncbuf", "出力を溜めておき、emit() でまとめて書き出すストリームバッファ。", "rare", "syncstream",
  "複数のスレッドが同じ `cout` に書くと、行が混ざります。`syncbuf` は、書き込みを自分のバッファに溜めておき、`emit()` を呼んだときに、まとめて（途中に他のスレッドの出力を挟まず）出力先に書き出します。`osyncstream` の内部で使われている部品です。",
  ["`emit()` を呼ぶまで、書き込みは出力先に出ない。", "デストラクタでも `emit()` される。", "ふつうは `osyncstream` を使う。"],
  [("複数のスレッドのログの行が混ざらないようにする", "`std::syncbuf sb(std::cout.rdbuf());`")], ("`emit()` を呼ばずに破棄を待つ", "デストラクタで出力されますが、タイミングが遅れます。"),
  [("[`osyncstream`](osyncstream.md)", "ストリームとして使えるラッパー")], ["出力を溜めて emit でまとめて出す", "行が混ざらない", "ふつうは osyncstream"],
  sig="template <class CharT, class Traits = char_traits<CharT>, class Allocator = allocator<CharT>>\nclass basic_syncbuf;\nusing syncbuf = basic_syncbuf<char>;", args=[("sbuf", "streambuf*", "最終的な出力先のバッファ")], ret="ストリームバッファとして使う", cx="溜めた量に比例",
  code="""#include <iostream>
#include <syncstream>

int main() {
  std::syncbuf sb(std::cout.rdbuf());
  std::ostream os(&sb);
  os << "hi\\n";
  sb.emit();
}""", out="hi", ver=("20", "C++20"), info="[`std::osyncstream`](osyncstream.md) を先に読んでください。", rj="syncstream/basic_syncbuf.html", cr="io/basic_syncbuf")
move("io/osyncstream.md", {"syncbuf": "io/syncbuf.md"}, "io/osyncstream.md")

for nm, enums, intro, body, out_ in [
    ("float_round_style", "round_indeterminate / round_toward_zero / round_to_nearest / round_toward_infinity / round_toward_neg_infinity", "浮動小数点の演算が、結果を丸めるときの方向を表す列挙型です。`std::numeric_limits<T>::round_style` の型で、多くの環境は `round_to_nearest`（最も近い値へ）です。", 'std::println("{}", std::numeric_limits<float>::round_style == std::round_to_nearest);', "true"),
    ("float_denorm_style", "denorm_indeterminate / denorm_absent / denorm_present", "0 に非常に近い小さな値（非正規数）を持てるかを表す列挙型です。`std::numeric_limits<T>::has_denorm` の型で、多くの環境は `denorm_present`（持てる）です。C++23 で `has_denorm` は非推奨になりました。", 'std::println("{}", std::numeric_limits<double>::denorm_min() > 0);', "true")]:
    P("numeric/" + nm + ".md", "std::" + nm, {"float_round_style": "浮動小数点の丸めの方向を表す列挙型。", "float_denorm_style": "非正規数を持つかを表す列挙型。"}[nm], "rare", "limits", intro,
      ["`numeric_limits` のメンバが返す型。", f"値: {enums}。", "ふつうは `numeric_limits` 経由で比べる。"],
      [("環境の浮動小数点の性質を調べる", f"`std::numeric_limits<float>::{'round_style' if nm == 'float_round_style' else 'has_denorm'}`")], ("実行時に変わると思う", "この値は型の性質で、`fesetround` で変えた丸めは反映されません。"),
      [("[`std::numeric_limits`](limits.md)", "型の性質"), ("[`fesetround`](fesetround.md)", "実行時の丸めモード")], [{"float_round_style": "丸めの方向を表す列挙型", "float_denorm_style": "非正規数を持つかを表す列挙型"}[nm], "numeric_limits のメンバが返す", "ふつうは意識しない"],
      sig=f"enum {nm} {{\n  /* {enums} */\n}};", args=[], ret="なし（列挙型）", cx="なし",
      code="#include <limits>\n#include <print>\n\nint main() {\n  " + body + "\n}", out=out_, info="[`std::numeric_limits`](limits.md) を先に読んでください。", rj=f"limits/{nm}.html", cr=f"types/numeric_limits/{nm}")
move("numeric/limits.md", {"float_round_style": "numeric/float_round_style.md", "float_denorm_style": "numeric/float_denorm_style.md"}, "numeric/limits.md")

for nm, size, extra in [("float16_t", 2, "半精度（16 ビット）。GPU のテクスチャや、メモリを節約したい大量の値に向きます。"), ("bfloat16_t", 2, "ブレイン浮動小数点（16 ビット）。指数部が `float` と同じ 8 ビットで、範囲は広く精度は低い形式です。機械学習で使われます。"),
                        ("float32_t", 4, "単精度（32 ビット）。`float` と同じ大きさで、IEEE 754 の形式であることが保証されます。"), ("float64_t", 8, "倍精度（64 ビット）。`double` と同じ大きさで、IEEE 754 の形式であることが保証されます。"), ("float128_t", 16, "四倍精度（128 ビット）。精度が必要な科学計算向けで、ゲームではほとんど使いません。")]:
    old_ids = {"float32_t": "numeric/float32_t.md", "float64_t": "numeric/float64_t.md", "float128_t": "numeric/float128_t.md"}
    P("numeric/" + nm + ".md", "std::" + nm, f"{size * 8} ビットの浮動小数点型。", "rare", "stdfloat",
      f"`float` や `double` の大きさは環境で違うことがあります。`std::{nm}` は、{size * 8} ビットの浮動小数点型です。{extra}実装が対応していない場合は定義されないので、`__STDCPP_{nm.upper()}__` マクロで確かめて使います。",
      ["実装が対応していない型は定義されない。", f"`__STDCPP_{nm.upper().replace('BFLOAT16_T', 'BFLOAT16_T')}__` で対応を確かめる。", "リテラルは接尾辞（`f16`・`bf16`・`f32`・`f64`・`f128`）。"],
      [("GPU に渡す大量の値の形式", f"`std::{nm}`")], ("対応を確かめずに使う", "対応していないコンパイラでは、型が存在せずコンパイルエラーになります。"), [("[`<stdfloat>`](stdfloat.md)", "概要")],
      [f"{size * 8} ビットの浮動小数点型", "対応はマクロで確かめる", "C++23"],
      sig=f"using {nm} = /* 実装定義の {size * 8} ビット浮動小数点型 */;", args=[], ret="なし（型）", cx="コンパイル時のみ",
      code=f"#include <print>\n#include <stdfloat>\n\nint main() {{\n#ifdef __STDCPP_{nm.upper()}__\n  std::println(\"{{}}\", sizeof(std::{nm}));\n#endif\n}}", out=str(size), ver=("23", "C++23"), info="[`<stdfloat>`](stdfloat.md) を先に読んでください。", rj=f"stdfloat/{nm}.html", cr=f"types/floating-point/{nm}")
move("numeric/stdfloat.md", {k: v for k, v in {"float32_t": "numeric/float32_t.md", "float64_t": "numeric/float64_t.md", "float128_t": "numeric/float128_t.md"}.items()}, "numeric/stdfloat.md")

# ================= <cstdint> の型 =================
CINT = "numeric/cstdint/"
types = []
for b in (8, 16, 32, 64):
    for kind, label in (("", "ちょうど {b} ビット"), ("_fast", "{b} ビット以上で最も速い"), ("_least", "{b} ビット以上で最も小さい")):
        for sg in ("int", "uint"):
            types.append((f"{sg}{kind}{b}_t", sg, kind, b))
types += [("intmax_t", "int", "max", 64), ("uintmax_t", "uint", "max", 64), ("intptr_t", "int", "ptr", 0), ("uintptr_t", "uint", "ptr", 0)]
SPECIAL = {
    "int32_t": "ファイルに書くとき、`int` の代わりに使うと環境が変わっても読めます。セーブデータの数値に向きます。",
    "uint32_t": "ビットフラグや ID、RGBA の色に使います。",
    "uint8_t": "0〜255 の値（色の各成分、バイト列）に使います。中身は `unsigned char` なので、`std::cout << x` では**文字**として出ます（`std::println` なら数値）。",
    "int64_t": "21 億を超える数（所持金、ミリ秒のタイムスタンプ）に使います。",
    "uint64_t": "ハッシュ値や、世代付きのハンドルを 1 つの数に詰めるのに使います。",
    "int16_t": "音声のサンプル（16bit PCM）に使います。",
    "uint16_t": "タイルの番号など、65535 までで足りてメモリを節約したいデータに使います。",
    "int8_t": "-128〜127 の小さな値に使います。`uint8_t` と同じく、`cout` では文字として出ます。",
    "uintptr_t": "ポインタのアドレスをハッシュにしたり、アライメント（4 の倍数か）を調べたりするときに使います。",
    "intptr_t": "ポインタをそのまま入れられる大きさの符号付き整数です。",
}
cs_ids = {}
for nm, sg, kind, b in types:
    signed = sg == "int"
    if kind == "":
        what = f"ちょうど {b} ビットの{'符号付き' if signed else '符号なし'}整数"
        sz = f"sizeof(std::{nm}) == {b // 8}"
    elif kind == "_fast":
        what = f"{b} ビット以上で、その環境で最も速く扱える{'符号付き' if signed else '符号なし'}整数"
        sz = f"sizeof(std::{nm}) >= {b // 8}"
    elif kind == "_least":
        what = f"{b} ビット以上で、最も小さい{'符号付き' if signed else '符号なし'}整数"
        sz = f"sizeof(std::{nm}) >= {b // 8}"
    elif kind == "max":
        what = f"その環境で最も大きい{'符号付き' if signed else '符号なし'}整数"
        sz = f"sizeof(std::{nm}) >= 8"
    else:
        what = f"ポインタをそのまま入れられる大きさの{'符号付き' if signed else '符号なし'}整数"
        sz = f"sizeof(std::{nm}) == sizeof(void*)"
    hint = SPECIAL.get(nm, "")
    extra_code = ""
    code_ = f"#include <cstdint>\n#include <print>\n\nint main() {{\n  std::println(\"{{}}\", {sz});\n}}"
    out_ = "true"
    if nm == "uint8_t":
        code_ = '#include <cstdint>\n#include <iostream>\n#include <print>\n\nint main() {\n  std::uint8_t level = 65;\n  std::cout << level << \' \' << static_cast<int>(level) << \'\\n\';  // 1 つ目は \'A\'\n  std::println("{}", level);  // println は数値で出す\n}'
        out_ = "A 65\n65"
    exact = kind == ""
    P(CINT + nm + ".md", "std::" + nm, f"{what}。", "often" if nm in ("int32_t", "uint32_t", "uint8_t", "int64_t") else "sometimes" if nm in ("uint64_t", "int16_t", "uint16_t") else "rare", "cstdint",
      f"`int` や `long` の大きさは環境で違います。`std::{nm}` は、{what}を表す型です。{hint}" + ("実装が対応していなくても定義される必要がない型（`optional` な型）なので、極端に特殊な環境では使えないことがあります。" if exact and b in (8, 16, 32, 64) else ""),
      [f"{what}。", "`<cstdint>` で定義される。", "普通の計算には `int` でよく、ファイル・通信・ビット操作で大きさを固定したいときに使う。" if exact else "大きさにこだわらない移植性のある書き方に使う。"],
      [("ファイル・通信・ビットフラグ", f"`std::{nm}`")], ("符号なしの引き算で負になると思う", "符号なしの型は、引いて 0 を下回ると、非常に大きな値にぐるっと回ります。" if not signed else "オーバーフローは未定義動作です。範囲を超える計算に注意します。"),
      [("[`<cstdint>`](../cstdint.md)", "整数型の一覧")], [what, "大きさを意識するときに使う", "普通の計算は int で足りる"],
      sig=f"using {nm} = /* {'符号付き' if signed else '符号なし'}整数型 */;", args=[], ret="なし（型）", cx="コンパイル時のみ",
      code=code_, out=out_, ver=("11", "C++11"), info="[`<cstdint>`](../cstdint.md) を先に読んでください。", rj=f"cstdint/{nm}.html", cr=f"types/integer")
    cs_ids[nm] = f"numeric/cstdint/{nm}.md"
# 旧ページの節を消して、一覧の表へのリンクを新しいページに付け替える
old = "numeric/cstdint.md"
ids_ = {}
for nm in ("int32_t", "uint32_t", "uint8_t", "int64_t", "uint64_t", "int16_t", "uint16_t", "int8_t", "intptr_t", "uintptr_t", "int_fast32_t", "int_least32_t", "int_fast8_t", "int_least8_t", "intmax_t", "uintmax_t"):
    ids_[nm] = f"numeric/cstdint/{nm}.md"
move(old, ids_, old)
p_ = STL / old
t_ = p_.read_text(encoding="utf-8")
# 表のページ内リンク (#xxx) を、新しいページへのリンクに直す
for nm in ids_:
    t_ = t_.replace(f"](#{nm})", f"](cstdint/{nm}.md)")
p_.write_text(t_, encoding="utf-8", newline="")
# 型の詳しい説明 / フラグ・オプションの節に、全部の型へのリンク表を足す
rows = "\n".join(f"| [`std::{nm}`](cstdint/{nm}.md) | {('符号付き' if sg == 'int' else '符号なし')} | " + ({"": "ちょうど", "_fast": "最も速い", "_least": "最も小さい", "max": "最大", "ptr": "ポインタ用"}[kind]) + " |" for nm, sg, kind, b in types)
add_list_text = "\n## 全部の型\n\n| 型 | 符号 | 種類 |\n| --- | --- | --- |\n" + rows + "\n"
t_ = p_.read_text(encoding="utf-8")
if "## 全部の型" not in t_:
    m = re.search(r"(?m)^## フラグ・オプション", t_)
    pos = m.start() if m else len(t_)
    t_ = t_[:pos] + add_list_text.lstrip("\n") + "\n" + t_[pos:]
    p_.write_text(t_, encoding="utf-8", newline="")

# ================= setjmp / longjmp =================
P("io/setjmp.md", "setjmp", "いまの実行位置を記録する（あとで longjmp で戻れる）。", "rare", "csetjmp",
  "「ここへあとで戻ってきたい」という実行位置を記録するのが `setjmp` です。最初は 0 を返し、あとで `longjmp` で戻ってくると、`longjmp` に渡された値（0 以外）を返します。C のエラー処理で使われた仕組みです。C++ ではデストラクタが呼ばれず危険なので、例外を使います。",
  ["`setjmp(env)` が位置を記録する（最初は 0 を返す）。", "`longjmp` で戻ってくると、0 以外の値を返す。", "C++ では例外を使う。"],
  [("C のライブラリのエラー処理の理解", "`longjmp` が使われていたら、C++ の境界を越えない")], ("デストラクタが呼ばれない", "間にあるオブジェクトのデストラクタは呼ばれず、リソースがリークします。"),
  [("[`longjmp`](longjmp.md)", "記録した位置に戻る"), ("[`std::exception`](../support/exceptions/exception.md)", "安全な代わり")], ["実行位置を記録する", "最初は 0、戻ってくると 0 以外", "C++ では例外"],
  sig="int setjmp(jmp_buf env);  // マクロ", args=[("env", "jmp_buf", "位置を保存する場所")], ret="記録したときは 0、`longjmp` で戻ってきたときは、その値", cx="O(1)",
  code="""#include <csetjmp>
#include <print>

std::jmp_buf g_env;

int main() {
  if (setjmp(g_env) == 0) {
    std::longjmp(g_env, 1);  // setjmp の場所へ戻る
  } else {
    std::println("戻ってきた");
  }
}""", out="戻ってきた", info="[`<csetjmp>`](csetjmp.md) の概要を先に読んでください。", rj="csetjmp/setjmp.html", cr="utility/program/setjmp", compiler="C 由来の機能です。C++ のどの版でも使えます。")
P("io/longjmp.md", "std::longjmp", "setjmp で記録した位置へ、一気に戻る。", "rare", "csetjmp",
  "`setjmp` で記録した位置まで、途中の関数を全部飛ばして戻ります。途中のオブジェクトのデストラクタは呼ばれないので、C++ では例外（`throw` / `catch`）を使うのが安全です。",
  ["`setjmp` で記録した位置に戻る。", "戻らない関数（`[[noreturn]]`）。", "`value` が 0 だと、`setjmp` は 1 を返す。"],
  [("C のライブラリのエラー処理の理解", "C のライブラリが `longjmp` でエラーを返す設計のとき、境界を越えないようにする")], ("C++ のオブジェクトがある関数をまたぐ", "デストラクタが呼ばれずリークします。例外を使います。"),
  [("[`setjmp`](setjmp.md)", "位置を記録する")], ["記録した位置へ飛ぶ", "戻らない", "デストラクタが呼ばれない"],
  sig="[[noreturn]] void longjmp(jmp_buf env, int value);", args=[("env", "jmp_buf", "`setjmp` で記録した場所"), ("value", "int", "`setjmp` が返す値（0 なら 1 になる）")], ret="戻らない", cx="O(1)",
  code="""#include <csetjmp>
#include <print>

std::jmp_buf g_env;

void Fail() {
  std::longjmp(g_env, 2);
}

int main() {
  int r = setjmp(g_env);
  if (r == 0) {
    Fail();
  } else {
    std::println("エラー {}", r);
  }
}""", out="エラー 2", info="[`<csetjmp>`](csetjmp.md) の概要を先に読んでください。", rj="csetjmp/longjmp.html", cr="utility/program/longjmp", compiler="C 由来の機能です。C++ のどの版でも使えます。")
# csetjmp.md は <csetjmp> の概要ページにする
p_ = STL / "io/csetjmp.md"
t_ = p_.read_text(encoding="utf-8")
t_ = t_.replace("title: setjmp / longjmp", "title: <csetjmp>（setjmp と longjmp）").replace("# setjmp / longjmp", "# &lt;csetjmp&gt;（setjmp と longjmp）")
t_ = re.sub(r"(?ms)^### setjmp / longjmp \{#csetjmp\}.*?(?=^## ゲームでの使いどころ)",
            "### 関数\n\n| 名前 | 何をする |\n| --- | --- |\n| [`setjmp`](setjmp.md) | 実行位置を記録する |\n| [`longjmp`](longjmp.md) | 記録した位置へ戻る |\n\n", t_)
t_ = t_.replace("### 関数\n", "### 関数一覧 {#functions}\n", 1)
p_.write_text(t_, encoding="utf-8", newline="")
record_moves("stl/io/csetjmp.md", {"csetjmp": "stl/io/setjmp.md"}, "stl/io/csetjmp.md")

# ================= new[] / delete[] と operator new / delete =================
P("memory/new_delete/delete_array.md", "delete[]", "new[] で確保した配列を解放する。", "rare", "new",
  "`new T[n]` で確保した配列は、必ず `delete[] p` で解放します。`delete p`（`[]` なし）だと、先頭の 1 個のデストラクタしか呼ばれず、未定義動作です。配列の大きさはポインタからは取れませんが、`delete[]` が内部で覚えている個数ぶんのデストラクタを呼びます。ほぼ使わず、`std::vector` や `std::unique_ptr<T[]>` を使います。",
  ["`new[]` と必ず対にする。", "`delete`（`[]` なし）で消すと未定義動作。", "`nullptr` に使っても安全。"],
  [("（古い C++ のコードの保守）", "`delete[] p;`")], ("`delete` で消す", "配列を `delete`（`[]` なし）で消すと未定義動作です。"),
  [("[`new[]`](new_array.md)", "確保する"), ("[`std::unique_ptr<T[]>`](../../utilities/unique_ptr.md)", "自動で解放")], ["new[] で確保した配列を消す", "必ず delete[]", "unique_ptr<T[]> を使う"],
  sig="void operator delete[](void* ptr) noexcept;  // delete[] p; の中身", args=[("p", "T*", "`new[]` で確保したポインタ")], ret="なし", cx="O(要素数)",
  code="""#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  Tracer* p = new Tracer[3];
  std::println("{}", Tracer::alive);
  delete[] p;
  std::println("{}", Tracer::alive);
}""", out="3\n0", info="[`new[]`](new_array.md) を先に読んでください。", rj="new/operator_delete.html", cr="memory/delete_array")
sub_in("memory/new_delete/new_array.md", [("title: new[] と delete[]", "title: new[]"), ("# new[] と delete[]", "# new[]"), ('### new[] / delete[] {#new_array data-toc-label="new[] と delete[]"}', '### new[] {#new_array data-toc-label="new[]"}')])
P("memory/new_delete/operator_delete.md", "operator delete", "new 式の「解放の部分」だけを行う関数（デストラクタは呼ばない）。", "rare", "new",
  "`delete p` は、デストラクタを呼んでから、メモリを解放します。この**メモリの解放だけ**を担当するのが `operator delete` です。`operator new` と対にして差し替えると、メモリの使用量の計測や、独自のアロケータへの切り替えができます。",
  ["`operator new` と対にする。", "`size` つきの版（C++14）は、確保した大きさが分かる。", "差し替えは、プロジェクトに 1 組だけ。"],
  [("全体のメモリ使用量を計測する", "`operator new` / `operator delete` を差し替えて、確保量を数える")], ("`new` と `delete` の対応を崩す", "差し替えるときは、`new` と `delete` の両方を、同じ方式にします。"),
  [("[`operator new`](operator_new.md)", "確保の部分"), ("[`delete`](delete.md)", "delete 式")], ["解放だけを行う関数", "operator new と対にする", "差し替えて計測に使う"],
  sig="void operator delete(void* p) noexcept;\nvoid operator delete(void* p, std::size_t size) noexcept;  // サイズ付き（C++14）\nvoid operator delete(void* p, std::align_val_t alignment) noexcept;  // C++17", args=[("p", "void*", "解放するポインタ"), ("size", "size_t", "確保したバイト数（サイズ付き版）")], ret="なし", cx="アロケータに依存",
  code="""#include <cstdlib>
#include <new>
#include <print>

int g_freed = 0;

void* operator new(std::size_t size) {
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}

void operator delete(void* p) noexcept {
  ++g_freed;
  std::free(p);
}

int main() {
  int* p = new int(1);
  delete p;
  std::println("{}", g_freed);
}""", out="1", ver=None, info="[`operator new`](operator_new.md) を先に読んでください。", rj="new/operator_delete.html", cr="memory/new/operator_delete")
sub_in("memory/new_delete/operator_new.md", [("title: operator new / operator delete", "title: operator new"), ("# operator new / operator delete", "# operator new"), ('### operator new / operator delete {#operator_new data-toc-label="operator new と operator delete"}', '### operator new {#operator_new data-toc-label="operator new"}')])

# ================= ios_base の型 =================
for nm, base_, what, intro in [
    ("streamsize", "整数", "ストリームで読み書きする文字数を表す符号付き整数型。", "`read(buf, n)` の `n` や `gcount()` の戻り値のように、「何文字読み書きするか」を表す型です。符号付きなので、`-1` のような値も表せます。"),
    ("streamoff", "整数", "ストリーム上の位置の差（オフセット）を表す符号付き整数型。", "`seekg(off, dir)` の `off` のように、ストリームの位置を相対的に動かす量を表す型です。"),
    ("streampos", "fpos", "ストリーム上の位置を表す型。", "`tellg()` が返し、`seekg(pos)` に渡す型です。`fpos<mbstate_t>` の別名で、マルチバイト文字の状態も含められます。整数と見なして計算するのは移植性がありません。"),
    ("fpos", "クラス", "ストリームの位置を状態つきで表すクラス。", "マルチバイト文字のように、位置に状態が必要なストリームのための位置の型です。`tellg()` の戻り値（`streampos`）がこれです。整数のように `streamoff` を足し引きできますが、`tellg()` で得た値以外の演算は移植性がありません。")]:
    P("io/" + nm + ".md", "std::" + nm, what, "rare", "ios", intro,
      ["入出力の位置・大きさを表す型。", "`<ios>` で定義される。", "ふつうは `auto` で受ける。"],
      [("ファイルの途中に戻る", "`auto pos = in.tellg(); ... in.seekg(pos);`")], ("`int` で受ける", "大きなファイルで桁あふれします。`auto` か、この型で受けます。"),
      [("[`ios_base`](ios_base.md)", "ストリームの土台"), ("[`ifstream`](ifstream.md)", "ファイル入力")], [what.rstrip("。"), "tellg / seekg で使う", "auto で受けるのが安全"],
      sig=(f"using {nm} = /* 実装定義の整数型 */;" if nm in ("streamsize", "streamoff") else "using streampos = fpos<mbstate_t>;" if nm == "streampos" else "template <class StateT>\nclass fpos;"), args=[], ret="なし（型）", cx="なし",
      code="#include <fstream>\n#include <print>\n#include <sstream>\n\nint main() {\n  std::istringstream in(\"abc\");\n  in.get();\n  std::" + ("streampos" if nm in ("streampos", "fpos") else nm) + (" pos = in.tellg();\n  std::println(\"{}\", static_cast<long long>(pos));" if nm in ("streampos", "fpos") else (" n = in.gcount();\n  std::println(\"{}\", static_cast<long long>(n));" if nm == "streamsize" else " off = 1;\n  in.seekg(off, std::ios::cur);\n  std::println(\"{}\", static_cast<char>(in.get()));")) + "\n}",
      out={"streampos": "1", "fpos": "1", "streamsize": "1", "streamoff": "c"}[nm], info="[`std::ios_base`](ios_base.md) を先に読んでください。", rj=f"ios/{nm}.html", cr=f"io/{nm}")
move("io/ios_base.md", {"streamsize": "io/streamsize.md", "streamoff": "io/streamoff.md", "streampos": "io/streampos.md", "fpos": "io/fpos.md"}, "io/ios_base.md")

# ================= filesystem の列挙型 =================
FSG = "ファイル操作（std::filesystem）"
FSI = "[`std::filesystem`](../filesystem.md) の概要を先に読んでください。"
P("io/filesystem/copy_options.md", "std::filesystem::copy_options", "copy / copy_file の動作（上書き・再帰など）を指定するビットマスク型。", "often", "filesystem",
  "ファイルをコピーするとき、「すでにあったら上書きするか」「フォルダの中身も全部コピーするか」といった動作を選びたくなります。それを指定するのが `copy_options` で、`fs::copy(from, to, オプション)` の第 3 引数に渡します。`|` で組み合わせられます。",
  ["`overwrite_existing`: すでにあれば上書き。", "`recursive`: フォルダの中身も全部コピー。", "オプションを省略すると、すでにあるとエラー。"],
  [("セーブデータのフォルダをバックアップ", "`fs::copy(\"saves\", \"backup\", fs::copy_options::recursive | fs::copy_options::overwrite_existing);`")], ("省略して上書きを期待する", "オプションを省略すると、コピー先があるときにエラーになります。`overwrite_existing` を付けます。"),
  [("[`copy`](copy.md)", "コピーする"), ("[`copy_file`](copy_file.md)", "ファイル 1 つのコピー")], ["コピーの動作を指定する", "| で組み合わせる", "overwrite_existing / recursive"],
  secs=[fn("std::filesystem::copy_options", "enum class copy_options : unsigned {\n  none = 0,\n  skip_existing = 1, overwrite_existing = 2, update_existing = 4,\n  recursive = 8,\n  copy_symlinks = 16, skip_symlinks = 32,\n  directories_only = 64, create_symlinks = 128, create_hard_links = 256\n};", None, "ビットマスク", "", None, ids="copy_options",
           notes="| 値 | 重要度 | 意味 |\n| --- | --- | --- |\n| `none` | <span class=\"rank rank-often\">よく使う</span> | 何もしない（すでにあるとエラー） |\n| `overwrite_existing` | <span class=\"rank rank-often\">よく使う</span> | すでにあれば上書き |\n| `recursive` | <span class=\"rank rank-sometimes\">たまに</span> | フォルダの中身も全部コピー |\n| `skip_existing` | <span class=\"rank rank-sometimes\">たまに</span> | すでにあれば何もしない |\n| `update_existing` | <span class=\"rank rank-sometimes\">たまに</span> | コピー元のほうが新しければ上書き |\n| `directories_only` | <span class=\"rank rank-rare\">知ってるだけ</span> | フォルダの構造だけコピー |\n| `copy_symlinks` / `skip_symlinks` | <span class=\"rank rank-rare\">知ってるだけ</span> | シンボリックリンクの扱い |\n| `create_symlinks` / `create_hard_links` | <span class=\"rank rank-rare\">知ってるだけ</span> | コピーの代わりにリンクを作る |\n\n`|` で組み合わせられます（`recursive | overwrite_existing`）。")],
  code="""#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path a = fs::temp_directory_path() / "kdocs_co_a.txt";
  fs::path b = fs::temp_directory_path() / "kdocs_co_b.txt";
  std::ofstream(a) << "x";
  std::ofstream(b) << "y";
  fs::copy_file(a, b, fs::copy_options::overwrite_existing);
  std::println("{}", fs::file_size(b));
  fs::remove(a);
  fs::remove(b);
}""", out="1", ver=("17", "C++17"), info=FSI, group=FSG, rj="filesystem/copy_options.html", cr="filesystem/copy_options")
P("io/filesystem/directory_options.md", "std::filesystem::directory_options", "フォルダの走査の動作（権限のないフォルダを飛ばすなど）を指定する型。", "sometimes", "filesystem",
  "フォルダの中身を `directory_iterator` で順に調べるとき、権限のないフォルダに入るとエラーになります。`skip_permission_denied` を指定すると、そのようなフォルダを飛ばして走査を続けられます。",
  ["`none`: 既定。", "`skip_permission_denied`: 権限のないフォルダを飛ばす。", "`follow_directory_symlink`: リンク先のフォルダにも入る。"],
  [("ゲームのデータフォルダを走査する", "`fs::recursive_directory_iterator(dir, fs::directory_options::skip_permission_denied)`")], ("`follow_directory_symlink` で無限ループ", "リンクが循環していると、走査が終わりません。"),
  [("[`directory_iterator`](directory_iterator.md)", "フォルダを走査する"), ("[`recursive_directory_iterator`](recursive_directory_iterator.md)", "再帰的に走査する")], ["走査の動作を指定する", "skip_permission_denied", "| で組み合わせられる"],
  secs=[fn("std::filesystem::directory_options", "enum class directory_options : unsigned {\n  none = 0,\n  follow_directory_symlink = 1,\n  skip_permission_denied = 2\n};", None, "ビットマスク", "", None, ids="directory_options",
           notes="| 値 | 重要度 | 意味 |\n| --- | --- | --- |\n| `none` | <span class=\"rank rank-often\">よく使う</span> | デフォルト |\n| `skip_permission_denied` | <span class=\"rank rank-sometimes\">たまに</span> | 権限の無いフォルダを飛ばす（エラーにしない） |\n| `follow_directory_symlink` | <span class=\"rank rank-rare\">知ってるだけ</span> | リンク先のフォルダにも入る |")],
  code="""#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::directory_iterator it(fs::current_path(), fs::directory_options::skip_permission_denied);
  std::println("{}", it != fs::directory_iterator{});
}""", out="true", ver=("17", "C++17"), info=FSI, group=FSG, rj="filesystem/directory_options.html", cr="filesystem/directory_options")
P("io/filesystem/file_type.md", "std::filesystem::file_type", "ファイルの種類（通常ファイル・フォルダ・リンクなど）を表す列挙型。", "sometimes", "filesystem",
  "`fs::status(p).type()` が返すのが、ファイルの種類を表す `file_type` です。通常のファイルか、フォルダか、シンボリックリンクか、存在しないかを区別できます。ふつうは `is_regular_file` や `is_directory` のほうが読みやすいです。",
  ["`regular`: 普通のファイル。", "`directory`: フォルダ。", "`not_found`: 存在しない（エラーではなく、この値）。"],
  [("パスの種類で処理を分ける", "`switch (fs::status(p).type()) { ... }`")], ("存在しないのを例外だと思う", "存在しないパスの `status` は、例外にならず `not_found` を返します。"),
  [("[`status`](status.md)", "種類を取得する"), ("[`is_regular_file`](is_regular_file.md)", "通常ファイルか"), ("[`is_directory`](is_directory.md)", "フォルダか")], ["ファイルの種類を表す列挙型", "status(p).type() の値", "存在しないのは not_found"],
  secs=[fn("std::filesystem::file_type", "enum class file_type {\n  none, not_found, regular, directory, symlink, block, character, fifo, socket, unknown\n};", None, "列挙型", "", None, ids="file_type",
           notes="| 値 | 意味 |\n| --- | --- |\n| `regular` | 普通のファイル |\n| `directory` | フォルダ |\n| `not_found` | 存在しない |\n| `symlink` | シンボリックリンク |\n| `block` / `character` / `fifo` / `socket` / `unknown` | 特殊なファイル（ゲームでは見ない） |\n| `none` | 状態を取得できていない |")],
  code="""#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  std::println("{}", fs::status(fs::current_path()).type() == fs::file_type::directory);
  std::println("{}", fs::status("no_such_file_kdocs").type() == fs::file_type::not_found);
}""", out="true\ntrue", ver=("17", "C++17"), info=FSI, group=FSG, rj="filesystem/file_type.html", cr="filesystem/file_type")
p_ = STL / "io/filesystem.md"
t_ = p_.read_text(encoding="utf-8")
t_ = re.sub(r"(?ms)^### copy_options\n.*?(?=^## 古い書き方と今の書き方)",
            "### copy_options\n\n[`copy_options`](filesystem/copy_options.md)（`copy` の動作の指定）を参照してください。\n\n### directory_options\n\n[`directory_options`](filesystem/directory_options.md)（フォルダの走査の動作の指定）を参照してください。\n\n### file_type\n\n[`file_type`](filesystem/file_type.md)（`status(p).type()` の値）を参照してください。\n\n", t_)
p_.write_text(t_, encoding="utf-8", newline="")
record_moves("stl/io/filesystem.md", {"copy_options": "stl/io/filesystem/copy_options.md", "directory_options": "stl/io/filesystem/directory_options.md", "file_type": "stl/io/filesystem/file_type.md"}, "stl/io/filesystem.md")

if __name__ == "__main__":
    flush_hubs()
