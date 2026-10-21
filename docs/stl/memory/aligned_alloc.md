---
title: aligned_alloc
summary: "アラインメントを指定して、メモリを確保する。"
order: 24
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# aligned_alloc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`aligned_alloc` は、**指定した境界（アラインメント）にそろえたメモリを確保する**関数です。SIMD（SSE / AVX）のために 16 や 32 バイト境界が欲しいときに使います。解放は `free` です。MSVC には無く、`_aligned_malloc` / `_aligned_free` を使います。

!!! tip "ポイント"
    - アラインメントは 2 のべき乗。サイズはその倍数にする。
    - MSVC では `_aligned_malloc` と `_aligned_free`（`free` では解放できない）。
    - C++ では `new (std::align_val_t{32}) T` も使える。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### aligned_alloc {#aligned_alloc}

```cpp
void* aligned_alloc(std::size_t alignment, std::size_t size);  // C11 / C++17
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alignment` | `std::size_t` | 先頭アドレスの約束（2 の累乗。64 ならキャッシュラインにそろう） |
| `size` | `std::size_t` | バイト数。**`alignment` の倍数**にする必要がある（実装による） |

- 戻り値: `alignment` の倍数のアドレスから始まる領域。失敗したら `nullptr`。`free` で返す
- SIMD（SSE / AVX）の命令や、キャッシュラインにそろえたいデータで使います
- **MSVC（Visual Studio）は `aligned_alloc` に対応していません**（Windows のヒープの仕様のため）。次の `_aligned_malloc` を使うか、`alignas` 付きの型を `new` します

### _aligned_malloc（MSVC） {#aligned_malloc_msvc data-toc-label="_aligned_malloc（MSVC）"}

```cpp
void* _aligned_malloc(std::size_t size, std::size_t alignment);  // 引数の順番が逆
void _aligned_free(void* ptr);                                    // free ではなくこちらで返す
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `size` | `std::size_t` | バイト数 |
| `alignment` | `std::size_t` | アラインメント |

- Windows（`<malloc.h>`）の、アラインメント付き確保です。**`aligned_alloc` と引数の順番が逆**で、解放も `_aligned_free` を使います（`free` で返すと壊れます）
- 移植したいなら、`alignas(64)` を付けた型を `new` する方法（C++17）が一番簡単です

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <cstdlib>
#include <print>

int main() {
#ifdef _MSC_VER
  void* p = _aligned_malloc(64, 32);
#else
  void* p = std::aligned_alloc(32, 64);  // サイズは境界の倍数にする
#endif
  std::println("{}", reinterpret_cast<std::uintptr_t>(p) % 32 == 0);
#ifdef _MSC_VER
  _aligned_free(p);
#else
  std::free(p);
#endif
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| SIMD 用に 32 バイト境界のバッファを確保する | `aligned_alloc(32, size)` |

## よくあるミス

??? failure "MSVC で使えない"
    `_aligned_malloc` を使います。解放も `_aligned_free` です。

??? failure "サイズがアラインメントの倍数でない"
    規格上は未定義です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 通常の確保 |
| [`align_val_t`](new_delete/align_val_t.md) | C++ の new 向け |

## コンパイラ対応

C 由来の関数です。`aligned_alloc` は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 境界を指定して確保
    - [x] MSVC は `_aligned_malloc`
    - [x] サイズは倍数に

## 関連ページ

- [cpprefjp: aligned_alloc](https://cpprefjp.github.io/reference/cstdlib/aligned_alloc.html)
- [cppreference: aligned_alloc](https://en.cppreference.com/w/cpp/memory/c/aligned_alloc)
