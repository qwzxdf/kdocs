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

テンプレートで、`0, 1, 2, ..., N-1` のような整数の列を、パラメーター パックとして扱いたい。たとえば、`tuple` の全要素を順に処理するとき、添字の列 `0, 1, 2` が要ります。`std::integer_sequence<T, ...>` は、コンパイル時の整数の列を、型として表すものです。

!!! tip "ポイント"
    - 整数の列を、型（`integer_sequence<T, 0, 1, 2>`）として持つ
    - 実体の値は持たない。パラメーター パックを取り出すための入れ物
    - 添字の列には `index_sequence` が使われる
    - 列は `make_integer_sequence<T, N>` で作る

!!! info "このページを読む前に"
    [`std::make_integer_sequence`](make_integer_sequence.md) と、パラメーター パックの基本を先に読んでください。

## 関数の詳しい説明

### std::integer_sequence {#integer_sequence}

<span class="ver ver-14">C++14</span>

```cpp
template <class T, T... Ints>
struct integer_sequence {
  using value_type = T;
  static constexpr std::size_t size() noexcept { return sizeof...(Ints); }
};
```

`integer_sequence<int, 3, 1, 4>` は、整数 3、1、4 の列を表します。値を持つ変数ではなく、型です。

使い方は、関数テンプレートの引数に、この型を受け取って、`Ints...` を取り出します。

```cpp
template <class T, T... Ints>
void Print(std::integer_sequence<T, Ints...>) {
  ((std::print("{} ", Ints)), ...);   // 畳み込み式
}
```

呼び出し側は、`Print(std::make_integer_sequence<int, 4>{})` のように、列の型の空のオブジェクトを渡します。コンパイラが `Ints` を推論して、`0, 1, 2, 3` を取り出します。

`size()` は、列の長さです。

## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

// 列の要素の合計をコンパイル時に求める
template <class T, T... Ints>
constexpr T Sum(std::integer_sequence<T, Ints...>) {
  return (Ints + ... + T{});
}

int main() {
  using Seq = std::integer_sequence<int, 3, 1, 4>;
  std::println("長さ: {}", Seq::size());
  std::println("合計: {}", Sum(Seq{}));

  // 0 から 4 までの列
  constexpr int total = Sum(std::make_integer_sequence<int, 5>{});
  static_assert(total == 10);
  std::println("0..4 の合計: {}", total);
}
```

```text title="実行結果"
長さ: 3
合計: 8
0..4 の合計: 10
```

## ゲームでの使いどころ

自分で書くより、`std::apply` や構造化束縛の裏で動いています。`tuple` の全要素に処理をするような、テンプレートのコードで出てきます。

## よくあるミス

??? failure "型を値のように扱う"
    `integer_sequence` は型です。関数に渡すときは `Seq{}` の空のオブジェクトにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::index_sequence`](index_sequence.md) | `size_t` の列。添字用 |
| [`std::make_integer_sequence`](make_integer_sequence.md) | `0` から `N-1` の列を作る |
| [`std::apply`](apply.md) | 内部で使っている |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::integer_sequence](https://cpprefjp.github.io/reference/utility/integer_sequence.html)
- [cppreference: std::integer_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
