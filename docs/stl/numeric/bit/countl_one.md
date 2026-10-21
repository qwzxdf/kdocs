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

`std::countl_one` は、**最上位のビットから数えて、連続している 1 の数**を返す関数です。ネットマスクの長さ（IP アドレスの `/24` など）の計算で使われます。

!!! tip "ポイント"
    - 全部 1 なら、型のビット数。
    - `countl_zero(~x)` と同じ。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::countl_one {#countl_one}

```cpp
template <class T>
constexpr int countl_one(T x) noexcept;
```

- 一番上の位から続く 1 の数

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::countl_one(0xF0000000u), std::countl_one(0u));
}
```

```text title="実行結果"
4 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ネットマスクの長さを求める | `std::countl_one(mask)` |

## よくあるミス

??? failure "符号つきの型に使う"
    符号なし整数だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countl_zero`](countl_zero.md) | 0 を数える |
| [`countr_one`](countr_one.md) | 下位から数える |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 上位から連続する 1 の数
    - [x] 全部 1 なら全ビット数
    - [x] ネットマスクの長さ

## 関連ページ

- [cpprefjp: std::countl_one](https://cpprefjp.github.io/reference/bit/countl_one.html)
- [cppreference: std::countl_one](https://en.cppreference.com/w/cpp/numeric/countl_one)
