---
title: std::is_move_constructible
summary: "ムーブして構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ムーブは、コピーより安く値を移す仕組みです。`std::is_move_constructible` は、<strong>型がムーブ構築できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_move_constructible_v<T>` は、`T` がムーブ構築できるか
    - コピーコンストラクターがあれば `true`
    - `std::is_move_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= delete` したムーブコンストラクターは `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_move_constructible_v {#is_move_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_move_constructible_v = is_move_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

右辺値から新しいオブジェクトを作れるかを調べます。ムーブコンストラクターがなくても、コピーコンストラクターがあれば右辺値をコピーで受けるので、`true` です。ムーブコンストラクターを `= delete` すると、`false` になります。

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
  std::println("Player                     -> {}", std::is_move_constructible_v<Player>);
  std::println("std::unique_ptr<int>       -> {}", std::is_move_constructible_v<std::unique_ptr<int>>);
  std::println("NoCopy                     -> {}", std::is_move_constructible_v<NoCopy>);
}
```

```text title="実行結果"
Player                     -> true
std::unique_ptr<int>       -> true
NoCopy                     -> false
```

## ゲームでの使いどころ

要素を移す処理を持つコンテナで、ムーブできない型を弾きます。

```cpp
template <class T>
class Pool {
  static_assert(std::is_move_constructible_v<T>, "確保し直すときに移せる型にしてください");
  std::vector<T> items_;
};
```

## よくあるミス

??? failure "コピーコンストラクターだけの型が false になると思う"
    右辺値は、コピーコンストラクターで受けられるので `true` です。`= delete` したときだけ `false` です。

??? failure "noexcept かどうかと混同する"
    ムーブできるかと、例外を投げないかは別です。後者は `is_nothrow_move_constructible` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_constructible`](is_copy_constructible.md) | コピー構築できるか |
| [`is_nothrow_move_constructible`](is_nothrow_move_constructible.md) | ムーブ構築が例外を投げないか |
| [`is_move_assignable`](is_move_assignable.md) | ムーブ代入できるか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_move_constructible_v<T>` は、`T` がムーブ構築できるか
    - [x] 右辺値から作れるかを調べる
    - [x] コピーだけの型でも `true`

## 関連ページ

- [cpprefjp: std::is_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_move_constructible.html)
- [cppreference: std::is_move_constructible](https://en.cppreference.com/w/cpp/types/is_move_constructible)
