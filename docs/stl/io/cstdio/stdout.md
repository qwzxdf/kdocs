---
title: std::stdout
summary: "標準出力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stdout

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`printf` や `puts` が出力する先は、どこでしょう。画面（コンソール）です。その出力先を表しているのが、`stdout`（標準出力）という、あらかじめ開かれている `FILE*` です。

!!! tip "ポイント"
    - プログラムの開始時に、自動で開かれている。`fopen` も `fclose` も要らない
    - `printf(...)` は `fprintf(stdout, ...)` と同じ
    - 端末につながっているときは行バッファー、ファイルにリダイレクトされているときはフル バッファー
    - ログのようなエラー出力は、`stdout` ではなく `stderr` に出す

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### stdout {#stdout}

```cpp
extern std::FILE* stdout;   // 実際はマクロの場合もある
```

`stdout` は、`printf`、`puts`、`putchar`、`std::print`（引数にファイルを取らない版）の出力先です。`fprintf(stdout, ...)` と書くと、`printf` と同じ意味になります。

シェルのリダイレクト（`game.exe > out.txt`）で、`stdout` はファイルに向きます。このとき、バッファーの方式が変わります。端末なら行ごとに書き出されますが、ファイルへのリダイレクトでは、バッファーが一杯になるまで溜まります。クラッシュすると、ファイルに最後の部分が入らないことがあります。

Windows の GUI アプリ（`WinMain` で始まるもの）では、コンソールがつながっていないので、`stdout` に出しても、どこにも表示されません。デバッグ出力は、`OutputDebugString` を使うか、`AllocConsole` でコンソールを作ります。

`stdout` を閉じてはいけません（`fclose(stdout)` はできるが、以降の出力が失われる）。出力先を変えるには、[`freopen`](freopen.md) を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::printf("printf の出力\n");
  std::fprintf(stdout, "fprintf(stdout) でも同じ\n");
  std::fputs("fputs(..., stdout)\n", stdout);
}
```

```text title="実行結果"
printf の出力
fprintf(stdout) でも同じ
fputs(..., stdout)
```

## ゲームでの使いどころ

通常の出力、つまり「プログラムの結果」を書き出す先です。ツール類では、結果を `stdout` に、診断やログを `stderr` に分けると、`> result.txt` でリダイレクトしたときに、結果だけをファイルに保存できます。

ゲームでは、デバッグ用の `printf` がこの先に出ます。製品版では、出力先を決めて、ログ ファイルに向けます（`freopen`）。

## よくあるミス

??? failure "GUI アプリで `printf` を書いて、何も出ない"
    コンソールがありません。`OutputDebugString` や `AllocConsole` を使います。

??? failure "リダイレクトしたとき、クラッシュ直前の出力が残らない"
    フル バッファーのためです。`fflush(stdout)` を呼ぶか、`setvbuf` でバッファーを切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stderr`](stderr.md) | 標準エラー出力。バッファーなし |
| [`stdin`](stdin.md) | 標準入力 |
| [`freopen`](freopen.md) | 出力先を変える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力の `FILE*`
    - [x] `printf` の出力先
    - [x] 結果は `stdout`、ログは `stderr`

## 関連ページ

- [cpprefjp: std::stdout](https://cpprefjp.github.io/reference/cstdio/stdout.html)
- [cppreference: std::stdout](https://en.cppreference.com/w/cpp/io/c/stdout)
