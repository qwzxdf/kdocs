---
title: std::byte
summary: "バイト（8 ビット）を表す型。整数としては扱えない。"
order: 5
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::byte

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <cstddef>`
</div>

`std::byte` は、**1 バイトのデータ（ビットの並び）を表す型**です。整数や文字と違い、足し算などの算術はできず、ビット演算（`&`、`|`、`<<` など）だけができます。バイナリデータのバッファを `char` や `uint8_t` ではなく `std::byte` で持つと、「ただのバイト列」だと明確になります。

!!! tip "ポイント"
    - 算術はできない。整数にするには [`to_integer`](to_integer.md)。
    - `std::vector<std::byte>` でバイナリバッファを表す。
    - メモリの別名（エイリアス）として特別扱いされる（`char` と同様）。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::byte {#byte}

<span class="ver ver-17">C++17</span>

```cpp
enum class byte : unsigned char {};
```

- 「数値でも文字でもない、ただのバイト」を表す型。足し算などはできず、ビット演算（`&`、`|`、`<<`）だけできます。ファイルやネットワークの生データに使うと、うっかり文字や数値として扱う間違いを防げます

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>

int main() {
  std::byte b{0x0F};
  b |= std::byte{0xF0};   // ビット演算はできる（足し算などはできない）
  std::println("{}", std::to_integer<int>(b));
}
```

```text title="実行結果"
255
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルを読んだバイナリのバッファ | `std::vector<std::byte> data(file_size);` |

## よくあるミス

??? failure "byte を整数のように足す"
    コンパイルエラーです。`to_integer` で整数にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_integer`](to_integer.md) | 整数に変換 |
| `std::uint8_t` | 整数として扱える 1 バイト |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト列を表す型
    - [x] 算術はできない
    - [x] 整数にするには to_integer

## 関連ページ

- [cpprefjp: std::byte](https://cpprefjp.github.io/reference/utility/byte.html)
- [cppreference: std::byte](https://en.cppreference.com/w/cpp/utility/byte)
