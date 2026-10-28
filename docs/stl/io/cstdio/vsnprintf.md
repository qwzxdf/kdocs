---
title: std::vsnprintf
summary: "可変引数のリスト（va_list）を使って、大きさを指定して文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::vsnprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

自作の書式化関数で、必要な大きさを先に調べてから、ちょうどの大きさで確保する、という使い方ができます。`nullptr` と 0 を渡すと、必要な長さだけが返ります。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vsnprintf {#vsnprintf}

```cpp
int vsnprintf(char* buffer, std::size_t buf_size, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | char* | 書き込み先（`nullptr` も可） |
| `buf_size` | size_t | 書き込める最大のバイト数（終端を含む） |
| `format` | const char* | 書式文字列 |
| `vlist` | va_list | 引数のリスト |

- 戻り値: 書き込めたはずの文字数（終端を除く）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>
#include <print>
#include <string>

std::string Format(const char* fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  va_list ap2;
  va_copy(ap2, ap);
  int n = std::vsnprintf(nullptr, 0, fmt, ap);
  std::string s(n, '\0');
  std::vsnprintf(s.data(), n + 1, fmt, ap2);
  va_end(ap2);
  va_end(ap);
  return s;
}

int main() {
  std::println("{}", Format("%d-%s", 1, "a"));
}
```

```text title="実行結果"
1-a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の書式化関数を安全に書く |

## よくあるミス

??? failure "`va_list` を 2 回使う"
    `va_list` は 1 回使うと進んでしまいます。2 回使うなら `va_copy` で複製します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vsprintf`](vsprintf.md) | 大きさを指定しない |
| [`va_copy`](../va_copy.md) | リストを複製する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 可変引数のリスト（va_list）を使って、大きさを指定して文字配列に書き込む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vsnprintf](https://cpprefjp.github.io/reference/cstdio/vsnprintf.html)
- [cppreference: std::vsnprintf](https://en.cppreference.com/w/cpp/io/c/vsnprintf)
