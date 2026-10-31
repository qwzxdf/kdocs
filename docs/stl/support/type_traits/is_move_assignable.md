---
title: std::is_move_assignable
summary: "ムーブ代入できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_move_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`a = std::move(b)` が書ける型かを調べたい。`std::is_move_assignable` は、<strong>型がムーブ代入できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_move_assignable_v<T>` は、`T` がムーブ代入できるか
    - コピー代入だけの型でも `true`
    - `std::is_move_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= delete` したムーブ代入や `const` メンバーは `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_move_assignable_v {#is_move_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_move_assignable_v = is_move_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

右辺値から代入できるか（`T& = T&&`）を調べます。ムーブ代入を持たず、コピー代入だけを持つ型でも、右辺値をコピー代入で受けられるので、`true` になります。ムーブ代入を `= delete` した型と、`const` メンバーを持つ型が `false` です。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                     -> {}", std::is_move_assignable_v<Player>);
  std::println("std::unique_ptr<int>       -> {}", std::is_move_assignable_v<std::unique_ptr<int>>);
  std::println("const Player               -> {}", std::is_move_assignable_v<const Player>);
}
```

```text title="実行結果"
Player                     -> true
std::unique_ptr<int>       -> true
const Player               -> false
```

## ゲームでの使いどころ

`std::vector` の要素の入れ替えや並べ替えなど、ムーブ代入を使う処理の前提を確かめます。

```cpp
template <class T>
void SortItems(std::vector<T>& items) {
  static_assert(std::is_move_assignable_v<T>, "並べ替えには、ムーブ代入が要ります");
  std::sort(items.begin(), items.end());
}
```

## よくあるミス

??? failure "ムーブ代入がないと false になると思う"
    コピー代入があれば、右辺値でもそれが使えるので `true` です。`= delete` で明示的に削除したときだけ `false` です。

??? failure "const メンバーを持つクラス"
    `const` のメンバーがあると、代入演算子が削除されるので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_assignable`](is_copy_assignable.md) | コピー代入できるか |
| [`is_nothrow_move_assignable`](is_nothrow_move_assignable.md) | ムーブ代入が例外を投げないか |
| [`is_move_constructible`](is_move_constructible.md) | ムーブ構築できるか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_move_assignable_v<T>` は、`T` がムーブ代入できるか
    - [x] 右辺値からの代入ができるかを調べる
    - [x] コピー代入があれば `true`

## 関連ページ

- [cpprefjp: std::is_move_assignable](https://cpprefjp.github.io/reference/type_traits/is_move_assignable.html)
- [cppreference: std::is_move_assignable](https://en.cppreference.com/w/cpp/types/is_move_assignable)
