---
title: <numeric>（gcd / lcm / midpoint など）
summary: "最大公約数（`gcd`）、最小公倍数、中間値、累積和など。"
order: 74
tags:
  - 数値
---

# &lt;numeric&gt;（gcd / lcm / midpoint など）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`<numeric>` は、**数値の範囲や整数についての便利な関数**をまとめたヘッダです。合計を出す `std::accumulate`、連番を作る `std::iota` のほかに、最大公約数 `std::gcd`、最小公倍数 `std::lcm`、オーバーフローしない中間値 `std::midpoint`、飽和演算（C++26）などがあります。

!!! tip "ポイント"
    - 合計は [`std::accumulate` / `std::ranges::fold_left`](../algorithms/accumulate.md)、連番は [`std::iota`](../algorithms/iota.md#iota)。
    - 最大公約数・最小公倍数は `std::gcd` / `std::lcm`（画面比、周期の計算）。
    - 2 つの値の真ん中は `(a + b) / 2` ではなく `std::midpoint(a, b)`（あふれない）。
    - 累積和（前から足していった値の列）は `std::partial_sum` / `std::inclusive_scan`。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::accumulate`](../algorithms/accumulate.md#accumulate) | <span class="rank rank-sometimes">たまに</span> | 合計（別ページ） |
| [`std::iota`](../algorithms/iota.md#iota) | <span class="rank rank-sometimes">たまに</span> | 連番で埋める（別ページ） |
| [`std::gcd`](gcd.md) | <span class="rank rank-sometimes">たまに</span> | 最大公約数 <span class="ver ver-17">C++17</span> |
| [`std::lcm`](lcm.md) | <span class="rank rank-sometimes">たまに</span> | 最小公倍数 <span class="ver ver-17">C++17</span> |
| [`std::midpoint`](midpoint.md) | <span class="rank rank-sometimes">たまに</span> | 真ん中の値（あふれない） <span class="ver ver-20">C++20</span> |
| [`std::partial_sum`](../algorithms/partial_sum.md) | <span class="rank rank-sometimes">たまに</span> | 累積和 |
| [`std::inclusive_scan`](../algorithms/inclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 累積和（並列化できる版） <span class="ver ver-17">C++17</span> |
| [`std::exclusive_scan`](../algorithms/exclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 自分を含まない累積和 <span class="ver ver-17">C++17</span> |
| [`std::adjacent_difference`](../algorithms/adjacent_difference.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣との差 |
| [`std::inner_product`](../algorithms/inner_product.md) | <span class="rank rank-rare">知ってるだけ</span> | 内積（掛けて足す） |
| [`std::transform_reduce`](../algorithms/transform_reduce.md) | <span class="rank rank-rare">知ってるだけ</span> | 変換してから合計（並列化できる） <span class="ver ver-17">C++17</span> |
| [`std::reduce`](../algorithms/reduce.md#reduce) | <span class="rank rank-rare">知ってるだけ</span> | 順番を問わない合計（別ページ） |

## よくある使い方

### 確率テーブルから累積和で抽選する

```cpp
#include <algorithm>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> weights = {70, 25, 5};  // ノーマル・レア・スーパーレア
  std::vector<int> cumulative(weights.size());
  std::partial_sum(weights.begin(), weights.end(), cumulative.begin());
  std::println("累積: {}", cumulative);  // [70, 95, 100]

  int roll = 80;  // 本当は 0〜99 の乱数
  auto it = std::ranges::upper_bound(cumulative, roll);
  std::println("当たったのは {} 番", it - cumulative.begin());
}
```

```text title="実行結果"
累積: [70, 95, 100]
当たったのは 1 番
```

（同じことは [`std::discrete_distribution`](../utilities/random/discrete_distribution.md#discrete) でもできます。）

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 画面比・グリッドの割り切れる大きさ | `gcd` |
| 周期の違うイベントの重なり | `lcm` |
| 重み付き抽選の準備 | `partial_sum` |
| 二分探索の真ん中 | `midpoint` |
| 購入金額の合計（単価 × 個数） | `inner_product` |

## よくあるミス

??? failure "gcd に浮動小数点を渡す"
    `std::gcd` は整数専用です。

??? failure "(a + b) / 2 であふれる"
    大きい int どうしだと足し算でオーバーフロー（未定義動作）します。`std::midpoint` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] gcd / lcm で約数・倍数
    - [x] 真ん中は midpoint
    - [x] 累積和は partial_sum

## 関連ページ

- [std::accumulate](../algorithms/accumulate.md)
- [cppreference: Numerics library](https://en.cppreference.com/w/cpp/numeric)
