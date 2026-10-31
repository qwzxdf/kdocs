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

通常の `new` は、型の標準のアライメント（普通は 16 バイト以下）で確保しますが、SIMD の型や、キャッシュ ラインに合わせた型は、32 や 64 バイトの境界を要求します。C++17 の `std::align_val_t` は、`operator new` に、アライメントを伝えるための型です。

!!! tip "ポイント"
    - `enum class align_val_t : std::size_t {};`
    - `alignas(64)` の型に `new` すると、コンパイラが自動で `align_val_t` つきの `operator new` を呼ぶ
    - 解放も `align_val_t` つきの `operator delete`
    - 自分で呼ぶことは少ない。アライメント指定の自作 `operator new` を書くときに出てくる

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### std::align_val_t {#align_val_t}

<span class="ver ver-17">C++17</span>

```cpp
enum class align_val_t : std::size_t {};

void* operator new(std::size_t size, std::align_val_t align);
void  operator delete(void* ptr, std::align_val_t align) noexcept;
```

C++17 より前は、標準以上のアライメントの型を `new` で確保しても、アライメントが守られませんでした。C++17 で、`alignas` つきの型の `new` 式が、`align_val_t` を渡す `operator new` を呼ぶようになりました。

`align` の値は、2 のべき乗である必要があります。

自作のアロケーターを書くときは、`std::aligned_alloc` や、プラットフォーム固有の関数（`_aligned_malloc`）で実装します。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <new>
#include <print>

struct alignas(64) CacheLine {
  char data[64];
};

int main() {
  // alignas(64) の型を new すると、64 バイト境界で確保される
  CacheLine* p = new CacheLine;
  std::println("64 バイト境界: {}", reinterpret_cast<std::uintptr_t>(p) % 64 == 0);
  delete p;

  // 明示的に align_val_t を渡す
  void* q = ::operator new(128, std::align_val_t{128});
  std::println("128 バイト境界: {}", reinterpret_cast<std::uintptr_t>(q) % 128 == 0);
  ::operator delete(q, std::align_val_t{128});
}
```

```text title="実行結果"
64 バイト境界: true
128 バイト境界: true
```

## ゲームでの使いどころ

SIMD 用のデータや、キャッシュ ラインの偽共有を避けたいデータ構造を、`new` で確保するときに、アライメントを守らせます。

## よくあるミス

??? failure "align を 2 のべき乗にしない"
    未定義の動作になります。

??? failure "align_val_t なしの delete で解放する"
    対応する解放関数を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`operator new`](operator_new.md) | 確保関数 |
| [`aligned_alloc`](../aligned_alloc.md) | C の関数 |
| `alignas` | 型にアライメントを指定する |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::align_val_t](https://cpprefjp.github.io/reference/new/align_val_t.html)
- [cppreference: std::align_val_t](https://en.cppreference.com/w/cpp/memory/new/align_val_t)
