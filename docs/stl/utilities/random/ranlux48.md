---
title: std::ranlux48
summary: "高品質で遅い乱数エンジン（`ranlux48_base` を間引いたもの）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::ranlux48

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::ranlux48` は、標準が用意する乱数エンジンのなかで、最も品質を重視したものの 1 つです。48 ビットの出力を返し、元のエンジン `ranlux48_base` の出力を、389 個のうち 11 個だけ使い、残りを捨てます。捨てるぶん、とても遅くなります。速さを犠牲にして、統計的な性質を良くしたい、科学計算向けのエンジンで、ゲームではまず使いません。

!!! tip "ポイント"
    - `discard_block_engine<ranlux48_base, 389, 11>` の別名
    - 出力は 48 ビット（0 〜 2^48 - 1）
    - 389 個のうち 11 個しか使わないので、`mt19937` の数十倍遅い
    - 高品質で、再現性が必要な数値実験向け

!!! info "このページを読む前に"
    [`std::discard_block_engine`](discard_block_engine.md) と [`std::ranlux24`](ranlux24.md) を先に読んでください。

## 関数の詳しい説明

### std::ranlux48 {#ranlux48}

<span class="ver ver-11">C++11</span>

```cpp
using ranlux48 = discard_block_engine<ranlux48_base, 389, 11>;
```

元の `ranlux48_base` は `subtract_with_carry_engine<uint_fast64_t, 48, 5, 12>` です。そこから 389 個ごとのブロックの先頭 11 個を使い、378 個を捨てるので、1 個の出力に、元のエンジンを約 35 回進める計算になります。

`ranlux24` の兄弟で、24 ビット版（`<ranlux24_base, 223, 23>`）に比べて、出力のビット数が多く、間引きも強いので、さらに遅く、品質が高いものです。

既定の種は 19780503 です。`seed(値)` で変更します。

出力の最大値は `2^48 - 1` です。`uniform_int_distribution` に渡して使うときは、分布が 48 ビットの出力から範囲を作ります。

## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  std::ranlux48 e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）

  std::println("max は 2^48 - 1: {}", std::ranlux48::max() == (1ull << 48) - 1);
}
```

```text title="実行結果"
249142670248501
max は 2^48 - 1: true
```

## ゲームでの使いどころ

使いません。速度が要るゲームの乱数には、`mt19937` を使います。

## よくあるミス

??? failure "品質が高いからと、ゲームの乱数に使う"
    1 回の呼び出しが遅く、フレームの時間を圧迫します。ゲームの乱数には、`mt19937` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranlux24`](ranlux24.md) | 24 ビット版 |
| [`ranlux48_base`](ranlux48_base.md) | 間引く前の元のエンジン |
| [`mt19937`](mt19937.md) | 速くて品質もよい定番 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::ranlux48](https://cpprefjp.github.io/reference/random/ranlux48.html)
- [cppreference: std::ranlux48](https://en.cppreference.com/w/cpp/numeric/random/ranlux48)
