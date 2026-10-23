---
title: std::is_constructible
summary: "指定した引数で構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

特定の引数で構築できる型かを、事前に調べたい。たとえば、`emplace_back` に渡す引数で構築できるかを確かめます。`std::is_constructible<T, Args...>` は、<strong>T を Args... から構築できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_constructible_v<T, Args...>` は、`T` を `Args...` から構築できるか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_constructible<T, Args...>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_constructible_v {#is_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class... Args>
inline constexpr bool is_constructible_v = is_constructible<T, Args...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 構築する型 |
| `Args...` | 型の並び | 構築に渡す引数の型 |

`T(args...)` と書ける組み合わせなら `true` です。引数なしの `<T>` は既定構築、`<T, const T&>` はコピー構築の可否になります。`explicit` なコンストラクターでも、明示的な構築なら `true` です（`is_convertible` との違い）。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

`is_default_constructible`、`is_copy_constructible`、`is_move_constructible` は、この特殊なケースです。

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
  std::println("Player                             -> {}", std::is_constructible_v<Player>);
  std::println("Player, const Player&              -> {}", std::is_constructible_v<Player, const Player&>);
  std::println("std::string, const char*           -> {}", std::is_constructible_v<std::string, const char*>);
  std::println("std::string, int*                  -> {}", std::is_constructible_v<std::string, int*>);
}
```

```text title="実行結果"
Player                             -> true
Player, const Player&              -> true
std::string, const char*           -> true
std::string, int*                  -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_constructible_v<T>) {
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
    - [x] `std::is_constructible_v<T, Args...>` は、`T` を `Args...` から構築できるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_constructible](https://cpprefjp.github.io/reference/type_traits/is_constructible.html)
- [cppreference: std::is_constructible](https://en.cppreference.com/w/cpp/types/is_constructible)
