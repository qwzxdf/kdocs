---
title: strncpy
summary: "C 文字列を最大 n 文字コピーする（終端に注意）。"
order: 12
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strncpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strcpy` の危険を避けるために、コピーする最大の文字数を指定できるのが `std::strncpy(dst, src, n)` です。ところがこの関数には、<strong>`src` が `n` 文字以上だと、終端を付けない</strong>という落とし穴があります。名前から想像する「安全な `strcpy`」ではありません。

!!! tip "ポイント"
    - 最大 `n` 文字をコピーする
    - `src` が `n` 文字以上なら、`dst` に終端が付かない
    - `src` が短いと、残りを `'\0'` で `n` 文字まで埋める
    - 終端が要るなら、自分で `dst[n - 1] = '\0'` と書く

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strncpy {#strncpy}

```cpp
char* strncpy(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | コピー先 |
| `src` | `const char*` | コピー元 |
| `count` | `std::size_t` | コピーする最大の文字数 |

`src` が `count` 文字より短いと、残りの領域を `'\0'` で埋めます。大きな配列に短い文字列をコピーすると、無駄に書き込みます。

`src` が `count` 文字以上のときは、ちょうど `count` 文字をコピーして、終端を付けません。そのまま `strlen` や `println` に渡すと、配列の外まで読みます。

安全な使い方は、`count` を配列の大きさ - 1 にして、最後に終端を書くことです。ただし、手間がかかるので、`snprintf` か `std::string` のほうが簡単です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char dst[4];
  std::strncpy(dst, "abcdefg", sizeof(dst) - 1);
  dst[sizeof(dst) - 1] = '\0';  // 終端は自分で付ける
  std::println("{}", dst);

  // 短い文字列なら、残りは \0 で埋められる
  char buf[8];
  std::strncpy(buf, "ab", sizeof(buf));
  std::println("長さ {} 末尾の要素は \\0: {}", std::strlen(buf), buf[7] == '\0');
}
```

```text title="実行結果"
abc
長さ 2 末尾の要素は \0: true
```

## ゲームでの使いどころ

固定長のフィールドに名前を詰めるような、古いデータ形式を扱うときに出てきます。

## よくあるミス

??? failure "終端が付かないまま使う"
    `count` 文字以上の `src` では、終端がありません。自分で付けます。

??? failure "count に配列の大きさをそのまま渡す"
    最後に終端を書く余地がなくなります。大きさ - 1 にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcpy`](strcpy.md) | 大きさを確認しない |
| [`snprintf`](snprintf.md) | 常に終端を付ける |
| `std::string` | 普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strncpy](https://cpprefjp.github.io/reference/cstring/strncpy.html)
- [cppreference: strncpy](https://en.cppreference.com/w/cpp/string/byte/strncpy)
