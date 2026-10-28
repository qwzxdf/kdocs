---
title: std::conditional
summary: "条件によって、2 つの型のどちらかを選ぶ。"
order: 17
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::conditional

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

条件によって、型を切り替えたい。たとえば、サイズが小さければ値渡し、大きければ参照渡しにしたい。`std::conditional` は、<strong>条件が真なら 1 つ目の型、偽なら 2 つ目の型</strong>を返します。型に対する三項演算子のようなものです。

!!! tip "ポイント"
    - `std::conditional_t<B, X, Y>`: `B` が真なら `X`、偽なら `Y`
    - 条件 `B` は、コンパイル時の `bool` の定数
    - 結果は型。値ではない
    - `if constexpr` と併用して、型と処理の両方を切り替える

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::conditional_t {#conditional}

<span class="ver ver-11">C++11</span>

```cpp
template <bool B, class T, class F>
using conditional_t = typename conditional<B, T, F>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B` | `bool` | 条件（コンパイル時の定数） |
| `T` | 型 | `B` が真のときの型 |
| `F` | 型 | `B` が偽のときの型 |

`conditional_t<B, T, F>` は `B` が `true` なら `T`、`false` なら `F` です。どちらの型も、使われないほうも含めて、有効な型でなければなりません。

用途は、パラメーターの渡し方の切り替えです。小さな型（`int`、`float`）は値渡し、大きな型は `const&` で渡すのが速いので、`conditional_t<(sizeof(T) <= 16), T, const T&>` のように書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

// 小さい型は値、大きい型は const 参照で受ける型
template <class T>
using Param = std::conditional_t<(sizeof(T) <= 16), T, const T&>;

struct Big {
  char data[100];
};

int main() {
  std::println("int は値渡し     : {}", std::is_same_v<Param<int>, int>);
  std::println("Big は参照渡し   : {}", std::is_same_v<Param<Big>, const Big&>);
  std::println("true なら int    : {}", std::is_same_v<std::conditional_t<true, int, float>, int>);
}
```

```text title="実行結果"
int は値渡し     : true
Big は参照渡し   : true
true なら int    : true
```

## ゲームでの使いどころ

引数の渡し方を型の大きさで自動的に切り替えます（上のコード）。

また、コンテナのインデックスの型を要素数に応じて `uint8_t` か `uint16_t` に切り替える、といった使い方もあります。

## よくあるミス

??? failure "条件に実行時の値を使う"
    条件はコンパイル時の定数でなければなりません。

??? failure "使われないほうの型が不正で、コンパイルエラーになる"
    両方の型が有効である必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`enable_if`](enable_if.md) | 条件が偽のとき、型を存在させない |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `conditional_t<B, X, Y>` は条件で型を選ぶ
    - [x] 条件はコンパイル時の定数
    - [x] 型の大きさで引数の渡し方を切り替えられる

## 関連ページ

- [cpprefjp: std::conditional](https://cpprefjp.github.io/reference/type_traits/conditional.html)
- [cppreference: std::conditional](https://en.cppreference.com/w/cpp/types/conditional)
