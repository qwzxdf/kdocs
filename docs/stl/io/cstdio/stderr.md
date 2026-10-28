---
title: std::stderr
summary: "標準エラー出力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stderr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

プログラムの結果と、エラーのメッセージが、同じ画面に混ざって出る。それでも、結果だけをファイルに保存したいときがあります。エラーを別の流れに分けるために、`stderr`（標準エラー出力）が用意されています。

!!! tip "ポイント"
    - `stdout` とは別の出力先。既定ではバッファーなしで、書くとすぐに出る
    - リダイレクト（`> out.txt`）しても、`stderr` は画面に出る（`2> err.txt` で別に向けられる）
    - エラー、警告、診断の出力に使う
    - クラッシュ直前のメッセージも、バッファーに残らずに出る

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### stderr {#stderr}

```cpp
extern std::FILE* stderr;   // 実際はマクロの場合もある
```

`fprintf(stderr, "...")` のように使います。`stdout` と違って、既定で<strong>バッファーされません</strong>。書いた内容がすぐに出力されるので、プログラムが直後にクラッシュしても、メッセージが失われません。

シェルで `game.exe > result.txt` とすると、`stdout` だけがファイルへ向き、`stderr` は画面に出続けます。結果とエラーを分けて扱えるのが、利点です。`2> errors.txt` とすれば、エラーだけをファイルにも向けられます。

C++ には `std::cerr`（バッファーなし）と `std::clog`（バッファーあり）がありますが、C の `stderr` と同じ出力先に結び付いています（既定では同期されているため、混ぜて使っても順序が崩れません）。

Windows の GUI アプリでは、`stdout` と同様に、コンソールがないので、どこにも出ません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("結果: 42");                                  // 標準出力
  std::fprintf(stderr, "警告: 設定ファイルがありません\n");   // 標準エラー出力。別の流れ
}
```

```text title="実行結果"
結果: 42
```

## ゲームでの使いどころ

ツールの結果（`stdout`）と、診断メッセージ（`stderr`）を分けるために使います。ゲームでは、致命的なエラーを `stderr` に出してから終了することで、リダイレクト先のファイルにも、画面にも、メッセージが残ります。

アサートや、例外のハンドラーでの最後の出力にも向いています。バッファーを通らないので、書いた直後にクラッシュしても失われません。

## よくあるミス

??? failure "エラー メッセージを `stdout` に出して、結果と混ざる"
    リダイレクトした結果のファイルに、エラーが混入します。`stderr` に出します。

??? failure "GUI アプリで出して、見えない"
    コンソールがありません。ログ ファイルか、`OutputDebugString` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stdout`](stdout.md) | 標準出力 |
| [`perror`](perror.md) | `errno` の説明を `stderr` に出す |
| `std::cerr` | C++ のストリームでの標準エラー出力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準エラー出力の `FILE*`
    - [x] 既定でバッファーなし
    - [x] エラーと診断は `stderr`

## 関連ページ

- [cpprefjp: std::stderr](https://cpprefjp.github.io/reference/cstdio/stderr.html)
- [cppreference: std::stderr](https://en.cppreference.com/w/cpp/io/c/stderr)
