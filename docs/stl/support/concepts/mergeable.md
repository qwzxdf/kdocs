---
title: std::mergeable
summary: "2 つの整列済み範囲を併合できるイテレータの組を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::mergeable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

2 つの整列済みの範囲を、1 つの整列済みの範囲にまとめる。`std::ranges::merge` が成り立つ条件が `std::mergeable<I1, I2, Out, R, P1, P2>` です。入力の 2 つが読めて、出力が書けて、比較の述語が使えることを表します。

!!! tip "ポイント"
    - `I1`、`I2` が入力イテレータで、`Out` が出力のイテレータ
    - 両方の要素を、`Out` にコピーして書ける
    - 比較の述語（`R`）で、順序を判定できる
    - `std::ranges::merge`、`set_union` などの条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::mergeable {#mergeable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I1, class I2, class Out, class R = std::ranges::less,
          class P1 = std::identity, class P2 = std::identity>
concept mergeable = std::input_iterator<I1> && std::input_iterator<I2>
    && std::weakly_incrementable<Out>
    && std::indirectly_copyable<I1, Out> && std::indirectly_copyable<I2, Out>
    && std::indirect_strict_weak_order<R, std::projected<I1, P1>, std::projected<I2, P2>>;
```

満たすべき条件は、次のとおりです。

- `std::input_iterator<I1>`、`std::input_iterator<I2>`、`std::weakly_incrementable<Out>`
- `std::indirectly_copyable<I1, Out>` と `std::indirectly_copyable<I2, Out>`
- `std::indirect_strict_weak_order<R, projected<I1, P1>, projected<I2, P2>>`

入力の 2 つが、整列済みであることは、構文では確かめられません。整列していない範囲を渡すと、出力は整列されません。

`ranges::merge` の出力先は、入力の範囲と重ならないようにします。

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
#include <algorithm>
#include <memory>
#include <string>

int main() {
  std::println("int*, int*, int*: {}", std::mergeable<int*, int*, int*>);
  std::println("const int*, const int*, int*: {}", std::mergeable<const int*, const int*, int*>);
  std::println("出力が const: {}", std::mergeable<const int*, const int*, const int*>);
}
```

```text title="実行結果"
int*, int*, int*: true
const int*, const int*, int*: true
出力が const: false
```

## ゲームでの使いどころ

整列済みの 2 つの配列を、1 つにまとめるアルゴリズムの制約に使います。

## よくあるミス

??? failure "整列していない範囲を渡す"
    構文は通りますが、出力が整列されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`merge`](../../algorithms/merge.md) | これを使うアルゴリズム |
| [`sortable`](sortable.md) | 整列できる条件 |
| [`indirectly_copyable`](indirectly_copyable.md) | コピーの条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::mergeable](https://cpprefjp.github.io/reference/iterator/mergeable.html)
- [cppreference: std::mergeable](https://en.cppreference.com/w/cpp/iterator/mergeable)
