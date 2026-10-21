---
title: std::bernoulli_distribution
summary: "確率 p で true、そうでなければ false を出す。"
order: 12
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::bernoulli_distribution

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::bernoulli_distribution` は、**確率 `p` で `true`、`1 - p` で `false` を出す分布**です。「30% で会心」「5% でレアドロップ」のような判定に使います。`uniform_real(0, 1) < 0.3f` と書くより、意図がはっきりします。

!!! tip "ポイント"
    - `bernoulli_distribution crit(0.3);` は 30% で `true`。
    - `p` は 0.0〜1.0。範囲外は未定義。
    - 複数回の試行の合計は [`binomial_distribution`](binomial_distribution.md)。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bernoulli_distribution {#bernoulli}

```cpp
class bernoulli_distribution {
 public:
  explicit bernoulli_distribution(double p = 0.5);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `double` | true が出る確率（0.0〜1.0） |

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(3);
  std::bernoulli_distribution always(1.0);
  std::bernoulli_distribution never(0.0);
  std::println("{} {}", always(rng), never(rng));
}
```

```text title="実行結果"
true false
```

!!! note "実際は"
    「30% で会心」「5% でレアドロップ」のような判定は、`uniform_real(0,1) < 0.3f` と書くより、こちらのほうが意図がはっきりします。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 会心の判定 | `crit(rng)` |
| レアドロップの判定 | `bernoulli_distribution rare(0.05);` |

## よくあるミス

??? failure "p を百分率で渡す"
    30% は `0.3` です。`30` を渡すと範囲外で未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 0〜1 の小数との比較でも書ける |
| [`discrete_distribution`](discrete_distribution.md) | 3 つ以上の選択肢 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確率 p で true
    - [x] p は 0〜1
    - [x] 会心・ドロップの判定

## 関連ページ

- [cpprefjp: std::bernoulli_distribution](https://cpprefjp.github.io/reference/random/bernoulli_distribution.html)
- [cppreference: std::bernoulli_distribution](https://en.cppreference.com/w/cpp/numeric/random/bernoulli_distribution)
