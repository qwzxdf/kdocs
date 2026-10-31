---
title: std::make_index_sequence
summary: "0 から N-1 までの index_sequence を作る。"
order: 900
tags:
  - ユーティリティ
---

# std::make_index_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`std::make_index_sequence<N>` は、`0` から `N-1` までの `size_t` の列を、`index_sequence<0, 1, ..., N-1>` として作る別名テンプレートです。`tuple` の要素数や、配列の長さに合わせた添字の列を作るときに使います。

!!! tip "ポイント"
    - `make_index_sequence<N>` は `index_sequence<0, 1, ..., N-1>`
    - `N` は、コンパイル時の定数
    - `tuple_size_v<Tuple>` を渡して、`tuple` の全要素の添字を作る
    - 型の並びの個数なら `index_sequence_for<Ts...>`

!!! info "このページを読む前に"
    [`std::index_sequence`](index_sequence.md) を先に読んでください。

## 関数の詳しい説明

### std::make_index_sequence {#make_index_sequence}

<span class="ver ver-14">C++14</span>

```cpp
template <std::size_t N>
using make_index_sequence = std::make_integer_sequence<std::size_t, N>;
```

`make_integer_sequence<size_t, N>` の短い書き方です。

配列の長さに合わせて、添字の列を作る例です。

```cpp
template <class T, std::size_t N, std::size_t... Is>
std::array<T, N> MakeImpl(std::index_sequence<Is...>) {
  return {{ (Is, T{})... }};     // N 個の T{} を並べる
}
```

`tuple_size_v` と組み合わせれば、`tuple` の全要素の処理の添字ができます。

```cpp
using Seq = std::make_index_sequence<std::tuple_size_v<Tuple>>;
```

## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <tuple>
#include <type_traits>
#include <utility>

// 配列の要素に、添字の 2 乗を入れる
template <std::size_t... Is>
constexpr std::array<int, sizeof...(Is)> Squares(std::index_sequence<Is...>) {
  return {{static_cast<int>(Is * Is)...}};
}

int main() {
  static_assert(std::is_same_v<std::make_index_sequence<3>, std::index_sequence<0, 1, 2>>);

  constexpr auto sq = Squares(std::make_index_sequence<5>{});
  std::println("{}", sq);

  // tuple の要素数から、添字の列を作る
  using T = std::tuple<int, char, float>;
  std::println("tuple の添字の数: {}", std::make_index_sequence<std::tuple_size_v<T>>::size());
}
```

```text title="実行結果"
[0, 1, 4, 9, 16]
tuple の添字の数: 3
```

`Is` が `0, 1, 2, 3, 4` に展開され、`Is * Is` の列が配列の初期値になっています。

## ゲームでの使いどころ

コンパイル時に表（サイン テーブルなど）を作る、`constexpr` の関数で使います。

## よくあるミス

??? failure "N が負や実行時の値"
    コンパイル時の非負の定数が要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_integer_sequence`](make_integer_sequence.md) | 型を選べる |
| [`std::index_sequence_for`](index_sequence_for.md) | 型の並びの個数から作る |
| [`std::index_sequence`](index_sequence.md) | 作られる列の型 |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::make_index_sequence](https://cpprefjp.github.io/reference/utility/make_index_sequence.html)
- [cppreference: std::make_index_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
