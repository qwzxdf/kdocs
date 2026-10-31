---
title: std::visit_format_arg
summary: "書式化の引数 1 つの中身を、型に応じて取り出す。"
order: 900
tags:
  - ユーティリティ
---

# std::visit_format_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`basic_format_arg` は整数や文字列などさまざまな型の値を 1 つの型で持っているので、中身を取り出すには型に応じた処理が要ります。`std::visit_format_arg(visitor, arg)` は `arg` の中身の実際の型の値を `visitor` に渡して呼び出します。`std::visit` の書式引数版です。

!!! tip "ポイント"
    - `visitor` は `int`、`double`、`string_view` など複数の型を受け取れる呼び出し可能なもの
    - 総称ラムダ（`[](auto v) {...}`）と `if constexpr` で書き分けるのが定番
    - 自作の型は `basic_format_arg::handle` として渡される
    - 自作の `formatter` で幅などを別の引数から読むときに使う

!!! info "このページを読む前に"
    [`std::basic_format_arg`](basic_format_arg.md) を先に読んでください。

## 関数の詳しい説明

### std::visit_format_arg {#visit_format_arg}

<span class="ver ver-20">C++20</span>

```cpp
template <class Visitor, class Context>
decltype(auto) visit_format_arg(Visitor&& vis, std::basic_format_arg<Context> arg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `vis` | 呼び出し可能なもの | 中身の値を受け取る関数 |
| `arg` | `basic_format_arg` | 取り出す対象の引数 |

`arg` の中身が `int` なら `vis(int)`、`double` なら `vis(double)` のように型に応じて呼び出します。`visitor` は保存されうるすべての型を受け取れなければなりません。総称ラムダで受け `if constexpr` で型ごとに分けると、簡潔に書けます。

内部の保存の型は `bool`、`char`、`int`、`unsigned`、`long long`、`unsigned long long`、`float`、`double`、`long double`、`const char*`、`string_view`、`const void*`、`nullptr_t`、`handle` です。たとえば `short` で渡した値は `int` として、`std::string` で渡した値は `string_view` として届きます。

C++26 では `basic_format_arg::visit` というメンバー関数に置き換えられこの関数は非推奨になる予定です。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>
#include <string_view>
#include <type_traits>

// 型に応じた説明を返す
std::string Describe(std::format_args args, std::size_t i) {
  return std::visit_format_arg(
      [](auto v) -> std::string {
        using T = decltype(v);
        if constexpr (std::is_same_v<T, int>) return "int";
        else if constexpr (std::is_same_v<T, double>) return "double";
        else if constexpr (std::is_same_v<T, std::string_view>) return "string_view";
        else return "その他";
      },
      args.get(i));
}

int main() {
  int a = 1;
  double b = 2.5;
  std::string c = "Hero";
  short d = 3;

  auto store = std::make_format_args(a, b, c, d);
  std::format_args args = store;
  for (std::size_t i = 0; i < 4; ++i) {
    std::println("{} 番目: {}", i, Describe(args, i));
  }
}
```

```text title="実行結果"
0 番目: int
1 番目: double
2 番目: string_view
3 番目: int
```

`short` が `int` に `std::string` が `string_view` になっています。

## ゲームでの使いどころ

自作の `formatter` が `{:{}}` のように幅を別の引数で受け取る設計にするときだけ使います。

## よくあるミス

??? failure "すべての型を受け取れない visitor を渡す"
    `int` だけ受け取るラムダは他の型でコンパイルできません。総称ラムダにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_format_arg`](basic_format_arg.md) | 取り出す対象 |
| `std::visit` | `variant` 用の同様の関数 |
| [`formatter`](formatter.md) | 自作の書式化 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::visit_format_arg](https://cpprefjp.github.io/reference/format/visit_format_arg.html)
- [cppreference: std::visit_format_arg](https://en.cppreference.com/w/cpp/utility/format/visit_format_arg)
