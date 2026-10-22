---
title: <type_traits>（型の性質を調べる）
summary: "型の性質（整数かポインタかなど）を、コンパイル時に調べる。"
order: 84
tags:
  - 型・言語サポート
---

# &lt;type_traits&gt;（型の性質を調べる）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`<type_traits>` は、**コンパイル時に型の性質を調べたり、型を変換したりする道具**をまとめたヘッダです。「この型は整数か」「ポインタか」「コピーできるか」を `std::is_integral_v<T>` のように調べられます。主に[テンプレート](../../basics/template.md)の中で、型によって処理を変えたり（`if constexpr`）、間違った型を弾いたり（`static_assert`）するのに使います。

!!! tip "ポイント"
    - 調べるのは `std::is_xxx_v<T>`（`bool` の定数）、変換するのは `std::xxx_t<T>`（型）。
    - `if constexpr (std::is_integral_v<T>)` で型ごとに処理を分ける。
    - 構造体をそのまま `memcpy` / ファイルに書いていいかは `std::is_trivially_copyable_v<T>` で確かめる。
    - C++20 以降は、テンプレートの型の条件は [concepts](../../basics/template.md#concepts型に条件を付ける)（`std::integral` など）のほうが読みやすい。

## 調べる（is_ 系）

よく使う順です。

| 名前 | 重要度 | `true` になる型 |
| --- | --- | --- |
| [`std::is_same_v<T, U>`](type_traits/is_same.md) | <span class="rank rank-often">よく使う</span> | T と U が同じ型 |
| [`std::is_integral_v<T>`](type_traits/is_integral.md) | <span class="rank rank-sometimes">たまに</span> | 整数型（bool、char も含む） |
| [`std::is_floating_point_v<T>`](type_traits/is_floating_point.md) | <span class="rank rank-sometimes">たまに</span> | float、double |
| [`std::is_trivially_copyable_v<T>`](type_traits/is_trivially_copyable.md) | <span class="rank rank-sometimes">たまに</span> | memcpy でコピーしてよい型 |
| [`std::is_enum_v<T>`](type_traits/is_enum.md) | <span class="rank rank-sometimes">たまに</span> | enum |
| [`std::is_pointer_v<T>`](type_traits/is_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタ |
| [`std::is_base_of_v<Base, D>`](type_traits/is_base_of.md) | <span class="rank rank-rare">知ってるだけ</span> | D が Base を継承している |
| [`std::is_arithmetic_v<T>`](type_traits/is_arithmetic.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数か浮動小数点 |
| [`std::is_const_v<T>`](type_traits/is_const.md) | <span class="rank rank-rare">知ってるだけ</span> | const が付いている |
| [`std::is_default_constructible_v<T>`](type_traits/is_default_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 引数なしで作れる |
| [`std::is_copy_constructible_v<T>`](type_traits/is_copy_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーできる |
| [`std::is_nothrow_move_constructible_v<T>`](type_traits/is_nothrow_move_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 例外を投げずにムーブできる |
| [`std::is_aggregate_v<T>`](type_traits/is_aggregate.md) | <span class="rank rank-rare">知ってるだけ</span> | `{}` でメンバを並べて作れる構造体 |
| [`std::is_void`](type_traits/is_void.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `void` かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_null_pointer`](type_traits/is_null_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `std::nullptr_t` かを調べる。 <span class="ver ver-14">C++14</span> |
| [`std::is_array`](type_traits/is_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が配列かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_union`](type_traits/is_union.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が共用体（union）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_class`](type_traits/is_class.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がクラス（struct を含む）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_function`](type_traits/is_function.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が関数の型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_lvalue_reference`](type_traits/is_lvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が左辺値参照かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_rvalue_reference`](type_traits/is_rvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が右辺値参照かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_member_object_pointer`](type_traits/is_member_object_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバ変数へのポインタかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_member_function_pointer`](type_traits/is_member_function_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバ関数へのポインタかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_fundamental`](type_traits/is_fundamental.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が基本型（算術型・`void`・`nullptr_t`）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_scalar`](type_traits/is_scalar.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がスカラー型（算術型・列挙・ポインタなど）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_object`](type_traits/is_object.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がオブジェクト型（関数・参照・`void` 以外）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_compound`](type_traits/is_compound.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が複合型（基本型以外）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_reference`](type_traits/is_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が参照（左辺値でも右辺値でも）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_member_pointer`](type_traits/is_member_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバへのポインタかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_volatile`](type_traits/is_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `volatile` 修飾されているかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_trivial`](type_traits/is_trivial.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がトリビアル（自明な構築・コピー・破棄ができる）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_standard_layout`](type_traits/is_standard_layout.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が標準レイアウト（C 言語と互換のメモリ配置）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_pod`](type_traits/is_pod.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が POD（トリビアルかつ標準レイアウト）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_polymorphic`](type_traits/is_polymorphic.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が仮想関数を持つ（多態的な）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_abstract`](type_traits/is_abstract.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が抽象クラス（純粋仮想関数を持つ）かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_final`](type_traits/is_final.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `final`（継承できない）かを調べる。 <span class="ver ver-14">C++14</span> |
| [`std::is_implicit_lifetime`](type_traits/is_implicit_lifetime.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が「暗黙的に寿命を始められる」型かを調べる。 <span class="ver ver-23">C++23</span> |
| [`std::is_unsigned`](type_traits/is_unsigned.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が符号なしの算術型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_bounded_array`](type_traits/is_bounded_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が要素数の決まった配列かを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_unbounded_array`](type_traits/is_unbounded_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が要素数の決まっていない配列かを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_scoped_enum`](type_traits/is_scoped_enum.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がスコープ付き列挙型（`enum class`）かを調べる。 <span class="ver ver-23">C++23</span> |
| [`std::is_constructible`](type_traits/is_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で構築できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_trivially_constructible`](type_traits/is_trivially_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、自明に（特別な処理なしで）構築できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_nothrow_constructible`](type_traits/is_nothrow_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、例外を投げずに構築できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_move_constructible`](type_traits/is_move_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブして構築できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_assignable`](type_traits/is_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入できる型の組かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_copy_assignable`](type_traits/is_copy_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | コピー代入できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_move_assignable`](type_traits/is_move_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブ代入できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_destructible`](type_traits/is_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 破棄できる型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_trivially_destructible`](type_traits/is_trivially_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 破棄が自明（何もしなくてよい）な型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_nothrow_destructible`](type_traits/is_nothrow_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | デストラクタが例外を投げない型かを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_swappable`](type_traits/is_swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | `swap` で入れ替えられる型かを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::is_swappable_with`](type_traits/is_swappable_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型の値を、たがいに `swap` できるかを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::is_nothrow_swappable`](type_traits/is_nothrow_swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | `swap` が例外を投げない型かを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::has_virtual_destructor`](type_traits/has_virtual_destructor.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が仮想デストラクタを持つかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::has_unique_object_representations`](type_traits/has_unique_object_representations.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値なら必ず同じビット列になる型かを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::is_layout_compatible`](type_traits/is_layout_compatible.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型のメモリ配置が互換かを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_pointer_interconvertible_base_of`](type_traits/is_pointer_interconvertible_base_of.md) | <span class="rank rank-rare">知ってるだけ</span> | 基底クラスのポインタと派生クラスのポインタを、相互に変換できるかを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_convertible`](type_traits/is_convertible.md) | <span class="rank rank-rare">知ってるだけ</span> | 型 `From` から `To` へ暗黙に変換できるかを調べる。 <span class="ver ver-11">C++11</span> |
| [`std::is_nothrow_convertible`](type_traits/is_nothrow_convertible.md) | <span class="rank rank-rare">知ってるだけ</span> | 暗黙の変換が例外を投げないかを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_invocable`](type_traits/is_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で呼び出せる型かを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::is_invocable_r`](type_traits/is_invocable_r.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::is_nothrow_invocable`](type_traits/is_nothrow_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、例外を投げずに呼び出せるかを調べる。 <span class="ver ver-17">C++17</span> |
| [`std::reference_constructs_from_temporary`](type_traits/reference_constructs_from_temporary.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照が、一時オブジェクトを作って束縛されるかを調べる。 <span class="ver ver-23">C++23</span> |
| [`std::reference_converts_from_temporary`](type_traits/reference_converts_from_temporary.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照が、暗黙の変換で一時オブジェクトに束縛されるかを調べる。 <span class="ver ver-23">C++23</span> |
| [`std::alignment_of`](type_traits/alignment_of.md) | <span class="rank rank-rare">知ってるだけ</span> | 型のアライメント（配置できる境界のバイト数）を調べる。 |
| [`std::is_corresponding_member`](type_traits/is_corresponding_member.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのメンバが、2 つの構造体の対応する位置にあるかを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::is_within_lifetime`](type_traits/is_within_lifetime.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタが指すオブジェクトが、いま寿命の中にあるかを調べる。 <span class="ver ver-26">C++26</span> |
| [`std::remove_cv`](type_traits/remove_cv.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` と `volatile` を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::remove_const`](type_traits/remove_const.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::remove_volatile`](type_traits/remove_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | `volatile` を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::add_cv`](type_traits/add_cv.md) | <span class="rank rank-rare">知ってるだけ</span> | `const volatile` を付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::add_const`](type_traits/add_const.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` を付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::add_volatile`](type_traits/add_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | `volatile` を付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::remove_reference`](type_traits/remove_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::add_lvalue_reference`](type_traits/add_lvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 左辺値参照を付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::add_rvalue_reference`](type_traits/add_rvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 右辺値参照を付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::make_signed`](type_traits/make_signed.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号なしの整数型を、同じ大きさの符号付きにする。 <span class="ver ver-11">C++11</span> |
| [`std::remove_extent`](type_traits/remove_extent.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列の最初の次元を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::remove_all_extents`](type_traits/remove_all_extents.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列の全部の次元を取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::remove_pointer`](type_traits/remove_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタを取り除く。 <span class="ver ver-11">C++11</span> |
| [`std::add_pointer`](type_traits/add_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタを付け足す。 <span class="ver ver-11">C++11</span> |
| [`std::aligned_storage`](type_traits/aligned_storage.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した大きさと境界の、生のメモリ領域の型。 |
| [`std::aligned_union`](type_traits/aligned_union.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型のどれでも入れられる、生のメモリ領域の型。 |
| [`std::enable_if`](type_traits/enable_if.md) | <span class="rank rank-sometimes">たまに</span> | 条件が真のときだけ、型を存在させる（SFINAE のための道具）。 |
| [`std::conjunction`](type_traits/conjunction.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の条件がすべて真かを調べる（短絡評価）。 <span class="ver ver-17">C++17</span> |
| [`std::disjunction`](type_traits/disjunction.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の条件のどれかが真かを調べる（短絡評価）。 <span class="ver ver-17">C++17</span> |
| [`std::negation`](type_traits/negation.md) | <span class="rank rank-rare">知ってるだけ</span> | 型特性の結果を反転する。 <span class="ver ver-17">C++17</span> |
| [`std::common_reference`](type_traits/common_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型が共有できる、共通の参照型を求める。 <span class="ver ver-20">C++20</span> |
| [`std::type_identity`](type_traits/type_identity.md) | <span class="rank rank-rare">知ってるだけ</span> | 何もしない型変換（テンプレート引数の推論を止めるのに使う）。 <span class="ver ver-20">C++20</span> |
| [`std::void_t`](type_traits/void_t.md) | <span class="rank rank-rare">知ってるだけ</span> | どんな型を渡しても `void` になる別名（検出イディオム用）。 <span class="ver ver-17">C++17</span> |
| [`std::is_constant_evaluated`](type_traits/is_constant_evaluated.md) | <span class="rank rank-rare">知ってるだけ</span> | いま、コンパイル時に評価されているかを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::integral_constant`](type_traits/integral_constant.md) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時の定数を、型として表す。 <span class="ver ver-11">C++11</span> |
| [`std::bool_constant`](type_traits/bool_constant.md) | <span class="rank rank-rare">知ってるだけ</span> | `bool` のコンパイル時の定数を、型として表す。 <span class="ver ver-11">C++11</span> |
| [`std::true_type`](type_traits/true_type.md) | <span class="rank rank-rare">知ってるだけ</span> | `true` を表すコンパイル時の定数の型。 <span class="ver ver-11">C++11</span> |
| [`std::false_type`](type_traits/false_type.md) | <span class="rank rank-rare">知ってるだけ</span> | `false` を表すコンパイル時の定数の型。 <span class="ver ver-11">C++11</span> |

## 変換する（_t 系）

| 名前 | 重要度 | 結果 |
| --- | --- | --- |
| [`std::remove_cvref_t<T>`](type_traits/remove_cvref.md) | <span class="rank rank-sometimes">たまに</span> | const と参照を取り除いた型 <span class="ver ver-20">C++20</span> |
| [`std::underlying_type_t<E>`](type_traits/underlying_type.md) | <span class="rank rank-sometimes">たまに</span> | enum の中身の整数型 |
| [`std::decay_t<T>`](type_traits/decay.md) | <span class="rank rank-rare">知ってるだけ</span> | 値で受け取ったときの型（配列はポインタに） |
| [`std::conditional_t<B, T, F>`](type_traits/conditional.md) | <span class="rank rank-rare">知ってるだけ</span> | B が true なら T、false なら F |
| [`std::common_type_t<T, U>`](type_traits/common_type.md) | <span class="rank rank-rare">知ってるだけ</span> | T と U の両方を表せる型 |
| [`std::make_unsigned_t<T>`](type_traits/make_unsigned.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号なし版の整数型 |
| [`std::invoke_result_t<F, Args...>`](type_traits/invoke_result.md) | <span class="rank rank-rare">知ってるだけ</span> | F を Args で呼んだ戻り値の型 |

## よくある使い方

```cpp
#include <cstring>
#include <print>
#include <string>
#include <type_traits>

// memcpy でそのまま書き出してよい型だけ受け付ける
template <class T>
void WriteRaw(const T& value) {
  static_assert(std::is_trivially_copyable_v<T>, "string や vector を含む型は書けない");
  char buffer[sizeof(T)];
  std::memcpy(buffer, &value, sizeof(T));
  std::println("{} バイト書いた", sizeof(T));
}

struct Header {
  int version;
  float time;
};

int main() {
  WriteRaw(Header{1, 2.5f});
  // WriteRaw(std::string("x"));  // コンパイルエラー（static_assert）
  std::println("{} {}", std::is_trivially_copyable_v<Header>,
               std::is_trivially_copyable_v<std::string>);
}
```

```text title="実行結果"
8 バイト書いた
true false
```

## フラグ・オプション

フラグはありません。`std::is_xxx<T>::value` と書く古い書き方は、`std::is_xxx_v<T>` と同じです。

## ゲームでの使いどころ

| 場面 | 道具 |
| --- | --- |
| バイナリで保存してよい型か確かめる | `is_trivially_copyable_v` + `static_assert` |
| 型ごとに処理を変える汎用の関数（シリアライズ、デバッグ表示） | `is_integral_v` などで `if constexpr` |
| AddComponent<T> の T を確かめる | `is_base_of_v` |
| enum を整数に | `underlying_type_t` |

## よくあるミス

??? failure "参照付きの型で調べて false になる"
    テンプレートの `T&&` で受け取ると、T が `int&` になることがあり、`is_integral_v<T>` が false になります。`std::remove_cvref_t<T>` してから調べます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 調べるのは `is_xxx_v<T>`、変換は `xxx_t<T>`
    - [x] `if constexpr` と `static_assert` と組み合わせる
    - [x] バイナリ保存の前に is_trivially_copyable_v

## 関連ページ

- [テンプレート](../../basics/template.md)
- [cppreference: Type support](https://en.cppreference.com/w/cpp/types)
