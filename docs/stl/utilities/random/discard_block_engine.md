---
title: std::discard_block_engine
summary: "別のエンジンの出力を、ブロックごとに間引くアダプタ（`ranlux24` の元）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::discard_block_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

乱数エンジンの中には、連続した出力に、わずかな相関が残るものがあります。その相関を、出力を「捨てる」ことで薄めるのが `std::discard_block_engine` です。元のエンジンの出力を `p` 個ずつのブロックに区切り、各ブロックの先頭の `r` 個だけを使って、残りの `p - r` 個は捨てます。`std::ranlux24` と `std::ranlux48` が、この方式です。

!!! tip "ポイント"
    - `discard_block_engine<Engine, p, r>`: `p` 個のうち、先頭の `r` 個を使い、残りを捨てる
    - 捨てるぶん、出力 1 個あたりの時間は `p / r` 倍になる
    - `ranlux24` は `<ranlux24_base, 223, 23>`、`ranlux48` は `<ranlux48_base, 389, 11>`
    - `base()` で、元のエンジンを参照できる

!!! info "このページを読む前に"
    [`std::subtract_with_carry_engine`](subtract_with_carry_engine.md) と [`std::ranlux24`](ranlux24.md) を先に読んでください。

## 関数の詳しい説明

### std::discard_block_engine {#discard_block_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class Engine, size_t p, size_t r>
class discard_block_engine;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Engine` | 元になるエンジン |
| `p` | ブロックの大きさ。`r` 以上 |
| `r` | ブロックのうち、使う個数。1 以上 |

元のエンジンから `p` 個を取り出し、先頭の `r` 個を順に返し、残りの `p - r` 個は、使わずに読み飛ばします。次のブロックも同じです。

`r == p` なら、何も捨てず、元のエンジンと同じ出力になります。

エンジンが持つ `min()` / `max()` は、元のエンジンのものと同じです。種の指定や `discard(n)` は、このアダプタの出力個数で数えます。

`base()` は、元のエンジンへの `const` 参照を返します。どこまで進んだかを調べるのに使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  // 4 個ずつのブロックの、先頭 2 個だけを使う
  std::discard_block_engine<std::minstd_rand0, 4, 2> e;
  const auto v1 = e();
  const auto v2 = e();
  const auto v3 = e();
  const auto v4 = e();
  std::println("{} {} {} {}", v1, v2, v3, v4);

  // ranlux24 と同じ組み合わせ
  std::discard_block_engine<std::ranlux24_base, 223, 23> r;
  r.discard(9999);
  std::println("{}", r());  // 10000 回目の値（標準で決まっている）
}
```

```text title="実行結果"
16807 282475249 1144108930 470211272
9901578
```

`minstd_rand0` の出力は 16807、282475249、1622650073、984943658、1144108930、470211272 … と続きます。ブロックの先頭 2 個を使い、3 番目と 4 番目（1622650073 と 984943658）を捨てているので、3 つ目の出力が 1144108930 になっています。

## ゲームでの使いどころ

自分で組み合わせることは、ほとんどありません。`ranlux24` を使うときに、裏で動いています。

## よくあるミス

??? failure "r が p より大きい"
    ブロックの大きさ以上は使えません。`r <= p` にします。

??? failure "出力が速いと思う"
    捨てるぶん、時間がかかります。`ranlux48` は `mt19937` より桁違いに遅いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranlux24`](ranlux24.md) | `<ranlux24_base, 223, 23>` の別名 |
| [`ranlux48`](ranlux48.md) | `<ranlux48_base, 389, 11>` の別名 |
| [`independent_bits_engine`](independent_bits_engine.md) | ビット数を変えるアダプタ |
| [`shuffle_order_engine`](shuffle_order_engine.md) | 順番を入れ替えるアダプタ |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::discard_block_engine](https://cpprefjp.github.io/reference/random/discard_block_engine.html)
- [cppreference: std::discard_block_engine](https://en.cppreference.com/w/cpp/numeric/random/discard_block_engine)
