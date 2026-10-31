---
title: std::tuple_cat
summary: "複数の tuple を連結して、1 つの tuple にする。"
order: 56
tags:
  - ユーティリティ
---

# std::tuple_cat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

2 つの `tuple` を、1 つにつなげたい。`std::tuple_cat(t1, t2)` は、複数の `tuple`（や `pair`、`array`）の要素を、順番に並べた 1 つの新しい `tuple` を返します。文字列の連結（`+`）の `tuple` 版です。

!!! tip "ポイント"
    - 渡した `tuple` の要素を、順に連結した新しい `tuple` を返す
    - `pair` や `std::array` も渡せる
    - 要素の型は、コピーされた型のまま。結果の型は引数の型から決まる
    - 3 つ以上でもよい。`tuple_cat(a, b, c)`

!!! info "このページを読む前に"
    [`std::make_tuple`](make_tuple.md) を先に読んでください。

## 関数の詳しい説明

### std::tuple_cat {#tuple_cat}

<span class="ver ver-11">C++11</span>

```cpp
template <class... Tuples>
constexpr std::tuple<CTypes...> tuple_cat(Tuples&&... tpls);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tpls` | `tuple` / `pair` / `array`（可変個） | つなげる対象 |

戻り値の型は、引数の要素の型を全部並べたものです。`tuple<int, float>` と `tuple<char>` をつなげると、`tuple<int, float, char>` です。

引数が左辺値なら、要素はコピーされ、右辺値ならムーブされます。参照の要素を持つ `tuple` を渡すと、結果にも参照の要素が入ります。

要素の個数と型は、コンパイル時に決まるので、結果を `auto` で受け、構造化束縛で取り出せます。

## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <string>
#include <tuple>

int main() {
  const auto a = std::make_tuple(1, 2.5);
  const auto b = std::make_tuple(std::string("Hero"));

  // 2 つをつなげる
  const auto ab = std::tuple_cat(a, b);
  static_assert(std::tuple_size_v<decltype(ab)> == 3);
  std::println("{} {} {}", std::get<0>(ab), std::get<1>(ab), std::get<2>(ab));

  // pair と array もつなげられる
  const auto c = std::tuple_cat(std::make_pair(1, 2), std::array<int, 2>{3, 4});
  std::println("要素数: {}", std::tuple_size_v<decltype(c)>);
}
```

```text title="実行結果"
1 2.5 Hero
要素数: 4
```

## ゲームでの使いどころ

可変引数テンプレートで、複数の `tuple` に分けて持ったパラメーターを、1 つにまとめて関数に渡す（`std::apply` と組み合わせる）ときに使います。

## よくあるミス

??? failure "結果の型を自分で書こうとする"
    型は長くなります。`auto` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::apply`](apply.md) | `tuple` を引数に展開して呼ぶ |
| [`std::make_tuple`](make_tuple.md) | 値から `tuple` を作る |
| `std::tuple_size_v` | 要素数を調べる |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::tuple_cat](https://cpprefjp.github.io/reference/tuple/tuple_cat.html)
- [cppreference: std::tuple_cat](https://en.cppreference.com/w/cpp/utility/tuple/tuple_cat)
