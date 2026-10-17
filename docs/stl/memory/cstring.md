---
title: 文字列・メモリ操作（cstring）
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
    [ポインタ](../../basics/pointer.md) と [未定義動作](../../basics/ub.md)、[malloc / free](c-memory.md) を先に読むと分かりやすいです。文字列の C++ 版は [std::string](../containers/string.md) です。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`memcpy`](#memcpy) | <span class="rank rank-often">よく使う</span> | メモリをコピーする |
| [`memset`](#memset) | <span class="rank rank-often">よく使う</span> | メモリを同じバイトで埋める |
| [`memmove`](#memmove) | <span class="rank rank-sometimes">たまに</span> | 重なっていてもよいコピー |
| [`memcmp`](#memcmp) | <span class="rank rank-sometimes">たまに</span> | メモリを比べる |
| [`strlen`](#strlen) | <span class="rank rank-often">よく使う</span> | C 文字列の長さ |
| [`strcmp`](#strcmp) | <span class="rank rank-sometimes">たまに</span> | C 文字列を比べる |
| [`strncmp`](#strncmp) | <span class="rank rank-sometimes">たまに</span> | 先頭の n 文字だけ比べる |
| [`memchr`](#memchr) | <span class="rank rank-rare">知ってるだけ</span> | メモリの中から 1 バイトを探す |
| [`strchr`](#strchr) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列から 1 文字を探す |
| [`strstr`](#strstr) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列から文字列を探す |
| [`strcpy`](#strcpy) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列をコピー（**危ない**） |
| [`strncpy`](#strncpy) | <span class="rank rank-rare">知ってるだけ</span> | n 文字までコピー（**終端に注意**） |
| [`strcat`](#strcat) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列をつなげる（**危ない**） |
| [`snprintf`](#snprintf) | <span class="rank rank-sometimes">たまに</span> | 大きさを指定して書式付きで書き込む |

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

## 関数の詳しい説明

### memcpy {#memcpy}

```cpp
void* memcpy(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーする**バイト数** |

- 戻り値: `dest`
- 計算量: O(count)。とても速い（CPU の命令でまとめてコピーされる）
- **`dest` と `src` が重なっていると未定義動作**です。重なる可能性があるなら `memmove` を使います
- **`dest` / `src` が `nullptr` は `count` が 0 でも未定義動作**です
- コピーする型は **trivially copyable**（コンストラクタ・デストラクタ・コピーの処理が単純なもの）に限ります。`std::string`、`std::vector`、`std::unique_ptr`、仮想関数を持つクラスは**壊れます**

<div class="anim" data-label="memcpy(dst, src, 3 * sizeof(int))">
1 2 3 4 | _ _ _ _ # src と dst
1 2 3 4 | +1 _ _ _ # 先頭から順にコピーされる
1 2 3 4 | +1 +2 +3 _ # 指定したバイト数だけ。それ以降は変わらない
</div>

### memset {#memset}

```cpp
void* memset(void* dest, int ch, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | 埋める先頭 |
| `ch` | `int` | 埋めるバイトの値（`unsigned char` に変換される） |
| `count` | `std::size_t` | 埋める**バイト数** |

- 戻り値: `dest`
- **1 バイトずつ**同じ値で埋めます。`memset(a, 1, sizeof(a))` で `int` の配列を埋めると、各要素は `1` ではなく `0x01010101` になります。**0 で埋めるとき以外は、基本使いません**（`std::fill` を使う）
- 浮動小数点やポインタを 0 で埋めると、環境によっては 0.0 や `nullptr` にならないことがあります（実際のゲーム機・PC ではなります）
- クラスのオブジェクトに使うと、中身（ポインタや仮想関数テーブル）を壊します。**`std::string` や仮想関数を持つクラスに `memset` してはいけません**

### memmove {#memmove}

```cpp
void* memmove(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーする**バイト数** |

- 戻り値: `dest`
- `memcpy` と違い、**`src` と `dest` が重なっていても正しくコピーされます**（元のデータを壊さない順番で動かす）
- 配列の中で、要素をずらすときに使います（`std::vector::insert` の中身がこれです）

<div class="anim" data-label="memmove(a + 1, a, 3 * sizeof(int))  ※重なっている">
1 2 3 4 _ # 配列 a
1 2 3 3 4 # 後ろから順に動かす（元のデータを壊さない）
1 1 2 3 4 # 全部 1 つ後ろへ移った
</div>

### memcmp {#memcmp}

```cpp
int memcmp(const void* lhs, const void* rhs, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const void*` | 比べる 2 つの領域 |
| `count` | `std::size_t` | 比べる**バイト数** |

- 戻り値: 等しければ 0。最初に違うバイトが `lhs` の方が小さければ負、大きければ正（**値の大きさは決まっていない**。符号だけ見る）
- バイトを 1 つずつ比べるだけです。**数値としての大小の比較にはなりません**（リトルエンディアンの `int` では、バイトの順番が逆になるため）
- 構造体の比較に使うのは危険です。**パディング**（隙間のバイト）に不定な値が入っていると、メンバが同じでも「違う」と判定されます。`float` も、`0.0` と `-0.0`、`NaN` で結果が変わります。`operator==`（`= default` でよい）を使います

### strlen {#strlen}

```cpp
std::size_t strlen(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | `'\0'` で終わる文字列 |

- 戻り値: 終端の `'\0'` を**数えない**文字数（バイト数）
- 計算量: O(n)。文字列を最後まで数えるので、ループの条件の中で毎回呼ぶと遅くなります
- 終端の `'\0'` がない配列に使うと、範囲外を読み続けます（未定義動作）
- UTF-8 の日本語は 1 文字が 3 バイトなので、`strlen("あ")` は 3 です。**文字数ではなくバイト数**です

### strcmp {#strcmp}

```cpp
int strcmp(const char* lhs, const char* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const char*` | 比べる 2 つの C 文字列 |

- 戻り値: 等しければ 0、`lhs` が辞書順で前なら負、後ろなら正
- <strong>`==` で比べてはいけません。</strong> `const char*` の `==` は、**文字列の中身ではなく、アドレスを比べる**からです。`std::string_view(a) == b` と書けば、中身で比べられます

### strncmp {#strncmp}

```cpp
int strncmp(const char* lhs, const char* rhs, std::size_t count);
```

| 引数 | 意味 |
| --- | --- |
| `lhs`, `rhs` | 比べる C 文字列 |
| `count` | 先頭から最大でこの文字数だけ比べる |

- 戻り値: `strcmp` と同じ
- 「先頭が `"enemy_"` で始まるか」の判定に使えます（`std::string_view::starts_with` のほうが簡単です）

### memchr {#memchr}

```cpp
const void* memchr(const void* ptr, int ch, std::size_t count);
```

| 引数 | 意味 |
| --- | --- |
| `ptr` | 探す領域の先頭 |
| `ch` | 探すバイトの値 |
| `count` | 探す範囲のバイト数 |

- 戻り値: 最初に見つかった場所のポインタ。なければ `nullptr`
- バイナリデータの中から、区切りのバイトを探すときに使います

### strchr {#strchr}

```cpp
const char* strchr(const char* str, int ch);
```

| 引数 | 意味 |
| --- | --- |
| `str` | 探す C 文字列 |
| `ch` | 探す文字 |

- 戻り値: 最初に見つかった位置のポインタ。なければ `nullptr`。`ch` に `'\0'` を渡すと、終端の位置が返る
- `std::string_view::find` のほうが安全です。

### strstr {#strstr}

```cpp
const char* strstr(const char* str, const char* substr);
```

| 引数 | 意味 |
| --- | --- |
| `str` | 探される C 文字列 |
| `substr` | 探す C 文字列 |

- 戻り値: 最初に見つかった位置のポインタ。なければ `nullptr`
- `std::string_view::find` / `contains` を使うほうが、長さを保てて安全です。

### strcpy {#strcpy}

```cpp
char* strcpy(char* dest, const char* src);
```

| 引数 | 意味 |
| --- | --- |
| `dest` | コピー先（`src` の長さ + 1 以上の大きさが必要） |
| `src` | コピー元の C 文字列 |

- 戻り値: `dest`
- <strong>コピー先の大きさを一切チェックしません。</strong> `src` が長いと、`dest` の後ろを壊します（バッファオーバーフロー）。セキュリティの穴の原因として有名です。**使ってはいけません**（MSVC は警告 C4996 を出します）
- `std::string` に入れるか、`snprintf` で大きさを指定します。

### strncpy {#strncpy}

```cpp
char* strncpy(char* dest, const char* src, std::size_t count);
```

| 引数 | 意味 |
| --- | --- |
| `dest` | コピー先 |
| `src` | コピー元 |
| `count` | コピーする最大の文字数 |

- 戻り値: `dest`
- 安全そうに見えますが、**`src` が `count` 以上の長さのとき、終端の `'\0'` を書いてくれません**。そのまま `strlen` や `printf` に渡すと範囲外を読みます。短いときは、残りを `'\0'` で埋めるので、無駄に遅い場合もあります
- 使うなら、最後に自分で `dest[count - 1] = '\0';` と書きます。基本は `std::string` を使います

### strcat {#strcat}

```cpp
char* strcat(char* dest, const char* src);
```

| 引数 | 意味 |
| --- | --- |
| `dest` | つなげる先（すでに C 文字列が入っている。十分な大きさが必要） |
| `src` | 後ろにつなげる C 文字列 |

- 戻り値: `dest`
- `strcpy` と同じで、**大きさのチェックがありません**。つなげるたびに先頭から終端を探すので、繰り返すと O(n²) です。`std::string` の `+=` を使います

### snprintf {#snprintf}

```cpp
int snprintf(char* buffer, std::size_t bufsz, const char* format, ...);  // <cstdio>
```

| 引数 | 意味 |
| --- | --- |
| `buffer` | 書き込み先 |
| `bufsz` | `buffer` の大きさ（終端の `'\0'` を含む） |
| `format` | `printf` 形式の書式 |

- 戻り値: **書き込めていれば書かれたはずの文字数**（`bufsz` 以上なら、切り捨てられている）
- 必ず終端の `'\0'` を書いてくれる、**大きさを守る安全な書式付き出力**です（`sprintf` は大きさを見ないので使いません）
- C++ では、[`std::format_to_n`](../utilities/format.md#format_to_n) が型安全な代わりです。

```cpp
char label[16];
std::snprintf(label, sizeof(label), "HP %d/%d", 30, 100);  // 長すぎても、15 文字で切れて安全
```

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
| `memcpy` / `memset` | CPU の最適な命令（AVX など）で、非常に速い。メモリの速度が限界 |
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

## 理解度チェック

!!! question "Q1. 配列 `a` の要素を 1 つ後ろにずらすのに、`memcpy(a + 1, a, n * sizeof(int))` は使える？"
    <div class="spoiler" markdown>

    **答え:** 使えません。コピー元とコピー先が重なっているので、未定義動作です。`memmove` か、`std::copy_backward` を使います。

    </div>

!!! question "Q2. `char buf[8]; strcpy(buf, \"hello world\");` の問題は？"
    <div class="spoiler" markdown>

    **答え:** `"hello world"` は終端を含めて 12 バイトで、`buf` は 8 バイトなので、後ろの 4 バイトが範囲外に書かれます（バッファオーバーフロー）。`snprintf(buf, sizeof(buf), "%s", ...)` か `std::string` を使います。

    </div>

!!! question "Q3. `float` のビット列を `uint32_t` として読みたい。一番良い書き方は？"
    <div class="spoiler" markdown>

    **答え:** `std::bit_cast<std::uint32_t>(f)`（C++20）です。型の大きさが違うとコンパイルエラーになります。昔は `memcpy` を使っていました。ポインタのキャストは未定義動作です。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::copy` / `std::fill`](../algorithms/copy_fill.md) | 型を見てくれる。単純な型なら `memcpy` と同じ速さ |
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

- [malloc / free（C 由来のメモリ確保）](c-memory.md)
- [std::string](../containers/string.md)
- [std::string_view](../utilities/string_view.md)
- [<bit>（std::bit_cast）](../numeric/bit.md)
- [cppreference: <cstring>](https://en.cppreference.com/w/cpp/header/cstring)
