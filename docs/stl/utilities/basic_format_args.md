---
title: std::basic_format_args
summary: "書式化の引数のリストを表す型。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_format_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::vformat` が受け取る `std::format_args` は、`std::basic_format_args<format_context>` の別名で、複数の引数をまとめて見るための型です。`make_format_args` が作った引数の集まりを参照し、`get(i)` で i 番目の引数を取り出せます。

!!! tip "ポイント"
    - `format_args` は `basic_format_args<format_context>` の別名
    - `wformat_args` が `wchar_t` 版
    - `get(i)` で、i 番目の引数を `basic_format_arg` として取り出す
    - 参照を持つだけの軽い型。コピーしてもよい

!!! info "このページを読む前に"
    [`std::make_format_args`](make_format_args.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_args {#basic_format_args}

<span class="ver ver-20">C++20</span>

```cpp
template <class Context>
class basic_format_args {
 public:
  template <class... Args>
  basic_format_args(const format_arg_store<Context, Args...>& store) noexcept;
  basic_format_arg<Context> get(std::size_t i) const noexcept;
};
```

`format_arg_store` から暗黙に変換できるので、`vformat(fmt, std::make_format_args(a, b))` と、そのまま渡せます。

`get(i)` は、i 番目の引数を返します。範囲外の番号を渡すと、空の `basic_format_arg`（`static_cast<bool>` が偽）が返ります。

自作の `formatter` の中で、書式の中の幅などを、別の引数から取るために、`ctx.arg(i)` として使われています。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int a = 1;
  double b = 2.5;
  auto store = std::make_format_args(a, b);
  std::format_args args = store;

  std::println("0 番目がある: {}", static_cast<bool>(args.get(0)));
  std::println("1 番目がある: {}", static_cast<bool>(args.get(1)));
  std::println("2 番目がある: {}", static_cast<bool>(args.get(2)));
}
```

```text title="実行結果"
0 番目がある: true
1 番目がある: true
2 番目がある: false
```

## ゲームでの使いどころ

自作のログ関数が、`std::format_args` を受け取って、`vformat` に渡す形にすると、`std::format` の包み方がきれいに書けます。

## よくあるミス

??? failure "format_arg_store が消えた後に使う"
    引数の集まりは、参照を持ちます。元の変数が消えると、使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_format_arg`](basic_format_arg.md) | 引数 1 つぶん |
| [`make_format_args`](make_format_args.md) | これを作る |
| [`vformat`](vformat.md) | これを受け取る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::basic_format_args](https://cpprefjp.github.io/reference/format/basic_format_args.html)
- [cppreference: std::basic_format_args](https://en.cppreference.com/w/cpp/utility/format/basic_format_args)
