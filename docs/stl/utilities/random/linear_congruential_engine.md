---
title: std::linear_congruential_engine
summary: "線形合同法の乱数エンジンのテンプレート（`minstd_rand` の元）。"
order: 900
tags:
  - ユーティリティ
---

# std::linear_congruential_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

「次の値 = (a × 今の値 + c) mod m」で乱数を作る方法が線形合同法です。`linear_congruential_engine<UInt, a, c, m>` は、そのパラメータを自分で選べるテンプレートで、`minstd_rand0` や `minstd_rand` はその特定の設定です。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::linear_congruential_engine {#linear_congruential_engine}

```cpp
template <class UIntType, UIntType a, UIntType c, UIntType m>
class linear_congruential_engine;
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
  // minstd_rand0 と同じパラメータ
  std::linear_congruential_engine<std::uint_fast32_t, 16807, 0, 2147483647> e;
  std::println("{}", e());
}
```

```text title="実行結果"
16807
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::linear_congruential_engine e{seed}; dist(e);` |

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
    - [x] 線形合同法の乱数エンジンのテンプレート（`minstd_rand` の元）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::linear_congruential_engine](https://cpprefjp.github.io/reference/random/linear_congruential_engine.html)
- [cppreference: std::linear_congruential_engine](https://en.cppreference.com/w/cpp/numeric/random/linear_congruential_engine)
