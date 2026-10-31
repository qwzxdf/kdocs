---
title: std::weakly_incrementable
summary: "`++` で進めるイテレータの最低限の条件を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::weakly_incrementable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータは、`++it` で次の位置に進めます。ただし、`std::istream_iterator` のように、進めたあとの位置を、もう一度たどれない（比較もできない）ものもあります。そうしたものも含めて、「`++` で進められる」という、最も弱い条件を表すのが `std::weakly_incrementable` です。他のイテレータのコンセプトの土台になっています。

!!! tip "ポイント"
    - `++i` と `i++` が書け、`++i` は `I&` を返す
    - 距離の型（`iter_difference_t`）が符号つき整数
    - 比較（`==`）できることは要求しない
    - `int` のような整数も満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::weakly_incrementable {#weakly_incrementable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept weakly_incrementable = std::movable<I> && requires(I i) {
  typename std::iter_difference_t<I>;
  requires /* 符号つき整数に準ずる */;
  { ++i } -> std::same_as<I&>;
  i++;
};
```

満たすべき条件は、次のとおりです。

- `std::movable<I>` を満たす
- `std::iter_difference_t<I>` が符号つきの整数に準ずる型
- `++i` が `I&` を返す
- `i++` が書ける（戻り値の型は問わない）

`incrementable` との違いは、複数回たどれる（再度同じ位置を指せる）ことを要求するかです。`weakly_incrementable` は、1 回きりの通過（入力ストリーム）も許します。

`std::ranges::iota_view` の要素の型は、`weakly_incrementable` を満たす必要があります。整数も、日付のような自作の型も、`++` と距離の型を用意すれば、`iota_view` に使えます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <sstream>
#include <vector>

template <std::weakly_incrementable T>
T Advance3(T x) {
  ++x; ++x; ++x;
  return x;
}

int main() {
  std::println("int: {}", std::weakly_incrementable<int>);
  std::println("int*: {}", std::weakly_incrementable<int*>);
  std::println("istream_iterator: {}", std::weakly_incrementable<std::istream_iterator<int>>);
  std::println("std::string: {}", std::weakly_incrementable<std::string>);
  std::println("{}", Advance3(10));
}
```

```text title="実行結果"
int: true
int*: true
istream_iterator: true
std::string: false
13
```

## ゲームでの使いどころ

`iota_view` のカウンターに使える型を、制約として書くときに出てきます。

## よくあるミス

??? failure "`++` があれば満たすと思う"
    `++i` が `I&` を返し、距離の型も要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`incrementable`](incrementable.md) | 複数回たどれる |
| [`input_or_output_iterator`](input_or_output_iterator.md) | 参照もできる |
| [`input_iterator`](input_iterator.md) | 読める |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::weakly_incrementable](https://cpprefjp.github.io/reference/iterator/weakly_incrementable.html)
- [cppreference: std::weakly_incrementable](https://en.cppreference.com/w/cpp/iterator/weakly_incrementable)
