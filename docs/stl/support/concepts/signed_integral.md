---
title: std::signed_integral
summary: "符号付きの整数型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::signed_integral

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

符号つきの整数だけを受け取るテンプレートを書きたい。`std::signed_integral` は、<strong>型が符号つきの整数型か</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::signed_integral<T>` は、`T` が符号つきの整数型か
    - `template <std::signed_integral T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::signed_integral {#signed_integral}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept signed_integral = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`int`、`long`、`short`、`signed char`、`long long` などが条件を満たします。`unsigned int` や `bool`、`float` は満たしません。`std::integral` かつ `std::is_signed_v` が真の型です。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("int                                -> {}", std::signed_integral<int>);
  std::println("unsigned int                       -> {}", std::signed_integral<unsigned int>);
  std::println("bool                               -> {}", std::signed_integral<bool>);
  std::println("float                              -> {}", std::signed_integral<float>);
}
```

```text title="実行結果"
int                                -> true
unsigned int                       -> false
bool                               -> false
float                              -> false
```

## ゲームでの使いどころ

差を計算して負になりうる値を受け取る関数に使います。

```cpp
template <std::signed_integral T>
T Distance(T a, T b) { return a > b ? a - b : b - a; }
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
    - [x] `std::signed_integral<T>` は、`T` が符号つきの整数型か
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::signed_integral](https://cpprefjp.github.io/reference/concepts/signed_integral.html)
- [cppreference: std::signed_integral](https://en.cppreference.com/w/cpp/concepts/signed_integral)
