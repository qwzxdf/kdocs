---
title: std::mersenne_twister_engine
summary: "メルセンヌ・ツイスタの乱数エンジンのテンプレート（`mt19937` の元）。"
order: 900
tags:
  - ユーティリティ
---

# std::mersenne_twister_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`mt19937` や `mt19937_64` は、`mersenne_twister_engine` に特定のパラメータを入れたものです。自分でパラメータ（語長、状態の大きさ、マスク）を選べますが、ふつうは `mt19937` を使います。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mersenne_twister_engine {#mersenne_twister_engine}

```cpp
template <class UIntType, size_t w, size_t n, size_t m, size_t r, UIntType a, size_t u, UIntType d, size_t s, UIntType b, size_t t, UIntType c, size_t l, UIntType f>
class mersenne_twister_engine;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | 整数 | 省略可。初期状態を決める値 |

- 戻り値: `operator()` で次の乱数を返す
- 計算量: 1 回あたり定数


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>

int main() {
  // mt19937 と同じパラメータ
  std::mersenne_twister_engine<std::uint_fast32_t, 32, 624, 397, 31, 0x9908b0df, 11,
                               0xffffffff, 7, 0x9d2c5680, 15, 0xefc60000, 18, 1812433253> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
4123659995
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::mersenne_twister_engine e{seed}; dist(e);` |

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
    - [x] メルセンヌ・ツイスタの乱数エンジンのテンプレート（`mt19937` の元）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::mersenne_twister_engine](https://cpprefjp.github.io/reference/random/mersenne_twister_engine.html)
- [cppreference: std::mersenne_twister_engine](https://en.cppreference.com/w/cpp/numeric/random/mersenne_twister_engine)
