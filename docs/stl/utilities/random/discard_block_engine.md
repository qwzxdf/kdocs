---
title: std::discard_block_engine
summary: "別のエンジンの出力を、ブロックごとに間引くアダプタ（`ranlux24` の元）。"
order: 900
tags:
  - ユーティリティ
---

# std::discard_block_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

品質の低いエンジンの出力は、続けて使うと偏りが出ることがあります。`discard_block_engine<Engine, P, R>` は、`P` 個ごとのブロックのうち `R` 個だけ使い、残りを捨てることで品質を上げます。`ranlux24` は `ranlux24_base` にこれを適用したものです。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::discard_block_engine {#discard_block_engine}

```cpp
template <class Engine, size_t p, size_t r>
class discard_block_engine;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | 整数 | 省略可。初期状態を決める値 |

- 戻り値: `operator()` で次の乱数を返す
- 計算量: 1 回あたり定数


## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  // ranlux24 と同じ組み合わせ
  std::discard_block_engine<std::ranlux24_base, 223, 23> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
9901578
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::discard_block_engine e{seed}; dist(e);` |

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
    - [x] 別のエンジンの出力を、ブロックごとに間引くアダプタ（`ranlux24` の元）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::discard_block_engine](https://cpprefjp.github.io/reference/random/discard_block_engine.html)
- [cppreference: std::discard_block_engine](https://en.cppreference.com/w/cpp/numeric/random/discard_block_engine)
