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
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_swappable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

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

`swap(a, b)` が書ける型なら `true` です。ムーブ構築とムーブ代入ができる型は、標準の `std::swap` で入れ替えられます。ムーブを削除した型は `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

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

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_swappable_v<T>) {
    // T が条件に当てはまる型のときの処理
  } else {
    // それ以外の型の処理
  }
}
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_swappable_v<T>` は、`T` の 2 つの値を `swap` できるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_swappable](https://cpprefjp.github.io/reference/type_traits/is_swappable.html)
- [cppreference: std::is_swappable](https://en.cppreference.com/w/cpp/types/is_swappable)
