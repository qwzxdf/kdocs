---
title: std::is_move_assignable
summary: "ムーブ代入できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_move_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`a = std::move(b)` が書ける型かを調べたい。`std::is_move_assignable` は、<strong>型がムーブ代入できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_move_assignable_v<T>` は、`T` がムーブ代入できるか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_move_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_move_assignable_v {#is_move_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_move_assignable_v = is_move_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブ代入演算子が使える（または、コピー代入で代用できる）型は `true` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                     -> {}", std::is_move_assignable_v<Player>);
  std::println("std::unique_ptr<int>       -> {}", std::is_move_assignable_v<std::unique_ptr<int>>);
  std::println("const Player               -> {}", std::is_move_assignable_v<const Player>);
}
```

```text title="実行結果"
Player                     -> true
std::unique_ptr<int>       -> true
const Player               -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_move_assignable_v<T>) {
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
    - [x] `std::is_move_assignable_v<T>` は、`T` がムーブ代入できるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_move_assignable](https://cpprefjp.github.io/reference/type_traits/is_move_assignable.html)
- [cppreference: std::is_move_assignable](https://en.cppreference.com/w/cpp/types/is_move_assignable)
