---
title: std::bit_cast
summary: "値のビット列を保ったまま、別の型として読み替える。"
order: 6
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_cast

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`float` の値をビットの並びのまま `uint32_t` として見たい。高速な逆平方根、ハッシュ値の計算、`float` のビットを使った並べ替えなどで、このような変換が必要です。

`reinterpret_cast` や、ポインタ越しのキャストで書くと、規格では未定義動作（エイリアシング違反）になります。昔は `memcpy` で逃げていました。`std::bit_cast` は、<strong>ビット表現をそのまま別の型として解釈する</strong>、正しい方法です。

!!! tip "ポイント"
    - `std::bit_cast<std::uint32_t>(1.0f)` は `0x3f800000`
    - 2 つの型は、同じ大きさで、トリビアルにコピーできること
    - ポインタのキャストと違い、未定義動作にならない
    - `constexpr` でも使える

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_cast {#bit_cast}

<span class="ver ver-20">C++20</span>

```cpp
template <class To, class From>
constexpr To bit_cast(const From& from) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `From` | 型 | 変換元の型。`To` と同じ大きさで、トリビアルにコピーできること |
| `from` | `From` の値 | ビットを取り出す値 |

戻り値は、`from` のビット列を `To` 型として解釈した値です。2 つの型は、同じ `sizeof` を持ち、どちらもトリビアルにコピーできる（`memcpy` できる）型でなければなりません。条件を満たさない場合はコンパイルエラーです。

`reinterpret_cast<std::uint32_t&>(f)` のようなキャストは、別の型のオブジェクトとして触ってよい、という保証が規格にないので、最適化の過程で誤動作する危険があります。`memcpy` は安全ですが、書く量が多いです。`bit_cast` は `memcpy` と同じ意味を型の検査つきで短く書けます。

多くの場合、コンパイラは `bit_cast` を単なるレジスタの移動に最適化するので、実行時のコストはありません。

エンディアンに依存します。ビッグエンディアンの環境で作った値と、リトルエンディアンの環境の値は、同じにはなりません。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  const float f = 1.0f;
  const std::uint32_t bits = std::bit_cast<std::uint32_t>(f);
  std::println("1.0f のビット = {:#x}", bits);

  // 逆向き: ビットから float を作る
  const float pi = std::bit_cast<float>(0x40490fdbu);
  std::println("0x40490fdb は {}", pi);
}
```

```text title="実行結果"
1.0f のビット = 0x3f800000
0x40490fdb は 3.1415927
```

## ゲームでの使いどころ

`float` を整数として並べ替える、浮動小数点数のビットを調べる、といった場面で使います。

```cpp
// float のビット列を使った高速な処理（例: 符号ビットの取り出し）
const std::uint32_t bits = std::bit_cast<std::uint32_t>(value);
const bool negative = (bits >> 31) != 0;   // 符号ビット
```

## よくあるミス

??? failure "サイズの違う型を指定して、コンパイルエラーになる"
    `sizeof(To) == sizeof(From)` の型にします。

??? failure "`reinterpret_cast` で書いて、最適化で壊れる"
    `bit_cast` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reinterpret_cast`](../../../basics/index.md) | 未定義動作の危険がある変換 |
| [`byteswap`](byteswap.md) | バイト順を入れ替える |
| [`endian`](endian.md) | 環境のバイト順 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bit_cast<To>(from)` はビット表現をそのまま別の型として見る
    - [x] 同じ大きさのトリビアルにコピーできる型だけ
    - [x] `reinterpret_cast` より安全。コストはほぼゼロ

## 関連ページ

- [cpprefjp: std::bit_cast](https://cpprefjp.github.io/reference/bit/bit_cast.html)
- [cppreference: std::bit_cast](https://en.cppreference.com/w/cpp/numeric/bit_cast)
