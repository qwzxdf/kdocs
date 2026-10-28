---
title: std::tuple_size
summary: "tuple や pair、array の要素数、各要素の型を、コンパイル時に調べる。"
order: 59
tags:
  - ユーティリティ
---

# std::tuple_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::tuple_size` と `std::tuple_element` は、**tuple・pair・array の要素数と、各要素の型をコンパイル時に調べる**部品です。テンプレートを書くとき以外は使いません。自作の型を構造化束縛に対応させるときにも、これらの特殊化を書きます。

!!! tip "ポイント"
    - `std::tuple_size_v<T>` が要素数、`std::tuple_element_t<N, T>` が N 番目の型。
    - テンプレートメタプログラミングの部品。
    - 自作クラスを構造化束縛に対応させるには、`tuple_size`・`tuple_element`・`get` を用意する。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::tuple_size, std::tuple_element {#tuple_size}

```cpp
template <class T>
struct tuple_size;                 // std::tuple_size_v<T> で値を取る

template <std::size_t I, class T>
struct tuple_element;              // std::tuple_element_t<I, T> で型を取る
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | tuple・pair・array などの型 |
| `I` | テンプレート引数 | 要素の番号（`tuple_element` のみ） |

- 戻り値: 要素数（`size_t`）、または I 番目の型
- 計算量: コンパイル時

```cpp
#include <print>
#include <tuple>
#include <type_traits>

int main() {
  using T = std::tuple<int, char, double>;

  std::println("要素数 {}", std::tuple_size_v<T>);
  std::println("1 番目は char？ {}", std::is_same_v<std::tuple_element_t<1, T>, char>);
}
```

```text title="実行結果"
要素数 3
1 番目は char？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、tuple のすべての要素に処理を適用する | `for_each_tuple` で `tuple_size_v` の数だけ繰り返す |

## よくあるミス

??? failure "型ではなく値に使う"
    `std::tuple_size` には「型」を渡します。変数ではなく `decltype(t)` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tuple`](tuple.md) | 本体 |
| [`std::array`](../containers/array.md) | `std::tuple_size` が使える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数と各要素の型をコンパイル時に調べる
    - [x] `tuple_size_v` と `tuple_element_t`
    - [x] 普通のコードでは使わない

## 関連ページ

- [cpprefjp: std::tuple_size](https://cpprefjp.github.io/reference/tuple/tuple_size.html)
- [cppreference: std::tuple_size](https://en.cppreference.com/w/cpp/utility/tuple_size)
