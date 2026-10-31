---
title: std::is_reference
summary: "型が参照（左辺値でも右辺値でも）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

値で受け取るか、参照で受け取るかによって、コピーの有無が変わります。`std::is_reference` は、<strong>型が参照か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_reference_v<T>` は、`T` が参照型（左辺値参照または右辺値参照）か
    - 左辺値参照と右辺値参照のどちらも `true`
    - `std::is_reference<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `reference_wrapper` は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_reference_v {#is_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_reference_v = is_reference<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int&`（左辺値参照）と `int&&`（右辺値参照）のどちらも `true` です。ポインターは参照ではないので `false` です。`std::reference_wrapper<int>` は、クラスなので `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int&                       -> {}", std::is_reference_v<int&>);
  std::println("int&&                      -> {}", std::is_reference_v<int&&>);
  std::println("int                        -> {}", std::is_reference_v<int>);
  std::println("int*                       -> {}", std::is_reference_v<int*>);
}
```

```text title="実行結果"
int&                       -> true
int&&                      -> true
int                        -> false
int*                       -> false
```

## ゲームでの使いどころ

テンプレートで保存する型を決めるとき、参照はそのまま持てないので、`reference_wrapper` に変えます。

```cpp
template <class T>
using Stored = std::conditional_t<std::is_reference_v<T>,
                                  std::reference_wrapper<std::remove_reference_t<T>>,
                                  T>;

// Stored<int&>  は std::reference_wrapper<int>
// Stored<int>   は int
```

## よくあるミス

??? failure "reference_wrapper が true になると思う"
    `std::reference_wrapper` は、参照を包んだクラスなので `false` です。

??? failure "ポインターを参照と混同する"
    `int*` は `false` です。ポインターは `is_pointer` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_lvalue_reference`](is_lvalue_reference.md) | 左辺値参照か |
| [`is_rvalue_reference`](is_rvalue_reference.md) | 右辺値参照か |
| [`remove_reference`](remove_reference.md) | 参照を外した型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_reference_v<T>` は、`T` が参照型（左辺値参照または右辺値参照）か
    - [x] `T&` と `T&&` が `true`
    - [x] 参照を外すのは `remove_reference_t`

## 関連ページ

- [cpprefjp: std::is_reference](https://cpprefjp.github.io/reference/type_traits/is_reference.html)
- [cppreference: std::is_reference](https://en.cppreference.com/w/cpp/types/is_reference)
