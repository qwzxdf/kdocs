---
title: std::uniform_real_distribution
summary: "範囲内の小数を、同じ確率で出す（上限は含まない）。"
order: 11
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::uniform_real_distribution

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::uniform_real_distribution` は、**`a` 以上 `b` 未満の小数を、どれも同じ確率で出す分布**です。ランダムな角度、位置、確率の判定（0〜1）に使います。**上限 `b` は含まれません**（`[a, b)`）。

!!! tip "ポイント"
    - `uniform_real_distribution<float> angle(0.0f, 360.0f);`
    - 確率の判定は `bernoulli_distribution` のほうが読みやすい。
    - `float` 版は、浮動小数点の丸めのせいで、まれに上限が出るという古い不具合報告がある（実装によっては注意）。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uniform_real_distribution {#uniform_real}

```cpp
template <class RealType = double>
class uniform_real_distribution {
 public:
  explicit uniform_real_distribution(RealType a, RealType b = 1.0);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 浮動小数点 | 最小値（含む） |
| `b` | 浮動小数点 | 最大値（**含まない**） |

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(7);
  std::uniform_real_distribution<float> angle(0.0f, 360.0f);
  float a = angle(rng);
  std::println("0 以上 360 未満？ {}", a >= 0.0f && a < 360.0f);
}
```

```text title="実行結果"
0 以上 360 未満？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランダムな角度・位置・速度 | `uniform_real_distribution<float> speed(1.0f, 3.0f);` |
| 敵のスポーン位置を範囲内でばらけさせる | `x = rx(rng); y = ry(rng);` |

## よくあるミス

??? failure "整数用の分布と取り違える"
    整数には `uniform_int_distribution` です。`uniform_real_distribution<int>` は未定義です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_int_distribution`](uniform_int_distribution.md) | 整数 |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 確率の判定 |
| [`normal_distribution`](normal_distribution.md) | 中心が出やすい |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `[a, b)` の小数を同じ確率で
    - [x] 上限は含まれない
    - [x] 確率の判定は `bernoulli`

## 関連ページ

- [cpprefjp: std::uniform_real_distribution](https://cpprefjp.github.io/reference/random/uniform_real_distribution.html)
- [cppreference: std::uniform_real_distribution](https://en.cppreference.com/w/cpp/numeric/random/uniform_real_distribution)
