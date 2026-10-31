---
title: std::add_volatile
summary: "`volatile` を付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_volatile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型に `volatile` を付けたい。`std::add_volatile` は、<strong>型に `volatile` を付けた型</strong>を返します。

!!! tip "ポイント"
    - `std::add_volatile_t<int>` は `volatile int`
    - すでに付いていればそのまま
    - 参照には変化しない
    - ゲームでは使う場面が少ない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_volatile_t {#add_volatile}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using add_volatile_t = typename add_volatile<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `volatile int` を返します。すでに `volatile` ならそのままで、参照には変化しません。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::add_volatile<T>::type` と書いても同じ型ですが、C++14 以降の `std::add_volatile_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::add_volatile_t<int> は volatile int : {}", std::is_same_v<std::add_volatile_t<int>, volatile int>);
  std::println("std::add_volatile_t<volatile int> は volatile int : {}", std::is_same_v<std::add_volatile_t<volatile int>, volatile int>);
}
```

```text title="実行結果"
std::add_volatile_t<int> は volatile int : true
std::add_volatile_t<volatile int> は volatile int : true
```

## ゲームでの使いどころ

`volatile` を付けた型を作ります。ハードウェアのレジスタなど、読み書きを省略させたくないメモリを指す型を作るときに出てきます。

```cpp
template <class T>
using Register = std::add_volatile_t<T>;

static_assert(std::is_same_v<Register<std::uint32_t>, volatile std::uint32_t>);
```

## よくあるミス

??? failure "スレッド間の同期に volatile を使う"
    `volatile` はスレッド間の同期になりません。`std::atomic` を使います。

??? failure "参照型に使って付くと思う"
    `std::add_volatile_t<int&>` は `int&` のままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_volatile`](remove_volatile.md) | `volatile` を外す |
| [`add_cv`](add_cv.md) | `const` と `volatile` を付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::add_volatile_t<int>` は `volatile int`
    - [x] すでに付いていればそのまま
    - [x] 参照には変化しない

## 関連ページ

- [cpprefjp: std::add_volatile](https://cpprefjp.github.io/reference/type_traits/add_volatile.html)
- [cppreference: std::add_volatile](https://en.cppreference.com/w/cpp/types/add_volatile)
