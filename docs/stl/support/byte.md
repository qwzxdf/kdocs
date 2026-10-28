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

メモリの生のバイトを扱うとき、`unsigned char` や `char` は「文字」や「数値」とも読めてしまい、意図が曖昧です。`std::byte` は、<strong>バイト列としてだけ扱える型</strong>です。算術演算ができず、ビット演算だけができます。

!!! tip "ポイント"
    - `std::byte` は生のバイトを表す列挙型（`enum class byte : unsigned char`）
    - 算術演算（`+`、`-`）は使えず、ビット演算（`&`、`|`、`^`、`~`、`<<`、`>>`）が使える
    - 数値に直すには `std::to_integer<int>(b)`
    - バイナリ データやバッファの型に使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::byte {#byte}

<span class="ver ver-17">C++17</span>

```cpp
enum class byte : unsigned char {};
```

`std::byte` は、数値でも文字でもないバイトを表します。`b + 1` はコンパイルエラーになります。数値として扱いたいときは `std::to_integer<T>(b)` で明示的に変換します。

ビット演算は使えます。`b << 4` や `b | std::byte{0x30}` のように書けます。

`unsigned char` の配列の代わりに `std::byte` の配列を使うと、バイト列であることが型で伝わり、算術や文字の演算を誤って書く事故を防げます。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>

int main() {
  std::byte b{0x0F};
  std::println("b << 4         = {}", std::to_integer<int>(b << 4));
  std::println("b | 0x30       = {}", std::to_integer<int>(b | std::byte{0x30}));
  std::println("サイズ         = {}", sizeof(std::byte));
}
```

```text title="実行結果"
b << 4         = 240
b | 0x30       = 63
サイズ         = 1
```

## ゲームでの使いどころ

ファイルや通信のバッファに使います。

```cpp
std::vector<std::byte> buffer(1024);
file.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
```

## よくあるミス

??? failure "`b + 1` と書いてコンパイルエラーになる"
    `std::to_integer` で数値にしてから計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_integer`](to_integer.md) | `byte` を整数にする |
| [`as_const`](as_const.md) | `const` 参照にする |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::byte` はバイト列を表す型
    - [x] 算術は不可、ビット演算は可
    - [x] 数値には `to_integer` で変換する

## 関連ページ

- [cpprefjp: std::byte](https://cpprefjp.github.io/reference/utility/byte.html)
- [cppreference: std::byte](https://en.cppreference.com/w/cpp/utility/byte)
