---
title: std::compare_three_way
summary: "`<=>` を関数オブジェクトにしたもの。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_three_way

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`a <=> b` を、関数として渡したい場面があります。たとえば、アルゴリズムに比較関数を渡すとき。`std::compare_three_way` は、<strong>`<=>` を呼ぶ関数オブジェクト</strong>です。`std::less<>` の三方比較版です。

!!! tip "ポイント"
    - `std::compare_three_way{}(a, b)` は `a <=> b`
    - 関数オブジェクトなので、アルゴリズムの引数に渡せる
    - `std::less<>` と同様、型を指定しなくてよい
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::compare_three_way {#compare_three_way}

<span class="ver ver-20">C++20</span>

```cpp
struct compare_three_way {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(std::forward<T>(t) <=> std::forward<U>(u));
};
```

`compare_three_way{}(a, b)` は `a <=> b` を返します。結果は `strong_ordering` などの順序型です。`std::lexicographical_compare_three_way` のような、三方比較を使うアルゴリズムの既定の比較関数として使われます。

型を問わず使えるので、`std::less<>` と同じ感覚で書けます。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  std::compare_three_way cmp;
  std::println("cmp(1, 2) は less    : {}", cmp(1, 2) == std::strong_ordering::less);
  std::println("cmp(2, 2) は equal   : {}", cmp(2, 2) == std::strong_ordering::equal);
}
```

```text title="実行結果"
cmp(1, 2) は less    : true
cmp(2, 2) は equal   : true
```

## ゲームでの使いどころ

三方比較を受け取るアルゴリズムに、既定の比較として渡します。

## よくあるミス

??? failure "結果を `bool` と思う"
    結果は順序型です。`std::is_lt` などで判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_three_way_result`](compare_three_way_result.md) | 結果の型 |
| [`less`](functional/less.md) | `<` の関数オブジェクト |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `compare_three_way` は `<=>` の関数オブジェクト
    - [x] 型を指定せずに使える
    - [x] 結果は順序型

## 関連ページ

- [cpprefjp: std::compare_three_way](https://cpprefjp.github.io/reference/compare/compare_three_way.html)
- [cppreference: std::compare_three_way](https://en.cppreference.com/w/cpp/utility/compare_three_way)
