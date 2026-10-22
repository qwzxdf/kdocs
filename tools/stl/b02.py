"""バッチ 2: <functional> の関数オブジェクトと、utility / functional の未登録分。"""
from mk import *  # noqa: F401,F403

F = "support/functional/"
HUB = "support/functional.md"
INFO_F = None  # hub から自動


def functor(name, op, expr, result, hdr, summary, intro, game, mistake, sim, rank="rare", ver=None, tname="int"):
    sig = (f"template <class T = void>\nstruct {name} {{\n  constexpr auto operator()(const T& a, const T& b) const;  // {op}\n}};"
           if op.count("a") and "b" in op else
           f"template <class T = void>\nstruct {name} {{\n  constexpr auto operator()(const T& a) const;  // {op}\n}};")
    P(F + name + ".md", "std::" + name, summary, rank, hdr, intro,
      [f"`std::{name}<>{{}}` と書くと型を推論してくれる（透過版）。", "アルゴリズムの引数に、ラムダを書かずに渡せる。"],
      game, mistake, sim, [f"{op} を関数オブジェクトにしたもの", "型を省略した `std::" + name + "<>{}` が便利", "アルゴリズムにそのまま渡せる"],
      sig=sig, args=[("a", "T", "左辺（1 つ目の値）")] + ([("b", "T", "右辺（2 つ目の値）")] if "b" in op else []),
      ret=f"`{op}` の結果", cx="定数", code=f"""#include <functional>
#include <print>

int main() {{
{expr}
}}""", out=result, hub=HUB, hubname="<functional>", rj=f"functional/{name}.html", cr=f"utility/functional/{name}", ver=ver)


functor("minus", "a - b", '  std::println("{}", std::minus<>{}(10, 3));', "7", "functional",
        "`a - b` を表す関数オブジェクト。", "`-` をアルゴリズムに渡したいとき、ラムダ `[](int a, int b){ return a - b; }` を書くのは冗長です。`std::minus<>{}` なら 1 語で済みます。差を取る `adjacent_difference` や、`fold_left` の演算に使います。",
        [("隣り合う値の差", "`std::adjacent_difference(v.begin(), v.end(), out.begin(), std::minus<>{});`")],
        ("引数の順序を逆に考える", "`minus(a, b)` は `a - b` です。`fold_right` では引数の順が逆になることがあるので、結果を確かめます。"),
        [("[`plus`](plus.md)", "足し算"), ("[`negate`](negate.md)", "符号を反転")])
functor("divides", "a / b", '  std::println("{}", std::divides<>{}(10, 3));', "3", "functional",
        "`a / b` を表す関数オブジェクト。", "割り算を `transform` や `fold` に渡したいとき、`std::divides<>{}` が使えます。整数なら小数点以下は切り捨てです。",
        [("全要素を同じ値で割る", "`std::transform(a.begin(), a.end(), b.begin(), out.begin(), std::divides<>{});`")],
        ("0 で割る", "整数を 0 で割ると未定義動作です。割る側の列に 0 がないことを確かめます。"),
        [("[`multiplies`](multiplies.md)", "かけ算"), ("[`modulus`](modulus.md)", "余り")])
functor("modulus", "a % b", '  std::println("{}", std::modulus<>{}(10, 3));', "1", "functional",
        "`a % b`（余り）を表す関数オブジェクト。", "余りを求める `%` も、関数オブジェクトとして渡せます。ループ再生のインデックスや、均等な振り分けに使う余りを、アルゴリズムの中で計算したいときに便利です。",
        [("インデックスを範囲内に折り返す", "`std::transform(a.begin(), a.end(), b.begin(), out.begin(), std::modulus<>{});`")],
        ("浮動小数点に使う", "`%` は整数専用です。小数の余りは [`std::fmod`](../../numeric/cmath/fmod.md) を使います。"),
        [("[`divides`](divides.md)", "割り算"), ("[`fmod`](../../numeric/cmath/fmod.md)", "小数の余り")])
functor("negate", "-a", '  std::println("{}", std::negate<>{}(5));', "-5", "functional",
        "`-a`（符号の反転）を表す関数オブジェクト。", "全要素の符号を反転したいとき、`transform` に `std::negate<>{}` を渡すと、ラムダなしで書けます。",
        [("速度ベクトルの成分を反転", "`std::transform(v.begin(), v.end(), v.begin(), std::negate<>{});`")],
        ("符号なしの型に使う", "`unsigned` に `negate` を使うと、大きな値にぐるっと回ります。符号つきの型で使います。"),
        [("[`minus`](minus.md)", "引き算")])
functor("not_equal_to", "a != b", '  std::println("{}", std::not_equal_to<>{}(3, 4));', "true", "functional",
        "`a != b` を表す関数オブジェクト。", "「違うものを数える」「違う場所を探す」といった処理で `!=` を渡したいとき、`std::not_equal_to<>{}` が使えます。`mismatch` や `adjacent_find` の述語にもなります。",
        [("2 つの配列で最初に違う位置を探す", "`std::mismatch(a.begin(), a.end(), b.begin(), b.end())`（既定は `==` の否定）。述語を渡すなら `std::equal_to<>{}`")],
        ("`equal_to` と取り違える", "述語の向きを間違えると、探しているものと逆の結果になります。"),
        [("[`equal_to`](equal_to.md)", "`==`")])
functor("greater_equal", "a >= b", '  std::println("{}", std::greater_equal<>{}(3, 3));', "true", "functional",
        "`a >= b` を表す関数オブジェクト。", "「以上」を述語として渡したいとき、`std::greater_equal<>{}` が使えます。`greater` は等しい値を含まないので、含めたいときはこちらです。",
        [("しきい値以上かを判定する述語", "`auto ge = std::bind_front(std::greater_equal<>{}, score);`（`ge(60)` は `score >= 60`）")],
        ("整列の比較に使う", "`sort` の比較関数には使えません。同じ値で `true` を返すと、厳密弱順序の条件を満たさず未定義動作です。`greater` / `less` を使います。"),
        [("[`greater`](greater.md)", "`>`"), ("[`less_equal`](less_equal.md)", "`<=`")])
functor("less_equal", "a <= b", '  std::println("{}", std::less_equal<>{}(4, 3));', "false", "functional",
        "`a <= b` を表す関数オブジェクト。", "「以下」を述語として渡したいときに使います。`less` は等しい値を含まないので、含めたいときはこちらです。",
        [("上限以下かを判定する述語", "`auto le = std::bind_front(std::less_equal<>{}, score);`（`le(100)` は `score <= 100`）")],
        ("整列の比較に使う", "`sort` の比較関数には使えません。同じ値で `true` を返すと未定義動作になります。`less` を使います。"),
        [("[`less`](less.md)", "`<`"), ("[`greater_equal`](greater_equal.md)", "`>=`")])
functor("logical_and", "a && b", '  std::println("{}", std::logical_and<>{}(true, false));', "false", "functional",
        "`a && b` を表す関数オブジェクト。", "「全部が真か」を 1 つの値にまとめたいとき、`&&` を畳み込みの演算として渡せます。ただし関数オブジェクトでは**短絡評価されません**。",
        [("フラグ配列の論理積", "`std::ranges::fold_left(flags, true, std::logical_and<>{});`")],
        ("短絡評価を期待する", "`a && b` は a が偽なら b を評価しませんが、`logical_and` は両方を引数として評価してから呼ばれます。"),
        [("[`logical_or`](logical_or.md)", "`||`"), ("[`all_of`](../../algorithms/all_of.md)", "全部が真か調べる")])
functor("logical_or", "a || b", '  std::println("{}", std::logical_or<>{}(true, false));', "true", "functional",
        "`a || b` を表す関数オブジェクト。", "「どれか 1 つでも真か」を畳み込みで調べたいときに使います。`any_of` のほうが短絡評価されるので、実際には `any_of` が向いています。",
        [("フラグ配列の論理和", "`std::ranges::fold_left(flags, false, std::logical_or<>{});`")],
        ("短絡評価を期待する", "関数オブジェクトでは両方の引数が先に評価されます。途中で止めたいなら `any_of` を使います。"),
        [("[`logical_and`](logical_and.md)", "`&&`"), ("[`any_of`](../../algorithms/any_of.md)", "どれかが真か調べる")])
functor("logical_not", "!a", '  std::println("{}", std::logical_not<>{}(true));', "false", "functional",
        "`!a` を表す関数オブジェクト。", "述語の結果を反転したいとき、`std::not_fn` を使うほか、単純な `!` なら `std::logical_not<>{}` を渡せます。",
        [("フラグを全部反転", "`std::transform(f.begin(), f.end(), f.begin(), std::logical_not<>{});`")],
        ("関数の結果を反転したい", "述語の反転は [`not_fn`](not_fn.md) のほうが向いています。`logical_not` は値の `!` です。"),
        [("[`not_fn`](not_fn.md)", "述語の結果を反転する")])
functor("bit_and", "a & b", '  std::println("{}", std::bit_and<>{}(12, 10));', "8", "functional",
        "`a & b`（ビットごとの AND）を表す関数オブジェクト。", "フラグの共通部分を求めたいとき、`&` を畳み込みに渡せます。複数のフラグ値のうち「全部に立っているビット」を求めるときなどです。",
        [("複数のマスクの共通部分", "`std::ranges::fold_left(masks, ~0u, std::bit_and<>{});`")],
        ("論理 AND と取り違える", "`bit_and` はビット単位、`logical_and` は真偽です。"),
        [("[`bit_or`](bit_or.md)", "`|`"), ("[`bit_xor`](bit_xor.md)", "`^`")])
functor("bit_or", "a | b", '  std::println("{}", std::bit_or<>{}(12, 10));', "14", "functional",
        "`a | b`（ビットごとの OR）を表す関数オブジェクト。", "複数のフラグを 1 つにまとめたいとき、`|` を畳み込みに渡します。",
        [("フラグ値を全部合成", "`std::ranges::fold_left(flags, 0u, std::bit_or<>{});`")],
        ("論理 OR と取り違える", "`bit_or` はビット単位、`logical_or` は真偽です。"),
        [("[`bit_and`](bit_and.md)", "`&`")])
functor("bit_xor", "a ^ b", '  std::println("{}", std::bit_xor<>{}(12, 10));', "6", "functional",
        "`a ^ b`（ビットごとの XOR）を表す関数オブジェクト。", "「違うビットだけ」を取り出したいとき、`^` を渡します。チェックサムの簡易計算や、2 つのフラグ集合の差分の取り出しに使います。",
        [("2 つのフラグ集合の差分", "`std::bit_xor<>{}(old_flags, new_flags)`")],
        ("累乗と取り違える", "C++ の `^` は排他的論理和で、累乗ではありません。累乗は [`pow`](../../numeric/cmath/pow.md) です。"),
        [("[`bit_and`](bit_and.md)", "`&`")])
functor("bit_not", "~a", '  std::println("{}", std::bit_not<>{}(0));', "-1", "functional",
        "`~a`（ビット反転）を表す関数オブジェクト。", "全ビットを反転したいとき、`~` を渡せます。マスクの反転（立っているビットと落ちているビットを入れ替える）に使います。",
        [("マスクを反転して「それ以外」を作る", "`std::bit_not<>{}(mask)`")],
        ("符号付きの型で反転する", "符号付き整数のビット反転は `-x - 1` と同じ値になります。マスク計算は `unsigned` で行います。"),
        [("[`logical_not`](logical_not.md)", "`!`")])

# ---- invoke_r / unwrap_reference / unwrap_ref_decay / placeholders ...
P(F + "invoke_r.md", "std::invoke_r", "呼び出しの結果を、指定した戻り値の型に変換して返す。", "rare", "functional",
  "コールバックの戻り値を、決まった型として受け取りたいことがあります。`std::invoke` の結果を毎回 `static_cast` で包むかわりに、`invoke_r<R>` は戻り値を `R` へ暗黙変換して返します。`R` が `void` なら、結果を捨てます。",
  ["`invoke` と同じく、関数・メンバ関数・メンバ変数を同じ書き方で呼べる。", "戻り値の型を指定できる（`void` なら結果を捨てる）。"],
  [("コールバックの結果を `double` で受ける", "`std::invoke_r<double>(callback, arg);`")],
  ("変換できない型を指定する", "戻り値が `R` に暗黙変換できないとコンパイルエラーになります。"),
  [("[`invoke`](invoke.md)", "戻り値の型はそのまま")],
  ["`invoke` の戻り値の型を指定する版", "`void` なら結果を捨てる", "暗黙変換できる型だけ"],
  sig="template <class R, class F, class... Args>\nconstexpr R invoke_r(F&& f, Args&&... args) noexcept(/* 呼び出しが noexcept なら */);",
  args=[("R", "テンプレート引数", "戻り値の型"), ("f", "呼び出せるもの", "関数・ラムダ・メンバ関数ポインタなど"), ("args...", "引数", "`f` に渡す引数")],
  ret="`f(args...)` の結果を `R` に変換した値", cx="呼ぶ関数に依存",
  code="""#include <functional>
#include <print>

int main() {
  auto f = [](int a, int b) { return a + b; };
  double d = std::invoke_r<double>(f, 1, 2);
  std::println("{}", d);
}""", out="3", ver=("23", "C++23"), hub=HUB, hubname="<functional>", rj="functional/invoke_r.html", cr="utility/functional/invoke")

P(F + "unwrap_reference.md", "std::unwrap_reference", "reference_wrapper を、ふつうの参照の型に戻す型変換。", "rare", "functional",
  "`std::ref(x)` が返す `reference_wrapper<T>` は、テンプレートの中で「中身は `T&`」と扱いたいことがあります。`unwrap_reference<T>` は、`reference_wrapper<U>` なら `U&`、それ以外なら `T` をそのまま返す型変換です。",
  ["`reference_wrapper<U>` を `U&` に直す。", "それ以外の型は変えない。", "`::type` で結果の型を取る。`_t` 版もある。"],
  [("ライブラリの内部で `ref` を解いて保存する", "`std::unwrap_reference_t<std::reference_wrapper<int>>` は `int&`")],
  ("値の `ref` を忘れる", "`std::ref` を渡し忘れると、コピーが保存されて参照になりません。"),
  [("[`unwrap_ref_decay`](unwrap_ref_decay.md)", "decay もしてから解く"), ("[`ref`](ref.md)", "参照のラッパーを作る")],
  ["reference_wrapper を参照に戻す型変換", "それ以外は変えない", "`unwrap_reference_t` で使う"],
  sig="template <class T> struct unwrap_reference;\ntemplate <class T> using unwrap_reference_t = typename unwrap_reference<T>::type;",
  args=[("T", "型", "解きたい型")], ret="`reference_wrapper<U>` なら `U&`、それ以外は `T`", cx="コンパイル時のみ",
  code="""#include <functional>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::unwrap_reference_t<std::reference_wrapper<int>>, int&>);
  std::println("{}", std::is_same_v<std::unwrap_reference_t<int>, int>);
}""", out="true\ntrue", ver=("20", "C++20"), hub=HUB, hubname="<functional>", rj="functional/unwrap_reference.html", cr="utility/functional/unwrap_reference")

P(F + "unwrap_ref_decay.md", "std::unwrap_ref_decay", "decay してから、reference_wrapper を参照に戻す型変換。", "rare", "functional",
  "`std::make_pair` や `make_tuple` は、引数を保存するときに「配列は先頭ポインタへ、const は外す、`reference_wrapper` は参照へ」という型の変換をします。この変換を自分のテンプレートで使うための部品が `unwrap_ref_decay` です。",
  ["`decay_t<T>` を作り、それが `reference_wrapper<U>` なら `U&` にする。", "`make_pair` / `make_tuple` の内部と同じ規則。"],
  [("関数の引数を値で保存するコンテナを作る", "`std::unwrap_ref_decay_t<T>` を保存する型にする")],
  ("decay だけを期待する", "`reference_wrapper` が入っていると参照になります。単なる decay は [`decay`](../type_traits/decay.md) です。"),
  [("[`unwrap_reference`](unwrap_reference.md)", "decay はしない"), ("[`decay`](../type_traits/decay.md)", "decay だけ")],
  ["decay + reference_wrapper の解除", "make_pair と同じ規則", "`_t` 版で使う"],
  sig="template <class T> struct unwrap_ref_decay;\ntemplate <class T> using unwrap_ref_decay_t = typename unwrap_ref_decay<T>::type;",
  args=[("T", "型", "変換したい型")], ret="`decay_t<T>` が `reference_wrapper<U>` なら `U&`、それ以外は `decay_t<T>`", cx="コンパイル時のみ",
  code="""#include <functional>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::unwrap_ref_decay_t<const int&>, int>);
  std::println("{}", std::is_same_v<std::unwrap_ref_decay_t<std::reference_wrapper<int>>, int&>);
}""", out="true\ntrue", ver=("20", "C++20"), hub=HUB, hubname="<functional>", rj="functional/unwrap_ref_decay.html", cr="utility/functional/unwrap_ref_decay")

P(F + "placeholders.md", "std::placeholders", "bind の引数の位置を表す _1, _2, … の名前空間。", "rare", "functional",
  "`std::bind` で「あとから渡す引数」を位置で指定するための印が、`std::placeholders::_1`、`_2`… です。`_1` は呼び出し時の 1 番目の引数、`_2` は 2 番目の引数、という意味です。",
  ["`std::placeholders::_1` から `_N` まで（N は実装依存で 10 以上）。", "名前空間が長いので `using namespace std::placeholders;` を関数の中で使うことが多い。", "新しいコードではラムダか [`bind_front`](bind_front.md) が読みやすい。"],
  [("引数の順を入れ替えた関数を作る", "`auto f = std::bind(g, _2, _1);`")],
  ("`using namespace` を広い範囲に書く", "ヘッダやグローバルに書くと、`_1` などの名前が衝突します。関数の中で書きます。"),
  [("[`bind_front`](bind_front.md)", "前の引数を固定するだけならこちら"), ("[ラムダ式](@/basics/lambda.md)", "読みやすさで勝る")],
  ["bind の引数位置の印", "関数の中で using する", "新しいコードはラムダか bind_front"],
  sig="namespace std::placeholders {\n  inline constexpr /* 実装定義 */ _1, _2, _3 /* ... */;\n}",
  args=[("_1, _2, ...", "プレースホルダー", "呼び出し時の 1 番目、2 番目、... の引数")], ret="なし（`bind` に渡す印）", cx="なし",
  code="""#include <functional>
#include <print>

int Sub(int a, int b) { return a - b; }

int main() {
  using namespace std::placeholders;
  auto f = std::bind(Sub, _2, _1);  // 引数を入れ替える
  std::println("{}", f(10, 3));      // Sub(3, 10)
}""", out="-7", hub=HUB, hubname="<functional>", rj="functional/placeholders.html", cr="utility/functional/placeholders")

P(F + "is_bind_expression.md", "std::is_bind_expression", "型が bind の式かどうかを調べる型特性。", "rare", "functional",
  "`std::bind` に別の `bind` の結果を渡すと、中の `bind` が先に評価されてその結果が使われます（入れ子の bind）。この「bind の式かどうか」を判定する型特性が `is_bind_expression` です。",
  ["`std::bind` の戻り値の型に対して `true`。", "自作のラッパーを bind 式として扱わせたいときに特殊化する。"],
  [("テンプレートで bind の戻り値かを判定", "`std::is_bind_expression_v<decltype(std::bind(f, _1))>`")],
  ("`std::function` と取り違える", "`std::function` は bind 式ではありません。`false` になります。"),
  [("[`is_placeholder`](is_placeholder.md)", "プレースホルダーかを調べる")],
  ["bind 式かどうかの型特性", "`_v` 版で bool", "普通は使わない"],
  sig="template <class T> struct is_bind_expression;\ntemplate <class T> inline constexpr bool is_bind_expression_v = is_bind_expression<T>::value;",
  args=[("T", "型", "調べる型")], ret="`bind` が返した型なら `true`", cx="コンパイル時のみ",
  code="""#include <functional>
#include <print>

int Add(int a, int b) { return a + b; }

int main() {
  auto b = std::bind(Add, std::placeholders::_1, 1);
  std::println("{}", std::is_bind_expression_v<decltype(b)>);
  std::println("{}", std::is_bind_expression_v<int>);
}""", out="true\nfalse", ver=("17", "C++17"), hub=HUB, hubname="<functional>", rj="functional/is_bind_expression.html", cr="utility/functional/is_bind_expression")

P(F + "is_placeholder.md", "std::is_placeholder", "型がプレースホルダー（_1 など）か、何番かを調べる型特性。", "rare", "functional",
  "`bind` の中で `_1` や `_2` を見分ける仕組みが `is_placeholder` です。プレースホルダーなら番号（1, 2, …）、そうでなければ 0 になります。",
  ["`_1` の型なら 1、`_2` なら 2、それ以外は 0。", "自作のプレースホルダーを作るときに特殊化する。"],
  [("テンプレートで引数が `_N` かを判定", "`std::is_placeholder_v<decltype(_2)>`")],
  ("値と型を取り違える", "判定するのは型です。`decltype(_1)` のように型を渡します。"),
  [("[`is_bind_expression`](is_bind_expression.md)", "bind 式かどうか")],
  ["プレースホルダーの番号を返す型特性", "プレースホルダーでなければ 0", "普通は使わない"],
  sig="template <class T> struct is_placeholder;\ntemplate <class T> inline constexpr int is_placeholder_v = is_placeholder<T>::value;",
  args=[("T", "型", "調べる型")], ret="プレースホルダーなら番号、そうでなければ 0", cx="コンパイル時のみ",
  code="""#include <functional>
#include <print>

int main() {
  using namespace std::placeholders;
  std::println("{}", std::is_placeholder_v<decltype(_1)>);
  std::println("{}", std::is_placeholder_v<decltype(_3)>);
  std::println("{}", std::is_placeholder_v<int>);
}""", out="1\n3\n0", ver=("17", "C++17"), hub=HUB, hubname="<functional>", rj="functional/is_placeholder.html", cr="utility/functional/is_placeholder")

P(F + "copyable_function.md", "std::copyable_function", "コピーできる、const や noexcept も指定できる関数のラッパー。", "rare", "functional",
  "`std::function` は const の扱いが曖昧で、`noexcept` や右辺値呼び出しを型で表せません。`std::copyable_function` は、`const` / `noexcept` / 参照修飾を関数シグネチャに書ける、新しいコピー可能な関数ラッパーです。",
  ["シグネチャに `const` や `noexcept` を書ける（`R(Args...) const noexcept`）。", "ムーブ専用でよければ [`move_only_function`](../../utilities/move_only_function.md)。", "`std::function` の置き換え候補。"],
  [("コールバックを const で呼べるようにしてコピーも許す", "`std::copyable_function<void(int) const> cb = ...;`")],
  ("`std::function` と同じ感覚で const を無視する", "`const` つきのシグネチャで宣言すると、呼び出しも const に限られます。呼ぶ関数がそれに合うか確かめます。"),
  [("[`std::function`](../../utilities/function.md)", "従来の版"), ("[`move_only_function`](../../utilities/move_only_function.md)", "ムーブ専用")],
  ["std::function の改良版", "const / noexcept をシグネチャで表せる", "コピー可能"],
  sig="template <class... Sigs> class copyable_function;  // Sigs の例: R(Args...) const noexcept",
  args=[("R(Args...) 修飾", "シグネチャ", "戻り値・引数と、`const` / `noexcept` / `&` / `&&` の修飾")], ret="呼び出し演算子で呼ぶ", cx="呼び出しは間接呼び出し 1 回",
  code="""#include <functional>
#include <print>

int main() {
  std::copyable_function<int(int) const> f = [](int x) { return x * 2; };
  auto g = f;  // コピーできる
  std::println("{} {}", f(3), g(4));
}""", out="6 8", ver=("26", "C++26"), hub=HUB, hubname="<functional>", rj="functional/copyable_function.html", cr="utility/functional/copyable_function", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")

P(F + "function_ref.md", "std::function_ref", "呼び出せるものを借りて参照するだけの、軽い関数ラッパー。", "rare", "functional",
  "関数の引数にコールバックを受けたいとき、`std::function` だとコピーのコストやヒープ確保が気になります。呼び出しの間だけ使えれば十分なら、中身をコピーせず**借りるだけ**の `function_ref` が軽く済みます。",
  ["持ち主にはならない。呼び出し中に元の関数オブジェクトが生きている必要がある。", "関数の引数として受け取る使い方が向く。メンバ変数に保存するのは危険。", "ヒープ確保は起きない。"],
  [("`for_each` 風の自作関数でコールバックを受ける", "`void Each(std::function_ref<void(int)> f);`")],
  ("ラムダの一時オブジェクトを保存する", "`function_ref` は参照なので、元のラムダが消えたあとに呼ぶと未定義動作です。関数の引数としてだけ使います。"),
  [("[`std::function`](../../utilities/function.md)", "持ち主になる（コピーする）"), ("[`move_only_function`](../../utilities/move_only_function.md)", "ムーブ専用の持ち主")],
  ["呼び出せるものを借りる関数ラッパー", "ヒープ確保なし", "保存せずに引数として使う"],
  sig="template <class... Sigs> class function_ref;  // Sigs の例: R(Args...) const noexcept",
  args=[("R(Args...)", "シグネチャ", "戻り値と引数")], ret="呼び出し演算子で呼ぶ", cx="間接呼び出し 1 回",
  code="""#include <functional>
#include <print>

void Each(std::function_ref<void(int)> f) {
  for (int i = 0; i < 3; ++i) f(i);
}

int main() {
  int sum = 0;
  Each([&](int x) { sum += x; });
  std::println("{}", sum);
}""", out="3", ver=("26", "C++26"), hub=HUB, hubname="<functional>", rj="functional/function_ref.html", cr="utility/functional/function_ref", compiler="C++26 の機能です。対応は新しい標準ライブラリに限られます。")

for nm, cls, expl in [
    ("default_searcher", "default_searcher", "標準の `std::search` と同じ、素朴な検索"),
    ("boyer_moore_searcher", "boyer_moore_searcher", "ボイヤー・ムーア法（長いパターン向き）"),
    ("boyer_moore_horspool_searcher", "boyer_moore_horspool_searcher", "ボイヤー・ムーア・ホースプール法（簡略版）")]:
    bm = nm != "default_searcher"
    P(F + nm + ".md", "std::" + nm, {"default_searcher": "`std::search` に渡せる、素朴な部分列検索のオブジェクト。", "boyer_moore_searcher": "長い列の中から部分列を速く探す検索のオブジェクト（ボイヤー・ムーア法）。", "boyer_moore_horspool_searcher": "ボイヤー・ムーア・ホースプール法で部分列を探す検索のオブジェクト。"}[nm], "rare", "functional",
      {"default_searcher": "`std::search(first, last, searcher)` には、探し方を「検索オブジェクト」として渡せます。`default_searcher` は標準の素朴な検索（先頭から順に比べる）をそのまま包んだもので、他の検索オブジェクトと同じ書き方でそろえたいときに使います。",
       "boyer_moore_searcher": "巨大なテキストの中から長いパターンを探すとき、先頭から 1 文字ずつ比べると遅くなります。`boyer_moore_searcher` は、パターンを前処理して「ずらせる幅」を大きくとることで、速く探します。",
       "boyer_moore_horspool_searcher": "ボイヤー・ムーア法の簡略版で、前処理が軽く実装も単純です。平均的にはボイヤー・ムーア法に近い速さで、短めのパターンや前処理を軽くしたいときに向きます。"}[nm],
      ["`std::search(first, last, searcher)` に渡して使う。", "パターンを渡して作り、同じ検索を何度も使い回すと前処理の元が取れる。" if bm else "検索結果は `search` と同じ。", "`<functional>` にある（`<algorithm>` ではない）。"],
      [("ログの長い文字列から特定のパターンを探す", f"`std::search(text.begin(), text.end(), std::{nm}(pat.begin(), pat.end()));`")],
      ("短いテキストで使う" if bm else "探し方を変えたいのに使う", ("前処理のコストがかかるので、短いテキストを 1 回探すだけなら素朴な `std::search` のほうが速いことがあります。" if bm else "素朴な検索そのものです。速くしたいなら `boyer_moore_searcher` を使います。")),
      [("[`search`](../../algorithms/search.md)", "検索オブジェクトを受け取る")],
      [f"{expl}", "`std::search` の第 3 引数に渡す", "同じパターンを何度も探すなら使い回す"],
      sig=f"template <class ForwardIt, class Pred = equal_to<>>\nclass {nm} {{\n public:\n  {nm}(ForwardIt pat_first, ForwardIt pat_last, Pred pred = Pred());\n  template <class It> pair<It, It> operator()(It first, It last) const;\n}};",
      args=[("pat_first, pat_last", "イテレータ", "探したいパターンの範囲"), ("pred", "述語", "省略可。要素を比べる述語")],
      ret="`operator()` は見つかった範囲の `pair`（見つからなければ `{last, last}`）", cx=("平均はテキスト長より小さい（最悪は線形 × パターン長）" if bm else "最悪は (テキスト長) × (パターン長)"),
      code=f"""#include <algorithm>
#include <functional>
#include <print>
#include <string>

int main() {{
  std::string text = "hello world, hello cpp";
  std::string pat = "world";
  auto it = std::search(text.begin(), text.end(),
                        std::{nm}(pat.begin(), pat.end()));
  std::println("{{}}", it - text.begin());
}}""", out="6", ver=("17", "C++17"), hub=HUB, hubname="<functional>", rj=f"functional/{nm}.html", cr=f"utility/functional/{nm}")

if __name__ == "__main__":
    flush_hubs()
