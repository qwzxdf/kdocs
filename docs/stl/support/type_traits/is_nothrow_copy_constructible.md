---
title: std::is_nothrow_copy_constructible
summary: "例外を投げずにコピーして構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

例外安全性の判断に使いたい。`std::is_nothrow_copy_constructible` は、<strong>型のコピー構築が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_copy_constructible_v<T>` は、`T` のコピー構築が例外を投げないか
    - `std::string` などのメモリを確保する型は `false`
    - `std::is_nothrow_copy_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= default` はメンバー次第

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_copy_constructible_v {#is_nothrow_copy_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_copy_constructible_v = is_nothrow_copy_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

コピー構築が `noexcept` と宣言されていれば `true` です。数値だけの構造体は `true` ですが、`std::string` のコピーはメモリを確保して例外を投げうるので `false` です。メンバーに `std::string` が 1 つでもあれば、`= default` のコピーも `false` になります。

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
  std::println("Player                             -> {}", std::is_nothrow_copy_constructible_v<Player>);
  std::println("int                                -> {}", std::is_nothrow_copy_constructible_v<int>);
  std::println("std::string                        -> {}", std::is_nothrow_copy_constructible_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

コピーを返す関数の `noexcept` を、型に合わせて決めます。

```cpp
template <class T>
T Duplicate(const T& value) noexcept(std::is_nothrow_copy_constructible_v<T>) {
  return value;   // コピーを作る
}
```

## よくあるミス

??? failure "= default のコピーが常に true だと思う"
    メンバーのどれかのコピーが `noexcept` でなければ、全体も `false` です。

??? failure "ムーブ構築と取り違える"
    ムーブは `is_nothrow_move_constructible` で調べます。`std::vector` の再確保は、ムーブが `noexcept` かで、移すかコピーするかを決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_move_constructible`](is_nothrow_move_constructible.md) | ムーブ構築が例外を投げないか |
| [`is_copy_constructible`](is_copy_constructible.md) | 例外を考えずに、コピー構築できるか |
| [`is_nothrow_constructible`](is_nothrow_constructible.md) | 任意の引数の構築 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_copy_constructible_v<T>` は、`T` のコピー構築が例外を投げないか
    - [x] コピー構築の `noexcept` を調べる
    - [x] `= default` の結果はメンバーで決まる

## 関連ページ

- [cpprefjp: std::is_nothrow_copy_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_copy_constructible.html)
- [cppreference: std::is_nothrow_copy_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_copy_constructible)
