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

`basic_format_arg` は型を消しているため、中身を取り出すには、`std::visit` と同じように、型ごとの処理を渡します。引数を処理する関数に全ての型（`int`・`string_view`・`handle` など）に対応するジェネリックなラムダを渡します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::visit_format_arg {#visit_format_arg}

```cpp
template <class Visitor, class Context>
decltype(auto) visit_format_arg(Visitor&& vis, basic_format_arg<Context> arg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `vis` | 関数 | 型ごとに呼ばれる関数 |
| `arg` | basic_format_arg | 取り出す引数 |

- 戻り値: `vis` の戻り値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <type_traits>

int main() {
  int v = 42;
  auto args = std::make_format_args(v);
  std::format_args fa = args;
  std::visit_format_arg([](auto&& x) {
    if constexpr (std::is_same_v<std::remove_cvref_t<decltype(x)>, int>) {
      std::println("int {}", x);
    } else {
      std::println("other");
    }
  }, fa.get(0));
}
```

```text title="実行結果"
int 42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のフォーマッタで、引数の型に応じて処理する |

## よくあるミス

??? failure "一部の型だけに対応する"
    全ての型（`monostate`・`handle` を含む）に対応しないと、コンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_format_arg`](basic_format_arg.md) | 引数 1 つ |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式化の引数 1 つの中身を型に応じて取り出す
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::visit_format_arg](https://cpprefjp.github.io/reference/format/visit_format_arg.html)
- [cppreference: std::visit_format_arg](https://en.cppreference.com/w/cpp/utility/format/visit_format_arg)
