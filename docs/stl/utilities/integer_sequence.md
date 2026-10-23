---
title: std::integer_sequence
summary: "整数の並び（0, 1, 2, …）をコンパイル時に作る。テンプレートで tuple などを展開する部品。"
order: 75
tags:
  - ユーティリティ
---

# std::integer_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`std::integer_sequence<T, N...>` は、**整数の並びを型として表す**クラスです。`std::make_index_sequence<N>` で `0, 1, ..., N-1` の並びを作り、テンプレートの引数として展開できます。`tuple` の全要素に処理を適用する、といった**コンパイル時の繰り返し**に使います。

!!! tip "ポイント"
    - `std::index_sequence<I...>` は `size_t` 版の別名。
    - `make_index_sequence<N>` で、0 から N-1 の並びを作る。
    - 可変引数テンプレートの「引数パック」を展開する技法とセットで使う。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::integer_sequence {#integer_sequence}

```cpp
template <class T, T... Ints>
struct integer_sequence;

template <std::size_t N>
using make_index_sequence = /* 0 .. N-1 の index_sequence */;
```

- 戻り値: （型）
- 計算量: コンパイル時

```cpp
#include <print>
#include <utility>
#include <vector>

template <std::size_t... I>
std::vector<std::size_t> ToVector(std::index_sequence<I...>) {
  return {I...};  // 0, 1, 2, 3 に展開される
}

int main() {
  std::println("{}", ToVector(std::make_index_sequence<4>{}));
}
```

```text title="実行結果"
[0, 1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| tuple の全要素に処理を適用する | `std::index_sequence` で `std::get<I>(t)` を展開 |

## よくあるミス

??? failure "使い道が分からない"
    普段のコードには出てきません。テンプレートライブラリの内部で使われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`apply`](apply.md) | 内部で使われている |
| [`tuple_size`](tuple_size.md) | 要素数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の並びを型で表す
    - [x] `make_index_sequence<N>`
    - [x] テンプレートの展開用

## 関連ページ

- [cpprefjp: std::integer_sequence](https://cpprefjp.github.io/reference/utility/integer_sequence.html)
- [cppreference: std::integer_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
