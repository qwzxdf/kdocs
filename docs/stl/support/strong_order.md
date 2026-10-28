---
title: std::strong_order
summary: "強い順序（等しいものは区別できない）で比べる。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::strong_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`<=>` が使えない型や、使えても意味が足りない型（浮動小数点数の NaN や符号つきゼロ）を指定した強さの順序で比べたい。`std::strong_order` は、<strong>2 つの値を全順序で比較する</strong>関数オブジェクトです。

!!! tip "ポイント"
    - `std::strong_order(a, b)` は `std::strong_ordering` を返す
    - 浮動小数点数の NaN や `-0.0` の扱いが、順序の強さで違う
    - `<=>` があればそれをなければ代わりの手段を探す
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strong_order {#strong_order}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* カスタマイズ ポイント オブジェクト */ strong_order;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 値 | 1 つ目の値 |
| `b` | 値 | 2 つ目の値 |

`std::strong_order` は、2 つの値を比べて `std::strong_ordering` の値を返します。浮動小数点数に対しては、型ごとに決まった規則で、NaN や符号つきゼロも比べられます。

`strong_order` は、すべての値（NaN を含む）に全順序を与えます。`-0.0` と `0.0` も区別します。`weak_order` は `-0.0` と `0.0` を同値とし、NaN は一番大きい値として扱います。`partial_order` は、NaN を含む比較を `unordered` とします。

用途は、浮動小数点数を含む値の並べ替えです。NaN が混ざっていても、順序が壊れない並べ替えには `strong_order` や `weak_order` を使います。

## 実際に動かしてみる

```cpp
#include <compare>
#include <limits>
#include <print>

int main() {
  [[maybe_unused]] const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("strong_order(-0.0, 0.0) は less : {}", std::strong_order(-0.0, 0.0) == std::strong_ordering::less);
}
```

```text title="実行結果"
strong_order(-0.0, 0.0) は less : true
```

## ゲームでの使いどころ

浮動小数点数の配列を NaN が混ざっても壊れずに並べ替えるときに使います。

```cpp
std::ranges::sort(values, [](double a, double b) { return std::is_lt(std::weak_order(a, b)); });
```

## よくあるミス

??? failure "`<` で NaN を含む配列を並べ替えて、順序が壊れる"
    `weak_order` か `strong_order` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_order`](strong_order.md) | 全順序 |
| [`weak_order`](weak_order.md) | 弱順序 |
| [`partial_order`](partial_order.md) | 半順序 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strong_order(a, b)` は全順序で比較する
    - [x] 浮動小数点数の NaN や `-0.0` を扱える
    - [x] 並べ替えを壊さないために使う

## 関連ページ

- [cpprefjp: std::strong_order](https://cpprefjp.github.io/reference/compare/strong_order.html)
- [cppreference: std::strong_order](https://en.cppreference.com/w/cpp/utility/strong_order)
