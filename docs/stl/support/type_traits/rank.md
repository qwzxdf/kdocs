---
title: std::rank
summary: "配列の次元の数を返す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::rank

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

配列は、`int[2][3]` のように何次元にもなります。`std::rank` は、<strong>配列の次元数</strong>を返します。

!!! tip "ポイント"
    - `std::rank_v<int[2][3]>` は 2
    - 配列でない型は 0
    - 各次元の要素数は `std::extent`
    - 戻り値は `std::size_t`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rank_v {#rank}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr std::size_t rank_v = rank<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 次元数を調べたい型 |

`rank_v<T>` は、`T` が配列型のとき、その次元数です。`int[3]` は 1、`int[2][3]` は 2、`int[2][3][4]` は 3 です。配列でない型は 0 です。

`int[]` のように要素数が決まっていない配列でも、次元数は数えます。各次元の要素数は、`std::extent` が返します。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("rank<int>         = {}", std::rank_v<int>);
  std::println("rank<int[3]>      = {}", std::rank_v<int[3]>);
  std::println("rank<int[2][3]>   = {}", std::rank_v<int[2][3]>);
}
```

```text title="実行結果"
rank<int>         = 0
rank<int[3]>      = 1
rank<int[2][3]>   = 2
```

## ゲームでの使いどころ

多次元配列を扱う汎用のテンプレートで、次元数を取り出します。ゲームでは、通常、`std::array` などを使うので、直接使う場面はまれです。

## よくあるミス

??? failure "`std::array` の次元数も取れると思う"
    `std::array` は配列型ではなくクラスなので、0 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`extent`](extent.md) | 次元の要素数 |
| [`remove_extent`](remove_extent.md) | 次元を外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rank_v<T>` は配列の次元数
    - [x] 配列でなければ 0
    - [x] 要素数は `extent`

## 関連ページ

- [cpprefjp: std::rank](https://cpprefjp.github.io/reference/type_traits/rank.html)
- [cppreference: std::rank](https://en.cppreference.com/w/cpp/types/rank)
