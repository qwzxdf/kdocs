---
title: std::bool_constant
summary: "`bool` のコンパイル時の定数を、型として表す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::bool_constant

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`std::integral_constant<bool, 条件>` と書くのは、長くて読みにくいです。`std::bool_constant<条件>` は、その<strong>短縮形</strong>です。条件式をそのまま渡せます。

!!! tip "ポイント"
    - `std::bool_constant<(2 > 1)>::value` は `true`
    - `std::integral_constant<bool, B>` の別名
    - 条件式の `>` は括弧で囲む
    - C++17 で追加

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bool_constant {#bool_constant}

<span class="ver ver-17">C++17</span>

```cpp
template <bool B>
using bool_constant = integral_constant<bool, B>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B` | `bool` | 真偽値の定数式 |

`bool_constant<B>` は、`integral_constant<bool, B>` を短く書くための別名です。自作のトレイトを、条件式から直接作れます。

条件式に `>` を含むときは、テンプレート引数の閉じ括弧と区別するために、括弧で囲む必要があります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

// 型の大きさが 8 バイト以上か
template <class T>
struct IsLarge : std::bool_constant<(sizeof(T) >= 8)> {};

int main() {
  std::println("IsLarge<int>    = {}", IsLarge<int>::value);
  std::println("IsLarge<double> = {}", IsLarge<double>::value);
}
```

```text title="実行結果"
IsLarge<int>    = false
IsLarge<double> = true
```

## ゲームでの使いどころ

条件式から、自作のトレイトを短く書きます（上のコード）。

## よくあるミス

??? failure "条件式の `>` を括弧で囲まず、コンパイルエラーになる"
    `bool_constant<(a > b)>` のように括弧で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`integral_constant`](integral_constant.md) | 元の型 |
| [`true_type`](true_type.md) | 真を表す型 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bool_constant<B>` は `integral_constant<bool, B>` の短縮形
    - [x] 条件式の `>` は括弧で囲む
    - [x] 自作のトレイトを条件式から書ける

## 関連ページ

- [cpprefjp: std::bool_constant](https://cpprefjp.github.io/reference/type_traits/bool_constant.html)
- [cppreference: std::bool_constant](https://en.cppreference.com/w/cpp/types/integral_constant)
