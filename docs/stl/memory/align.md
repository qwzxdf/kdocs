---
title: std::align
summary: "確保済みの領域の中で、指定した境界にそろった位置を求める。"
order: 21
tags:
  - メモリ
---

# std::align

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

渡されたバッファの途中から、`alignment` バイトの境界に合わせた位置に、`size` バイトの領域を切り出したい。`std::align(alignment, size, ptr, space)` は、`ptr` を進めて境界に合わせ、残りの大きさ `space` を更新します。入りきらなければ `nullptr` を返します。

!!! tip "ポイント"
    - `ptr` を境界まで進める。成功すると `ptr` と `space` が更新される
    - 失敗すると `nullptr` を返し、`ptr` と `space` は変わらない
    - 自作のアリーナ アロケーターで、バッファの途中を切り出すときに使う
    - `ptr` は参照渡し。呼び出した後に、変数が変わる

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::align {#align}

<span class="ver ver-11">C++11</span>

```cpp
void* align(std::size_t alignment, std::size_t size, void*& ptr, std::size_t& space);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alignment` | `std::size_t` | 合わせる境界。2 のべき乗 |
| `size` | `std::size_t` | 欲しい領域の大きさ |
| `ptr` | `void*&` | バッファの現在位置。更新される |
| `space` | `std::size_t&` | 残りの大きさ。更新される |

成功すると、合わせた位置を返し、`ptr` はその位置、`space` はそこからの残りになります。合わせるために進んだ分、`space` は減ります。

領域を切り出したあとは、自分で `ptr` を `size` だけ進め、`space` を `size` だけ減らして、次の確保に備えます。

`alignment` が 2 のべき乗でないと、未定義動作です。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <memory>
#include <print>

int main() {
  alignas(64) char buffer[64];
  void* ptr = buffer + 1;      // わざと境界をずらす
  std::size_t space = sizeof(buffer) - 1;

  void* aligned = std::align(16, 8, ptr, space);
  std::println("成功: {}", aligned != nullptr);
  std::println("16 バイト境界: {}", reinterpret_cast<std::uintptr_t>(aligned) % 16 == 0);
  std::println("進んだ分だけ space が減った: {}", space == sizeof(buffer) - 16);

  // 入りきらないと nullptr
  void* tail = buffer + 60;
  std::size_t small = 4;
  std::println("入りきらない: {}", std::align(16, 8, tail, small) == nullptr);
}
```

```text title="実行結果"
成功: true
16 バイト境界: true
進んだ分だけ space が減った: true
入りきらない: true
```

## ゲームでの使いどころ

自作のアリーナ アロケーターで、1 本のバッファから、アライメントを守って切り出すときに使います。

## よくあるミス

??? failure "ptr と space を更新し忘れる"
    次の確保で、同じ位置を返してしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assume_aligned`](assume_aligned.md) | 境界にあると約束する |
| [`aligned_alloc`](aligned_alloc.md) | 境界つきで確保する |
| [`monotonic_buffer_resource`](pmr/monotonic_buffer_resource.md) | 同じことをするリソース |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::align](https://cpprefjp.github.io/reference/memory/align.html)
- [cppreference: std::align](https://en.cppreference.com/w/cpp/memory/align)
