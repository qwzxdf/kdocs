---
title: std::default_random_engine
summary: "実装が選ぶ既定の乱数エンジン。環境によって中身が違うので、再現性が必要なら使わない。"
order: 7
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::default_random_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::default_random_engine` は、**標準ライブラリの実装が「これでよい」と選んだ乱数エンジン**の別名です。環境によって中身が違います（MSVC では `mt19937`、libstdc++ では `minstd_rand0`）。そのため、**同じ種でも、環境が違うと違う列が出ます**。再現性が必要なゲームでは使わず、`std::mt19937` を指定します。

!!! tip "ポイント"
    - **環境で結果が変わる。** リプレイ・テスト・ネットワーク対戦では使わない。
    - 手早く試すだけのコードで使われることがある。
    - 本番は `std::mt19937`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::default_random_engine {#default_random_engine}

```cpp
using default_random_engine = /* 実装定義 */;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `seed` | 整数 | 種 | 実装による |

- 戻り値: `operator()` で整数を返す
- 計算量: O(1)

```cpp
#include <print>
#include <random>

int main() {
  std::default_random_engine a(7);
  std::default_random_engine b(7);
  std::println("同じ環境・同じ種なら同じ値？ {}", a() == b());
  // 値そのものは、環境（GCC / MSVC / Clang）によって違う
}
```

```text title="実行結果"
同じ環境・同じ種なら同じ値？ true
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
friend bool operator==(const default_random_engine& a, const default_random_engine& b);
```

- 計算量: O(状態の大きさ)

2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 試作で手早く乱数を使う | 本番では `std::mt19937` に置き換える |

## よくあるミス

??? failure "環境をまたいで結果を揃えようとする"
    PC 版とコンソール版で結果が違います。`std::mt19937` を使います（これも分布は環境で違う場合があるので注意）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](mt19937.md) | 中身が決まっている定番のエンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実装定義の既定エンジン
    - [x] 環境で結果が変わる
    - [x] 本番は `mt19937`

## 関連ページ

- [cpprefjp: std::default_random_engine](https://cpprefjp.github.io/reference/random/default_random_engine.html)
- [cppreference: std::default_random_engine](https://en.cppreference.com/w/cpp/numeric/random/default_random_engine)
