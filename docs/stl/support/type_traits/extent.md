---
title: std::extent
summary: "配列の指定した次元の要素数を返す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`int[2][3]` の最初の次元の要素数は 2、2 番目は 3 です。`std::extent` は、<strong>配列の指定した次元の要素数</strong>を返します。

!!! tip "ポイント"
    - `std::extent_v<int[2][3], 0>` は 2、`<int[2][3], 1>` は 3
    - 第 2 引数は次元の番号（0 から）。省略時は 0
    - 配列でない型や、範囲外の次元は 0
    - 戻り値は `std::size_t`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::extent_v {#extent}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, unsigned N = 0>
inline constexpr std::size_t extent_v = extent<T, N>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい配列の型 |
| `N` | `unsigned` | 次元の番号（0 から）。既定は 0 |

`extent_v<T, N>` は、`T` が配列型のとき、`N` 番目の次元の要素数です。`int[2][3]` の 0 番目は 2、1 番目は 3 です。範囲外の次元や、配列でない型、要素数が決まっていない次元（`int[]`）は 0 です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("extent<int[2][3], 0> = {}", std::extent_v<int[2][3], 0>);
  std::println("extent<int[2][3], 1> = {}", std::extent_v<int[2][3], 1>);
  std::println("extent<int[2][3], 2> = {}", std::extent_v<int[2][3], 2>);   // 範囲外
  std::println("extent<int[], 0>     = {}", std::extent_v<int[], 0>);      // 要素数不明
}
```

```text title="実行結果"
extent<int[2][3], 0> = 2
extent<int[2][3], 1> = 3
extent<int[2][3], 2> = 0
extent<int[], 0>     = 0
```

## ゲームでの使いどころ

配列の大きさを型から取り出す、テンプレートの部品として使います。通常のコードでは `std::size(array)` や `std::ssize` のほうが簡単です。

## よくあるミス

??? failure "範囲外の次元を渡して 0 が返る"
    次元の範囲を `rank_v` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rank`](rank.md) | 次元数 |
| [`remove_extent`](remove_extent.md) | 次元を外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `extent_v<T, N>` は `N` 番目の次元の要素数
    - [x] 範囲外・配列でない・要素数不明は 0
    - [x] 普通は `std::size` で足りる

## 関連ページ

- [cpprefjp: std::extent](https://cpprefjp.github.io/reference/type_traits/extent.html)
- [cppreference: std::extent](https://en.cppreference.com/w/cpp/types/extent)
