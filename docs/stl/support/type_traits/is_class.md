---
title: std::is_class
summary: "型がクラス（struct を含む）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_class

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

構造体やクラスだけを受け取るテンプレートを書きたい。`std::is_class` は、<strong>型が `struct` または `class` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_class_v<T>` は、`T` が `struct` か `class`（共用体を除く）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_class<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_class_v {#is_class}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_class_v = is_class<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`struct` と `class` の型なら `true` です。共用体と列挙型は `false` です。ポインタや参照は、指す先の型にかかわらず `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
enum class Color { kRed, kBlue };
union Number {
  int i;
  float f;
};

int main() {
  std::println("Player                     -> {}", std::is_class_v<Player>);
  std::println("Color                      -> {}", std::is_class_v<Color>);
  std::println("Number                     -> {}", std::is_class_v<Number>);
  std::println("int                        -> {}", std::is_class_v<int>);
}
```

```text title="実行結果"
Player                     -> true
Color                      -> false
Number                     -> false
int                        -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_class_v<T>) {
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
    - [x] `std::is_class_v<T>` は、`T` が `struct` か `class`（共用体を除く）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_class](https://cpprefjp.github.io/reference/type_traits/is_class.html)
- [cppreference: std::is_class](https://en.cppreference.com/w/cpp/types/is_class)
