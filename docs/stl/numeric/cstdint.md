---
title: <cstdint>（大きさの決まった整数型）
summary: "`std::int32_t` など大きさが決まった整数の型。"
order: 71
tags:
  - 数値
---

# &lt;cstdint&gt;（大きさの決まった整数型）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` は、環境によって大きさが違います。`long` は Windows では 32 ビットで、Linux では 64 ビットです。セーブデータをファイルに書き出すとき、この違いでデータが読めなくなったら困ります。`<cstdint>` は、ビット数がはっきり決まった整数型（`std::int32_t`、`std::uint8_t` など）を用意するヘッダーです。ファイル、通信、ビット操作では、この型を使います。

!!! tip "ポイント"
    - **ファイル・通信・ビット操作では大きさの決まった型**（`std::int32_t`、`std::uint64_t` など）を使う。
    - 普通の計算（ループのカウンタ、HP）は `int` で十分。
    - 0〜255 の小さな値（色など）は `std::uint8_t`。ただし `std::cout` で出すと文字として表示されるので注意。
    - 大きさ・個数は `std::size_t`（`<cstddef>`）。

!!! info "このページを読む前に"
    整数型の大きさと符号の基本が分かると読みやすいです。ビット演算は[ビット演算](../../basics/bit-operations.md)の基本を先に読んでください。

## 主な型

よく使う順です。

| 型 | 重要度 | ビット数 | 範囲 | 使う場面 |
| --- | --- | --- | --- | --- |
| [`std::int32_t`](cstdint/int32_t.md) | <span class="rank rank-often">よく使う</span> | 32 | 約 -21 億〜21 億 | セーブデータの数値 |
| [`std::uint32_t`](cstdint/uint32_t.md) | <span class="rank rank-often">よく使う</span> | 32 | 0〜約 43 億 | ID、フラグ、色（RGBA） |
| [`std::uint8_t`](cstdint/uint8_t.md) | <span class="rank rank-often">よく使う</span> | 8 | 0〜255 | 色の各成分、バイト列 |
| [`std::int64_t`](cstdint/int64_t.md) | <span class="rank rank-often">よく使う</span> | 64 | 約 ±922 京 | 所持金、タイムスタンプ |
| [`std::uint64_t`](cstdint/uint64_t.md) | <span class="rank rank-sometimes">たまに</span> | 64 | 0〜約 1845 京 | ハッシュ値、ハンドル |
| [`std::int16_t`](cstdint/int16_t.md) | <span class="rank rank-sometimes">たまに</span> | 16 | -32768〜32767 | 音声データ（16bit PCM） |
| [`std::uint16_t`](cstdint/uint16_t.md) | <span class="rank rank-sometimes">たまに</span> | 16 | 0〜65535 | 小さなファイル形式、タイルの番号 |
| [`std::int8_t`](cstdint/int8_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 8 | -128〜127 | |
| [`std::size_t`](#size_t) | <span class="rank rank-must">必須</span> | 環境による（64bit なら 64） | 0〜 | 大きさ・個数・添字（`<cstddef>`） |
| [`std::ptrdiff_t`](#ptrdiff_t) | <span class="rank rank-sometimes">たまに</span> | 環境による | 符号付き | ポインタ・イテレータの差 |
| [`std::intptr_t`](cstdint/intptr_t.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタと同じ | 符号付き | ポインタを整数として扱う |
| [`std::uintptr_t`](cstdint/uintptr_t.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタと同じ | 符号なし | ポインタを整数として扱う |
| [`std::int_fast32_t`](cstdint/int_fast32_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 32 以上で一番速い | | |
| [`std::int_least32_t`](cstdint/int_least32_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 32 以上で一番小さい | | |

## よくある使い方

```cpp
#include <cstdint>
#include <print>

struct Color {
  std::uint8_t r;
  std::uint8_t g;
  std::uint8_t b;
  std::uint8_t a;
};

constexpr std::uint32_t Pack(Color c) {
  return (std::uint32_t{c.r} << 24) | (std::uint32_t{c.g} << 16) | (std::uint32_t{c.b} << 8) |
         c.a;
}

int main() {
  Color orange{255, 136, 0, 255};
  std::println("#{:08X} / {} バイト", Pack(orange), sizeof(Color));
  std::int64_t gold = 3'000'000'000;  // int だと入らない
  std::println("{}", gold);
}
```

```text title="実行結果"
#FF8800FF / 4 バイト
3000000000
```

## 型の詳しい説明

### std::size_t {#size_t}

```cpp
#include <cstddef>
```

- `sizeof` の結果や、コンテナの `size()` の型。64 ビット環境では 64 ビットの符号なし整数です。**マイナスにならない**ので、`size() - 1` に注意（[vector のよくあるミス](../containers/vector.md#よくあるミス)）

### std::ptrdiff_t {#ptrdiff_t}

- ポインタやイテレータの差の型（符号付き）。`std::ssize(v)` もこの型を返します

## 全部の型

| 型 | 符号 | 種類 |
| --- | --- | --- |
| [`std::int8_t`](cstdint/int8_t.md) | 符号付き | ちょうど |
| [`std::uint8_t`](cstdint/uint8_t.md) | 符号なし | ちょうど |
| [`std::int_fast8_t`](cstdint/int_fast8_t.md) | 符号付き | 最も速い |
| [`std::uint_fast8_t`](cstdint/uint_fast8_t.md) | 符号なし | 最も速い |
| [`std::int_least8_t`](cstdint/int_least8_t.md) | 符号付き | 最も小さい |
| [`std::uint_least8_t`](cstdint/uint_least8_t.md) | 符号なし | 最も小さい |
| [`std::int16_t`](cstdint/int16_t.md) | 符号付き | ちょうど |
| [`std::uint16_t`](cstdint/uint16_t.md) | 符号なし | ちょうど |
| [`std::int_fast16_t`](cstdint/int_fast16_t.md) | 符号付き | 最も速い |
| [`std::uint_fast16_t`](cstdint/uint_fast16_t.md) | 符号なし | 最も速い |
| [`std::int_least16_t`](cstdint/int_least16_t.md) | 符号付き | 最も小さい |
| [`std::uint_least16_t`](cstdint/uint_least16_t.md) | 符号なし | 最も小さい |
| [`std::int32_t`](cstdint/int32_t.md) | 符号付き | ちょうど |
| [`std::uint32_t`](cstdint/uint32_t.md) | 符号なし | ちょうど |
| [`std::int_fast32_t`](cstdint/int_fast32_t.md) | 符号付き | 最も速い |
| [`std::uint_fast32_t`](cstdint/uint_fast32_t.md) | 符号なし | 最も速い |
| [`std::int_least32_t`](cstdint/int_least32_t.md) | 符号付き | 最も小さい |
| [`std::uint_least32_t`](cstdint/uint_least32_t.md) | 符号なし | 最も小さい |
| [`std::int64_t`](cstdint/int64_t.md) | 符号付き | ちょうど |
| [`std::uint64_t`](cstdint/uint64_t.md) | 符号なし | ちょうど |
| [`std::int_fast64_t`](cstdint/int_fast64_t.md) | 符号付き | 最も速い |
| [`std::uint_fast64_t`](cstdint/uint_fast64_t.md) | 符号なし | 最も速い |
| [`std::int_least64_t`](cstdint/int_least64_t.md) | 符号付き | 最も小さい |
| [`std::uint_least64_t`](cstdint/uint_least64_t.md) | 符号なし | 最も小さい |
| [`std::intmax_t`](cstdint/intmax_t.md) | 符号付き | 最大 |
| [`std::uintmax_t`](cstdint/uintmax_t.md) | 符号なし | 最大 |
| [`std::intptr_t`](cstdint/intptr_t.md) | 符号付き | ポインタ用 |
| [`std::uintptr_t`](cstdint/uintptr_t.md) | 符号なし | ポインタ用 |

## 型の選び方(ちょうど・最速・最小) {#choose}

型の名前は、`int` に続けて**幅**(ビット数)を付けた形をしています。幅の前の語で、意味が 3 通りに分かれます。

| 名前の形 | 意味 |
| --- | --- |
| `int32_t` のように幅だけ | **ちょうど** 32 ビット。その幅の型がない環境では、型そのものが存在しない |
| `int_fast32_t` | **32 ビット以上**で、その環境で最も速く計算できる型 |
| `int_least32_t` | **32 ビット以上**で、最も小さい型 |

#### ちょうど(`int32_t` など)

ファイルや通信の形式は、幅がぴったり決まっていないと困るので、ここで使うのはこの型です。8・16・32・64 ビットの整数と、2 の補数表現の環境（ほぼすべて）にだけ存在します。ない環境では、その名前を書くだけでコンパイルエラーになるので、気づかず壊れることはありません。

`std::uint8_t` は、普通は `unsigned char` の別名です。そのため、`std::cout << x` では文字として出力されます。数値として出したいときは、`static_cast<int>(x)` にするか、`std::println` を使います。

#### 最速(`int_fast32_t` など)

「最低 N ビットあれば足りて、速さが欲しい」ときの型です。たとえば、MSVC の `int_fast16_t` は 32 ビットの `int` です。16 ビット命令より、32 ビット命令のほうが速いためです。環境ごとに幅が変わるので、ファイルや通信の形式には使えません。

#### 最小(`int_least32_t` など)

「最低 N ビットあって、メモリを節約したい」ときの型です。多くの環境では、ちょうどの型と同じ大きさです。

ふつうは、幅がいらない計算には `int` で十分です。`fast` や `least` を使うのは、幅の違う環境に移植するライブラリを書くときぐらいです。

#### そのほかの型

- `std::intmax_t` / `std::uintmax_t`: その環境で最も幅の広い整数。`std::ratio` や `std::chrono` が内部で使っている
- `std::intptr_t` / `std::uintptr_t`: ポインターを整数に直して、また戻せる幅の型。ポインターの値を整数として扱うビット演算に使う（どの環境にもあるとは限らない）
- `std::size_t`: オブジェクトの大きさと個数の型。`<cstddef>` にある
- `std::ptrdiff_t`: ポインター(イテレータ)どうしの差の型。符号付き

### 実際に動かす: 型の大きさ {#sizes}

```cpp
#include <cstdint>
#include <print>
#include <type_traits>

int main() {
  // 型のバイト数: ちょうど / 最速 / 最小
  std::println("int8_t   {} / fast {} / least {}", sizeof(std::int8_t), sizeof(std::int_fast8_t), sizeof(std::int_least8_t));
  std::println("int16_t  {} / fast {} / least {}", sizeof(std::int16_t), sizeof(std::int_fast16_t), sizeof(std::int_least16_t));
  std::println("int32_t  {} / fast {} / least {}", sizeof(std::int32_t), sizeof(std::int_fast32_t), sizeof(std::int_least32_t));
  std::println("int64_t  {} / fast {} / least {}", sizeof(std::int64_t), sizeof(std::int_fast64_t), sizeof(std::int_least64_t));
  std::println("intmax_t {}, intptr_t {}, size_t {}", sizeof(std::intmax_t), sizeof(std::intptr_t), sizeof(std::size_t));

  // uint8_t は、普通は unsigned char の別名
  std::println("uint8_t は unsigned char: {}", std::is_same_v<std::uint8_t, unsigned char>);
  std::println("int64_t は long long: {}", std::is_same_v<std::int64_t, long long>);
}
```

```text title="実行結果（MSVC）"
int8_t   1 / fast 1 / least 1
int16_t  2 / fast 4 / least 2
int32_t  4 / fast 4 / least 4
int64_t  8 / fast 8 / least 8
intmax_t 8, intptr_t 8, size_t 8
uint8_t は unsigned char: true
int64_t は long long: true
```

MSVC では `int_fast16_t` が 4 バイトになっています。`int_fast8_t` は 1 バイトのままです。glibc(Linux)では、`int_fast16_t` が 8 バイトのように、環境で違う値になります。

## 限界値と定数を作るマクロ {#macros}

各型には、最小値・最大値のマクロがあります。名前は、`型名から _t を除いて大文字にした名前_MAX` / `_MIN` です。`int32_t` なら `INT32_MIN`・`INT32_MAX`、`uint8_t` なら `UINT8_MAX` です。符号なしの型の最小値は常に 0 なので、`UINT32_MIN` はありません。

整数リテラルを、特定の型にするマクロもあります。`INT64_C(1)` は、`1` を `int64_t` の幅の定数にします(環境によって `1L` や `1LL`)。

### SIZE_MAX {#SIZE_MAX}

```cpp
#define SIZE_MAX /* std::size_t の最大値 */
```

`std::size_t` で表せる最大値です。64 ビット環境では 18446744073709551615 です。「見つからなかった」を表す値として、`std::string::npos` が使っているのと同じ値で、`std::size_t` に `-1` を入れた値とも一致します。

`size_t` の `-1` を無自覚に使うより、`SIZE_MAX` と書いたほうが、意図が読み取れます。

### INT32_MAX {#INT32_MAX}

```cpp
#define INT32_MAX 2147483647
```

`std::int32_t` の最大値で、2147483647 です。`int` が 32 ビットの環境では `INT_MAX` と同じ値ですが、`INT32_MAX` は、幅が 32 ビットだと明示した型の限界である点が違います。セーブデータの形式のように、幅を 32 ビットに決めている数値の範囲検査には、こちらを使います。最小値の `INT32_MIN` は -2147483648 です。

### INT64_MAX {#INT64_MAX}

```cpp
#define INT64_MAX 9223372036854775807
```

`std::int64_t` の最大値で、約 922 京です。所持金やタイムスタンプなど、`int` に収まらない値の上限に使います。最小値の `INT64_MIN` は -9223372036854775808 です。

`std::int64_t` の実体は、MSVC では `long long`、64 ビットの Linux では `long` です。`printf` の書式指定で `%lld` と `%ld` が変わってしまうので、`std::println` を使うか、`<cinttypes>` の `PRId64` を使います。

### UINT32_MAX {#UINT32_MAX}

```cpp
#define UINT32_MAX 4294967295u
```

`std::uint32_t` の最大値で、4294967295(約 43 億)です。ID や RGBA の色のように、符号がいらない 32 ビット値の上限に使います。

### UINT64_MAX {#UINT64_MAX}

```cpp
#define UINT64_MAX 18446744073709551615ull
```

`std::uint64_t` の最大値で、約 1845 京です。64 ビットのハッシュ値の取りうる最大値です。

### 実際に動かす: マクロ {#macro-sample}

```cpp
#include <cstdint>
#include <limits>
#include <print>
#include <string>

int main() {
  // 最大値のマクロは、型 std::numeric_limits<> と同じ値
  static_assert(INT32_MAX == std::numeric_limits<std::int32_t>::max());
  static_assert(UINT64_MAX == std::numeric_limits<std::uint64_t>::max());
  std::println("INT32_MAX  = {}", INT32_MAX);
  std::println("UINT32_MAX = {}", UINT32_MAX);
  std::println("INT64_MAX  = {}", INT64_MAX);
  std::println("UINT64_MAX = {}", UINT64_MAX);
  std::println("SIZE_MAX == npos: {}", SIZE_MAX == std::string::npos);

  // 64 ビットでシフトするときは、定数も 64 ビットにする
  std::int64_t small = 1 << 20;            // 20 ビットなら int でも収まる
  std::int64_t right = INT64_C(1) << 40;   // 40 ビットずらすなら、1 を 64 ビットにしておく
  std::println("1 << 20 = {}, INT64_C(1) << 40 = {}", small, right);
}
```

```text title="実行結果"
INT32_MAX  = 2147483647
UINT32_MAX = 4294967295
INT64_MAX  = 9223372036854775807
UINT64_MAX = 18446744073709551615
SIZE_MAX == npos: true
1 << 20 = 1048576, INT64_C(1) << 40 = 1099511627776
```

`1 << 40` と書くと、`1` が `int`(32 ビット)なので、40 ビットのシフトは未定義動作です。`INT64_C(1)` を使うか、`std::int64_t{1} << 40` と書きます。

## ゲームでの使いどころ

セーブデータとネットワークの通信で、大きさの決まった型を使います。ファイルの先頭にバージョンを `std::uint32_t` で書き、次に件数、データ、と続ける形式なら、環境が違っても同じファイルが読めます。

色は、0〜255 の値を持つので `std::uint8_t` を使います。RGBA を 1 つの `std::uint32_t` に詰める表現もよくあります。ビットフラグも、幅が決まった型にします。

大きさや個数には、`std::size_t` を使います。普通の計算（ループのカウンター、HP）には、`int` で十分です。むやみに `int32_t` へ置き換えると、かえって読みにくくなります。

## よくあるミス

??? failure "uint8_t を cout で出して文字化け"
    `std::cout << static_cast<int>(x)` にするか、`std::println` を使います。

??? failure "符号なし整数でマイナスの計算"
    `std::uint32_t a = 3; a - 5` は 4294967294 になります。引き算する値は符号付きにします。

??? failure "セーブデータに int や long を使う"
    環境によって大きさが違い、別の PC で読めなくなることがあります。

??? failure "1 << 40 のように、int の定数を 64 ビットまでずらす"
    `1` は `int` なので、32 ビット以上のシフトは未定義動作です。`std::int64_t{1} << 40` か `INT64_C(1) << 40` と書きます。

??? failure "int_fast や int_least をファイルの形式に使う"
    環境によって幅が変わります。ファイルや通信には、幅がぴったり決まった `int32_t` などを使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイル・通信・ビット操作は大きさの決まった型
    - [x] 普通の計算は int、大きさ・個数は size_t
    - [x] uint8_t は cout で文字になる

## 関連ページ

- [std::numeric_limits](limits.md)
- [cppreference: Fixed width integer types](https://en.cppreference.com/w/cpp/types/integer)
