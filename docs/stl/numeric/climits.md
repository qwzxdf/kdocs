---
title: <climits>（整数の限界マクロ）
summary: "`INT_MAX` など、整数型の最大値・最小値を表す C 由来のマクロ。"
order: 30
tags:
  - 数値
---

# <climits>（整数の限界マクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <climits>`
</div>

`int` の最大値は 2147483647 です。これを覚えていなくても、`INT_MAX` と書けば、コンパイラが環境に合わせた値にしてくれます。`<climits>` は、整数型ごとの最大値・最小値と、1 バイトのビット数(`CHAR_BIT`)を、C のマクロで定義するヘッダーです。範囲の上限を超える計算を避ける、最小値を探すループの初期値を決める、といった場面で使います。

!!! tip "ポイント"
    - `INT_MAX` は 2147483647、`INT_MIN` は -2147483648(32 ビット `int` の場合)。
    - **`long` の大きさは環境で違う**。Windows(MSVC)は 32 ビット、64 ビット Linux は 64 ビット。
    - 符号付き整数のオーバーフローは未定義動作。足す前に `INT_MAX` と比べるか、大きい型で計算する。
    - `char` が符号付きか符号なしかは環境次第。`CHAR_MIN` で判別できる。
    - 新しいコードでは、型ごとに取れる `std::numeric_limits<int>::max()` を使ってもよい。

!!! info "このページを読む前に"
    [`std::numeric_limits`](limits.md) を先に読むと、同じ値を型ごとに取る書き方が分かります。ビット数を指定した型は [`<cstdint>`](cstdint.md) にあります。

## マクロの詳しい説明

マクロの名前は、`型の略称_MIN` / `型の略称_MAX` の形になっています。略称は、`SCHAR`(`signed char`)、`UCHAR`(`unsigned char`)、`SHRT`(`short`)、`USHRT`(`unsigned short`)、`INT`、`UINT`、`LONG`、`ULONG`、`LLONG`(`long long`)、`ULLONG`(`unsigned long long`)です。符号なしの型は最小値が常に 0 なので、`UINT_MIN` のようなマクロはありません。

値は、環境によって違うものがあります。次の表は、規格が保証する**最低限の大きさ**です。

| 型 | 規格が保証する最小のビット数 | MSVC (64 ビット) | GCC / Clang (64 ビット Linux) |
| --- | --- | --- | --- |
| `char` | 8 | 8 | 8 |
| `short` | 16 | 16 | 16 |
| `int` | 16 | 32 | 32 |
| `long` | 32 | 32 | 64 |
| `long long` | 64 | 64 | 64 |

`int` が 16 ビットで済む環境は、今はほとんどありませんが、`long` は 32 ビットと 64 ビットが混在しています。ここが、環境をまたぐコードで最もよく問題になります。

### <climits> {#climits}

```cpp
#include <climits>
```

C 言語の `<limits.h>` と同じ内容です。値は、`#if` でも使える定数式です。型ごとの値を、テンプレートの中で取りたいときは、[`std::numeric_limits`](limits.md) を使います。`std::numeric_limits<int>::max()` は `INT_MAX` と同じ値です。

### CHAR_BIT {#CHAR_BIT}

```cpp
#define CHAR_BIT 8
```

1 バイトのビット数です。今のほぼすべての環境で `8` です。規格は「8 以上」としか保証していないので、`8` を前提にするコードは、`static_assert(CHAR_BIT == 8)` を 1 行書いておくと、前提が崩れたときにすぐ気づけます。

型のビット数は、`sizeof(T) * CHAR_BIT` で求められます。ビット演算で「何ビットずらせるか」を計算するときなどに使います。

### SCHAR_MIN {#SCHAR_MIN}

```cpp
#define SCHAR_MIN -128
```

`signed char` の最小値です。2 の補数表現なら `-128` です。規格は `-127` 以下と定めています。

### SCHAR_MAX {#SCHAR_MAX}

```cpp
#define SCHAR_MAX 127
```

`signed char` の最大値で、`127` です。

### UCHAR_MAX {#UCHAR_MAX}

```cpp
#define UCHAR_MAX 255
```

`unsigned char` の最大値で、`255` です。色の 1 成分(0〜255)や、バイト列を扱う `std::uint8_t` の最大値と同じです。最小値は常に `0` なので、`UCHAR_MIN` はありません。

### CHAR_MIN {#CHAR_MIN}

```cpp
#define CHAR_MIN /* SCHAR_MIN か 0 */
```

**素の `char`** の最小値です。`char` が符号付きの環境では `SCHAR_MIN`(-128)、符号なしの環境では `0` になります。

`char` が符号付きか符号なしかは、環境(とコンパイラ オプション)で決まります。MSVC は既定で符号付きで、`/J` オプションを付けると符号なしになります。ARM 系の Linux 向けの GCC は、既定で符号なしです。

`CHAR_MIN < 0` なら符号付き、という判定ができます。`char` を数値として扱うコードは、この違いで動作が変わるので、`std::int8_t` か `std::uint8_t` を使います。

### CHAR_MAX {#CHAR_MAX}

```cpp
#define CHAR_MAX /* SCHAR_MAX か UCHAR_MAX */
```

素の `char` の最大値です。符号付きなら `127`、符号なしなら `255` です。

### SHRT_MIN {#SHRT_MIN}

```cpp
#define SHRT_MIN -32768
```

`short` の最小値で、16 ビットの符号付き整数の `-32768` です。音声の 16 ビット PCM の最小の振幅も、同じ値です。

### SHRT_MAX {#SHRT_MAX}

```cpp
#define SHRT_MAX 32767
```

`short` の最大値で、`32767` です。

### USHRT_MAX {#USHRT_MAX}

```cpp
#define USHRT_MAX 65535
```

`unsigned short` の最大値で、`65535` です。頂点インデックスを 16 ビットで持つときの、頂点数の上限(65,536 個)と同じ量です。

### INT_MIN {#INT_MIN}

```cpp
#define INT_MIN (-INT_MAX - 1)
```

`int` の最小値で、32 ビットなら `-2147483648` です。定義が `-INT_MAX - 1` の形になっているのは、`-2147483648` と書くと、`2147483648` がまず `int` に入らず、その符号を反転する形になってしまうからです。

`INT_MIN` を引数にした `std::abs` は、結果の `+2147483648` が `int` に入らないので、未定義動作です。符号を反転する処理(`-x`)も同じです。入力が `INT_MIN` になりうるなら、事前に確かめます。

### INT_MAX {#INT_MAX}

```cpp
#define INT_MAX 2147483647
```

`int` の最大値で、32 ビットなら `2147483647`(約 21 億)です。

`INT_MAX + 1` は、符号付き整数のオーバーフローで、未定義動作です。「あふれたら `INT_MIN` に戻る」とは限りません。足す前に `a > INT_MAX - b` で確かめるか、より大きい型(`std::int64_t`)で計算します。

最小値を探すループの初期値に `INT_MAX` を使う書き方は定番です。ただし、浮動小数点数の場合は `FLT_MAX` を使います。

### UINT_MAX {#UINT_MAX}

```cpp
#define UINT_MAX 4294967295u
```

`unsigned int` の最大値で、32 ビットなら `4294967295`(約 43 億)です。

符号なしの整数は、あふれると `0` に戻ります(modulo 2^N の算術)。これは定義された動作です。ハッシュの計算では、これを利用します。一方、`0 - 1` が `UINT_MAX` になるので、`size() - 1` が空のコンテナで巨大な値になる、という落とし穴の原因でもあります。

### LONG_MIN {#LONG_MIN}

```cpp
#define LONG_MIN /* 環境による */
```

`long` の最小値です。MSVC(Windows)では 32 ビットで `-2147483648`、64 ビット Linux の GCC / Clang では 64 ビットで `-9223372036854775808` です。

この違いが原因で、`long` を使ったコードは、Windows と Linux で結果が変わります。環境をまたぐコードでは、`long` を避け、`std::int32_t`・`std::int64_t`(`<cstdint>`)を使います。

### LONG_MAX {#LONG_MAX}

```cpp
#define LONG_MAX /* 環境による */
```

`long` の最大値です。MSVC では `2147483647`、64 ビット Linux では `9223372036854775807` です。

### ULONG_MAX {#ULONG_MAX}

```cpp
#define ULONG_MAX /* 環境による */
```

`unsigned long` の最大値です。MSVC では `4294967295`、64 ビット Linux では `18446744073709551615` です。Windows API の `DWORD` は `unsigned long` なので、Windows では 32 ビットです。

### LLONG_MIN {#LLONG_MIN}

```cpp
#define LLONG_MIN (-LLONG_MAX - 1)
```

`long long` の最小値で、`-9223372036854775808` です。`long long` は C++11 から標準で、どの環境でも 64 ビット以上です。

### LLONG_MAX {#LLONG_MAX}

```cpp
#define LLONG_MAX 9223372036854775807
```

`long long` の最大値で、約 922 京です。所持金やタイムスタンプで、`int` に入らない大きな値が要るときに使う型の上限です。

### ULLONG_MAX {#ULLONG_MAX}

```cpp
#define ULLONG_MAX 18446744073709551615ull
```

`unsigned long long` の最大値で、約 1845 京です。64 ビットのハッシュ値や ID を入れる型の上限です。

### MB_LEN_MAX {#MB_LEN_MAX}

```cpp
#define MB_LEN_MAX /* 環境による */
```

マルチバイト文字 1 文字を表すために必要な、最大のバイト数です。UTF-8 なら 4 バイトまでですが、`MB_LEN_MAX` は、すべてのロケールの最大です。MSVC では `5`、glibc では `16` です。

マルチバイト文字を変換する関数に渡す、バッファの大きさを決めるときに使います。UTF-8 を前提にするなら、4 バイトで足ります。

## 実際に動かしてみる

```cpp
#include <climits>
#include <print>

// a + b がオーバーフローするかを、足す前に調べる
bool AddWouldOverflow(int a, int b) {
  if (b > 0) return a > INT_MAX - b;
  return a < INT_MIN - b;
}

int main() {
  static_assert(CHAR_BIT == 8);   // この前提で書いたコードは、ここで確かめておく

  std::println("char の符号: {}", CHAR_MIN < 0 ? "符号付き" : "符号なし");
  std::println("short: {} .. {}", SHRT_MIN, SHRT_MAX);
  std::println("int: {} .. {}", INT_MIN, INT_MAX);
  std::println("unsigned int: 0 .. {}", UINT_MAX);
  std::println("long: {} .. {}", LONG_MIN, LONG_MAX);
  std::println("long long: {} .. {}", LLONG_MIN, LLONG_MAX);
  std::println("sizeof(long) = {}", sizeof(long));

  // 符号なしは、あふれると 0 に戻る(定義された動作)
  unsigned int u = UINT_MAX;
  ++u;
  std::println("UINT_MAX + 1 = {}", u);

  // 符号付きは、あふれると未定義動作なので、足す前に調べる
  std::println("INT_MAX + 1 は危ない: {}", AddWouldOverflow(INT_MAX, 1));
  std::println("100 + 200 は安全: {}", !AddWouldOverflow(100, 200));
}
```

```text title="実行結果（MSVC）"
char の符号: 符号付き
short: -32768 .. 32767
int: -2147483648 .. 2147483647
unsigned int: 0 .. 4294967295
long: -2147483648 .. 2147483647
long long: -9223372036854775808 .. 9223372036854775807
sizeof(long) = 4
UINT_MAX + 1 = 0
INT_MAX + 1 は危ない: true
100 + 200 は安全: true
```

`long` の範囲は、環境によって違います(上の結果は MSVC のもの)。64 ビット Linux の GCC / Clang では、`long` が 64 ビットになり、`sizeof(long)` は 8、範囲は `long long` と同じになります。

## ゲームでの使いどころ

最小値を探すループ(いちばん近い敵、いちばん安い武器)の初期値に `INT_MAX` を使うのが定番です。ダメージや所持金のような、あふれると困る値に上限を設けるときも、`INT_MAX` を目安にします。

```cpp
int AddGold(int gold, int amount) {
  if (amount > 0 && gold > INT_MAX - amount) return INT_MAX;   // 上限で止める
  return gold + amount;
}
```

セーブデータや通信のように、環境をまたぐ値を扱うときは、`long` を避けて `std::int32_t`・`std::int64_t` を使います。その上限は、`INT32_MAX`・`INT64_MAX`([`<cstdint>`](cstdint.md))です。

## よくあるミス

??? failure "INT_MAX + 1 が INT_MIN に戻ると思う"
    符号付き整数のオーバーフローは未定義動作です。最適化で、条件分岐ごと消されることもあります。足す前に `a > INT_MAX - b` で確かめるか、`std::int64_t` で計算します。

??? failure "long を 32 ビットだと思って、他の環境に持ち込む"
    Windows では 32 ビットでも、64 ビット Linux では 64 ビットです。ファイルに `long` をそのまま書き出すと、環境が違うと読めなくなります。

??? failure "abs(INT_MIN) を計算する"
    結果の `2147483648` が `int` に入らないので、未定義動作です。入力が `INT_MIN` になりうるなら、事前に除外します。

??? failure "素の char を数値として扱う"
    `char` が符号付きの環境と符号なしの環境があり、`255` を入れた値が `-1` になったりならなかったりします。数値には `std::uint8_t` か `std::int8_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型ごとに取れる C++ の書き方。テンプレートの中で便利 |
| [`<cstdint>`](cstdint.md) | ビット数が決まった型と、その最大値のマクロ(`INT32_MAX` など) |
| [`<cfloat>`](cfloat.md) | 浮動小数点数の限界のマクロ |

## コンパイラ対応

C++98 から使えます。`LLONG_MIN` などの `long long` 用のマクロは C++11 からです。

## 関連ページ

- [cpprefjp: <climits>（整数の限界マクロ）](https://cpprefjp.github.io/reference/climits.html)
- [cppreference: <climits>（整数の限界マクロ）](https://en.cppreference.com/w/cpp/types/climits)
