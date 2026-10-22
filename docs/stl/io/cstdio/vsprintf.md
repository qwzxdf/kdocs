---
title: std::vsprintf
summary: "可変引数のリスト（va_list）を使って、文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::vsprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`sprintf` を包んだ自作の書式化関数用です。配列の大きさを確かめないため、`vsnprintf` のほうが安全です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vsprintf {#vsprintf}

```cpp
int vsprintf(char* buffer, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | char* | 書き込み先 |
| `format` | const char* | 書式文字列 |
| `vlist` | va_list | 引数のリスト |

- 戻り値: 書き込んだ文字数
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>
#include <print>
#include <string>

std::string Format(const char* fmt, ...) {
  char buf[32];
  va_list ap;
  va_start(ap, fmt);
  std::vsprintf(buf, fmt, ap);
  va_end(ap);
  return buf;
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
| 使いどころ | （古い C のコードの保守） |

## よくあるミス

??? failure "バッファがあふれる"
    長さの確認がありません。`vsnprintf` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vsnprintf`](vsnprintf.md) | 大きさを指定する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 可変引数のリスト（va_list）を使って、文字配列に書き込む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vsprintf](https://cpprefjp.github.io/reference/cstdio/vsprintf.html)
- [cppreference: std::vsprintf](https://en.cppreference.com/w/cpp/io/c/vsprintf)
