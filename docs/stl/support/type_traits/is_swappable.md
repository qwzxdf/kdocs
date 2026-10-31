---
title: std::is_swappable
summary: "`swap` で入れ替えられる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

ソートや `vector` の操作は、要素の入れ替え（`swap`）を使います。`std::is_swappable` は、<strong>型の値を入れ替えられるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_swappable_v<T>` は、`T` の 2 つの値を `swap` できるか
    - 標準の `swap` はムーブで入れ替える
    - `std::is_swappable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `const` な型は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_swappable_v {#is_swappable}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
inline constexpr bool is_swappable_v = is_swappable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`swap(a, b)`（`using std::swap;` を前に置いて、引数に関連する名前空間の `swap` も探す形）が書ける型なら `true` です。ムーブ構築とムーブ代入ができる型は、標準の `std::swap` で入れ替えられます。ムーブを削除した型や、`const` な型は `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Fixed {
  Fixed(Fixed&&) = delete;
  Fixed& operator=(Fixed&&) = delete;
};

int main() {
  std::println("int                                -> {}", std::is_swappable_v<int>);
  std::println("std::string                        -> {}", std::is_swappable_v<std::string>);
  std::println("Fixed                              -> {}", std::is_swappable_v<Fixed>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
Fixed                              -> false
```

## ゲームでの使いどころ

並べ替えやシャッフルの前に、要素が入れ替えられる型かを確かめます。

```cpp
template <class T>
void Shuffle(std::vector<T>& items) {
  static_assert(std::is_swappable_v<T>, "要素は swap できる型にしてください");
  // ...
}
```

## よくあるミス

??? failure "const な型を入れ替えようとする"
    `const int` は変更できないので、`false` です。

??? failure "ムーブを削除した型で true を期待する"
    標準の `swap` はムーブで入れ替えます。ムーブを `= delete` した型は `false` です。自前の `swap` を用意すれば、`true` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_swappable`](is_nothrow_swappable.md) | 入れ替えが例外を投げないか |
| [`is_swappable_with`](is_swappable_with.md) | 型の違う 2 つを入れ替えられるか |
| [`is_move_assignable`](is_move_assignable.md) | ムーブ代入できるか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_swappable_v<T>` は、`T` の 2 つの値を `swap` できるか
    - [x] `swap(a, b)` が書けるかを調べる
    - [x] ムーブを削除した型や `const` は `false`

## 関連ページ

- [cpprefjp: std::is_swappable](https://cpprefjp.github.io/reference/type_traits/is_swappable.html)
- [cppreference: std::is_swappable](https://en.cppreference.com/w/cpp/types/is_swappable)
