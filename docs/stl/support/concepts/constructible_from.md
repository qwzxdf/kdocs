---
title: std::constructible_from
summary: "指定した引数から構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::constructible_from

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

ファクトリー関数で、特定の引数で構築できる型だけを受け付けたい。`std::constructible_from<T, Args...>` は、<strong>T を Args... から構築できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::constructible_from<T, Args...>` は、`T` が `Args...` から構築できるか
    - `template <std::constructible_from T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::constructible_from {#constructible_from}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class... Args>
concept constructible_from = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 構築する型 |
| `Args...` | 型の並び | 構築に渡す引数の型 |

`T(args...)` と書けて、デストラクターも使える型なら満たします。`std::is_constructible` に、`destructible` の条件を足したものです。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  std::println("std::string, const char*           -> {}", std::constructible_from<std::string, const char*>);
  std::println("std::string, int*                  -> {}", std::constructible_from<std::string, int*>);
  std::println("int, int                           -> {}", std::constructible_from<int, int>);
}
```

```text title="実行結果"
std::string, const char*           -> true
std::string, int*                  -> false
int, int                           -> true
```

## ゲームでの使いどころ

`make` 系の関数の引数を制限します。

```cpp
template <class T, class... Args>
  requires std::constructible_from<T, Args...>
T Create(Args&&... args) { return T(std::forward<Args>(args)...); }
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_constructible`](../type_traits/is_constructible.md) | 型特性版 |
| [`default_initializable`](default_initializable.md) | 既定構築できるか |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::constructible_from<T, Args...>` は、`T` が `Args...` から構築できるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::constructible_from](https://cpprefjp.github.io/reference/concepts/constructible_from.html)
- [cppreference: std::constructible_from](https://en.cppreference.com/w/cpp/concepts/constructible_from)
