---
title: std::totally_ordered_with
summary: "2 つの異なる型を `<` などで比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::totally_ordered_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::totally_ordered_with<T, U>` は、型の違う値どうしを、`<`、`>`、`<=`、`>=` で比べられ、しかも全順序（どの 2 つも大小が決まる）になっていることを表します。`int` と `double` は満たしますが、`int` と `std::string` は満たしません。

!!! tip "ポイント"
    - `<`、`>`、`<=`、`>=` が、両方向で書ける
    - `equality_comparable_with` も満たす
    - 全順序であること（意味の約束）
    - `std::ranges::lower_bound(r, value)` で、値の型が違ってもよい理由

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::totally_ordered_with {#totally_ordered_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
concept totally_ordered_with = std::totally_ordered<T> && std::totally_ordered<U>
    && std::equality_comparable_with<T, U>
    && std::totally_ordered<std::common_reference_t<const std::remove_reference_t<T>&, const std::remove_reference_t<U>&>>
    && /* < > <= >= が両方向で書ける */;
```

満たすべき条件は、次のとおりです。

- `std::totally_ordered<T>` と `std::totally_ordered<U>`
- `std::equality_comparable_with<T, U>`
- `t < u`、`t > u`、`t <= u`、`t >= u` と、`u` と `t` を入れ替えたものが書ける

浮動小数点数は、`NaN` があるため、全順序ではありません。`double` は、`totally_ordered` を満たすと扱われますが、`NaN` との比較は、意味の約束を破ります。

意味の約束は、コンパイラには確かめられません。型の作者が守ります。

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
  std::println("int と double: {}", std::totally_ordered_with<int, double>);
  std::println("int と long: {}", std::totally_ordered_with<int, long>);
  std::println("string と int: {}", std::totally_ordered_with<std::string, int>);
  std::println("string と const char*: {}", std::totally_ordered_with<std::string, const char*>);
}
```

```text title="実行結果"
int と double: true
int と long: true
string と int: false
string と const char*: true
```

## ゲームでの使いどころ

異なる型の値を、二分探索の探し値に渡せるようにする、アルゴリズムの制約に使います。

## よくあるミス

??? failure "NaN を含む浮動小数点数に使う"
    全順序の約束を破ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`totally_ordered`](totally_ordered.md) | 同じ型どうし |
| [`equality_comparable_with`](equality_comparable_with.md) | 等しさの比較 |
| [`common_with`](common_with.md) | 共通の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::totally_ordered_with](https://cpprefjp.github.io/reference/concepts/totally_ordered_with.html)
- [cppreference: std::totally_ordered_with](https://en.cppreference.com/w/cpp/concepts/totally_ordered_with)
