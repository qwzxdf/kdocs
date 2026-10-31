---
title: std::remove_extent
summary: "配列の最初の次元を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

配列型 `int[3]` から、要素の型 `int` を取り出したい。`std::remove_extent` は、<strong>配列の 1 次元を外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_extent_t<int[3]>` は `int`
    - 最初の次元だけ外す
    - 配列でなければ、そのまま
    - すべての次元を外すなら `remove_all_extents`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_extent_t {#remove_extent}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_extent_t = typename remove_extent<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int[3]` や `int[]` なら `int` を返します。多次元配列 `int[2][3]` は、最初の次元だけ外して `int[3]` になります。配列でなければ、そのまま返します。

すべての次元を外すなら `remove_all_extents` です。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_extent<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_extent_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_extent_t<int[3]> は int : {}", std::is_same_v<std::remove_extent_t<int[3]>, int>);
  std::println("std::remove_extent_t<int[2][3]> は int[3] : {}", std::is_same_v<std::remove_extent_t<int[2][3]>, int[3]>);
  std::println("std::remove_extent_t<int> は int : {}", std::is_same_v<std::remove_extent_t<int>, int>);
}
```

```text title="実行結果"
std::remove_extent_t<int[3]> は int : true
std::remove_extent_t<int[2][3]> は int[3] : true
std::remove_extent_t<int> は int : true
```

## ゲームでの使いどころ

配列の最も外側の 1 次元を外した型を作ります。`int[]` や `int[3]` から要素の型 `int` を取り出すときに使います。

```cpp
template <class T>
struct ArrayDeleter {
  void operator()(std::remove_extent_t<T>* p) const { delete[] p; }   // T=int[] なら int*
};

static_assert(std::is_same_v<std::remove_extent_t<int[3]>, int>);
```

## よくあるミス

??? failure "多次元配列をすべて外せると思う"
    `remove_extent_t<int[3][4]>` は `int[4]` です。すべて外すには `remove_all_extents` を使います。

??? failure "std::array を配列として外す"
    `std::array<int, 3>` は、配列ではなくクラスなので、そのまま返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_all_extents`](remove_all_extents.md) | すべての次元を外す |
| [`extent`](extent.md) | 次元の要素数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_extent_t<int[3]>` は `int`
    - [x] 最初の次元だけ外す
    - [x] 配列でなければ、そのまま

## 関連ページ

- [cpprefjp: std::remove_extent](https://cpprefjp.github.io/reference/type_traits/remove_extent.html)
- [cppreference: std::remove_extent](https://en.cppreference.com/w/cpp/types/remove_extent)
