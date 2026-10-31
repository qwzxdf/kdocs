---
title: std::is_member_object_pointer
summary: "型がメンバ変数へのポインタかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_member_object_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

クラスのメンバー変数を名前でなく「どのメンバーか」を値として持ち回したいときに、メンバー変数へのポインタを使います。`std::is_member_object_pointer` は、<strong>型がメンバー変数へのポインタか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_member_object_pointer_v<T>` は、`T` がメンバー変数へのポインタか
    - `&Player::hp` の型が対象
    - `std::is_member_object_pointer<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `obj.*ptr` でアクセスする

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_member_object_pointer_v {#is_member_object_pointer}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_member_object_pointer_v = is_member_object_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int Player::*` のような、メンバー変数へのポインターが `true` です。オブジェクトのアドレスに足してアクセスする目印で、`obj.*ptr` と書いて値を取ります。静的メンバー変数へのポインターは、普通のポインターなので `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int Player::*              -> {}", std::is_member_object_pointer_v<int Player::*>);
  std::println("void (Player::*)()         -> {}", std::is_member_object_pointer_v<void (Player::*)()>);
  std::println("int*                       -> {}", std::is_member_object_pointer_v<int*>);
}
```

```text title="実行結果"
int Player::*              -> true
void (Player::*)()         -> false
int*                       -> false
```

## ゲームでの使いどころ

メンバー変数を指す印で、名前の表を作るような、簡易的な仕組みに使います。

```cpp
struct Player {
  int hp;
  int mp;
};

template <class Class, class Member>
void Print(const Class& obj, Member Class::*field) {
  static_assert(std::is_member_object_pointer_v<Member Class::*>);
  std::println("{}", obj.*field);
}
// Print(player, &Player::hp);
```

## よくあるミス

??? failure "静的メンバー変数が true になると思う"
    `static` なメンバー変数は、普通の変数と同じなので、そのポインターは `false` です。

??? failure "メンバー関数ポインターを調べる"
    `is_member_function_pointer` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_member_function_pointer`](is_member_function_pointer.md) | メンバー関数へのポインターか |
| [`is_member_pointer`](is_member_pointer.md) | どちらも含む |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_member_object_pointer_v<T>` は、`T` がメンバー変数へのポインタか
    - [x] メンバー変数へのポインターが `true`
    - [x] 静的メンバーは対象外

## 関連ページ

- [cpprefjp: std::is_member_object_pointer](https://cpprefjp.github.io/reference/type_traits/is_member_object_pointer.html)
- [cppreference: std::is_member_object_pointer](https://en.cppreference.com/w/cpp/types/is_member_object_pointer)
