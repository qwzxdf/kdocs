---
title: std::is_member_pointer
summary: "型がメンバへのポインタかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_member_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

メンバー変数へのポインタとメンバー関数へのポインタをまとめて扱いたい場面があります。`std::is_member_pointer` は、<strong>型がメンバーへのポインタか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_member_pointer_v<T>` は、`T` がメンバーへのポインタ（変数または関数）か
    - メンバーポインターは通常のポインターではない
    - `std::is_member_pointer<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `std::invoke` の内部で使われる考え方

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_member_pointer_v {#is_member_pointer}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_member_pointer_v = is_member_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

メンバー変数へのポインターと、メンバー関数へのポインターの、どちらかなら `true` です。`std::invoke` が、呼ぶものがメンバーを指すか、関数かで処理を分けるときに、この判定が土台になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  void Move() {}
};

int main() {
  std::println("int Player::*              -> {}", std::is_member_pointer_v<int Player::*>);
  std::println("void (Player::*)()         -> {}", std::is_member_pointer_v<void (Player::*)()>);
  std::println("int*                       -> {}", std::is_member_pointer_v<int*>);
}
```

```text title="実行結果"
int Player::*              -> true
void (Player::*)()         -> true
int*                       -> false
```

## ゲームでの使いどころ

`std::invoke` と同じように、関数ポインターとメンバーポインターの両方を、まとめて呼ぶ関数を書きます。

```cpp
template <class F, class... Args>
decltype(auto) Call(F f, Args&&... args) {
  if constexpr (std::is_member_pointer_v<F>) {
    return std::invoke(f, std::forward<Args>(args)...);   // 最初の引数がオブジェクト
  } else {
    return f(std::forward<Args>(args)...);
  }
}
```

## よくあるミス

??? failure "ポインターの is_pointer が true になると思う"
    メンバーポインターは、通常のポインターではないので、`is_pointer_v` は `false` です。

??? failure "メンバーが値かどうかを見分けようとする"
    変数か関数かの区別には、`is_member_object_pointer` と `is_member_function_pointer` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_member_object_pointer`](is_member_object_pointer.md) | メンバー変数へのポインターか |
| [`is_member_function_pointer`](is_member_function_pointer.md) | メンバー関数へのポインターか |
| [`is_pointer`](is_pointer.md) | 通常のポインターか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_member_pointer_v<T>` は、`T` がメンバーへのポインタ（変数または関数）か
    - [x] メンバー変数・メンバー関数のどちらのポインターでも `true`
    - [x] 通常のポインターは `is_pointer`

## 関連ページ

- [cpprefjp: std::is_member_pointer](https://cpprefjp.github.io/reference/type_traits/is_member_pointer.html)
- [cppreference: std::is_member_pointer](https://en.cppreference.com/w/cpp/types/is_member_pointer)
