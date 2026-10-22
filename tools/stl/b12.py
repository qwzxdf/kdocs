"""バッチ 12: stacktrace・coroutine・コンテナ周辺・並行処理の未登録分。"""
from mk import *  # noqa: F401,F403

# ================= support（スタックトレース、コルーチン、その他） =================
SU = "support/"
P(SU + "stacktrace_entry.md", "std::stacktrace_entry", "スタックトレースの 1 行（関数 1 つぶん）を表す型。", "rare", "stacktrace",
  "クラッシュ時のログに「どの関数から呼ばれたか」を残したいとき、`std::stacktrace` の 1 行ぶんが `stacktrace_entry` です。関数の説明（`description()`）、ソースのファイル名（`source_file()`）、行番号（`source_line()`）を取り出せます。",
  ["`std::stacktrace` の要素の型。", "`description()` / `source_file()` / `source_line()` で中身を取る。", "デバッグ情報がないと、空の文字列や 0 が返る。"],
  [("クラッシュログに呼び出し元を書く", "`for (const auto& e : std::stacktrace::current()) log << e.description();`")],
  ("リリースビルドで情報を期待する", "デバッグ情報（`-g` など）がないと、関数名やファイル名が取れません。"),
  [("[`stacktrace`](stacktrace.md)", "スタックトレース全体")],
  ["スタックトレースの 1 行", "description / source_file / source_line", "デバッグ情報が必要"],
  sig="class stacktrace_entry {\n public:\n  std::string description() const;\n  std::string source_file() const;\n  uint_least32_t source_line() const;\n  explicit operator bool() const noexcept;\n};", args=[], ret="関数の説明・ファイル名・行番号", cx="情報の取得は重め（シンボルの解決が入る）",
  code="""#include <print>
#include <stacktrace>

int main() {
  auto trace = std::stacktrace::current();
  for (const auto& entry : trace) {
    std::println("{}", entry.description());
  }
}""", out=None, ver=("23", "C++23"), info="[`std::stacktrace`](stacktrace.md) を先に読んでください。", rj="stacktrace/stacktrace_entry.html", cr="utility/stacktrace_entry", compiler="C++23 の機能です。GCC では `-lstdc++exp`（または `-lstdc++_libbacktrace`）が必要です。")
P(SU + "basic_stacktrace.md", "std::basic_stacktrace", "stacktrace の元になる、アロケータを選べるテンプレート。", "rare", "stacktrace",
  "`std::stacktrace` は、`basic_stacktrace<std::allocator<stacktrace_entry>>` の別名です。スタックトレースを保存するときのメモリ確保を自分で管理したい（pmr など）なら、`basic_stacktrace<MyAlloc>` を直接使います。ふつうは別名の `stacktrace` で足ります。",
  ["`stacktrace` = `basic_stacktrace<std::allocator<stacktrace_entry>>`。", "アロケータを差し替えられる。", "ふつうは `stacktrace` を使う。"],
  [("スタックトレースを pmr のメモリに保存する", "`std::basic_stacktrace<std::pmr::polymorphic_allocator<std::stacktrace_entry>>`")],
  ("別名と取り違える", "アロケータを変えない限り、`stacktrace` と書けば十分です。"), [("[`stacktrace`](stacktrace.md)", "別名")],
  ["stacktrace の元のテンプレート", "アロケータを選べる", "ふつうは別名で足りる"],
  sig="template <class Allocator>\nclass basic_stacktrace;\nusing stacktrace = basic_stacktrace<allocator<stacktrace_entry>>;", args=[("Allocator", "型", "要素を保持するアロケータ")], ret="`stacktrace` と同じ関数をもつ", cx="`stacktrace` と同じ",
  code="""#include <memory>
#include <print>
#include <stacktrace>
#include <type_traits>

int main() {
  using Alias = std::basic_stacktrace<std::allocator<std::stacktrace_entry>>;
  std::println("{}", std::is_same_v<Alias, std::stacktrace>);
}""", out="true", ver=("23", "C++23"), info="[`std::stacktrace`](stacktrace.md) を先に読んでください。", rj="stacktrace/basic_stacktrace.html", cr="utility/basic_stacktrace", compiler="C++23 の機能です。")
P(SU + "coroutine/coroutine_traits.md", "std::coroutine_traits", "コルーチンの戻り値の型から、promise_type を取り出す特性。", "rare", "coroutine",
  "コルーチンの戻り値の型（`Task` など）には、コンパイラが探す `promise_type` が必要です。ふつうは `Task::promise_type` を定義すれば足りますが、自分で書けない型（`std::future` など）を戻り値にしたいときは、`coroutine_traits` を特殊化して `promise_type` を外から与えます。",
  ["既定では、戻り値の型の `promise_type` を使う。", "他人の型にコルーチンの性質を足したいときに、特殊化する。", "ふつうの自作コルーチンでは、意識しなくてよい。"],
  [("`std::future` をコルーチンの戻り値にする", "`std::coroutine_traits<std::future<int>, Args...>` を特殊化する")],
  ("`promise_type` を定義し忘れる", "戻り値の型にも特殊化にも `promise_type` がないと、コルーチンとしてコンパイルできません。"), [("[`coroutine_handle`](coroutine_handle.md)", "コルーチンの操作")],
  ["戻り値の型から promise_type を求める", "既定は Task::promise_type", "他人の型には特殊化で足す"],
  sig="template <class R, class... Args>\nstruct coroutine_traits { using promise_type = typename R::promise_type; };", args=[("R", "型", "コルーチンの戻り値の型"), ("Args...", "型", "引数の型")], ret="`promise_type`", cx="コンパイル時のみ",
  code="""#include <coroutine>
#include <print>
#include <type_traits>

struct Task {
  struct promise_type {};
};

int main() {
  std::println("{}", std::is_same_v<std::coroutine_traits<Task>::promise_type, Task::promise_type>);
}""", out="true", ver=("20", "C++20"), info="[`coroutine_handle`](coroutine_handle.md) を先に読んでください。", rj="coroutine/coroutine_traits.html", cr="coroutine/coroutine_traits", group="コルーチン（<coroutine>）")
P(SU + "coroutine/noop_coroutine.md", "std::noop_coroutine", "何もしないコルーチンのハンドルを返す。", "rare", "coroutine",
  "コルーチンが終わるとき、次に実行するコルーチンを返す「対称転送」で、「次はなし」を表したいことがあります。`noop_coroutine()` は、`resume()` しても何も起きないコルーチンのハンドルを返します。",
  ["`resume()` しても何も起こらない。", "`await_suspend` の戻り値として「何もしない」を表すときに使う。", "`done()` は常に `false`。"],
  [("`await_suspend` で次の実行先がないとき", "`return std::noop_coroutine();`")],
  ("`destroy()` を呼ぶ", "ハンドルは共有された 1 つの実体です。`destroy()` を呼んでも意味はありません。"), [("[`coroutine_handle`](coroutine_handle.md)", "コルーチンの操作")],
  ["何もしないコルーチン", "resume しても何も起こらない", "対称転送の「次なし」に使う"],
  sig="noop_coroutine_handle noop_coroutine() noexcept;", args=[], ret="何もしないコルーチンのハンドル", cx="定数",
  code="""#include <coroutine>
#include <print>

int main() {
  std::coroutine_handle<> h = std::noop_coroutine();
  h.resume();
  std::println("{}", h.done());
}""", out="false", ver=("20", "C++20"), info="[`coroutine_handle`](coroutine_handle.md) を先に読んでください。", rj="coroutine/noop_coroutine.html", cr="coroutine/noop_coroutine", group="コルーチン（<coroutine>）")
P(SU + "contract_violation.md", "std::contracts::contract_violation", "契約（事前条件・事後条件）の違反の情報を表す型。", "rare", "contracts",
  "C++26 の契約（`pre`・`post`・`contract_assert`）が破られたとき、違反の内容（どの条件か、どこか）を知らせるのが `contract_violation` です。違反ハンドラ（`handle_contract_violation`）の引数として渡されます。",
  ["違反ハンドラの引数として受け取る。", "`comment()` で条件の文字列、`location()` で場所を取る。", "C++26 の機能。"],
  [("違反をログに出すハンドラ", "`void handle_contract_violation(const std::contracts::contract_violation& v);`")],
  ("自分で作る", "ライブラリが作って渡す型です。自分でインスタンスを作ることはありません。"), [("[`source_location`](source_location.md)", "場所を表す型")],
  ["契約違反の情報", "ハンドラの引数", "C++26"],
  sig="namespace std::contracts {\nclass contract_violation {\n public:\n  const char* comment() const noexcept;\n  std::source_location location() const noexcept;\n  // ...\n};\n}", args=[], ret="違反の条件の文字列・場所など", cx="定数",
  code="""#include <contracts>
#include <print>

// 契約違反のハンドラ（実装がリンク時に探す）
void handle_contract_violation(const std::contracts::contract_violation& v) {
  std::println("契約違反: {}", v.comment());
}""", out=None, ver=("26", "C++26"), info="[`std::source_location`](source_location.md) を先に読んでください。", rj="contracts/contract_violation.html", cr="utility/contract_violation", compiler="C++26 の機能です。対応は新しいコンパイラに限られます。")
P(SU + "text_encoding.md", "std::text_encoding", "文字エンコーディング（UTF-8 など）の名前を表す型。", "rare", "text_encoding",
  "ファイルや端末がどの文字コードかを、文字列ではなく型で扱いたいことがあります。`std::text_encoding` は、IANA 登録の文字エンコーディング（UTF-8、Shift_JIS など）を表す型で、`literal()` でソース上の文字列リテラルのエンコーディング、`environment()` で環境の既定を取れます。",
  ["`text_encoding::literal()` で文字列リテラルの文字コードを取る。", "`name()` で名前、`mib()` で IANA の番号を取る。", "C++26 の機能。"],
  [("実行環境の文字コードに合わせて変換する", "`std::text_encoding::environment()`")],
  ("名前の綴りで比べる", "同じ文字コードでも別名があります。`==` で比べると、別名も同じものと判定されます。"), [("[文字コード](@/encoding/index.md)", "文字コードの考え方")],
  ["文字エンコーディングを表す型", "literal() / environment()", "C++26"],
  sig="class text_encoding {\n public:\n  static text_encoding literal() noexcept;\n  static text_encoding environment();\n  const char* name() const noexcept;\n  id mib() const noexcept;\n};", args=[], ret="エンコーディングの名前など", cx="定数",
  code="""#include <print>
#include <text_encoding>

int main() {
  std::println("{}", std::text_encoding::literal().name());
}""", out=None, ver=("26", "C++26"), info="[文字コード](@/encoding/index.md) の基本を先に読んでください。", rj="text_encoding/text_encoding.html", cr="locale/text_encoding", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")

# ================= containers 周辺 =================
CT = "containers/"
CTI = "[`std::mdspan`](mdspan.md) を先に読んでください。"
P(CT + "dynamic_extent.md", "std::dynamic_extent", "span や mdspan で「要素数が実行時に決まる」ことを表す定数。", "rare", "span",
  "`std::span<int, 3>` は要素数を型で固定し、`std::span<int>` は実行時に決まる要素数を持ちます。後者の「実行時に決まる」ことを表す特別な値が `std::dynamic_extent` です。`span<int>::extent` は、この値と等しくなります。",
  ["`span<T>` の `extent` が、これと等しい。", "値は `size_t` の最大値（`-1`）。", "`mdspan` の `extents` でも、動的な次元を表すのに使う。"],
  [("固定長か動的かをコンパイル時に分岐する", "`if constexpr (S::extent == std::dynamic_extent)`")],
  ("実際の要素数と思う", "`dynamic_extent` は「不定」を表す目印で、要素数そのものではありません。"), [("[`span`](span.md)", "要素数を持つ view")],
  ["要素数が実行時に決まることを表す", "size_t の最大値", "span / mdspan で使う"],
  sig="inline constexpr std::size_t dynamic_extent = std::numeric_limits<std::size_t>::max();", args=[], ret="定数", cx="なし",
  code="""#include <print>
#include <span>

int main() {
  std::println("{}", std::span<int>::extent == std::dynamic_extent);
  std::println("{}", std::span<int, 3>::extent);
}""", out="true\n3", ver=("20", "C++20"), info="[`std::span`](span.md) を先に読んでください。", rj="span/dynamic_extent.html", cr="container/span/dynamic_extent")
P(CT + "dextents.md", "std::dextents", "すべての次元が実行時に決まる extents の別名。", "rare", "mdspan",
  "2 次元の画像のように、縦横の大きさが実行時に決まる `mdspan` を作りたいとき、`extents<size_t, dynamic_extent, dynamic_extent>` と書くのは長いです。`dextents<size_t, 2>` と書けば、同じ型になります。",
  ["`dextents<IndexType, Rank>` = `extents<IndexType, dynamic_extent, ...>`（Rank 個）。", "次元の数だけを指定する。", "`mdspan` のテンプレート引数に使う。"],
  [("実行時にサイズが決まる 2 次元配列", "`std::mdspan<float, std::dextents<std::size_t, 2>>`")],
  ("一部の次元だけ固定したい", "`dextents` はすべて動的です。一部を固定するなら `extents` を直接書きます。"), [("[`extents`](extents.md)", "次元ごとに固定・動的を選ぶ")],
  ["すべて動的な extents の別名", "次元の数を指定する", "mdspan で使う"],
  sig="template <class IndexType, std::size_t Rank>\nusing dextents = /* Rank 個の dynamic_extent を持つ extents */;", args=[("IndexType", "型", "添字の型"), ("Rank", "size_t", "次元の数")], ret="`extents` の型", cx="コンパイル時のみ",
  code="""#include <cstddef>
#include <mdspan>
#include <print>

int main() {
  std::dextents<std::size_t, 2> e(3, 4);
  std::println("{} {}", e.extent(0), e.extent(1));
}""", out="3 4", ver=("23", "C++23"), info=CTI, rj="mdspan/dextents.html", cr="container/mdspan/extents")
P(CT + "default_accessor.md", "std::default_accessor", "mdspan の要素への標準のアクセス方法（ふつうのポインタ）。", "rare", "mdspan",
  "`mdspan` は、要素にアクセスする方法（アクセサ）を差し替えられます。何も指定しなければ、ふつうのポインタで読み書きする `default_accessor` が使われます。",
  ["`mdspan` の第 4 テンプレート引数の既定。", "`access(p, i)` が `p[i]` を返す。", "差し替えるとアトミックなアクセスなどにできる。"],
  [("要素へのアクセスを自作する", "自作のアクセサを `mdspan` の第 4 引数に渡す")],
  ("自分で指定する", "ふつうの用途では指定しません。省略すれば `default_accessor` が使われます。"), [("[`aligned_accessor`](aligned_accessor.md)", "境界を保証するアクセサ")],
  ["mdspan の標準のアクセサ", "p[i] を返す", "ふつうは意識しない"],
  sig="template <class ElementType>\nstruct default_accessor {\n  using reference = ElementType&;\n  constexpr reference access(data_handle_type p, size_t i) const noexcept;\n};", args=[("ElementType", "型", "要素の型")], ret="要素への参照", cx="定数",
  code="""#include <mdspan>
#include <print>

int main() {
  int arr[] = {1, 2, 3};
  std::default_accessor<int> a;
  std::println("{}", a.access(arr, 1));
}""", out="2", ver=("23", "C++23"), info=CTI, rj="mdspan/default_accessor.html", cr="container/mdspan/default_accessor")
P(CT + "aligned_accessor.md", "std::aligned_accessor", "要素が指定した境界に並ぶことを保証する mdspan のアクセサ。", "rare", "mdspan",
  "SIMD で配列を処理するとき、配列の先頭が 16 バイト境界などに揃っていると速くなります。`aligned_accessor<T, N>` は、「この配列は N バイト境界に揃っている」と約束するアクセサで、コンパイラが速いコードを出せるようになります。",
  ["`byte_alignment` に境界のバイト数が入る。", "約束が嘘だと未定義動作。", "[`assume_aligned`](../memory/assume_aligned.md) と同じ考え方。"],
  [("16 バイト境界の配列を SIMD で処理する", "`std::mdspan<float, Ext, std::layout_right, std::aligned_accessor<float, 16>>`")],
  ("境界が合っていない配列を渡す", "約束が守られないと未定義動作です。`alignas` で確保した配列だけに使います。"), [("[`default_accessor`](default_accessor.md)", "標準のアクセサ"), ("[`assume_aligned`](../memory/assume_aligned.md)", "ポインタに境界を約束する")],
  ["境界を保証するアクセサ", "byte_alignment", "嘘は未定義動作"],
  sig="template <class ElementType, std::size_t ByteAlignment>\nstruct aligned_accessor {\n  static constexpr std::size_t byte_alignment = ByteAlignment;\n};", args=[("ElementType", "型", "要素の型"), ("ByteAlignment", "size_t", "境界のバイト数（2 のべき乗）")], ret="`byte_alignment` に境界が入る", cx="定数",
  code="""#include <mdspan>
#include <print>

int main() {
  std::println("{}", std::aligned_accessor<float, 16>::byte_alignment);
}""", out="16", ver=("26", "C++26"), info=CTI, rj="mdspan/aligned_accessor.html", cr="container/mdspan/aligned_accessor", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")
P(CT + "full_extent.md", "std::full_extent", "submdspan で「この次元は全部」を表す目印。", "rare", "mdspan",
  "`mdspan` の一部だけを取り出す `submdspan(m, 行, 列)` で、「この次元は全部ほしい」を表したいことがあります。それが `std::full_extent` です。行を 1 つ指定して、列は全部、のような使い方をします。",
  ["`submdspan` の引数として使う。", "スライスの「全部」を表す。", "数値（1 つの添字）や範囲（`pair`）と同じ位置に書く。"],
  [("画像の 1 行だけを取り出す", "`std::submdspan(img, 3, std::full_extent)`")],
  ("次元の数を間違える", "`submdspan` に渡すスライスは、次元の数と同じだけ必要です。"), [("[`submdspan`](submdspan.md)", "一部を取り出す"), ("[`strided_slice`](strided_slice.md)", "間隔つきの範囲")],
  ["「全部」を表す目印", "submdspan の引数", "C++26"],
  sig="struct full_extent_t { explicit full_extent_t() = default; };\ninline constexpr full_extent_t full_extent{};", args=[], ret="なし（目印）", cx="なし",
  code="""#include <mdspan>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::remove_const_t<decltype(std::full_extent)>, std::full_extent_t>);
}""", out="true", ver=("26", "C++26"), info=CTI, rj="mdspan/full_extent_t.html", cr="container/mdspan/full_extent_t", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")
P(CT + "strided_slice.md", "std::strided_slice", "submdspan で「開始位置・長さ・間隔」を指定する範囲。", "rare", "mdspan",
  "`mdspan` の一部を、1 つおきに取り出したいことがあります（偶数番目の列だけ、など）。`strided_slice{offset, extent, stride}` は、開始位置・長さ・間隔を指定する範囲で、`submdspan` に渡します。",
  ["`offset`・`extent`・`stride` の 3 つのメンバ。", "`stride` が 2 なら 1 つおき。", "C++26 の機能。"],
  [("画像の列を 1 つおきに取り出す", "`std::strided_slice{.offset = 0, .extent = 6, .stride = 2}`")],
  ("`extent` を終端位置と思う", "`extent` は取り出す範囲の「長さ」です。終端の位置ではありません。"), [("[`submdspan`](submdspan.md)", "一部を取り出す"), ("[`full_extent`](full_extent.md)", "全部")],
  ["開始・長さ・間隔の範囲", "submdspan の引数", "C++26"],
  sig="template <class OffsetType, class ExtentType, class StrideType>\nstruct strided_slice {\n  OffsetType offset;\n  ExtentType extent;\n  StrideType stride;\n};", args=[("offset", "整数", "開始位置"), ("extent", "整数", "範囲の長さ"), ("stride", "整数", "間隔")], ret="なし（範囲の指定）", cx="なし",
  code="""#include <mdspan>
#include <print>

int main() {
  std::strided_slice s{.offset = 0, .extent = 6, .stride = 2};
  std::println("{} {} {}", s.offset, s.extent, s.stride);
}""", out="0 6 2", ver=("26", "C++26"), info=CTI, rj="mdspan/strided_slice.html", cr="container/mdspan/strided_slice", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")
P(CT + "submdspan.md", "std::submdspan", "mdspan の一部（行・列・範囲）を取り出して、新しい mdspan にする。", "rare", "mdspan",
  "画像の 1 行だけ、2 次元配列の一部の矩形だけを処理したいとき、元のデータをコピーせずに、その部分を指す `mdspan` を作れるのが `submdspan` です。行や列を 1 つ指定したり、範囲を指定したり、`full_extent` で全部を指定したりします。",
  ["次元の数と同じだけのスライスを渡す。", "1 つの添字を渡すと、その次元は消える（次元が 1 つ減る）。", "コピーはしない（元の配列を指す）。"],
  [("画像の 1 行を取り出して処理", "`auto row = std::submdspan(img, y, std::full_extent);`")],
  ("元の配列が先に消える", "`submdspan` は元のデータを指すだけです。元のデータが生きている間だけ使えます。"), [("[`full_extent`](full_extent.md)", "全部を表す"), ("[`strided_slice`](strided_slice.md)", "間隔つきの範囲")],
  ["mdspan の一部を取り出す", "コピーしない", "C++26"],
  sig="template <class T, class Extents, class Layout, class Accessor, class... Slices>\nconstexpr auto submdspan(const mdspan<T, Extents, Layout, Accessor>& src, Slices... slices);", args=[("src", "mdspan", "元の mdspan"), ("slices...", "スライス", "各次元の指定（整数・範囲・`full_extent`）")], ret="一部を指す新しい `mdspan`", cx="定数",
  code="""#include <mdspan>
#include <print>

int main() {
  int data[] = {1, 2, 3, 4, 5, 6};
  std::mdspan m(data, 2, 3);
  auto row = std::submdspan(m, 1, std::full_extent);
  std::println("{} {} {}", row[0], row[1], row[2]);
}""", out="4 5 6", ver=("26", "C++26"), info=CTI, rj="mdspan/submdspan.html", cr="container/mdspan/submdspan", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")

VA = "[`std::valarray`](valarray.md) を先に読んでください。"
for nm, sig_, what, intro, body, out, miss in [
    ("slice", "class slice {\n public:\n  slice(std::size_t start, std::size_t size, std::size_t stride);\n};", "valarray から、開始位置・個数・間隔で要素を選ぶ。", "`valarray` の中から、1 つおき、あるいは行列の列のように、一定の間隔の要素を選びたいことがあります。`slice(start, size, stride)` で選び方を指定して、`v[slice]` と書きます。",
     'std::valarray<int> v = {1, 2, 3, 4, 5, 6};\nstd::valarray<int> s = v[std::slice(1, 3, 2)];\nstd::println("{} {} {}", s[0], s[1], s[2]);', "2 4 6", ("結果が元を指すと思う", "`v[slice]` を `valarray` に代入すると、コピーされます。")),
    ("gslice", "class gslice {\n public:\n  gslice(std::size_t start, const std::valarray<std::size_t>& sizes, const std::valarray<std::size_t>& strides);\n};", "valarray から、多次元の添字（開始位置・各次元の個数・各次元の間隔）で要素を選ぶ。", "`slice` は 1 次元の選び方です。行列の一部の矩形のように、多次元の選び方は `gslice(start, sizes, strides)` で指定します。",
     'std::valarray<int> v(16);\nfor (int i = 0; i < 16; ++i) v[i] = i;\nstd::valarray<std::size_t> sizes = {2, 2};\nstd::valarray<std::size_t> strides = {4, 1};\nstd::valarray<int> s = v[std::gslice(0, sizes, strides)];\nstd::println("{} {} {} {}", s[0], s[1], s[2], s[3]);', "0 1 4 5", ("次元の数が合わない", "`sizes` と `strides` は、同じ長さ（次元の数）にします。")),
    ("mask_array", "template <class T>\nclass mask_array;  // v[mask] が返す型", "valarray から、bool の配列（マスク）で選んだ要素への参照。", "`v[mask]`（`mask` は `valarray<bool>`）と書くと、`true` の位置の要素だけを選べます。その結果の型が `mask_array` です。代入すると、元の `valarray` の対応する要素が書き換わります。",
     'std::valarray<int> v = {1, 2, 3, 4};\nstd::valarray<bool> mask = {true, false, true, false};\nv[mask] = 0;\nstd::println("{} {} {} {}", v[0], v[1], v[2], v[3]);', "0 2 0 4", ("マスクの長さが違う", "`mask` は `v` と同じ長さにします。")),
    ("indirect_array", "template <class T>\nclass indirect_array;  // v[indices] が返す型", "valarray から、添字の配列で選んだ要素への参照。", "`v[indices]`（`indices` は `valarray<size_t>`）と書くと、指定した添字の要素を選べます。その結果の型が `indirect_array` です。代入すると、元の `valarray` の対応する要素が書き換わります。",
     'std::valarray<int> v = {1, 2, 3, 4};\nstd::valarray<std::size_t> idx = {3, 0};\nv[idx] = 9;\nstd::println("{} {} {} {}", v[0], v[1], v[2], v[3]);', "9 2 3 9", ("範囲外の添字", "範囲外の添字は未定義動作です。")),
]:
    P(CT + nm + ".md", "std::" + nm, what, "rare", "valarray", intro,
      ["`valarray` の部分選択に使う。", "`v[選び方]` の形で書く。", "ゲームではほとんど使わない（`span` や `mdspan` のほうが一般的）。"],
      [("配列の一部を一括で書き換える", f"`v[std::{nm}(...)] = x;`")], miss, [("[`valarray`](valarray.md)", "数値計算用の配列")],
      [what.rstrip("。"), "`v[...]` の形で使う", "valarray 専用"],
      sig=sig_, args=[], ret="選んだ要素", cx="選んだ要素の数に比例", code="#include <print>\n#include <valarray>\n\nint main() {\n" + "\n".join("  " + l for l in body.split("\n")) + "\n}", out=out, info=VA, rj=f"valarray/{nm}.html", cr=f"numeric/valarray/{nm}")
P(CT + "hive.md", "std::hive", "要素を挿入・削除しても、他の要素の位置が変わらない順序なしコンテナ。", "rare", "hive",
  "ゲームのエンティティのように、頻繁に追加・削除され、削除しても他の要素へのポインタが無効にならないでほしいコンテナがあります。`std::hive` は、要素を複数のブロックに分けて持ち、**削除された場所を再利用する**ことで、ポインタを安定させつつ、挿入・削除を速くします。順序は保証されません。",
  ["要素へのポインタ・イテレータが、挿入・削除で無効にならない（削除した要素自身は除く）。", "順序は保証されない（隙間を再利用するため）。", "C++26 の機能。`plf::colony` が元になった。"],
  [("敵やパーティクルの管理", "`std::hive<Enemy>` に追加し、倒したら `erase`")],
  ("順序を期待する", "挿入した順に並ぶとは限りません。順序が必要なら `vector` を使います。"), [("[`vector`](vector.md)", "連続した順序つきの配列"), ("[`list`](list.md)", "ポインタは安定だがキャッシュに弱い")],
  ["位置が安定する順序なしコンテナ", "削除した場所を再利用する", "C++26"],
  sig="template <class T, class Allocator = allocator<T>>\nclass hive;", args=[("T", "型", "要素の型")], ret="`insert`・`erase`・イテレータなどをもつ", cx="挿入・削除は 償却定数",
  code="""#include <hive>
#include <print>

int main() {
  std::hive<int> h = {1, 2, 3};
  h.insert(4);
  std::println("{}", h.size());
}""", out="4", ver=("26", "C++26"), info="[`std::vector`](vector.md) を先に読んでください。", rj="hive/hive.html", cr="container/hive", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます（`plf::hive` が使える）。")
P(CT + "to_array.md", "std::to_array", "配列リテラルや C の配列から、std::array を作る。", "sometimes", "array",
  "`std::array<int, 3> a = {1, 2, 3};` と書くと、要素数 `3` を自分で書く必要があります。`std::to_array({1, 2, 3})` なら、要素数を数えて `std::array<int, 3>` を作ってくれます。C の配列や文字列リテラルからも作れます。",
  ["要素数を数えなくてよい（推論される）。", "文字列リテラルからは、終端の `'\\0'` も含む `array<char, N>` になる。", "C 配列からのコピーやムーブもできる。"],
  [("定数の表を `std::array` にする", "`constexpr auto table = std::to_array({1, 2, 3});`")],
  ("型が混ざった初期化子を渡す", "`{1, 2.5}` のように型が混ざると、型が決まらずコンパイルエラーです。型をそろえるか、要素の型を指定します（`std::to_array<double>({1, 2.5})`）。"), [("[`array`](array.md)", "固定長配列")],
  ["要素数を推論して std::array を作る", "文字列リテラルは終端も含む", "型は 1 つにそろえる"],
  sig="template <class T, std::size_t N>\nconstexpr std::array<std::remove_cv_t<T>, N> to_array(T (&a)[N]);\ntemplate <class T, std::size_t N>\nconstexpr std::array<std::remove_cv_t<T>, N> to_array(T (&&a)[N]);", args=[("a", "配列", "元の配列（C の配列、または `{...}` の初期化子）")], ret="`std::array<T, N>`", cx="O(N)",
  code="""#include <array>
#include <print>

int main() {
  auto a = std::to_array({1, 2, 3});
  auto s = std::to_array("ab");
  std::println("{} {}", a.size(), s.size());
}""", out="3 3", ver=("20", "C++20"), info="[`std::array`](array.md) を先に読んでください。", rj="array/to_array.html", cr="container/array/to_array")

# ================= 並行処理 =================
CO = "concurrency/"
COI = "[並行処理の基本](@/basics/concurrency.md) を先に読んでください。"
P(CO + "recursive_timed_mutex.md", "std::recursive_timed_mutex", "同じスレッドで何度でもロックでき、時間切れも指定できるミューテックス。", "rare", "mutex",
  "`recursive_mutex`（同じスレッドが何度でもロックできる）と、`timed_mutex`（ロックの待ち時間を指定できる）を、両方使えるようにしたものです。再帰的に呼ばれる関数の中でロックが必要で、かつ時間切れも指定したいという、まれな場面で使います。",
  ["同じスレッドが何度でも `lock()` できる（解除も同じ回数）。", "`try_lock_for`・`try_lock_until` で待ち時間を指定できる。", "ふつうは設計を見直して、必要としない形にする。"],
  [("再帰呼び出しの中で時間つきでロックする", "`if (m.try_lock_for(10ms)) { ... m.unlock(); }`")],
  ("ロックと同じ回数だけ解除しない", "`lock()` を 2 回したら、`unlock()` も 2 回必要です。"), [("[`recursive_mutex`](recursive_mutex.md)", "時間指定なし"), ("[`timed_mutex`](timed_mutex.md)", "再帰なし")],
  ["再帰ロック + 時間切れのミューテックス", "ロックした回数だけ解除する", "ふつうは別の設計にする"],
  sig="class recursive_timed_mutex {\n public:\n  void lock();\n  bool try_lock();\n  template <class Rep, class Period> bool try_lock_for(const std::chrono::duration<Rep, Period>& d);\n  template <class Clock, class Duration> bool try_lock_until(const std::chrono::time_point<Clock, Duration>& t);\n  void unlock();\n};", args=[], ret="`try_lock_for` / `try_lock_until` はロックできたら `true`", cx="OS に依存",
  code="""#include <chrono>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;
  std::recursive_timed_mutex m;
  m.lock();
  m.lock();  // 同じスレッドなので、もう一度ロックできる
  m.unlock();
  m.unlock();
  std::println("{}", m.try_lock_for(10ms));
  m.unlock();
}""", out="true", ver=("11", "C++11"), info=COI, rj="mutex/recursive_timed_mutex.html", cr="thread/recursive_timed_mutex")
P(CO + "shared_timed_mutex.md", "std::shared_timed_mutex", "読み取りは同時に、書き込みは 1 つだけで、時間切れも指定できるミューテックス。", "rare", "shared_mutex",
  "`shared_mutex`（複数のスレッドが同時に読めるロック）に、ロックの待ち時間を指定する機能を足したものです。C++14 で登場しましたが、C++17 の `shared_mutex` のほうが軽いので、時間指定が必要なときだけ使います。",
  ["`lock_shared()` で読み取りロック、`lock()` で書き込みロック。", "`try_lock_for` / `try_lock_shared_for` で待ち時間を指定する。", "時間指定が不要なら [`shared_mutex`](shared_mutex.md)。"],
  [("読み取りが多く、時間切れも必要な設定データ", "`std::shared_lock lk(m, 10ms);`")],
  ("読み取りロックで書き込む", "`lock_shared()` で取ったロックの間は、データを書き換えてはいけません。"), [("[`shared_mutex`](shared_mutex.md)", "時間指定なし")],
  ["読み書きロック + 時間切れ", "shared が読み取り", "時間指定が不要なら shared_mutex"],
  sig="class shared_timed_mutex {\n public:\n  void lock();\n  void lock_shared();\n  template <class Rep, class Period> bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& d);\n  void unlock();\n  void unlock_shared();\n};", args=[], ret="`try_lock_*_for` はロックできたら `true`", cx="OS に依存",
  code="""#include <chrono>
#include <print>
#include <shared_mutex>

int main() {
  using namespace std::chrono_literals;
  std::shared_timed_mutex m;
  m.lock_shared();
  std::println("{}", m.try_lock_shared_for(10ms));  // 読み取りは同時にできる
  m.unlock_shared();
  m.unlock_shared();
}""", out="true", ver=("14", "C++14"), info=COI, rj="shared_mutex/shared_timed_mutex.html", cr="thread/shared_timed_mutex")
P(CO + "once_flag.md", "std::once_flag", "call_once で「1 回だけ実行」を管理するための旗。", "sometimes", "mutex",
  "初期化処理を「最初に必要になったときに 1 回だけ」行いたいとき、複数のスレッドが同時に来ても 1 回だけ実行されるようにするには、`once_flag` と `call_once` を組み合わせます。`once_flag` は、「もう実行したか」を覚えておく旗です。",
  ["`std::call_once(flag, 関数)` に渡して使う。", "コピー・ムーブできない。", "スレッドセーフな遅延初期化に使う。"],
  [("最初に使うときだけ設定ファイルを読む", "`std::call_once(flag, LoadConfig);`")],
  ("旗を毎回新しく作る", "`once_flag` を関数の中のローカル変数にすると、毎回新しい旗になり、毎回実行されます。`static` かメンバにします。"), [("[`call_once`](call_once.md)", "1 回だけ実行する")],
  ["「1 回だけ」の旗", "call_once と組み合わせる", "static かメンバにする"],
  sig="struct once_flag {\n  constexpr once_flag() noexcept;\n  once_flag(const once_flag&) = delete;\n  once_flag& operator=(const once_flag&) = delete;\n};", args=[], ret="なし（旗）", cx="定数",
  code="""#include <mutex>
#include <print>

int main() {
  std::once_flag flag;
  for (int i = 0; i < 3; ++i) {
    std::call_once(flag, [] { std::println("once"); });
  }
}""", out="once", ver=("11", "C++11"), info=COI, rj="mutex/once_flag.html", cr="thread/once_flag")
for nm, what, intro, body, out in [
    ("defer_lock", "unique_lock に「まだロックしない」と伝える目印。", "`unique_lock` は、作った時点でミューテックスをロックします。あとでまとめて（デッドロックを避けて）ロックしたいときは、`std::defer_lock` を渡して「ロックは後で」と伝えます。", 'std::mutex m;\nstd::unique_lock lk(m, std::defer_lock);\nstd::println("{}", lk.owns_lock());', "false"),
    ("try_to_lock", "unique_lock に「ロックを試すだけ。取れなければ待たない」と伝える目印。", "ロックが取れないときに待ち続けたくない場合、`std::try_to_lock` を渡すと、取れたかどうかを `owns_lock()` で確かめられます。", 'std::mutex m;\nstd::unique_lock lk(m, std::try_to_lock);\nstd::println("{}", lk.owns_lock());', "true"),
    ("adopt_lock", "「すでにロック済みのミューテックスを引き取る」と伝える目印。", "すでに自分でロックしたミューテックスを、`lock_guard` や `unique_lock` に引き取らせて、スコープを抜けるときに解除させたいときに、`std::adopt_lock` を渡します。`std::lock` で複数を同時にロックしたあとに使います。", 'std::mutex m;\nm.lock();\n{\n  std::lock_guard g(m, std::adopt_lock);\n  std::println("adopted");\n}', "adopted")]:
    P(CO + nm + ".md", "std::" + nm, what, "rare", "mutex", intro,
      ["`std::" + nm + "_t` 型の定数。", "`lock_guard`・`unique_lock`・`scoped_lock` のコンストラクタの第 2 引数に渡す。", "デッドロックを避ける `std::lock` と組み合わせて使う。"],
      [("複数のミューテックスを同時にロック", "`std::lock(m1, m2);` のあと `std::lock_guard g1(m1, std::adopt_lock);`")],
      ("目印とロックの状態が食い違う", "`adopt_lock` は、すでにロックしていることが前提です。ロックしていないと未定義動作です。" if nm == "adopt_lock" else "`owns_lock()` で、実際にロックを持っているかを確かめてから使います。"),
      [("[`unique_lock`](unique_lock.md)", "柔軟なロック"), ("[`lock_guard`](lock_guard.md)", "単純なロック"), ("[`std::lock`](lock.md)", "複数を同時にロック")],
      [what.rstrip("。"), "ロックの方法を指定する目印", "std::lock と組み合わせる"],
      sig=f"struct {nm}_t {{ explicit {nm}_t() = default; }};\ninline constexpr {nm}_t {nm}{{}};", args=[], ret="なし（目印）", cx="なし",
      code="#include <mutex>\n#include <print>\n\nint main() {\n" + "\n".join("  " + l for l in body.split("\n")) + "\n}", out=out, ver=("11", "C++11"), info=COI, rj="mutex/defer_lock.html", cr="thread/lock_tag")
P(CO + "notify_all_at_thread_exit.md", "std::notify_all_at_thread_exit", "スレッドが完全に終わった（後始末も済んだ）あとで、条件変数に通知する。", "rare", "condition_variable",
  "スレッドの終了時に `notify_all()` を呼ぶと、待っているスレッドが、まだ終わっていないスレッドのローカル変数を見てしまう危険があります。`notify_all_at_thread_exit(cv, lock)` なら、スレッドのローカル変数の後始末が全部済んでから通知されるので安全です。",
  ["第 2 引数に、すでに取っているロックを渡す。", "スレッドが終わるときに、ロックを解除して通知する。", "`thread_local` の変数が破棄されたあとに通知される。"],
  [("スレッドの終了と結果を同時に知らせる", "`std::notify_all_at_thread_exit(cv, std::move(lk));`")],
  ("ロックを取らずに呼ぶ", "ロックを取った `unique_lock` を渡す必要があります。"), [("[`condition_variable`](condition_variable.md)", "条件変数")],
  ["スレッド終了後に通知する", "ロックを渡す", "ローカル変数の後始末のあとで通知される"],
  sig="void notify_all_at_thread_exit(condition_variable& cond, unique_lock<mutex> lk);", args=[("cond", "condition_variable&", "通知する条件変数"), ("lk", "unique_lock<mutex>", "取得済みのロック（ムーブで渡す）")], ret="なし", cx="定数",
  code="""#include <condition_variable>
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex m;
  std::condition_variable cv;
  bool done = false;
  std::thread t([&] {
    std::unique_lock lk(m);
    done = true;
    std::notify_all_at_thread_exit(cv, std::move(lk));
  });
  {
    std::unique_lock lk(m);
    cv.wait(lk, [&] { return done; });
  }
  t.join();
  std::println("done");
}""", out="done", ver=("11", "C++11"), info=COI, rj="condition_variable/notify_all_at_thread_exit.html", cr="thread/notify_all_at_thread_exit")
P(CO + "cv_status.md", "std::cv_status", "条件変数の待機が、通知で終わったか、時間切れで終わったかを表す列挙型。", "rare", "condition_variable",
  "`cv.wait_for(lk, 時間)` は、通知を受けて起きた場合と、時間切れで起きた場合のどちらもあります。どちらだったかを `cv_status::no_timeout`（通知）か `cv_status::timeout`（時間切れ）で返します。述語つきの版は `bool` を返します。",
  ["`wait_for` / `wait_until` の戻り値（述語なしの版）。", "`timeout` と `no_timeout` の 2 つ。", "偽の起床（spurious wakeup）で `no_timeout` が返ることがある。"],
  [("通知を待つが、一定時間でなだめる", "`if (cv.wait_for(lk, 100ms) == std::cv_status::timeout) { ... }`")],
  ("`no_timeout` なら条件が成立したと思う", "偽の起床でも `no_timeout` が返ります。条件は述語で確かめます。"), [("[`condition_variable`](condition_variable.md)", "条件変数")],
  ["待機の結果を表す列挙型", "timeout / no_timeout", "偽の起床に注意"],
  sig="enum class cv_status { no_timeout, timeout };", args=[], ret="なし（列挙型）", cx="なし",
  code="""#include <chrono>
#include <condition_variable>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;
  std::mutex m;
  std::condition_variable cv;
  std::unique_lock lk(m);
  std::println("{}", cv.wait_for(lk, 10ms) == std::cv_status::timeout);
}""", out="true", ver=("11", "C++11"), info=COI, rj="condition_variable/cv_status.html", cr="thread/cv_status")
P(CO + "launch.md", "std::launch", "async の実行方法（別スレッドか、遅延か）を選ぶ列挙型。", "sometimes", "future",
  "`std::async` で関数を実行するとき、別スレッドで動かすのか、`get()` を呼ぶまで遅らせるのかを選べます。それを指定するのが `std::launch::async`（別スレッド）と `std::launch::deferred`（遅延）です。省略すると、どちらかを実装が選びます。",
  ["`std::launch::async`: すぐ別スレッドで始める。", "`std::launch::deferred`: `get()` / `wait()` のときに、呼んだスレッドで実行する。", "省略すると実装が選ぶので、意図を持つなら明示する。"],
  [("重い処理を確実に別スレッドで動かす", "`std::async(std::launch::async, f);`")],
  ("省略して別スレッドだと思う", "省略すると `deferred` になる可能性があります。並列にしたいなら `launch::async` を明示します。"), [("[`async`](async.md)", "非同期実行"), ("[`future`](future.md)", "結果を受け取る")],
  ["async の実行方法を選ぶ", "async は別スレッド、deferred は遅延", "省略は実装任せ"],
  sig="enum class launch : /* 実装定義 */ { async = 1, deferred = 2 };", args=[], ret="なし（列挙型）", cx="なし",
  code="""#include <future>
#include <print>
#include <thread>

int main() {
  auto f = std::async(std::launch::deferred, [] { return std::this_thread::get_id(); });
  std::println("{}", f.get() == std::this_thread::get_id());  // 呼んだスレッドで実行される
}""", out="true", ver=("11", "C++11"), info=COI, rj="future/launch.html", cr="thread/launch")
P(CO + "future_status.md", "std::future_status", "future の待機の結果（準備完了・時間切れ・遅延）を表す列挙型。", "rare", "future",
  "`future::wait_for(時間)` は、結果が準備できた、時間切れ、まだ始まっていない（遅延）のどれかを `future_status` で返します。結果が出たかをポーリングしたいときに使います。",
  ["`ready`: 結果が出た。", "`timeout`: 時間切れ。", "`deferred`: `launch::deferred` で、まだ実行されていない。"],
  [("ロード中を、別の画面表示でつなぐ", "`if (f.wait_for(0s) == std::future_status::ready) { ... }`")],
  ("`deferred` を忘れる", "`launch::deferred` の `future` は、`wait_for` が常に `deferred` を返します。`get()` するまで動きません。"), [("[`future`](future.md)", "結果を受け取る"), ("[`launch`](launch.md)", "実行方法")],
  ["future の待機の結果", "ready / timeout / deferred", "0 秒で wait_for するとポーリング"],
  sig="enum class future_status { ready, timeout, deferred };", args=[], ret="なし（列挙型）", cx="なし",
  code="""#include <chrono>
#include <future>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto f = std::async(std::launch::deferred, [] { return 1; });
  std::println("{}", f.wait_for(0s) == std::future_status::deferred);
}""", out="true", ver=("11", "C++11"), info=COI, rj="future/future_status.html", cr="thread/future_status")
P(CO + "future_error.md", "std::future_error", "future / promise の使い方を間違えたときの例外。", "rare", "future",
  "`promise` から `get_future()` を 2 回呼ぶ、`promise` を使わずに壊す、などの使い方のミスがあると、`future_error` が投げられます。`code()` で原因を `future_errc` として取り出せます。",
  ["`std::logic_error` から派生。", "`code()` で原因（`future_errc`）を取る。", "プログラムのミスを表す例外。"],
  [("`promise` の二重取得を検出", "`catch (const std::future_error& e) { e.code() == std::future_errc::future_already_retrieved }`")],
  ("通常のエラーとして扱う", "プログラムのミスを表す例外です。入力のエラーとして扱うものではありません。"), [("[`future_errc`](future_errc.md)", "原因の列挙型"), ("[`promise`](promise.md)", "値を渡す側")],
  ["future / promise のミスを表す例外", "code() で原因を取る", "future_errc"],
  sig="class future_error : public logic_error {\n public:\n  const error_code& code() const noexcept;\n};", args=[], ret="`code()` が原因の `error_code`", cx="なし",
  code="""#include <future>
#include <print>

int main() {
  std::promise<int> p;
  p.get_future();
  try {
    p.get_future();
  } catch (const std::future_error& e) {
    std::println("{}", e.code() == std::future_errc::future_already_retrieved);
  }
}""", out="true", ver=("11", "C++11"), info=COI, rj="future/future_error.html", cr="thread/future_error")
P(CO + "future_errc.md", "std::future_errc", "future_error の原因を表す列挙型。", "rare", "future",
  "`future_error` がなぜ投げられたかを、`future_errc` の値で区別できます。`broken_promise`（約束が果たされなかった）、`future_already_retrieved`（`get_future` の二重呼び出し）、`promise_already_satisfied`（値を二重に設定）、`no_state`（状態がない）の 4 つです。",
  ["`broken_promise`: `promise` が値を設定する前に破棄された。", "`future_already_retrieved`: `get_future()` を 2 回呼んだ。", "`promise_already_satisfied`: 値を 2 回設定した。 `no_state`: 状態を持たない `future` を使った。"],
  [("エラーの原因ごとに処理を分ける", "`switch (e.code().value()) { ... }` ではなく `e.code() == std::future_errc::...` で比べる")],
  ("`value()` を直接比べる", "数値は実装依存です。`future_errc` との比較（`==`）を使います。"), [("[`future_error`](future_error.md)", "例外クラス")],
  ["future_error の原因", "4 つの値", "== で比べる"],
  sig="enum class future_errc {\n  broken_promise = /* 実装定義 */,\n  future_already_retrieved,\n  promise_already_satisfied,\n  no_state\n};", args=[], ret="なし（列挙型）", cx="なし",
  code="""#include <future>
#include <print>

int main() {
  std::future<int> f;  // 状態を持たない
  try {
    f.get();
  } catch (const std::future_error& e) {
    std::println("{}", e.code() == std::future_errc::no_state);
  }
}""", out="true", ver=("11", "C++11"), info=COI, rj="future/future_errc.html", cr="thread/future_errc")

# ---- atomic の自由関数
AT = "concurrency/"
ATI = "[`std::atomic`](atomic.md) を先に読んでください。"


def A(name, summary, intro, sig, args, ret, body, out, use, miss, sim, ver=None, inc=("atomic", "print"), cr=None):
    Q(AT + name + ".md", "std::" + name, summary, "rare", list(inc), intro, ["`std::atomic` のメンバ関数と同じ働きの、自由関数版。", "ふつうはメンバ関数のほうが読みやすい。", "C 言語との互換のためにある。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx="定数（アトミック命令）", ver=ver, info=ATI, rj=f"atomic/{name}.html", cr=f"atomic/{cr or name}")


A("atomic_fetch_add", "アトミックに加算し、加算前の値を返す。", "`a.fetch_add(n)` の自由関数版です。複数のスレッドから同時に加算しても、更新が失われません。", "template <class T>\nT atomic_fetch_add(std::atomic<T>* obj, T arg) noexcept;", [("obj", "atomic<T>*", "対象"), ("arg", "T", "足す値")], "加算前の値",
  'std::atomic<int> a{1};\nint old = std::atomic_fetch_add(&a, 2);\nstd::println("{} {}", old, a.load());', "1 3", "スレッド間で共有するカウンタを増やす", ("`a += 2` との違いを気にしない", "`a += 2` も同じ意味ですが、戻り値（加算前）が欲しいときだけ `fetch_add` です。"), [("[`atomic_fetch_sub`](atomic_fetch_sub.md)", "減算")])
A("atomic_fetch_sub", "アトミックに減算し、減算前の値を返す。", "`a.fetch_sub(n)` の自由関数版です。参照カウントを減らして、0 になったかを調べるときなどに使います。", "template <class T>\nT atomic_fetch_sub(std::atomic<T>* obj, T arg) noexcept;", [("obj", "atomic<T>*", "対象"), ("arg", "T", "引く値")], "減算前の値",
  'std::atomic<int> a{3};\nint old = std::atomic_fetch_sub(&a, 2);\nstd::println("{} {}", old, a.load());', "3 1", "参照カウントを減らす", ("戻り値を減算後と思う", "戻り値は減算**前**の値です。"), [("[`atomic_fetch_add`](atomic_fetch_add.md)", "加算")])
A("atomic_load_explicit", "メモリ順序を指定して、アトミックに値を読む。", "`a.load(order)` の自由関数版です。同期が必要な最小限の順序（`acquire` や `relaxed`）を指定して、速度を稼ぎます。", "template <class T>\nT atomic_load_explicit(const std::atomic<T>* obj, std::memory_order order) noexcept;", [("obj", "const atomic<T>*", "対象"), ("order", "memory_order", "メモリ順序")], "読んだ値",
  'std::atomic<int> a{5};\nstd::println("{}", std::atomic_load_explicit(&a, std::memory_order_relaxed));', "5", "フラグを軽く読む", ("順序を弱めすぎる", "他のデータの可視性が必要なら `acquire` を使います。"), [("[`atomic_store_explicit`](atomic_store_explicit.md)", "書く"), ("[`memory_order`](memory_order.md)", "順序")])
A("atomic_store_explicit", "メモリ順序を指定して、アトミックに値を書く。", "`a.store(x, order)` の自由関数版です。`release` で書くと、それより前の書き込みが、読む側から見えるようになります。", "template <class T>\nvoid atomic_store_explicit(std::atomic<T>* obj, T desired, std::memory_order order) noexcept;", [("obj", "atomic<T>*", "対象"), ("desired", "T", "書く値"), ("order", "memory_order", "メモリ順序")], "なし",
  'std::atomic<int> a{0};\nstd::atomic_store_explicit(&a, 5, std::memory_order_release);\nstd::println("{}", a.load());', "5", "完了フラグを立てる", ("`acquire` を指定する", "書き込みに `acquire` は使えません（`release` / `seq_cst` / `relaxed`）。"), [("[`atomic_load_explicit`](atomic_load_explicit.md)", "読む")])
A("atomic_init", "atomic を初期化する（まだ他のスレッドが触っていないとき）。", "古い C++ では、`atomic<T>` の既定構築が初期化しないことがあり、`atomic_init` で初期化する必要がありました。C++20 以降は、既定構築で値初期化されるので、不要になり、非推奨です。", "template <class T>\nvoid atomic_init(std::atomic<T>* obj, T desired) noexcept;", [("obj", "atomic<T>*", "対象"), ("desired", "T", "初期値")], "なし",
  'std::atomic<int> a;\nstd::atomic_init(&a, 7);\nstd::println("{}", a.load());', "7", "古いコードの保守", ("新しいコードで使う", "C++20 以降は非推奨です。コンストラクタで初期化します。"), [("[`atomic`](atomic.md)", "コンストラクタで初期化する")], ver=None)
A("atomic_is_lock_free", "atomic の操作が、ロックなしで行えるかを調べる。", "`atomic<T>` は、型によっては内部でロックを使います。`is_lock_free()` の自由関数版で、ロックなしで動くなら `true` です。ゲームでは、`int` や `bool` のほとんどが `true` です。", "template <class T>\nbool atomic_is_lock_free(const std::atomic<T>* obj) noexcept;", [("obj", "const atomic<T>*", "調べる対象")], "ロックなしなら `true`",
  'std::atomic<int> a;\nstd::println("{}", std::atomic_is_lock_free(&a));', "true", "リアルタイム処理で、ロックが入らないことを確かめる", ("大きな構造体に使う", "大きな型の `atomic` は、内部でロックを使います。"), [("[`atomic`](atomic.md)", "`is_lock_free()` メンバ")])
A("atomic_wait", "値が変わるまで、アトミックに待つ。", "`atomic` の値が `old` と等しい間、スレッドを眠らせます。ビジーループ（回り続ける）より CPU を使いません。`atomic_notify_one` / `atomic_notify_all` で起こされます。", "template <class T>\nvoid atomic_wait(const std::atomic<T>* obj, T old) noexcept;", [("obj", "const atomic<T>*", "対象"), ("old", "T", "この値と等しい間、待つ")], "なし",
  'std::atomic<int> a{1};\nstd::atomic_wait(&a, 0);  // 値は 0 ではないので待たずに戻る\nstd::println("returned");', "returned", "別のスレッドの完了を待つ", ("通知を忘れる", "値を変えたら、`atomic_notify_one` / `atomic_notify_all` で起こす必要があります。"), [("[`atomic_notify_one`](atomic_notify_one.md)", "1 つ起こす"), ("[`atomic_notify_all`](atomic_notify_all.md)", "全部起こす")], ver=("20", "C++20"))
A("atomic_notify_one", "atomic_wait で待っているスレッドを 1 つ起こす。", "`atomic_wait` で待っているスレッドが複数いるとき、そのうち 1 つを起こします。値を変えたあとに呼びます。", "template <class T>\nvoid atomic_notify_one(std::atomic<T>* obj) noexcept;", [("obj", "atomic<T>*", "対象")], "なし",
  'std::atomic<int> a{0};\na.store(1);\nstd::atomic_notify_one(&a);\nstd::println("notified");', "notified", "待機中のスレッドを 1 つ起こす", ("値を変えずに通知する", "値を変えてから通知します。変えないと、起きても再び眠ります。"), [("[`atomic_wait`](atomic_wait.md)", "待つ"), ("[`atomic_notify_all`](atomic_notify_all.md)", "全部起こす")], ver=("20", "C++20"))
A("atomic_notify_all", "atomic_wait で待っているスレッドを全部起こす。", "`atomic_wait` で待っているスレッドを、全部起こします。「完了した」ことを複数のスレッドに知らせるときに使います。", "template <class T>\nvoid atomic_notify_all(std::atomic<T>* obj) noexcept;", [("obj", "atomic<T>*", "対象")], "なし",
  'std::atomic<int> a{0};\na.store(1);\nstd::atomic_notify_all(&a);\nstd::println("notified all");', "notified all", "全スレッドに完了を知らせる", ("値を変えずに通知する", "値を変えてから通知します。"), [("[`atomic_wait`](atomic_wait.md)", "待つ"), ("[`atomic_notify_one`](atomic_notify_one.md)", "1 つ起こす")], ver=("20", "C++20"))
A("atomic_flag_test_and_set", "atomic_flag を立て、立てる前の状態を返す。", "`atomic_flag` は、最も単純な `atomic` の旗です。`test_and_set` は、旗を立てて、立てる前に立っていたかを返します。スピンロックの基本部品です。", "bool atomic_flag_test_and_set(std::atomic_flag* obj) noexcept;", [("obj", "atomic_flag*", "対象の旗")], "立てる前に立っていたか",
  'std::atomic_flag f = ATOMIC_FLAG_INIT;\nstd::println("{}", std::atomic_flag_test_and_set(&f));\nstd::println("{}", std::atomic_flag_test_and_set(&f));', "false\ntrue", "自作のスピンロック", ("初期化を忘れる", "C++20 より前は、`ATOMIC_FLAG_INIT` で初期化しないと、状態が不定でした。"), [("[`atomic_flag_clear`](atomic_flag_clear.md)", "旗を下ろす"), ("[`atomic_flag`](atomic_flag.md)", "旗のクラス")], inc=("atomic", "print"))
A("atomic_flag_clear", "atomic_flag を下ろす。", "`atomic_flag_test_and_set` で立てた旗を、`clear` で下ろします。スピンロックの解除に使います。", "void atomic_flag_clear(std::atomic_flag* obj) noexcept;", [("obj", "atomic_flag*", "対象の旗")], "なし",
  'std::atomic_flag f = ATOMIC_FLAG_INIT;\nstd::atomic_flag_test_and_set(&f);\nstd::atomic_flag_clear(&f);\nstd::println("{}", std::atomic_flag_test_and_set(&f));', "false", "自作のスピンロックを解除する", ("解除し忘れる", "旗を下ろさないと、待っているスレッドがずっと待ち続けます。"), [("[`atomic_flag_test_and_set`](atomic_flag_test_and_set.md)", "旗を立てる")])
A("atomic_thread_fence", "スレッド間のメモリ順序を、変数なしで強制する柵（フェンス）。", "`atomic` 変数の読み書きに順序を付ける代わりに、独立した「柵」を置いて、その前後のメモリ操作の順序を固定します。`release` の柵の前の書き込みは、`acquire` の柵の後の読み込みから見えるようになります。", "void atomic_thread_fence(std::memory_order order) noexcept;", [("order", "memory_order", "柵の強さ")], "なし",
  'int data = 0;\nstd::atomic<bool> ready{false};\nstd::thread producer([&] {\n  data = 42;\n  std::atomic_thread_fence(std::memory_order_release);\n  ready.store(true, std::memory_order_relaxed);\n});\nstd::thread consumer([&] {\n  while (!ready.load(std::memory_order_relaxed)) {\n  }\n  std::atomic_thread_fence(std::memory_order_acquire);\n  std::println("{}", data);\n});\nproducer.join();\nconsumer.join();', "42", "細かい同期の最適化", ("柵の置き場所を間違える", "柵は、フラグの書き込み・読み込みを挟む位置に置かないと、順序が守られません。"), [("[`memory_order`](memory_order.md)", "順序の種類"), ("[`atomic_signal_fence`](atomic_signal_fence.md)", "シグナルハンドラとの間")], inc=("atomic", "print", "thread"))
A("atomic_signal_fence", "同じスレッドの中の、シグナルハンドラとの間の順序を強制する柵。", "`atomic_thread_fence` はスレッド間の順序ですが、`atomic_signal_fence` は同じスレッドの中で、通常の処理とシグナルハンドラの間の順序を固定します。CPU 命令は出さず、コンパイラの並べ替えだけを防ぎます。", "void atomic_signal_fence(std::memory_order order) noexcept;", [("order", "memory_order", "柵の強さ")], "なし",
  '// 例: シグナルハンドラと本体の間で、書き込みの順序を保つ\nstd::atomic_signal_fence(std::memory_order_seq_cst);', None, "シグナルハンドラとの順序を保つ", ("スレッド間の同期に使う", "スレッド間には効きません。`atomic_thread_fence` を使います。"), [("[`atomic_thread_fence`](atomic_thread_fence.md)", "スレッド間の柵")])
A("kill_dependency", "メモリ順序の依存関係をここで断ち切る。", "`memory_order_consume` の依存の連鎖を、ここで終わらせます。実際の実装では `consume` が `acquire` として扱われるので、ほとんど使われません。C++26 では `consume` 自体が非推奨です。", "template <class T>\nT kill_dependency(T y) noexcept;", [("y", "T", "依存を断ち切る値")], "`y` のコピー",
  'int y = std::kill_dependency(5);\nstd::println("{}", y);', "5", "（実際にはほぼ使われない）", ("新しいコードで使う", "`consume` が非推奨のため、使う場面がありません。"), [("[`memory_order`](memory_order.md)", "順序の種類")], inc=("atomic", "print"))

# ---- stop_token 周辺
P(CO + "nostopstate.md", "std::nostopstate", "stop_source を、停止の状態を持たない形で作る目印。", "rare", "stop_token",
  "`std::stop_source` は、作ると停止の状態（共有されるフラグ）を確保します。確保したくない（まだ使わない）ときは、`std::nostopstate` を渡して作ると、状態を持たない `stop_source` になります。",
  ["`stop_source(std::nostopstate)` の形で使う。", "状態を持たないので、`stop_possible()` は `false`。", "あとで本物の `stop_source` を代入できる。"],
  [("停止の機能を使わないときの初期値", "`std::stop_source s(std::nostopstate);`")],
  ("状態がない `stop_source` に `request_stop` する", "状態を持たないものに停止を要求しても、何も起こりません。"), [("[`stop_source`](stop_source.md)", "停止を要求する側"), ("[`stop_token`](stop_token.md)", "停止を見る側")],
  ["停止の状態を持たない目印", "stop_possible() が false", "あとで代入できる"],
  sig="struct nostopstate_t { explicit nostopstate_t() = default; };\ninline constexpr nostopstate_t nostopstate{};", args=[], ret="なし（目印）", cx="定数",
  code="""#include <print>
#include <stop_token>

int main() {
  std::stop_source s(std::nostopstate);
  std::println("{}", s.stop_possible());
}""", out="false", ver=("20", "C++20"), info=COI, rj="stop_token/nostopstate.html", cr="thread/nostopstate")
P(CO + "never_stop_token.md", "std::never_stop_token", "停止が絶対に要求されない stop_token。", "rare", "stop_token",
  "停止の機能を持つ関数でも、停止させる必要がない呼び出し元もあります。そのとき、本物の `stop_source` を作る代わりに、`never_stop_token` を渡すと、停止の確認が常に `false` になり、コストもかかりません。",
  ["`stop_possible()` と `stop_requested()` が常に `false`。", "ジェネリックな関数で、停止が不要な場合の型として使う。", "C++26 の機能。"],
  [("停止不要の呼び出し", "`Run(std::never_stop_token{})`")],
  ("停止できると期待する", "停止が要求されることはありません。"), [("[`stop_token`](stop_token.md)", "実際の stop_token")],
  ["絶対に止まらない stop_token", "常に false", "C++26"],
  sig="class never_stop_token {\n public:\n  static constexpr bool stop_requested() noexcept { return false; }\n  static constexpr bool stop_possible() noexcept { return false; }\n};", args=[], ret="なし", cx="定数",
  code="""#include <print>
#include <stop_token>

int main() {
  std::never_stop_token t;
  std::println("{}", t.stop_possible());
}""", out="false", ver=("26", "C++26"), info=COI, rj="stop_token/never_stop_token.html", cr="thread/never_stop_token", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")

# ---- 実行ポリシー
EXC = "algorithms/"
for nm, what, intro, ver_ in [
    ("seq", "並列化せず、順番に実行するポリシー。", "`std::execution::seq` を第 1 引数に渡すと、アルゴリズムは**1 つのスレッドで順番に**実行されます。ポリシーなしと同じ動作ですが、「並列にしない」ことを明示できます。例外が出たら `std::terminate` になる点が、ポリシーなしと違います。", ("17", "C++17")),
    ("par_unseq", "複数のスレッドで、しかもベクトル化も許して実行するポリシー。", "`std::execution::par_unseq` は、複数のスレッドに分けたうえで、1 つのスレッドの中でも SIMD 命令でまとめて処理することを許します。最も速くなりうる代わり、処理の中でロックを取ったり、メモリを確保したりしてはいけません。", ("17", "C++17")),
    ("unseq", "1 つのスレッドの中で、ベクトル化（SIMD）を許して実行するポリシー。", "`std::execution::unseq` は、スレッドは増やさず、1 つのスレッドの中で SIMD 命令でまとめて処理することを許します。処理の中でロックを取ってはいけません。", ("20", "C++20"))]:
    P(EXC + nm + ".md", f"std::execution::{nm}", what, "rare", "execution", intro,
      ["アルゴリズムの第 1 引数に渡して使う。", "実装の対応はコンパイラごとに違う（GCC は TBB が必要なことがある）。", "処理の中で、データ競合を起こさないようにする。"],
      [("大量のデータの整列や変換を速くする", f"`std::sort(std::execution::{nm}, v.begin(), v.end());`")],
      ("データ競合を起こす", "ポリシーを付けると、要素ごとの処理が並行・同時に走ることがあります。共有する変数への書き込みは、`atomic` などで守ります。"),
      [("[`execution`](execution.md)", "実行ポリシーの全体")],
      [what.rstrip("。"), "アルゴリズムの第 1 引数に渡す", "データ競合に注意"],
      sig=f"inline constexpr /* 実装定義 */ std::execution::{nm};", args=[], ret="なし（ポリシーの定数）", cx="アルゴリズムに依存",
      code=f"""#include <algorithm>
#include <execution>
#include <print>
#include <vector>

int main() {{
  std::vector<int> v = {{3, 1, 2}};
  std::sort(std::execution::{nm}, v.begin(), v.end());
  std::println("{{}}", v);
}}""", out="[1, 2, 3]", ver=ver_, info="[実行ポリシー](execution.md) を先に読んでください。", rj="execution/execution_policy.html", cr="algorithm/execution_policy_tag",
      compiler=f"{ver_[1]} の機能です。GCC では TBB（`-ltbb`）が必要なことがあります。")
P(EXC + "is_execution_policy.md", "std::is_execution_policy", "型が実行ポリシーかを調べる型特性。", "rare", "execution",
  "ジェネリックな関数で、第 1 引数がポリシーかそうでないかを区別したいことがあります。`is_execution_policy_v<T>` は、`T` が `seq`・`par`・`par_unseq`・`unseq` の型なら `true` です。",
  ["`_v` 版で `bool` が取れる。", "ポリシーつきとなしのオーバーロードを書き分けるときに使う。", "型に `const` や参照がついていない形（`remove_cvref_t`）で調べる。"],
  [("ポリシーを受け取るテンプレートを制約する", "`std::enable_if_t<std::is_execution_policy_v<std::decay_t<P>>>`")],
  ("参照つきの型を渡す", "`const auto&` のままだと `false` です。`std::remove_cvref_t` で外してから調べます。"), [("[`execution`](execution.md)", "実行ポリシー")],
  ["実行ポリシーかを調べる型特性", "_v 版で bool", "参照を外してから調べる"],
  sig="template <class T>\nstruct is_execution_policy;\ntemplate <class T>\ninline constexpr bool is_execution_policy_v = is_execution_policy<T>::value;", args=[("T", "型", "調べる型")], ret="実行ポリシーなら `true`", cx="コンパイル時のみ",
  code="""#include <execution>
#include <print>
#include <type_traits>

int main() {
  using Par = std::remove_cvref_t<decltype(std::execution::par)>;
  std::println("{}", std::is_execution_policy_v<Par>);
  std::println("{}", std::is_execution_policy_v<int>);
}""", out="true\nfalse", ver=("17", "C++17"), info="[実行ポリシー](execution.md) を先に読んでください。", rj="execution/is_execution_policy.html", cr="algorithm/is_execution_policy")

# ---- RCU と hazard pointer（C++26）
RC_ = "concurrency/"
RCI = COI


def RCU(name, summary, intro, sig, ret, tips, game, miss, sim, header="rcu"):
    P(RC_ + name + ".md", "std::" + name, summary, "rare", header, intro, tips, [("読み取りが圧倒的に多い共有データの管理", game)], miss, sim,
      [summary.rstrip("。"), "読み取りをロックなしで行う仕組み", "C++26"], sig=sig, args=[], ret=ret, cx="実装依存",
      code="// 例（概念）: " + game, out=None, ver=("26", "C++26"), info=RCI, rj=f"{header}/{name}.html", cr=f"thread/{name}", compiler="C++26 の機能です。対応する標準ライブラリは、まだ限られます。")


RCU("rcu_domain", "RCU の管理単位（ドメイン）を表す型。", "RCU（Read-Copy-Update）は、読み取りをロックなしで行い、書き換えはコピーを作って差し替える同期方式です。`rcu_domain` は、読み取り中のスレッドを数える管理の単位で、ふつうは標準のドメイン（`rcu_default_domain()`）を使います。",
    "class rcu_domain {\n public:\n  void lock() noexcept;    // 読み取り区間の開始\n  void unlock() noexcept;  // 読み取り区間の終了\n};", "読み取り区間を管理する", ["`lock()` / `unlock()` が読み取り区間の開始・終了。", "`scoped_lock` で読み取り区間を作る。", "ふつうは標準のドメインを使う。"], "読み取りが多い設定データを、ロックなしで読めるようにする", ("読み取り区間で長く待つ", "区間が長いと、書き換えの後始末が遅れます。"), [("[`rcu_default_domain`](rcu_default_domain.md)", "標準のドメイン")])
RCU("rcu_default_domain", "標準の RCU ドメインを返す関数。", "ふつうは自分でドメインを作らず、標準のドメインを使います。`std::rcu_default_domain()` が、そのドメインへの参照を返します。",
    "rcu_domain& rcu_default_domain() noexcept;", "標準の `rcu_domain` への参照", ["標準のドメインを返す。", "`scoped_lock lk(std::rcu_default_domain());` で読み取り区間を作る。", "プログラム全体で 1 つ。"], "標準のドメインで読み取り区間を作る", ("ドメインを自作する", "特別な理由がなければ、標準のドメインを使います。"), [("[`rcu_domain`](rcu_domain.md)", "ドメインの型")])
RCU("rcu_obj_base", "RCU で保護するオブジェクトが継承する基底クラス。", "RCU で守るオブジェクトは、書き換えで古いものを差し替えたあと、読み取り中のスレッドがいなくなってから破棄する必要があります。`rcu_obj_base<T>` を継承すると、`retire()` で「あとで安全になったら破棄して」と頼めます。",
    "template <class T, class D = default_delete<T>>\nclass rcu_obj_base {\n public:\n  void retire(D d = D(), rcu_domain& dom = rcu_default_domain()) noexcept;\n};", "`retire()` でオブジェクトの破棄を予約する", ["`class MyData : public std::rcu_obj_base<MyData>` と継承する。", "`retire()` が、安全になったら破棄する。", "C++26。"], "古い設定データを、読み取りが終わってから破棄する", ("`delete` を直接呼ぶ", "読み取り中のスレッドがいると壊れます。`retire()` に任せます。"), [("[`rcu_retire`](rcu_retire.md)", "継承せずに破棄を予約する")])
RCU("rcu_retire", "オブジェクトの破棄を、読み取りが終わってからの予約にする。", "`rcu_obj_base` を継承できない型でも、`rcu_retire(ptr)` で、読み取り中のスレッドがいなくなってから破棄させられます。",
    "template <class T, class D = default_delete<T>>\nvoid rcu_retire(T* p, D d = D(), rcu_domain& dom = rcu_default_domain());", "なし", ["継承せずに破棄を予約できる。", "第 2 引数で破棄の方法を指定できる。", "C++26。"], "古いデータを安全に破棄する", ("すぐに破棄されると思う", "読み取りが終わったあと、あるタイミングで破棄されます。"), [("[`rcu_obj_base`](rcu_obj_base.md)", "継承して使う版")])
RCU("rcu_synchronize", "読み取り中のスレッドがいなくなるまで待つ。", "古いデータを差し替えたあと、そのデータを読んでいるかもしれないスレッドが、全員終わるまで待つ関数です。待ったあとは、古いデータを破棄しても安全です。",
    "void rcu_synchronize(rcu_domain& dom = rcu_default_domain()) noexcept;", "なし（読み取りが終わるまで待つ）", ["差し替えのあと、古いデータの破棄の前に呼ぶ。", "待つので、遅い。", "遅れてよいなら `rcu_retire`。"], "データ差し替えの後始末を同期的に行う", ("読み取り区間の中で呼ぶ", "自分自身を待ってしまい、デッドロックします。"), [("[`rcu_retire`](rcu_retire.md)", "待たずに予約する")])
RCU("rcu_barrier", "予約された破棄が、すべて終わるまで待つ。", "`rcu_retire` で予約した破棄が、全部完了するのを待ちます。プログラム終了前に、後始末を確実に終わらせたいときに使います。",
    "void rcu_barrier(rcu_domain& dom = rcu_default_domain()) noexcept;", "なし（予約済みの破棄が終わるまで待つ）", ["`rcu_retire` の予約が全部終わるまで待つ。", "終了処理の前に呼ぶ。", "C++26。"], "終了前に、保留中の破棄を完了させる", ("読み取り区間の中で呼ぶ", "デッドロックします。"), [("[`rcu_retire`](rcu_retire.md)", "破棄を予約する")])
RCU("hazard_pointer", "別のスレッドが使用中のオブジェクトを「使っている」と宣言する印。", "ハザードポインタは、ロックなしのデータ構造で、「いま読んでいるオブジェクトを、他のスレッドに破棄されない」ように守る仕組みです。`hazard_pointer` に読みたいオブジェクトを登録（保護）してから読みます。",
    "class hazard_pointer {\n public:\n  template <class T> T* protect(const std::atomic<T*>& src) noexcept;\n  void reset_protection() noexcept;\n};", "保護しているポインタを返す", ["`protect(src)` で読みたいポインタを保護する。", "`reset_protection()` で保護を解く。", "C++26。"], "ロックなしのキューで、読み取り中のノードを守る", ("保護せずに読む", "別のスレッドが破棄すると壊れます。"), [("[`hazard_pointer_obj_base`](hazard_pointer_obj_base.md)", "守られる側の基底クラス"), ("[`make_hazard_pointer`](make_hazard_pointer.md)", "作る関数")], header="hazard_pointer")
RCU("hazard_pointer_obj_base", "ハザードポインタで守るオブジェクトが継承する基底クラス。", "ハザードポインタで守るオブジェクトは、誰も保護していないことを確かめてから破棄する必要があります。`hazard_pointer_obj_base<T>` を継承すると、`retire()` で「保護が外れたら破棄して」と頼めます。",
    "template <class T, class D = default_delete<T>>\nclass hazard_pointer_obj_base {\n public:\n  void retire(D d = D()) noexcept;\n};", "`retire()` で破棄を予約する", ["`class Node : public std::hazard_pointer_obj_base<Node>` と継承する。", "`retire()` が、保護が外れたら破棄する。", "C++26。"], "ロックなしのキューのノードを、安全に破棄する", ("`delete` を直接呼ぶ", "他のスレッドが保護していると壊れます。`retire()` に任せます。"), [("[`hazard_pointer`](hazard_pointer.md)", "保護する側")], header="hazard_pointer")
RCU("make_hazard_pointer", "ハザードポインタを作る。", "空のハザードポインタを作ります。作ったものに `protect()` で、読みたいオブジェクトを保護させます。",
    "hazard_pointer make_hazard_pointer();", "新しい `hazard_pointer`", ["戻り値で `hazard_pointer` を受け取る。", "作るのにはコストがかかるので、使い回すとよい。", "C++26。"], "ロックなしのデータ構造の読み取りを始める前に作る", ("読み取りごとに作る", "作るコストがかかります。スレッドごとに使い回します。"), [("[`hazard_pointer`](hazard_pointer.md)", "ハザードポインタ")], header="hazard_pointer")

if __name__ == "__main__":
    flush_hubs()
