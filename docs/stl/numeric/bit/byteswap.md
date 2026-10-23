---
title: std::byteswap
summary: "バイトの並び順を反転する（リトルエンディアン ⇄ ビッグエンディアン）。"
order: 13
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::byteswap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <bit>`
</div>

ファイルや通信のデータには、数値を上位バイトから並べるもの（ビッグエンディアン）と、下位バイトから並べるもの（リトルエンディアン）があります。PC の CPU はリトルエンディアンですが、ネットワークの標準はビッグエンディアンです。形式が違う相手とやり取りするとき、バイトの並びを入れ替える必要があります。

`std::byteswap` は、<strong>整数のバイトの並びを逆順に入れ替え</strong>ます。

!!! tip "ポイント"
    - `std::byteswap(0x12345678u)` は `0x78563412`
    - 整数型（符号つきも可）が対象
    - 2 回呼ぶと元に戻る
    - C++23 で追加

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::byteswap {#byteswap}

<span class="ver ver-23">C++23</span>

```cpp
template <class T>
constexpr T byteswap(T n) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数型 | バイト順を入れ替える値 |

戻り値は、`n` のバイトの順序を逆にした値です。1 バイトの型（`uint8_t`）では何も変わりません。`uint16_t` なら上位バイトと下位バイトが入れ替わり、`uint32_t` なら 4 バイトが逆順になります。

ほかのビット操作関数（`popcount` など）と違って、符号つきの整数型も受け取れます。ビットの並びではなく、バイトの並びを入れ替えるだけだからです。

用途は、エンディアンの変換です。自分の環境が `std::endian::little` で、データがビッグエンディアンなら、`byteswap` で変換します。環境のバイト順は `std::endian::native` で調べられます。

CPU の `bswap` 命令に直接対応するので速いです。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  const std::uint32_t x = 0x12345678u;
  std::println("byteswap(x)    = {:#x}", std::byteswap(x));
  std::println("2 回で元に戻る = {:#x}", std::byteswap(std::byteswap(x)));
}
```

```text title="実行結果"
byteswap(x)    = 0x78563412
2 回で元に戻る = 0x12345678
```

## ゲームでの使いどころ

ビッグエンディアンのファイルやネットワークのデータを読むときに使います。

```cpp
// リトルエンディアンの PC で、ビッグエンディアンの 32 ビット値を読む
std::uint32_t value = ReadRawU32(file);
if constexpr (std::endian::native == std::endian::little) {
  value = std::byteswap(value);
}
```

## よくあるミス

??? failure "エンディアンを確かめず、常に入れ替える"
    `std::endian::native` で環境を調べて、必要なときだけ入れ替えます。

??? failure "C++20 のコンパイラで使えない"
    `byteswap` は C++23 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`endian`](endian.md) | 環境のバイト順を調べる |
| [`rotl`](rotl.md) | ビットの回転 |

## コンパイラ対応

C++23 から使えます。GCC 12 以降、Clang 14 以降、Visual Studio 2022 17.1 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `byteswap(n)` はバイトの並びを逆にする
    - [x] 2 回呼ぶと元に戻る。符号つきの整数も扱える
    - [x] エンディアン変換に使う（C++23）

## 関連ページ

- [cpprefjp: std::byteswap](https://cpprefjp.github.io/reference/bit/byteswap.html)
- [cppreference: std::byteswap](https://en.cppreference.com/w/cpp/numeric/byteswap)
