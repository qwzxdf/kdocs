---
title: std::basic_format_arg
summary: "書式化の引数 1 つぶんを表す型。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_format_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format` に渡された 1 つの引数を型に関係なく扱うための型が `std::basic_format_arg` です。整数、小数、文字列、ポインタ、自作の型のいずれもこの型の値として、一様に持てます。`basic_format_args::get(i)` が返す型で `visit_format_arg` で中身を取り出します。

!!! tip "ポイント"
    - 型をそろえた引数 1 つぶんの入れ物
    - `explicit operator bool` で有効な引数か（空でないか）を調べる
    - 中身の取り出しは `std::visit_format_arg`
    - 自作の `formatter` の実装に近い所で使う

!!! info "このページを読む前に"
    [`std::basic_format_args`](basic_format_args.md) と [`std::visit_format_arg`](visit_format_arg.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_arg {#basic_format_arg}

<span class="ver ver-20">C++20</span>

```cpp
template <class Context>
class basic_format_arg {
 public:
  basic_format_arg() noexcept;
  explicit operator bool() const noexcept;
};
```

内部では引数の型に応じた値を `std::variant` に近い形で持っています。保存する型は `bool`、`char`、`int`、`unsigned`、`long long`、`unsigned long long`、`float`、`double`、`long double`、`const char*`、`string_view`、`const void*`、そして自作の型の `handle` です。

整数型は `int` や `long long` に統合されます。たとえば `short` は `int` として保存されます。`std::string` は `string_view` になります。

既定のコンストラクターで作ると、空の引数です。`static_cast<bool>(arg)` が偽になります。

自作の `formatter` の `format` 関数が幅や精度を別の引数から取る（`{:{}}`）とき `ctx.arg(n)` で `basic_format_arg` を取得して、`visit_format_arg` で整数として読み取ります。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  int v = 42;
  std::string s = "Hero";
  auto store = std::make_format_args(v, s);
  std::format_args args = store;

  const auto a0 = args.get(0);
  const auto a1 = args.get(1);
  const auto a9 = args.get(9);  // 範囲外: 空の引数

  std::println("0: {}", static_cast<bool>(a0));
  std::println("1: {}", static_cast<bool>(a1));
  std::println("9: {}", static_cast<bool>(a9));
}
```

```text title="実行結果"
0: true
1: true
9: false
```

## ゲームでの使いどころ

自作の `formatter` を幅や精度を引数から受け取る形（`{:{}}`）にするときだけ触れます。

## よくあるミス

??? failure "空の引数を取り出す"
    範囲外の番号の `get` は空の引数を返します。`static_cast<bool>` で確かめてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_format_args`](basic_format_args.md) | 引数の集まり |
| [`visit_format_arg`](visit_format_arg.md) | 中身を取り出す |
| [`formatter`](formatter.md) | 自作の書式化 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::basic_format_arg](https://cpprefjp.github.io/reference/format/basic_format_arg.html)
- [cppreference: std::basic_format_arg](https://en.cppreference.com/w/cpp/utility/format/basic_format_arg)
