---
title: std::is_integral
summary: "整数型かを調べる。"
order: 2
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_integral

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

テンプレートの関数で、整数のときは割り算を、小数のときは掛け算を使うなど、型によって処理を切り替えたいことがあります。型を人の目で判断するのではなく、コンパイラーに聞くのが `std::is_integral_v<T>` です。型 `T` が整数型（`int`、`char`、`bool` など）なら `true` です。`if constexpr` と組み合わせて、型ごとの処理を書き分けます。

!!! tip "ポイント"
    - `bool` と `char` も整数型。
    - `enum` は整数型ではない。
    - C++20 では `std::integral` コンセプトも使える。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

## 関数の詳しい説明

### std::is_integral_v {#is_integral}

```cpp
template <class T>
inline constexpr bool is_integral_v;
```

- 整数型（bool、char、short、int、long、long long、符号なし版）なら true

## しくみ

`is_integral_v<T>` は、`T` が `bool`、`char` の各種、`short`、`int`、`long`、`long long` と、その符号なしの版のどれかなら `true` です。`const` や `volatile` が付いていても `true` ですが、参照やポインターは `false` です。

`enum` は整数型ではありません。`enum` を整数として扱いたいなら、`std::is_enum_v` で別に調べ、`std::to_underlying` で変換します。`float` や `double` は、`is_floating_point_v` で調べます。

C++20 のコンセプト `std::integral` は、同じ判定を `template <std::integral T>` の形で書けます。条件を `if constexpr` で使うときは型特性、関数の制約に使うときはコンセプトを選びます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {} {}", std::is_integral_v<int>, std::is_integral_v<bool>, std::is_integral_v<float>);
}
```

```text title="実行結果"
true true false
```

## ゲームでの使いどころ

数値を扱うテンプレート関数の中で、整数と小数の処理を切り替えるために使います。

```cpp
template <class T>
T Half(T v) {
  if constexpr (std::is_integral_v<T>) {
    return v / 2;  // 整数は割り算
  } else {
    return v * 0.5;  // 小数は掛け算
  }
}
```

シリアライズでは、整数型はそのままバイナリに書き込み、小数は別の書式にする、といった分岐で使います。

数学ライブラリの関数に、不正な型が渡されたときの `static_assert` にも使えます。`static_assert(std::is_integral_v<T> || std::is_floating_point_v<T>, "数値型のみ");` と書くと、文字列などを渡したときに分かりやすいメッセージが出ます。

## よくあるミス

??? failure "`bool` や `char` も整数型であることを忘れる"
    `is_integral_v<bool>` は `true` です。`Half(true)` が通ってしまいます。数としての整数だけを許すなら、`bool` を別に除きます。

??? failure "`enum` を整数型だと思う"
    `enum` は `is_integral_v` が `false` です。`std::is_enum_v` で別に調べます。

??? failure "参照型で `false` になって困惑する"
    `is_integral_v<int&>` は `false` です。テンプレートが参照で型を受けているときは、`std::remove_cvref_t<T>` を通してから調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::is_floating_point`](is_floating_point.md) | 小数型かを調べる |
| `std::is_arithmetic` | 整数または小数のどちらかか |
| [`std::integral`](../concepts/integral.md) | コンセプト版。関数の制約に使う |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `is_integral_v<T>` で整数型かを調べる。
    - [x] `bool` と `char` も整数型。`enum` は違う。
    - [x] 参照型には `remove_cvref_t` を通してから使う。

## 関連ページ

- [cpprefjp: std::is_integral](https://cpprefjp.github.io/reference/type_traits/is_integral.html)
- [cppreference: std::is_integral](https://en.cppreference.com/w/cpp/types/is_integral)
