---
title: std::assume_aligned
summary: "ポインタが N バイト境界にあると、コンパイラに約束する。"
order: 900
tags:
  - メモリ
---

# std::assume_aligned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

SIMD で処理するとき、データが 32 バイトや 64 バイトの境界に並んでいると、コンパイラは速い命令を使えます。ところが、関数の引数のポインターは、そのアライメントが分かりません。`std::assume_aligned<N>(p)` は、「`p` は `N` バイトの境界にある」とコンパイラに約束します。

!!! tip "ポイント"
    - `std::assume_aligned<64>(p)` で、`p` が 64 バイト境界だと伝える
    - 約束を破ると、未定義動作
    - 実行時の処理は何もしない。最適化の助け
    - C++20

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::assume_aligned {#assume_aligned}

<span class="ver ver-20">C++20</span>

```cpp
template <std::size_t N, class T>
[[nodiscard]] constexpr T* assume_aligned(T* ptr);
```

`N` は 2 のべき乗でなければなりません。`ptr` が実際に `N` バイトの境界にないと、未定義動作です。

戻り値は `ptr` と同じ値ですが、アライメントの情報が付いています。戻り値を使うこと（`[[nodiscard]]`）が前提です。

ベクトル化できるループの前に、入力のポインターに適用すると、コンパイラが、境界を処理する余計なコードを出さずに済みます。ただし、効果の有無は、コンパイラ次第です。

アライメントを保証するのは、確保する側の責任です。`alignas(64)` の配列や、`std::aligned_alloc`、`operator new(size, align_val_t)` で確保した領域に使います。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <memory>
#include <print>

float Sum(const float* data, int n) {
  const float* p = std::assume_aligned<64>(data);  // 64 バイト境界だと約束する
  float s = 0;
  for (int i = 0; i < n; ++i) s += p[i];
  return s;
}

int main() {
  alignas(64) float arr[16];
  for (int i = 0; i < 16; ++i) arr[i] = 1.0f;

  std::println("合計: {}", Sum(arr, 16));
  std::println("境界にある: {}", reinterpret_cast<std::uintptr_t>(arr) % 64 == 0);
}
```

```text title="実行結果"
合計: 16
境界にある: true
```

## ゲームでの使いどころ

SIMD で処理する大きな配列を扱う関数の冒頭で、アライメントを伝えます。

## よくあるミス

??? failure "境界にないポインターに使う"
    未定義動作です。確保の側でアライメントを守ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`align`](align.md) | 領域の中で、境界に合わせる |
| [`aligned_alloc`](aligned_alloc.md) | アライメントつきの確保 |
| [`align_val_t`](new_delete/align_val_t.md) | new のアライメント指定 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::assume_aligned](https://cpprefjp.github.io/reference/memory/assume_aligned.html)
- [cppreference: std::assume_aligned](https://en.cppreference.com/w/cpp/memory/assume_aligned)
