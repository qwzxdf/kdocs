---
title: std::is_nothrow_default_constructible
summary: "例外を投げずに既定構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_default_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

コンテナの拡張や初期化で、例外が起きないと保証できるかを知りたい。`std::is_nothrow_default_constructible` は、<strong>型の既定構築が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_default_constructible_v<T>` は、`T` の既定構築が例外を投げないか
    - 数値だけの構造体は `true`
    - `std::is_nothrow_default_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= default` はメンバー次第

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_default_constructible_v {#is_nothrow_default_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_default_constructible_v = is_nothrow_default_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

引数なしの構築（`T()`）が `noexcept` と宣言されていれば `true` です。メンバーが数値だけの構造体は `true` です。コンストラクターの中でメモリを確保する型は、`noexcept` を付けない限り `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Slow {
  Slow() noexcept(false) {}
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::is_nothrow_default_constructible_v<Player>);
  std::println("int                                -> {}", std::is_nothrow_default_constructible_v<int>);
  std::println("Slow                               -> {}", std::is_nothrow_default_constructible_v<Slow>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
Slow                               -> false
```

## ゲームでの使いどころ

要素を 1 つ包む型の、引数なしのコンストラクターの `noexcept` を、要素の型に合わせます。

```cpp
template <class T>
struct Cell {
  T value;
  Cell() noexcept(std::is_nothrow_default_constructible_v<T>) : value() {}
};
```

## よくあるミス

??? failure "= default の型が常に true だと思う"
    メンバーのどれかの既定の構築が `noexcept` でなければ、全体も `false` です。

??? failure "noexcept と書いたコンストラクターで確保する"
    `noexcept` を付けたまま `new` が失敗すると、`std::terminate` で終了します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_default_constructible`](is_default_constructible.md) | 例外を考えずに、引数なしで作れるか |
| [`is_nothrow_constructible`](is_nothrow_constructible.md) | 任意の引数の構築 |
| [`is_trivially_default_constructible`](is_trivially_default_constructible.md) | 何もしない構築か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_default_constructible_v<T>` は、`T` の既定構築が例外を投げないか
    - [x] 引数なしの構築の `noexcept` を調べる
    - [x] 確保をするコンストラクターは `false`

## 関連ページ

- [cpprefjp: std::is_nothrow_default_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_default_constructible.html)
- [cppreference: std::is_nothrow_default_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_default_constructible)
