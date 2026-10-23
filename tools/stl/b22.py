"""バッチ 22: 取りこぼしの補充その 2（type_traits、iterator / ranges の関数、try_lock、ranlux48）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mk import *  # noqa: F401,F403,E402
from b10 import T  # noqa: E402

NT = "struct Th {\n  Th() {}\n};"
T("is_empty", "型が空（非静的なメンバ変数を持たない）かを調べる。", "メンバ変数も仮想関数も持たない空のクラスは、「型だけの目印」として使われます。そうした型かを判定します。空の基底クラスは、継承しても大きさが増えない最適化（空の基底の最適化）の対象になります。", "std::is_empty_v<E>", "std::is_empty_v<NE>", pre="struct E {};\nstruct NE {\n  int x;\n};")
T("is_signed", "型が符号付きの算術型かを調べる。", "`int` や `float` のように、負の値を持てる算術型かを判定します。`unsigned` と `bool` は `false` です。", "std::is_signed_v<int>", "std::is_signed_v<unsigned>")
T("rank", "配列の次元の数を返す。", "`int[2][3]` のような配列が、何次元かを調べます。配列でない型は 0 です。", "std::rank_v<int[2][3]>", "std::rank_v<int>", true_out="2", false_out="0", miss=("要素数と取り違える", "`rank` は次元の数です。要素数は `extent` で調べます。"), params=("T",))
T("extent", "配列の指定した次元の要素数を返す。", "`int[2][3]` の 0 番目の次元の要素数は 2、1 番目は 3 です。配列でない、または要素数が不明な次元では 0 です。", "std::extent_v<int[2][3]>", "std::extent_v<int[2][3], 1>", true_out="2", false_out="3", miss=("要素数が不明な配列で期待する", "`int[]` のように要素数が不明なら 0 です。"), params=("T", "N = 0"))
T("is_nothrow_copy_constructible", "例外を投げずにコピーして構築できる型かを調べる。", "`noexcept` でコピーできるかを判定します。`vector` の再確保が、ムーブとコピーのどちらを選ぶかなどの分岐に使われます。", "std::is_nothrow_copy_constructible_v<int>", "std::is_nothrow_copy_constructible_v<std::string>", extra_inc=("string",))
T("is_nothrow_default_constructible", "例外を投げずに既定構築できる型かを調べる。", "引数なしの構築が `noexcept` かを判定します。", "std::is_nothrow_default_constructible_v<int>", "std::is_nothrow_default_constructible_v<Th>", pre=NT)
T("is_trivially_default_constructible", "既定構築が自明（何もしなくてよい）な型かを調べる。", "ユーザー定義のコンストラクタを経由しない、既定構築かを判定します。この型の配列は、メモリを確保するだけで使い始められます。", "std::is_trivially_default_constructible_v<int>", "std::is_trivially_default_constructible_v<Th>", pre=NT)
T("is_trivially_copy_constructible", "コピーして構築するのが自明（メモリのコピーだけ）な型かを調べる。", "コピーコンストラクタが、メモリのコピーで済むかを判定します。`memcpy` で安全にコピーできる条件のひとつです。", "std::is_trivially_copy_constructible_v<int>", "std::is_trivially_copy_constructible_v<std::string>", extra_inc=("string",))
T("is_trivially_move_constructible", "ムーブして構築するのが自明（メモリのコピーだけ）な型かを調べる。", "ムーブコンストラクタが、メモリのコピーで済むかを判定します。", "std::is_trivially_move_constructible_v<int>", "std::is_trivially_move_constructible_v<std::string>", extra_inc=("string",))
T("is_trivially_assignable", "代入が自明（メモリのコピーだけ）な型の組かを調べる。", "`T = U` が、メモリのコピーで済むかを判定します。左辺は参照の型で渡します。", "std::is_trivially_assignable_v<int&, int>", "std::is_trivially_assignable_v<std::string&, const std::string&>", params=("T", "U"), extra_inc=("string",))
T("is_trivially_copy_assignable", "コピー代入が自明（メモリのコピーだけ）な型かを調べる。", "コピー代入が、メモリのコピーで済むかを判定します。", "std::is_trivially_copy_assignable_v<int>", "std::is_trivially_copy_assignable_v<std::string>", extra_inc=("string",))
T("is_trivially_move_assignable", "ムーブ代入が自明（メモリのコピーだけ）な型かを調べる。", "ムーブ代入が、メモリのコピーで済むかを判定します。", "std::is_trivially_move_assignable_v<int>", "std::is_trivially_move_assignable_v<std::string>", extra_inc=("string",))
T("is_nothrow_assignable", "例外を投げずに代入できる型の組かを調べる。", "`T = U` が `noexcept` かを判定します。左辺は参照の型で渡します。", "std::is_nothrow_assignable_v<int&, int>", "std::is_nothrow_assignable_v<std::string&, const char*>", params=("T", "U"), extra_inc=("string",))
T("is_nothrow_copy_assignable", "例外を投げずにコピー代入できる型かを調べる。", "コピー代入が `noexcept` かを判定します。", "std::is_nothrow_copy_assignable_v<int>", "std::is_nothrow_copy_assignable_v<std::string>", extra_inc=("string",))
T("is_nothrow_move_assignable", "例外を投げずにムーブ代入できる型かを調べる。", "ムーブ代入が `noexcept` かを判定します。`vector` の操作が強い例外保証を保つために、この結果を見て、ムーブとコピーを選びます。ムーブ代入に `noexcept` を付け忘れると、効率が落ちます。", "std::is_nothrow_move_assignable_v<int>", "std::is_nothrow_move_assignable_v<MA>", pre="struct MA {\n  MA& operator=(MA&&) { return *this; }\n};")
T("is_nothrow_invocable_r", "指定した引数で例外を投げずに呼び出せ、結果を R に変換できるかを調べる。", "`is_invocable_r` に、`noexcept` であることを足した条件です。", "std::is_nothrow_invocable_r_v<double, decltype(&Safe), int>", "std::is_nothrow_invocable_r_v<double, decltype(&Maybe), int>", ver="17", params=("R", "F", "Args..."), pre="int Safe(int) noexcept;\nint Maybe(int);")
T("is_nothrow_swappable_with", "2 つの型の値を、例外を投げずに `swap` できるかを調べる。", "異なる型どうしを入れ替えられ、しかも `noexcept` かを判定します。参照の型を渡します。", "std::is_nothrow_swappable_with_v<int&, int&>", "std::is_nothrow_swappable_with_v<int&, long&>", ver="17", params=("T", "U"), extra_inc=("utility",))
T("is_virtual_base_of", "型が、別の型の仮想基底クラスかを調べる。", "ひし形継承で使う `virtual` 継承の、基底クラスかどうかを判定します。", "std::is_virtual_base_of_v<V, D>", "std::is_virtual_base_of_v<D, V>", ver="26", params=("Base", "Derived"), pre="struct V {};\nstruct D : virtual V {};")
Q("support/type_traits/is_pointer_interconvertible_with_class.md", "std::is_pointer_interconvertible_with_class", "メンバへのポインタが、クラスの先頭のメンバを指すかを調べる。", "rare", ["type_traits", "print"],
  "標準レイアウトのクラスの先頭のメンバは、そのクラスのオブジェクトと同じアドレスにあります。`is_pointer_interconvertible_with_class(&S::m)` は、メンバ `m` がそのような先頭のメンバか（ポインタを相互に変換してよいか）を、コンパイル時に調べます。",
  ["`constexpr` の関数。", "先頭のメンバなら `true`。", "ほとんど使わない。"], "template <class S, class M>\nconstexpr bool is_pointer_interconvertible_with_class(M S::* mp) noexcept;", [("mp", "メンバへのポインタ", "調べるメンバ")], "先頭のメンバなら `true`",
  'std::println("{}", std::is_pointer_interconvertible_with_class(&S::m));\nstd::println("{}", std::is_pointer_interconvertible_with_class(&S::n));', "true\nfalse",
  use="C のライブラリとの境界で、構造体の先頭を相互変換する", miss=("標準レイアウトでない型に使う", "標準レイアウトでないと、結果は `false` です。"), sim=[("[`is_pointer_interconvertible_base_of`](is_pointer_interconvertible_base_of.md)", "基底クラスとの変換")],
  cx="コンパイル時のみ", ver=("20", "C++20"), hub="support/type_traits.md", hubname="<type_traits>", rj="type_traits/is_pointer_interconvertible_with_class.html", cr="types/is_pointer_interconvertible_with_class", pre="struct S {\n  int m;\n  int n;\n};")

# ---- iterator の関数
IT = "support/iterator/"
ITI = "[`std::begin`](begin.md) を先に読んでください。"


def IF(name, summary, intro, sig, body, out, simname):
    Q(IT + name + ".md", "std::" + name, summary, "sometimes" if name in ("cbegin", "rbegin") else "rare", ["iterator", "vector", "print"], intro,
      ["コンテナでも C の配列でも同じ書き方で使える。", "`c." + name + "()` と同じ働き。", "ジェネリックなコードで使う。"], sig, [("c", "コンテナ / 配列", "対象")], summary.rstrip("。"), body, out,
      use="ジェネリックな走査を書く", miss=("空のコンテナの先頭を読む", "空のコンテナで `*" + name + "(c)` を読むと未定義動作です。`empty()` で確かめます。" if "begin" in name else "終端の位置は読めません。"),
      sim=[(simname, "対になる関数"), ("[`std::begin`](begin.md)", "先頭")], cx="定数", ver=("14", "C++14") if name.startswith(("cb", "ce", "rb", "re")) else None, info=ITI, hub="support/iterator.md", hubname="<iterator>", rj=f"iterator/{name}.html", cr=f"iterator/{name}")


IF("cbegin", "コンテナや配列の先頭を指す、const のイテレータを返す。", "読むだけの走査では、書き換えられない `const_iterator` を使うほうが安全です。`std::cbegin(c)` は、コンテナなら `c.cbegin()`、配列なら先頭へのポインタを返します。", "template <class C>\nconstexpr auto cbegin(const C& c) -> decltype(std::begin(c));", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::cbegin(v));', "1", "[`cend`](cend.md)")
IF("cend", "コンテナや配列の終端を指す、const のイテレータを返す。", "`cbegin` と組み合わせて、読むだけの走査の終わりを表します。", "template <class C>\nconstexpr auto cend(const C& c) -> decltype(std::end(c));", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::distance(std::cbegin(v), std::cend(v)));', "3", "[`cbegin`](cbegin.md)")
IF("rbegin", "コンテナや配列の逆順の先頭（最後の要素）を指すイテレータを返す。", "後ろから前へ走査したいとき、`std::rbegin(c)` が、最後の要素を指すイテレータを返します。コンテナなら `c.rbegin()`、配列なら `reverse_iterator` を作って返します。", "template <class C>\nconstexpr auto rbegin(C& c) -> decltype(c.rbegin());", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::rbegin(v));', "3", "[`rend`](rend.md)")
IF("rend", "コンテナや配列の逆順の終端（先頭の手前）を指すイテレータを返す。", "`rbegin` と組み合わせて、逆順の走査の終わりを表します。", "template <class C>\nconstexpr auto rend(C& c) -> decltype(c.rend());", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::distance(std::rbegin(v), std::rend(v)));', "3", "[`rbegin`](rbegin.md)")

# ---- ranges の関数オブジェクト
RGD = "support/ranges/"
RGI = "[`std::ranges::begin`](begin.md) を先に読んでください。"


def RF(name, summary, intro, sig, body, out, ret, simname, ver=("20", "C++20")):
    Q(RGD + name + ".md", "std::ranges::" + name, summary, "rare", ["ranges", "vector", "print"], intro,
      ["配列・コンテナ・view に同じ書き方で使える。", "関数ではなく、関数オブジェクト（カスタマイズポイント）。", "使えない型には、コンパイルエラーになる。"], sig, [("t", "範囲", "対象の範囲")], ret, body, out,
      use="ジェネリックなコードで、範囲を扱う", miss=("`std::` の同名の関数と混ぜる", "`std::" + name + "` とは別物です。`ranges::` 版は、範囲に必要な条件を満たさない型を、早めに弾いてくれます。"),
      sim=[(simname, "対になる関数"), ("[`std::ranges::begin`](begin.md)", "先頭")], cx="定数", ver=ver, info=RGI, hub=None, rj=f"ranges/{name}.html", cr=f"ranges/{name}", group="ranges の基本部品")


RF("end", "範囲の終端を指すイテレータ（またはセンチネル）を返す。", "`ranges::begin` と組み合わせて、範囲の終端を取ります。C++20 の範囲では、終端が先頭とは別の型（センチネル）のことがあり、`ranges::end` はそれを返します。", "inline constexpr /* カスタマイズポイント */ ranges::end;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::ranges::end(v) - std::ranges::begin(v));', "3", "終端のイテレータ（センチネル）", "[`begin`](begin.md)")
RF("cbegin", "範囲の先頭を指す、const のイテレータを返す。", "読むだけの走査では、書き換えられないイテレータを使うほうが安全です。`ranges::cbegin(r)` は、`ranges::begin` の const 版です。", "inline constexpr /* カスタマイズポイント */ ranges::cbegin;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::ranges::cbegin(v));', "1", "const のイテレータ", "[`cend`](cend.md)")
RF("cend", "範囲の終端を指す、const のイテレータを返す。", "`ranges::cbegin` と組み合わせて、読むだけの走査の終わりを表します。", "inline constexpr /* カスタマイズポイント */ ranges::cend;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::ranges::cend(v) - std::ranges::cbegin(v));', "3", "const の終端", "[`cbegin`](cbegin.md)")
RF("rbegin", "範囲の逆順の先頭（最後の要素）を指すイテレータを返す。", "後ろから前へ走査したいときに使います。双方向以上の範囲で使えます。", "inline constexpr /* カスタマイズポイント */ ranges::rbegin;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::ranges::rbegin(v));', "3", "逆順のイテレータ", "[`rend`](rend.md)")
RF("rend", "範囲の逆順の終端（先頭の手前）を指すイテレータを返す。", "`ranges::rbegin` と組み合わせて、逆順の走査の終わりを表します。", "inline constexpr /* カスタマイズポイント */ ranges::rend;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::ranges::rend(v) - std::ranges::rbegin(v));', "3", "逆順の終端", "[`rbegin`](rbegin.md)")
RF("crbegin", "範囲の逆順の先頭を指す、const のイテレータを返す。", "後ろから前へ、読むだけで走査したいときに使います。", "inline constexpr /* カスタマイズポイント */ ranges::crbegin;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::ranges::crbegin(v));', "3", "const の逆順のイテレータ", "[`crend`](crend.md)")
RF("crend", "範囲の逆順の終端を指す、const のイテレータを返す。", "`ranges::crbegin` と組み合わせて、逆順の読み取り専用の走査の終わりを表します。", "inline constexpr /* カスタマイズポイント */ ranges::crend;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::ranges::crend(v) - std::ranges::crbegin(v));', "3", "const の逆順の終端", "[`crbegin`](crbegin.md)")
RF("empty", "範囲が空かを調べる。", "`c.empty()` を持たない範囲（配列や、`size` が使えない view）でも、`begin() == end()` で空かどうかを調べてくれます。", "inline constexpr /* カスタマイズポイント */ ranges::empty;", 'std::vector<int> v;\nstd::println("{}", std::ranges::empty(v));', "true", "空なら `true`", "[`size`](size.md)")
RF("data", "範囲の要素が並ぶ先頭へのポインタを返す。", "連続したメモリに要素が並ぶ範囲（`vector`・`array`・`string`・`span`）で、先頭へのポインタを取ります。C の API にバッファを渡すときに使います。", "inline constexpr /* カスタマイズポイント */ ranges::data;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::ranges::data(v));', "1", "要素へのポインタ", "[`cdata`](cdata.md)")
RF("cdata", "範囲の要素が並ぶ先頭への、const のポインタを返す。", "`ranges::data` の const 版です。読み取り専用で C の API に渡すときに使います。", "inline constexpr /* カスタマイズポイント */ ranges::cdata;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", *std::ranges::cdata(v));', "1", "const の要素へのポインタ", "[`data`](data.md)")
RF("ssize", "範囲の要素数を、符号付きの整数で返す。", "`size()` は符号なしなので、`size() - 1` のような計算が桁あふれ（0 のときに大きな値）を起こします。`ranges::ssize(r)` は、符号付きの整数で返すので、この問題を避けられます。", "inline constexpr /* カスタマイズポイント */ ranges::ssize;", 'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::ranges::ssize(v));', "3", "符号付きの要素数", "[`size`](size.md)")

# ---- try_lock / ranlux48
Q("concurrency/try_lock.md", "std::try_lock", "複数のミューテックスを、待たずにまとめてロックしようとする。", "rare", ["mutex", "print"],
  "複数のミューテックスを同時にロックするとき、`std::lock` はロックが取れるまで待ちます。`std::try_lock` は待たず、順にロックを試みて、1 つでも取れなければ、取れたものを全部解除して、取れなかった番号を返します。全部取れたら `-1` です。",
  ["戻り値が `-1` なら、全部ロックできた。", "失敗したら、取れた分は解除される。", "`std::lock` は待つが、`try_lock` は待たない。"], "template <class L1, class L2, class... Ln>\nint try_lock(L1& l1, L2& l2, Ln&... ln);", [("l1, l2, ln...", "ロックできるもの", "ロックを試みるミューテックス")], "全部取れたら `-1`、取れなかったら最初に失敗した番号（0 から）",
  'std::mutex a;\nstd::mutex b;\nint r = std::try_lock(a, b);\nstd::println("{}", r);\nif (r == -1) {\n  a.unlock();\n  b.unlock();\n}', "-1", use="2 つの資源を、取れるときだけ同時に取る", miss=("失敗したときに解除しようとする", "失敗したときは、取れた分は自動で解除されています。もう一度 `unlock` しないようにします。"),
  sim=[("[`lock`](lock.md)", "取れるまで待つ"), ("[`scoped_lock`](scoped_lock.md)", "RAII でまとめてロックする")], cx="ミューテックスの数に比例", ver=("11", "C++11"), info="[並行処理の基本](@/basics/concurrency.md) を先に読んでください。", rj="mutex/try_lock.html", cr="thread/try_lock")
Q("utilities/random/ranlux48.md", "std::ranlux48", "高品質で遅い乱数エンジン（`ranlux48_base` を間引いたもの）。", "rare", ["random", "print"],
  "`ranlux48_base` は速いが品質が低いので、`discard_block_engine` で出力を間引いて品質を上げたものが `ranlux48` です。品質は非常に高い一方、遅く、ゲームの通常の乱数には `mt19937` で足ります。厳密な乱数の品質が必要な科学計算などに向きます。",
  ["48 ビットの乱数を作る。", "`ranlux24` の 48 ビット版。", "ゲームの乱数にはふつう不要。"], "using ranlux48 = discard_block_engine<ranlux48_base, 389, 11>;", [("seed", "整数", "省略可。初期状態を決める値")], "`operator()` で次の乱数を返す",
  'std::ranlux48 e;\ne.discard(9999);\nstd::println("{}", e());  // 10000 回目の値（標準で決まっている）', "249142670597055", use="統計的な品質が重要な計算", miss=("速さを期待する", "非常に遅いエンジンです。通常は `mt19937` を使います。"),
  sim=[("[`ranlux24`](ranlux24.md)", "24 ビット版"), ("[`mt19937`](mt19937.md)", "標準的な高品質エンジン")], cx="1 回あたり重い", ver=("11", "C++11"), info="[`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。", rj="random/ranlux48.html", cr="numeric/random/ranlux48")

if __name__ == "__main__":
    flush_hubs()


