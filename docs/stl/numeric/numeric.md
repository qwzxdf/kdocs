---
title: <numeric>（gcd / lcm / midpoint など）
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

!!! tip "結論"
    - 合計は [`std::accumulate` / `std::ranges::fold_left`](../algorithms/accumulate.md)、連番は [`std::iota`](../algorithms/copy_fill.md#iota)。
    - 最大公約数・最小公倍数は `std::gcd` / `std::lcm`（画面比、周期の計算）。
    - 2 つの値の真ん中は `(a + b) / 2` ではなく `std::midpoint(a, b)`（あふれない）。
    - 累積和（前から足していった値の列）は `std::partial_sum` / `std::inclusive_scan`。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::accumulate`](../algorithms/accumulate.md#accumulate) | <span class="rank rank-sometimes">たまに</span> | 合計（別ページ） |
| [`std::iota`](../algorithms/copy_fill.md#iota) | <span class="rank rank-sometimes">たまに</span> | 連番で埋める（別ページ） |
| [`std::gcd`](#gcd) | <span class="rank rank-sometimes">たまに</span> | 最大公約数 <span class="ver ver-17">C++17</span> |
| [`std::lcm`](#lcm) | <span class="rank rank-sometimes">たまに</span> | 最小公倍数 <span class="ver ver-17">C++17</span> |
| [`std::midpoint`](#midpoint) | <span class="rank rank-sometimes">たまに</span> | 真ん中の値（あふれない） <span class="ver ver-20">C++20</span> |
| [`std::partial_sum`](#partial_sum) | <span class="rank rank-sometimes">たまに</span> | 累積和 |
| [`std::inclusive_scan`](#inclusive_scan) | <span class="rank rank-rare">知ってるだけ</span> | 累積和（並列化できる版） <span class="ver ver-17">C++17</span> |
| [`std::exclusive_scan`](#exclusive_scan) | <span class="rank rank-rare">知ってるだけ</span> | 自分を含まない累積和 <span class="ver ver-17">C++17</span> |
| [`std::adjacent_difference`](#adjacent_difference) | <span class="rank rank-rare">知ってるだけ</span> | 隣との差 |
| [`std::inner_product`](#inner_product) | <span class="rank rank-rare">知ってるだけ</span> | 内積（掛けて足す） |
| [`std::transform_reduce`](#transform_reduce) | <span class="rank rank-rare">知ってるだけ</span> | 変換してから合計（並列化できる） <span class="ver ver-17">C++17</span> |
| [`std::reduce`](../algorithms/accumulate.md#reduce) | <span class="rank rank-rare">知ってるだけ</span> | 順番を問わない合計（別ページ） |

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

（同じことは [`std::discrete_distribution`](../utilities/random.md#discrete) でもできます。）

## 関数の詳しい説明

### std::gcd {#gcd}

<span class="ver ver-17">C++17</span>

```cpp
template <class M, class N>
constexpr std::common_type_t<M, N> gcd(M m, N n);
```

- 最大公約数（両方を割り切れる一番大きい数）。整数のみ

### std::lcm {#lcm}

<span class="ver ver-17">C++17</span>

```cpp
template <class M, class N>
constexpr std::common_type_t<M, N> lcm(M m, N n);
```

- 最小公倍数（両方で割り切れる一番小さい数）。周期の違う 2 つのイベントが次に重なるタイミングの計算などに使えます

```cpp
#include <numeric>
#include <print>

int main() {
  int w = 1920;
  int h = 1080;
  int g = std::gcd(w, h);
  std::println("画面比 {}:{}", w / g, h / g);
  std::println("3 秒ごとと 4 秒ごとのイベントは {} 秒ごとに重なる", std::lcm(3, 4));
}
```

```text title="実行結果"
画面比 16:9
3 秒ごとと 4 秒ごとのイベントは 12 秒ごとに重なる
```

### std::midpoint {#midpoint}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T midpoint(T a, T b) noexcept;  // 整数・浮動小数点
template <class T>
constexpr T* midpoint(T* a, T* b);        // ポインタ
```

- `a` と `b` の真ん中。`(a + b) / 2` は大きい整数どうしだと足し算であふれますが、midpoint はあふれません。整数のときは `a` 寄りに丸めます

```cpp
#include <climits>
#include <numeric>
#include <print>

int main() {
  int a = INT_MAX - 2;
  int b = INT_MAX;
  std::println("{}", std::midpoint(a, b) == INT_MAX - 1);
  std::println("{} {}", std::midpoint(1, 4), std::midpoint(4, 1));
}
```

```text title="実行結果"
true
2 3
```

### std::partial_sum {#partial_sum}

```cpp
template <class InputIt, class OutputIt>
OutputIt partial_sum(InputIt first, InputIt last, OutputIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 元の範囲 |
| `d_first` | 出力イテレータ | 結果を書く先（元と同じでもいい） |

- `[a, b, c]` → `[a, a+b, a+b+c]`

### std::inclusive_scan {#inclusive_scan}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class OutputIt>
OutputIt inclusive_scan(InputIt first, InputIt last, OutputIt d_first);
```

- `partial_sum` と同じ結果ですが、並列実行（`std::execution::par`）ができます

### std::exclusive_scan {#exclusive_scan}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class OutputIt, class T>
OutputIt exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init);
```

- 自分を**含まない**累積和：`[a, b, c]` → `[init, init+a, init+a+b]`。「各グループが何番目から始まるか」を出すのに使えます

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> counts = {3, 1, 4};  // 各種類の敵の数
  std::vector<int> start(counts.size());
  std::exclusive_scan(counts.begin(), counts.end(), start.begin(), 0);
  std::vector<int> total(counts.size());
  std::inclusive_scan(counts.begin(), counts.end(), total.begin());
  std::println("開始位置 {} / 累計 {}", start, total);
}
```

```text title="実行結果"
開始位置 [0, 3, 4] / 累計 [3, 4, 8]
```

### std::adjacent_difference {#adjacent_difference}

```cpp
template <class InputIt, class OutputIt>
OutputIt adjacent_difference(InputIt first, InputIt last, OutputIt d_first);
```

- 隣との差：`[a, b, c]` → `[a, b-a, c-b]`。毎フレームの位置の記録から速度を出すのに使えます

### std::inner_product {#inner_product}

```cpp
template <class InputIt1, class InputIt2, class T>
T inner_product(InputIt1 first1, InputIt1 last1, InputIt2 first2, T init);
```

- 2 つの範囲の要素を掛けて足し合わせます（内積）

### std::transform_reduce {#transform_reduce}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt1, class InputIt2, class T>
T transform_reduce(InputIt1 first1, InputIt1 last1, InputIt2 first2, T init);
```

- inner_product の並列化できる版です

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> positions = {0, 3, 7, 12};
  std::vector<int> velocity(positions.size());
  std::adjacent_difference(positions.begin(), positions.end(), velocity.begin());
  std::println("{}", velocity);

  std::vector<int> price = {100, 50};
  std::vector<int> count = {2, 3};
  std::println("{} {}", std::inner_product(price.begin(), price.end(), count.begin(), 0),
               std::transform_reduce(price.begin(), price.end(), count.begin(), 0));
}
```

```text title="実行結果"
[0, 3, 4, 5]
350 350
```

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

## 理解度チェック

!!! question "Q1. `std::partial_sum` で `[1, 2, 3, 4]` は何になる？"
    <div class="spoiler" markdown>

    **答え:** `[1, 3, 6, 10]`。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] gcd / lcm で約数・倍数
    - [x] 真ん中は midpoint
    - [x] 累積和は partial_sum

## 関連ページ

- [std::accumulate](../algorithms/accumulate.md)
- [cppreference: Numerics library](https://en.cppreference.com/w/cpp/numeric)
