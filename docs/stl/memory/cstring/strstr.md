---
title: strstr
summary: "C 文字列の中から、別の文字列を探す。"
order: 10
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strstr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

文字列の中から、部分文字列を探したい。`std::strstr(haystack, needle)` は、`haystack` の中で `needle` が最初に現れる位置へのポインタを返します。なければ `nullptr` です。

!!! tip "ポイント"
    - 部分文字列が最初に現れる位置を返す。なければ `nullptr`
    - `needle` が空文字列なら、`haystack` の先頭を返す
    - 大文字小文字を区別する
    - 計算量は長さの積に近い。長い文字列には向かない

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strstr {#strstr}

```cpp
const char* strstr(const char* str, const char* substr);
char* strstr(char* str, char* substr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 探される側 |
| `substr` | `const char*` | 探す文字列 |

見つかった位置は、ポインタの差で番号にできます。続きを探すなら、その位置の次から、もう一度 `strstr` を呼びます。

大文字小文字を区別しない検索は、標準にはありません。両方を小文字にそろえてから探します。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* log = "error: file not found";
  const char* p = std::strstr(log, "not");
  if (p != nullptr) {
    std::println("位置 {} から: {}", p - log, p);
  }
  std::println("なければ nullptr: {}", std::strstr(log, "warning") == nullptr);
  std::println("大文字小文字は区別される: {}", std::strstr(log, "ERROR") == nullptr);
}
```

```text title="実行結果"
位置 12 から: not found
なければ nullptr: true
大文字小文字は区別される: true
```

## ゲームでの使いどころ

ログの中の特定の語を探すときに使います。自分のコードでは `std::string::find` です。

## よくあるミス

??? failure "空の needle を渡して、先頭が返るのを知らない"
    空文字列は、先頭に一致します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 1 文字を探す |
| `std::string::find` | 普段はこちら |
| `std::search` | 汎用の部分列の検索 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strstr](https://cpprefjp.github.io/reference/cstring/strstr.html)
- [cppreference: strstr](https://en.cppreference.com/w/cpp/string/byte/strstr)
