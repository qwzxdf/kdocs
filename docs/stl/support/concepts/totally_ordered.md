---
title: std::totally_ordered
summary: "`<`、`>`、`==` などで大小を比べられることを要求するコンセプト。"
order: 8
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::totally_ordered

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

並べ替えや範囲の判定のために、大小を比べられる型だけを受け付けたい。`std::totally_ordered` は、<strong>T が大小も含めて比べられるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::totally_ordered<T>` は、`T` が `<` `>` `<=` `>=` と `==` で比べられるか
    - `template <std::totally_ordered T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::totally_ordered {#totally_ordered}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept totally_ordered = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`==`、`!=`、`<`、`>`、`<=`、`>=` のすべてが書ける型が満たします。`int` や `std::string` は満たします。比較演算子を持たない構造体は満たしません。

C++20 の `operator<=>` を定義しておくと、すべての比較演算子が自動で揃い、この条件を満たします。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                                -> {}", std::totally_ordered<int>);
  std::println("std::string                        -> {}", std::totally_ordered<std::string>);
  std::println("Player                             -> {}", std::totally_ordered<Player>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
Player                             -> false
```

## ゲームでの使いどころ

最大値や並べ替えの関数に使います。

```cpp
template <std::totally_ordered T>
T Clamp(T v, T lo, T hi) { return v < lo ? lo : (v > hi ? hi : v); }
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
    - [x] `std::totally_ordered<T>` は、`T` が `<` `>` `<=` `>=` と `==` で比べられるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::totally_ordered](https://cpprefjp.github.io/reference/concepts/totally_ordered.html)
- [cppreference: std::totally_ordered](https://en.cppreference.com/w/cpp/concepts/totally_ordered)
