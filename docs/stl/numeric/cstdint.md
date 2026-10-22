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

## フラグ・オプション

| マクロ | 意味 |
| --- | --- |
| `INT32_MAX`、`UINT8_MAX` など | 各型の最大値・最小値（C の書き方。C++ では [`std::numeric_limits`](limits.md) も使える） |
| `INT64_C(123)` など | その型のリテラルを作るマクロ |

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
