---
title: std::is_member_function_pointer
summary: "型がメンバ関数へのポインタかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_member_function_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

メンバー関数を後から呼べる値として持ち回すとき、メンバー関数へのポインタを使います。`std::is_member_function_pointer` は、<strong>型がメンバー関数へのポインタか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_member_function_pointer_v<T>` は、`T` がメンバー関数へのポインタか
    - `&Player::Hit` の型が対象。静的メンバー関数は `false`
    - `std::is_member_function_pointer<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 呼び出しには `.*` か `std::invoke`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_member_function_pointer_v {#is_member_function_pointer}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_member_function_pointer_v = is_member_function_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`void (Player::*)(int)` のような、メンバー関数へのポインターが `true` です。静的メンバー関数は、普通の関数ポインターなので `false` です。呼ぶときは `(obj.*pmf)(args)` と書き、`std::invoke` がこれを統一して扱います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  void Move() {}
};

int main() {
  std::println("void (Player::*)()         -> {}", std::is_member_function_pointer_v<void (Player::*)()>);
  std::println("int Player::*              -> {}", std::is_member_function_pointer_v<int Player::*>);
  std::println("void (*)()                 -> {}", std::is_member_function_pointer_v<void (*)()>);
}
```

```text title="実行結果"
void (Player::*)()         -> true
int Player::*              -> false
void (*)()                 -> false
```

## ゲームでの使いどころ

イベントに、メンバー関数と自由関数のどちらも登録できる関数を書きます。

```cpp
template <class F, class Obj>
void Bind(F f, Obj* obj) {
  if constexpr (std::is_member_function_pointer_v<F>) {
    handler_ = [f, obj](int arg) { (obj->*f)(arg); };
  } else {
    handler_ = [f](int arg) { f(arg); };
  }
}
```

## よくあるミス

??? failure "静的メンバー関数が true になると思う"
    静的メンバー関数は、普通の関数と同じ型なので `false` です。

??? failure "メンバー変数へのポインターを調べる"
    `int Player::*` は `false` です。`is_member_object_pointer` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_member_object_pointer`](is_member_object_pointer.md) | メンバー変数へのポインターか |
| [`is_member_pointer`](is_member_pointer.md) | どちらのメンバーポインターか |
| [`invoke`](../functional/invoke.md) | 統一して呼ぶ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_member_function_pointer_v<T>` は、`T` がメンバー関数へのポインタか
    - [x] メンバー関数へのポインターが `true`
    - [x] 呼ぶには `(obj.*pmf)()` か `std::invoke`

## 関連ページ

- [cpprefjp: std::is_member_function_pointer](https://cpprefjp.github.io/reference/type_traits/is_member_function_pointer.html)
- [cppreference: std::is_member_function_pointer](https://en.cppreference.com/w/cpp/types/is_member_function_pointer)
