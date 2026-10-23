---
title: std::compare_three_way_result
summary: "`<=>` の戻り値の型を求める。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_three_way_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`a <=> b` の結果の型は、`int` なら `strong_ordering`、`double` なら `partial_ordering` と、型によって違います。その型を、テンプレートの中で取り出したいときに使うのが `std::compare_three_way_result` です。

!!! tip "ポイント"
    - `std::compare_three_way_result_t<T>` は `T <=> T` の結果の型
    - `int` は `strong_ordering`、`double` は `partial_ordering`
    - `<=>` が使えない型には、型が存在しない
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::compare_three_way_result_t {#compare_three_way_result}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U = T>
using compare_three_way_result_t = typename compare_three_way_result<T, U>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 1 つ目の型 |
| `U` | 型 | 2 つ目の型。既定は `T` |

`T` と `U` の三方比較（`<=>`）の結果の型を返します。`<=>` が使えない型には、結果の型がありません。

自作のテンプレートで、戻り値の型を決めるときに使います。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <type_traits>

int main() {
  using IntResult = std::compare_three_way_result_t<int>;
  using DoubleResult = std::compare_three_way_result_t<double>;
  std::println("int は strong_ordering    : {}", std::is_same_v<IntResult, std::strong_ordering>);
  std::println("double は partial_ordering: {}", std::is_same_v<DoubleResult, std::partial_ordering>);
}
```

```text title="実行結果"
int は strong_ordering    : true
double は partial_ordering: true
```

## ゲームでの使いどころ

比較関数のテンプレートで、戻り値の型を決めます。

```cpp
template <class T>
std::compare_three_way_result_t<T> Compare(const T& a, const T& b) { return a <=> b; }
```

## よくあるミス

??? failure "`<=>` を持たない型に使う"
    `three_way_comparable` で先に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_three_way`](compare_three_way.md) | `<=>` の関数オブジェクト |
| [`common_comparison_category`](common_comparison_category.md) | 共通の順序型 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `compare_three_way_result_t<T>` は `<=>` の結果の型
    - [x] 型ごとに違う
    - [x] `<=>` がなければ型がない

## 関連ページ

- [cpprefjp: std::compare_three_way_result](https://cpprefjp.github.io/reference/compare/compare_three_way_result.html)
- [cppreference: std::compare_three_way_result](https://en.cppreference.com/w/cpp/utility/compare_three_way_result)
