---
title: std::iter_reference_t
summary: "イテレータの `*it` の型（参照）を取り出す型の別名。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_reference_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータを `*` で参照したときの型を知りたい。`std::vector<int>::iterator` なら `int&`、`const int*` なら `const int&` です。この型を取り出すのが `std::iter_reference_t<I>` で、`decltype(*std::declval<I&>())` と同じ意味です。

!!! tip "ポイント"
    - `*it` の型を返す
    - `vector<bool>` のようなプロキシ参照のイテレータでは、プロキシの型になる
    - `iter_value_t` は保存用の値、これはアクセス用の参照
    - C++20

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::iter_reference_t {#iter_reference_t}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
using iter_reference_t = decltype(*std::declval<I&>());
```

`std::input_or_output_iterator<I>` を満たす `I` に使えます。

通常のイテレータは `T&`、`const_iterator` は `const T&`、`move_iterator` は `T&&` を返します。アルゴリズムの戻り値の型や、関数に渡す引数の型を、イテレータから導くときに使います。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

int main() {
  static_assert(std::is_same_v<std::iter_reference_t<std::vector<int>::iterator>, int&>);
  static_assert(std::is_same_v<std::iter_reference_t<const int*>, const int&>);
  static_assert(std::is_same_v<std::iter_reference_t<std::move_iterator<int*>>, int&&>);

  // vector<bool> の参照は、本物の参照ではない
  using Ref = std::iter_reference_t<std::vector<bool>::iterator>;
  std::println("bool& ではない: {}", !std::is_same_v<Ref, bool&>);
}
```

```text title="実行結果"
bool& ではない: true
```

## ゲームでの使いどころ

イテレータの先の要素に、関数を適用するテンプレートで、引数の型を決めるときに使います。

## よくあるミス

??? failure "常に T& だと思う"
    `const_iterator` や `move_iterator` では違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_value_t`](iter_value_t.md) | 保存用の値の型 |
| [`iter_move`](iter_move.md) | 右辺値として取り出す |
| [`iter_difference_t`](iter_difference_t.md) | 距離の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::iter_reference_t](https://cpprefjp.github.io/reference/iterator/iter_reference_t.html)
- [cppreference: std::iter_reference_t](https://en.cppreference.com/w/cpp/iterator/iter_reference_t)
