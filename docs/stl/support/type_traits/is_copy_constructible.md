---
title: std::is_copy_constructible
summary: "コピーして作れる型かを調べる。"
order: 11
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

コンテナに入れる、関数に値渡しする、といった場面で、コピーできる型かが必要になります。`std::is_copy_constructible` は、<strong>型がコピー構築できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_copy_constructible_v<T>` は、`T` がコピー構築できるか
    - `unique_ptr` のようなムーブ専用の型は `false`
    - `std::is_copy_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 抽象クラスも `false`（作れないため）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_copy_constructible_v {#is_copy_constructible}

```cpp
template <class T>
inline constexpr bool is_copy_constructible_v = is_copy_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`const T&` から新しいオブジェクトを作れるかを調べます。`std::string` や `std::vector` は `true`、`std::unique_ptr` や `std::thread` は `false` です。抽象クラスも `false` です。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct NoCopy {
  NoCopy() = default;
  NoCopy(const NoCopy&) = delete;
  NoCopy& operator=(const NoCopy&) = delete;
};

int main() {
  std::println("Player                     -> {}", std::is_copy_constructible_v<Player>);
  std::println("NoCopy                     -> {}", std::is_copy_constructible_v<NoCopy>);
  std::println("std::unique_ptr<int>       -> {}", std::is_copy_constructible_v<std::unique_ptr<int>>);
}
```

```text title="実行結果"
Player                     -> true
NoCopy                     -> false
std::unique_ptr<int>       -> false
```

## ゲームでの使いどころ

イベントを待ち行列に入れるとき、コピーできる型は複製して持ち、コピーできない型はムーブで持つ、と分けられます。

```cpp
template <class Event>
void Push(Event&& e) {
  using E = std::remove_cvref_t<Event>;
  if constexpr (std::is_copy_constructible_v<E>) {
    queue_.emplace_back(e);               // コピーして残す
  } else {
    queue_.emplace_back(std::move(e));    // ムーブ専用の型
  }
}
```

## よくあるミス

??? failure "抽象クラスが true になると思う"
    抽象クラスはオブジェクトを作れないので `false` です。

??? failure "ムーブ専用の型を std::vector に入れてコピーしようとする"
    `std::vector<std::unique_ptr<T>>` は、コピーコンストラクターが宣言されているので `true` になりますが、実際にコピーしようとするとコンパイルエラーです。コンテナの中身の型でも調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_move_constructible`](is_move_constructible.md) | ムーブして作れるか |
| [`is_copy_assignable`](is_copy_assignable.md) | コピー代入できるか |
| [`is_nothrow_copy_constructible`](is_nothrow_copy_constructible.md) | コピー構築が例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_copy_constructible_v<T>` は、`T` がコピー構築できるか
    - [x] `const T&` から作れるかを調べる
    - [x] ムーブ専用の型や抽象クラスは `false`

## 関連ページ

- [cpprefjp: std::is_copy_constructible](https://cpprefjp.github.io/reference/type_traits/is_copy_constructible.html)
- [cppreference: std::is_copy_constructible](https://en.cppreference.com/w/cpp/types/is_copy_constructible)
