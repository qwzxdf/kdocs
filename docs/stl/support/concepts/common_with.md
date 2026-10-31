---
title: std::common_with
summary: "2 つの型が、共通の型を持つことを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::common_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

2 つの型を混ぜて計算する（`cond ? a : b` や `std::max(a, b)`）とき、両方が変換できる「共通の型」が必要です。`std::common_with<T, U>` は、`T` と `U` に共通の型があり、両方がそれに変換できることを表します。`int` と `long` は共通の型 `long` を持ちますが、`int` と `std::string` は持ちません。

!!! tip "ポイント"
    - `std::common_type_t<T, U>` が存在する
    - `T` と `U` の両方が、共通の型へ明示的に変換できる
    - `int` と `long`、`float` と `double` は満たす
    - `int` と `std::string` は満たさない

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::common_with {#common_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
concept common_with = std::same_as<std::common_type_t<T, U>, std::common_type_t<U, T>>
    && requires { static_cast<std::common_type_t<T, U>>(std::declval<T>());
                  static_cast<std::common_type_t<T, U>>(std::declval<U>()); }
    && std::common_reference_with<std::add_lvalue_reference_t<const T>, std::add_lvalue_reference_t<const U>>
    && std::common_reference_with<std::add_lvalue_reference_t<std::common_type_t<T, U>>, /* 共通の参照 */>;
```

満たすべき条件は、次のとおりです。

- `std::common_type_t<T, U>` と `std::common_type_t<U, T>` が同じ型
- `static_cast` で `T` と `U` が、その型へ変換できる
- `std::common_reference_with<const T&, const U&>` も満たす

`equality_comparable_with` や `totally_ordered_with` は、この `common_with` を土台に、型の違う値どうしの比較を定義しています。

自作の型の間で混ぜて計算したいときは、`std::common_type` を特殊化して、共通の型を用意します。

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

template <class T, class U>
  requires std::common_with<T, U>
std::common_type_t<T, U> Larger(T a, U b) {
  return a > b ? a : b;
}

int main() {
  std::println("int と long: {}", std::common_with<int, long>);
  std::println("int と double: {}", std::common_with<int, double>);
  std::println("int と string: {}", std::common_with<int, std::string>);
  std::println("{}", Larger(3, 4.5));
}
```

```text title="実行結果"
int と long: true
int と double: true
int と string: false
4.5
```

## ゲームでの使いどころ

型の違う 2 つの値を、混ぜて比べたり計算したりする関数の制約に使います。

## よくあるミス

??? failure "共通の型がない組を混ぜる"
    満たさず、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`common_reference_with`](common_reference_with.md) | 参照の共通の型 |
| [`equality_comparable_with`](equality_comparable_with.md) | 混ぜて `==` できる |
| [`convertible_to`](convertible_to.md) | 変換できる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::common_with](https://cpprefjp.github.io/reference/concepts/common_with.html)
- [cppreference: std::common_with](https://en.cppreference.com/w/cpp/concepts/common_with)
