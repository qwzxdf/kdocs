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

`std::byteswap` は、**整数のバイトの並びを反対にする**関数です。リトルエンディアンの PC で、ビッグエンディアン（ネットワークバイトオーダー）のデータを読むときなどに使います。`0x12345678` が `0x78563412` になります。

!!! tip "ポイント"
    - ネットワークやファイルフォーマットが、PC と逆の順序のとき。
    - `std::endian` で、自分の環境の順序を調べられる。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

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

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{:#x}", std::byteswap(0x12345678u));
}
```

```text title="実行結果"
0x78563412
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ビッグエンディアンのファイル形式を読む | `std::byteswap(value)` |

## よくあるミス

??? failure "1 バイトの型に使う"
    何も起きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`endian`](endian.md) | 自分の環境の順序 |
| [`bit_cast`](bit_cast.md) | 型の読み替え |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイトの並びを反転
    - [x] 環境と逆のデータ形式に
    - [x] C++23

## 関連ページ

- [cpprefjp: std::byteswap](https://cpprefjp.github.io/reference/bit/byteswap.html)
- [cppreference: std::byteswap](https://en.cppreference.com/w/cpp/numeric/byteswap)
