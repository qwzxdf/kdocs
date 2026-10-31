---
title: std::is_compound
summary: "型が複合型（基本型以外）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_compound

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

基本型の反対側です。`std::is_compound` は、<strong>型が複合型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_compound_v<T>` は、`T` が基本型でない型（配列、関数、ポインタ、参照、クラス、共用体、列挙型、メンバーポインタ）か
    - `is_fundamental_v<T>` と必ず逆の値になる
    - `std::is_compound<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 参照やポインターも複合型

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_compound_v {#is_compound}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_compound_v = is_compound<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

基本型（算術型・`void`・`nullptr_t`）以外のすべてが `true` です。配列、関数、ポインター、参照、クラス、共用体、列挙型、メンバーへのポインターが含まれます。`is_fundamental` の裏返しです。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                     -> {}", std::is_compound_v<Player>);
  std::println("int*                       -> {}", std::is_compound_v<int*>);
  std::println("int                        -> {}", std::is_compound_v<int>);
  std::println("void                       -> {}", std::is_compound_v<void>);
}
```

```text title="実行結果"
Player                     -> true
int*                       -> true
int                        -> false
void                       -> false
```

## ゲームでの使いどころ

基本型は値渡し、それ以外は参照渡しにする、引数の型の選択に使えます。

```cpp
template <class T>
using Param = std::conditional_t<std::is_compound_v<T>, const T&, T>;

template <class T>
void Show(Param<T> value);   // int は値渡し、std::string は const 参照
```

## よくあるミス

??? failure "nullptr_t を複合型だと思う"
    `std::nullptr_t` は基本型なので `false` です。

??? failure "is_fundamental と同時に true になると思う"
    2 つは、必ず逆の値になります（どちらかが `true`）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_fundamental`](is_fundamental.md) | 基本型か。`is_compound` の裏返し |
| [`is_scalar`](is_scalar.md) | 算術型・列挙型・ポインターなどか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_compound_v<T>` は、`T` が基本型でない型（配列、関数、ポインタ、参照、クラス、共用体、列挙型、メンバーポインタ）か
    - [x] 基本型以外のすべてが `true`
    - [x] `is_fundamental` と必ず逆の値になる

## 関連ページ

- [cpprefjp: std::is_compound](https://cpprefjp.github.io/reference/type_traits/is_compound.html)
- [cppreference: std::is_compound](https://en.cppreference.com/w/cpp/types/is_compound)
