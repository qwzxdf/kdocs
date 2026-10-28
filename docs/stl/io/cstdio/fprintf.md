---
title: std::fprintf
summary: "書式を指定して、ファイルに出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ログ ファイルに「HP: 100 / 120」のような、数値を含む行を書き出したい。文字列を `+` でつなぐのは面倒なので、書式の中に値をはめ込んで、ファイルへ出す関数が `std::fprintf` です。`printf` の出力先を選べる版です。

!!! tip "ポイント"
    - `fprintf(ファイル, 書式, 値...)`。書式の `%d`、`%f`、`%s` などに、値がはまる
    - 戻り値は、書いた文字数。失敗は負の値
    - 書式と値の型が合っていないと、未定義動作になる。コンパイラの警告を有効にする
    - ユーザー入力を書式にそのまま渡してはいけない。`"%s"` を使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fprintf {#fprintf}

```cpp
int fprintf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 出力先。`stdout` や `stderr` も渡せる |
| `format` | `const char*` | 書式文字列。`%` から始まる指定に、値がはまる |
| `...` | 可変個引数 | 書式に対応する値 |

よく使う指定は、`%d`（`int`）、`%u`（`unsigned`）、`%f`（`double`）、`%s`（文字列）、`%c`（文字）、`%x`（16 進数）、`%%`（`%` そのもの）です。`long long` には `%lld`、`size_t` には `%zu` を使います。

<strong>書式と値の型が食い違うと、未定義動作</strong>です。`%d` に `double` を渡すと、でたらめな値が出たり、クラッシュしたりします。`float` は可変個引数に渡す時点で `double` になるので `%f` で受けられます。GCC や Clang は `-Wformat`、MSVC は `/W4` で、食い違いを警告します。

書式文字列が、プログラムに埋め込んだ定数ではなく、ユーザー入力やファイルの内容から来ていると、`%s` や `%n` を仕込まれる危険があります（書式文字列攻撃）。外から来た文字列は、`fprintf(f, "%s", text)` のように、値として渡します。

C++23 の `std::print(FILE*, ...)` なら、型が合っていないとコンパイル エラーになるので、新しいコードではそちらが安全です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("status.log", "w");
  int n = std::fprintf(f, "HP: %d / %d (%.1f%%)\n", 85, 120, 85 * 100.0 / 120);
  std::fclose(f);
  std::println("書いた文字数: {}", n);

  std::FILE* in = std::fopen("status.log", "r");
  char buf[64];
  std::fgets(buf, sizeof(buf), in);
  std::print("{}", buf);
  std::fclose(in);
}
```

```text title="実行結果"
書いた文字数: 21
HP: 85 / 120 (70.8%)
```

## ゲームでの使いどころ

ログ ファイルへの出力や、`stderr` へのエラー表示に使います。`fprintf(stderr, ...)` は、標準エラー出力にメッセージを出す、C の定番の書き方です。

新しい C++ のコードでは、`std::print` / `std::println`（C++23）や `std::format` が、型安全で書きやすいので、`fprintf` は、C のコードを読むときと、C のライブラリに合わせるときに使います。

## よくあるミス

??? failure "書式と値の型が食い違って、でたらめな値が出る"
    `%d` に `double`、`%s` に `int` などを渡さないようにします。警告を有効にします。

??? failure "ユーザー入力を書式に渡して、脆弱性になる"
    `fprintf(f, input)` ではなく、`fprintf(f, "%s", input)` にします。

??? failure "`size_t` を `%d` で出して、大きな値で壊れる"
    `%zu` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`printf`](printf.md) | 標準出力に書く |
| [`sprintf`](sprintf.md) | 文字配列に書く |
| `std::print` | C++23 の型安全な出力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式つきでファイルに書く
    - [x] 書式と値の型を合わせる
    - [x] 外から来た文字列は `"%s"` で渡す

## 関連ページ

- [cpprefjp: std::fprintf](https://cpprefjp.github.io/reference/cstdio/fprintf.html)
- [cppreference: std::fprintf](https://en.cppreference.com/w/cpp/io/c/fprintf)
