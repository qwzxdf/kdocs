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

代入がビットの複製だけで済むかを知りたい。`std::is_trivially_assignable<T, U>` は、<strong>T への U の代入が自明か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_assignable_v<T, U>` は、`T` に `U` を自明に代入できるか
    - 自明な代入は、ビットを写すだけで済む代入
    - `std::is_trivially_assignable<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `T` は参照型で渡す

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

`declval<T>() = declval<U>()` が、自明な（ビットを写すだけの）処理で済むなら `true` です。第 1 引数は代入される側の型で、`T&` を渡します。

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

代入する範囲の型が自明に代入できるなら、`memcpy` で一気に写します。

```cpp
template <class T>
void CopyRange(T* dst, const T* src, std::size_t n) {
  if constexpr (std::is_trivially_assignable_v<T&, const T&>) {
    std::memcpy(dst, src, sizeof(T) * n);
  } else {
    std::copy_n(src, n, dst);
  }
}
```

## よくあるミス

??? failure "T を参照にしないで調べる"
    右辺値への代入になり、`false` です。`T&` の形で渡します。

??? failure "自明な代入ならコピーしてよいと思う"
    代入が自明でも、オブジェクトの寿命を始めるわけではありません。`memcpy` で写す先に、すでに生きているオブジェクトがあるときだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_assignable`](is_assignable.md) | 例外や自明さを考えずに、代入できるか |
| [`is_trivially_copy_assignable`](is_trivially_copy_assignable.md) | 同じ型のコピー代入に絞った版 |
| [`is_trivially_move_assignable`](is_trivially_move_assignable.md) | ムーブ代入に絞った版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_assignable_v<T, U>` は、`T` に `U` を自明に代入できるか
    - [x] 代入の自明さを調べる
    - [x] memcpy の近道を選ぶ条件になる

## 関連ページ

- [cpprefjp: std::is_trivially_assignable](https://cpprefjp.github.io/reference/type_traits/is_trivially_assignable.html)
- [cppreference: std::is_trivially_assignable](https://en.cppreference.com/w/cpp/types/is_trivially_assignable)
