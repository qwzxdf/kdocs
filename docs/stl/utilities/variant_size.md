---
title: std::variant_size
summary: "variant が持てる型の数をコンパイル時に取り出す。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::variant<int, float, std::string>` には、いくつの型が入りうるか。コンパイル時にそれを知りたいときに使うのが `std::variant_size_v<V>` です。`tuple_size` の `variant` 版で、型の個数を定数として返します。

!!! tip "ポイント"
    - `std::variant_size_v<V>` は、`V` の選択肢の数
    - コンパイル時の定数
    - 実行時の番号は `0` 〜 `size - 1`。これと `variant_npos` が `index()` の取りうる値
    - `const` や `volatile` が付いた型にも使える

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_size {#variant_size}

<span class="ver ver-17">C++17</span>

```cpp
template <class Variant> struct variant_size;
template <class Variant> inline constexpr std::size_t variant_size_v = variant_size<Variant>::value;
```

`std::variant<A, B, C>` なら 3 です。同じ型が複数回現れても、その分も数えます。`std::variant<int, int>` は 2 です。

`std::monostate` も 1 つの選択肢として数えます。`std::variant<std::monostate, int>` は 2 です。

テンプレートの中で、`variant` の全選択肢について、順に処理する（再帰やパラメーター パックの展開）とき、個数が要ります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  using V = std::variant<int, float, std::string>;
  static_assert(std::variant_size_v<V> == 3);

  std::println("V: {}", std::variant_size_v<V>);
  std::println("monostate つき: {}", std::variant_size_v<std::variant<std::monostate, int>>);
  std::println("同じ型を 2 回: {}", std::variant_size_v<std::variant<int, int>>);

  // index() の取りうる範囲は 0 〜 size - 1
  V v = 1.5f;
  std::println("index {} は範囲内: {}", v.index(), v.index() < std::variant_size_v<V>);
}
```

```text title="実行結果"
V: 3
monostate つき: 2
同じ型を 2 回: 2
index 1 は範囲内: true
```

## ゲームでの使いどころ

イベントを `variant` にまとめたとき、各イベント型に対するハンドラーの配列を、型の個数ぶん用意する、といった場面で使います。

## よくあるミス

??? failure "variant の値に使う"
    型を渡します。`decltype(v)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant_alternative`](variant_alternative.md) | 番号から型を取り出す |
| [`std::tuple_size`](tuple_size.md) | `tuple` の要素数 |
| [`std::variant_npos`](variant_npos.md) | 値なしの番号 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::variant_size](https://cpprefjp.github.io/reference/variant/variant_size.html)
- [cppreference: std::variant_size](https://en.cppreference.com/w/cpp/utility/variant/variant_size)
