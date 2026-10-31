---
title: std::independent_bits_engine
summary: "別のエンジンの出力から、指定したビット数の乱数を作るアダプタ。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::independent_bits_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`mt19937` は 32 ビットの乱数を返しますが、16 ビットや 7 ビットの乱数が欲しいことがあります。上位や下位を切り出すだけだと、偏りの出る場合があります。`std::independent_bits_engine<Engine, w, UIntType>` は、元のエンジンの出力から、ちょうど `w` ビットの、偏りのない乱数を作るアダプタです。

!!! tip "ポイント"
    - `w` ビットの乱数を返す。値の範囲は `0` から `2^w - 1`
    - 元のエンジンの出力を、必要なだけ集めて作る。1 回の出力に、元の出力を複数回使うことがある
    - `w` が元のエンジンのビット数より大きくてもよい（64 ビットを 32 ビットのエンジンから作るなど）
    - 分布の `uniform_int_distribution` で足りる場面が多い

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) を先に読んでください。

## 関数の詳しい説明

### std::independent_bits_engine {#independent_bits_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class Engine, size_t w, class UIntType>
class independent_bits_engine;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Engine` | 元になるエンジン |
| `w` | 作る乱数のビット数 |
| `UIntType` | 出力の整数型。`w` ビットが収まる大きさ |

`min()` は 0、`max()` は `2^w - 1` です。たとえば `w = 16` なら、`max()` は 65535 です。

元のエンジンの 1 回の出力が `w` ビットより多いときは、必要なビットだけを取り出します。少ないときは、複数回の出力を組み合わせます。どの場合も、各ビットが等しい確率で 0 か 1 になるように作られます。

64 ビットの乱数が欲しいのに、32 ビットのエンジン（`mt19937`）しかないとき、`independent_bits_engine<std::mt19937, 64, std::uint64_t>` で、2 回の出力から作れます。ただし、64 ビットのエンジンが必要なら、`mt19937_64` のほうが速くて自然です。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>

int main() {
  using E16 = std::independent_bits_engine<std::mt19937, 16, std::uint32_t>;
  std::println("16 ビット: max = {}", E16::max());

  E16 e16(42);
  bool in_range = true;
  for (int i = 0; i < 1000; ++i) {
    if (e16() > E16::max()) in_range = false;
  }
  std::println("1000 回すべて範囲内: {}", in_range);

  // 7 ビット: 0〜127
  using E7 = std::independent_bits_engine<std::mt19937, 7, std::uint32_t>;
  std::println("7 ビット: max = {}", E7::max());
}
```

```text title="実行結果"
16 ビット: max = 65535
1000 回すべて範囲内: true
7 ビット: max = 127
```

## ゲームでの使いどころ

特定のビット数の乱数が必要な、ID や ハッシュ値の生成に使えます。範囲を指定した整数が欲しいだけなら、`uniform_int_distribution` を使います。

## よくあるミス

??? failure "UIntType が w ビットを収められない"
    `w = 40` で `UIntType` が `uint32_t` だと、コンパイルできません。`uint64_t` にします。

??? failure "下位ビットを切り出すのと同じだと思う"
    元のエンジンの下位ビットだけに偏りがあるとき、切り出すと偏りがそのまま出ます。このアダプタは、偏りが出ないように作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`discard_block_engine`](discard_block_engine.md) | 出力を間引く |
| [`shuffle_order_engine`](shuffle_order_engine.md) | 出力の順番を入れ替える |
| [`uniform_int_distribution`](uniform_int_distribution.md) | 範囲を指定した整数。普段はこちら |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::independent_bits_engine](https://cpprefjp.github.io/reference/random/independent_bits_engine.html)
- [cppreference: std::independent_bits_engine](https://en.cppreference.com/w/cpp/numeric/random/independent_bits_engine)
