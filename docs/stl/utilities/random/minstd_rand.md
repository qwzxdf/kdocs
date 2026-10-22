---
title: std::minstd_rand
summary: "軽い乱数エンジン（状態が 4 バイト）。品質は mt19937 より低い。"
order: 4
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::minstd_rand

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::minstd_rand` は、**状態がたった 4 バイトの、軽い乱数エンジン**です。「線形合同法」という単純な計算で作ります。`mt19937` より速い（状態も小さい）代わりに、品質は低めです。オブジェクトごとに小さなエンジンを持たせたい、品質は多少悪くてもよい、というときに使えます。`minstd_rand0` は古い定数の版です。

!!! tip "ポイント"
    - 状態が 4 バイト。数万個のオブジェクトが、それぞれ持っても重くならない。
    - 周期は約 21 億。長い列を使う用途には向かない。
    - 品質が気になるなら `mt19937`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::minstd_rand {#minstd_rand}

```cpp
using minstd_rand0 = std::linear_congruential_engine<std::uint_fast32_t, 16807, 0, 2147483647>;
using minstd_rand  = std::linear_congruential_engine<std::uint_fast32_t, 48271, 0, 2147483647>;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `seed` | `unsigned` | 種（0 は 1 として扱われる） | `1` |

- 戻り値: `operator()` で整数を返す
- 計算量: O(1)

```cpp
#include <print>
#include <random>

int main() {
  std::minstd_rand rng(1);
  std::println("{}", rng());   // 48271 × 1 mod (2^31 − 1)

  std::minstd_rand0 old(1);
  std::println("{}", old());   // 16807 × 1
}
```

```text title="実行結果"
48271
16807
```

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

内部の状態を、シードで初期化し直します。同じシードなら、同じ乱数の並びになります。

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
friend bool operator==(const minstd_rand& a, const minstd_rand& b);
```

- 計算量: O(状態の大きさ)

2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 体ごとに小さな乱数エンジンを持たせる（パーティクルなど） | `std::minstd_rand rng_;` |

## よくあるミス

??? failure "低い桁のばらつきが悪い"
    線形合同法は、下位のビットの質が低めです。`% 2` のような使い方は避け、分布（`uniform_int_distribution`）を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](mt19937.md) | 品質が高い定番 |
| [`std::default_random_engine`](default_random_engine.md) | 環境が選ぶ既定のエンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 状態 4 バイトの軽いエンジン
    - [x] 品質は低め
    - [x] 大量の小さなエンジンに向く

## 関連ページ

- [cpprefjp: std::minstd_rand](https://cpprefjp.github.io/reference/random/linear_congruential_engine.html)
- [cppreference: std::linear_congruential_engine](https://en.cppreference.com/w/cpp/numeric/random/linear_congruential_engine)
