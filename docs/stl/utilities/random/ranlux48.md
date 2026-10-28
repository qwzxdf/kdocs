---
title: std::ranlux48
summary: "高品質で遅い乱数エンジン（`ranlux48_base` を間引いたもの）。"
order: 900
tags:
  - ユーティリティ
---

# std::ranlux48

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`ranlux48_base` は速いが品質が低いので、`discard_block_engine` で出力を間引いて品質を上げたものが `ranlux48` です。品質は高い一方、遅く、ゲームの通常の乱数には `mt19937` で足ります。厳密な乱数の品質が必要な科学計算などに向きます。

!!! tip "ポイント"
    - 48 ビットの乱数を作る。
    - `ranlux24` の 48 ビット版。
    - ゲームの乱数にはふつう不要。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranlux48 {#ranlux48}

```cpp
using ranlux48 = discard_block_engine<ranlux48_base, 389, 11>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | 整数 | 省略可。初期状態を決める値 |

- 戻り値: `operator()` で次の乱数を返す
- 計算量: 1 回あたり重い


## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  std::ranlux48 e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
249142670248501
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 統計的な品質が重要な計算 |

## よくあるミス

??? failure "速さを期待する"
    遅いエンジンです。通常は `mt19937` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranlux24`](ranlux24.md) | 24 ビット版 |
| [`mt19937`](mt19937.md) | 標準的な高品質エンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高品質で遅い乱数エンジン（`ranlux48_base` を間引いたもの）
    - [x] 48 ビットの乱数を作る
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranlux48](https://cpprefjp.github.io/reference/random/ranlux48.html)
- [cppreference: std::ranlux48](https://en.cppreference.com/w/cpp/numeric/random/ranlux48)
