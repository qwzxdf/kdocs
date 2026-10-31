---
title: std::strerror
summary: "エラー番号（errno）を、説明の文字列にする。"
order: 900
tags:
  - メモリ
---

# std::strerror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cerrno>`
</div>

`fopen` が失敗したとき、`errno` に原因の番号が入ります。数字のままでは意味が分からないので、人間が読める文章にするのが `std::strerror(errnum)` です。

!!! tip "ポイント"
    - `errno` の値を、説明の文字列にする
    - 戻り値は静的な領域を指す。次の呼び出しで上書きされる
    - スレッドから使うなら `strerror_s`（MSVC）/ `strerror_r`（POSIX）
    - 文章の内容は環境で違う。比較には使わない

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strerror {#strerror}

```cpp
char* strerror(int errnum);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `errnum` | `int` | `errno` の値 |

戻り値の文字列は、実装が持つ領域を指します。保存したいなら、`std::string` にコピーします。

文章は実装ごとに違います。英語のこともあれば、ロケールで翻訳されることもあります。プログラムの分岐には、文章ではなく `errno` の値（`ENOENT` など）を使います。

C++ では `std::error_code(errno, std::generic_category()).message()` でも、同じ文章が得られます。

## 実際に動かしてみる

```cpp
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <print>

int main() {
  std::FILE* f = std::fopen("no_such_file.txt", "r");
  if (f == nullptr) {
    const int err = errno;
    std::println("ENOENT: {}", err == ENOENT);
    std::println("説明がある: {}", std::strlen(std::strerror(err)) > 0);
  }
}
```

```text title="実行結果"
ENOENT: true
説明がある: true
```

## ゲームでの使いどころ

ファイルの読み込みに失敗したときのログに、原因を添えます。

## よくあるミス

??? failure "文章で分岐する"
    環境で変わります。`errno` の値で分岐します。

??? failure "戻り値のポインタを保存する"
    次の呼び出しで上書きされます。コピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::error_code::message()` | C++ の同様の機能 |
| `std::perror` | 標準エラーに出力する |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strerror](https://cpprefjp.github.io/reference/cstring/strerror.html)
- [cppreference: std::strerror](https://en.cppreference.com/w/cpp/string/byte/strerror)
