---
title: std::minstd_rand0
summary: "古典的な線形合同法の乱数エンジン（軽いが品質は低め）。"
order: 900
tags:
  - ユーティリティ
---

# std::minstd_rand0

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

状態が小さく、1 回の計算も軽い乱数エンジンが欲しいことがあります。`minstd_rand0` は、`x ← 16807 × x mod (2³¹−1)` で次の値を作る、最も素朴な線形合同法です。品質は低いので、本格的な用途には `mt19937` を使います。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::minstd_rand0 {#minstd_rand0}

```cpp
using minstd_rand0 = linear_congruential_engine<uint_fast32_t, 16807, 0, 2147483647>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | 整数 | 省略可。初期状態を決める値 |

- 戻り値: `operator()` で次の乱数を返す
- 計算量: 1 回あたり定数

### operator() {#op_call}

```cpp
result_type operator()();
```

- 計算量: 定数

次の乱数を返します。呼ぶたびに内部の状態が進みます。

### seed {#seed}

```cpp
void seed(result_type value = default_seed);
template <class SeedSeq> void seed(SeedSeq& seq);
```

- 計算量: O(状態の大きさ)

内部の状態をシードで初期化し直します。同じシードなら、同じ乱数の並びになります。

### discard {#discard}

```cpp
void discard(unsigned long long z);
```

- 計算量: O(z)

乱数を `z` 個ぶん、捨てて進めます。並びの途中から使いたいとき（セーブした位置から再開するなど）に使います。

### min {#min}

```cpp
static constexpr result_type min();
```

- 計算量: 定数

`operator()` が返しうる最小値。

### max {#max}

```cpp
static constexpr result_type max();
```

- 計算量: 定数

`operator()` が返しうる最大値。

### operator== {#op_eq}

```cpp
friend bool operator==(const minstd_rand0& a, const minstd_rand0& b);
```

- 計算量: O(状態の大きさ)

2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。

## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  std::minstd_rand0 e;  // 既定のシードは 1
  std::println("{}", e());
  std::println("{}", e());
}
```

```text title="実行結果"
16807
282475249
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::minstd_rand0 e{seed}; dist(e);` |

## よくあるミス

??? failure "シードを固定のまま使う"
    シードを与えないと毎回同じ並びになります。本番では `random_device` などで初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mt19937`](mt19937.md) | 標準的な高品質エンジン |
| [`default_random_engine`](default_random_engine.md) | 処理系おまかせ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 古典的な線形合同法の乱数エンジン（軽いが品質は低め）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::minstd_rand0](https://cpprefjp.github.io/reference/random/minstd_rand0.html)
- [cppreference: std::minstd_rand0](https://en.cppreference.com/w/cpp/numeric/random/minstd_rand0)
