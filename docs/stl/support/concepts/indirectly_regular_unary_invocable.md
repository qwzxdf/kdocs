---
title: std::indirectly_regular_unary_invocable
summary: "イテレータが指す値で、副作用なく 1 引数の関数を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_regular_unary_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`indirectly_unary_invocable` に、「正則（regular）」という条件を足したのが `std::indirectly_regular_unary_invocable<F, I>` です。正則とは、同じ引数で呼べば、いつも同じ結果が返る（状態を持たず、副作用で結果が変わらない）ことです。`std::ranges::sort` の射影の関数に、この条件があります。

!!! tip "ポイント"
    - `indirectly_unary_invocable` と同じ形で呼べる
    - `std::regular_invocable` を要求する（同じ引数で同じ結果）
    - 射影（`Proj`）に使う関数の条件
    - 構文上は区別できない。使い手の約束

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_regular_unary_invocable {#indirectly_regular_unary_invocable}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I>
concept indirectly_regular_unary_invocable = std::indirectly_readable<I>
    && std::copy_constructible<F>
    && std::regular_invocable<F&, std::iter_value_t<I>&>
    && std::regular_invocable<F&, std::iter_reference_t<I>>
    && /* 結果の型に共通の参照がある */;
```

満たすべき条件は、次のとおりです。

- `std::copy_constructible<F>`
- `F&` を `iter_value_t<I>&` と `iter_reference_t<I>` で、`regular_invocable` として呼べる

`regular_invocable` と `invocable` は、構文では区別できません。違いは、意味の約束だけです。呼び出しごとに結果が変わる関数（乱数、カウンター）を渡すと、約束を破ります。

範囲のアルゴリズムは、同じ要素に対して射影を複数回呼ぶことがあります。結果が変わると、整列の結果が壊れます。

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

struct Item { int id; };

int main() {
  auto get_id = [](const Item& i) { return i.id; };

  std::println("射影として使える: {}",
               std::indirectly_regular_unary_invocable<decltype(get_id), Item*>);
  std::println("int* には使えない: {}",
               std::indirectly_regular_unary_invocable<decltype(get_id), int*>);
}
```

```text title="実行結果"
射影として使える: true
int* には使えない: false
```

## ゲームでの使いどころ

射影に渡す関数が、状態を持たない純粋な関数であることを、制約として表します。

## よくあるミス

??? failure "呼ぶたびに結果が変わる関数を渡す"
    約束を破り、整列などの結果が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_unary_invocable`](indirectly_unary_invocable.md) | 正則を要求しない |
| [`regular_invocable`](regular_invocable.md) | 一般の正則な呼び出し可能 |
| [`projected`](../iterator/projected.md) | 射影を通したイテレータ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_regular_unary_invocable](https://cpprefjp.github.io/reference/iterator/indirectly_regular_unary_invocable.html)
- [cppreference: std::indirectly_regular_unary_invocable](https://en.cppreference.com/w/cpp/iterator/indirectly_regular_unary_invocable)
