---
title: std::equality_comparable_with
summary: "2 つの異なる型を `==` で比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equality_comparable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::equality_comparable<T>` は、同じ型どうしを `==` で比べられることを表します。`std::equality_comparable_with<T, U>` は、<strong>型の違う値どうし</strong>を `==` で比べられることを表します。たとえば、`std::string` と `const char*` は、比べられます。

!!! tip "ポイント"
    - `t == u`、`u == t`、`t != u`、`u != t` がすべて書ける
    - 両方の型が、それぞれ `equality_comparable`
    - `common_reference_with` を満たす（共通の型へ変換できる）
    - 比べた結果が、変換後に比べた結果と一致するという意味の約束がある

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::equality_comparable_with {#equality_comparable_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
concept equality_comparable_with = std::equality_comparable<T> && std::equality_comparable<U>
    && std::common_reference_with<const std::remove_reference_t<T>&, const std::remove_reference_t<U>&>
    && std::equality_comparable<std::common_reference_t<const std::remove_reference_t<T>&, const std::remove_reference_t<U>&>>
    && /* 4 つの比較が書ける */;
```

満たすべき条件は、次のとおりです。

- `std::equality_comparable<T>` と `std::equality_comparable<U>`
- `std::common_reference_with<const T&, const U&>`
- `t == u`、`u == t`、`t != u`、`u != t` が `boolean-testable` を返す

`int` と `long` は満たします。`int` と `std::string` は、`==` が書けないので満たしません。

約束の部分が重要です。`t == u` の結果は、両方を共通の型に変換してから比べた結果と、同じであるべきです。そうでない `==` を定義すると、構文は満たしても、`std::ranges::find` などの結果が、おかしくなります。

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
  std::println("int と long: {}", std::equality_comparable_with<int, long>);
  std::println("string と const char*: {}", std::equality_comparable_with<std::string, const char*>);
  std::println("int と string: {}", std::equality_comparable_with<int, std::string>);
}
```

```text title="実行結果"
int と long: true
string と const char*: true
int と string: false
```

## ゲームでの使いどころ

`std::ranges::find(r, value)` の `value` の型が、範囲の要素の型と違っても許す、という設計の土台です。

## よくあるミス

??? failure "意味の違う == を定義する"
    構文は満たしても、アルゴリズムの結果が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equality_comparable`](equality_comparable.md) | 同じ型どうし |
| [`totally_ordered_with`](totally_ordered_with.md) | 大小の比較 |
| [`common_with`](common_with.md) | 共通の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::equality_comparable_with](https://cpprefjp.github.io/reference/concepts/equality_comparable_with.html)
- [cppreference: std::equality_comparable_with](https://en.cppreference.com/w/cpp/concepts/equality_comparable_with)
