---
title: std::begin
summary: "先頭と終端のイテレータを返す（配列にも使える）。"
order: 9
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::begin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::begin(c)` と `std::end(c)` は、**先頭と終わりのイテレータを返す**関数です。`c.begin()` / `c.end()` と同じですが、**生の配列にも使える**のが利点です。範囲 for の内部でも使われています。

!!! tip "ポイント"
    - テンプレートで、コンテナも配列も同じ書き方で扱える。
    - C++20 の ranges には `std::ranges::begin` がある。
    - 普段は `c.begin()` で足りる。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::begin {#begin}

```cpp
template <class C>
constexpr auto begin(C& c) -> decltype(c.begin());
template <class T, std::size_t N>
constexpr T* begin(T (&array)[N]) noexcept;
```

- C の配列でもコンテナでも先頭を返します。テンプレートで「何でも受け取る」関数を書くときに使います

### std::end {#end}

```cpp
template <class C>
constexpr auto end(C& c) -> decltype(c.end());
```

- 同じく終わりを返します

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  int a[] = {10, 20, 30};
  std::println("{} {}", *std::begin(a), std::end(a) - std::begin(a));
}
```

```text title="実行結果"
10 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列を std::sort に渡す | `std::sort(std::begin(a), std::end(a))` |

## よくあるミス

??? failure "ポインターに変換された配列に使う"
    大きさが分からずコンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](../../algorithms/sort.md) | 範囲をそのまま渡せる |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭と終端のイテレータ
    - [x] 配列にも使える
    - [x] ranges では範囲を渡せば不要

## 関連ページ

- [cpprefjp: std::begin / std::end](https://cpprefjp.github.io/reference/iterator/begin.html)
- [cppreference: std::begin / std::end](https://en.cppreference.com/w/cpp/iterator/begin)
