---
title: std::indirectly_comparable
summary: "2 つのイテレータが指す要素を、比較関数で比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

2 つの範囲の要素どうしを、比べたい。`std::ranges::equal` や `std::ranges::mismatch` が成り立つ条件が `std::indirectly_comparable<I1, I2, R>` です。`I1` と `I2` の先の要素を、述語 `R` で比べられることを表します。

!!! tip "ポイント"
    - 2 つのイテレータの先を、比較の述語 `R` で比べられる
    - 射影（`Proj1`、`Proj2`）を通した後の値を比べる
    - `std::ranges::equal_to` を渡すと `==` 比較
    - `std::ranges::equal`、`mismatch`、`search` の引数の条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_comparable {#indirectly_comparable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I1, class I2, class R, class P1 = std::identity, class P2 = std::identity>
concept indirectly_comparable = std::indirect_binary_predicate<R, std::projected<I1, P1>, std::projected<I2, P2>>;
```

満たすべき条件は、次のとおりです。

- `std::indirect_binary_predicate<R, projected<I1, P1>, projected<I2, P2>>` を満たす

`int*` と `std::string*` を `equal_to` で比べると、`int` と `std::string` の `==` がないので、満たしません。

射影を渡すと、比べる前に変換できます。`std::ranges::equal(a, b, {}, &Item::id, &Item::id)` のように、構造体のメンバーで比べられます。

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
  std::println("int* どうし: {}", std::indirectly_comparable<int*, int*, std::ranges::equal_to>);
  std::println("int と long: {}", std::indirectly_comparable<int*, long*, std::ranges::equal_to>);
  std::println("int と string: {}", std::indirectly_comparable<int*, std::string*, std::ranges::equal_to>);
}
```

```text title="実行結果"
int* どうし: true
int と long: true
int と string: false
```

## ゲームでの使いどころ

2 つの範囲を比べるアルゴリズムを自作するときに、制約として使います。

## よくあるミス

??? failure "比較できない型の範囲を渡す"
    満たさず、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_binary_predicate`](indirect_binary_predicate.md) | 土台の条件 |
| [`indirect_equivalence_relation`](indirect_equivalence_relation.md) | 同値関係 |
| [`projected`](../iterator/projected.md) | 射影を通したイテレータ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_comparable](https://cpprefjp.github.io/reference/iterator/indirectly_comparable.html)
- [cppreference: std::indirectly_comparable](https://en.cppreference.com/w/cpp/iterator/indirectly_comparable)
