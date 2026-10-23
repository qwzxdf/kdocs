---
title: std::negation
summary: "型特性の結果を反転する。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::negation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

条件を反転したいとき、`!std::is_integral_v<T>` と書けますが、型の性質どうしの組み合わせ（`conjunction`、`disjunction`）の中では、型として反転した結果が欲しいことがあります。`std::negation` は、<strong>型の性質の結果を反転した型</strong>です。

!!! tip "ポイント"
    - `std::negation_v<B>` は `!B::value`
    - `B` はトレイト（`::value` を持つ型）
    - `conjunction` と `disjunction` の引数として使える
    - C++17 で追加

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::negation_v {#negation}

<span class="ver ver-17">C++17</span>

```cpp
template <class B>
inline constexpr bool negation_v = negation<B>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B` | トレイト | `::value` を持つ型 |

`negation<B>` は、`B::value` を反転した値を持つ型です。`conjunction<is_integral<T>, negation<is_signed<T>>>` のように、型の性質を論理式のように組み合わせるときに使います。

単独の否定なら `!B::value` や `!std::is_integral_v<T>` で足ります。`negation` が必要なのは、`conjunction` / `disjunction` の引数の中だけです。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("negation<is_integral<float>> = {}", std::negation_v<std::is_integral<float>>);
  std::println("negation<is_integral<int>>   = {}", std::negation_v<std::is_integral<int>>);
  // 符号なしの整数か: 整数かつ、符号つきではない
  std::println("unsigned は符号なし整数 = {}",
               std::conjunction_v<std::is_integral<unsigned>, std::negation<std::is_signed<unsigned>>>);
}
```

```text title="実行結果"
negation<is_integral<float>> = true
negation<is_integral<int>>   = false
unsigned は符号なし整数 = true
```

## ゲームでの使いどころ

複数の型の性質を、論理式のように組み合わせます（上のコード）。

## よくあるミス

??? failure "単独の否定にも使い、読みにくくなる"
    単独なら `!` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conjunction`](conjunction.md) | 論理積 |
| [`disjunction`](disjunction.md) | 論理和 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `negation_v<B>` は `!B::value`
    - [x] `conjunction` / `disjunction` の引数に使う
    - [x] 単独の否定は `!` で足りる

## 関連ページ

- [cpprefjp: std::negation](https://cpprefjp.github.io/reference/type_traits/negation.html)
- [cppreference: std::negation](https://en.cppreference.com/w/cpp/types/negation)
