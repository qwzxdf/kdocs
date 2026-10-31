---
title: std::add_cv
summary: "`const volatile` を付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_cv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型に `const` と `volatile` を両方付けたい。`std::add_cv` は、<strong>`const volatile` を付けた型</strong>を返します。

!!! tip "ポイント"
    - `std::add_cv_t<int>` は `const volatile int`
    - 重複しない
    - 参照には変化しない
    - ゲームではほぼ使わない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_cv_t {#add_cv}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using add_cv_t = typename add_cv<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `const volatile int` を返します。すでに付いている修飾は重複せず、参照には変化しません。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::add_cv<T>::type` と書いても同じ型ですが、C++14 以降の `std::add_cv_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::add_cv_t<int> は const volatile int : {}", std::is_same_v<std::add_cv_t<int>, const volatile int>);
  std::println("std::add_cv_t<const int> は const volatile int : {}", std::is_same_v<std::add_cv_t<const int>, const volatile int>);
}
```

```text title="実行結果"
std::add_cv_t<int> は const volatile int : true
std::add_cv_t<const int> は const volatile int : true
```

## ゲームでの使いどころ

`const` と `volatile` を同時に付けた型を作ります。メモリ マップド I/O のレジスタを指す型を、読み取り専用の volatile にするような、低レベルの場面に出てきます。

```cpp
template <class T>
using RegisterRef = std::add_cv_t<T>&;   // const volatile な参照

static_assert(std::is_same_v<std::add_cv_t<std::uint32_t>, const volatile std::uint32_t>);
```

## よくあるミス

??? failure "volatile を付けたくないのに使う"
    `add_cv` は、`const` と `volatile` を両方付けます。`const` だけなら `add_const` を使います。

??? failure "参照型に使って付くと思う"
    `std::add_cv_t<int&>` は、`int&` のままです。参照には `const` も `volatile` も付けられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cv`](remove_cv.md) | 両方を外す |
| [`add_const`](add_const.md) | `const` だけ付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::add_cv_t<int>` は `const volatile int`
    - [x] 重複しない
    - [x] 参照には変化しない

## 関連ページ

- [cpprefjp: std::add_cv](https://cpprefjp.github.io/reference/type_traits/add_cv.html)
- [cppreference: std::add_cv](https://en.cppreference.com/w/cpp/types/add_cv)
