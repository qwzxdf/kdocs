---
title: std::partial_order
summary: "半順序（比べられない場合がある）で比べる。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::partial_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`partial_order(a, b)` は `partial_ordering` を返す比較です。NaN のように比べられない値の組は `unordered` になります。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::partial_order {#partial_order}

```cpp
inline constexpr /* カスタマイズポイント */ partial_order;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a, b` | 型 | 比べる 2 つの値 |

- 戻り値: `std::partial_ordering`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <compare>
#include <print>

int main() {
  std::println("{}", std::partial_order(1.0, std::nan("")) == std::partial_ordering::unordered);
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
    `partial_order` は NaN を含めた順序を決めます。`<` の結果とは違うことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`partial_ordering`](partial_ordering.md) | 結果の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半順序（比べられない場合がある）で比べる
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::partial_order](https://cpprefjp.github.io/reference/compare/partial_order.html)
- [cppreference: std::partial_order](https://en.cppreference.com/w/cpp/utility/partial_order)
