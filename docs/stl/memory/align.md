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

`std::align(境界, 大きさ, ptr, space)` は、**確保済みのバッファの中で、指定した境界（アラインメント）にそろった位置を探す**関数です。自作のアリーナ（積むだけのメモリ）で、確保のたびに先頭を境界へそろえるのに使います。

!!! tip "ポイント"
    - 成功すると `ptr` と `space` が更新される。
    - 収まらないときは `nullptr` を返す（`ptr` と `space` は変わらない）。
    - [`monotonic_buffer_resource`](pmr/monotonic_buffer_resource.md) を使えば、自分で書かなくて済む。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::align {#align}

```cpp
void* align(std::size_t alignment, std::size_t size, void*& ptr, std::size_t& space);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alignment` | `size_t` | そろえたい境界（2 のべき乗） |
| `size` | `size_t` | 必要な大きさ |
| `ptr` | `void*&` | 現在位置。成功すると進む |
| `space` | `size_t&` | 残りの大きさ。成功すると減る |

- 戻り値: そろった位置（収まらなければ `nullptr`）
- 計算量: O(1)

```cpp
#include <cstdint>
#include <memory>
#include <print>

int main() {
  alignas(64) char buffer[128];
  void* p = buffer + 1;           // わざと境界からずらす
  std::size_t space = sizeof(buffer) - 1;

  void* aligned = std::align(16, 8, p, space);
  auto addr = reinterpret_cast<std::uintptr_t>(aligned);
  std::println("{} {}", aligned != nullptr, addr % 16 == 0);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作のアリーナで、確保位置を境界にそろえる | `std::align(alignof(T), sizeof(T), cur, space)` |

## よくあるミス

??? failure "収まらないのに結果を使う"
    `nullptr` が返ったときは、バッファの残りが足りません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`monotonic_buffer_resource`](pmr/monotonic_buffer_resource.md) | 標準のアリーナ |
| [`max_align_t`](../support/max_align_t.md) | 基本の境界 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 境界にそろった位置を探す
    - [x] 成功すると ptr / space が進む
    - [x] 収まらなければ nullptr

## 関連ページ

- [cpprefjp: std::align](https://cpprefjp.github.io/reference/memory/align.html)
- [cppreference: std::align](https://en.cppreference.com/w/cpp/memory/align)
