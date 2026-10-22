---
title: std::independent_bits_engine
summary: "別のエンジンの出力から、指定したビット数の乱数を作るアダプタ。"
order: 900
tags:
  - ユーティリティ
---

# std::independent_bits_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

エンジンの出力のビット幅と、欲しいビット幅が合わないことがあります。`independent_bits_engine<Engine, W, UInt>` は、元のエンジンを何回か呼び、W ビットの乱数を組み立てます。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::independent_bits_engine {#independent_bits_engine}

```cpp
template <class Engine, size_t w, class UIntType>
class independent_bits_engine;
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
  using E = std::independent_bits_engine<std::mt19937, 16, std::uint32_t>;
  std::println("{}", E::max());  // 16 ビットなので 65535
}
```

```text title="実行結果"
65535
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::independent_bits_engine e{seed}; dist(e);` |

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
    - [x] 別のエンジンの出力から、指定したビット数の乱数を作るアダプタ
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::independent_bits_engine](https://cpprefjp.github.io/reference/random/independent_bits_engine.html)
- [cppreference: std::independent_bits_engine](https://en.cppreference.com/w/cpp/numeric/random/independent_bits_engine)
