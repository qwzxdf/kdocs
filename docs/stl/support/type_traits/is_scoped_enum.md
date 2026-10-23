---
title: std::is_scoped_enum
summary: "型がスコープ付き列挙型（`enum class`）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_scoped_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <type_traits>`
</div>

`enum` と `enum class` は、整数への暗黙の変換ができるかが違います。`std::is_scoped_enum` は、<strong>型が `enum class` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_scoped_enum_v<T>` は、`T` が `enum class`（スコープ付き列挙型）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_scoped_enum<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_scoped_enum_v {#is_scoped_enum}

<span class="ver ver-23">C++23</span>

```cpp
template <class T>
inline constexpr bool is_scoped_enum_v = is_scoped_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`enum class Color` は `true`、旧式の `enum` は `false`、整数型も `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class Color { kRed, kBlue };
enum Old { kOne };

int main() {
  std::println("Color                      -> {}", std::is_scoped_enum_v<Color>);
  std::println("Old                        -> {}", std::is_scoped_enum_v<Old>);
  std::println("int                        -> {}", std::is_scoped_enum_v<int>);
}
```

```text title="実行結果"
Color                      -> true
Old                        -> false
int                        -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_scoped_enum_v<T>) {
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

C++23 から使えます。新しい規格の機能なので、コンパイラの対応状況を確かめてください。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_scoped_enum_v<T>` は、`T` が `enum class`（スコープ付き列挙型）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_scoped_enum](https://cpprefjp.github.io/reference/type_traits/is_scoped_enum.html)
- [cppreference: std::is_scoped_enum](https://en.cppreference.com/w/cpp/types/is_scoped_enum)
