"""バッチ 8: views のクラス名、ranges の部品、<iterator> の未登録分。"""
from mk import *  # noqa: F401,F403

# ================= views のクラス（アダプタのページに節を足す） =================
V = "algorithms/views/"
VIEWS = [
    ("filter", "filter_view", "template <input_range V, indirect_unary_predicate<iterator_t<V>> Pred>\nclass filter_view;", "条件に合う要素だけを通す view。`views::filter(pred)` が作ります。", "20"),
    ("transform", "transform_view", "template <input_range V, copy_constructible F>\nclass transform_view;", "各要素を関数で変換して見せる view。`views::transform(f)` が作ります。", "20"),
    ("take", "take_view", "template <view V>\nclass take_view;", "先頭から n 個だけを見せる view。`views::take(n)` が作ります。", "20"),
    ("take_while", "take_while_view", "template <view V, class Pred>\nclass take_while_view;", "条件が真の間だけ先頭から見せる view。`views::take_while(pred)` が作ります。", "20"),
    ("drop", "drop_view", "template <view V>\nclass drop_view;", "先頭の n 個を飛ばして見せる view。`views::drop(n)` が作ります。", "20"),
    ("drop_while", "drop_while_view", "template <view V, class Pred>\nclass drop_while_view;", "条件が真の間だけ先頭を飛ばして見せる view。`views::drop_while(pred)` が作ります。", "20"),
    ("join", "join_view", "template <input_range V>\nclass join_view;", "範囲の範囲を、1 本につなげて見せる view。`views::join` が作ります。", "20"),
    ("join_with", "join_with_view", "template <input_range V, forward_range Pattern>\nclass join_with_view;", "範囲の範囲を、区切りをはさんでつなぐ view。`views::join_with(sep)` が作ります。", "23"),
    ("lazy_split", "lazy_split_view", "template <input_range V, forward_range Pattern>\nclass lazy_split_view;", "区切りで分割する view（入力範囲でも使える遅延版）。`views::lazy_split(sep)` が作ります。", "20"),
    ("split", "split_view", "template <forward_range V, forward_range Pattern>\nclass split_view;", "区切りで分割する view。`views::split(sep)` が作ります。", "20"),
    ("common", "common_view", "template <view V>\nclass common_view;", "begin と end が同じ型になるように包んだ view。`views::common` が作ります。", "20"),
    ("reverse", "reverse_view", "template <view V>\nclass reverse_view;", "逆順に見せる view。`views::reverse` が作ります。", "20"),
    ("as_const", "as_const_view", "template <input_range V>\nclass as_const_view;", "要素を const として見せる view。`views::as_const` が作ります。", "23"),
    ("as_rvalue", "as_rvalue_view", "template <input_range V>\nclass as_rvalue_view;", "要素を右辺値として見せる（ムーブさせる）view。`views::as_rvalue` が作ります。", "23"),
    ("elements", "elements_view", "template <input_range V, size_t N>\nclass elements_view;", "タプルの N 番目の要素だけを取り出す view。`views::elements<N>` が作ります。", "20"),
    ("keys", "keys_view", "template <class V>\nusing keys_view = elements_view<V, 0>;", "ペアの 1 つ目（map のキー）を取り出す view。`views::keys` が作ります。", "20"),
    ("values", "values_view", "template <class V>\nusing values_view = elements_view<V, 1>;", "ペアの 2 つ目（map の値）を取り出す view。`views::values` が作ります。", "20"),
    ("zip", "zip_view", "template <input_range... Vs>\nclass zip_view;", "複数の範囲をいっしょに歩き、タプルにして見せる view。`views::zip` が作ります。", "23"),
    ("zip_transform", "zip_transform_view", "template <copy_constructible F, input_range... Vs>\nclass zip_transform_view;", "複数の範囲をいっしょに歩き、関数で 1 つの値にする view。`views::zip_transform` が作ります。", "23"),
    ("adjacent", "adjacent_view", "template <forward_range V, size_t N>\nclass adjacent_view;", "隣り合う N 個の要素の組を見せる view。`views::adjacent<N>` が作ります。", "23"),
    ("adjacent_transform", "adjacent_transform_view", "template <forward_range V, copy_constructible F, size_t N>\nclass adjacent_transform_view;", "隣り合う N 個の要素を関数で 1 つの値にする view。`views::adjacent_transform<N>` が作ります。", "23"),
    ("slide", "slide_view", "template <forward_range V>\nclass slide_view;", "長さ n の窓を 1 つずつずらして見せる view。`views::slide(n)` が作ります。", "23"),
    ("chunk", "chunk_view", "template <view V>\nclass chunk_view;", "n 個ずつの塊に区切って見せる view。`views::chunk(n)` が作ります。", "23"),
    ("chunk_by", "chunk_by_view", "template <forward_range V, indirect_binary_predicate<iterator_t<V>, iterator_t<V>> Pred>\nclass chunk_by_view;", "隣り合う要素の関係が続く間を塊にする view。`views::chunk_by(pred)` が作ります。", "23"),
    ("stride", "stride_view", "template <input_range V>\nclass stride_view;", "n 個おきに要素を見せる view。`views::stride(n)` が作ります。", "23"),
    ("cartesian_product", "cartesian_product_view", "template <input_range First, forward_range... Vs>\nclass cartesian_product_view;", "複数の範囲の直積（全部の組み合わせ）を見せる view。`views::cartesian_product` が作ります。", "23"),
    ("enumerate", "enumerate_view", "template <view V>\nclass enumerate_view;", "要素に 0 から始まる番号をつけて見せる view。`views::enumerate` が作ります。", "23"),
    ("empty", "empty_view", "template <class T>\nclass empty_view;", "要素が 0 個の view。`views::empty<T>` で作ります。", "20"),
    ("single", "single_view", "template <move_constructible T>\nclass single_view;", "要素が 1 個だけの view。`views::single(x)` が作ります。", "20"),
    ("iota", "iota_view", "template <weakly_incrementable W, semiregular Bound = unreachable_sentinel_t>\nclass iota_view;", "start から 1 ずつ増える値を並べる view。`views::iota(a, b)` が作ります。", "20"),
    ("repeat", "repeat_view", "template <move_constructible W, semiregular Bound = unreachable_sentinel_t>\nclass repeat_view;", "同じ値を繰り返す view。`views::repeat(x, n)` が作ります。", "23"),
    ("istream_view", "basic_istream_view", "template <movable Val, class CharT, class Traits>\nclass basic_istream_view;", "入力ストリームから `>>` で読み取り続ける view。`views::istream<T>(in)` が作ります。", "20"),
]
for page_, cls, sig_, what, ver in VIEWS:
    add_secs(V + page_ + ".md", fn(f"std::ranges::{cls}", sig_, None, "`begin()` / `end()` をもつ view の型", "begin / end は定数。要素の取り出しは元の範囲と同じ", None,
             notes=f"{what}\n\nふつうは `views::{page_}` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::{cls} v(r, ...)` と直接作るときにだけ登場します。",
             ver=("23" if ver == "23" else "20", "C++" + ver), ids=cls))

# 新しい view（C++26）
P(V + "concat.md", "views::concat", "複数の範囲を、1 本につなげて見せる view。", "rare", "ranges",
  "2 つの `vector` の中身を順に処理したいとき、結合した `vector` を作ると、コピーが必要になります。`views::concat(a, b, ...)` は、コピーせずに、複数の範囲を 1 本の範囲のように見せます。`join` と違い、範囲の範囲ではなく、複数の範囲を直接渡します。",
  ["要素の型はそろっている必要がある（共通の参照型が必要）。", "コピーはしない（元の範囲を借りるだけ）。", "`join` は範囲の範囲用、`concat` は範囲を直接並べる用。"],
  [("2 つの配列を 1 つのループで処理", "`for (int x : std::views::concat(a, b)) { ... }`")],
  ("元の範囲が先に消える", "view は借りるだけなので、元の範囲が先に消えると壊れます。"),
  [("[`views::join`](join.md)", "範囲の範囲をつなぐ"), ("[`views::zip`](zip.md)", "並べて歩く")],
  ["複数の範囲を 1 本に見せる", "コピーしない", "C++26"],
  secs=[fn("views::concat", "template <input_range... Rs>\nconstexpr auto views::concat(Rs&&... rs);", [("rs...", "範囲", "つなぐ範囲（2 つ以上）")], "`concat_view`", "begin / end は定数。要素の取り出しは元の範囲と同じ", None, ids="concat"),
        fn("std::ranges::concat_view", "template <input_range... Views>\nclass concat_view;", None, "`views::concat` が作る view の型", "", None, notes="ふつうは `views::concat` で書くので、型の名前を自分で書くことは少なく、`auto` で受けます。", ids="concat_view")],
  code="""#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> a = {1, 2};
  std::vector<int> b = {3, 4};
  int sum = 0;
  for (int x : std::views::concat(a, b)) {
    sum += x;
  }
  std::println("{}", sum);
}""", out="10", ver=("26", "C++26"), info="[`views`](../views.md) を先に読んでください。", rj="ranges/concat_view.html", cr="ranges/concat_view",
  group="ビュー（std::views）", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")
P(V + "cache_latest.md", "views::cache_latest", "直前に計算した要素を覚えておく view。", "rare", "ranges",
  "`transform` の関数が重い処理で、同じ要素に対して何度も呼ばれると無駄です。`views::cache_latest` は、いま見ている要素の計算結果を 1 つだけ覚えておき、同じ要素を読むときは再計算しません。",
  ["直前の 1 要素だけを覚える。", "`transform` や `filter` と組み合わせて、同じ要素の関数呼び出しが何度も起きるのを防ぐ。", "`const` では使えない（内部に状態をもつため）。"],
  [("重い変換の結果を 1 度だけ計算する", "`v | views::transform(heavy) | views::cache_latest | views::filter(pred)`")],
  ("const な範囲に使う", "内部に状態を持つため、`const` の view としては使えません。"),
  [("[`views::transform`](transform.md)", "各要素を変換する")],
  ["直前の要素の結果を覚える", "同じ要素の再計算を避ける", "C++26"],
  secs=[fn("views::cache_latest", "constexpr auto views::cache_latest();  // パイプで使う", None, "`cache_latest_view`", "begin / end は定数", None, ids="cache_latest"),
        fn("std::ranges::cache_latest_view", "template <input_range V>\nclass cache_latest_view;", None, "`views::cache_latest` が作る view の型", "", None, notes="ふつうは `views::cache_latest` で書くので、型の名前を自分で書くことは少なく、`auto` で受けます。", ids="cache_latest_view")],
  code="""#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  int calls = 0;
  auto heavy = [&](int x) { ++calls; return x * x; };
  auto r = v | std::views::transform(heavy) | std::views::cache_latest
             | std::views::filter([](int x) { return x % 2 == 0; });
  int sum = 0;
  for (int x : r) sum += x;
  std::println("{} {}", sum, calls);
}""", out="20 4", ver=("26", "C++26"), info="[`views`](../views.md) を先に読んでください。", rj="ranges/cache_latest_view.html", cr="ranges/cache_latest_view",
  group="ビュー（std::views）", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")

# ================= ranges の部品 =================
RG = "support/ranges/"
RGI = "[`std::ranges::range`](range.md) を先に読んでください。"
V20 = ("20", "C++20")


def RC(name, summary, intro, req, body, out, miss, sim, tips=None, rank="rare"):
    Q(RG + name + ".md", "std::ranges::" + name, summary, rank, ["ranges", "print"], intro,
      tips or ["コンセプトなので、`requires` やテンプレートの制約に書く。", "`std::ranges::" + name + "<T>` は `bool` の定数式。", "`static_assert` でも確かめられる。"],
      f"template <class T>\nconcept {name} = /* {req} */;", [("T", "型", "調べる範囲の型")], "条件を満たせば `true`（コンパイル時の定数）", body, out,
      use="テンプレートの引数を制約して、使える範囲だけを受け付ける", miss=miss, sim=sim, cx="コンパイル時のみ", ver=V20, info=RGI, rj=f"ranges/{name}.html", cr=f"ranges/{name}")


RC("input_range", "入力として一度だけ読める範囲を要求するコンセプト。", "ストリームのように、先頭から一方向に 1 回だけ読める範囲もあります。`input_range` は、そうした最も弱い条件の範囲です。ほとんどの標準コンテナと view が満たします。", "begin が input_iterator を返す",
   '  std::println("{}", std::ranges::input_range<std::vector<int>>);\n  std::println("{}", std::ranges::input_range<int>);', "true\nfalse",
   ("入力範囲を 2 回読む", "入力専用の範囲（`istream_view` など）は、2 回走査できません。2 回読むなら `forward_range` を要求します。"), [("[`forward_range`](forward_range.md)", "何度でも読める")])
RC("output_range", "書き込める範囲を要求するコンセプト。", "結果を書き込む先の範囲を受け取る関数では、「書き込める」ことを要求します。`output_range<R, T>` は、型 `T` の値を書き込める範囲かを調べます。", "begin が output_iterator<T> を返す",
   '  std::println("{}", std::ranges::output_range<std::vector<int>, int>);\n  std::println("{}", std::ranges::output_range<const std::vector<int>, int>);', "true\nfalse",
   ("const な範囲に書く", "const な範囲は書き込めません。`output_range` を要求しておくと、コンパイル時に分かります。"), [("[`input_range`](input_range.md)", "読める範囲")])
RC("forward_range", "何度でも先頭から読み直せる範囲を要求するコンセプト。", "ストリームと違って、`std::forward_list` のような範囲は、何度でも先頭から読み直せます。`forward_range` は、その性質を要求します。", "begin が forward_iterator を返す",
   '  std::println("{}", std::ranges::forward_range<std::forward_list<int>>);\n  std::println("{}", std::ranges::forward_range<std::ranges::istream_view<int>>);', "true\nfalse",
   ("`istream_view` に使う", "入力ストリームは 1 回しか読めません。"), [("[`input_range`](input_range.md)", "より弱い条件"), ("[`bidirectional_range`](bidirectional_range.md)", "後ろにも戻れる")])
RC("bidirectional_range", "前後どちらにも進める範囲を要求するコンセプト。", "`std::list` のように、前にも後ろにも 1 つずつ動ける範囲です。`reverse` のように、後ろから歩く処理が使えます。", "begin が bidirectional_iterator を返す",
   '  std::println("{}", std::ranges::bidirectional_range<std::list<int>>);\n  std::println("{}", std::ranges::bidirectional_range<std::forward_list<int>>);', "true\nfalse",
   ("`forward_list` に reverse を使う", "`forward_list` は前にしか進めません。"), [("[`forward_range`](forward_range.md)", "より弱い条件"), ("[`random_access_range`](random_access_range.md)", "添字で飛べる")])
RC("random_access_range", "添字で好きな位置へ飛べる範囲を要求するコンセプト。", "`vector` や `deque` のように、`it + n` で一気に飛べる範囲です。`sort` などが要求します。", "begin が random_access_iterator を返す",
   '  std::println("{}", std::ranges::random_access_range<std::deque<int>>);\n  std::println("{}", std::ranges::random_access_range<std::list<int>>);', "true\nfalse",
   ("`list` に sort を使う", "`list` は添字で飛べないので `sort` できません。`list::sort` を使います。"), [("[`bidirectional_range`](bidirectional_range.md)", "より弱い条件"), ("[`contiguous_range`](contiguous_range.md)", "メモリが連続")])
RC("contiguous_range", "要素がメモリ上で連続して並ぶ範囲を要求するコンセプト。", "`vector`・`array`・`string` のように、要素が連続して並ぶ範囲です。`data()` でポインタを取り出して、C の API に渡せます。", "begin が contiguous_iterator を返し、data() がある",
   '  std::println("{}", std::ranges::contiguous_range<std::vector<int>>);\n  std::println("{}", std::ranges::contiguous_range<std::deque<int>>);', "true\nfalse",
   ("`deque` を C の API に渡す", "`deque` は連続していません。`data()` もありません。"), [("[`random_access_range`](random_access_range.md)", "連続とは限らない")])
RC("sized_range", "要素数を定数時間で返せる範囲を要求するコンセプト。", "`size()` を呼べる範囲です。`list` は `size()` が定数時間なので満たし、`forward_list` は `size()` がないので満たしません。", "ranges::size(r) が使える",
   '  std::println("{}", std::ranges::sized_range<std::list<int>>);\n  std::println("{}", std::ranges::sized_range<std::forward_list<int>>);', "true\nfalse",
   ("`size()` が速いと思い込む", "`sized_range` は定数時間を求めます。距離を数える必要がある範囲は満たしません。"), [("[`std::ranges::size`](size.md)", "要素数を返す")])
RC("common_range", "begin と end が同じ型の範囲を要求するコンセプト。", "従来のアルゴリズムは、`begin` と `end` が同じ型であることを前提にしていました。`common_range` は、その性質を要求します。`views::iota(1)`（終わりなし）のような範囲は満たしません。", "begin と end が同じ型",
   '  std::println("{}", std::ranges::common_range<std::vector<int>>);\n  std::println("{}", std::ranges::common_range<std::ranges::iota_view<int>>);', "true\nfalse",
   ("古いアルゴリズムに view を直接渡す", "`common_range` でない view は、従来の `std::sort` などに渡せません。`views::common` で包みます。"), [("[`views::common`](../../algorithms/views/common.md)", "common_range に変える")])
RC("borrowed_range", "元の範囲より長生きするイテレータを返せる範囲を要求するコンセプト。", "`find` が返したイテレータを、一時オブジェクトの範囲に対して使うと、そのまま壊れた参照になります。`borrowed_range` は、「イテレータが範囲の寿命に依存しない」範囲です。左辺値の範囲や `string_view`・`span` は満たします。", "左辺値、または enable_borrowed_range が true",
   '  std::println("{}", std::ranges::borrowed_range<std::vector<int>&>);\n  std::println("{}", std::ranges::borrowed_range<std::vector<int>>);\n  std::println("{}", std::ranges::borrowed_range<std::string_view>);', "true\nfalse\ntrue",
   ("一時オブジェクトの `find` の結果を使う", "`borrowed_range` でない一時オブジェクトに `ranges::find` を使うと、`dangling` が返ります。"), [("[`dangling`](dangling.md)", "壊れたイテレータの代わり"), ("[`enable_borrowed_range`](enable_borrowed_range.md)", "借りられると宣言する")])
RC("viewable_range", "view に変換できる範囲を要求するコンセプト。", "パイプ（`|`）で view に渡せる範囲かを表します。左辺値の範囲や、ムーブできる右辺値の範囲が満たします。`views::all` で包めるかが条件です。", "views::all が使える",
   '  std::println("{}", std::ranges::viewable_range<std::vector<int>&>);\n  std::println("{}", std::ranges::viewable_range<int>);', "true\nfalse",
   ("コピーできない範囲を左辺値の const で渡す", "view に包めない範囲は、パイプに渡せません。"), [("[`views::all`](../../algorithms/views/all.md)", "view に包む")])

for nm, base, ex, out in [
    ("range_value_t", "std::ranges::range_value_t<std::vector<int>>", "int", "true"),
    ("range_reference_t", "std::ranges::range_reference_t<std::vector<int>>", "int&", "true"),
    ("range_difference_t", "std::ranges::range_difference_t<std::vector<int>>", "std::ptrdiff_t", "true"),
    ("range_size_t", "std::ranges::range_size_t<std::vector<int>>", "std::size_t", "true"),
    ("iterator_t", "std::ranges::iterator_t<std::vector<int>>", "std::vector<int>::iterator", "true"),
    ("sentinel_t", "std::ranges::sentinel_t<std::vector<int>>", "std::vector<int>::iterator", "true"),
    ("borrowed_iterator_t", "std::ranges::borrowed_iterator_t<std::vector<int>&>", "std::vector<int>::iterator", "true")]:
    what = {"range_value_t": "範囲の要素の型", "range_reference_t": "範囲の要素の参照の型", "range_difference_t": "範囲のイテレータの差の型", "range_size_t": "範囲の要素数の型",
            "iterator_t": "範囲のイテレータの型", "sentinel_t": "範囲の終端（sentinel）の型", "borrowed_iterator_t": "範囲のイテレータの型（借りられない範囲なら dangling）"}[nm]
    Q(RG + nm + ".md", "std::ranges::" + nm, f"{what}を取り出す型の別名。", "rare", ["ranges", "type_traits", "vector", "print", "cstddef"] if nm in ("range_difference_t", "range_size_t") else ["ranges", "type_traits", "vector", "print"],
      f"テンプレートの中で、範囲の型 `R` から「要素の型」や「イテレータの型」を知りたいことがあります。`R::value_type` では、配列や view など `value_type` を持たない範囲に使えません。`{nm}<R>` は、どんな範囲にも使える統一された書き方です。",
      ["`R` は `range` を満たす型。", "`_t` が付いた型の別名（`typename` 不要）。", "配列にも view にも使える。"],
      f"template <ranges::range R>\nusing {nm} = /* {what} */;", [("R", "型", "範囲の型")], what, f'using T = {base};\nstd::println("{{}}", std::is_same_v<T, {ex}>);', out,
      use="ジェネリックな関数で、要素の型を取り出す", miss=("`R::value_type` を使う", "配列や view には `value_type` がないことがあります。`range_value_t<R>` を使います。"),
      sim=[("[`range`](range.md)", "範囲のコンセプト"), ("[`std::iter_value_t`](../iterator/iter_value_t.md)", "イテレータ側の型")], cx="コンパイル時のみ", ver=V20, info=RGI, rj=f"ranges/{nm}.html", cr=f"ranges/{nm}")

Q(RG + "enable_borrowed_range.md", "std::ranges::enable_borrowed_range", "自分の型を borrowed_range として扱ってよいと宣言する変数テンプレート。", "rare", ["ranges", "print", "string_view", "string"],
  "`string_view` や `span` は、元のデータを借りているだけなので、一時オブジェクトでも、イテレータは元のデータが生きている限り使えます。このことを標準に伝えるのが `enable_borrowed_range<T>` で、自作の view の型に対して `true` に特殊化します。",
  ["`string_view`・`span`・`subrange` などは最初から `true`。", "自作の view がイテレータを自分の中に持たないなら、`true` に特殊化する。", "`true` にすると `ranges::find` の戻り値が `dangling` にならない。"],
  "template <class R>\ninline constexpr bool enable_borrowed_range = false;", [("R", "型", "宣言する範囲の型")], "既定は `false`。特殊化で `true`",
  'std::println("{}", std::ranges::enable_borrowed_range<std::string_view>);\nstd::println("{}", std::ranges::enable_borrowed_range<std::string>);', "true\nfalse",
  use="自作の view を一時オブジェクトでも使えるようにする", miss=("元のデータを持つ型に `true` を指定する", "データそのものを持つ型（`vector` など）に `true` を指定すると、壊れたイテレータが返ります。"),
  sim=[("[`borrowed_range`](borrowed_range.md)", "このコンセプトの元になる"), ("[`dangling`](dangling.md)", "壊れたイテレータの代わり")], cx="コンパイル時のみ", ver=V20, info=RGI, rj="ranges/enable_borrowed_range.html", cr="ranges/borrowed_range")
Q(RG + "enable_view.md", "std::ranges::enable_view", "自分の型を view として扱ってよいと宣言する変数テンプレート。", "rare", ["ranges", "print", "string_view", "vector"],
  "view は「コピー・ムーブが軽い範囲」です。ただし C++ はそれを型から自動で判断できません。自作の view には、`view_base` を継承するか、`enable_view<T>` を `true` に特殊化して「これは view です」と宣言します。",
  ["`view_base` か `view_interface` を継承していれば、自動で `true`。", "標準の view は最初から `true`。", "`vector` のような持ち主のコンテナは `false`。"],
  "template <class T>\ninline constexpr bool enable_view = derived_from<T, view_base>;", [("T", "型", "宣言する型")], "view なら `true`",
  'std::println("{}", std::ranges::enable_view<std::string_view>);\nstd::println("{}", std::ranges::enable_view<std::vector<int>>);', "true\nfalse",
  use="自作の view を、標準のパイプで使えるようにする", miss=("コンテナに `true` を指定する", "view はコピーが軽いことを前提にしています。コンテナに指定すると、不要なコピーが起きます。"),
  sim=[("[`view_interface`](view_interface.md)", "view の土台"), ("[`range`](range.md)", "範囲")], cx="コンパイル時のみ", ver=V20, info=RGI, rj="ranges/enable_view.html", cr="ranges/view")
Q(RG + "view_interface.md", "std::ranges::view_interface", "begin と end だけ書けば、empty() や front() などを足してくれる view の土台。", "rare", ["ranges", "print"],
  "自作の view を作るとき、`begin()` と `end()` のほかに `empty()`・`front()`・`size()`・`operator[]` を全部書くのは大変です。`view_interface<Derived>` を継承（CRTP）すると、`begin` / `end` から、使える関数を自動で足してくれます。",
  ["`class MyView : public std::ranges::view_interface<MyView>` と書く。", "`empty`・`front`・`back`・`size`・`operator[]`・`data` などが、条件に応じて使える。", "コピーが軽く、既定構築できる型にする。"],
  "template <class Derived>\nrequires is_class_v<Derived> && same_as<Derived, remove_cv_t<Derived>>\nclass view_interface : public view_base;", [("Derived", "型", "継承するクラス自身")], "`empty()` などの関数が `Derived` に足される",
  'struct IntView : std::ranges::view_interface<IntView> {\n  const int* b = nullptr;\n  const int* e = nullptr;\n  IntView() = default;\n  IntView(const int* b, const int* e) : b(b), e(e) {}\n  const int* begin() const { return b; }\n  const int* end() const { return e; }\n};\n\nint a[] = {3, 4, 5};\nIntView v(a, a + 3);\nstd::println("{} {}", v.front(), v.size());', "3 3",
  use="自作の view を最小限のコードで作る", miss=("既定構築できない型にする", "view は既定構築できる必要があります。`= default` のコンストラクタを書きます。"),
  sim=[("[`enable_view`](enable_view.md)", "view と宣言する")], cx="コンパイル時のみ", ver=V20, info=RGI, rj="ranges/view_interface.html", cr="ranges/view_interface",
  pre="")
Q(RG + "all_t.md", "std::views::all_t", "views::all が返す view の型。", "rare", ["ranges", "type_traits", "vector", "print"],
  "`views::all(r)` は、範囲 `r` を view として包みます。包んだ後の型を知りたいときは、`all_t<R>` が使えます。左辺値のコンテナなら `ref_view<R>`、右辺値のコンテナなら `owning_view<R>` になります。",
  ["`views::all_t<R>` = `decltype(views::all(declval<R>()))`。", "左辺値の範囲は `ref_view`、右辺値の範囲は `owning_view`、view はそのまま。", "テンプレートで、view の型を持つメンバを作るときに使う。"],
  "template <viewable_range R>\nusing views::all_t = decltype(views::all(declval<R>()));", [("R", "型", "包む範囲の型")], "包んだ view の型", 'using V = std::views::all_t<std::vector<int>&>;\nstd::println("{}", std::is_same_v<V, std::ranges::ref_view<std::vector<int>>>);', "true",
  use="view をメンバ変数に持つクラスを書く", miss=("右辺値を渡して `ref_view` になると思う", "右辺値のコンテナは `owning_view` になります。"),
  sim=[("[`views::all`](../../algorithms/views/all.md)", "view に包む関数")], cx="コンパイル時のみ", ver=V20, info=RGI, rj="ranges/all_t.html", cr="ranges/all_view")
Q(RG + "range_adaptor_closure.md", "std::ranges::range_adaptor_closure", "自作のパイプ対応アダプタを作るための土台。", "rare", ["ranges", "print", "vector"],
  "`v | views::reverse` のようなパイプは、標準の view だけが使えるのではありません。`range_adaptor_closure<T>` を継承した自作の関数オブジェクトにも使えます。`v | sum` のように、自作の関数をパイプでつなげられます。",
  ["`struct Sum : std::ranges::range_adaptor_closure<Sum> {...}` と継承する。", "`operator()(Range&&)` を定義すると、`範囲 | Sum{}` が呼べる。", "C++23 の機能（C++20 では実装定義の仕組みで自作しづらい）。"],
  "template <class D>\nrequires is_class_v<D> && same_as<D, remove_cv_t<D>>\nclass range_adaptor_closure;", [("D", "型", "継承するクラス自身")], "`range | D{}` を `D{}(range)` として呼べるようにする",
  'struct Sum : std::ranges::range_adaptor_closure<Sum> {\n  template <std::ranges::range R>\n  int operator()(R&& r) const {\n    int s = 0;\n    for (int x : r) s += x;\n    return s;\n  }\n};\n\nstd::vector<int> v = {1, 2, 3};\nstd::println("{}", v | Sum{});', "6",
  use="自作の変換をパイプでつなぐ", miss=("引数を範囲にしない", "`operator()` の引数は範囲 1 つです。ほかの引数はコンストラクタで受けます。"),
  sim=[("[`views::transform`](../../algorithms/views/transform.md)", "標準のアダプタ")], cx="コンパイル時のみ", ver=("23", "C++23"), info=RGI, rj="ranges/range_adaptor_closure.html", cr="ranges/range_adaptor_closure")
Q(RG + "from_range.md", "std::from_range", "コンテナのコンストラクタに「範囲から作る」と伝える目印。", "rare", ["ranges", "print", "vector"],
  "`std::vector<int> v(first, last)` は、イテレータを 2 つ渡す必要があります。範囲（`views::iota(1, 4)` のような）をそのまま渡したいときは、先頭に `std::from_range` を置いて `v(std::from_range, range)` と書きます。",
  ["コンテナのコンストラクタ、`assign_range`・`insert_range`・`append_range` などで使う。", "範囲を直接渡せるので、イテレータのペアを作らなくてよい。", "C++23 で追加された。"],
  "struct from_range_t { explicit from_range_t() = default; };\ninline constexpr from_range_t from_range{};", [], "なし（目印）",
  'std::vector<int> v(std::from_range, std::views::iota(1, 4));\nstd::println("{}", v);', "[1, 2, 3]",
  use="view の結果をそのままコンテナにする", miss=("目印を忘れる", "`vector(range)` のように範囲だけを渡すとコンパイルエラーです。`std::from_range` が必要です。"),
  sim=[("[`ranges::to`](../../algorithms/ranges_to.md)", "範囲をコンテナに変換する")], cx="コンストラクタに依存", ver=("23", "C++23"), info=RGI, rj="ranges/from_range.html", cr="ranges/from_range_t")
Q(RG + "to_input.md", "std::views::to_input", "範囲を、入力範囲（1 回だけ読める）として見せる view。", "rare", ["ranges", "print", "vector"],
  "テストなどで、「この処理は、範囲を 1 回しか読まない」と保証したいことがあります。`views::to_input` は、元の範囲が何であっても、入力範囲（1 回しか読めない）として見せます。",
  ["元が `vector` でも、入力範囲に弱められる。", "ジェネリックなアルゴリズムが、入力範囲でも動くかの確認に使える。", "C++26 の機能。"],
  "constexpr auto views::to_input;  // 範囲アダプタ", [], "`to_input_view`",
  'std::vector<int> v = {1, 2, 3};\nauto in = v | std::views::to_input;\nstd::println("{}", std::ranges::forward_range<decltype(in)>);', "false",
  use="入力範囲でも動くコードをテストする", miss=("2 回読む", "入力範囲は 1 回しか読めません。"),
  sim=[("[`input_range`](input_range.md)", "入力範囲のコンセプト")], cx="定数", ver=("26", "C++26"), info=RGI, rj="ranges/to_input_view.html", cr="ranges/to_input_view", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")

# ================= iterator =================
IT = "support/iterator/"
ITI = "[イテレータ](@/basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。"


def I(name, summary, intro, sig, args, ret, body, out, use, miss, sim, extra_inc=(), ver=None, tips=None, rank="rare", cr=None, pre=""):
    Q(IT + name + ".md", "std::" + name, summary, rank, ["iterator", "print", *extra_inc], intro,
      tips or ["`<iterator>` の部品。", "ふつうは補助関数（`back_inserter` など）経由で使う。", "アルゴリズムの出力先や入力元に渡す。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx="定数", ver=ver, info=ITI, hub="support/iterator.md", hubname="<iterator>", rj=f"iterator/{name}.html", cr=f"iterator/{cr or name}", pre=pre)


I("iterator_traits", "イテレータの性質（要素の型、種類など）を取り出す。", "自作のアルゴリズムで、渡されたイテレータが指す要素の型や、前後に進めるかを知りたいことがあります。`iterator_traits<It>` は、`value_type`・`difference_type`・`iterator_category` などを取り出す統一の入り口です。生ポインタにも使えます。",
  "template <class It>\nstruct iterator_traits {\n  using difference_type = /* 差の型 */;\n  using value_type = /* 要素の型 */;\n  using pointer = /* ポインタ型 */;\n  using reference = /* 参照型 */;\n  using iterator_category = /* 種類 */;\n};", [("It", "型", "調べるイテレータの型")], "型メンバ",
  'using It = std::vector<int>::iterator;\nstd::println("{}", std::is_same_v<std::iterator_traits<It>::value_type, int>);\nstd::println("{}", std::is_same_v<std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>);', "true\ntrue",
  "ジェネリックなアルゴリズムで、要素の型を取り出す", ("C++20 のコードで使い続ける", "C++20 以降は `std::iter_value_t<It>` のほうが、コンセプトとの相性がよく、安全です。"), [("[`iter_value_t`](iter_value_t.md)", "C++20 の取り出し方"), ("[`iterator_category`](input_iterator_tag.md)", "種類のタグ")], extra_inc=["vector", "type_traits", "iterator"], tips=["`value_type`・`difference_type`・`pointer`・`reference`・`iterator_category` を取れる。", "生ポインタ `T*` にも特殊化がある。", "C++20 では `iter_value_t` などが使いやすい。"])
for tag, cat, desc, ex, exout in [
    ("input_iterator_tag", "入力", "1 回だけ読み進められる", "std::istream_iterator<int>", ""),
    ("output_iterator_tag", "出力", "書き込みながら進められる", "std::back_insert_iterator<std::vector<int>>", ""),
    ("forward_iterator_tag", "前方", "何度でも読み返せる（一方向）", "std::forward_list<int>::iterator", ""),
    ("bidirectional_iterator_tag", "双方向", "前後どちらにも進める", "std::list<int>::iterator", ""),
    ("random_access_iterator_tag", "ランダムアクセス", "添字で好きな位置へ飛べる", "std::vector<int>::iterator", ""),
    ("contiguous_iterator_tag", "連続", "メモリ上で連続した要素を指す", "int*", "")]:
    cat_expr = {"contiguous_iterator_tag": "std::iterator_traits<int*>::iterator_concept"}.get(tag, f"std::iterator_traits<{ex}>::iterator_category")
    inc = {"input_iterator_tag": ["iterator", "type_traits"], "output_iterator_tag": ["iterator", "type_traits", "vector"], "forward_iterator_tag": ["iterator", "type_traits", "forward_list"],
           "bidirectional_iterator_tag": ["iterator", "type_traits", "list"], "random_access_iterator_tag": ["iterator", "type_traits", "vector"], "contiguous_iterator_tag": ["iterator", "type_traits"]}[tag]
    I(tag, f"{cat}イテレータ（{desc}）を表すタグの型。", f"アルゴリズムは、渡されたイテレータの能力に合わせて、使う手順を変えます（`advance` が +n と ++ を使い分けるなど）。その能力を型で表した目印が `{tag}` で、{desc}イテレータが持つ性質です。",
      f"struct {tag} {{}};", [], "なし（目印）", f'std::println("{{}}", std::is_same_v<{cat_expr}, std::{tag}>);', "true",
      "自作のアルゴリズムでイテレータの能力ごとに実装を切り替える", ("C++20 のコンセプトを使わない", "C++20 以降は `std::" + tag.replace("_tag", "") + "<It>` のコンセプトのほうが書きやすいです。"),
      [("[`iterator_traits`](iterator_traits.md)", "タグを取り出す")], extra_inc=inc[2:] if False else [], ver=("20", "C++20") if tag == "contiguous_iterator_tag" else None,
      tips=[f"{desc}イテレータの目印。", "`iterator_traits<It>::iterator_category` で取り出す。", "C++20 では `iterator_concept` やコンセプトのほうが細かく表せる。"])
for nm, what, intro, body, out, inc, sim in [
    ("crbegin", "const の逆順イテレータで、末尾の要素を指す。", "逆順に読むだけ（書き換えない）とき、`crbegin(c)` と書くと、const の逆順イテレータが得られます。`c.crbegin()` と同じです。", "std::vector<int> v = {1, 2, 3};\nstd::println(\"{}\", *std::crbegin(v));", "3", ["vector"], [("[`rbegin`](reverse_iterator.md)", "const でない版")]),
    ("crend", "const の逆順イテレータで、先頭の手前を指す。", "`crbegin` と組み合わせて、逆順に読むときの終端を表します。", "std::vector<int> v = {1, 2, 3};\nint n = 0;\nfor (auto it = std::crbegin(v); it != std::crend(v); ++it) ++n;\nstd::println(\"{}\", n);", "3", ["vector"], [("[`crbegin`](crbegin.md)", "逆順の開始位置")]),
    ("make_reverse_iterator", "イテレータから reverse_iterator を作る。", "`reverse_iterator<It>` は型を書く必要があります。`make_reverse_iterator(it)` なら、型を推論して作ってくれます（C++17 以降は CTAD でも書けます）。", "std::vector<int> v = {1, 2, 3};\nauto r = std::make_reverse_iterator(v.end());\nstd::println(\"{}\", *r);", "3", ["vector"], [("[`reverse_iterator`](reverse_iterator.md)", "逆順イテレータの型")])]:
    I(nm, what, intro, f"auto {nm}(/* ... */);", [("c / it", "コンテナ / イテレータ", "対象")], what.rstrip("。"), body, out, "逆順に走査する", ("`end()` の指す先を読む", "`make_reverse_iterator(end)` は、`end()` の 1 つ手前の要素を指します。`end()` そのものは読めません。" if nm == "make_reverse_iterator" else "空のコンテナで `*crbegin` を読むと未定義動作です。"), sim, extra_inc=inc,
      ver=("14", "C++14") if nm in ("crbegin", "crend") else None)
I("move_sentinel", "move_iterator と組み合わせる、ムーブ用の終端。", "範囲の終端が別の型（sentinel）のとき、`move_iterator` とそろえた終端として `move_sentinel` を使います。ふつうは `ranges::copy` などの C++20 のアルゴリズムに、`move_iterator` と一緒に渡します。",
  "template <semiregular S>\nclass move_sentinel;", [("S", "型", "元の終端の型")], "ムーブ用の終端として比較に使う",
  'std::vector<std::string> src = {"aaaaaaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbbbbbb"};\nstd::vector<std::string> dst;\nstd::ranges::copy(std::move_iterator(src.begin()), std::move_sentinel(src.end()), std::back_inserter(dst));\nstd::println("{}", dst.size());', "2",
  "範囲の中身を別の場所へムーブする", ("コピーだと思う", "`move_iterator` 経由では要素はムーブされ、元は空になるかもしれません。"), [("[`move_iterator`](move_iterator.md)", "ムーブ用イテレータ")], extra_inc=["vector", "string", "algorithm"], ver=("20", "C++20"))
I("back_insert_iterator", "代入するたびに、コンテナの末尾へ push_back するイテレータ。", "`back_inserter(c)` が返す型の正体です。`*it = x` と代入するたびに `c.push_back(x)` が呼ばれます。出力先の大きさを気にせず、結果を `vector` に積み上げられます。",
  "template <class Container>\nclass back_insert_iterator;", [("Container", "型", "`push_back` をもつコンテナ")], "代入で `push_back` する",
  'std::vector<int> v;\nstd::back_insert_iterator<std::vector<int>> it(v);\n*it = 1;\n++it;\n*it = 2;\nstd::println("{}", v);', "[1, 2]",
  "アルゴリズムの結果を `vector` に積む", ("`vector` の末尾以外に挿したい", "末尾に追加するだけです。位置を指定するなら `insert_iterator` です。"), [("[`back_inserter`](back_inserter.md)", "作る関数"), ("[`front_insert_iterator`](front_insert_iterator.md)", "先頭に挿す")], extra_inc=["vector"])
I("front_insert_iterator", "代入するたびに、コンテナの先頭へ push_front するイテレータ。", "`front_inserter(c)` が返す型の正体です。`*it = x` と代入するたびに `c.push_front(x)` が呼ばれます。`deque` や `list` で使えます。",
  "template <class Container>\nclass front_insert_iterator;", [("Container", "型", "`push_front` をもつコンテナ")], "代入で `push_front` する",
  'std::deque<int> d;\nstd::front_insert_iterator<std::deque<int>> it(d);\n*it = 1;\n++it;\n*it = 2;\nstd::println("{}", d);', "[2, 1]",
  "逆順に積み上げる", ("`vector` に使う", "`vector` には `push_front` がありません。`deque` や `list` を使います。"), [("[`front_inserter`](front_inserter.md)", "作る関数"), ("[`back_insert_iterator`](back_insert_iterator.md)", "末尾に追加する")], extra_inc=["deque"])
I("insert_iterator", "代入するたびに、コンテナの指定位置へ insert するイテレータ。", "`inserter(c, pos)` が返す型の正体です。`*it = x` と代入するたびに `c.insert(pos, x)` が呼ばれ、位置は挿入した要素の次に進みます。連続して挿すと、順番を保ったまま入ります。",
  "template <class Container>\nclass insert_iterator;", [("Container", "型", "`insert` をもつコンテナ")], "代入で `insert` する",
  'std::vector<int> v = {1, 4};\nstd::insert_iterator<std::vector<int>> it(v, v.begin() + 1);\n*it = 2;\n*it = 3;\nstd::println("{}", v);', "[1, 2, 3, 4]",
  "`set` や `vector` の途中に、順番に挿す", ("毎回 `insert` で `vector` の途中に挿す", "`vector` の途中への挿入は、後ろの要素を全部ずらします。大量に挿すなら別の方法を検討します。"), [("[`inserter`](inserter.md)", "作る関数")], extra_inc=["vector"])
I("istreambuf_iterator", "ストリームバッファから、1 文字ずつ生で読むイテレータ。", "`istream_iterator<char>` は空白をスキップしてしまいます。`istreambuf_iterator` は、書式を無視して、バッファから 1 文字ずつそのまま読みます。ファイルの全体を `std::string` に読むときに使われます。",
  "template <class CharT, class Traits = char_traits<CharT>>\nclass istreambuf_iterator;", [("CharT", "型", "文字の型")], "`*it` で 1 文字",
  'std::istringstream in("a b");\nstd::string s{std::istreambuf_iterator<char>(in), {}};\nstd::println("{}", s);', "a b",
  "ファイルを丸ごと文字列に読み込む", ("`istream_iterator<char>` で空白が消える", "`istream_iterator` は空白を読み飛ばします。空白を残したいときは `istreambuf_iterator` を使います。"), [("[`istream_iterator`](istream_iterator.md)", "書式つきで読む")], extra_inc=["sstream", "string"])
I("ostreambuf_iterator", "ストリームバッファへ、1 文字ずつ生で書くイテレータ。", "`ostream_iterator` は区切り文字を付けて書式つきで出力します。`ostreambuf_iterator` は、書式なしで 1 文字ずつ書きます。速く、余計な処理がありません。",
  "template <class CharT, class Traits = char_traits<CharT>>\nclass ostreambuf_iterator;", [("CharT", "型", "文字の型")], "代入で 1 文字書く",
  'std::ostringstream out;\nstd::ostreambuf_iterator<char> it(out);\n*it++ = \'h\';\n*it++ = \'i\';\nstd::println("{}", out.str());', "hi",
  "アルゴリズムの結果を文字列ストリームへ出す", ("区切り文字を期待する", "区切りは付きません。必要なら自分で書きます。"), [("[`ostream_iterator`](ostream_iterator.md)", "区切りつきで書く")], extra_inc=["sstream"])
I("counted_iterator", "残りの個数を数えながら進むイテレータ。", "「先頭から n 個だけ」を処理したいとき、`take` のような view を使わなくても、`counted_iterator` で個数つきのイテレータにできます。残りが 0 になると、`default_sentinel` と等しくなります。",
  "template <input_or_output_iterator It>\nclass counted_iterator;", [("It", "型", "元のイテレータ")], "`count()` で残りの個数",
  'std::vector<int> v = {1, 2, 3};\nstd::vector<int> out;\nstd::ranges::copy(std::counted_iterator(v.begin(), 2), std::default_sentinel, std::back_inserter(out));\nstd::println("{}", out);', "[1, 2]",
  "先頭から n 個だけ処理する", ("n を要素数より大きくする", "要素数を超えると範囲外を読みます。"), [("[`default_sentinel`](default_sentinel.md)", "終端"), ("[`views::counted`](../../algorithms/views/counted.md)", "view 版")], extra_inc=["vector", "algorithm"], ver=("20", "C++20"))
I("default_sentinel", "counted_iterator などの終端を表す目印の定数。", "終端のイテレータを別に用意しなくても、「数え終わった」ことを `default_sentinel` と比べて知らせる仕組みです。`counted_iterator` が終わりかを調べるときに使います。",
  "struct default_sentinel_t {};\ninline constexpr default_sentinel_t default_sentinel{};", [], "なし（目印）",
  'std::vector<int> v = {1, 2, 3};\nint sum = 0;\nfor (std::counted_iterator it(v.begin(), 2); it != std::default_sentinel; ++it) {\n  sum += *it;\n}\nstd::println("{}", sum);', "3",
  "個数で止まるループ", ("普通のイテレータと比べる", "`default_sentinel` と比べられるのは、対応するイテレータ（`counted_iterator` など）だけです。"), [("[`counted_iterator`](counted_iterator.md)", "これと使う")], extra_inc=["vector"], ver=("20", "C++20"))
I("unreachable_sentinel", "「終わりには絶対に届かない」と約束する終端。", "必ず見つかると分かっている検索では、終端の比較が不要です。`unreachable_sentinel` を終端に渡すと、「この範囲は終わらない」とコンパイラに伝え、終端の比較が省かれます。見つからないと範囲外を読みます。",
  "struct unreachable_sentinel_t {};\ninline constexpr unreachable_sentinel_t unreachable_sentinel{};", [], "なし（目印）",
  'std::vector<int> v = {1, 2, 3};\nauto it = std::ranges::find(v.begin(), std::unreachable_sentinel, 3);\nstd::println("{}", *it);', "3",
  "必ず見つかる検索を、終端の比較なしで速くする", ("見つからないかもしれない検索に使う", "見つからないと、範囲外へ読み進めて未定義動作になります。必ず存在する場合だけに使います。"), [("[`views::iota`](../../algorithms/views/iota.md)", "終わりのない範囲"), ("[`default_sentinel`](default_sentinel.md)", "個数が決まった終端")], extra_inc=["vector", "algorithm"], ver=("20", "C++20"))
I("common_iterator", "イテレータと sentinel（終端）を、1 つの型にまとめる。", "C++20 の範囲は、`begin` と `end` が別の型のことがあります。古いアルゴリズムは、同じ型の組を要求します。`common_iterator<It, Sent>` は、2 つの型を 1 つにまとめて、古いアルゴリズムに渡せるようにします。",
  "template <input_or_output_iterator It, sentinel_for<It> Sent>\nclass common_iterator;", [("It", "型", "イテレータの型"), ("Sent", "型", "終端の型")], "どちらにもなれるイテレータ",
  'std::vector<int> v = {1, 2, 3};\nusing CI = std::common_iterator<std::counted_iterator<std::vector<int>::iterator>, std::default_sentinel_t>;\nstd::vector<int> out(CI(std::counted_iterator(v.begin(), 2)), CI(std::default_sentinel));\nstd::println("{}", out);', "[1, 2]",
  "古いアルゴリズムに C++20 の範囲を渡す", ("`views::common` で足りる場面", "view なら [`views::common`](../../algorithms/views/common.md) で包むほうが簡単です。"), [("[`views::common`](../../algorithms/views/common.md)", "view を common にする")], extra_inc=["vector"], ver=("20", "C++20"))
I("basic_const_iterator", "要素を const として見せるイテレータのアダプタ。", "読み取り専用でしか使わないイテレータを、「書き換えない」型で保証したいことがあります。`basic_const_iterator<It>` は、`*it` が必ず const 参照になるように包みます。",
  "template <input_iterator It>\nclass basic_const_iterator;", [("It", "型", "元のイテレータ")], "`*it` が const になるイテレータ",
  'std::vector<int> v = {1, 2, 3};\nstd::basic_const_iterator<std::vector<int>::iterator> it(v.begin());\nstd::println("{}", std::is_const_v<std::remove_reference_t<decltype(*it)>>);', "true",
  "読み取り専用で関数に渡す", ("書き換えるつもりで包む", "包むと `*it = x` はできなくなります。"), [("[`make_const_iterator`](make_const_iterator.md)", "作る関数")], extra_inc=["vector", "type_traits"], ver=("23", "C++23"))
I("make_const_iterator", "イテレータを、要素が const として見えるイテレータに変換する。", "`const_iterator` を持たない範囲（`views` など）でも、読み取り専用のイテレータが欲しいことがあります。`make_const_iterator(it)` は、すでに const なら何もせず、そうでなければ `basic_const_iterator` で包みます。",
  "template <input_iterator It>\nconstexpr const_iterator<It> make_const_iterator(It it);", [("it", "イテレータ", "変換するイテレータ")], "要素が const のイテレータ",
  'std::vector<int> v = {1, 2, 3};\nauto it = std::make_const_iterator(v.begin());\nstd::println("{}", std::is_const_v<std::remove_reference_t<decltype(*it)>>);', "true",
  "読み取り専用のイテレータを渡す", ("書き込みに使う", "const になるため、書き込めません。"), [("[`basic_const_iterator`](basic_const_iterator.md)", "実体の型")], extra_inc=["vector", "type_traits"], ver=("23", "C++23"))
I("projected", "プロジェクション（変換）を通した値を、アルゴリズムに見せるための型。", "`ranges::sort(v, comp, proj)` のように、アルゴリズムは「比較の前に値を変換するプロジェクション」を受け取ります。`projected<It, Proj>` は、その変換後の値を、コンセプトの制約で使うための型です。自分で書くことはほとんどなく、自作のアルゴリズムの制約に登場します。",
  "template <indirectly_readable It, indirectly_regular_unary_invocable<It> Proj>\nstruct projected;", [("It", "型", "元のイテレータ"), ("Proj", "型", "プロジェクション")], "プロジェクション後の値の型を表す型",
  '// 自作アルゴリズムの制約の例\n// template <std::input_iterator I, class Proj = std::identity,\n//           std::indirect_strict_weak_order<std::projected<I, Proj>> Comp = std::ranges::less>\n// void MySort(I first, I last, Comp comp = {}, Proj proj = {});', None,
  "自作の ranges アルゴリズムを書くとき", ("制約を手で書く", "標準のアルゴリズムと同じ制約は、`projected` を使うとまとめて書けます。"), [("[`std::identity`](../functional/identity.md)", "何もしないプロジェクション")], ver=("20", "C++20"))
for nm, expr, exp_, what in [
    ("iter_value_t", "std::iter_value_t<It>", "int", "イテレータが指す値の型"),
    ("iter_reference_t", "std::iter_reference_t<It>", "int&", "イテレータの `*it` の型（参照）"),
    ("iter_difference_t", "std::iter_difference_t<It>", "std::ptrdiff_t", "イテレータの差の型")]:
    I(nm, f"{what}を取り出す型の別名。", f"テンプレートの中で、イテレータ型 `It` が指す値の型を知りたいとき、`iterator_traits<It>::value_type` と書くと長くなります。`{nm}<It>` は、C++20 のコンセプトと相性のよい書き方です。",
      f"template <class It>\nusing {nm} = /* {what} */;", [("It", "型", "イテレータの型")], what, f'using It = std::vector<int>::iterator;\nstd::println("{{}}", std::is_same_v<{expr}, {exp_}>);', "true",
      "ジェネリックなアルゴリズムで、値の型を取り出す", ("`iterator_traits` と混ぜる", "C++20 のコードでは、`iter_value_t` などに統一したほうが読みやすいです。"), [("[`iterator_traits`](iterator_traits.md)", "従来の取り出し方")], extra_inc=["vector", "type_traits", "cstddef"], ver=("20", "C++20"))
I("iter_move", "イテレータが指す要素を、右辺値として取り出す。", "`std::move(*it)` と書くと、プロキシ型のイテレータ（`vector<bool>` など）でうまくいかないことがあります。`ranges::iter_move(it)` は、イテレータごとの正しい方法で、要素を右辺値にして返します。",
  "inline constexpr /* カスタマイズポイント */ ranges::iter_move;", [("it", "イテレータ", "要素を指すイテレータ")], "右辺値の参照（または値）",
  'std::vector<int> v = {1, 2, 3};\nstd::println("{}", std::is_rvalue_reference_v<decltype(std::ranges::iter_move(v.begin()))>);', "true",
  "ジェネリックなアルゴリズムで要素をムーブする", ("`std::move(*it)` と書く", "プロキシ型のイテレータでは `std::move(*it)` が正しくありません。`iter_move` を使います。"), [("[`iter_swap`](../../algorithms/iter_swap.md)", "要素を入れ替える")], extra_inc=["vector", "type_traits"], ver=("20", "C++20"))

if __name__ == "__main__":
    flush_hubs()
