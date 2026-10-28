---
title: std::to_integer
summary: "`std::byte` を整数に変換する。"
order: 6
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::to_integer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cstddef>`
</div>

`std::byte` は算術型ではないので、`int` に直接代入できません。バイトの値を数値として使うときの変換が `std::to_integer<T>(b)` です。

!!! tip "ポイント"
    - `std::to_integer<int>(b)` は `byte` の値を整数にする
    - 変換先の型 `T` をテンプレート引数で指定する
    - `byte` が持つ値（0〜255）がそのまま入る
    - 逆の変換は `std::byte{値}`

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::to_integer {#to_integer}

<span class="ver ver-17">C++17</span>

```cpp
template <class IntegerType>
constexpr IntegerType to_integer(std::byte b) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `IntegerType` | 整数型 | 変換先の整数型（テンプレート引数） |
| `b` | `std::byte` | 変換するバイト |

`b` の値を `IntegerType` で返します。`unsigned char` の範囲（0〜255）の値が、符号を保って入ります。`int` に直した値は、負になりません。

逆向きは、`static_cast<std::byte>(value)` か `std::byte{value}` です。後者は、値が定数で 0〜255 の範囲に収まる必要があります。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>

int main() {
  const std::byte b{0x2A};
  std::println("to_integer<int>(0x2A)  = {}", std::to_integer<int>(b));
  std::println("to_integer<char>      = {}", std::to_integer<char>(b));
}
```

```text title="実行結果"
to_integer<int>(0x2A)  = 42
to_integer<char>      = *
```

## ゲームでの使いどころ

バイナリ データから、整数を取り出します。

```cpp
const int red = std::to_integer<int>(pixels[0]);
```

## よくあるミス

??? failure "`byte` を `int` に直接代入しようとする"
    `to_integer` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`byte`](byte.md) | バイトを表す型 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `to_integer<T>(b)` は `byte` を整数にする
    - [x] 変換先の型をテンプレート引数で指定
    - [x] 逆は `std::byte{値}`

## 関連ページ

- [cpprefjp: std::to_integer](https://cpprefjp.github.io/reference/utility/to_integer.html)
- [cppreference: std::to_integer](https://en.cppreference.com/w/cpp/utility/to_integer)
