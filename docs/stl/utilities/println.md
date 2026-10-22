---
title: std::println
summary: "書式つきで出力して、最後に改行する。"
order: 900
tags:
  - ユーティリティ
---

# std::println

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-23">C++23</span>
`#include <print>`
</div>

`std::print` で出力するたびに、`\n` を自分で書くのは手間です。`std::println` は、`print` と同じ書式で出力し、最後に自動で改行を付けます。ゲームのデバッグ出力の大半は、これで足ります。

!!! tip "ポイント"
    - `print` と同じ書式（`{}` に値を入れる）。
    - 最後に改行が付く。
    - 第 1 引数に `FILE*` を渡すと、出力先を選べる（`stderr` など）。

!!! info "このページを読む前に"
    [`std::print`](print.md) を先に読んでください。

## 関数の詳しい説明

### std::println {#println}

```cpp
template <class... Args>
void println(std::format_string<Args...> fmt, Args&&... args);
template <class... Args>
void println(std::FILE* stream, std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 出力先。省略すると `stdout`。`stderr` も指定できる |
| `fmt` | 書式文字列 | `{}` を含む文字列。**コンパイル時の定数** |
| `args...` | 値 | `{}` に順番に入れる値 |

- 戻り値: なし
- 計算量: O(出力の長さ)


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("通常の出力");
  std::println(stderr, "エラー出力: {}", 404);  // stderr は実行結果欄には出ないことがある
}
```

```text title="実行結果"
通常の出力
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグ表示 | `std::println("HP: {}", hp);` |
| エラー出力 | `std::println(stderr, "error: {}", code);` |

## よくあるミス

??? failure "書式と引数の数を合わせない"
    `{}` の数と引数の数が合わないと、コンパイルエラーになります（実行時ではなく）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`print`](print.md) | 改行なし |
| [`format`](format.md) | 文字列として作る |
| [`std::cout`](../io/cout.md) | 従来の出力 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式つきで出力して改行する
    - [x] print の改行つき版
    - [x] stderr も指定できる

## 関連ページ

- [cpprefjp: std::println](https://cpprefjp.github.io/reference/print/println.html)
- [cppreference: std::println](https://en.cppreference.com/w/cpp/io/println)
