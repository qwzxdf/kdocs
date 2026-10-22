---
title: std::common_comparison_category
summary: "複数の順序型から、全部を含む共通の順序型を求める。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::common_comparison_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`strong_ordering`・`weak_ordering`・`partial_ordering` のうち、複数のメンバが混ざった構造体の `<=>` の戻り値は、一番弱いものに合わせる必要があります。`common_comparison_category_t<...>` が、その型を求めます。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::common_comparison_category {#common_comparison_category}

```cpp
template <class... Ts>
struct common_comparison_category { using type = /* 共通の順序型 */; };
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Ts...` | 順序型 | 比べる順序型 |

- 戻り値: 共通の順序型（`::type`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <type_traits>

int main() {
  using R = std::common_comparison_category_t<std::strong_ordering, std::partial_ordering>;
  std::println("{}", std::is_same_v<R, std::partial_ordering>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | メンバごとに順序型が違う構造体の `<=>` の戻り値を決める |

## よくあるミス

??? failure "強い順序型と思い込む"
    1 つでも `partial_ordering`（`double` など）が混ざると、全体が `partial_ordering` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`partial_ordering`](partial_ordering.md) | 半順序 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の順序型から、全部を含む共通の順序型を求める
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::common_comparison_category](https://cpprefjp.github.io/reference/compare/common_comparison_category.html)
- [cppreference: std::common_comparison_category](https://en.cppreference.com/w/cpp/utility/common_comparison_category)
