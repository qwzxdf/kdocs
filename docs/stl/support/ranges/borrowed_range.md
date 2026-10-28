---
title: std::ranges::borrowed_range
summary: "元の範囲より長生きするイテレータを返せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::borrowed_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

一時的な `vector` に `std::ranges::find` を呼ぶと、結果のイテレーターは、すぐに破棄された `vector` を指すことになります。そうした危険な呼び出しを避けるために、範囲には「借用できる」という性質があります。`std::ranges::borrowed_range<R>` は、<strong>R のイテレーターが、R が破棄されたあとも有効か</strong>を表すコンセプトです。

!!! tip "ポイント"
    - `std::ranges::borrowed_range<R>`: 一時オブジェクトのイテレーターを返しても安全か
    - 左辺値参照の範囲（`std::vector<int>&`）は満たす
    - 一時的な `std::vector<int>` は満たさない
    - `std::string_view` や `std::span` は、元データを借りるだけなので満たす

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::borrowed_range {#borrowed_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept borrowed_range = range<T> &&
    (std::is_lvalue_reference_v<T> || enable_borrowed_range<std::remove_cvref_t<T>>);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

範囲のアルゴリズムは、借用できない範囲（一時的な値）に対して呼ぶと、イテレーターの代わりに `std::ranges::dangling` を返します。ぶら下がった参照を使ってしまう事故を、型で防ぐ仕組みです。

`std::span` や `std::string_view` のように、データを所有せず、見ているだけの型は、範囲が破棄されてもイテレーターが有効です。そうした型は `enable_borrowed_range` を `true` にして、借用可能と宣言します。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <string_view>
#include <vector>

int main() {
  std::println("vector<int>&         : {}", std::ranges::borrowed_range<std::vector<int>&>);
  std::println("vector<int>（一時）  : {}", std::ranges::borrowed_range<std::vector<int>>);
  std::println("string_view          : {}", std::ranges::borrowed_range<std::string_view>);
}
```

```text title="実行結果"
vector<int>&         : true
vector<int>（一時）  : false
string_view          : true
```

## ゲームでの使いどころ

範囲を受け取り、イテレーターを返す自作の関数で、一時オブジェクトを弾きます。

```cpp
template <std::ranges::borrowed_range R>
auto FindFirst(R&& r);   // 一時オブジェクトは受け付けない
```

## よくあるミス

??? failure "一時的な範囲のイテレーターを使って、未定義動作になる"
    `dangling` が返る呼び方は避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dangling`](dangling.md) | 借用できないときの戻り値 |
| [`borrowed_iterator_t`](borrowed_iterator_t.md) | 借用できるときだけイテレーター |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `borrowed_range<R>` はイテレーターが範囲の破棄後も有効か
    - [x] 一時的なコンテナは満たさない
    - [x] `string_view` や `span` は満たす

## 関連ページ

- [cpprefjp: std::ranges::borrowed_range](https://cpprefjp.github.io/reference/ranges/borrowed_range.html)
- [cppreference: std::ranges::borrowed_range](https://en.cppreference.com/w/cpp/ranges/borrowed_range)
