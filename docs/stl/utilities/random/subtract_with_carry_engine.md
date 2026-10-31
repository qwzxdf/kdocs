---
title: std::subtract_with_carry_engine
summary: "キャリーつき引き算法の乱数エンジンのテンプレート（`ranlux24_base` の元）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::subtract_with_carry_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

線形合同法が前の 1 つの値だけから次を作るのに対し、キャリーつき引き算法は、少し前の値と、もっと前の値の 2 つを使います。`x[i] = x[i-s] - x[i-r] - carry` を `2^w` で割った余りで求め、引き算が足りなくて借りが出たら、次の計算の `carry` を 1 にします。`std::subtract_with_carry_engine` はこの方式のテンプレートで、`ranlux24_base` と `ranlux48_base` が、パラメータを決めた別名です。

!!! tip "ポイント"
    - `x[i] = (x[i-s] - x[i-r] - carry) mod 2^w`。借りは次の計算に持ち越す
    - テンプレート引数は、語のビット数 `w`、短い遅れ `s`、長い遅れ `r`
    - 状態は `r` 個の語と、借りの値
    - 単独では連続した値に相関が残る。`discard_block_engine` で間引いた `ranlux24` / `ranlux48` が実用向き

!!! info "このページを読む前に"
    [`std::ranlux24_base`](ranlux24_base.md) と [`std::discard_block_engine`](discard_block_engine.md) を先に読んでください。

## 関数の詳しい説明

### std::subtract_with_carry_engine {#subtract_with_carry_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class UIntType, size_t w, size_t s, size_t r>
class subtract_with_carry_engine;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `UIntType` | 状態と出力の整数型 |
| `w` | 1 語のビット数 |
| `s` | 短い遅れ。`0 < s < r` |
| `r` | 長い遅れ。状態の語数でもある |

### 定数 {#constants}

`word_size`（`w`）、`short_lag`（`s`）、`long_lag`（`r`）、`default_seed`（19780503）が静的な定数として取れます。

### 別名 {#aliases}

| 別名 | パラメータ |
| --- | --- |
| `ranlux24_base` | `<uint_fast32_t, 24, 10, 24>` |
| `ranlux48_base` | `<uint_fast64_t, 48, 5, 12>` |

どちらも、単独で使うことは勧められません。連続した出力に相関が残るため、`discard_block_engine` で間引いて使う設計だからです。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>

int main() {
  // ranlux24_base と同じパラメータ
  using E = std::subtract_with_carry_engine<std::uint_fast32_t, 24, 10, 24>;
  E e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）

  std::println("語 {} ビット 短い遅れ {} 長い遅れ {}", E::word_size, E::short_lag, E::long_lag);
  std::println("出力は 24 ビット以内: {}", E::max() == (1u << 24) - 1);
}
```

```text title="実行結果"
7937952
語 24 ビット 短い遅れ 10 長い遅れ 24
出力は 24 ビット以内: true
```

## ゲームでの使いどころ

使いません。`ranlux24` / `ranlux48` を使うときの土台として、存在を知っておくだけです。

## よくあるミス

??? failure "単独で使う"
    連続した出力に相関が残ります。使うなら、間引いた `ranlux24` / `ranlux48` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranlux24_base`](ranlux24_base.md) | 24 ビット版の別名 |
| [`ranlux48_base`](ranlux48_base.md) | 48 ビット版の別名 |
| [`discard_block_engine`](discard_block_engine.md) | 間引いて品質を上げる |
| [`mersenne_twister_engine`](mersenne_twister_engine.md) | 実用的な定番 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::subtract_with_carry_engine](https://cpprefjp.github.io/reference/random/subtract_with_carry_engine.html)
- [cppreference: std::subtract_with_carry_engine](https://en.cppreference.com/w/cpp/numeric/random/subtract_with_carry_engine)
