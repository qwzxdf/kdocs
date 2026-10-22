---
title: std::vprint_nonunicode
summary: "実行時の書式文字列で、Unicode 変換なしで出力する。"
order: 900
tags:
  - ユーティリティ
---

# std::vprint_nonunicode

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`vprint_unicode` との違いは、端末向けの Unicode 変換（UTF-8 から端末の文字コードへ）をしないことです。バイト列をそのまま出します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::vprint_nonunicode {#vprint_nonunicode}

```cpp
void vprint_nonunicode(string_view fmt, format_args args);
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
  std::vprint_nonunicode("{}\n", std::make_format_args(x));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | バイト列をそのまま出力する |

## よくあるミス

??? failure "端末の文字化けを期待する"
    変換しないので、端末の文字コードが UTF-8 でないと化けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vprint_unicode`](vprint_unicode.md) | Unicode 対応 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時の書式文字列で、Unicode 変換なしで出力する
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vprint_nonunicode](https://cpprefjp.github.io/reference/format/vprint_nonunicode.html)
- [cppreference: std::vprint_nonunicode](https://en.cppreference.com/w/cpp/utility/format/vprint_nonunicode)
