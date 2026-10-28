---
title: std::align_val_t
summary: "new にアラインメントを指定するための型。"
order: 11
group: new / delete まわり
tags:
  - メモリ
---

# std::align_val_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <new>`
</div>

`std::align_val_t` は、**`new` にアラインメント（境界）を指定する**ための型です。`new (std::align_val_t{32}) T` や、`alignas(32)` つきの型を `new` するときに、内部で使われます。SIMD 向けのデータをヒープで確保するときに知っておくと役立ちます。

!!! tip "ポイント"
    - `alignas(32)` を付けた型は、C++17 以降の `new` が自動で境界をそろえる。
    - `operator new(size, std::align_val_t)` が呼ばれる。
    - C の `aligned_alloc` に近い。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::align_val_t {#align_val_t data-toc-label="std::align_val_t"}

```cpp
struct alignas(64) CacheLine {
  float data[16];
};
auto* p = new CacheLine;  // C++17 以降、64 バイト境界で確保される
```

- C++17 から、`alignas` で大きなアラインメントを指定した型を `new` すると、**正しい位置**に確保されます（それまでは、`new` が合わせてくれないことがありました）
- `aligned_alloc` で C スタイルに取ることもできます（[malloc / free](../aligned_alloc.md#aligned_alloc)）

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

struct alignas(32) V {
  float v[8];
};

int main() {
  V* p = new V;  // alignas(32) の型は、C++17 以降の new が境界をそろえる
  std::println("{}", reinterpret_cast<std::uintptr_t>(p) % 32 == 0);
  delete p;
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| SIMD 用のデータをヒープに確保する | `alignas(32) struct Vec8 { float v[8]; };` を `new` |

## よくあるミス

??? failure "古い規格だと境界が守られない"
    C++14 以前は、`alignas` を超える境界が `new` で保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`aligned_alloc`](../aligned_alloc.md) | C 由来の確保 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] new にアラインメントを渡す型
    - [x] `alignas` つきの型は自動
    - [x] C++17

## 関連ページ

- [cpprefjp: std::align_val_t](https://cpprefjp.github.io/reference/new/align_val_t.html)
- [cppreference: std::align_val_t](https://en.cppreference.com/w/cpp/memory/new/align_val_t)
