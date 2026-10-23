---
title: std::swappable_with
summary: "2 つの型の値を、たがいに `swap` できることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::swappable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

型の違う 2 つの値を入れ替えられるかを要求したい。`std::swappable_with<T, U>` は、<strong>T と U の値を入れ替えられるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::swappable_with<T, U>` は、`T` と `U` の値を入れ替えられるか
    - `template <std::swappable_with T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::swappable_with {#swappable_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
concept swappable_with = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 1 つ目の型（`T&` で渡す） |
| `U` | 型 | 2 つ目の型（`U&` で渡す） |

`ranges::swap(t, u)` と `ranges::swap(u, t)` が書ければ満たします。`T` と `U` は参照（`int&`）で渡すのが普通です。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  std::println("int&, int&                         -> {}", std::swappable_with<int&, int&>);
  std::println("int&, float&                       -> {}", std::swappable_with<int&, float&>);
  std::println("std::string&, std::string&         -> {}", std::swappable_with<std::string&, std::string&>);
}
```

```text title="実行結果"
int&, int&                         -> true
int&, float&                       -> false
std::string&, std::string&         -> true
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::swappable_with T>
void Process(T value) {
  // T は swappable_with を満たす型だけ
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
    - [x] `std::swappable_with<T, U>` は、`T` と `U` の値を入れ替えられるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::swappable_with](https://cpprefjp.github.io/reference/concepts/swappable_with.html)
- [cppreference: std::swappable_with](https://en.cppreference.com/w/cpp/concepts/swappable_with)
