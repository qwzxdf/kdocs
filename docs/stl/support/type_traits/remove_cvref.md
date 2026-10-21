---
title: std::remove_cvref
summary: "`const`・`volatile`・参照をすべて外した型にする。"
order: 14
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_cvref

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

`std::remove_cvref_t<T>` は、**型 T から `const`、`volatile`、参照を全部外した型**を返します。テンプレートで受け取った引数の型が、`const int&` や `int&&` など様々な形をとるときに、「素の型」に直して比べるために使います。

!!! tip "ポイント"
    - `is_same_v<remove_cvref_t<T>, int>` の形が定番。
    - C++20 の機能。それ以前は `decay_t` で代用。
    - ポインターの指す先の `const` は外れない。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::remove_cvref_t {#remove_cvref}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
using remove_cvref_t = /* const・volatile・参照を取り除いた T */;
```

- `const std::string&` → `std::string`。テンプレートで受け取った型を「素の型」にして比べるのに使います

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::remove_cvref_t<const int&>, int>, std::is_same_v<std::remove_cvref_t<int&&>, int>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 転送参照で受けた型を、素の型に直す | `std::remove_cvref_t<T>` |

## よくあるミス

??? failure "decay と混同する"
    `decay_t` は配列や関数をポインターに変えるので、結果が違うことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`decay`](decay.md) | 配列・関数もポインターに |
| [`is_same`](is_same.md) | 型の比較 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] const / volatile / 参照を外す
    - [x] `is_same` の前に使う
    - [x] C++20

## 関連ページ

- [cpprefjp: std::remove_cvref](https://cpprefjp.github.io/reference/type_traits/remove_cvref.html)
- [cppreference: std::remove_cvref](https://en.cppreference.com/w/cpp/types/remove_cvref)
