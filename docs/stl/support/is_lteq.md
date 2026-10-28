---
title: std::is_lteq
summary: "順序型の結果が「以下」かを `bool` で返す。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::is_lteq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

三方比較 `a <=> b` の結果は、`less`、`equal`、`greater` のような値で、`<` や `==` の真偽値ではありません。`std::is_lteq` は、<strong>三方比較の結果が「以下」かを `bool` で返します</strong>。

!!! tip "ポイント"
    - `std::is_lteq(a <=> b)` は、`a` と `b` が「以下」のとき `true`
    - `a <=> b` の結果（`strong_ordering` など）を受け取る
    - 結果の値を `0` と比べる書き方（`r < 0`）の読みやすい版
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_lteq {#is_lteq}

<span class="ver ver-20">C++20</span>

```cpp
constexpr bool is_lteq(std::partial_ordering cmp) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `cmp` | `partial_ordering` など | `<=>` の結果 |

三方比較の結果は、`0` との比較演算子で判定できます（`r < 0`、`r == 0`）。`is_lteq` は、その判定に名前を付けた関数です。

`std::partial_ordering`、`std::weak_ordering`、`std::strong_ordering` のどれでも受け取れます（後者の 2 つは、前者に変換できるためです）。浮動小数点数の比較で `unordered`（NaN を含むとき）が返る場合、`is_lteq` は `false` を返します。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  std::println("is_lteq(1 <=> 1) = {}", std::is_lteq(1 <=> 1));
  std::println("is_lteq(2 <=> 1) = {}", std::is_lteq(2 <=> 1));
}
```

```text title="実行結果"
is_lteq(1 <=> 1) = true
is_lteq(2 <=> 1) = false
```

## ゲームでの使いどころ

自作の型の `operator<=>` を使った比較の結果を読みやすく判定します。

```cpp
auto result = a <=> b;
if (std::is_lt(result)) { /* a が b より小さい */ }
```

## よくあるミス

??? failure "`unordered` を考えず、NaN の比較で意図しない結果になる"
    `partial_ordering` では `unordered` のとき、すべて `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_ordering`](strong_ordering.md) | 全順序を表す型 |
| [`partial_ordering`](partial_ordering.md) | 順序が決まらない場合を含む型 |
| [`three_way_comparable`](three_way_comparable.md) | `<=>` が使えるか |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `is_lteq(cmp)` は三方比較の結果が「以下」か
    - [x] `partial_ordering` / `weak_ordering` / `strong_ordering` を受け取る
    - [x] `unordered` のときは `false`

## 関連ページ

- [cpprefjp: std::is_lteq](https://cpprefjp.github.io/reference/compare/is_lteq.html)
- [cppreference: std::is_lteq](https://en.cppreference.com/w/cpp/utility/is_lteq)
