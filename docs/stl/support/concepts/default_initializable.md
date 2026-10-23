---
title: std::default_initializable
summary: "引数なしで作れる型であることを要求するコンセプト。"
order: 11
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::default_initializable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

配列や `std::vector<T>(n)` は、引数なしで初期化できる型を要求します。`std::default_initializable` は、<strong>T が引数なしで初期化できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::default_initializable<T>` は、`T` が既定の初期化ができるか
    - `template <std::default_initializable T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::default_initializable {#default_initializable}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept default_initializable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`T{}`、`T()`、`T t;` のいずれも書ける型が満たします。引数が必須のコンストラクターだけを持つ型は満たしません。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

struct NoDefault {
  explicit NoDefault(int) {}
};

int main() {
  std::println("int                                -> {}", std::default_initializable<int>);
  std::println("std::string                        -> {}", std::default_initializable<std::string>);
  std::println("NoDefault                          -> {}", std::default_initializable<NoDefault>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
NoDefault                          -> false
```

## ゲームでの使いどころ

配列やバッファを `T` で確保する関数に使います。

```cpp
template <std::default_initializable T>
std::vector<T> MakeBuffer(std::size_t n) { return std::vector<T>(n); }
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
    - [x] `std::default_initializable<T>` は、`T` が既定の初期化ができるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::default_initializable](https://cpprefjp.github.io/reference/concepts/default_initializable.html)
- [cppreference: std::default_initializable](https://en.cppreference.com/w/cpp/concepts/default_initializable)
