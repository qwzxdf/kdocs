---
title: std::strpbrk
summary: "文字列の中から、指定した文字のどれかが最初に現れる位置を探す。"
order: 900
tags:
  - メモリ
---

# std::strpbrk

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

区切り文字が複数ある（`,` か `;` か空白）とき、そのうち最初に現れるものの位置を知りたい。`std::strpbrk(s, chars)` は、`chars` のどれかの文字が最初に現れる位置を、ポインタで返します。

!!! tip "ポイント"
    - `chars` のどれかが最初に現れる位置を返す
    - なければ `nullptr`
    - `strchr` を複数の文字に広げたもの
    - 長さが欲しいなら `strcspn`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strpbrk {#strpbrk}

```cpp
const char* strpbrk(const char* dest, const char* breakset);
char* strpbrk(char* dest, const char* breakset);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `const char*` | 探される側 |
| `breakset` | `const char*` | 探す文字の集まり |

見つからなければ `nullptr` なので、確かめてから使います。

最初に現れた位置だけを返します。続きを探すなら、その次の位置から、もう一度呼びます。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "a b,c;d";
  const char* p = std::strpbrk(s, ",; ");
  std::println("最初の区切り: '{}' 位置 {}", *p, p - s);

  const char* q = std::strpbrk(p + 1, ",; ");
  std::println("次の区切り: '{}' 位置 {}", *q, q - s);

  std::println("なければ nullptr: {}", std::strpbrk("abc", ",;") == nullptr);
}
```

```text title="実行結果"
最初の区切り: ' ' 位置 1
次の区切り: ',' 位置 3
なければ nullptr: true
```

## ゲームでの使いどころ

複数の区切り文字をまとめて探すときに使います。

## よくあるミス

??? failure "nullptr を確かめない"
    見つからないと `nullptr` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 1 文字だけを探す |
| [`strcspn`](strcspn.md) | 位置ではなく長さを返す |
| [`strtok`](strtok.md) | 区切って取り出す |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strpbrk](https://cpprefjp.github.io/reference/cstring/strpbrk.html)
- [cppreference: std::strpbrk](https://en.cppreference.com/w/cpp/string/byte/strpbrk)
