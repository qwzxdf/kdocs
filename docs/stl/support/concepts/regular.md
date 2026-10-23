---
title: std::regular
summary: "値のように扱える型（コピー・既定構築・比較）を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::regular

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`int` のように、コピーでき、既定初期化でき、比較できる、「値」らしい型を受け付けたい。`std::regular` は、<strong>T が値として扱える型か</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::regular<T>` は、`T` が値のように振る舞う型か
    - `template <std::regular T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::regular {#regular}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept regular = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`semiregular`（コピーと既定初期化）に加えて、`==` で比較できる型が満たします。`int` や `std::string` は満たします。比較演算子を持たない構造体や、コピーできない型は満たしません。

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
  std::println("int                                -> {}", std::regular<int>);
  std::println("std::string                        -> {}", std::regular<std::string>);
  std::println("Player                             -> {}", std::regular<Player>);
  std::println("std::unique_ptr<int>               -> {}", std::regular<std::unique_ptr<int>>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
Player                             -> false
std::unique_ptr<int>               -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::regular T>
void Process(T value) {
  // T は regular を満たす型だけ
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
    - [x] `std::regular<T>` は、`T` が値のように振る舞う型か
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::regular](https://cpprefjp.github.io/reference/concepts/regular.html)
- [cppreference: std::regular](https://en.cppreference.com/w/cpp/concepts/regular)
