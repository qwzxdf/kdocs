---
title: std::range_format
summary: "範囲の書式化の種類を表す列挙型。"
order: 900
tags:
  - ユーティリティ
---

# std::range_format

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`format_kind` の値の型です。`disabled`（書式化できない）・`map`・`set`・`sequence`・`string`・`debug_string` があります。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::range_format {#range_format}

```cpp
enum class range_format {
  disabled,
  map,
  set,
  sequence,
  string,
  debug_string
};
```

- 戻り値: なし（列挙型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <vector>

int main() {
  std::println("{}", std::format_kind<std::vector<int>> == std::range_format::sequence);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 範囲の書式化の種類を分ける |

## よくあるミス

??? failure "`string` を `sequence` と混同する"
    文字の範囲は `string` として、引用符つきの出力になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_kind`](format_kind.md) | 種類を表す変数 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の書式化の種類を表す列挙型
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::range_format](https://cpprefjp.github.io/reference/format/range_format.html)
- [cppreference: std::range_format](https://en.cppreference.com/w/cpp/utility/format/range_format)
