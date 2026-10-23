---
title: std::max_align_t
summary: "その環境で、最も厳しい（最大の）アラインメントを持つ型。"
order: 23
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::max_align_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstddef>`
</div>

`std::max_align_t` は、**その環境で、基本的な型の中で最も厳しいアラインメント（メモリ上の置き方の制約）を持つ型**です。`alignof(std::max_align_t)` が、`new` や `malloc` が保証する基本のアラインメントになります。自作のメモリアロケーターで、確保した領域の境界をそろえるときに使います。

!!! tip "ポイント"
    - `alignof(std::max_align_t)` の値は環境によって違う（GCC / Clang は 16、MSVC は 8 のことが多い）。
    - `new` / `malloc` が返すメモリは、これで境界がそろっている。
    - SIMD の 32 バイト境界などは、これでは足りない（`alignas` を使う）。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::max_align_t {#max_align_t}

```cpp
struct max_align_t { /* 実装定義 */ };
```

- 戻り値: （型）
- 計算量: O(1)

```cpp
#include <cstddef>
#include <print>

int main() {
  std::println("{}", alignof(std::max_align_t) >= alignof(double));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作アロケーターの基本の境界 | `alignof(std::max_align_t)` に切り上げる |

## よくあるミス

??? failure "32 バイト境界が保証されると思う"
    SIMD 用には `alignas(32)` や `aligned_alloc` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`aligned_alloc`](../memory/aligned_alloc.md) | 境界を指定して確保 |
| [`align_val_t`](../memory/new_delete/align_val_t.md) | new に境界を伝える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本のアラインメントを持つ型
    - [x] 環境で値が違う
    - [x] SIMD には足りない

## 関連ページ

- [cpprefjp: std::max_align_t](https://cpprefjp.github.io/reference/cstddef/max_align_t.html)
- [cppreference: std::max_align_t](https://en.cppreference.com/w/cpp/types/max_align_t)
