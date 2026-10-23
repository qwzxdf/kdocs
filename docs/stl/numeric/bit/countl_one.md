---
title: std::countl_one
summary: "上位（左）から数えて、連続する 1 のビット数を数える。"
order: 9
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::countl_one

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

上位から数えて、1 のビットが何個続いているか。ビットを反転すると `countl_zero` と同じ意味になるので、使う機会は少ないですが、上位ビットが埋まっている長さを直接調べたいときに便利です。

!!! tip "ポイント"
    - `std::countl_one(0xF0000000u)` は 4
    - 全ビットが 1 なら型のビット幅
    - `countl_zero(~x)` と同じ
    - 符号なし整数型だけが対象

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::countl_one {#countl_one}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int countl_one(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

`std::countl_one(x)` は、`x` の最上位ビットから見て、連続する 1 の数を返します。`x` の全ビットが 1 なら型のビット幅、最上位ビットが 0 なら 0 です。

`countl_zero(~x)` と同じ値になります。`~x` を書く手間を省くための関数です。

符号なし整数型だけが対象です。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("countl_one(0xF0000000) = {}", std::countl_one(std::uint32_t{0xF0000000}));
  std::println("countl_one(0) = {}", std::countl_one(std::uint32_t{0}));
  std::println("countl_one(0xFFFFFFFF) = {}", std::countl_one(std::uint32_t{0xFFFFFFFF}));
}
```

```text title="実行結果"
countl_one(0xF0000000) = 4
countl_one(0) = 0
countl_one(0xFFFFFFFF) = 32
```

## ゲームでの使いどころ

上位ビットが連続して立っているマスクの幅を調べるときに使います。ネットワークマスク（IP アドレスのサブネット）の長さを求める処理が典型です。

```cpp
// サブネットマスク 255.255.255.0 の長さ（24）
const int prefix_length = std::countl_one(mask);
```

## よくあるミス

??? failure "`countl_zero` と取り違える"
    数える対象が 1 か 0 かの違いです。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしに直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countl_zero`](countl_zero.md) | 上位の 0 の連続数 |
| [`countr_one`](countr_one.md) | 下位の 1 の連続数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `countl_one(x)` は上位から続く 1 の数
    - [x] `countl_zero(~x)` と同じ
    - [x] サブネットマスクの長さなどに使う

## 関連ページ

- [cpprefjp: std::countl_one](https://cpprefjp.github.io/reference/bit/countl_one.html)
- [cppreference: std::countl_one](https://en.cppreference.com/w/cpp/numeric/countl_one)
