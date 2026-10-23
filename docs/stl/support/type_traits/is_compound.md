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
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_compound<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

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

`is_fundamental` が `false` の型は、すべて `true` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

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

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_compound_v<T>) {
    // T が条件に当てはまる型のときの処理
  } else {
    // それ以外の型の処理
  }
}
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_compound_v<T>` は、`T` が基本型でない型（配列、関数、ポインタ、参照、クラス、共用体、列挙型、メンバーポインタ）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_compound](https://cpprefjp.github.io/reference/type_traits/is_compound.html)
- [cppreference: std::is_compound](https://en.cppreference.com/w/cpp/types/is_compound)
