---
title: std::is_nothrow_move_assignable
summary: "例外を投げずにムーブ代入できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_move_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`std::vector` などの操作が強い例外保証を持てるかに関わる。`std::is_nothrow_move_assignable` は、<strong>型のムーブ代入が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_move_assignable_v<T>` は、`T` のムーブ代入が例外を投げないか
    - 自作のムーブ代入には `noexcept` を付ける
    - `std::is_nothrow_move_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 付け忘れると `std::swap` の `noexcept` も `false` になる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_move_assignable_v {#is_nothrow_move_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_move_assignable_v = is_nothrow_move_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブ代入（`T& = T&&`）が `noexcept` と宣言されていれば `true` です。標準のコンテナのムーブ代入は、通常 `noexcept` です。自作の型で `noexcept` を付け忘れると `false` になり、ムーブを使うアルゴリズムが、例外に対する保証を弱めます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct MayThrow {
  MayThrow() = default;
  MayThrow(MayThrow&&) noexcept(false) {}
  MayThrow& operator=(MayThrow&&) noexcept(false) { return *this; }
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::is_nothrow_move_assignable_v<Player>);
  std::println("std::string                        -> {}", std::is_nothrow_move_assignable_v<std::string>);
  std::println("MayThrow                           -> {}", std::is_nothrow_move_assignable_v<MayThrow>);
}
```

```text title="実行結果"
Player                             -> true
std::string                        -> true
MayThrow                           -> false
```

## ゲームでの使いどころ

入れ替えの関数で、ムーブ構築とムーブ代入のどちらも `noexcept` のときだけ、全体を `noexcept` にします。

```cpp
template <class T>
void MySwap(T& a, T& b) noexcept(std::is_nothrow_move_constructible_v<T> &&
                                 std::is_nothrow_move_assignable_v<T>) {
  T tmp = std::move(a);
  a = std::move(b);
  b = std::move(tmp);
}
```

## よくあるミス

??? failure "自作のムーブ代入に noexcept を付け忘れる"
    `false` になります。ムーブで例外が出ない実装なら、`noexcept` を付けます。

??? failure "コピー代入だけの型で true を期待する"
    コピー代入が `noexcept` なら `true` ですが、メモリを確保する型は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_move_constructible`](is_nothrow_move_constructible.md) | ムーブ構築が例外を投げないか |
| [`is_move_assignable`](is_move_assignable.md) | 例外を考えずに、ムーブ代入できるか |
| [`is_nothrow_swappable`](is_nothrow_swappable.md) | 入れ替えが例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_move_assignable_v<T>` は、`T` のムーブ代入が例外を投げないか
    - [x] ムーブ代入の `noexcept` を調べる
    - [x] 自作の型は `noexcept` を付ける

## 関連ページ

- [cpprefjp: std::is_nothrow_move_assignable](https://cpprefjp.github.io/reference/type_traits/is_nothrow_move_assignable.html)
- [cppreference: std::is_nothrow_move_assignable](https://en.cppreference.com/w/cpp/types/is_nothrow_move_assignable)
