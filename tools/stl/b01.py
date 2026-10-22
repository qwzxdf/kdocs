"""バッチ 1: algorithm / numeric の未登録分。"""
from mk import *  # noqa: F401,F403

A = "algorithms/"
H = None
IT = "[イテレータ](@/basics/iterator.md) が分かると読みやすいです。"

P(A + "replace_copy_if.md", "std::replace_copy_if", "条件に合う要素だけ置き換えながら、別の場所へコピーする。", "rare", "algorithm",
  "元のデータは残したまま、「条件に合うものだけ別の値に置き換えた結果」がほしいことがあります。`replace_if` は元の列を書き換えてしまうので、コピーしながら置き換える `replace_copy_if` を使います。",
  ["元の列は変わらない。出力先は別に用意する。", "条件は関数（ラムダ）で渡す。値で決めるなら [`replace_copy`](replace_copy.md)。"],
  [("負の値を 0 にした配列を作る", "`std::replace_copy_if(src.begin(), src.end(), dst.begin(), [](int x){ return x < 0; }, 0);`")],
  ("出力先の大きさが足りない", "出力先に `dst.begin()` を渡すだけでは領域は増えません。あらかじめ同じ大きさにするか、`std::back_inserter(dst)` を渡します。"),
  [("[`replace_copy`](replace_copy.md)", "値で比べる版"), ("[`replace_if`](replace.md)", "その場で書き換える版"), ("[`copy_if`](copy.md)", "条件に合うものだけ取り出す")],
  ["条件に合う要素を置き換えながらコピーする", "元の列は変わらない", "出力先は別に用意する"],
  sig="template <class InputIt, class OutputIt, class Pred, class T>\nOutputIt replace_copy_if(InputIt first, InputIt last, OutputIt d_first, Pred pred, const T& new_value);",
  args=[("first, last", "イテレータ", "元の範囲"), ("d_first", "イテレータ", "コピー先の先頭"), ("pred", "述語", "`true` を返した要素を置き換える"), ("new_value", "T", "置き換える値")],
  ret="コピー先の最後の次のイテレータ", cx="線形（`last - first` 回、`pred` を呼ぶ）",
  code="""#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {3, -1, 4, -5, 9};
  std::vector<int> dst(src.size());
  // 負の値を 0 に置き換えてコピーする
  std::replace_copy_if(src.begin(), src.end(), dst.begin(),
                       [](int x) { return x < 0; }, 0);
  std::println("{}", src);
  std::println("{}", dst);
}""", out="[3, -1, 4, -5, 9]\n[3, 0, 4, 0, 9]", info=IT, rj="algorithm/replace_copy_if.html", cr="algorithm/replace_copy")

P(A + "lexicographical_compare_three_way.md", "std::lexicographical_compare_three_way", "2 つの範囲を辞書順に比べて、順序（strong_ordering など）を返す。", "rare", "algorithm",
  "辞書順の比較は `lexicographical_compare` で「小さいかどうか」が分かります。でも「等しい」「大きい」まで 1 回で知りたいときは、3 通りを返す `lexicographical_compare_three_way` が使えます。`<=>`（宇宙船演算子）の範囲版です。",
  ["戻り値は `std::strong_ordering` などの順序型（`<` `==` `>` と 0 を比べて使う）。", "要素の比較は `<=>` が使われる。"],
  [("バージョン番号の大小を 3 通りで判定", "`std::lexicographical_compare_three_way(a.begin(), a.end(), b.begin(), b.end()) < 0`")],
  ("順序型を整数と思う", "戻り値は `int` ではなく `std::strong_ordering` です。`0` との比較（`== 0`、`< 0`）だけが書けます。"),
  [("[`lexicographical_compare`](lexicographical_compare.md)", "小さいかどうかの `bool` だけ返す"), ("[`equal`](equal.md)", "等しいかどうかだけ")],
  ["範囲の辞書順比較を `<=>` で行う", "戻り値は順序型", "0 と比べて使う"],
  sig="template <class InputIt1, class InputIt2>\nauto lexicographical_compare_three_way(InputIt1 first1, InputIt1 last1, InputIt2 first2, InputIt2 last2);",
  args=[("first1, last1", "イテレータ", "1 つ目の範囲"), ("first2, last2", "イテレータ", "2 つ目の範囲"), ("comp", "関数", "省略可。要素を比べる関数（順序型を返す）")],
  ret="順序型（`std::strong_ordering` など）。1 つ目が小さければ負、等しければ 0、大きければ正と比べられる", cx="線形（最大でも短いほうの長さの回数だけ比較）",
  code="""#include <algorithm>
#include <compare>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3};
  std::vector<int> b = {1, 2, 4};
  auto r = std::lexicographical_compare_three_way(a.begin(), a.end(), b.begin(), b.end());
  std::println("a < b: {}", r < 0);
  std::println("a == b: {}", r == 0);
}""", out="a < b: true\na == b: false", ver=("20", "C++20"), info=IT, rj="algorithm/lexicographical_compare_three_way.html", cr="algorithm/lexicographical_compare_three_way")

P(A + "fold_right_last.md", "std::ranges::fold_right_last", "初期値なしで、範囲を右から畳み込む。", "rare", "algorithm",
  "合計や最大値のように、列を 1 つの値にまとめたいとき、初期値を別に用意するのが面倒なことがあります。`fold_right_last` は最後の要素を初期値にして右から畳み込みます。空の範囲では何も返せないので、戻り値は `optional` です。",
  ["初期値の代わりに最後の要素を使う。", "戻り値は `std::optional`。空なら `nullopt`。", "左から畳むのは [`fold_left_first`](fold_left.md)。"],
  [("リストの要素を右結合で 1 つにまとめる", "`std::ranges::fold_right_last(v, std::plus<>{})`")],
  ("空の範囲に `.value()` を呼ぶ", "空の範囲だと `nullopt` が返ります。`*r` や `.value()` を呼ぶ前に、値があるか確かめます。"),
  [("[`fold_right`](fold_right.md)", "初期値を渡す版"), ("[`fold_left_first`](fold_left.md)", "左から畳む版")],
  ["最後の要素を初期値にして右から畳む", "戻り値は optional", "空なら nullopt"],
  sig="template <ranges::bidirectional_range R, class F>\nconstexpr auto ranges::fold_right_last(R&& r, F f);",
  args=[("r", "範囲", "畳み込む範囲（双方向以上）"), ("f", "関数", "2 引数の関数。`f(要素, 累積値)` の形で呼ばれる")],
  ret="`std::optional<T>`（空の範囲なら `nullopt`）", cx="線形（`f` を `size - 1` 回呼ぶ）",
  code="""#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto sum = std::ranges::fold_right_last(v, std::plus<>{});
  std::println("{}", *sum);
  std::vector<int> empty;
  std::println("{}", std::ranges::fold_right_last(empty, std::plus<>{}).has_value());
}""", out="10\nfalse", ver=("23", "C++23"), info=IT, rj="algorithm/ranges_fold_right_last.html", cr="algorithm/ranges/fold_right_last")

P(A + "fold_left_with_iter.md", "std::ranges::fold_left_with_iter", "左から畳み込み、結果と「どこまで読んだか」の両方を返す。", "rare", "algorithm",
  "`fold_left` は結果の値だけ返します。入力がイテレータのペア（ストリームなど）のときは、「どこまで読み進めたか」も知りたくなります。`fold_left_with_iter` は、結果と終端イテレータを一緒に返します。",
  ["戻り値は `{in, value}` の組（構造化束縛で受けると読みやすい）。", "初期値なしの版は [`fold_left_first_with_iter`](fold_left_first_with_iter.md)。"],
  [("入力ストリームを合計しつつ、読んだ位置も使う", "`auto [it, sum] = std::ranges::fold_left_with_iter(v, 0, std::plus<>{});`")],
  ("戻り値を 1 つの値と思う", "結果は 2 つの要素をもつ構造体です。値だけ欲しいなら `fold_left` を使います。"),
  [("[`fold_left`](fold_left.md)", "結果の値だけ返す版"), ("[`fold_left_first_with_iter`](fold_left_first_with_iter.md)", "初期値なしの版")],
  ["fold_left の結果と終端を両方返す", "構造化束縛で受ける", "初期値は引数で渡す"],
  sig="template <input_iterator I, sentinel_for<I> S, class T, class F>\nconstexpr auto ranges::fold_left_with_iter(I first, S last, T init, F f);\n\ntemplate <input_range R, class T, class F>\nconstexpr auto ranges::fold_left_with_iter(R&& r, T init, F f);",
  args=[("first, last / r", "範囲", "畳み込む範囲"), ("init", "T", "初期値"), ("f", "関数", "`f(累積値, 要素)` の形で呼ばれる")],
  ret="`in`（読み終えた位置のイテレータ）と `value`（結果）をもつ構造体", cx="線形",
  code="""#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto [it, sum] = std::ranges::fold_left_with_iter(v, 0, std::plus<>{});
  std::println("{} {}", sum, it == v.end());
}""", out="10 true", ver=("23", "C++23"), info=IT, rj="algorithm/ranges_fold_left_with_iter.html", cr="algorithm/ranges/fold_left_with_iter")

P(A + "fold_left_first_with_iter.md", "std::ranges::fold_left_first_with_iter", "初期値なしで左から畳み込み、結果と読んだ位置を返す。", "rare", "algorithm",
  "`fold_left_with_iter` の、初期値なし版です。先頭の要素を初期値にします。空の範囲では結果が `nullopt` になります。",
  ["先頭の要素を初期値にする。", "結果は `optional`。終端イテレータと一緒に返る。"],
  [("先頭を初期値にして合計し、読み終えた位置も使う", "`auto [it, r] = std::ranges::fold_left_first_with_iter(v, std::plus<>{});`")],
  ("空の範囲で値を取り出す", "`r` が `nullopt` のことがあります。`if (r)` で確かめてから使います。"),
  [("[`fold_left_with_iter`](fold_left_with_iter.md)", "初期値を渡す版"), ("[`fold_left_first`](fold_left.md)", "結果だけ返す版")],
  ["初期値なしで左から畳む", "結果は optional", "終端も返る"],
  sig="template <input_iterator I, sentinel_for<I> S, class F>\nconstexpr auto ranges::fold_left_first_with_iter(I first, S last, F f);\n\ntemplate <input_range R, class F>\nconstexpr auto ranges::fold_left_first_with_iter(R&& r, F f);",
  args=[("first, last / r", "範囲", "畳み込む範囲"), ("f", "関数", "`f(累積値, 要素)` の形で呼ばれる")],
  ret="`in`（読み終えた位置）と `value`（`std::optional<T>`）をもつ構造体", cx="線形",
  code="""#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {5, 1, 2};
  auto [it, r] = std::ranges::fold_left_first_with_iter(v, std::plus<>{});
  std::println("{} {}", *r, it == v.end());
}""", out="8 true", ver=("23", "C++23"), info=IT, rj="algorithm/ranges_fold_left_first_with_iter.html", cr="algorithm/ranges/fold_left_first_with_iter")

P("algorithms/transform_inclusive_scan.md", "std::transform_inclusive_scan", "各要素を変換してから、先頭からの累積を作る（その位置を含む）。", "rare", "numeric",
  "累積和を作る前に、各要素を何か変換したいことがあります（たとえば 2 乗してから足す）。`inclusive_scan` の前に `transform` を挟むと 2 回走査しますが、`transform_inclusive_scan` なら 1 回で済みます。",
  ["変換関数と結合関数の 2 つを渡す。", "その位置を含む累積は inclusive、含まないのは [`transform_exclusive_scan`](transform_exclusive_scan.md)。", "実行ポリシーを付けると並列に動く。"],
  [("2 乗和の累積を作る", "`std::transform_inclusive_scan(v.begin(), v.end(), out.begin(), std::plus<>{}, [](int x){ return x * x; });`")],
  ("結合関数が結合法則を満たさない", "並列版は順序が不定です。引き算のような結合法則を満たさない演算は結果が不定になります。"),
  [("[`inclusive_scan`](inclusive_scan.md)", "変換なしの版"), ("[`transform_exclusive_scan`](transform_exclusive_scan.md)", "その位置を含まない版"), ("[`partial_sum`](partial_sum.md)", "順序が固定の古い版")],
  ["変換しながら累積を作る", "その位置を含む", "結合法則を満たす演算で"],
  sig="template <class InputIt, class OutputIt, class BinaryOp, class UnaryOp>\nOutputIt transform_inclusive_scan(InputIt first, InputIt last, OutputIt d_first, BinaryOp binary_op, UnaryOp unary_op);\n\ntemplate <class InputIt, class OutputIt, class BinaryOp, class UnaryOp, class T>\nOutputIt transform_inclusive_scan(InputIt first, InputIt last, OutputIt d_first, BinaryOp binary_op, UnaryOp unary_op, T init);",
  args=[("first, last", "イテレータ", "入力の範囲"), ("d_first", "イテレータ", "出力の先頭"), ("binary_op", "関数", "累積に使う 2 項演算"), ("unary_op", "関数", "各要素に先に適用する変換"), ("init", "T", "省略可。初期値")],
  ret="出力の最後の次のイテレータ", cx="線形",
  code="""#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::vector<int> out(v.size());
  std::transform_inclusive_scan(v.begin(), v.end(), out.begin(), std::plus<>{},
                                [](int x) { return x * x; });
  std::println("{}", out);
}""", out="[1, 5, 14, 30]", ver=("17", "C++17"), info=IT, rj="numeric/transform_inclusive_scan.html", cr="algorithm/transform_inclusive_scan")

P("algorithms/transform_exclusive_scan.md", "std::transform_exclusive_scan", "各要素を変換してから、先頭からの累積を作る（その位置を含まない）。", "rare", "numeric",
  "`transform_inclusive_scan` の、「その位置を含まない」版です。出力の先頭は初期値になり、そこから 1 つ前までの変換後の値の累積が並びます。",
  ["初期値が必須。出力の最初の要素は初期値そのもの。", "含むのは [`transform_inclusive_scan`](transform_inclusive_scan.md)。"],
  [("各オブジェクトが配列のどこから始まるかを求める（サイズ列の累積）", "`std::transform_exclusive_scan(sizes.begin(), sizes.end(), offs.begin(), 0, std::plus<>{}, [](int s){ return s; });`")],
  ("初期値を忘れる", "exclusive 系は初期値が必須です。`inclusive` と違い省略できません。"),
  [("[`exclusive_scan`](exclusive_scan.md)", "変換なしの版"), ("[`transform_inclusive_scan`](transform_inclusive_scan.md)", "その位置を含む版")],
  ["変換しながら累積を作る", "その位置を含まない", "初期値が必須"],
  sig="template <class InputIt, class OutputIt, class T, class BinaryOp, class UnaryOp>\nOutputIt transform_exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init, BinaryOp binary_op, UnaryOp unary_op);",
  args=[("first, last", "イテレータ", "入力の範囲"), ("d_first", "イテレータ", "出力の先頭"), ("init", "T", "初期値"), ("binary_op", "関数", "累積に使う 2 項演算"), ("unary_op", "関数", "各要素に先に適用する変換")],
  ret="出力の最後の次のイテレータ", cx="線形",
  code="""#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::vector<int> out(v.size());
  std::transform_exclusive_scan(v.begin(), v.end(), out.begin(), 0, std::plus<>{},
                                [](int x) { return x * x; });
  std::println("{}", out);
}""", out="[0, 1, 5, 14]", ver=("17", "C++17"), info=IT, rj="numeric/transform_exclusive_scan.html", cr="algorithm/transform_exclusive_scan")

# --- 既存ページへの節の追加（_if / _not の別形）
add_secs("algorithms/find_last.md", fn("std::ranges::find_last_if_not", """template <ranges::forward_range R, class Pred>
constexpr ranges::borrowed_subrange_t<R> ranges::find_last_if_not(R&& r, Pred pred);""",
  [("r", "範囲", "探す範囲"), ("pred", "述語", "`false` を返す要素を探す")],
  "条件に合わない最後の要素から末尾までの `subrange`。見つからなければ空の `subrange`", "線形", None,
  notes="`find_last_if` の逆で、**条件に合わない**最後の要素を探します。「最後に壊れていないものの次」のような探し方に使います。", ver=("23", "C++23"), ids="find_last_if_not"))

if __name__ == "__main__":
    flush_hubs()
