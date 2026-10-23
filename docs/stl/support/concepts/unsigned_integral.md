---
title: std::unsigned_integral
summary: "符号なしの整数型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::unsigned_integral

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

符号なしの整数だけを受け取るテンプレートを書きたい。ビット演算では、符号なしの整数が前提になることが多いです。`std::unsigned_integral` は、<strong>型が符号なしの整数型か</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::unsigned_integral<T>` は、`T` が符号なしの整数型か
    - `template <std::unsigned_integral T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unsigned_integral {#unsigned_integral}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept unsigned_integral = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`unsigned int`、`unsigned char`、`std::size_t` などが条件を満たします。`bool` も符号なしの整数型として条件を満たします。`int` や `float` は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("unsigned int                       -> {}", std::unsigned_integral<unsigned int>);
  std::println("int                                -> {}", std::unsigned_integral<int>);
  std::println("bool                               -> {}", std::unsigned_integral<bool>);
  std::println("float                              -> {}", std::unsigned_integral<float>);
}
```

```text title="実行結果"
unsigned int                       -> true
int                                -> false
bool                               -> true
float                              -> false
```

## ゲームでの使いどころ

ビット演算の関数を、符号なしだけに限ります。

```cpp
template <std::unsigned_integral T>
int CountBits(T value) { return std::popcount(value); }
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`same_as`](same_as.md) | 2 つの型が同じ |
| [`integral`](integral.md) | 整数型 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::unsigned_integral<T>` は、`T` が符号なしの整数型か
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::unsigned_integral](https://cpprefjp.github.io/reference/concepts/unsigned_integral.html)
- [cppreference: std::unsigned_integral](https://en.cppreference.com/w/cpp/concepts/unsigned_integral)
