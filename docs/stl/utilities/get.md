---
title: std::get
summary: "pair / tuple / array / variant の N 番目（または型で）の要素を取り出す。"
order: 50
tags:
  - ユーティリティ
---

# std::get

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`pair` や `tuple` は、中身に名前がありません。`first`、`second` か、番号で取り出します。`std::get<0>(t)` のように書くと、`tuple` の最初の要素を取り出せます。番号を実行時に変えることはできません。番号は、コンパイル時に決まっている必要があります。`variant` に使うと、いま入っている型の値を取り出せます。

!!! tip "ポイント"
    - `std::get<N>(x)` で N 番目（0 始まり）。型が 1 つだけなら `std::get<T>(x)` で型指定もできる。
    - 番号は**コンパイル時の定数**。実行時の変数は使えない。
    - variant に使うと、違う型が入っているとき `std::bad_variant_access` を投げる。

!!! info "このページを読む前に"
    [`std::pair`](pair.md)、[`std::tuple`](tuple.md)、[`std::variant`](variant.md) の中身の持ち方を先に読んでください。`get` は、その中身を取り出す関数です。

## 関数の詳しい説明

### std::get {#get}

```cpp
template <std::size_t I, class... Types>
constexpr auto& get(std::tuple<Types...>& t) noexcept;

template <class T, class... Types>
constexpr T& get(std::tuple<Types...>& t) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `I` | 何番目か（0 始まり、コンパイル時の定数） |
| `T` | 型で指定（その型が 1 つだけのときに使える） |

```cpp
#include <print>
#include <string>
#include <tuple>

int main() {
  std::tuple<std::string, int, float> enemy = {"スライム", 10, 1.5f};
  std::println("{} {} {}", std::get<0>(enemy), std::get<int>(enemy), std::get<2>(enemy));
}
```

```text title="実行結果"
スライム 10 1.5
```

## ゲームでの使いどころ

`pair` と `tuple` の要素を取り出すのが基本ですが、実際には構造化束縛 `auto [a, b] = t;` のほうが読みやすいので、`get` を直接書く場面は少なめです。

テンプレートの中で、番号を引数にして要素を順に処理するときには、`get<I>` が必要です。`apply` や `visit` が内部で使っています。

`variant` から値を取り出すときは、`get_if` のほうが安全です。`get<T>(v)` は、違う型が入っていると `bad_variant_access` の例外を投げます。型が確実に分かっているときにだけ使います。

## よくあるミス

??? failure "番号に実行時の変数を使う"
    `std::get<i>(t)` の `i` は、コンパイル時の定数でなければなりません。`for` ループの変数は使えません。ループで順に処理したいなら、`std::apply` を使います。

??? failure "同じ型が 2 つ以上ある `tuple` で、型指定の `get` を使う"
    `std::get<int>(t)` は、`tuple<int, int>` では曖昧でコンパイルエラーです。番号で指定します。

??? failure "`variant` の違う型に `get` して、例外で落ちる"
    `std::get<float>(v)` で、`v` が `int` を持っていると `bad_variant_access` です。型が不確かなら、`get_if` か `holds_alternative` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| 構造化束縛 `auto [a, b] = t;` | 名前が付く。こちらが読みやすい |
| [`std::get_if`](get_if.md) | variant 用。例外を投げず、ポインターで返す |
| [`std::visit`](visit.md) | variant の型ごとに処理を書き分ける |

## コンパイラ対応

C++11 から使えます。型指定の `get<T>` は C++14 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::get<N>(x)` で N 番目、`std::get<T>(x)` で型指定。
    - [x] 番号はコンパイル時の定数。
    - [x] `variant` で型が違うと例外。確かめるなら `get_if`。

## 関連ページ

- [cpprefjp: std::get (tuple)](https://cpprefjp.github.io/reference/tuple/tuple/get.html)
- [cppreference: std::get](https://en.cppreference.com/w/cpp/utility/tuple/get)
