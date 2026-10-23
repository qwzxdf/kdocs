---
title: 文字列・メモリ操作（cstring）
summary: "`memcpy`、`memset`、`strlen` などバイト列のコピーや比較。"
order: 63
tags:
  - メモリ
  - C由来
---

# 文字列・メモリ操作（cstring）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C 言語由来</span>
`#include <cstring>`
</div>

`<cstring>` は、C 言語から引き継いだ**メモリの塊の操作**（`memcpy`、`memset`、`memcmp`…）と、**C 文字列（`'\0'` で終わる `char` 配列）の操作**（`strlen`、`strcmp`、`strcpy`…）の関数が入ったヘッダです。C++ では `std::copy`、`std::fill`、`std::string`、`std::string_view` が代わりになるので、普段は使いません。ただし、**C のライブラリとのやり取り、バイナリデータの読み書き、速さが大事な低レベルのコード**では今でもよく出てきます。使うなら、「**型を無視してバイトとして扱う**」「**範囲の確認をしてくれない**」という性質を理解して、安全に使う必要があります。

!!! tip "ポイント"
    - <strong>普段は使わない。</strong> 代わりは `std::copy` / `std::fill` / `std::ranges::equal`、`std::string`、`std::string_view`。
    - 使うのは、**数値と構造体（trivially copyable な型）の、バイト単位のコピー・クリア・比較**だけ。
    - <strong>`memcpy` は、コピー元とコピー先が重なっていると未定義動作。</strong> 重なるなら `memmove`。
    - **`std::string` や `std::vector` のオブジェクトに `memcpy` / `memset` を使わない**（中のポインタを壊す）。
    - C 文字列関数（`strcpy`、`strcat`、`sprintf`）は**バッファの大きさを見ない**ので危ない。`std::string` や `std::format` を使う。
    - 型の変換のためなら、`memcpy` ではなく **`std::bit_cast`** を使う。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) と [未定義動作](../../basics/ub.md)、[malloc / free](malloc.md) を先に読むと分かりやすいです。文字列の C++ 版は [std::string](../containers/string.md) です。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`memcpy`](cstring/memcpy.md) | <span class="rank rank-often">よく使う</span> | メモリをコピーする |
| [`memset`](cstring/memset.md) | <span class="rank rank-often">よく使う</span> | メモリを同じバイトで埋める |
| [`memmove`](cstring/memmove.md) | <span class="rank rank-sometimes">たまに</span> | 重なっていてもよいコピー |
| [`memcmp`](cstring/memcmp.md) | <span class="rank rank-sometimes">たまに</span> | メモリを比べる |
| [`strlen`](cstring/strlen.md) | <span class="rank rank-often">よく使う</span> | C 文字列の長さ |
| [`strcmp`](cstring/strcmp.md) | <span class="rank rank-sometimes">たまに</span> | C 文字列を比べる |
| [`strncmp`](cstring/strncmp.md) | <span class="rank rank-sometimes">たまに</span> | 先頭の n 文字だけ比べる |
| [`memchr`](cstring/memchr.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリの中から 1 バイトを探す |
| [`strchr`](cstring/strchr.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列から 1 文字を探す |
| [`strstr`](cstring/strstr.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列から文字列を探す |
| [`strcpy`](cstring/strcpy.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列をコピー（**危ない**） |
| [`strncpy`](cstring/strncpy.md) | <span class="rank rank-rare">知ってるだけ</span> | n 文字までコピー（**終端に注意**） |
| [`strcat`](cstring/strcat.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列をつなげる（**危ない**） |
| [`snprintf`](cstring/snprintf.md) | <span class="rank rank-sometimes">たまに</span> | 大きさを指定して書式付きで書き込む |
| [`std::strncat`](cstring/strncat.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の末尾に、最大 n 文字を連結する。 |
| [`std::strrchr`](cstring/strrchr.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の中から、指定した文字が最後に現れる位置を探す。 |
| [`std::strspn`](cstring/strspn.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭から、指定した文字だけが続く長さを返す。 |
| [`std::strcspn`](cstring/strcspn.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭から、指定した文字を含まない部分の長さを返す。 |
| [`std::strpbrk`](cstring/strpbrk.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の中から、指定した文字のどれかが最初に現れる位置を探す。 |
| [`std::strtok`](cstring/strtok.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を、区切り文字で分割して 1 つずつ取り出す。 |
| [`std::strcoll`](cstring/strcoll.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールの規則で、2 つの文字列を比べる。 |
| [`std::strxfrm`](cstring/strxfrm.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールの規則での比較用に、文字列を変換する。 |
| [`std::strerror`](cstring/strerror.md) | <span class="rank rank-rare">知ってるだけ</span> | エラー番号（errno）を、説明の文字列にする。 |

## 置き換え早見表

| C の関数 | C++ で書くなら |
| --- | --- |
| `memcpy(dst, src, n * sizeof(T))` | `std::copy(src, src + n, dst)` / `std::ranges::copy` |
| `memset(p, 0, n * sizeof(T))` | `std::fill(p, p + n, T{})` / `std::ranges::fill` |
| `memcmp(a, b, n)` | `std::ranges::equal` / `a == b` |
| `strlen(s)` | `std::string_view(s).size()` |
| `strcmp(a, b) == 0` | `std::string_view(a) == b` |
| `strcpy` / `strcat` | `std::string` と `+=` |
| `sprintf` / `snprintf` | `std::format` / `std::format_to_n` |
| `memcpy` で型を読み替える | `std::bit_cast<To>(from)` |

`std::copy` などは、**型が trivially copyable（単純にコピーできる）ならコンパイラが `memcpy` と同じ命令に置き換えてくれる**ので、速さは変わりません。そのうえ、型が合わないときはエラーにしてくれます。

## よくある使い方

```cpp
#include <cstdint>
#include <cstring>
#include <print>

struct Header {
  std::uint32_t magic;
  std::uint16_t version;
  std::uint16_t count;
};

int main() {
  // バイト列（ファイルやネットワークから読んだもの）から、構造体に取り出す
  std::uint8_t bytes[8] = {0x4B, 0x44, 0x4F, 0x43, 0x02, 0x00, 0x05, 0x00};

  Header header;
  std::memcpy(&header, bytes, sizeof(header));  // バイトの並びをそのまま構造体にコピー

  std::println("magic={:#x} version={} count={}", header.magic, header.version, header.count);

  // 構造体を 0 で初期化する（C のライブラリに渡す構造体でよくやる）
  Header zero;
  std::memset(&zero, 0, sizeof(zero));
  std::println("zero.count={}", zero.count);
}
```

```text title="実行結果"
magic=0x434f444b version=2 count=5
zero.count=0
```

(この結果は、リトルエンディアンの CPU の場合です。PC・スマホ・ゲーム機は、ほぼすべてそうです。)

## 型の読み替えには std::bit_cast

`memcpy` は、「ある型のバイトを、別の型として読む」ために使われてきました。C++20 からは、**`std::bit_cast`**（[`<bit>`](../numeric/bit.md)）が、型の大きさが合っているかをコンパイル時に確認してくれる、安全な書き方です。

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  float f = 1.0f;
  auto bits = std::bit_cast<std::uint32_t>(f);  // float のビット列を整数として見る
  std::println("{:#x}", bits);
}
```

```text title="実行結果"
0x3f800000
```

!!! warning "ポインタのキャストで型を読み替えない"
    `*reinterpret_cast<std::uint32_t*>(&f)` は、規格では未定義動作（ストリクトエイリアシング違反）で、最適化で壊れることがあります。`memcpy` か `std::bit_cast` を使います。

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| `memcpy` / `memset` | CPU の最適な命令（AVX など）で、速い。メモリの速度が限界 |
| `strlen` | 最後まで数えるので O(n)。繰り返し呼ばない |
| `std::copy` / `std::fill` | trivially copyable な型なら、`memcpy` / `memset` と同じ速さ |
| `strcat` を繰り返す | 毎回先頭から終端を探すので O(n²) |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| ファイル・ネットワークのバイト列から構造体を取り出す | `memcpy`（エンディアンとパディングに注意） |
| C の API に渡す構造体を 0 で初期化 | `memset`（または `Header header{};` と書く） |
| 配列の中の要素をずらす | `memmove`（普通は `std::vector::insert` を使う） |
| ビット列の読み替え（`float` → `uint32_t`） | `std::bit_cast` |
| 固定長のデバッグ表示用バッファ | `snprintf`（長い文字は切られる） |

## よくあるミス

??? failure "`std::string` や `std::vector` を `memcpy` / `memset` する"
    ```cpp
    std::string a = "hello world, this is long";
    std::string b;
    std::memcpy(&b, &a, sizeof(a));  // 中のポインタがコピーされ、a と b が同じ文字列を指す
    ```
    `a` と `b` が同じヒープを指し、両方が破棄されるときに二重解放になります。必ずコピー代入（`b = a;`）を使います。

??? failure "memcpy の範囲が重なっている"
    同じ配列の中で、ずらしてコピーするときに `memcpy` を使うと未定義動作です。`memmove` を使います。

??? failure "`sizeof(ポインタ)` を渡す"
    ```cpp
    void Clear(int* data) { std::memset(data, 0, sizeof(data)); }  // 8 バイトしか消えない
    ```
    関数に渡された配列はポインタになっていて、`sizeof` は配列の大きさではなく、ポインタの大きさ（8 バイト）です。要素の数を別に受け取ります。

??? failure "`memset(a, 1, sizeof(a))` で int を 1 にしたつもりになる"
    バイトごとに `1` を入れるので、`int` は `0x01010101`（16843009）になります。0 以外で埋めたいなら `std::fill` を使います。

??? failure "`==` で C 文字列を比べる"
    `const char*` の `==` はアドレスの比較です。同じ内容でも、別の場所にあれば `false` になります。`std::strcmp(a, b) == 0` か、`std::string_view` を使います。

??? failure "構造体を `memcmp` で比べる"
    パディングのバイトが不定なので、メンバが同じでも「違う」と判定されることがあります。`operator==` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::copy` / `std::fill`](../algorithms/copy.md) | 型を見てくれる。単純な型なら `memcpy` と同じ速さ |
| [`std::string`](../containers/string.md) / [`std::string_view`](../utilities/string_view.md) | 長さを覚えている。C 文字列の関数はいらない |
| [`std::bit_cast`](../numeric/bit.md) | 型の読み替えを安全に行う |
| [`std::span`](../containers/span.md) | ポインタ + 長さをまとめて渡す。範囲を意識できる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普段は `std::copy` / `std::fill` / `std::string` / `std::string_view` を使う
    - [x] `memcpy` は重ならないコピー、重なるなら `memmove`
    - [x] クラス（`std::string` など）に `memcpy` / `memset` を使わない
    - [x] `strcpy` / `strcat` / `sprintf` は使わない。`snprintf` か `std::string`
    - [x] C 文字列を `==` で比べない。`strcmp` か `string_view`
    - [x] 型の読み替えは `std::bit_cast`

## 関連ページ

- [malloc / free（C 由来のメモリ確保）](malloc.md)
- [std::string](../containers/string.md)
- [std::string_view](../utilities/string_view.md)
- [<bit>（std::bit_cast）](../numeric/bit.md)
- [cppreference: <cstring>](https://en.cppreference.com/w/cpp/header/cstring)
