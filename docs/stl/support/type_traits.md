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
