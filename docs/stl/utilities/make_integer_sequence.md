---
title: std::make_integer_sequence
summary: "0 から N-1 までの integer_sequence を、整数型を選んで作る。"
order: 900
tags:
  - ユーティリティ
---

# std::make_integer_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`std::integer_sequence<int, 0, 1, 2, 3>` を、手で書くのは面倒です。`std::make_integer_sequence<T, N>` は、`0` から `N-1` までの列を、`integer_sequence<T, 0, 1, ..., N-1>` として作る別名テンプレートです。

!!! tip "ポイント"
    - `make_integer_sequence<T, N>` は、`integer_sequence<T, 0, 1, ..., N-1>`
    - `N` が 0 なら、空の列
    - `size_t` の列は `make_index_sequence<N>`
    - コンパイル時の N の個数だけ、展開される

!!! info "このページを読む前に"
    [`std::integer_sequence`](integer_sequence.md) を先に読んでください。

## 関数の詳しい説明

### std::make_integer_sequence {#make_integer_sequence}

<span class="ver ver-14">C++14</span>

```cpp
template <class T, T N>
using make_integer_sequence = std::integer_sequence<T, /* 0, 1, ..., N-1 */>;
```

| 引数 | 意味 |
| --- | --- |
| `T` | 要素の整数型 |
| `N` | 列の長さ。0 以上 |

`make_integer_sequence<int, 4>` は `integer_sequence<int, 0, 1, 2, 3>` です。`N` が負だと、コンパイル エラーです。

実装は、再帰ではなく、コンパイラの組み込み機能で行われます。`N` が大きくても、コンパイル時間があまりかかりません。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>

int main() {
  static_assert(std::is_same_v<std::make_integer_sequence<int, 4>,
                               std::integer_sequence<int, 0, 1, 2, 3>>);
  static_assert(std::is_same_v<std::make_integer_sequence<int, 0>,
                               std::integer_sequence<int>>);

  std::println("長さ: {}", std::make_integer_sequence<int, 4>::size());
  std::println("空の長さ: {}", std::make_integer_sequence<int, 0>::size());
}
```

```text title="実行結果"
長さ: 4
空の長さ: 0
```

## ゲームでの使いどころ

直接使うより、`make_index_sequence` のほうが多く使われます。

## よくあるミス

??? failure "N に負の数や実行時の値を渡す"
    コンパイル時の非負の定数が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_index_sequence`](make_index_sequence.md) | `size_t` 版 |
| [`std::integer_sequence`](integer_sequence.md) | 作られる列の型 |
| [`std::index_sequence_for`](index_sequence_for.md) | 型の並びから作る |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::make_integer_sequence](https://cpprefjp.github.io/reference/utility/make_integer_sequence.html)
- [cppreference: std::make_integer_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
