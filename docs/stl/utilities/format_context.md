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

自作の型を `std::format` に対応させるとき、`formatter<T>::format` が受け取るのが `format_context` です。`out()` で出力先のイテレータを取り、そこへ文字を書き込みます。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::format_context {#format_context}

```cpp
using format_context = basic_format_context<std::back_insert_iterator<std::string>, char>;
```

- 戻り値: 書式化の出力先と引数

### out {#out}

```cpp
iterator out();
```

- 戻り値: 出力先のイテレータ
- 計算量: 定数

`std::format_to(ctx.out(), "...", ...)` のように、ここへ書き込みます。

### arg {#arg}

```cpp
basic_format_arg<basic_format_context> arg(size_t id) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `id` | size_t | 引数の番号 |

- 戻り値: その番号の引数
- 計算量: 定数

`{:{}}` のように、幅を別の引数で指定するときなどに使います。

### locale {#locale}

```cpp
std::locale locale();
```

- 戻り値: 書式化で使うロケール
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

struct P {
  int x;
};
template <>
struct std::formatter<P> {
  constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }
  auto format(const P& p, std::format_context& ctx) const { return std::format_to(ctx.out(), "P({})", p.x); }
};

int main() {
  std::println("{}", P{5});
}
```

```text title="実行結果"
P(5)
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の型の出力内容を決める |

## よくあるミス

??? failure "`out()` を書き込まない"
    `format` は書き込んだあとの出力イテレータを返す必要があります。`std::format_to(ctx.out(), ...)` の戻り値を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | 自作の formatter |
| [`format_parse_context`](format_parse_context.md) | 解析側 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式化の出力先と引数を持つクラス（自作の formatter の format で受け取る）
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::format_context](https://cpprefjp.github.io/reference/format/format_context.html)
- [cppreference: std::format_context](https://en.cppreference.com/w/cpp/utility/format/format_context)
