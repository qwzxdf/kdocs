---
title: std::uintptr_t
summary: "ポインタをそのまま入れられる大きさの符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uintptr_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

ポインタのアドレスが 16 バイトの境界に揃っているかを調べたい。SIMD や GPU に渡すバッファは、アドレスが特定の倍数に揃っていなければなりません。そのためにポインタを整数として扱います。

`std::uintptr_t` は、<strong>ポインタを入れても欠けない符号なし整数型</strong>です。アドレスはふつう負の値を持たないので、符号なし版のほうがよく使われます。

!!! tip "ポイント"
    - `void*` を変換して戻しても、元のポインタに戻る大きさ
    - 64 ビット環境では 64 ビット
    - アドレスの配置（アラインメント）を調べるときに使う
    - `std::intptr_t` は符号つき版

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uintptr_t {#uintptr_t}

<span class="ver ver-11">C++11</span>

```cpp
using uintptr_t = /* ポインタを保持できる符号なし整数型 */;
```

`std::uintptr_t` は、`void*` を `reinterpret_cast` で整数に変換したときに情報が欠けない、符号なし整数型です。ポインタと同じ幅になります。

アドレスが `N` バイト境界に揃っているかは、`address % N == 0`（N が 2 の累乗なら `(address & (N - 1)) == 0`）で調べます。標準の `std::align` や `alignas` でも扱えますが、既存のバッファの配置を調べたいときは、整数に直すのが手軽です。

整数に直したアドレスの計算結果をポインタに戻して使うことは、規格では保証されません。実際の環境では動くことが多いですが、移植性は損なわれます。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  alignas(16) char buffer[32];
  const auto address = reinterpret_cast<std::uintptr_t>(buffer);
  std::println("16 バイト境界に揃っている: {}", address % 16 == 0);
}
```

```text title="実行結果"
16 バイト境界に揃っている: true
```

## ゲームでの使いどころ

SIMD 用のバッファや GPU に渡すデータが正しく揃っているかを確かめる検査に使います。

```cpp
assert(reinterpret_cast<std::uintptr_t>(data) % 16 == 0);   // 16 バイト境界に揃っていること
```

揃っていない場合は、確保の方法を `alignas` や `std::aligned_alloc` に変えます。

## よくあるミス

??? failure "`unsigned int` にアドレスを入れて、64 ビット環境で欠ける"
    `std::uintptr_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`intptr_t`](intptr_t.md) | 符号つき版 |
| [`size_t`](../../support/size_t.md) | 大きさやインデックスを表す型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインタを保持できる大きさの符号なし整数
    - [x] アドレスの配置（アラインメント）の検査に使う
    - [x] 整数に変えたアドレスの計算は、ポインタに戻せる保証がない

## 関連ページ

- [cpprefjp: std::uintptr_t](https://cpprefjp.github.io/reference/cstdint/uintptr_t.html)
- [cppreference: std::uintptr_t](https://en.cppreference.com/w/cpp/types/integer)
