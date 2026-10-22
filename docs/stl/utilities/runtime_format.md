---
title: std::runtime_format
summary: "実行時の文字列を、書式文字列として `format` に渡す。"
order: 900
tags:
  - ユーティリティ
---

# std::runtime_format

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <format>`
</div>

`std::format` の書式文字列は、コンパイル時に検査されるため、実行時に読み込んだ文字列は渡せません。`std::runtime_format(s)` で包むと、検査を実行時に行う形で渡せます。誤りがあると例外になります。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::runtime_format {#runtime_format}

```cpp
constexpr /* 実装定義 */ runtime_format(string_view fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | string_view | 実行時の書式文字列 |

- 戻り値: `format` に渡せる書式文字列
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  std::string fmt = "{}";
  std::println("{}", std::format(std::runtime_format(fmt), 5));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルから読み込んだ書式文字列を使う |

## よくあるミス

??? failure "信頼できない入力を使う"
    誤った書式で例外になります。外部入力には `try` を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vformat`](vformat.md) | 古典的な書き方 |

## コンパイラ対応

C++26 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時の文字列を、書式文字列として `format` に渡す
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::runtime_format](https://cpprefjp.github.io/reference/format/runtime_format.html)
- [cppreference: std::runtime_format](https://en.cppreference.com/w/cpp/utility/format/runtime_format)
