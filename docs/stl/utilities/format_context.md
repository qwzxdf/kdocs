---
title: std::format_context
summary: "書式化の出力先と引数を持つクラス（自作の formatter の format で受け取る）。"
order: 900
tags:
  - ユーティリティ
---

# std::format_context

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

自作の `formatter` を書くとき、`format` 関数の第 2 引数に渡ってくるのが `std::format_context` です。書式化の結果を書き込む出力先（`ctx.out()`）と、書式化の引数（`ctx.arg(i)`）を持っています。

!!! tip "ポイント"
    - `ctx.out()` が、結果を書き込む出力イテレータ
    - 書き終えたら、出力イテレータを返す。`std::format_to(ctx.out(), ...)` の戻り値をそのまま返す
    - `ctx.arg(i)` で、書式の引数を取れる
    - `wchar_t` 版は `std::wformat_context`

!!! info "このページを読む前に"
    [`std::formatter`](formatter.md) と [`std::format_parse_context`](format_parse_context.md) を先に読んでください。

## 関数の詳しい説明

### std::format_context {#format_context}

<span class="ver ver-20">C++20</span>

```cpp
class format_context {
 public:
  using iterator = /* 実装定義の出力イテレータ */;
  using char_type = char;
  iterator out();
  void advance_to(iterator it);
  std::basic_format_arg<format_context> arg(std::size_t id) const noexcept;
  std::locale locale();
};
```

`out()` は、書き込み先を指す出力イテレータです。`std::format_to(ctx.out(), "...", ...)` で書き込み、その戻り値（書き終えた位置）を、`format` 関数の戻り値として返します。

`advance_to(it)` は、出力位置を進めます。`format_to` の戻り値を使う場合は、呼ばなくて済みます。

`arg(id)` は、番号指定の引数を取ります。幅や精度を、別の引数から受け取る書式（`{:{}}`）を実装するときに使います。

`locale()` は、書式化に使うロケールです。`{:L}` の指定のときに参照します。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>

struct Point {
  int x, y;
};

template <>
struct std::formatter<Point> {
  constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }

  // ctx.out() に書き込み、書き終えた位置を返す
  auto format(const Point& p, std::format_context& ctx) const {
    return std::format_to(ctx.out(), "({}, {})", p.x, p.y);
  }
};

int main() {
  std::println("{}", Point{3, 4});
  std::println("{}", std::format("pos = {}", Point{1, 2}));
}
```

```text title="実行結果"
(3, 4)
pos = (1, 2)
```

## ゲームでの使いどころ

ゲーム独自の型（ベクトル、色、ID）を、`println` で表示できるようにするときに、`format` の中で使います。

## よくあるミス

??? failure "書き終えた位置を返さない"
    `format` の戻り値は、書き終えた出力イテレータです。`format_to` の戻り値を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_parse_context`](format_parse_context.md) | 書式の解析用の文脈 |
| [`formatter`](formatter.md) | これを受け取る側 |
| [`basic_format_args`](basic_format_args.md) | 引数の集まり |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::format_context](https://cpprefjp.github.io/reference/format/format_context.html)
- [cppreference: std::format_context](https://en.cppreference.com/w/cpp/utility/format/format_context)
