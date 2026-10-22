---
title: std::vformat_to
summary: "実行時の書式文字列で、出力イテレータに書式化して出力する。"
order: 900
tags:
  - ユーティリティ
---

# std::vformat_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format_to` は書式文字列がコンパイル時の定数でないといけません。`vformat_to` は、実行時に決まる書式文字列で、出力先のイテレータに書き込みます。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::vformat_to {#vformat_to}

```cpp
template <class OutIt>
OutIt vformat_to(OutIt out, string_view fmt, format_args args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き込み先 |
| `fmt` | string_view | 書式文字列 |
| `args` | format_args | `make_format_args` で作った引数のリスト |

- 戻り値: 書き終えた後の出力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <iterator>
#include <print>
#include <string>

int main() {
  int a = 1;
  int b = 2;
  std::string s;
  std::vformat_to(std::back_inserter(s), "{} {}", std::make_format_args(a, b));
  std::println("{}", s);
}
```

```text title="実行結果"
1 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 多言語対応で、実行時に読み込んだ書式文字列を使う |

## よくあるミス

??? failure "書式の誤りを見落とす"
    実行時の書式文字列は、誤りがあると `format_error` が投げられます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to`](format_to.md) | コンパイル時の書式文字列 |
| [`vformat`](vformat.md) | 文字列を返す版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時の書式文字列で、出力イテレータに書式化して出力する
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vformat_to](https://cpprefjp.github.io/reference/format/vformat_to.html)
- [cppreference: std::vformat_to](https://en.cppreference.com/w/cpp/utility/format/vformat_to)
