"""バッチ 9: <concepts> / <iterator> のコンセプト / <type_traits> の未登録分。"""
from mk import *  # noqa: F401,F403

CN = "support/concepts/"
CNI = "[コンセプト](@/basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。"
V20 = ("20", "C++20")


def CC(name, summary, intro, req, params, body, out, miss, sim, inc=("concepts",), pre="", rank="rare", tips=None):
    Q(CN + name + ".md", "std::" + name, summary, rank, [*inc, "print"], intro,
      tips or ["コンセプト。`requires` やテンプレートの制約に書く。", f"`std::{name}<...>` は `bool` の定数式。", "満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。"],
      f"template <{', '.join('class ' + p for p in params)}>\nconcept {name} = /* {req} */;", [(p, "型", "調べる型") for p in params], "条件を満たせば `true`（コンパイル時の定数）", body, out,
      use="テンプレートの引数に条件をつけて、使える型を制限する", miss=miss, sim=sim, cx="コンパイル時のみ", ver=V20, info=CNI, pre=pre, rj=f"concepts/{name}.html", cr=f"concepts/{name}",
      hub=None, group="コンセプト（<concepts>）")


P_ = lambda t: f'std::println("{{}}", {t});'
CC("common_reference_with", "2 つの型が、共通の参照型を持つことを要求する。", "2 つの型の値を、同じ型の参照として扱えるかを調べます。条件演算子（`a ? b : c`）や、比較の前提になります。", "common_reference_t<T, U> が存在し、両方から変換できる", ["T", "U"],
   P_("std::common_reference_with<int&, const int&>") + "\n" + P_("std::common_reference_with<int, std::string>"), "true\nfalse", ("値と参照の組み合わせを考えない", "`int` と `std::string` のように、共通の参照型が作れない組み合わせは `false` です。"), [("[`common_with`](common_with.md)", "共通の型")])
CC("common_with", "2 つの型が、共通の型を持つことを要求する。", "2 つの型を混ぜた計算（`int` と `double` の足し算など）ができるかを調べます。`common_type_t<T, U>` が存在し、両方から変換できることが条件です。", "common_type_t<T, U> が存在し、両方から変換できる", ["T", "U"],
   P_("std::common_with<int, double>") + "\n" + P_("std::common_with<int, std::string>"), "true\nfalse", ("見かけだけで判断する", "`int` と `std::string` は、同じ「何か」に変換できないので `false` です。"), [("[`common_reference_with`](common_reference_with.md)", "共通の参照型")])
CC("signed_integral", "符号付きの整数型であることを要求する。", "`integral` のうち、負の値を持てる整数型だけを受け付けます。`int`・`long` は満たし、`unsigned` や `float` は満たしません。", "integral<T> かつ T が符号付き", ["T"],
   P_("std::signed_integral<int>") + "\n" + P_("std::signed_integral<unsigned>") + "\n" + P_("std::signed_integral<float>"), "true\nfalse\nfalse", ("`char` の符号を決めつける", "`char` の符号は処理系次第です。`signed char` や `unsigned char` を明示します。"), [("[`integral`](integral.md)", "整数全般"), ("[`unsigned_integral`](unsigned_integral.md)", "符号なし")])
CC("unsigned_integral", "符号なしの整数型であることを要求する。", "`integral` のうち、負の値を持たない整数型だけを受け付けます。`unsigned`・`size_t` は満たしますが、`bool` も満たす点に注意が必要です。", "integral<T> かつ T が符号なし", ["T"],
   P_("std::unsigned_integral<unsigned>") + "\n" + P_("std::unsigned_integral<int>") + "\n" + P_("std::unsigned_integral<bool>"), "true\nfalse\ntrue", ("`bool` を除外し忘れる", "`bool` は符号なし整数に含まれます。除きたいなら `!std::same_as<T, bool>` を併用します。"), [("[`integral`](integral.md)", "整数全般"), ("[`signed_integral`](signed_integral.md)", "符号付き")])
CC("assignable_from", "左辺の型に、右辺の値を代入できることを要求する。", "`a = b` が書ける型の組を要求します。左辺は**左辺値参照**の型で渡します（`int&`）。", "左辺値参照 T に U を代入できる", ["T", "U"],
   P_("std::assignable_from<int&, int>") + "\n" + P_("std::assignable_from<int, int>"), "true\nfalse", ("左辺に値の型を渡す", "`assignable_from<int, int>` は `false` です。左辺は `int&` のように参照で渡します。"), [("[`copyable`](copyable.md)", "コピーできる")])
CC("swappable", "`swap` で入れ替えられる型であることを要求する。", "`std::swap` が使える型だけを受け付けます。`const` の値は入れ替えられないので満たしません。", "ranges::swap(a, a) が使える", ["T"],
   P_("std::swappable<int>") + "\n" + P_("std::swappable<const int>"), "true\nfalse", ("const な型を渡す", "`const` の値は書き換えられないので、入れ替えられません。"), [("[`swappable_with`](swappable_with.md)", "2 つの型を入れ替える")])
CC("swappable_with", "2 つの型の値を、たがいに `swap` できることを要求する。", "異なる型の値を入れ替えられるかを調べます。左辺値参照の型を渡します。", "ranges::swap(a, b) と ranges::swap(b, a) が使える", ["T", "U"],
   P_("std::swappable_with<int&, int&>") + "\n" + P_("std::swappable_with<int&, long&>"), "true\nfalse", ("参照を付けずに渡す", "`swappable_with<int, int>` は `false` です。参照で渡します。"), [("[`swappable`](swappable.md)", "同じ型")])
CC("destructible", "破棄できる型であることを要求する。", "デストラクタが呼べる型を要求します。`void` や、デストラクタが `private` の型は満たしません。ほぼ全ての型が満たす、最も弱いコンセプトのひとつです。", "T が noexcept で破棄できる", ["T"],
   P_("std::destructible<int>") + "\n" + P_("std::destructible<void>"), "true\nfalse", ("デストラクタが投げる型", "`noexcept(false)` のデストラクタの型は満たしません。"), [("[`constructible_from`](constructible_from.md)", "作れる")])
CC("constructible_from", "指定した引数から構築できる型であることを要求する。", "`T(args...)` と書ける型を要求します。ジェネリックなコンテナの `emplace` などの制約に使います。", "destructible<T> かつ is_constructible_v<T, Args...>", ["T", "Args..."],
   P_("std::constructible_from<std::string, const char*>") + "\n" + P_("std::constructible_from<std::string, int>"), "true\nfalse", ("暗黙変換と混同する", "コンストラクタが `explicit` でも `constructible_from` は満たします。暗黙変換は `convertible_to` です。"), [("[`convertible_to`](convertible_to.md)", "暗黙の変換"), ("[`default_initializable`](default_initializable.md)", "引数なしで作れる")], inc=("concepts", "string"))
CC("move_constructible", "ムーブして構築できる型であることを要求する。", "他のオブジェクトからムーブして作れる型を要求します。`unique_ptr` のようなコピー不可・ムーブ可の型も満たします。", "constructible_from<T, T> かつ convertible_to<T, T>", ["T"],
   P_("std::move_constructible<std::string>") + "\n" + P_("std::move_constructible<std::unique_ptr<int>>"), "true\ntrue", ("ムーブ不可の型を渡す", "ムーブコンストラクタを `delete` した型は満たしません。"), [("[`copy_constructible`](copy_constructible.md)", "コピーできる"), ("[`movable`](movable.md)", "ムーブして代入もできる")], inc=("concepts", "string", "memory"))
CC("copy_constructible", "コピーして構築できる型であることを要求する。", "他のオブジェクトからコピーして作れる型を要求します。`unique_ptr` はコピーできないので満たしません。", "move_constructible<T> かつ T がコピーで構築できる", ["T"],
   P_("std::copy_constructible<std::string>") + "\n" + P_("std::copy_constructible<std::unique_ptr<int>>"), "true\nfalse", ("ムーブだけの型を渡す", "`unique_ptr` などのムーブ専用の型は満たしません。"), [("[`move_constructible`](move_constructible.md)", "ムーブして作れる"), ("[`copyable`](copyable.md)", "代入もできる")], inc=("concepts", "string", "memory"))
CC("semiregular", "コピーでき、既定構築できる型であることを要求する。", "「普通の値のように扱える」ための条件の前半です。コピーできて、引数なしでも作れる型を要求します。", "copyable<T> かつ default_initializable<T>", ["T"],
   P_("std::semiregular<int>") + "\n" + P_("std::semiregular<std::unique_ptr<int>>"), "true\nfalse", ("既定構築できない型", "引数なしで作れない型は満たしません。"), [("[`regular`](regular.md)", "さらに比較できる"), ("[`copyable`](copyable.md)", "既定構築は不要")], inc=("concepts", "memory"))
CC("regular", "値のように扱える型（コピー・既定構築・比較）を要求する。", "`int` のように「コピーでき、引数なしで作れ、`==` で比べられる」型を要求します。標準の多くのアルゴリズムが、この条件を前提にします。", "semiregular<T> かつ equality_comparable<T>", ["T"],
   P_("std::regular<int>") + "\n" + P_("std::regular<std::unique_ptr<int>>"), "true\nfalse", ("`==` の無い型", "比較できない型は満たしません。"), [("[`semiregular`](semiregular.md)", "比較は不要")], inc=("concepts", "memory"))
CC("equality_comparable", "`==` と `!=` で比べられる型であることを要求する。", "`a == b` が書ける型を要求します。`==` のほかに `!=` も使えることが条件です。", "T 同士で == と != が使える", ["T"],
   P_("std::equality_comparable<int>") + "\n" + P_("std::equality_comparable<NoEq>"), "true\nfalse", ("`==` を定義していない構造体", "`struct` は、`operator==` を書くか `= default` するまで比べられません。"), [("[`equality_comparable_with`](equality_comparable_with.md)", "異なる型どうし"), ("[`totally_ordered`](totally_ordered.md)", "大小も比べられる")], pre="struct NoEq {};")
CC("equality_comparable_with", "2 つの異なる型を `==` で比べられることを要求する。", "`int` と `long` のように、型が違う値を比べられるかを調べます。", "T と U が == で比べられ、共通の参照型がある", ["T", "U"],
   P_("std::equality_comparable_with<int, long>") + "\n" + P_("std::equality_comparable_with<int, std::string>"), "true\nfalse", ("暗黙変換できるだけで満たすと思う", "共通の参照型を持ち、両方向の `==` が使える必要があります。"), [("[`equality_comparable`](equality_comparable.md)", "同じ型どうし")], inc=("concepts", "string"))
CC("totally_ordered_with", "2 つの異なる型を `<` などで比べられることを要求する。", "`totally_ordered` の、型が異なる版です。`int` と `long` のように、混ぜて大小を比べられるかを調べます。", "T と U が <, >, <=, >= で比べられ、共通の参照型がある", ["T", "U"],
   P_("std::totally_ordered_with<int, long>") + "\n" + P_("std::totally_ordered_with<int, std::string>"), "true\nfalse", ("符号付きと符号なしを混ぜる", "満たしても、比較の結果が直感と違うことがあります。`std::cmp_less` を使います。"), [("[`totally_ordered`](totally_ordered.md)", "同じ型どうし")], inc=("concepts", "string"))
CC("regular_invocable", "同じ引数で何度呼んでも、同じ結果になる呼び出し可能な型を要求する。", "`invocable` より厳しく、「関数の副作用がなく、同じ入力に同じ出力」という意味が付きます。ただし、コンパイラが意味まで検査するわけではなく、構文上は `invocable` と同じです。", "invocable<F, Args...>（意味の上で等価性を保つ）", ["F", "Args..."],
   'auto f = [](int x) { return x; };\n' + P_("std::regular_invocable<decltype(f), int>") + "\n" + P_("std::regular_invocable<decltype(f), std::string>"), "true\nfalse", ("乱数やカウンタを返す関数に使う", "意味の上では、呼ぶたびに結果が変わる関数は対象外です。コンパイラは検査しません。"), [("[`invocable`](invocable.md)", "構文だけの条件")], inc=("concepts", "string"))
CC("relation", "2 つの値を比べる二項関係（真偽を返す関数）を要求する。", "`less` や `equal_to` のように、2 つの値を受け取って `bool` を返す関数を要求します。`sort` の比較関数などの制約に使われます。", "predicate<R, T, T> かつ predicate<R, T, U> など（4 つの組み合わせ）", ["R", "T", "U"],
   P_("std::relation<std::less<>, int, int>") + "\n" + P_("std::relation<std::less<>, int, std::string>"), "true\nfalse", ("1 引数の関数を渡す", "2 つの値を受け取る関数だけが対象です。"), [("[`equivalence_relation`](equivalence_relation.md)", "同値関係"), ("[`strict_weak_order`](strict_weak_order.md)", "整列に使える")], inc=("concepts", "functional", "string"))
CC("equivalence_relation", "同値関係（反射・対称・推移）となる二項関係を要求する。", "`==` のように、「A と A は同じ」「A と B が同じなら B と A も同じ」「A=B, B=C なら A=C」が成り立つ関係を要求します。構文上は `relation` と同じで、意味の条件は人間が守ります。", "relation<R, T, U>（意味の上で同値関係）", ["R", "T", "U"],
   P_("std::equivalence_relation<std::equal_to<>, int, int>"), "true", ("成り立たない関係を渡す", "コンパイラは意味を検査しません。たとえば `<` を渡しても通りますが、結果は保証されません。"), [("[`relation`](relation.md)", "構文だけの条件")], inc=("concepts", "functional"))
CC("strict_weak_order", "厳密な弱順序（`sort` に使える比較）となる二項関係を要求する。", "`<` のように、`sort` が使える比較関数が満たすべき条件です。「A<A は偽」「推移的」「等価も推移的」が成り立つことを要求します。構文上は `relation` と同じです。", "relation<R, T, U>（意味の上で厳密な弱順序）", ["R", "T", "U"],
   P_("std::strict_weak_order<std::less<>, int, int>"), "true", ("`<=` を渡す", "`<=` は「A<=A が真」になり、厳密な弱順序ではありません。`sort` で未定義動作になります。"), [("[`relation`](relation.md)", "構文だけの条件")], inc=("concepts", "functional"))

# ---- イテレータのコンセプト
CI_ = "[イテレータ](@/basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。"


def IC(name, summary, intro, req, params, body, out, miss, sim, inc=("iterator",), pre="", tips=None):
    Q(CN + name + ".md", "std::" + name, summary, "rare", [*inc, "print"], intro,
      tips or ["コンセプト。`requires` やテンプレートの制約に書く。", f"`std::{name}<...>` は `bool` の定数式。", "C++20 のアルゴリズムが、引数の制約に使っている。"],
      f"template <{', '.join('class ' + p for p in params)}>\nconcept {name} = /* {req} */;", [(p, "型", "調べる型") for p in params], "条件を満たせば `true`（コンパイル時の定数）", body, out,
      use="自作のアルゴリズムの引数を制約する", miss=miss, sim=sim, cx="コンパイル時のみ", ver=V20, info=CI_, pre=pre, rj=f"iterator/{name}.html", cr=f"iterator/{name}", hub=None, group="コンセプト（<concepts>）")


IC("input_or_output_iterator", "イテレータとして最低限の操作ができることを要求する。", "`*it` と `++it` が使える、最も弱いイテレータの条件です。入力・出力のどちらでも満たします。", "weakly_incrementable<I> かつ *i が使える", ["I"],
   P_("std::input_or_output_iterator<int*>") + "\n" + P_("std::input_or_output_iterator<int>"), "true\nfalse", ("整数をイテレータとして扱う", "`int` は `++` ができても `*` が使えません。"), [("[`input_iterator`](input_iterator.md)", "読み取れる"), ("[`output_iterator`](output_iterator.md)", "書き込める")])
IC("input_iterator", "要素を読みながら進められるイテレータを要求する。", "一度だけ前に進みながら、`*it` で要素を読めるイテレータです。ストリームから読むイテレータも満たします。", "input_or_output_iterator かつ indirectly_readable", ["I"],
   P_("std::input_iterator<int*>") + "\n" + P_("std::input_iterator<int>"), "true\nfalse", ("書き込み専用を渡す", "`back_insert_iterator` は読めないので満たしません。"), [("[`forward_iterator`](forward_iterator.md)", "何度でも読み返せる")])
IC("output_iterator", "指定した型の値を書き込めるイテレータを要求する。", "`*it = value` で値を書き込みながら進められるイテレータです。`output_iterator<I, T>` と、書き込む値の型も指定します。", "input_or_output_iterator かつ indirectly_writable<I, T>", ["I", "T"],
   P_("std::output_iterator<int*, int>") + "\n" + P_("std::output_iterator<const int*, int>"), "true\nfalse", ("const のポインタを出力先にする", "`const int*` には書き込めません。"), [("[`input_iterator`](input_iterator.md)", "読み取れる")])
IC("forward_iterator", "何度でも読み返せて、一方向に進むイテレータを要求する。", "同じ範囲を複数回走査できるイテレータです。`forward_list` のイテレータが典型で、`vector` のものも満たします。", "input_iterator かつ incrementable かつ sentinel_for<I, I>", ["I"],
   P_("std::forward_iterator<std::forward_list<int>::iterator>") + "\n" + P_("std::forward_iterator<std::istream_iterator<int>>"), "true\nfalse", ("入力ストリームのイテレータを渡す", "入力ストリームは 1 回しか読めません。"), [("[`input_iterator`](input_iterator.md)", "1 回だけ"), ("[`bidirectional_iterator`](bidirectional_iterator.md)", "後ろにも戻れる")], inc=("iterator", "forward_list"))
IC("bidirectional_iterator", "前後どちらにも進めるイテレータを要求する。", "`--it` で後ろに戻れるイテレータです。`list` や `map` のイテレータが満たします。", "forward_iterator かつ --i が使える", ["I"],
   P_("std::bidirectional_iterator<std::list<int>::iterator>") + "\n" + P_("std::bidirectional_iterator<std::forward_list<int>::iterator>"), "true\nfalse", ("`forward_list` に使う", "`forward_list` は後ろに戻れません。"), [("[`forward_iterator`](forward_iterator.md)", "一方向"), ("[`random_access_iterator`](random_access_iterator.md)", "添字で飛べる")], inc=("iterator", "list", "forward_list"))
IC("random_access_iterator", "添字で好きな位置へ飛べるイテレータを要求する。", "`it + n` や `it[n]` で一気に飛べるイテレータです。`vector`・`deque`・配列のイテレータが満たします。`sort` などが要求します。", "bidirectional_iterator かつ +, -, [], < などが使える", ["I"],
   P_("std::random_access_iterator<std::vector<int>::iterator>") + "\n" + P_("std::random_access_iterator<std::list<int>::iterator>"), "true\nfalse", ("`list` に sort を使う", "`list` は飛べないので、`sort` できません。`list::sort` を使います。"), [("[`bidirectional_iterator`](bidirectional_iterator.md)", "1 つずつ"), ("[`contiguous_iterator`](contiguous_iterator.md)", "さらにメモリが連続")], inc=("iterator", "vector", "list"))
IC("contiguous_iterator", "要素がメモリ上で連続して並ぶことを保証するイテレータを要求する。", "ポインタに直せる（`std::to_address`）ことが保証されたイテレータです。`vector`・`array`・`string` のイテレータが満たします。`memcpy` などの最適化の条件になります。", "random_access_iterator かつ 要素が連続している", ["I"],
   P_("std::contiguous_iterator<int*>") + "\n" + P_("std::contiguous_iterator<std::deque<int>::iterator>"), "true\nfalse", ("`deque` を連続だと思う", "`deque` は複数のブロックに分かれています。"), [("[`random_access_iterator`](random_access_iterator.md)", "連続とは限らない")], inc=("iterator", "deque"))
IC("sentinel_for", "あるイテレータの終端として使える型を要求する。", "範囲の終わりを表す型が、イテレータとは別の型のことがあります。`sentinel_for<S, I>` は、`S` が `I` と `==` で比べられる、終端として使える型かを調べます。", "semiregular<S> かつ I と S が == で比べられる", ["S", "I"],
   P_("std::sentinel_for<int*, int*>") + "\n" + P_("std::sentinel_for<int, int*>"), "true\nfalse", ("異なる種類のイテレータを組み合わせる", "比べられない組み合わせは満たしません。"), [("[`sized_sentinel_for`](sized_sentinel_for.md)", "差を求められる")])
IC("sized_sentinel_for", "イテレータとの差（距離）を定数時間で求められる終端を要求する。", "`sentinel_for` に加えて、`end - begin` で要素数を求められることを要求します。`vector` のイテレータは満たしますが、`list` は満たしません。", "sentinel_for<S, I> かつ S - I が使える", ["S", "I"],
   P_("std::sized_sentinel_for<int*, int*>") + "\n" + P_("std::sized_sentinel_for<std::list<int>::iterator, std::list<int>::iterator>"), "true\nfalse", ("`list` の距離を速いと思う", "`list` は 1 つずつ数えるので、差が定数時間では求まりません。"), [("[`sentinel_for`](sentinel_for.md)", "差は不要")], inc=("iterator", "list"))
IC("weakly_incrementable", "`++` で進めるイテレータの最低限の条件を要求する。", "`++it` と `it++` が使えて、差の型（`difference_type`）が定義されている型です。`int` も満たします（`views::iota` が `int` を数えるときに使われます）。", "default_initializable かつ movable かつ ++i が使える", ["I"],
   P_("std::weakly_incrementable<int>") + "\n" + P_("std::weakly_incrementable<void*>"), "true\nfalse", ("ポインタを何でも満たすと思う", "`void*` は演算できないので満たしません。"), [("[`incrementable`](incrementable.md)", "さらに等価性がある")])
IC("incrementable", "`++` で進められ、何度でも同じ範囲を走査できる型を要求する。", "`weakly_incrementable` に、「コピーしたイテレータを独立に進めても同じ結果になる」という性質を足したものです。", "weakly_incrementable かつ regular かつ i++ が i と同じ型を返す", ["I"],
   P_("std::incrementable<int>") + "\n" + P_("std::incrementable<const int>"), "true\nfalse", ("const の型を渡す", "`const int` は `++` できません。"), [("[`weakly_incrementable`](weakly_incrementable.md)", "弱い条件")])
IC("indirectly_readable", "`*it` で値を読み取れる型を要求する。", "イテレータやポインタのように、`*` で間接的に値を読める型です。値の型と参照の型が定義されていることが条件です。", "*it で値を読め、iter_value_t などが定義されている", ["In"],
   P_("std::indirectly_readable<int*>") + "\n" + P_("std::indirectly_readable<int>"), "true\nfalse", ("書き込み専用の型を渡す", "`back_insert_iterator` は `*` で読めません。"), [("[`indirectly_writable`](indirectly_writable.md)", "書き込める")])
IC("indirectly_writable", "`*it = value` で値を書き込める型を要求する。", "イテレータやポインタのように、`*` を通して値を書き込める型です。書き込む値の型も指定します。", "*it = value が使える", ["Out", "T"],
   P_("std::indirectly_writable<int*, int>") + "\n" + P_("std::indirectly_writable<const int*, int>"), "true\nfalse", ("const のポインタを渡す", "`const int*` は書き込めません。"), [("[`indirectly_readable`](indirectly_readable.md)", "読み取れる")])
IC("indirectly_movable", "あるイテレータから別のイテレータへ、要素をムーブできることを要求する。", "`move` 系のアルゴリズムの制約に使われます。読み取り側と書き込み側の型が合っているかを調べます。", "indirectly_readable<In> かつ indirectly_writable<Out, iter_rvalue_reference_t<In>>", ["In", "Out"],
   P_("std::indirectly_movable<int*, int*>") + "\n" + P_("std::indirectly_movable<int*, const int*>"), "true\nfalse", ("const な出力先", "書き込めない出力先は満たしません。"), [("[`indirectly_copyable`](indirectly_copyable.md)", "コピーする")])
IC("indirectly_copyable", "あるイテレータから別のイテレータへ、要素をコピーできることを要求する。", "`copy` 系のアルゴリズムの制約に使われます。", "indirectly_readable<In> かつ indirectly_writable<Out, iter_reference_t<In>>", ["In", "Out"],
   P_("std::indirectly_copyable<int*, int*>") + "\n" + P_("std::indirectly_copyable<int*, const int*>"), "true\nfalse", ("コピーできない要素を渡す", "`unique_ptr` の列は、コピーできません。ムーブにします。"), [("[`indirectly_movable`](indirectly_movable.md)", "ムーブする")])
IC("indirectly_swappable", "2 つのイテレータが指す要素を、入れ替えられることを要求する。", "`swap_ranges` などの制約に使われます。", "iter_swap(i1, i2) が使える", ["I1", "I2"],
   P_("std::indirectly_swappable<int*, int*>") + "\n" + P_("std::indirectly_swappable<const int*, const int*>"), "true\nfalse", ("const な要素", "書き込めない要素は入れ替えられません。"), [("[`swappable`](swappable.md)", "値の入れ替え")])
IC("indirectly_comparable", "2 つのイテレータが指す要素を、比較関数で比べられることを要求する。", "`equal` や `find` などの制約に使われます。比較関数と、それぞれのイテレータを指定します。", "indirect_binary_predicate<Comp, projected<I1, P1>, projected<I2, P2>>", ["I1", "I2", "Comp"],
   P_("std::indirectly_comparable<int*, int*, std::ranges::equal_to>"), "true", ("比較できない型の組", "要素どうしが比較関数に渡せない組み合わせは満たしません。"), [("[`indirect_binary_predicate`](indirect_binary_predicate.md)", "二項述語")], inc=("iterator", "functional"))
IC("sortable", "並べ替えられるイテレータ（ランダムアクセスと入れ替えと比較）を要求する。", "`ranges::sort` が使える条件です。ランダムアクセスで、要素を入れ替えられ、比較できる必要があります。", "permutable かつ indirect_strict_weak_order", ["I"],
   P_("std::sortable<std::vector<int>::iterator>") + "\n" + P_("std::sortable<std::list<int>::iterator>"), "true\nfalse", ("`list` に sort を使う", "`list` はランダムアクセスできないので、`ranges::sort` できません。"), [("[`permutable`](permutable.md)", "並べ替えの前提"), ("[`mergeable`](mergeable.md)", "併合の前提")], inc=("iterator", "vector", "list"))
IC("permutable", "要素を並べ替えられるイテレータを要求する。", "要素を入れ替えたり、動かしたりできる前方イテレータです。`rotate` や `unique` などの制約に使われます。", "forward_iterator かつ indirectly_movable_storable かつ indirectly_swappable", ["I"],
   P_("std::permutable<int*>") + "\n" + P_("std::permutable<const int*>"), "true\nfalse", ("const のポインタを渡す", "書き込めないので、並べ替えられません。"), [("[`sortable`](sortable.md)", "並べ替えられる")])
IC("mergeable", "2 つの整列済み範囲を併合できるイテレータの組を要求する。", "`merge` や `set_union` などの制約に使われます。2 つの入力と 1 つの出力の組み合わせを調べます。", "input_iterator が 2 つと、書き込める出力先、比較ができる", ["I1", "I2", "Out"],
   P_("std::mergeable<int*, int*, int*>"), "true", ("出力先が const", "書き込めない出力先は満たしません。"), [("[`sortable`](sortable.md)", "並べ替え")])
IC("indirectly_unary_invocable", "イテレータが指す値で、1 引数の関数を呼べることを要求する。", "`for_each` のように、要素を 1 つずつ関数に渡すアルゴリズムの制約に使われます。", "関数 F が iter_value_t と iter_reference_t で呼べる", ["F", "I"],
   'auto f = [](int x) { return x; };\n' + P_("std::indirectly_unary_invocable<decltype(f), int*>"), "true", ("引数の型が合わない関数", "要素の型を受けられない関数は満たしません。"), [("[`indirectly_regular_unary_invocable`](indirectly_regular_unary_invocable.md)", "副作用なしの条件")], inc=("iterator",))
IC("indirectly_regular_unary_invocable", "イテレータが指す値で、副作用なく 1 引数の関数を呼べることを要求する。", "`indirectly_unary_invocable` に、「同じ入力なら同じ出力」の意味が付きます。プロジェクションなどに使われます。", "関数 F が値・参照の両方で regular_invocable", ["F", "I"],
   'auto f = [](int x) { return x; };\n' + P_("std::indirectly_regular_unary_invocable<decltype(f), int*>"), "true", ("状態を持つ関数", "コンパイラは意味を検査しません。"), [("[`indirectly_unary_invocable`](indirectly_unary_invocable.md)", "構文だけの条件")], inc=("iterator",))
IC("indirect_unary_predicate", "イテレータが指す値で、1 引数の述語を呼べることを要求する。", "`find_if` や `count_if` のように、要素を条件で判定するアルゴリズムの制約に使われます。述語は `bool` に変換できる値を返す必要があります。", "述語 Pred が値・参照で predicate", ["Pred", "I"],
   'auto p = [](int x) { return x > 0; };\n' + P_("std::indirect_unary_predicate<decltype(p), int*>"), "true", ("`bool` に変換できない戻り値", "戻り値が `bool` に変換できない関数は満たしません。"), [("[`predicate`](predicate.md)", "値の述語")], inc=("iterator",))
IC("indirect_binary_predicate", "2 つのイテレータが指す値で、2 引数の述語を呼べることを要求する。", "`mismatch` や `equal` のように、2 つの範囲の要素を比べるアルゴリズムの制約に使われます。", "述語が 2 つのイテレータの値・参照で predicate", ["Pred", "I1", "I2"],
   P_("std::indirect_binary_predicate<std::equal_to<>, int*, int*>"), "true", ("型が比べられない組", "比較できない型の組み合わせは満たしません。"), [("[`indirect_unary_predicate`](indirect_unary_predicate.md)", "1 引数")], inc=("iterator", "functional"))
IC("indirect_equivalence_relation", "2 つのイテレータが指す値で、同値関係を呼べることを要求する。", "`unique` のように、同じ値を探すアルゴリズムの制約に使われます。", "述語が 2 つのイテレータの値・参照で equivalence_relation", ["Pred", "I1", "I2"],
   P_("std::indirect_equivalence_relation<std::equal_to<>, int*>"), "true", ("`<` を渡す", "同値関係には `==` を渡します。`<` は意味が違います。"), [("[`equivalence_relation`](equivalence_relation.md)", "値の同値関係")], inc=("iterator", "functional"))
IC("indirect_strict_weak_order", "2 つのイテレータが指す値で、厳密な弱順序を呼べることを要求する。", "`sort` や `lower_bound` のように、要素の順序を比べるアルゴリズムの制約に使われます。", "述語が 2 つのイテレータの値・参照で strict_weak_order", ["Comp", "I"],
   P_("std::indirect_strict_weak_order<std::less<>, int*>"), "true", ("`<=` を渡す", "`<=` は厳密な弱順序ではありません。"), [("[`strict_weak_order`](strict_weak_order.md)", "値の弱順序")], inc=("iterator", "functional"))

if __name__ == "__main__":
    flush_hubs()
