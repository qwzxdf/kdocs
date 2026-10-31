---
title: std::is_rvalue_reference
summary: "型が右辺値参照かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_rvalue_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

一時オブジェクトを受け取ったかを区別したい。`std::is_rvalue_reference` は、<strong>型が右辺値参照か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_rvalue_reference_v<T>` は、`T` が右辺値参照（`T&&`）か
    - 万能参照の `T` が `X&` のときは、右辺値参照ではない
    - `std::is_rvalue_reference<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `std::move` の戻り値の型が右辺値参照

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_rvalue_reference_v {#is_rvalue_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_rvalue_reference_v = is_rvalue_reference<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int&&` のような右辺値参照型が `true` です。左辺値参照（`int&`）と参照でない型は `false` です。注意したいのは、テンプレートの `T&&`（万能参照）で、`T` が `X&` と推論されたときは、`X&` になり、右辺値参照ではありません。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int&&                      -> {}", std::is_rvalue_reference_v<int&&>);
  std::println("int&                       -> {}", std::is_rvalue_reference_v<int&>);
  std::println("int                        -> {}", std::is_rvalue_reference_v<int>);
}
```

```text title="実行結果"
int&&                      -> true
int&                       -> false
int                        -> false
```

## ゲームでの使いどころ

式の型から、右辺値参照かどうかを確かめます。`std::move` の結果は右辺値参照、括弧つきの名前は左辺値参照です。

```cpp
Item item;

static_assert(std::is_rvalue_reference_v<decltype(std::move(item))>);   // move は右辺値参照を返す
static_assert(!std::is_rvalue_reference_v<decltype(item)>);             // 変数の型は Item
static_assert(std::is_lvalue_reference_v<decltype((item))>);           // 括弧つきの名前は左辺値参照
```

## よくあるミス

??? failure "T&& の引数が常に右辺値参照だと思う"
    `T` が推論されるテンプレートでは、`T&&` は左辺値参照にもなります（`T = X&` のとき `X&`）。

??? failure "名前のついた右辺値参照変数を右辺値だと思う"
    `Item&& r` と宣言した `r` は、式としては左辺値です。`std::move(r)` で右辺値に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_lvalue_reference`](is_lvalue_reference.md) | 左辺値参照か |
| [`is_reference`](is_reference.md) | どちらの参照か |
| [`remove_reference`](remove_reference.md) | 参照を外した型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_rvalue_reference_v<T>` は、`T` が右辺値参照（`T&&`）か
    - [x] `X&&` が `true`
    - [x] 万能参照では、`T` を調べて区別する

## 関連ページ

- [cpprefjp: std::is_rvalue_reference](https://cpprefjp.github.io/reference/type_traits/is_rvalue_reference.html)
- [cppreference: std::is_rvalue_reference](https://en.cppreference.com/w/cpp/types/is_rvalue_reference)
