---
title: std::vformat
summary: "書式の文字列を、実行時に決める。"
order: 51
tags:
  - ユーティリティ
---

# std::vformat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::vformat` は、`std::format` とは違い、**書式の文字列を実行時に決められる**関数です。`std::format` や `std::println` の書式はコンパイル時に決まっていなければなりませんが、設定ファイルや翻訳テキストから書式を読み込むときは、こちらを使います。

!!! tip "ポイント"
    - 引数は `std::make_format_args(...)` で包んで渡す。
    - 書式と引数が合わないと、実行時に `std::format_error` の例外になる。
    - ユーザーが入力した文字列をそのまま書式に使ってはいけない（意図しない展開が起きる）。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) などは不要です。書式の指定は [std::format](format.md) のページにまとめてあります。

## 関数の詳しい説明

### std::vformat {#vformat}

```cpp
std::string vformat(std::string_view fmt, std::format_args args);
```

- 書式文字列を**実行時に**決めたいときに使います（翻訳ファイルから読み込んだ文字列など）
- 引数は `std::make_format_args(...)` で包みます。書式が間違っていると `std::format_error` 例外

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  std::string fmt = "{} を {} 個手に入れた";  // 翻訳ファイルから読んだとする
  std::string item = "ポーション";
  int count = 3;
  std::println("{}", std::vformat(fmt, std::make_format_args(item, count)));
}
```

```text title="実行結果"
ポーション を 3 個手に入れた
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 翻訳テキスト（書式つき）を読み込んで展開する | `std::vformat(text, std::make_format_args(name, count))` |

## よくあるミス

??? failure "書式を実行時に決めたのに format を使う"
    `std::format(fmt, ...)` の `fmt` は定数です。実行時の文字列は `std::vformat` です（C++26 では `std::runtime_format` も使える）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 書式はコンパイル時に決まる |
| [`std::print`](print.md) | 出力 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を実行時に決める
    - [x] 引数は `make_format_args` で包む
    - [x] 不一致は実行時に例外

## 関連ページ

- [cpprefjp: std::vformat](https://cpprefjp.github.io/reference/format/vformat.html)
- [cppreference: std::vformat](https://en.cppreference.com/w/cpp/utility/format/vformat)
