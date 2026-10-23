---
title: std::endian
summary: "環境のバイト順序（エンディアン）を調べる。"
order: 14
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::endian

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

数値をメモリにどの順で並べるか。0x12345678 を、下位のバイトから 78 56 34 12 と並べる環境（リトルエンディアン）と、上位から 12 34 56 78 と並べる環境（ビッグエンディアン）があります。自作のファイル形式や通信を作るとき、環境のバイト順を知る必要があります。

`std::endian` は、<strong>環境のバイト順を、コンパイル時に調べる</strong>ための列挙型です。

!!! tip "ポイント"
    - `std::endian::native` が、環境のバイト順
    - `std::endian::little` と `std::endian::big` と比べて判定する
    - コンパイル時の定数なので、`if constexpr` で使える
    - PC・コンソール・スマホは、ほぼすべてリトルエンディアン

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::endian {#endian}

<span class="ver ver-20">C++20</span>

```cpp
enum class endian {
  little = /* ... */,
  big    = /* ... */,
  native = /* little か big */
};
```

`std::endian::native` は、`little` か `big` のどちらかと等しくなります。環境が混在エンディアン（まれ）の場合は、どちらとも等しくありません。

以前は、`int` を `char` の配列として見て、最初のバイトを調べる実行時のコードで確かめていました。`std::endian` は、コンパイル時に決まるので、`if constexpr` で分岐を消せます。

ゲームの環境では、Windows、PlayStation、Xbox、Switch、スマホのほぼすべてがリトルエンディアンです。それでも明示するのは、ファイル形式がビッグエンディアンと決まっている相手（ネットワークのパケット、PNG などの形式）と、意識的にやり取りするためです。

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("リトルエンディアン: {}", std::endian::native == std::endian::little);
  std::println("ビッグエンディアン: {}", std::endian::native == std::endian::big);
}
```

```text title="実行結果"
リトルエンディアン: true
ビッグエンディアン: false
```

## ゲームでの使いどころ

ビッグエンディアンの外部データを読むとき、環境に応じて入れ替えます。

```cpp
if constexpr (std::endian::native == std::endian::little) {
  value = std::byteswap(value);   // ビッグエンディアンのデータをリトルの環境で読む
}
```

## よくあるミス

??? failure "実行時に調べようとして、冗長なコードを書く"
    `std::endian::native` でコンパイル時に判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`byteswap`](byteswap.md) | バイト順を入れ替える |
| [`bit_cast`](bit_cast.md) | ビット表現をそのまま別の型として見る |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::endian::native` が環境のバイト順
    - [x] `little` / `big` と比べて判定する
    - [x] ほぼすべてのゲーム環境はリトルエンディアン

## 関連ページ

- [cpprefjp: std::endian](https://cpprefjp.github.io/reference/bit/endian.html)
- [cppreference: std::endian](https://en.cppreference.com/w/cpp/numeric/endian)
