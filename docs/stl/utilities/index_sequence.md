---
title: std::index_sequence
summary: "0, 1, 2, … の番号の並びを、型で表す。"
order: 900
tags:
  - ユーティリティ
---

# std::index_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`tuple` の全要素を順番に処理するには、添字 `0, 1, 2, ...` をテンプレートの引数として取り出す必要があります。`std::index_sequence<0, 1, 2>` は、`size_t` の整数の列を表す型で、`integer_sequence<size_t, ...>` の別名です。`tuple` やコンテナの添字に使うので、専用の名前が付いています。

!!! tip "ポイント"
    - `integer_sequence<std::size_t, ...>` の別名
    - `0, 1, 2, ..., N-1` の列は `make_index_sequence<N>`
    - 型の並びの個数に合わせた列は `index_sequence_for<Ts...>`
    - `tuple` の全要素の処理や、配列の初期化に使う

!!! info "このページを読む前に"
    [`std::integer_sequence`](integer_sequence.md) を先に読んでください。

## 関数の詳しい説明

### std::index_sequence {#index_sequence}

<span class="ver ver-14">C++14</span>

```cpp
template <std::size_t... Ints>
using index_sequence = std::integer_sequence<std::size_t, Ints...>;
```

型が `size_t` に固定されているだけで、`integer_sequence` と使い方は同じです。

`tuple` の全要素を処理する典型的な形は、次のとおりです。

```cpp
template <class Tuple, std::size_t... Is>
void PrintImpl(const Tuple& t, std::index_sequence<Is...>) {
  ((std::println("{}", std::get<Is>(t))), ...);   // Is = 0, 1, 2, ... に展開
}

template <class... Ts>
void Print(const std::tuple<Ts...>& t) {
  PrintImpl(t, std::index_sequence_for<Ts...>{});
}
```

`Is...` が `0, 1, 2` に展開されるので、`std::get<Is>(t)` が、各要素に対応します。

C++20 以降は、テンプレート ラムダでも書けます。`[]<std::size_t... Is>(std::index_sequence<Is...>) { ... }(std::make_index_sequence<N>{})` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <tuple>
#include <utility>

template <class Tuple, std::size_t... Is>
void PrintImpl(const Tuple& t, std::index_sequence<Is...>) {
  // Is... を 0, 1, 2 に展開して、各要素を表示する
  (std::println("[{}] {}", Is, std::get<Is>(t)), ...);
}

template <class... Ts>
void Print(const std::tuple<Ts...>& t) {
  PrintImpl(t, std::index_sequence_for<Ts...>{});
}

int main() {
  Print(std::make_tuple(10, std::string("Hero"), 1.5));
}
```

```text title="実行結果"
[0] 10
[1] Hero
[2] 1.5
```

## ゲームでの使いどころ

`tuple` で持った複数のコンポーネントに、順番に処理をかけるようなテンプレートに出てきます。

## よくあるミス

??? failure "型を値のように扱う"
    関数には `std::index_sequence_for<Ts...>{}` と、空のオブジェクトを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::integer_sequence`](integer_sequence.md) | 型を選べる元のテンプレート |
| [`std::make_index_sequence`](make_index_sequence.md) | `0` から `N-1` の列を作る |
| [`std::index_sequence_for`](index_sequence_for.md) | 型の並びの個数から作る |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::index_sequence](https://cpprefjp.github.io/reference/utility/index_sequence.html)
- [cppreference: std::index_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
