---
title: std::sortable
summary: "並べ替えられるイテレータ（入れ替えと比較）を要求する。ランダムアクセスは別に必要。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sortable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::ranges::sort` を呼べるイテレータの条件が `std::sortable<I, R, P>` です。要素を並べ替えられて（`permutable`）、比較の述語（`R`）で順序を判定できることを表します。ただし、`sort` 自体は、さらに `random_access_iterator` を要求します。

!!! tip "ポイント"
    - `permutable` に、比較の述語の条件を足したもの
    - `R` が狭義の弱順序であること
    - `const` の範囲は満たさない
    - ランダム アクセスは要求しない（`ranges::sort` は別に要求する）

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sortable {#sortable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I, class R = std::ranges::less, class P = std::identity>
concept sortable = std::permutable<I>
    && std::indirect_strict_weak_order<R, std::projected<I, P>>;
```

満たすべき条件は、次のとおりです。

- `std::permutable<I>`
- `std::indirect_strict_weak_order<R, projected<I, P>>`

`list` のイテレータは `sortable` を満たしますが、`std::ranges::sort` はランダム アクセスを要求するため、受け付けません。`list::sort` を使います。

`std::ranges::stable_sort` や `std::ranges::partial_sort` なども、この条件を要求します。

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
  std::println("vector: {}", std::sortable<std::vector<int>::iterator>);
  std::println("const int*: {}", std::sortable<const int*>);
  std::println("list: {}", std::sortable<std::list<int>::iterator>);
  std::println("unique_ptr の範囲: {}", std::sortable<std::vector<std::unique_ptr<int>>::iterator>);
}
```

```text title="実行結果"
vector: true
const int*: false
list: true
unique_ptr の範囲: true
```

## ゲームでの使いどころ

独自のソートを書くときに、整列できる範囲の条件として使います。

## よくあるミス

??? failure "sortable ならランダム アクセスだと思う"
    `list` も満たします。`ranges::sort` は別に要求します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permutable`](permutable.md) | 土台の条件 |
| [`random_access_iterator`](random_access_iterator.md) | `sort` が別に要求する |
| [`indirect_strict_weak_order`](indirect_strict_weak_order.md) | 比較の条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::sortable](https://cpprefjp.github.io/reference/iterator/sortable.html)
- [cppreference: std::sortable](https://en.cppreference.com/w/cpp/iterator/sortable)
