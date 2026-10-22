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

`fprintf` を包んだ自作のログ関数用です。出力先の `FILE*` を指定できます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vfprintf {#vfprintf}

```cpp
int vfprintf(std::FILE* stream, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 出力先 |
| `format` | const char* | 書式文字列 |
| `vlist` | va_list | 引数のリスト |

- 戻り値: 書き込んだ文字数。失敗したら負の値
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>

void Log(const char* fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  std::vfprintf(stdout, fmt, ap);
  va_end(ap);
}

int main() {
  Log("%d-%s\n", 1, "a");
}
```

```text title="実行結果"
1-a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のログ関数（出力先を選べる） |

## よくあるミス

??? failure "`va_end` を忘れる"
    `va_start` したら、必ず `va_end` で閉じます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vprintf`](vprintf.md) | 標準出力 |
| [`fprintf`](fprintf.md) | 直接書く |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 可変引数のリスト（va_list）を使って、ファイルに出力する
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vfprintf](https://cpprefjp.github.io/reference/cstdio/vfprintf.html)
- [cppreference: std::vfprintf](https://en.cppreference.com/w/cpp/io/c/vfprintf)
