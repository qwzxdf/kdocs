---
title: std::movable
summary: "ムーブできる型であることを要求するコンセプト。"
order: 10
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::movable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

値のように扱えるが、コピーは要らない型を受け付けたい。`std::movable` は、<strong>T がムーブ構築・ムーブ代入・swap できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::movable<T>` は、`T` がムーブでき、入れ替えられるか
    - `template <std::movable T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::movable {#movable}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept movable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

オブジェクトとして、ムーブ構築、ムーブ代入、`swap` ができる型が満たします。`std::unique_ptr` や `std::vector` は満たします。ムーブを削除した型は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <memory>
#include <print>

struct Fixed {
  Fixed(Fixed&&) = delete;
  Fixed& operator=(Fixed&&) = delete;
};

int main() {
  std::println("int                                -> {}", std::movable<int>);
  std::println("std::unique_ptr<int>               -> {}", std::movable<std::unique_ptr<int>>);
  std::println("Fixed                              -> {}", std::movable<Fixed>);
}
```

```text title="実行結果"
int                                -> true
std::unique_ptr<int>               -> true
Fixed                              -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::movable T>
void Process(T value) {
  // T は movable を満たす型だけ
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
    - [x] `std::movable<T>` は、`T` がムーブでき、入れ替えられるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::movable](https://cpprefjp.github.io/reference/concepts/movable.html)
- [cppreference: std::movable](https://en.cppreference.com/w/cpp/concepts/movable)
