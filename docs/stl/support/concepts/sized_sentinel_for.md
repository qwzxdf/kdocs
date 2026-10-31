---
title: std::sized_sentinel_for
summary: "イテレータとの差（距離）を定数時間で求められる終端を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sized_sentinel_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

番兵とイテレータの差（距離）を、O(1) で求められるか。`std::sized_sentinel_for<S, I>` は、`s - i` と `i - s` が書けて、その距離が分かることを表します。`std::ranges::size` や、`distance` の最適化が、これを使います。

!!! tip "ポイント"
    - `s - i` と `i - s` が書ける
    - ランダム アクセスのイテレータは、満たす
    - `list` のイテレータは満たさない（距離は O(n)）
    - 満たすと、範囲の `size()` が O(1) で求まる

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sized_sentinel_for {#sized_sentinel_for}

<span class="ver ver-20">C++20</span>

```cpp
template <class S, class I>
concept sized_sentinel_for = std::sentinel_for<S, I>
  && !std::disable_sized_sentinel_for<std::remove_cv_t<S>, std::remove_cv_t<I>>
  && requires(const I& i, const S& s) {
    { s - i } -> std::same_as<std::iter_difference_t<I>>;
    { i - s } -> std::same_as<std::iter_difference_t<I>>;
  };
```

満たすべき条件は、次のとおりです。

- `std::sentinel_for<S, I>` を満たす
- `s - i` が `iter_difference_t<I>` を返す
- `i - s` が `iter_difference_t<I>` を返す
- `disable_sized_sentinel_for<S, I>` が偽

`disable_sized_sentinel_for` は、差の演算を持つのに、計算量が O(1) でない型のために、用意された例外の指定です。

`std::ranges::distance(first, last)` は、`sized_sentinel_for` なら、差を引き算で求めます。そうでなければ、1 つずつ数えるので、O(n) です。

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

int main() {
  std::println("vector: {}",
               std::sized_sentinel_for<std::vector<int>::iterator, std::vector<int>::iterator>);
  std::println("list: {}",
               std::sized_sentinel_for<std::list<int>::iterator, std::list<int>::iterator>);
  std::println("unreachable_sentinel: {}",
               std::sized_sentinel_for<std::unreachable_sentinel_t, int*>);
}
```

```text title="実行結果"
vector: true
list: false
unreachable_sentinel: false
```

## ゲームでの使いどころ

範囲の大きさを速く求められるかで、アルゴリズムの実装を切り替えるテンプレートに使います。

## よくあるミス

??? failure "差が書けるだけで O(1) と思う"
    `disable_sized_sentinel_for` で例外の指定があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sentinel_for`](sentinel_for.md) | 土台 |
| [`random_access_iterator`](random_access_iterator.md) | 差を持つイテレータ |
| [`distance`](../iterator/distance.md) | 距離を求める |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::sized_sentinel_for](https://cpprefjp.github.io/reference/iterator/sized_sentinel_for.html)
- [cppreference: std::sized_sentinel_for](https://en.cppreference.com/w/cpp/iterator/sized_sentinel_for)
