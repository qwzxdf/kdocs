---
title: std::bit_width
summary: "値を表すのに必要なビット数を返す。"
order: 5
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_width

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

整数を 2 進数で書いたとき、何ビット必要か。255 は 8 ビット、256 は 9 ビットです。ミップマップの段数を求める、データを詰めるためのビット幅を決める、といった場面で、この答えが必要になります。

`std::bit_width` は、<strong>値を表すのに必要な最小のビット数</strong>を返します。

!!! tip "ポイント"
    - `std::bit_width(255u)` は 8、`std::bit_width(256u)` は 9
    - `0` のときは 0
    - 符号なし整数型だけを受け取る（符号つきを渡すとコンパイルエラー）
    - 整数の `floor(log2(x)) + 1` と同じ値を誤差なく求められる

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_width {#bit_width}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int bit_width(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | ビット幅を知りたい値 |

戻り値は、最上位の 1 のビットの位置に 1 を足した値です。つまり、値を 2 進数で書いたときの桁数で、0 のときは 0 を返します。`1` は 1 ビット、`2` と `3` は 2 ビット、`4` から `7` は 3 ビット、という具合です。

型は `unsigned char`、`unsigned short`、`unsigned int`、`unsigned long`、`unsigned long long`（と拡張型）に限られます。`int` のような符号つき型や `bool`、`char` を渡すと、コンパイルエラーになります。符号つきの値を調べたいなら、`static_cast<unsigned>` で変換します。

`log2` を浮動小数点数で呼んで切り捨てる方法と比べると、誤差がなく、CPU 命令（leading zero count）に直接対応するので速いです。`floor(log2(x)) + 1` が `bit_width(x)` に当たります。

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("bit_width(0)   = {}", std::bit_width(0u));
  std::println("bit_width(1)   = {}", std::bit_width(1u));
  std::println("bit_width(255) = {}", std::bit_width(255u));
  std::println("bit_width(256) = {}", std::bit_width(256u));
}
```

```text title="実行結果"
bit_width(0)   = 0
bit_width(1)   = 1
bit_width(255) = 8
bit_width(256) = 9
```

## ゲームでの使いどころ

ミップマップの段数を整数だけで求められます。

```cpp
// 幅 1024、高さ 512 のテクスチャのミップ段数（大きいほうの辺で決まる）
const unsigned size = std::max(1024u, 512u);
const int mip_levels = std::bit_width(size);   // 1024 → 11 段
```

ビットフィールドに詰めるデータで、値の最大から必要なビット数を決めるときにも使います。

## よくあるミス

??? failure "`int` を渡してコンパイルエラーになる"
    符号なし整数型にして渡します。

??? failure "0 のときの結果を忘れる"
    0 は 0 ビットです。ミップ段数などで 0 を許すなら、先に 1 以上に補正します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_floor`](bit_floor.md) | 以下で最大の 2 の累乗 |
| [`log2`](../cmath/log2.md) | 浮動小数点数の底 2 の対数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bit_width(x)` は値を表す最小のビット数
    - [x] `0` なら 0。符号なし整数型のみ
    - [x] 整数だけで、誤差なく `floor(log2(x)) + 1` が求まる

## 関連ページ

- [`std::bit_floor`](bit_floor.md)
- [cpprefjp: std::bit_width](https://cpprefjp.github.io/reference/bit/bit_width.html)
- [cppreference: std::bit_width](https://en.cppreference.com/w/cpp/numeric/bit_width)
