---
title: std::assignable_from
summary: "左辺の型に、右辺の値を代入できることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::assignable_from

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

代入の可否を条件にしたい。`std::assignable_from<LHS, RHS>` は、<strong>LHS に RHS を代入できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::assignable_from<LHS, RHS>` は、`LHS` に `RHS` を代入できるか
    - `template <std::assignable_from T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::assignable_from {#assignable_from}

<span class="ver ver-20">C++20</span>

```cpp
template <class LHS, class RHS>
concept assignable_from = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `LHS` | 型 | 代入される側の型（`T&` で渡す） |
| `RHS` | 型 | 代入する値の型 |

`lhs = rhs` が書けて、その結果が `LHS` への参照で返る型が満たします。`LHS` は左辺値参照（`int&`）で渡します。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  std::println("int&, int                          -> {}", std::assignable_from<int&, int>);
  std::println("int&, const char*                  -> {}", std::assignable_from<int&, const char*>);
  std::println("std::string&, const char*          -> {}", std::assignable_from<std::string&, const char*>);
}
```

```text title="実行結果"
int&, int                          -> true
int&, const char*                  -> false
std::string&, const char*          -> true
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::assignable_from T>
void Process(T value) {
  // T は assignable_from を満たす型だけ
}
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
    - [x] `std::assignable_from<LHS, RHS>` は、`LHS` に `RHS` を代入できるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::assignable_from](https://cpprefjp.github.io/reference/concepts/assignable_from.html)
- [cppreference: std::assignable_from](https://en.cppreference.com/w/cpp/concepts/assignable_from)
