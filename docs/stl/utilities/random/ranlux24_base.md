---
title: std::ranlux24_base
summary: "ranlux24 の土台になる、キャリーつき引き算法のエンジン。"
order: 900
tags:
  - ユーティリティ
---

# std::ranlux24_base

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`ranlux24` は高品質な乱数エンジンですが、その中身は `ranlux24_base` の出力を間引いたものです。`ranlux24_base` 自体は速いものの、単独では統計的な品質が劣ります。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranlux24_base {#ranlux24_base}

```cpp
using ranlux24_base = subtract_with_carry_engine<uint_fast32_t, 24, 10, 24>;
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
friend bool operator==(const ranlux24_base& a, const ranlux24_base& b);
```

- 計算量: O(状態の大きさ)

2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。

## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  std::ranlux24_base e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
7937952
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::ranlux24_base e{seed}; dist(e);` |

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
    - [x] ranlux24 の土台になる、キャリーつき引き算法のエンジン
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::ranlux24_base](https://cpprefjp.github.io/reference/random/ranlux24_base.html)
- [cppreference: std::ranlux24_base](https://en.cppreference.com/w/cpp/numeric/random/ranlux24_base)
