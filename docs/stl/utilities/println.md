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

ゲームのデバッグ出力は、数も回数も多くなります。`print` で書くたびに `\n` を自分で付けるのは、地味に面倒で、付け忘れると次の出力と同じ行につながってしまいます。`std::println` は、`print` と同じ書式で出力して、最後に自動で改行を付けます。ゲームのデバッグ出力の大半は、これで足ります。

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

デバッグ表示が、いちばん多い使い方です。`std::println("HP: {}", hp);` のように、変数の値を確かめるのに使います。エラーは標準エラー出力へ、`std::println(stderr, "error: {}", code);` と出します。

ゲームの本番では、コンソールを出さない構成が多いので、`println` はデバッグ専用です。製品のログは、ファイルや画面内のコンソールに書き出す仕組みを別に作り、`std::format` で文字列を作ります。

## よくあるミス

??? failure "改行を二重に書く"
    `std::println("HP: {}\n", hp)` と書くと、改行が 2 つ出て空行ができます。`println` は自動で改行するので、文字列の最後に `\n` を付けません。

??? failure "`print` と `println` を取り違える"
    `print` は改行しないので、複数回呼ぶと 1 行につながって出力されます。1 行ごとに出したいなら `println` を使います。

??? failure "古いコンパイラで使えない"
    `<print>` は C++23 の機能です。Visual Studio 2022 の 17.7 以降、GCC 14 以降、Clang 18 以降が必要です。それより古いと、`std::format` と `std::cout` で代用します。

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
