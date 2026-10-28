---
title: std::move_constructible
summary: "ムーブして構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::move_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

一時オブジェクトや、所有権を渡す関数の引数にムーブできる型だけを受け付けたい。`std::move_constructible` は、<strong>T がムーブ構築でき、破棄できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::move_constructible<T>` は、`T` がムーブ構築できるか
    - `template <std::move_constructible T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::move_constructible {#move_constructible}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept move_constructible = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`T(T&&)` で構築できる（コピーでの代用を含む）型が満たします。ムーブ構築が削除された型は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <memory>
#include <print>

struct Player {
  int hp;
  float x;
};
struct Fixed {
  Fixed(Fixed&&) = delete;
  Fixed& operator=(Fixed&&) = delete;
};

int main() {
  std::println("Player                             -> {}", std::move_constructible<Player>);
  std::println("std::unique_ptr<int>               -> {}", std::move_constructible<std::unique_ptr<int>>);
  std::println("Fixed                              -> {}", std::move_constructible<Fixed>);
}
```

```text title="実行結果"
Player                             -> true
std::unique_ptr<int>               -> true
Fixed                              -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::move_constructible T>
void Process(T value) {
  // T は move_constructible を満たす型だけ
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
    - [x] `std::move_constructible<T>` は、`T` がムーブ構築できるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::move_constructible](https://cpprefjp.github.io/reference/concepts/move_constructible.html)
- [cppreference: std::move_constructible](https://en.cppreference.com/w/cpp/concepts/move_constructible)
