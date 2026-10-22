---
title: std::shuffle_order_engine
summary: "別のエンジンの出力の順番を入れ替えるアダプタ（`knuth_b` の元）。"
order: 900
tags:
  - ユーティリティ
---

# std::shuffle_order_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

線形合同法のような単純なエンジンは、出力の並びに規則性が出ます。`shuffle_order_engine<Engine, K>` は、K 個の値を貯めておき、ランダムな順番で取り出すことで規則性を崩します。`knuth_b` は `minstd_rand0` にこれを適用したものです。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::shuffle_order_engine {#shuffle_order_engine}

```cpp
template <class Engine, size_t k>
class shuffle_order_engine;
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
  // knuth_b と同じ組み合わせ
  std::shuffle_order_engine<std::minstd_rand0, 256> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
1112339016
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::shuffle_order_engine e{seed}; dist(e);` |

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
    - [x] 別のエンジンの出力の順番を入れ替えるアダプタ（`knuth_b` の元）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::shuffle_order_engine](https://cpprefjp.github.io/reference/random/shuffle_order_engine.html)
- [cppreference: std::shuffle_order_engine](https://en.cppreference.com/w/cpp/numeric/random/shuffle_order_engine)
