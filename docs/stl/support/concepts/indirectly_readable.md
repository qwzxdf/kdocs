---
title: std::indirectly_readable
summary: "`*it` で値を読み取れる型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_readable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの先から値を読む。`*it` で読めることを、コンセプトで表したのが `std::indirectly_readable` です。イテレータだけでなく、`std::shared_ptr` や `std::optional` のような、`*` で中身を読める型も満たします。値の型（`iter_value_t`）と参照の型（`iter_reference_t`）が決まっていることも、要求します。

!!! tip "ポイント"
    - `*it` で読める（const のオブジェクトからも）
    - 値の型と参照の型が決まる（`iter_value_t`、`iter_reference_t`）
    - `int*`、`const int*`、`shared_ptr<T>` などが満たす
    - `int` のような、`*` が使えない型は満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_readable {#indirectly_readable}

<span class="ver ver-20">C++20</span>

```cpp
template <class In>
concept indirectly_readable = /* 値の型、参照の型が決まり、*in が const でも書ける */;
```

満たすべき条件は、次のとおりです。

- `std::iter_value_t<In>`、`std::iter_reference_t<In>`、`std::iter_rvalue_reference_t<In>` が使える
- `*in` が `iter_reference_t<In>` を返す（const のオブジェクトでも）
- 値の型と参照の型の間に、共通の参照が存在する

入力イテレータの土台になるコンセプトです。`std::input_iterator` は、`input_or_output_iterator` と、これの両方を要求します。

`std::ranges::copy(in, out)` の `in` が `indirectly_readable` であることが、`copy` の最低限の要求です。

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
  std::println("const int*: {}", std::indirectly_readable<const int*>);
  std::println("vector のイテレータ: {}", std::indirectly_readable<std::vector<int>::iterator>);
  std::println("shared_ptr<int>: {}", std::indirectly_readable<std::shared_ptr<int>>);
  std::println("int: {}", std::indirectly_readable<int>);
}
```

```text title="実行結果"
const int*: true
vector のイテレータ: true
shared_ptr<int>: true
int: false
```

## ゲームでの使いどころ

`*` で中身を読める型を、まとめて受け付けるテンプレートを書くときに使います。

## よくあるミス

??? failure "読み専用なら常に満たすと思う"
    `*` が使えない型は、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_writable`](indirectly_writable.md) | 書ける条件 |
| [`input_iterator`](input_iterator.md) | これを土台にしたイテレータ |
| [`indirectly_copyable`](indirectly_copyable.md) | 読んで、別へ書ける |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_readable](https://cpprefjp.github.io/reference/iterator/indirectly_readable.html)
- [cppreference: std::indirectly_readable](https://en.cppreference.com/w/cpp/iterator/indirectly_readable)
