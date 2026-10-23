---
title: std::is_nothrow_move_constructible
summary: "ムーブが例外を投げない型かを調べる。"
order: 12
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::vector` は、要素を新しい領域に移すとき、ムーブ構築が `noexcept` ならムーブし、そうでなければ安全のためコピーします。`std::is_nothrow_move_constructible` は、<strong>ムーブ構築が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_move_constructible_v<T>` は、`T` のムーブ構築が例外を投げないか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_nothrow_move_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_move_constructible_v {#is_nothrow_move_constructible}

```cpp
template <class T>
inline constexpr bool is_nothrow_move_constructible_v = is_nothrow_move_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブコンストラクターが `noexcept` なら `true` です。`noexcept` を付け忘れると、`vector` の拡張が遅いコピーになります。ゲームの型では、ムーブコンストラクターに必ず `noexcept` を付けます。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct MayThrow {
  MayThrow() = default;
  MayThrow(MayThrow&&) noexcept(false) {}
};

int main() {
  std::println("Player                     -> {}", std::is_nothrow_move_constructible_v<Player>);
  std::println("std::string                -> {}", std::is_nothrow_move_constructible_v<std::string>);
  std::println("MayThrow                   -> {}", std::is_nothrow_move_constructible_v<MayThrow>);
}
```

```text title="実行結果"
Player                     -> true
std::string                -> true
MayThrow                   -> false
```

## ゲームでの使いどころ

自作の型のムーブコンストラクターが `noexcept` であることを保証します。

```cpp
static_assert(std::is_nothrow_move_constructible_v<Enemy>, "Enemy のムーブに noexcept を付けてください");
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
    - [x] `std::is_nothrow_move_constructible_v<T>` は、`T` のムーブ構築が例外を投げないか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_nothrow_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_move_constructible.html)
- [cppreference: std::is_nothrow_move_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_move_constructible)
