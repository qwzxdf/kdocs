---
title: std::is_nothrow_move_constructible
summary: "ムーブが例外を投げない型かを調べる。"
order: 12
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::vector` は、要素を新しい領域に移すとき、ムーブ構築が `noexcept` ならムーブし、そうでなければ安全のためコピーします。`std::is_nothrow_move_constructible` は、<strong>ムーブ構築が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_move_constructible_v<T>` は、`T` のムーブ構築が例外を投げないか
    - `vector` の再確保は、ムーブが `noexcept` かで、ムーブとコピーを選ぶ
    - `std::is_nothrow_move_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= default` のムーブは、メンバー次第で `noexcept` になる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_move_constructible_v {#is_nothrow_move_constructible}

```cpp
template <class T>
inline constexpr bool is_nothrow_move_constructible_v = is_nothrow_move_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブコンストラクターが `noexcept` と宣言されていれば `true` です。`std::vector` は、要素を新しい領域へ移すとき、ムーブが `noexcept` ならムーブし、そうでなければコピーします。ムーブの途中で例外が出ると、元に戻せなくなるためです。`noexcept` を付け忘れると、再確保のたびにコピーされて遅くなります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct MayThrow {
  MayThrow() = default;
  MayThrow(MayThrow&&) noexcept(false) {}
};

int main() {
  std::println("Player                     -> {}", std::is_nothrow_move_constructible_v<Player>);
  std::println("std::string                -> {}", std::is_nothrow_move_constructible_v<std::string>);
  std::println("MayThrow                   -> {}", std::is_nothrow_move_constructible_v<MayThrow>);
}
```

```text title="実行結果"
Player                     -> true
std::string                -> true
MayThrow                   -> false
```

## ゲームでの使いどころ

自作の型のムーブが `noexcept` であることを、コンパイル時に保証します。

```cpp
struct Enemy {
  std::string name;
  std::vector<int> items;

  Enemy(Enemy&&) noexcept = default;
  Enemy& operator=(Enemy&&) noexcept = default;
};

static_assert(std::is_nothrow_move_constructible_v<Enemy>, "Enemy のムーブに noexcept を付けてください");
```

## よくあるミス

??? failure "自作のムーブコンストラクターに noexcept を付けない"
    `vector` の再確保が、ムーブではなくコピーになり、遅くなります。`noexcept` が付けられる実装なら、必ず付けます。

??? failure "コピーしかない型で true を期待する"
    コピーコンストラクターが `noexcept` なら、右辺値はそれで受けられるので `true` になります。ただし、メモリを確保する型は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_move_constructible`](is_move_constructible.md) | 例外を考えずに、ムーブ構築できるか |
| [`is_nothrow_copy_constructible`](is_nothrow_copy_constructible.md) | コピー構築が例外を投げないか |
| [`is_nothrow_move_assignable`](is_nothrow_move_assignable.md) | ムーブ代入が例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_move_constructible_v<T>` は、`T` のムーブ構築が例外を投げないか
    - [x] ムーブ構築の `noexcept` を調べる
    - [x] 自作の型には、ムーブに `noexcept` を付ける

## 関連ページ

- [cpprefjp: std::is_nothrow_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_move_constructible.html)
- [cppreference: std::is_nothrow_move_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_move_constructible)
