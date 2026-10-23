---
title: std::countr_one
summary: "下位（右）から数えて、連続する 1 のビット数を数える。"
order: 10
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::countr_one

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

下位から数えて、1 が何個続いているか。空いている最初の場所を探す処理に使えます。たとえば、使用中の枠が 1 のビットで表されていて、最初の空き枠（0 のビット）の位置を知りたいとき、答えは「下位から続く 1 の数」と同じです。

!!! tip "ポイント"
    - `std::countr_one(7u)` は 3（下位の 1 が 3 個）
    - 全ビットが 1 なら型のビット幅
    - `countr_zero(~x)` と同じ
    - 最初の空き枠を探すのに使える

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::countr_one {#countr_one}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int countr_one(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

`std::countr_one(x)` は、`x` の最下位ビットから見て、連続する 1 の数を返します。全ビットが 1 なら型のビット幅、最下位ビットが 0 なら 0 です。

`countr_zero(~x)` と同じ値になります。

使用中の枠を 1 で表したビットマスクでは、`countr_one(mask)` が最初の空き枠の番号になります。全部埋まっていれば、幅と同じ値が返るので、空きなしを判定できます。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("countr_one(7) = {}", std::countr_one(std::uint32_t{7}));
  std::println("countr_one(0) = {}", std::countr_one(std::uint32_t{0}));
  std::println("countr_one(0b0111) = {}", std::countr_one(std::uint32_t{0b0111}));
}
```

```text title="実行結果"
countr_one(7) = 3
countr_one(0) = 0
countr_one(0b0111) = 3
```

## ゲームでの使いどころ

オブジェクトプールで、使用中の枠をビットマスクで管理しているとき、最初の空き枠を探します。

```cpp
std::uint32_t used = 0b0111;                 // 0, 1, 2 番が使用中
const int free_slot = std::countr_one(used); // 3 番が最初の空き
```

## よくあるミス

??? failure "全部埋まっているときの戻り値を空きの番号と思う"
    全ビットが 1 なら、型のビット幅が返ります。幅と比べて空きなしを判定します。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしに直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countr_zero`](countr_zero.md) | 下位の 0 の連続数 |
| [`countl_one`](countl_one.md) | 上位の 1 の連続数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `countr_one(x)` は下位から続く 1 の数
    - [x] `countr_zero(~x)` と同じ
    - [x] 最初の空き枠の番号を求めるのに使える

## 関連ページ

- [cpprefjp: std::countr_one](https://cpprefjp.github.io/reference/bit/countr_one.html)
- [cppreference: std::countr_one](https://en.cppreference.com/w/cpp/numeric/countr_one)
