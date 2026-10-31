---
title: std::inout_ptr
summary: "C のAPI に、既存のポインターを渡して、置き換えてもらう。"
order: 77
tags:
  - ユーティリティ
---

# std::inout_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

C の API には、既存のオブジェクトのポインタを受け取り、必要なら解放して新しいものに置き換えて返す、`void Resize(Thing** inout)` のような形があります。`std::inout_ptr(ptr)` は、スマート ポインタを、このような入出力引数（`T**`）として渡せる形にします。`out_ptr` との違いは、`ptr` が持っている値を、API に渡すことです。

!!! tip "ポイント"
    - `Resize(std::inout_ptr(ptr))` のように、入出力引数に渡す
    - 呼び出し前の値は、API に渡される（解放はしない）
    - API が置き換えたら、新しい値が `ptr` に入る
    - 古い値の解放は、API の責任。デリーターが二重に呼ばれないように、内部で `release` される

!!! info "このページを読む前に"
    [`std::out_ptr`](out_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::inout_ptr {#inout_ptr}

<span class="ver ver-23">C++23</span>

```cpp
template <class Pointer = void, class Smart, class... Args>
auto inout_ptr(Smart& s, Args&&... args);
```

アダプターの作成時に、`s` の持つポインタを取り出して（`release`）、API に渡す `T**` の指す先に入れます。API が値を書き換えたあと、アダプターの破棄時に、その値を `s.reset(...)` で戻します。

API が古いポインタを解放して、新しいものを返す設計だと、`s` のデリーターが古いポインタを解放しないよう、`release` します。`inout_ptr` が、それを自動で行います。

API が値を変えなかった場合は、元のポインタが、そのまま `s` に戻ります。

`realloc` のように、既存のメモリを拡張する API が典型です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <memory>
#include <print>

// C 風の API: 領域を確保し直して、ポインタを入出力引数で返す
void Grow(int** inout, std::size_t count) {
  *inout = static_cast<int*>(std::realloc(*inout, count * sizeof(int)));
}

struct FreeDeleter {
  void operator()(int* p) const { std::free(p); }
};

int main() {
  std::unique_ptr<int, FreeDeleter> p(static_cast<int*>(std::malloc(sizeof(int))));
  *p = 7;

  Grow(std::inout_ptr(p), 4);  // 古い領域は realloc が面倒を見る
  p.get()[3] = 9;
  std::println("{} {}", p.get()[0], p.get()[3]);
}
```

```text title="実行結果"
7 9
```

`realloc` が古い領域を解放して新しい領域を返しても、`p` のデリーターが二重に解放することはありません。

## ゲームでの使いどころ

領域を拡張する C のライブラリの API を、`unique_ptr` で包んだまま使うときに使います。

## よくあるミス

??? failure "out_ptr を使って、古い領域を二重に解放する"
    API が古い値を読む設計なら、`out_ptr` は、先に古い値を解放してしまいます。`inout_ptr` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`out_ptr`](out_ptr.md) | API が新しい値を書くだけの場合 |
| `std::realloc` | 領域の拡張 |
| `unique_ptr::release` | 手動で所有権を放す |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::inout_ptr](https://cpprefjp.github.io/reference/memory/inout_ptr.html)
- [cppreference: std::inout_ptr](https://en.cppreference.com/w/cpp/memory/inout_ptr_t)
