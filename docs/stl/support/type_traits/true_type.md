---
title: std::true_type
summary: "`true` を表すコンパイル時の定数の型。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::true_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型の性質を調べる `is_xxx` は、結果を `true` か `false` の値で返すだけでなく、<strong>型としても</strong>返します。`std::true_type` は、「真」を表すその型です。`std::integral_constant<bool, true>` の別名です。

!!! tip "ポイント"
    - `std::true_type::value` は `true`
    - `std::integral_constant<bool, true>` の別名
    - `is_integral<int>` などは `true_type` を継承する
    - 自作のトレイトの結果を表すときに継承して使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::true_type {#true_type}

<span class="ver ver-11">C++11</span>

```cpp
using true_type = integral_constant<bool, true>;
```

`std::true_type` は、`value` が `true` の型です。標準のトレイトは、結果が真なら `true_type` を、偽なら `false_type` を継承します。そのため、`std::is_integral<int>{}` は `true_type` として扱えます。

自作のトレイトを書くときは、条件に当てはまる場合に `std::true_type` を継承する特殊化を書き、既定を `std::false_type` にするのが定石です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

// 自作のトレイト: T が int か
template <class T> struct IsInt : std::false_type {};
template <> struct IsInt<int> : std::true_type {};

int main() {
  std::println("IsInt<int>   = {}", IsInt<int>::value);
  std::println("IsInt<float> = {}", IsInt<float>::value);
  std::println("true_type::value = {}", std::true_type::value);
}
```

```text title="実行結果"
IsInt<int>   = true
IsInt<float> = false
true_type::value = true
```

## ゲームでの使いどころ

自作のトレイトの結果を表します（上のコード）。標準のトレイトと同じ使い方（`::value`、`_v`）ができます。

## よくあるミス

??? failure "`true_type` と `bool` の `true` を混同する"
    `true_type` は型です。値は `::value` で取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`false_type`](false_type.md) | 偽を表す型 |
| [`integral_constant`](integral_constant.md) | 定数を包む型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::true_type` は「真」を表す型
    - [x] 標準のトレイトは、結果で `true_type` / `false_type` を継承する
    - [x] 自作のトレイトでも、この 2 つを継承して書く

## 関連ページ

- [cpprefjp: std::true_type](https://cpprefjp.github.io/reference/type_traits/true_type.html)
- [cppreference: std::true_type](https://en.cppreference.com/w/cpp/types/integral_constant)
