---
title: std::copy_constructible
summary: "コピーして構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

コンテナに保存して、値のコピーを取る関数のために、コピーできる型だけを受け付けたい。`std::copy_constructible` は、<strong>T がコピーでき、ムーブでき、破棄できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::copy_constructible<T>` は、`T` がコピー構築できるか
    - `template <std::copy_constructible T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::copy_constructible {#copy_constructible}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept copy_constructible = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`T(const T&)` で構築できる型で、ムーブ構築と破棄もできる型が満たします。`std::unique_ptr` のようなコピー不可の型は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <memory>
#include <print>
#include <string>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::copy_constructible<Player>);
  std::println("std::string                        -> {}", std::copy_constructible<std::string>);
  std::println("std::unique_ptr<int>               -> {}", std::copy_constructible<std::unique_ptr<int>>);
}
```

```text title="実行結果"
Player                             -> true
std::string                        -> true
std::unique_ptr<int>               -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::copy_constructible T>
void Process(T value) {
  // T は copy_constructible を満たす型だけ
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
    - [x] `std::copy_constructible<T>` は、`T` がコピー構築できるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::copy_constructible](https://cpprefjp.github.io/reference/concepts/copy_constructible.html)
- [cppreference: std::copy_constructible](https://en.cppreference.com/w/cpp/concepts/copy_constructible)
