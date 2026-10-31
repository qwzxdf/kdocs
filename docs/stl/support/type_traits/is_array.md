---
title: std::is_array
summary: "型が配列かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_array

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

配列とポインタは別物ですが、関数に渡すと配列がポインタに変わるため、混同しやすいです。`std::is_array` は、<strong>型が配列か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_array_v<T>` は、`T` が配列型（`int[3]` や `int[]`）か
    - `T[N]` と `T[]` の両方が `true`
    - `std::is_array<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `std::array` は配列ではなくクラスなので `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_array_v {#is_array}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_array_v = is_array<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int[3]` や `int[]` のような、組み込みの配列型が `true` です。`std::array<int, 3>` は配列ではなくクラスなので `false` です。ポインターに変わった配列（関数の引数に渡した後の `int*`）も `false` になります。

## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <type_traits>

int main() {
  std::println("int[3]                     -> {}", std::is_array_v<int[3]>);
  std::println("int[]                      -> {}", std::is_array_v<int[]>);
  std::println("int*                       -> {}", std::is_array_v<int*>);
  std::println("std::array<int, 3>         -> {}", std::is_array_v<std::array<int, 3>>);
}
```

```text title="実行結果"
int[3]                     -> true
int[]                      -> true
int*                       -> false
std::array<int, 3>         -> false
```

## ゲームでの使いどころ

配列型の `T` には `delete[]`、それ以外には `delete` を選ぶ、カスタム削除子を書けます。

```cpp
template <class T>
struct Deleter {
  void operator()(std::remove_extent_t<T>* p) const {
    if constexpr (std::is_array_v<T>) {
      delete[] p;
    } else {
      delete p;
    }
  }
};
```

## よくあるミス

??? failure "std::array を配列だと思う"
    `std::array` は、配列を中に持つクラスなので、`false` です。`std::is_class_v` が `true` になります。

??? failure "引数で受けた配列を調べる"
    関数の引数の `int a[3]` は、`int*` に変わっているので、`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_bounded_array`](is_bounded_array.md) | 要素数が決まった配列か（C++20） |
| [`is_unbounded_array`](is_unbounded_array.md) | 要素数が不明の配列か（C++20） |
| [`remove_extent`](remove_extent.md) | 配列の 1 次元ぶんを外した型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_array_v<T>` は、`T` が配列型（`int[3]` や `int[]`）か
    - [x] 組み込みの配列型だけが `true`（`std::array` は `false`）
    - [x] `delete[]` と `delete` の切り替えなどに使う

## 関連ページ

- [cpprefjp: std::is_array](https://cpprefjp.github.io/reference/type_traits/is_array.html)
- [cppreference: std::is_array](https://en.cppreference.com/w/cpp/types/is_array)
