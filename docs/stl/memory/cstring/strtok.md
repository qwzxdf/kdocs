---
title: std::strtok
summary: "文字列を、区切り文字で分割して 1 つずつ取り出す。"
order: 900
tags:
  - メモリ
---

# std::strtok

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

「a,b,c」のような文字列を、区切り文字で分けて、1 つずつ取り出したい。`std::strtok(s, delim)` は、最初の呼び出しで文字列を渡し、2 回目以降は `nullptr` を渡すと、続きを返します。ただし、<strong>元の文字列を書き換え</strong>（区切りを `'\0'` にする）、内部に状態を持つので、使いにくい関数です。

!!! tip "ポイント"
    - 最初は `strtok(s, delim)`、続きは `strtok(nullptr, delim)`
    - 元の文字列の区切りを `'\0'` に書き換える
    - 内部の状態を使う。同時に 2 つの分割はできず、スレッドにも向かない
    - 連続した区切りは、1 つの区切りとして扱われ、空の要素は出ない

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strtok {#strtok}

```cpp
char* strtok(char* str, const char* delim);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `char*` | 分ける文字列。2 回目以降は `nullptr` |
| `delim` | `const char*` | 区切り文字の集まり |

戻り値は、取り出した要素の先頭です。もう要素がなければ `nullptr` です。

書き換えるので、文字列リテラル（`const char*`）は渡せません。`char s[] = "a,b,c";` のように、書き込める配列に入れます。

内部の状態は 1 つだけです。分割している最中に、別の文字列を `strtok` で分けると、状態が壊れます。MSVC の `strtok_s` や POSIX の `strtok_r` が、状態を引数で持つ版です。

C++ では、`std::views::split` や、`std::getline` を区切り文字つきで使うほうが、安全に書けます。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char s[] = "a,b,,c";  // 書き込める配列
  for (char* t = std::strtok(s, ","); t != nullptr; t = std::strtok(nullptr, ",")) {
    std::println("[{}]", t);
  }
}
```

```text title="実行結果"
[a]
[b]
[c]
```

## ゲームでの使いどころ

古いコードの読解用です。新しく書くなら、`std::string_view` と `std::views::split` を使います。

## よくあるミス

??? failure "文字列リテラルを渡す"
    書き換えようとして、クラッシュします。

??? failure "入れ子で使う"
    内部の状態が 1 つなので、壊れます。

??? failure "空の要素が出ると思う"
    連続した区切りは、まとめて 1 つです。`b` と `c` の間の空の要素は出ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strpbrk`](strpbrk.md) | 区切りの位置を探す |
| `std::views::split` | C++20 の分割 |
| `std::getline` | 区切り文字を指定して読める |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strtok](https://cpprefjp.github.io/reference/cstring/strtok.html)
- [cppreference: std::strtok](https://en.cppreference.com/w/cpp/string/byte/strtok)
