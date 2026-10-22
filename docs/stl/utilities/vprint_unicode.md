---
title: std::vprint_unicode
summary: "実行時の書式文字列で、Unicode 対応の出力をする。"
order: 900
tags:
  - ユーティリティ
---

# std::vprint_unicode

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`std::print` は書式文字列がコンパイル時の定数でないといけません。`vprint_unicode` は、実行時の書式文字列を使い、出力先が端末なら Unicode として正しく出力します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::vprint_unicode {#vprint_unicode}

```cpp
void vprint_unicode(string_view fmt, format_args args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | string_view | 書式文字列 |
| `args` | format_args | `make_format_args` で作った引数のリスト |

- 戻り値: なし
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int x = 5;
  std::vprint_unicode("{}\n", std::make_format_args(x));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 多言語対応で、実行時に読み込んだ書式を出力する |

## よくあるミス

??? failure "`print` で足りる場面で使う"
    書式がコンパイル時に決まるなら、`std::print` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`print`](print.md) | コンパイル時の書式 |
| [`vprint_nonunicode`](vprint_nonunicode.md) | Unicode 変換なし |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時の書式文字列で、Unicode 対応の出力をする
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vprint_unicode](https://cpprefjp.github.io/reference/format/vprint_unicode.html)
- [cppreference: std::vprint_unicode](https://en.cppreference.com/w/cpp/utility/format/vprint_unicode)
