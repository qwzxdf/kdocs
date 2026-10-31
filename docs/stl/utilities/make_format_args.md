---
title: std::make_format_args
summary: "引数を、書式化用の引数リストにまとめる。"
order: 900
tags:
  - ユーティリティ
---

# std::make_format_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::vformat` に渡す引数を、1 つの値にまとめる関数が `std::make_format_args` です。引数への参照を持つオブジェクト（`format_arg_store`）を返し、`std::format_args` として `vformat` に渡せます。

!!! tip "ポイント"
    - 引数は左辺値の変数。C++23 以降は右辺値を渡すとコンパイル エラー
    - 返したオブジェクトは参照を持つ。変数が消えると、ぶら下がる
    - `wchar_t` の書式には `make_wformat_args`
    - 普段は `std::format` に直接引数を渡す

!!! info "このページを読む前に"
    [`std::vformat`](vformat.md) を先に読んでください。

## 関数の詳しい説明

### std::make_format_args {#make_format_args}

<span class="ver ver-20">C++20</span>

```cpp
template <class Context = std::format_context, class... Args>
/* format_arg_store */ make_format_args(Args&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 左辺値（可変個） | 書式の引数 |

引数の値そのものではなく、参照を保存します。そのため、返したオブジェクトは、引数の変数が生きている間だけ有効です。

C++20 では、`const Args&...` を取りましたが、一時オブジェクトを渡すと危険なため、C++23（の欠陥報告）で `Args&...` に変更されました。`make_format_args(5)` と書くと、コンパイル エラーです。

返ったオブジェクトは、`std::format_args` に暗黙に変換されて、`vformat` や `vformat_to` に渡せます。ログ関数など、可変個の引数を転送する関数で使います。

```cpp
template <class... Args>
void Log(std::string_view fmt, Args&&... args) {
  std::string s = std::vformat(fmt, std::make_format_args(args...));
}
```

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  int hp = 30;
  std::string name = "Hero";

  // 変数を並べて包み、vformat に渡す
  std::println("{}", std::vformat("{}: HP {}", std::make_format_args(name, hp)));

  // 同じ引数を、別の書式で再利用できる
  auto args = std::make_format_args(name, hp);
  std::println("{}", std::vformat("[{}] {}", args));
}
```

```text title="実行結果"
Hero: HP 30
[Hero] 30
```

## ゲームでの使いどころ

可変個の引数を受け取る、自作のログ関数で、実行時の書式に整形するときに使います。

## よくあるミス

??? failure "一時オブジェクトを渡す"
    `make_format_args(5)` は、C++23 でコンパイルできません。変数に入れます。

??? failure "返したオブジェクトを、変数のスコープ外で使う"
    参照がぶら下がります。同じスコープ内で使い切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_wformat_args`](make_wformat_args.md) | `wchar_t` 版 |
| [`vformat`](vformat.md) | これを受け取る |
| [`basic_format_args`](basic_format_args.md) | 受け取る側の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::make_format_args](https://cpprefjp.github.io/reference/format/make_format_args.html)
- [cppreference: std::make_format_args](https://en.cppreference.com/w/cpp/utility/format/make_format_args)
