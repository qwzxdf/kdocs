---
title: std::size
summary: "コンテナや配列の要素数を返す（配列にも使える）。"
order: 5
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::size

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <iterator>`
</div>

`std::size(c)` は、**コンテナや配列の要素数を返す**関数です。`c.size()` と同じですが、**生の配列（`int a[5]`）にも使える**のが利点です。`size()` は符号なし（`size_t`）で返します。

!!! tip "ポイント"
    - 生の配列では `sizeof(a) / sizeof(a[0])` の代わりに。
    - 符号つきが欲しければ [`ssize`](ssize.md)。
    - ポインターに変換された配列には使えない。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::size {#size}

<span class="ver ver-17">C++17</span>

```cpp
template <class C>
constexpr auto size(const C& c) -> decltype(c.size());
template <class T, std::size_t N>
constexpr std::size_t size(const T (&array)[N]) noexcept;
```

- C の配列でもコンテナでも要素数を返します。`sizeof(a) / sizeof(a[0])` の代わり

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  int a[5] = {};
  std::vector<int> v = {1, 2, 3};
  std::println("{} {}", std::size(a), std::size(v));
}
```

```text title="実行結果"
5 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列の要素数 | `std::size(table)` |

## よくあるミス

??? failure "関数に渡して配列がポインターになる"
    `void f(int a[])` の `std::size(a)` はコンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ssize`](ssize.md) | 符号つき |
| [`empty`](empty.md) | 空か |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数
    - [x] 生の配列にも使える
    - [x] 符号なしで返る

## 関連ページ

- [cpprefjp: std::size](https://cpprefjp.github.io/reference/iterator/size.html)
- [cppreference: std::size](https://en.cppreference.com/w/cpp/iterator/size)
