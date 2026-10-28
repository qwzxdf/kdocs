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

メモリを確保するときに、どんな型のオブジェクトを置いても大丈夫な配置（アラインメント）が知りたいことがあります。`std::max_align_t` は、<strong>この環境で、組み込みの型の中で最も厳しいアラインメントを持つ型</strong>です。`new` が返すメモリは、この境界に揃っています。

!!! tip "ポイント"
    - `alignof(std::max_align_t)` は、組み込みの型で最大のアラインメント
    - `malloc` や `new` が返すアドレスは、この境界に揃う
    - 自前のアロケーターの既定の境界に使う
    - 多くの環境で 16

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::max_align_t {#max_align_t}

<span class="ver ver-11">C++11</span>

```cpp
struct max_align_t { /* 実装定義 */ };
```

`alignof(std::max_align_t)` は、`long double` などの組み込み型の中で最も大きいアラインメントです。多くの 64 ビット環境で 16 バイトです。

自前のアロケーターは、確保した領域の先頭をこの境界に揃えれば、どの型を置いても安全です。SIMD 型などの、より厳しい境界（32、64）を要求する型には、`alignas` を別に指定する必要があります。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>

int main() {
  std::println("double 以上の境界: {}", alignof(std::max_align_t) >= alignof(double));
  std::println("2 の累乗: {}", (alignof(std::max_align_t) & (alignof(std::max_align_t) - 1)) == 0);
}
```

```text title="実行結果"
double 以上の境界: true
2 の累乗: true
```

## ゲームでの使いどころ

自前のアロケーターで、既定の境界を決めます。

```cpp
constexpr std::size_t kDefaultAlign = alignof(std::max_align_t);
```

## よくあるミス

??? failure "SIMD 型に使えると思う"
    より厳しい境界は `alignas` で指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`align`](../memory/align.md) | ポインターを境界に揃える |
| [`alignment_of`](type_traits/alignment_of.md) | 型のアラインメント |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `max_align_t` は組み込みの型で最大のアラインメントを持つ型
    - [x] `new` が返すメモリはこの境界
    - [x] SIMD 型には別に `alignas`

## 関連ページ

- [cpprefjp: std::max_align_t](https://cpprefjp.github.io/reference/cstddef/max_align_t.html)
- [cppreference: std::max_align_t](https://en.cppreference.com/w/cpp/types/max_align_t)
