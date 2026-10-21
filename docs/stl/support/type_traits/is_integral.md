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

`std::is_integral_v<T>` は、**型 T が整数型（`int`、`char`、`bool` など）か**を調べます。テンプレートで、整数と小数の処理を切り替えるときに使います。

!!! tip "ポイント"
    - `bool` と `char` も整数型。
    - `enum` は整数型ではない。
    - C++20 では `std::integral` コンセプトも使える。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_integral_v {#is_integral}

```cpp
template <class T>
inline constexpr bool is_integral_v;
```

- 整数型（bool、char、short、int、long、long long、符号なし版）なら true

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

| 場面 | 書き方 |
| --- | --- |
| 整数だけを受け取るテンプレート | `static_assert(std::is_integral_v<T>)` |

## よくあるミス

??? failure "bool を整数と思わない"
    `is_integral_v<bool>` は `true` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_floating_point`](is_floating_point.md) | 小数型 |
| [`is_arithmetic`](is_arithmetic.md) | 整数または小数 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数型かを調べる
    - [x] bool と char も整数
    - [x] コンセプト版もある

## 関連ページ

- [cpprefjp: std::is_integral](https://cpprefjp.github.io/reference/type_traits/is_integral.html)
- [cppreference: std::is_integral](https://en.cppreference.com/w/cpp/types/is_integral)
