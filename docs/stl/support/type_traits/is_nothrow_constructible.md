---
title: std::is_nothrow_constructible
summary: "指定した引数で、例外を投げずに構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

特定の引数で構築する処理が例外を投げないと保証できるかを知りたい。`std::is_nothrow_constructible<T, Args...>` は、<strong>構築が `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_constructible_v<T, Args...>` は、`T` を `Args...` から構築するとき例外を投げないか
    - `Args...` の並びごとに結果が変わる
    - `std::is_nothrow_constructible<T, Args...>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - メモリを確保する型は、ふつう `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_constructible_v {#is_nothrow_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class... Args>
inline constexpr bool is_nothrow_constructible_v = is_nothrow_constructible<T, Args...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 構築する型 |
| `Args...` | 型の並び | 構築に渡す引数の型 |

`T(args...)` を作る式が `noexcept` と宣言されていれば `true` です。数値だけを持つ構造体は `true`、メモリを確保する型（`std::string` を文字列リテラルから作る場合など）は `false` です。

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
  std::println("Player                             -> {}", std::is_nothrow_constructible_v<Player>);
  std::println("int, int                           -> {}", std::is_nothrow_constructible_v<int, int>);
  std::println("std::string, const char*           -> {}", std::is_nothrow_constructible_v<std::string, const char*>);
}
```

```text title="実行結果"
Player                             -> true
int, int                           -> true
std::string, const char*           -> false
```

## ゲームでの使いどころ

要素を作って持つ入れ物で、中の型の構築が例外を投げないときだけ、入れ物のコンストラクターを `noexcept` にします。

```cpp
template <class T>
struct Slot {
  template <class... Args>
  explicit Slot(Args&&... args) noexcept(std::is_nothrow_constructible_v<T, Args...>)
      : value(std::forward<Args>(args)...) {}

  T value;
};
```

## よくあるミス

??? failure "メモリを確保する型で true を期待する"
    `std::string` を文字列リテラルから作ると、確保で `std::bad_alloc` を投げうるので `false` です。

??? failure "引数の型の並びを省略する"
    引数つきの構築は `Args...` を渡さないと、別の組み合わせを調べてしまいます。引数なしだけなら `is_nothrow_default_constructible` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_constructible`](is_constructible.md) | 例外を考えずに、作れるかだけを調べる |
| [`is_nothrow_default_constructible`](is_nothrow_default_constructible.md) | 引数なしに絞った版 |
| [`is_nothrow_copy_constructible`](is_nothrow_copy_constructible.md) | コピー構築に絞った版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_constructible_v<T, Args...>` は、`T` を `Args...` から構築するとき例外を投げないか
    - [x] 構築の式に `noexcept` が付いているかを調べる
    - [x] 入れ物の `noexcept` を、中の型に合わせる

## 関連ページ

- [cpprefjp: std::is_nothrow_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_constructible.html)
- [cppreference: std::is_nothrow_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_constructible)
