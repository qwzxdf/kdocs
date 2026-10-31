---
title: memcmp
summary: "2 つのメモリを、バイト単位で比べる。"
order: 4
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memcmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

2 つのバイト列が同じ内容かを調べたい。`std::memcmp(a, b, n)` は、先頭から `n` バイトを、`unsigned char` として比べます。`strcmp` と違い、終端を見ません。

!!! tip "ポイント"
    - 先頭から `n` バイトを比べる
    - 戻り値は、負・0・正
    - 構造体の比較に使うと、パディングの中身で不一致になることがある
    - 浮動小数点数の比較には使わない（`0.0` と `-0.0` が違う）

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::memcmp {#memcmp}

```cpp
int memcmp(const void* lhs, const void* rhs, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const void*` | 比べる領域 |
| `count` | `std::size_t` | 比べるバイト数 |

構造体を `memcmp` で比べるのは危険です。メンバーの間にある詰め物（パディング）は、中身が不定で、同じ値のオブジェクトでも違うことがあります。比べるなら、メンバーごとに比べる `operator==` を作ります。

整数のバイト順（エンディアン）の影響で、`memcmp` の大小は、整数の大小と一致しません。一致するかどうかだけを見るなら、問題ありません。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const unsigned char a[] = {1, 2, 3, 4};
  const unsigned char b[] = {1, 2, 3, 5};
  std::println("同じ: {}", std::memcmp(a, a, sizeof(a)) == 0);
  std::println("先頭 3 バイトは同じ: {}", std::memcmp(a, b, 3) == 0);
  std::println("a < b: {}", std::memcmp(a, b, 4) < 0);
}
```

```text title="実行結果"
同じ: true
先頭 3 バイトは同じ: true
a < b: true
```

## ゲームでの使いどころ

ハッシュ値や、固定長のバイナリ ID の比較に使います。

## よくあるミス

??? failure "構造体を丸ごと比べる"
    パディングで不一致になることがあります。

??? failure "float を比べる"
    `0.0f` と `-0.0f` が不一致になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](strcmp.md) | 終端までの文字列 |
| `std::equal` | 型に合わせた比較 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: memcmp](https://cpprefjp.github.io/reference/cstring/memcmp.html)
- [cppreference: memcmp](https://en.cppreference.com/w/cpp/string/byte/memcmp)
