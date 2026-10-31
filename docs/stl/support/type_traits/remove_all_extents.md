---
title: std::remove_all_extents
summary: "配列の全部の次元を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_all_extents

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

多次元配列の最終的な要素の型を取り出したい。`std::remove_all_extents` は、<strong>配列のすべての次元を外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_all_extents_t<int[2][3]>` は `int`
    - すべての次元を外す
    - 配列でなければ、そのまま
    - 1 次元だけなら `remove_extent`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_all_extents_t {#remove_all_extents}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_all_extents_t = typename remove_all_extents<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int[2][3]` なら `int` を返します。`int[3]` も `int` です。配列でなければ、そのまま返します。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_all_extents<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_all_extents_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_all_extents_t<int[2][3]> は int : {}", std::is_same_v<std::remove_all_extents_t<int[2][3]>, int>);
  std::println("std::remove_all_extents_t<int[3]> は int : {}", std::is_same_v<std::remove_all_extents_t<int[3]>, int>);
  std::println("std::remove_all_extents_t<float> は float : {}", std::is_same_v<std::remove_all_extents_t<float>, float>);
}
```

```text title="実行結果"
std::remove_all_extents_t<int[2][3]> は int : true
std::remove_all_extents_t<int[3]> は int : true
std::remove_all_extents_t<float> は float : true
```

## ゲームでの使いどころ

多次元配列の最も内側の要素の型を取り出します。`int[3][4]` なら `int` で、配列全体の要素数を数えるときなどに使います。

```cpp
template <class T>
constexpr std::size_t TotalCount() {
  return sizeof(T) / sizeof(std::remove_all_extents_t<T>);   // int[3][4] なら 12
}

static_assert(TotalCount<int[3][4]>() == 12);
```

## よくあるミス

??? failure "remove_extent と取り違える"
    `remove_extent_t<int[3][4]>` は `int[4]`（1 次元ぶんだけ）です。すべての次元を外すのが `remove_all_extents` です。

??? failure "配列でない型に使って変わると思う"
    配列でない型は、そのまま返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_extent`](remove_extent.md) | 最初の次元だけ外す |
| [`rank`](rank.md) | 次元数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_all_extents_t<int[2][3]>` は `int`
    - [x] すべての次元を外す
    - [x] 配列でなければ、そのまま

## 関連ページ

- [cpprefjp: std::remove_all_extents](https://cpprefjp.github.io/reference/type_traits/remove_all_extents.html)
- [cppreference: std::remove_all_extents](https://en.cppreference.com/w/cpp/types/remove_all_extents)
