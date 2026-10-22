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

`<=>` は型によって結果の強さが違います。`strong_order(a, b)` は、`strong_ordering` を必ず返す比較で、型が `<=>` を持たなくても、浮動小数点なら全順序のルールに従って比べます。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::strong_order {#strong_order}

```cpp
inline constexpr /* カスタマイズポイント */ strong_order;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a, b` | 型 | 比べる 2 つの値 |

- 戻り値: `std::strong_ordering`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <compare>
#include <print>

int main() {
  std::println("{}", std::is_lt(std::strong_order(1, 2)));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 浮動小数点も含めて、一貫した順序で整列する |

## よくあるミス

??? failure "浮動小数点で `<` と混ぜる"
    `strong_order` は NaN を含めた順序を決めます。`<` の結果とは違うことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_ordering`](strong_ordering.md) | 結果の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 強い順序（等しいものは区別できない）で比べる
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strong_order](https://cpprefjp.github.io/reference/compare/strong_order.html)
- [cppreference: std::strong_order](https://en.cppreference.com/w/cpp/utility/strong_order)
