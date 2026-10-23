---
title: std::is_trivially_assignable
summary: "代入が自明（メモリのコピーだけ）な型の組かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

代入が、ビットの複製だけで済むかを知りたい。`std::is_trivially_assignable<T, U>` は、<strong>T への U の代入が自明か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_assignable_v<T, U>` は、`T` に `U` を自明に代入できるか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_trivially_assignable<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_assignable_v {#is_trivially_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
inline constexpr bool is_trivially_assignable_v = is_trivially_assignable<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 代入される側の型（`T&` で渡す） |
| `U` | 型 | 代入する値の型 |

`declval<T>() = declval<U>()` が自明な処理で済むなら `true` です。第 1 引数は代入される側の型で、左辺値参照 `T&` を渡します。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

第 1 引数に `Player`（参照なし）を渡すと、右辺値への代入になり、別の結果になります。通常は `T&` を渡します。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player&, const Player&             -> {}", std::is_trivially_assignable_v<Player&, const Player&>);
  std::println("std::string&, const std::string&   -> {}", std::is_trivially_assignable_v<std::string&, const std::string&>);
  std::println("int&, int                          -> {}", std::is_trivially_assignable_v<int&, int>);
}
```

```text title="実行結果"
Player&, const Player&             -> true
std::string&, const std::string&   -> false
int&, int                          -> true
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_trivially_assignable_v<T>) {
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
    - [x] `std::is_trivially_assignable_v<T, U>` は、`T` に `U` を自明に代入できるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_trivially_assignable](https://cpprefjp.github.io/reference/type_traits/is_trivially_assignable.html)
- [cppreference: std::is_trivially_assignable](https://en.cppreference.com/w/cpp/types/is_trivially_assignable)
