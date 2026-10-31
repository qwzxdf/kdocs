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

特定の引数で構築できる型かを事前に調べたい。たとえば、`emplace_back` に渡す引数で構築できるかを確かめます。`std::is_constructible<T, Args...>` は、<strong>T を Args... から構築できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_constructible_v<T, Args...>` は、`T` を `Args...` から構築できるか
    - 引数の型の並びを `Args...` として渡す
    - `std::is_constructible<T, Args...>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `explicit` のコンストラクターでも `true`（暗黙の変換とは別）

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

`std::is_constructible_v<T, Args...>` は、`T(args...)` と書いてオブジェクトを作れるかを調べます。デストラクターが使える（アクセスできる）ことも条件です。private のコンストラクターは `false` になります。

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

汎用の `Create` 関数で、構築できない組み合わせを、制約で弾きます。

```cpp
template <class T, class... Args>
  requires std::is_constructible_v<T, Args...>
T* Create(Args&&... args) {
  return new T(std::forward<Args>(args)...);
}
```

## よくあるミス

??? failure "引数の型を間違えて false になる"
    `std::is_constructible_v<Player, int>` は、`Player(int)` が必要です。暗黙の変換で作れる型は `true` になります。

??? failure "private のコンストラクターが使えると思う"
    アクセスできないコンストラクターは `false` です。`friend` の中で調べても、外の判定は変わりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_default_constructible`](is_default_constructible.md) | 引数なしで作れるか |
| [`is_copy_constructible`](is_copy_constructible.md) | コピーして作れるか |
| [`is_nothrow_constructible`](is_nothrow_constructible.md) | 作る処理が例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_constructible_v<T, Args...>` は、`T` を `Args...` から構築できるか
    - [x] `T(args...)` が書けるかを調べる
    - [x] private や削除されたコンストラクターは `false`

## 関連ページ

- [cpprefjp: std::is_constructible](https://cpprefjp.github.io/reference/type_traits/is_constructible.html)
- [cppreference: std::is_constructible](https://en.cppreference.com/w/cpp/types/is_constructible)
