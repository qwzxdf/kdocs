---
title: memchr
summary: "メモリの中から、1 バイトの値を探す。"
order: 8
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strchr` は終端までしか探せません。途中に `'\0'` があるバイト列や、終端のないバッファの中で、あるバイトを探したいときは、長さを指定できる `std::memchr(p, ch, n)` を使います。

!!! tip "ポイント"
    - 先頭から `n` バイトの範囲で、`ch` を探す
    - 見つかれば位置へのポインタ、なければ `nullptr`
    - 終端文字に関係なく、`n` バイトまで調べる
    - `ch` は `unsigned char` として比べる

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::memchr {#memchr}

```cpp
const void* memchr(const void* ptr, int ch, std::size_t count);
void* memchr(void* ptr, int ch, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `const void*` | 探す領域の先頭 |
| `ch` | `int` | 探すバイト（`unsigned char` に変換される） |
| `count` | `std::size_t` | 探す範囲のバイト数 |

戻り値は `void*` で、使うには `char*` などにキャストします。

`count` が実際の領域より大きいと、領域の外を読みます。バイト列の長さを、自分で管理します。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  // 途中に \0 があるバイト列
  const char data[] = {'a', 'b', '\0', 'c', 'd'};
  const void* p = std::memchr(data, 'd', sizeof(data));
  std::println("d の位置: {}", static_cast<const char*>(p) - data);

  std::println("範囲に無ければ nullptr: {}", std::memchr(data, 'z', sizeof(data)) == nullptr);
}
```

```text title="実行結果"
d の位置: 4
範囲に無ければ nullptr: true
```

## ゲームでの使いどころ

ネットワークのパケットやファイルの中身（バイナリ）から、特定のバイトを探すときに使います。

## よくあるミス

??? failure "count を領域より大きくする"
    範囲の外を読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 終端まで探す |
| `std::find` | 汎用の探索 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: memchr](https://cpprefjp.github.io/reference/cstring/memchr.html)
- [cppreference: memchr](https://en.cppreference.com/w/cpp/string/byte/memchr)
