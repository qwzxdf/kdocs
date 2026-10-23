---
title: std::popcount
summary: "立っているビット（1）の数を数える。"
order: 1
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::popcount

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

立っているビット（1 のビット）が何個あるか。フラグの集合の要素数、ビットマスクで表した敵の数、ハッシュの一致度。ビットを 1 つずつ数えるループは、`popcount` なら CPU の専用命令 1 つで済みます。

!!! tip "ポイント"
    - `std::popcount(255u)` は 8（1 のビットの数）
    - 符号なし整数型だけ。戻り値は `int`
    - 多くの CPU で専用命令 1 つに置き換わる
    - フラグの数、集合の要素数に使える

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::popcount {#popcount}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int popcount(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

`std::popcount(x)` は、`x` の 2 進表現で 1 になっているビットの数を返します。0 なら 0、全ビットが 1 ならそのビット幅です。符号なし整数型だけが対象で、`int` のような符号つき型はコンパイルエラーになります。

多くの CPU に `popcnt` 命令があり、コンパイラはそれに置き換えます。対応していない CPU 向けにも、速いソフトウェア実装が使われます。

戻り値は `int` で、`x` の型の幅（`uint32_t` なら 32）を超えません。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("popcount(0) = {}", std::popcount(0u));
  std::println("popcount(0b1011) = {}", std::popcount(0b1011u));
  std::println("popcount(255) = {}", std::popcount(255u));
}
```

```text title="実行結果"
popcount(0) = 0
popcount(0b1011) = 3
popcount(255) = 8
```

## ゲームでの使いどころ

ビットマスクで管理した集合の要素数を数えるときに使います。

```cpp
// 32 体の敵のうち、生きている敵をビットで管理している
std::uint32_t alive_mask = 0b1011;
const int alive_count = std::popcount(alive_mask);   // 3 体
```

## よくあるミス

??? failure "符号つき整数を渡してコンパイルエラーになる"
    `static_cast<unsigned>(x)` で符号なしに直します。負の値は、2 の補数表現のビットで数えられます。

??? failure "ループで 1 ビットずつ数えて遅い"
    `popcount` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`has_single_bit`](has_single_bit.md) | ビットが 1 つだけか |
| [`countr_zero`](countr_zero.md) | 下位の 0 の連続数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `popcount(x)` は 1 のビットの個数
    - [x] 符号なし整数型のみ。CPU の専用命令になる
    - [x] 集合の要素数、フラグの数に使う

## 関連ページ

- [cpprefjp: std::popcount](https://cpprefjp.github.io/reference/bit/popcount.html)
- [cppreference: std::popcount](https://en.cppreference.com/w/cpp/numeric/popcount)
