---
title: strchr
summary: "C 文字列の中から、1 文字を探す。"
order: 9
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

文字列の中で、ある文字が最初に現れる位置を知りたい。`std::strchr(s, ch)` は、`s` の先頭から `ch` を探し、見つかればその位置へのポインタ、なければ `nullptr` を返します。

!!! tip "ポイント"
    - 最初に見つかった位置へのポインタを返す。なければ `nullptr`
    - `ch` に `'\0'` を渡すと、終端の位置が返る
    - 位置の番号は、ポインタの差（`p - s`）で求める
    - 最後の位置を探すなら `strrchr`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strchr {#strchr}

```cpp
const char* strchr(const char* str, int ch);
char* strchr(char* str, int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 探す対象の文字列 |
| `ch` | `int` | 探す文字（`char` に変換される） |

戻り値が `nullptr` かどうかを必ず確かめます。確かめずに `p - s` や `*p` を使うとクラッシュします。

`ch` が `int` なのは C 由来の事情で、`char` に変換されます。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "key=value";
  const char* eq = std::strchr(s, '=');
  if (eq != nullptr) {
    std::println("位置: {}", eq - s);
    std::println("値: {}", eq + 1);
  }
  std::println("なければ nullptr: {}", std::strchr(s, '#') == nullptr);
}
```

```text title="実行結果"
位置: 3
値: value
なければ nullptr: true
```

## ゲームでの使いどころ

`key=value` のような行を、`=` で分けるときに使います。

## よくあるミス

??? failure "nullptr を確かめない"
    見つからないと `nullptr` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strrchr`](strrchr.md) | 最後の位置を探す |
| [`strstr`](strstr.md) | 文字列を探す |
| `std::string::find` | 普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strchr](https://cpprefjp.github.io/reference/cstring/strchr.html)
- [cppreference: strchr](https://en.cppreference.com/w/cpp/string/byte/strchr)
