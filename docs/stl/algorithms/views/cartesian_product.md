---
title: std::views::cartesian_product
summary: "複数の範囲の、すべての組み合わせを並べて見る。"
order: 39
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::cartesian_product

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::cartesian_product` は、**複数の範囲から 1 つずつ取る、すべての組み合わせ**を並べるビューです。「全マスの (x, y)」「全キャラ × 全スキル」のように、**二重（三重）ループ**を 1 つの範囲で書けます。

!!! tip "ポイント"
    - 最後の範囲が最も速く変わる（二重ループの内側）。
    - 組は tuple。構造化束縛で受ける。
    - 要素数は、各範囲の要素数の積になる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::cartesian_product {#cartesian_product}

```cpp
std::views::cartesian_product(r1, r2, ...)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r1, r2, ...` | 範囲 | 組み合わせを作る範囲（1 つ以上） |

- 戻り値: 全組み合わせの tuple を並べたビュー
- 計算量: O(1)（1 つ進めるたび）。全体では要素数の積

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> xs = {1, 2};
  std::vector<int> ys = {10, 20};

  for (auto [x, y] : std::views::cartesian_product(xs, ys)) {
    std::println("({}, {})", x, y);
  }
}
```

```text title="実行結果"
(1, 10)
(1, 20)
(2, 10)
(2, 20)
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| マップの全マス (x, y) を回す | `cartesian_product(iota(0, w), iota(0, h))` |
| 全キャラ × 全スキルの組み合わせを検証する | `cartesian_product(chars, skills)` |

## よくあるミス

??? failure "組み合わせが爆発する"
    3 つの範囲が各 100 個なら 100 万通りです。数が大きいときは注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::zip`](zip.md) | 同じ位置どうしの組（積ではない） |
| 二重の `for` | 従来の書き方。処理が複雑ならこちらのほうが読みやすいこともある |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全部の組み合わせを 1 つの範囲で
    - [x] 最後の範囲が最も速く変わる
    - [x] 要素数は積

## 関連ページ

- [cpprefjp: std::ranges::cartesian_product_view](https://cpprefjp.github.io/reference/ranges/cartesian_product_view.html)
- [cppreference: std::ranges::cartesian_product_view](https://en.cppreference.com/w/cpp/ranges/cartesian_product_view)
