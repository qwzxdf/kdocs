---
title: std::ranlux24
summary: "品質が非常に高いが、遅い乱数エンジン（24 ビット / 48 ビット版）。"
order: 5
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::ranlux24

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::ranlux24` と `std::ranlux48` は、**品質を最優先にした乱数エンジン**です。`mt19937` より**ずっと遅い**ので、ゲームではほとんど使いません。科学計算のように、乱数の質が結果を左右するときの選択肢です。

!!! tip "ポイント"
    - `ranlux24` は 24 ビットの値、`ranlux48` は 48 ビットの値を出す。
    - ゲームでは `mt19937` で十分。
    - 速度を気にしない、品質重視の計算用。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### ranlux24, ranlux48 {#ranlux24}

```cpp
using ranlux24 = std::discard_block_engine<std::ranlux24_base, 223, 23>;
using ranlux48 = std::discard_block_engine<std::ranlux48_base, 389, 11>;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `seed` | 整数 | 種 | `19780503` |

- 戻り値: `operator()` で 24（または 48）ビットの整数を返す
- 計算量: O(1)（mt19937 より遅い）

```cpp
#include <print>
#include <random>

int main() {
  std::println("24: {} 〜 {}", std::ranlux24::min(), std::ranlux24::max());
  std::println("48: {} 〜 {}", std::ranlux48::min(), std::ranlux48::max());
}
```

```text title="実行結果"
24: 0 〜 16777215
48: 0 〜 281474976710655
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
friend bool operator==(const ranlux24& a, const ranlux24& b);
```

- 計算量: O(状態の大きさ)

2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 品質が必要なシミュレーション（ゲームではほとんど不要） | `std::ranlux48 rng;` |

## よくあるミス

??? failure "ゲームの乱数に使って重くなる"
    `mt19937` の数倍遅いことがあります。ゲームでは `mt19937` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](mt19937.md) | 速くて品質も十分な定番 |
| [`std::knuth_b`](knuth_b.md) | 並べ替えを使った別のエンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 品質重視で遅いエンジン
    - [x] ゲームでは `mt19937`
    - [x] `ranlux24` と `ranlux48`

## 関連ページ

- [cpprefjp: std::ranlux24](https://cpprefjp.github.io/reference/random/discard_block_engine.html)
- [cppreference: std::discard_block_engine](https://en.cppreference.com/w/cpp/numeric/random/discard_block_engine)
