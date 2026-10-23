---
title: std::swappable
summary: "`swap` で入れ替えられる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

ソートなどのアルゴリズムは、値の入れ替えを使います。`std::swappable` は、<strong>T の値どうしを入れ替えられるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::swappable<T>` は、`T` の値を入れ替えられるか
    - `template <std::swappable T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::swappable {#swappable}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept swappable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`ranges::swap(a, b)` が書ける型が満たします。ムーブ構築とムーブ代入ができる型は、ふつう満たします。ムーブを削除した型は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

struct Fixed {
  Fixed(Fixed&&) = delete;
  Fixed& operator=(Fixed&&) = delete;
};

int main() {
  std::println("int                                -> {}", std::swappable<int>);
  std::println("std::string                        -> {}", std::swappable<std::string>);
  std::println("Fixed                              -> {}", std::swappable<Fixed>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
Fixed                              -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::swappable T>
void Process(T value) {
  // T は swappable を満たす型だけ
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
    - [x] `std::swappable<T>` は、`T` の値を入れ替えられるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::swappable](https://cpprefjp.github.io/reference/concepts/swappable.html)
- [cppreference: std::swappable](https://en.cppreference.com/w/cpp/concepts/swappable)
