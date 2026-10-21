---
title: std::generate_canonical
summary: "エンジンから、[0, 1) の小数の乱数を直接作る。"
order: 30
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::generate_canonical

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::generate_canonical` は、**乱数エンジンから、0 以上 1 未満の小数を直接作る**関数です。`uniform_real_distribution<>(0, 1)` と同じ結果が得られ、使う精度（ビット数）を指定できます。普通は `uniform_real_distribution` を使い、この関数は分布を自作するときの部品として使います。

!!! tip "ポイント"
    - 戻り値は `[0, 1)`。
    - `generate_canonical<double, 53>(rng)` のように、型とビット数を指定する。
    - 自作の分布を作るときの部品。普段は `uniform_real_distribution`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::generate_canonical {#generate_canonical}

```cpp
template <class RealType, std::size_t Bits, class URBG>
RealType generate_canonical(URBG& g);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `RealType` | テンプレート引数 | 返す小数の型 |
| `Bits` | テンプレート引数 | 使う乱数のビット数 |
| `g` | エンジン | 乱数エンジン |

- 戻り値: `[0, 1)` の小数
- 計算量: O(1)

```cpp
#include <limits>
#include <print>
#include <random>

int main() {
  std::mt19937 rng(42);
  double x = std::generate_canonical<double, std::numeric_limits<double>::digits>(rng);
  std::println("0 以上 1 未満？ {}", x >= 0.0 && x < 1.0);
}
```

```text title="実行結果"
0 以上 1 未満？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の乱数分布を作る部品 | `generate_canonical` から変換する |

## よくあるミス

??? failure "普通の乱数に使う"
    範囲を決めたいだけなら `uniform_real_distribution` のほうが簡単です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 範囲を指定して小数を出す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エンジンから [0, 1) の小数を作る
    - [x] 分布の自作用
    - [x] 普通は `uniform_real_distribution`

## 関連ページ

- [cpprefjp: std::generate_canonical](https://cpprefjp.github.io/reference/random/generate_canonical.html)
- [cppreference: std::generate_canonical](https://en.cppreference.com/w/cpp/numeric/random/generate_canonical)
