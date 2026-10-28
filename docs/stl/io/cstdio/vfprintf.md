---
title: std::vfprintf
summary: "可変引数のリスト（va_list）を使って、ファイルに出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::vfprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

自作のログ関数で、出力先のファイルを呼び出し側が選べるようにしたい。`vprintf` は標準出力に固定ですが、<strong>出力先を指定でき、可変個引数を `va_list` で受け取る</strong>のが `std::vfprintf` です。

!!! tip "ポイント"
    - `vfprintf(ファイル, 書式, va_list)`。`fprintf` の可変個引数を `va_list` にした版
    - `va_start` と `va_end` を対にして使う
    - 戻り値は、書いた文字数。失敗は負の値
    - ログ ファイルへの出力を包む関数で使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vfprintf {#vfprintf}

```cpp
int vfprintf(std::FILE* stream, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 出力先 |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

[`vprintf`](vprintf.md) の出力先を選べる版です。自作のログ関数で、`stdout` や `stderr`、ログ ファイルへ振り分けるときに使います。

```cpp
void LogTo(std::FILE* out, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vfprintf(out, fmt, args);
  va_end(args);
}
```

`va_list` を使い回す際の注意は、`vprintf` と同じです。複数の出力先に同じ内容を書くなら、`va_copy` でコピーします。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>

void LogTo(std::FILE* out, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vfprintf(out, fmt, args);
  va_end(args);
}

int main() {
  LogTo(stdout, "level=%d name=%s\n", 3, "cave");
}
```

```text title="実行結果"
level=3 name=cave
```

## ゲームでの使いどころ

ログの出力先（コンソール、ファイル、`stderr`）を切り替えられるロガーで使います。レベルごとに出力先を変える、という設計の中心になる関数です。

## よくあるミス

??? failure "`va_end` を忘れる"
    必ず対にします。

??? failure "2 つの出力先に、同じ `va_list` を渡して壊れる"
    `va_copy` で複製します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vprintf`](vprintf.md) | 標準出力に固定 |
| [`fprintf`](fprintf.md) | 可変個引数のまま受け取る |
| [`vsnprintf`](vsnprintf.md) | 文字配列に書く |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力先を選べる `vprintf`
    - [x] ログ関数で使う
    - [x] `va_copy` で複数の出力先

## 関連ページ

- [cpprefjp: std::vfprintf](https://cpprefjp.github.io/reference/cstdio/vfprintf.html)
- [cppreference: std::vfprintf](https://en.cppreference.com/w/cpp/io/c/vfprintf)
