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

`std::vformat` は、整形した結果を新しい `std::string` に作ります。既存のバッファに追記したいときは、出力先を指定できる `std::vformat_to` を使います。`std::format_to` の、実行時の書式版です。

!!! tip "ポイント"
    - `vformat_to(出力先, 書式, make_format_args(...))` の形
    - 出力先は出力イテレータ（`std::back_inserter(s)` など）
    - 書式の誤りは、実行時に `std::format_error`
    - 書式がコンパイル時に決まるなら `std::format_to`

!!! info "このページを読む前に"
    [`std::vformat`](vformat.md) と [`std::format_to`](format_to.md) を先に読んでください。

## 関数の詳しい説明

### std::vformat_to {#vformat_to}

<span class="ver ver-20">C++20</span>

```cpp
template <class OutputIt>
OutputIt vformat_to(OutputIt out, std::string_view fmt, std::format_args args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き込み先 |
| `fmt` | `std::string_view` | 書式文字列 |
| `args` | `std::format_args` | `make_format_args` の結果 |

整形した結果を `out` に書き出して、書き終えた位置の出力イテレータを返します。戻り値を使えば、続きに書けます。

`std::back_inserter(s)` を渡すと、`std::string s` の末尾に追記されます。固定長の配列に書くなら、ポインタを渡しますが、長さを超えないよう、注意が要ります。長さを制限するには `format_to_n` です。

## 実際に動かしてみる

```cpp
#include <format>
#include <iterator>
#include <print>
#include <string>

int main() {
  const std::string fmt = "{}:{}";
  int a = 1;
  int b = 2;

  // 既存の文字列に追記する
  std::string log = "[";
  std::vformat_to(std::back_inserter(log), fmt, std::make_format_args(a, b));
  log += "]";
  std::println("{}", log);
}
```

```text title="実行結果"
[1:2]
```

## ゲームでの使いどころ

ログのバッファに、複数の書式つきの行を追記していくときに使います。

## よくあるミス

??? failure "固定長の配列に書いてあふれる"
    ポインタを渡すと、長さの確認がありません。`format_to_n` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vformat`](vformat.md) | 新しい文字列を返す |
| [`format_to`](format_to.md) | コンパイル時に検査される書式 |
| [`format_to_n`](format_to_n.md) | 書き込む長さを制限する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::vformat_to](https://cpprefjp.github.io/reference/format/vformat_to.html)
- [cppreference: std::vformat_to](https://en.cppreference.com/w/cpp/utility/format/vformat_to)
