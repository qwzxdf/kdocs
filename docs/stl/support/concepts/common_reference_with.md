---
title: std::common_reference_with
summary: "2 つの型が、共通の参照型を持つことを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::common_reference_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

型の違う 2 つの値を、参照のまま混ぜたいときがあります（`cond ? a : b` が参照を返す）。`std::common_reference_with<T, U>` は、`T` と `U` に、共通の参照の型があることを表します。`common_with` の参照版です。

!!! tip "ポイント"
    - `std::common_reference_t<T, U>` が存在する
    - `T` と `U` の両方が、その参照の型へ変換できる
    - `int&` と `const int&` は、`const int&` が共通
    - プロキシ参照（`vector<bool>` の要素）の扱いのために作られた

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::common_reference_with {#common_reference_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
concept common_reference_with = std::same_as<std::common_reference_t<T, U>, std::common_reference_t<U, T>>
    && std::convertible_to<T, std::common_reference_t<T, U>>
    && std::convertible_to<U, std::common_reference_t<T, U>>;
```

満たすべき条件は、次のとおりです。

- `std::common_reference_t<T, U>` と `std::common_reference_t<U, T>` が同じ型
- `T` と `U` の両方が、その型へ変換できる

`vector<bool>` の `reference` は、実際の参照ではない、プロキシ型です。`bool&` と、このプロキシ型の共通の参照は、特別な定義がなければ存在しません。範囲ライブラリは、`common_reference` を使うことで、プロキシ参照を持つイテレータも扱えるようにしています。

自作のプロキシ型を、範囲ライブラリに対応させるには、`std::basic_common_reference` を特殊化します。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <sstream>
#include <vector>
#include <algorithm>
#include <memory>
#include <string>

int main() {
  std::println("int& と const int&: {}", std::common_reference_with<int&, const int&>);
  std::println("int& と long&: {}", std::common_reference_with<int&, long&>);
  std::println("int& と string&: {}", std::common_reference_with<int&, std::string&>);

  using R = std::common_reference_t<int&, const int&>;
  std::println("共通は const int&: {}", std::is_same_v<R, const int&>);
}
```

```text title="実行結果"
int& と const int&: true
int& と long&: true
int& と string&: false
共通は const int&: true
```

## ゲームでの使いどころ

範囲ライブラリのプロキシ参照に対応した、自作のイテレータを書くときに関わります。

## よくあるミス

??? failure "プロキシ型に共通の参照を用意しない"
    範囲ライブラリで使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`common_with`](common_with.md) | 値の共通の型 |
| [`convertible_to`](convertible_to.md) | 変換できる |
| [`indirectly_readable`](indirectly_readable.md) | 内部でこれを使う |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::common_reference_with](https://cpprefjp.github.io/reference/concepts/common_reference_with.html)
- [cppreference: std::common_reference_with](https://en.cppreference.com/w/cpp/concepts/common_reference_with)
