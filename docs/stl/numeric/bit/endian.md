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

`std::endian` は、**この環境のバイト順序（リトルエンディアンかビッグエンディアンか）**を表す列挙型です。`std::endian::native` と `std::endian::little` を比べると、環境の順序が分かります。通常の PC / コンソールはリトルエンディアンです。

!!! tip "ポイント"
    - `if constexpr (std::endian::native == std::endian::little)` で分岐する。
    - ファイル形式の順序と環境が違うときに `byteswap`。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル形式が環境と同じ順序か判定する | `std::endian::native == std::endian::big` |

## よくあるミス

??? failure "マクロで判定する"
    `std::endian` なら、型安全に、コンパイル時に判定できます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`byteswap`](byteswap.md) | 順序を反転する |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 環境のバイト順序
    - [x] `native` と `little` を比べる
    - [x] 普通の PC はリトルエンディアン

## 関連ページ

- [cpprefjp: std::endian](https://cpprefjp.github.io/reference/bit/endian.html)
- [cppreference: std::endian](https://en.cppreference.com/w/cpp/numeric/endian)
