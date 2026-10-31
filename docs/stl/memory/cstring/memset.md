---
title: memset
summary: "メモリの範囲を、同じバイト値で埋める。"
order: 2
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memset

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

配列やバッファを、同じバイトで埋めたい。`std::memset(p, value, n)` は、`p` から `n` バイトを、`value` で埋めます。ゼロクリアの定番ですが、`int` 配列を 1 で埋めるといった用途には向きません。バイト単位で埋めるからです。

!!! tip "ポイント"
    - `n` バイトを、同じバイトで埋める
    - ゼロクリア（`memset(p, 0, n)`）が主な用途
    - `int` を `0` 以外で埋めると、期待と違う値になる
    - クラスのオブジェクトには使わない

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::memset {#memset}

```cpp
void* memset(void* dest, int ch, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | 埋める領域の先頭 |
| `ch` | `int` | 埋めるバイト（`unsigned char` に変換される） |
| `count` | `std::size_t` | 埋めるバイト数 |

`int` の配列を `memset(a, 1, sizeof(a))` で埋めると、各バイトが `0x01` なので、値は `0x01010101`（16843009）になります。`0` と `-1`（全ビットが 1）だけは、期待どおりになります。

浮動小数点数は、全ビット 0 が `0.0` なので、ゼロクリアはできます。

`std::string` などの、コンストラクターを持つ型を `memset` で 0 にすると、内部の状態が壊れます。C++ では、`std::fill` か、`T{}` による値初期化を使います。

パスワードのような秘密を消す目的の `memset` は、コンパイラが「使われないから」と取り除くことがあります。この用途には、`memset_s` や `SecureZeroMemory`（Windows）を使います。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  int a[4];
  std::memset(a, 0, sizeof(a));  // ゼロクリア
  std::println("{} {} {} {}", a[0], a[1], a[2], a[3]);

  // int を 1 で埋めると、各バイトが 1 になる
  int b[1];
  std::memset(b, 1, sizeof(b));
  std::println("{}", b[0]);

  char buf[4];
  std::memset(buf, 'x', sizeof(buf) - 1);
  buf[3] = '\0';
  std::println("{}", buf);
}
```

```text title="実行結果"
0 0 0 0
16843009
xxx
```

## ゲームでの使いどころ

大きな配列や構造体を、ゼロクリアするときに使います。C++ では `T arr[N] = {};` でも同じです。

## よくあるミス

??? failure "int を 0 以外で埋める"
    各バイトが埋められるので、期待の値になりません。`std::fill` を使います。

??? failure "std::string などに使う"
    内部の状態が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::fill` | 型に合わせて埋める |
| `T{}` | 値初期化 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: memset](https://cpprefjp.github.io/reference/cstring/memset.html)
- [cppreference: memset](https://en.cppreference.com/w/cpp/string/byte/memset)
