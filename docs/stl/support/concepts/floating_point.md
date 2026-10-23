---
title: std::floating_point
summary: "小数型であることを要求するコンセプト。"
order: 3
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::floating_point

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

小数だけを受け取るテンプレートを書きたい。`std::floating_point` は、<strong>型が浮動小数点型か</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::floating_point<T>` は、`T` が浮動小数点型か
    - `template <std::floating_point T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::floating_point {#floating_point}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept floating_point = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`float`、`double`、`long double` が条件を満たします。整数型や、ポインタは満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("float                              -> {}", std::floating_point<float>);
  std::println("double                             -> {}", std::floating_point<double>);
  std::println("int                                -> {}", std::floating_point<int>);
}
```

```text title="実行結果"
float                              -> true
double                             -> true
int                                -> false
```

## ゲームでの使いどころ

線形補間のように、小数だけで意味のある関数に使います。

```cpp
template <std::floating_point T>
T Lerp(T a, T b, T t) { return a + (b - a) * t; }
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`same_as`](same_as.md) | 2 つの型が同じ |
| [`integral`](integral.md) | 整数型 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::floating_point<T>` は、`T` が浮動小数点型か
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::floating_point](https://cpprefjp.github.io/reference/concepts/floating_point.html)
- [cppreference: std::floating_point](https://en.cppreference.com/w/cpp/concepts/floating_point)
