---
title: std::indirectly_unary_invocable
summary: "イテレータが指す値で、1 引数の関数を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_unary_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの先の要素を、関数に渡して呼びたい。`std::ranges::for_each` が成り立つ条件が `std::indirectly_unary_invocable<F, I>` です。`F` を、`I` が指す値や参照で呼べることを表します。

!!! tip "ポイント"
    - `F` を、イテレータの先の値、参照のどちらでも呼べる
    - 呼んだ結果の型は問わない
    - `std::ranges::for_each` の引数の条件
    - 状態を持たない関数（同じ引数で同じ結果）まで要求するなら `regular` 版

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_unary_invocable {#indirectly_unary_invocable}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I>
concept indirectly_unary_invocable = std::indirectly_readable<I> && std::copy_constructible<F>
    && std::invocable<F&, std::iter_value_t<I>&> && std::invocable<F&, std::iter_reference_t<I>>
    && /* 結果の型に共通の参照がある */;
```

満たすべき条件は、次のとおりです。

- `std::copy_constructible<F>`
- `F&` を `iter_value_t<I>&` と `iter_reference_t<I>` で呼べる
- 結果に共通の参照が存在する

ラムダ式 `[](int x) { ... }` は、`int*` に対して満たします。`std::string` を取るラムダは、`int*` に対して満たしません。

`for_each` や `transform` に、要素の型と合わない関数を渡したときの、エラーの原因を、コンセプトの形で分かりやすく伝えます。

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
  auto print_int = [](int x) { (void)x; };
  auto takes_string = [](const std::string& s) { (void)s; };

  std::println("int の関数 × int*: {}", std::indirectly_unary_invocable<decltype(print_int), int*>);
  std::println("string の関数 × int*: {}", std::indirectly_unary_invocable<decltype(takes_string), int*>);
}
```

```text title="実行結果"
int の関数 × int*: true
string の関数 × int*: false
```

## ゲームでの使いどころ

要素に関数を適用するアルゴリズムを自作するときの、制約に使います。

## よくあるミス

??? failure "要素の型と合わない関数を渡す"
    満たさず、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_regular_unary_invocable`](indirectly_regular_unary_invocable.md) | 正則な呼び出しを要求する |
| [`indirect_unary_predicate`](indirect_unary_predicate.md) | 結果が `bool` になる |
| [`invocable`](invocable.md) | 一般の呼び出し可能 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_unary_invocable](https://cpprefjp.github.io/reference/iterator/indirectly_unary_invocable.html)
- [cppreference: std::indirectly_unary_invocable](https://en.cppreference.com/w/cpp/iterator/indirectly_unary_invocable)
