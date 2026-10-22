---
title: std::format_parse_context
summary: "書式文字列の解析の途中状態を持つクラス（自作の formatter の parse で受け取る）。"
order: 900
tags:
  - ユーティリティ
---

# std::format_parse_context

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

自作の型を `std::format` に対応させるとき、`formatter<T>::parse` が受け取るのが `format_parse_context` です。`{:` の後ろの書式指定（`.2f` など）を、`begin()` から `end()` の範囲で読み取り、解析した位置を `parse` の戻り値で返します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::format_parse_context {#format_parse_context}

```cpp
using format_parse_context = basic_format_parse_context<char>;
```

- 戻り値: 書式文字列の解析状態

### begin {#begin}

```cpp
constexpr const_iterator begin() const noexcept;
```

- 戻り値: 解析する書式指定の先頭
- 計算量: 定数

`{:.2f}` の `.2f` の先頭を指します。

### end {#end}

```cpp
constexpr const_iterator end() const noexcept;
```

- 戻り値: 書式文字列全体の終わり
- 計算量: 定数

`}` の位置ではなく、書式文字列全体の終わりです。`}` を自分で探します。

### advance_to {#advance_to}

```cpp
constexpr void advance_to(const_iterator it);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | const_iterator | 解析し終えた位置 |

- 戻り値: なし
- 計算量: 定数

### next_arg_id {#next_arg_id}

```cpp
constexpr size_t next_arg_id();
```

- 戻り値: 次の自動の引数番号
- 計算量: 定数

`{}` のように番号を省略したときの、次の引数の番号を取ります。

### check_arg_id {#check_arg_id}

```cpp
constexpr void check_arg_id(size_t id);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `id` | size_t | 引数の番号 |

- 戻り値: なし
- 計算量: 定数

`{0}` のように番号を指定したときに、使います。自動の番号との混在を検出します。


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
| 使いどころ | 自作の型に書式指定を足す |

## よくあるミス

??? failure "`}` を超えて読む"
    `parse` は、書式指定の終わり（`}`）の位置までを返します。`end()` まで進めてはいけません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | 自作の formatter |
| [`format_context`](format_context.md) | 出力側 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式文字列の解析の途中状態を持つクラス（自作の formatter の parse で受け取る）
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::format_parse_context](https://cpprefjp.github.io/reference/format/format_parse_context.html)
- [cppreference: std::format_parse_context](https://en.cppreference.com/w/cpp/utility/format/format_parse_context)
