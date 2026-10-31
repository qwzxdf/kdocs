---
title: std::indirect_equivalence_relation
summary: "2 つのイテレータが指す値で、同値関係を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_equivalence_relation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

等しさの判定を、「同値関係」に限定したい。同値関係とは、反射（自分と等しい）、対称（`a == b` なら `b == a`）、推移（`a == b` かつ `b == c` なら `a == c`）を満たす関係です。`std::indirect_equivalence_relation<R, I1, I2>` は、`indirect_binary_predicate` に、この意味の約束を足した条件です。

!!! tip "ポイント"
    - `indirect_binary_predicate` と同じ形で呼べる
    - 同値関係であること（反射・対称・推移）を約束する
    - `std::ranges::unique`、`adjacent_find` などの述語に使われる
    - 意味の約束は、コンパイラには確かめられない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_equivalence_relation {#indirect_equivalence_relation}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I1, class I2 = I1>
concept indirect_equivalence_relation = std::indirectly_readable<I1> && std::indirectly_readable<I2>
    && std::copy_constructible<F>
    && std::equivalence_relation<F&, std::iter_value_t<I1>&, std::iter_value_t<I2>&>
    /* ほかの組み合わせも */;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<I1>`、`std::indirectly_readable<I2>`、`std::copy_constructible<R>`
- `std::equivalence_relation<R&, 値と参照のすべての組み合わせ>`

`equivalence_relation` は、`predicate` と同じ構文です。違いは、意味の約束だけです。「差の絶対値が 1 以下なら等しい」のような関係は、推移的でない（`1 ≈ 2`、`2 ≈ 3` でも `1 ≈ 3` ではない）ので、同値関係ではありません。そのような述語を `unique` などに渡すと、結果が不定です。

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
  std::println("equal_to: {}",
               std::indirect_equivalence_relation<std::ranges::equal_to, int*, int*>);

  // 構文は満たすが、意味の上では同値関係でない例 (推移的でない)
  auto close = [](int a, int b) { return a - b <= 1 && b - a <= 1; };
  std::println("構文上は満たす: {}", std::indirect_equivalence_relation<decltype(close), int*, int*>);
}
```

```text title="実行結果"
equal_to: true
構文上は満たす: true
```

## ゲームでの使いどころ

`unique` のように、同値関係を前提にするアルゴリズムの述語に使います。

## よくあるミス

??? failure "推移的でない述語を渡す"
    構文は通りますが、結果が不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_binary_predicate`](indirect_binary_predicate.md) | 意味の約束がない版 |
| [`equivalence_relation`](equivalence_relation.md) | 一般の同値関係 |
| [`indirect_strict_weak_order`](indirect_strict_weak_order.md) | 順序の関係 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirect_equivalence_relation](https://cpprefjp.github.io/reference/iterator/indirect_equivalence_relation.html)
- [cppreference: std::indirect_equivalence_relation](https://en.cppreference.com/w/cpp/iterator/indirect_equivalence_relation)
