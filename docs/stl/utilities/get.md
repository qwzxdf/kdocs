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

`std::get` は、**pair・tuple・array・variant の中身を、番号（または型）を指定して取り出す**関数です。番号はコンパイル時の定数で、`std::get<0>(t)` のように書きます。構造化束縛が使える場面では、そちらのほうが読みやすいです。

!!! tip "ポイント"
    - `std::get<N>(x)` で N 番目（0 始まり）。型が 1 つだけなら `std::get<T>(x)` で型指定もできる。
    - 番号は**コンパイル時の定数**。実行時の変数は使えない。
    - variant に使うと、違う型が入っているとき `std::bad_variant_access` を投げる。

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

| 場面 | 書き方 |
| --- | --- |
| tuple の特定の要素だけ取り出す | `std::get<2>(enemy)` |
| variant の中身を、型を指定して取り出す | `std::get<int>(v)`（違うと例外） |

## よくあるミス

??? failure "番号に変数を使う"
    `std::get<i>(t)` の `i` は定数でなければなりません。実行時に選びたいなら、`std::array` や `std::vector` を使います。

??? failure "variant で型が違う"
    `std::get<int>(v)` は、`v` が `int` でないと例外です。安全に調べるなら [`std::get_if`](get_if.md)。

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
    - [x] `std::get<N>(x)` で N 番目を取り出す
    - [x] 番号は定数
    - [x] variant では型違いで例外

## 関連ページ

- [cpprefjp: std::get (tuple)](https://cpprefjp.github.io/reference/tuple/tuple/get.html)
- [cppreference: std::get](https://en.cppreference.com/w/cpp/utility/tuple/get)
