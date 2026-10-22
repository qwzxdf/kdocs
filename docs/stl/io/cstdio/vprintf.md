---
title: std::vprintf
summary: "可変引数のリスト（va_list）を使って、標準出力に出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::vprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`printf` を包んだ自作のログ関数を書くとき、受け取った `...` をそのまま `printf` には渡せません。`va_list` にして `vprintf` に渡します。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vprintf {#vprintf}

```cpp
int vprintf(const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | const char* | 書式文字列 |
| `vlist` | va_list | `va_start` で作った引数のリスト |

- 戻り値: 書き込んだ文字数。失敗したら負の値
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>

void Log(const char* fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  std::vprintf(fmt, ap);
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
| 使いどころ | 自作のログ関数 |

## よくあるミス

??? failure "`va_end` を忘れる"
    `va_start` したら、必ず `va_end` で閉じます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`printf`](printf.md) | 直接書く |
| [`va_start`](../va_start.md) | 可変引数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 可変引数のリスト（va_list）を使って、標準出力に出力する
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::vprintf](https://cpprefjp.github.io/reference/cstdio/vprintf.html)
- [cppreference: std::vprintf](https://en.cppreference.com/w/cpp/io/c/vprintf)
