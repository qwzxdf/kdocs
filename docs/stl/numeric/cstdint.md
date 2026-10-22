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

`int` や `long` は、**環境によって大きさ（ビット数）が違う**ことがあります（たとえば `long` は Windows では 32 ビット、Linux では 64 ビット）。`<cstdint>` は、**ビット数がはっきり決まった整数型**（`std::int32_t`、`std::uint8_t` など）を用意してくれるヘッダです。セーブデータ、ネットワーク、ファイル形式、ビットフラグのように、大きさが変わると困る場面で使います。

!!! tip "ポイント"
    - **ファイル・通信・ビット操作では大きさの決まった型**（`std::int32_t`、`std::uint64_t` など）を使う。
    - 普通の計算（ループのカウンタ、HP）は `int` で十分。
    - 0〜255 の小さな値（色など）は `std::uint8_t`。ただし `std::cout` で出すと文字として表示されるので注意。
    - 大きさ・個数は `std::size_t`（`<cstddef>`）。

## 主な型

よく使う順です。

| 型 | 重要度 | ビット数 | 範囲 | 使う場面 |
| --- | --- | --- | --- | --- |
| [`std::int32_t`](#int32_t) | <span class="rank rank-often">よく使う</span> | 32 | 約 -21 億〜21 億 | セーブデータの数値 |
| [`std::uint32_t`](#uint32_t) | <span class="rank rank-often">よく使う</span> | 32 | 0〜約 43 億 | ID、フラグ、色（RGBA） |
| [`std::uint8_t`](#uint8_t) | <span class="rank rank-often">よく使う</span> | 8 | 0〜255 | 色の各成分、バイト列 |
| [`std::int64_t`](#int64_t) | <span class="rank rank-often">よく使う</span> | 64 | 約 ±922 京 | 所持金、タイムスタンプ |
| [`std::uint64_t`](#uint64_t) | <span class="rank rank-sometimes">たまに</span> | 64 | 0〜約 1845 京 | ハッシュ値、ハンドル |
| [`std::int16_t`](#int16_t) | <span class="rank rank-sometimes">たまに</span> | 16 | -32768〜32767 | 音声データ（16bit PCM） |
| [`std::uint16_t`](#uint16_t) | <span class="rank rank-sometimes">たまに</span> | 16 | 0〜65535 | 小さなファイル形式、タイルの番号 |
| [`std::int8_t`](#int8_t) | <span class="rank rank-rare">知ってるだけ</span> | 8 | -128〜127 | |
| [`std::size_t`](#size_t) | <span class="rank rank-must">必須</span> | 環境による（64bit なら 64） | 0〜 | 大きさ・個数・添字（`<cstddef>`） |
| [`std::ptrdiff_t`](#ptrdiff_t) | <span class="rank rank-sometimes">たまに</span> | 環境による | 符号付き | ポインタ・イテレータの差 |
| [`std::intptr_t`](#intptr_t) | <span class="rank rank-rare">知ってるだけ</span> | ポインタと同じ | 符号付き | ポインタを整数として扱う |
| [`std::uintptr_t`](#uintptr_t) | <span class="rank rank-rare">知ってるだけ</span> | ポインタと同じ | 符号なし | ポインタを整数として扱う |
| [`std::int_fast32_t`](#int_fast32_t) | <span class="rank rank-rare">知ってるだけ</span> | 32 以上で一番速い | | |
| [`std::int_least32_t`](#int_least32_t) | <span class="rank rank-rare">知ってるだけ</span> | 32 以上で一番小さい | | |

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

### std::int32_t {#int32_t}

- ちょうど 32 ビットの符号付き整数。ファイルに書くとき、`int` の代わりに使うと環境が変わっても読めます

### std::uint32_t {#uint32_t}

- ちょうど 32 ビットの符号なし整数。ビットフラグや ID、RGBA の色に使います

### std::uint8_t {#uint8_t}

- ちょうど 8 ビットの符号なし整数（0〜255）。中身は `unsigned char` なので、`std::cout << x` では**文字**として出ます（`std::println` なら数値）

```cpp
#include <cstdint>
#include <iostream>
#include <print>

int main() {
  std::uint8_t level = 65;
  std::cout << level << ' ' << static_cast<int>(level) << '\n';  // 1 つ目は 'A'
  std::println("{}", level);  // println は数値で出す
}
```

```text title="実行結果"
A 65
65
```

### std::int64_t {#int64_t}

- ちょうど 64 ビットの符号付き整数。21 億を超える数（所持金、ミリ秒のタイムスタンプ）に使います

### std::uint64_t {#uint64_t}

- 64 ビットの符号なし整数。ハッシュ値や、世代付きの[ハンドル](../../engine/handle.md)を 1 つの数に詰めるのに使います

### std::int16_t {#int16_t}

- ちょうど 16 ビットの符号付き整数。音声のサンプル（16bit PCM）に使います

### std::uint16_t {#uint16_t}

- ちょうど 16 ビットの符号なし整数。タイルの番号など、65535 までで足りてメモリを節約したいデータに使います

### std::int8_t {#int8_t}

- 8 ビットの符号付き整数（-128〜127）。uint8_t と同じく、cout では文字として出ます

### std::size_t {#size_t}

```cpp
#include <cstddef>
```

- `sizeof` の結果や、コンテナの `size()` の型。64 ビット環境では 64 ビットの符号なし整数です。**マイナスにならない**ので、`size() - 1` に注意（[vector のよくあるミス](../containers/vector.md#よくあるミス)）

### std::ptrdiff_t {#ptrdiff_t}

- ポインタやイテレータの差の型（符号付き）。`std::ssize(v)` もこの型を返します

### std::intptr_t {#intptr_t}

- ポインタをそのまま入れられる大きさの符号付き整数

### std::uintptr_t {#uintptr_t}

- ポインタをそのまま入れられる大きさの符号なし整数。ポインタのアドレスをハッシュにしたり、アライメント（4 の倍数か）を調べたりするときに使います

### std::int_fast32_t {#int_fast32_t}

- 少なくとも 32 ビットあり、その環境で一番速い整数型。`int_fast8_t`、`int_fast16_t`、`int_fast64_t`（と符号なし版）もあります。ゲームではほとんど使いません

### std::int_least32_t {#int_least32_t}

- 少なくとも 32 ビットあり、一番小さい整数型。`int_least8_t` などもあります。ほとんど使いません

```cpp
#include <cstddef>
#include <cstdint>
#include <print>

int main() {
  std::println("{} {} {} {}", sizeof(std::int16_t), sizeof(std::int64_t), sizeof(std::size_t),
               sizeof(std::uintptr_t) == sizeof(void*));
}
```

```text title="実行結果（64 ビット環境）"
2 8 8 true
```

## フラグ・オプション

| マクロ | 意味 |
| --- | --- |
| `INT32_MAX`、`UINT8_MAX` など | 各型の最大値・最小値（C の書き方。C++ では [`std::numeric_limits`](limits.md) も使える） |
| `INT64_C(123)` など | その型のリテラルを作るマクロ |

### std::int_fast8_t {#int_fast8_t}

```cpp
using int_fast8_t = /* int など */;
```

- 戻り値: 8 ビット以上で、最も速く扱える符号つき整数型の別名
- 計算量: コンパイル時

8 ビット以上で、最も速く扱える符号つき整数型です。速さを優先する計算に使います。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::int_fast8_t) >= 1);
}
```

```text title="実行結果"
true
```

### std::int_least8_t {#int_least8_t}

```cpp
using int_least8_t = /* signed char など */;
```

- 戻り値: 8 ビット以上で、最も小さい符号つき整数型の別名
- 計算量: コンパイル時

8 ビット以上で、最も小さい符号つき整数型です。メモリの大きさを優先するときに使います。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::int_least8_t) >= 1);
}
```

```text title="実行結果"
true
```

### std::intmax_t {#intmax_t}

```cpp
using intmax_t = /* long long など */;
```

- 戻り値: 最も大きい符号つき整数型の別名
- 計算量: コンパイル時

最も大きい符号つき整数型です。ビット幅を気にせず、最大の範囲を確保したいときに使います。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::intmax_t) >= 1);
}
```

```text title="実行結果"
true
```

### std::uintmax_t {#uintmax_t}

```cpp
using uintmax_t = /* unsigned long long など */;
```

- 戻り値: 最も大きい符号なし整数型の別名
- 計算量: コンパイル時

最も大きい符号なし整数型です。ビット幅を気にせず、最大の範囲を確保したいときに使います。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::uintmax_t) >= 1);
}
```

```text title="実行結果"
true
```

### SIZE_MAX {#SIZE_MAX}

```cpp
#define SIZE_MAX /* size_t の最大値 */
```

- 戻り値: `size_t` の最大値（定数）
- 計算量: コンパイル時

`size_t` で表せる最大値のマクロです。「見つからない」を表す値（`std::string::npos` など）として使われます。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", SIZE_MAX == static_cast<std::size_t>(-1));
}
```

```text title="実行結果"
true
```

### INT32_MAX {#INT32_MAX}

```cpp
#define INT32_MAX 2147483647
```

- 戻り値: 固定幅の整数型の最大値（定数）
- 計算量: コンパイル時

幅が決まった整数型の最大値です（2147483647）。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", INT32_MAX);
}
```

```text title="実行結果"
2147483647
```

### INT64_MAX {#INT64_MAX}

```cpp
#define INT64_MAX 9223372036854775807
```

- 戻り値: 固定幅の整数型の最大値（定数）
- 計算量: コンパイル時

幅が決まった整数型の最大値です（9223372036854775807）。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", INT64_MAX);
}
```

```text title="実行結果"
9223372036854775807
```

### UINT32_MAX {#UINT32_MAX}

```cpp
#define UINT32_MAX 4294967295
```

- 戻り値: 固定幅の整数型の最大値（定数）
- 計算量: コンパイル時

幅が決まった整数型の最大値です（4294967295）。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", UINT32_MAX);
}
```

```text title="実行結果"
4294967295
```

### UINT64_MAX {#UINT64_MAX}

```cpp
#define UINT64_MAX 18446744073709551615
```

- 戻り値: 固定幅の整数型の最大値（定数）
- 計算量: コンパイル時

幅が決まった整数型の最大値です（18446744073709551615）。

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", UINT64_MAX);
}
```

```text title="実行結果"
18446744073709551615
```

## ゲームでの使いどころ

| 場面 | 型 |
| --- | --- |
| セーブデータ・ファイル形式 | `std::int32_t`、`std::uint32_t` など全部大きさ決め打ち |
| 色 | `std::uint8_t` × 4、または `std::uint32_t` |
| ID・ハンドル | `std::uint32_t`、`std::uint64_t` |
| 所持金・スコア（大きくなる） | `std::int64_t` |
| ループ・HP など普通の計算 | `int` |

## よくあるミス

??? failure "uint8_t を cout で出して文字化け"
    `std::cout << static_cast<int>(x)` にするか、`std::println` を使います。

??? failure "符号なし整数でマイナスの計算"
    `std::uint32_t a = 3; a - 5` は 4294967294 になります。引き算する値は符号付きにします。

??? failure "セーブデータに int や long を使う"
    環境によって大きさが違い、別の PC で読めなくなることがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイル・通信・ビット操作は大きさの決まった型
    - [x] 普通の計算は int、大きさ・個数は size_t
    - [x] uint8_t は cout で文字になる

## 関連ページ

- [std::numeric_limits](limits.md)
- [cppreference: Fixed width integer types](https://en.cppreference.com/w/cpp/types/integer)
