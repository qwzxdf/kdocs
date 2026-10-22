---
title: std::ranlux48_base
summary: "ranlux48 の土台になる、キャリーつき引き算法のエンジン。"
order: 900
tags:
  - ユーティリティ
---

# std::ranlux48_base

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`ranlux48` の土台になる、48 ビット幅のエンジンです。`ranlux48_base` は単独では品質が劣り、そのまま使うことは少なく、`ranlux48` を使います。

!!! tip "ポイント"
    - `<random>` のエンジン（乱数を作る部品）。
    - 分布（`uniform_int_distribution` など）と組み合わせて使う。
    - シードは `std::random_device` などで与える。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranlux48_base {#ranlux48_base}

```cpp
using ranlux48_base = subtract_with_carry_engine<uint_fast64_t, 48, 5, 12>;
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
  std::ranlux48_base e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
61839128582725
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームの乱数 | `std::ranlux48_base e{seed}; dist(e);` |

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
    - [x] ranlux48 の土台になる、キャリーつき引き算法のエンジン
    - [x] 分布と組み合わせて使う
    - [x] シードは random_device で

## 関連ページ

- [cpprefjp: std::ranlux48_base](https://cpprefjp.github.io/reference/random/ranlux48_base.html)
- [cppreference: std::ranlux48_base](https://en.cppreference.com/w/cpp/numeric/random/ranlux48_base)
