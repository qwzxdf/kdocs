---
title: std::subtract_with_carry_engine
summary: "キャリーつき引き算法の乱数エンジンのテンプレート（`ranlux24_base` の元）。"
order: 900
tags:
  - ユーティリティ
---

# std::subtract_with_carry_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

過去の 2 つの値の差とキャリー（繰り下がり）から次の値を作る方法です。`ranlux24_base` と `ranlux48_base` は、これの特定の設定です。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::subtract_with_carry_engine {#subtract_with_carry_engine}

```cpp
template <class UIntType, size_t w, size_t s, size_t r>
class subtract_with_carry_engine;
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
  // ranlux24_base と同じパラメータ
  std::subtract_with_carry_engine<std::uint_fast32_t, 24, 10, 24> e;
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
| ゲームの乱数 | `std::subtract_with_carry_engine e{seed}; dist(e);` |

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
    - [x] キャリーつき引き算法の乱数エンジンのテンプレート（`ranlux24_base` の元）
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::subtract_with_carry_engine](https://cpprefjp.github.io/reference/random/subtract_with_carry_engine.html)
- [cppreference: std::subtract_with_carry_engine](https://en.cppreference.com/w/cpp/numeric/random/subtract_with_carry_engine)
