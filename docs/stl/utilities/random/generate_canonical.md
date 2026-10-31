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
`#include <chrono>`
</div>

0 以上 1 未満の小数の乱数が欲しいとき、普通は `uniform_real_distribution<double>(0.0, 1.0)` を使います。その内部で呼ばれている関数が `std::generate_canonical` です。エンジンの整数の出力を、指定したビット数ぶんだけ集めて、`[0, 1)` の小数に変換します。

!!! tip "ポイント"
    - `generate_canonical<double, 53>(rng)` で、`[0, 1)` の `double` が得られる
    - 第 2 引数 `Bits` は、使うビット数。`numeric_limits<double>::digits` が 53
    - 普段は `uniform_real_distribution` で足りる
    - 丸めの都合で、まれに `1.0` が返る実装がある

!!! info "このページを読む前に"
    [`std::uniform_real_distribution`](uniform_real_distribution.md) を先に読んでください。

## 関数の詳しい説明

### std::generate_canonical {#generate_canonical}

<span class="ver ver-11">C++11</span>

```cpp
template <class RealType, size_t Bits, class URBG>
RealType generate_canonical(URBG& g);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `RealType` | テンプレート引数 | 返す小数の型（`double` など） |
| `Bits` | テンプレート引数 | 使う乱数のビット数 |
| `g` | `URBG&` | 乱数エンジン |

エンジンの出力が `Bits` ビットに足りなければ、複数回呼んで、組み合わせます。たとえば `mt19937` の 32 ビットの出力から、53 ビットの `double` を作るには、2 回呼びます。

`Bits` には、`std::numeric_limits<RealType>::digits` を渡すのが標準的で、`double` なら 53、`float` なら 24 です。

戻り値は `[0, 1)` のはずですが、規格のとおりに実装すると、`float` の丸めで `1.0` になることがある、という既知の問題（LWG 2524）があります。実装によっては、1 未満に収める処理が入っています。確実に 1 未満が要るなら、結果が 1 なら引き直す、などの防御を書きます。

## 実際に動かしてみる

```cpp
#include <limits>
#include <print>
#include <random>

int main() {
  std::mt19937 rng(42);

  const double x = std::generate_canonical<double, std::numeric_limits<double>::digits>(rng);
  std::println("0 以上 1 未満: {}", x >= 0.0 && x < 1.0);

  // 平均は 0.5 に近い
  double sum = 0.0;
  for (int i = 0; i < 10000; ++i) {
    sum += std::generate_canonical<double, 53>(rng);
  }
  const double mean = sum / 10000;
  std::println("平均は 0.5 の近く: {}", mean > 0.48 && mean < 0.52);
}
```

```text title="実行結果"
0 以上 1 未満: true
平均は 0.5 の近く: true
```

## ゲームでの使いどころ

「確率 30% で発動」のような判定を、`generate_canonical<double, 53>(rng) < 0.3` と書けます。普段は `uniform_real_distribution` か `bernoulli_distribution` を使うほうが、意図が読み取りやすくなります。

## よくあるミス

??? failure "float で 1.0 が返る可能性を考えない"
    `float` で使うと、まれに `1.0f` が返る実装があります。上限を前提にした配列の添字などに使うときは、気をつけます。

??? failure "Bits をエンジンのビット数にする"
    `Bits` は、結果の精度のビット数です。`double` なら 53 を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 範囲を指定した小数。普段はこちら |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 確率で true / false |
| [`mt19937`](mt19937.md) | 渡すエンジン |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::generate_canonical](https://cpprefjp.github.io/reference/random/generate_canonical.html)
- [cppreference: std::generate_canonical](https://en.cppreference.com/w/cpp/numeric/random/generate_canonical)
