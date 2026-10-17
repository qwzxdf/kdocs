---
title: <bit>（ビット操作）
tags:
  - 数値
---

# &lt;bit&gt;（ビット操作）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`<bit>` は、**整数のビットを調べたり操作したりする関数**をまとめた C++20 のヘッダです。「1 のビットが何個あるか」「2 のべき乗か」「次の 2 のべき乗はいくつか」などを、CPU の専用命令を使って速く計算します。また `std::bit_cast` を使うと、float の中身をビット列として安全に読むこともできます。

!!! tip "ポイント"
    - 1 のビットの数は `std::popcount`、2 のべき乗かは `std::has_single_bit`、次の 2 のべき乗は `std::bit_ceil`。
    - 型を「中身のビットはそのままで」別の型として読むなら `std::bit_cast`（`reinterpret_cast` は未定義動作になりやすい）。
    - 引数は**符号なし整数**（`unsigned`、`std::uint32_t` など）。int を渡すとコンパイルエラー。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::popcount`](#popcount) | <span class="rank rank-sometimes">たまに</span> | 1 のビットの数 |
| [`std::has_single_bit`](#has_single_bit) | <span class="rank rank-sometimes">たまに</span> | 2 のべき乗か |
| [`std::bit_ceil`](#bit_ceil) | <span class="rank rank-sometimes">たまに</span> | 以上で一番小さい 2 のべき乗 |
| [`std::bit_cast`](#bit_cast) | <span class="rank rank-sometimes">たまに</span> | ビットはそのままで別の型として読む |
| [`std::countr_zero`](#countr_zero) | <span class="rank rank-sometimes">たまに</span> | 下位から続く 0 の数（一番下の 1 の位置） |
| [`std::bit_floor`](#bit_floor) | <span class="rank rank-rare">知ってるだけ</span> | 以下で一番大きい 2 のべき乗 |
| [`std::bit_width`](#bit_width) | <span class="rank rank-rare">知ってるだけ</span> | 表すのに必要なビット数 |
| [`std::countl_zero`](#countl_zero) | <span class="rank rank-rare">知ってるだけ</span> | 上位から続く 0 の数 |
| [`std::countl_one`](#countl_one) | <span class="rank rank-rare">知ってるだけ</span> | 上位から続く 1 の数 |
| [`std::countr_one`](#countr_one) | <span class="rank rank-rare">知ってるだけ</span> | 下位から続く 1 の数 |
| [`std::rotl`](#rotl) | <span class="rank rank-rare">知ってるだけ</span> | 左回転（はみ出したビットが反対側から入る） |
| [`std::rotr`](#rotr) | <span class="rank rank-rare">知ってるだけ</span> | 右回転 |
| [`std::byteswap`](#byteswap) | <span class="rank rank-rare">知ってるだけ</span> | バイトの並びを逆にする <span class="ver ver-23">C++23</span> |
| [`std::endian`](#endian) | <span class="rank rank-rare">知ってるだけ</span> | 今の CPU のエンディアン |

## よくある使い方

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint32_t flags = 0b1011'0000;  // 取ったアイテムのフラグ
  std::println("取った数: {}", std::popcount(flags));

  std::uint32_t texture_size = 300;
  std::println("2 のべき乗？ {} / 切り上げ {}", std::has_single_bit(texture_size),
               std::bit_ceil(texture_size));

  float f = 1.0f;
  std::println("1.0f のビット: {:#010x}", std::bit_cast<std::uint32_t>(f));
}
```

```text title="実行結果"
取った数: 3
2 のべき乗？ false / 切り上げ 512
1.0f のビット: 0x3f800000
```

## 関数の詳しい説明

### std::popcount {#popcount}

```cpp
template <class T>
constexpr int popcount(T x) noexcept;  // T は符号なし整数
```

- 1 になっているビットの数

<div class="anim" data-label="std::popcount(0b1011u)">
1 0 1 1 # ビット列
*1 0 1 1 # 1 のビットを数える
*1 0 *1 1 # 2 つ目
*1 0 *1 *1 # 3 つ。結果は 3
</div>

### std::has_single_bit {#has_single_bit}

```cpp
template <class T>
constexpr bool has_single_bit(T x) noexcept;
```

- 1 のビットがちょうど 1 つ（= 2 のべき乗）なら `true`。0 は `false`

### std::bit_ceil {#bit_ceil}

```cpp
template <class T>
constexpr T bit_ceil(T x);
```

- `x` 以上で一番小さい 2 のべき乗。テクスチャやバッファの大きさを 2 のべき乗にそろえるのに使います

### std::bit_cast {#bit_cast}

```cpp
template <class To, class From>
constexpr To bit_cast(const From& from) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `To` | 読み替える先の型（`From` と同じ大きさで、コピーできる型） |

- メモリの中身（ビット）はそのままで、別の型として読みます。ハッシュ値の計算や、ネットワーク・ファイル用に float を整数として扱うときに使います

### std::countr_zero {#countr_zero}

```cpp
template <class T>
constexpr int countr_zero(T x) noexcept;
```

- 一番下の位から続く 0 の数 = 一番下にある 1 の位置。フラグの中から「次に立っているビット」を探すのに使えます

<div class="anim" data-label="std::countr_zero(0b1000u)">
1 0 0 0 # ビット列
1 *0 *0 *0 # 右から続く 0 を数える（3）
</div>

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint32_t pending = 0b0010'1000;  // 3 番と 5 番の処理が残っている
  while (pending != 0) {
    int index = std::countr_zero(pending);  // 一番下の 1 の位置
    std::print("{} ", index);
    pending &= pending - 1;                 // 一番下の 1 を消す
  }
  std::println("");
}
```

```text title="実行結果"
3 5 
```

### std::bit_floor {#bit_floor}

```cpp
template <class T>
constexpr T bit_floor(T x) noexcept;
```

- `x` 以下で一番大きい 2 のべき乗（0 なら 0）

### std::bit_width {#bit_width}

```cpp
template <class T>
constexpr int bit_width(T x) noexcept;
```

- `x` を表すのに必要なビット数（0 なら 0）。`bit_width(x) - 1` が「2 を底とする対数（切り捨て）」

### std::countl_zero {#countl_zero}

```cpp
template <class T>
constexpr int countl_zero(T x) noexcept;
```

- 一番上の位から続く 0 の数

### std::countl_one {#countl_one}

```cpp
template <class T>
constexpr int countl_one(T x) noexcept;
```

- 一番上の位から続く 1 の数

### std::countr_one {#countr_one}

```cpp
template <class T>
constexpr int countr_one(T x) noexcept;
```

- 一番下の位から続く 1 の数

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint8_t x = 0b0001'0111;
  std::println("floor {} / width {} / countl_zero {} / countr_one {} / countl_one {}",
               std::bit_floor(x), std::bit_width(x), std::countl_zero(x), std::countr_one(x),
               std::countl_one(static_cast<std::uint8_t>(0b1110'0000)));
}
```

```text title="実行結果"
floor 16 / width 5 / countl_zero 3 / countr_one 3 / countl_one 3
```

### std::rotl {#rotl}

```cpp
template <class T>
constexpr T rotl(T x, int s) noexcept;
```

- 左に `s` ビット回転します。はみ出したビットは右から入ります（ハッシュ関数や乱数でよく使う）

<div class="anim" data-label="std::rotl(0b1001u, 1)">
1 0 0 1 # ビット列
>0 >0 >1 >1 # 左に 1 つ回す。はみ出した 1 が右端に戻る
</div>

### std::rotr {#rotr}

```cpp
template <class T>
constexpr T rotr(T x, int s) noexcept;
```

- 右に回転します

<div class="anim" data-label="std::rotr(0b1001u, 1)">
1 0 0 1 # ビット列
>1 >1 >0 >0 # 右に 1 つ回す。はみ出した 1 が左端に戻る
</div>

### std::byteswap {#byteswap}

<span class="ver ver-23">C++23</span>

```cpp
template <class T>
constexpr T byteswap(T n) noexcept;
```

- バイトの並び順を逆にします。エンディアンの違う形式のファイル・通信を読むときに使います

<div class="anim" data-label="std::byteswap(0x12345678u)">
12 34 56 78 # 4 バイト
>78 >56 >34 >12 # バイトの並びを逆にする（エンディアン変換）
</div>

### std::endian {#endian}

```cpp
enum class endian { little, big, native };
```

- `std::endian::native == std::endian::little` で、今の CPU がリトルエンディアンか分かります（PC はほぼリトル）

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint8_t x = 0b1000'0001;
  std::println("{:08b} {:08b}", std::rotl(x, 1), std::rotr(x, 1));
  std::println("{:#x}", std::byteswap(std::uint32_t{0x11223344}));
  std::println("リトルエンディアン？ {}", std::endian::native == std::endian::little);
}
```

```text title="実行結果"
00000011 11000000
0x44332211
リトルエンディアン？ true
```

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int count = __builtin_popcount(x);  // GCC 専用
    int count2 = __popcnt(x);           // MSVC 専用
    std::uint32_t bits = *reinterpret_cast<std::uint32_t*>(&f);  // 未定義動作
    ```

=== "今の書き方（C++20）"

    ```cpp
    int count = std::popcount(x);
    auto bits = std::bit_cast<std::uint32_t>(f);
    ```

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| フラグの数を数える | `popcount` |
| テクスチャの大きさを 2 のべき乗に | `has_single_bit`、`bit_ceil` |
| ECS のコンポーネントのビットマスクを回す | `countr_zero` |
| ハッシュ関数 | `rotl`、`bit_cast` |
| ファイル形式の読み込み | `byteswap`、`endian` |

## よくあるミス

??? failure "int を渡してコンパイルエラー"
    `std::popcount(5)` はエラーです。`5u` か `std::uint32_t{5}` のように符号なしにします。

??? failure "reinterpret_cast で float を読む"
    型の違うポインタで読むのは未定義動作（strict aliasing 違反）です。`std::bit_cast` を使います。

## 理解度チェック

!!! question "Q1. `std::bit_ceil(65u)` と `std::bit_floor(65u)` は？"
    <div class="spoiler" markdown>

    **答え:** `128` と `64`。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数える popcount、2 のべき乗 has_single_bit / bit_ceil
    - [x] 型の読み替えは bit_cast
    - [x] 引数は符号なし整数

## 関連ページ

- [std::bitset](../containers/bitset.md)
- [cppreference: <bit>](https://en.cppreference.com/w/cpp/header/bit)
