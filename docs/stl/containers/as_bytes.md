---
title: std::as_bytes
summary: "span を、読み取り専用のバイト列（span<const std::byte>）として見る。"
order: 900
tags:
  - コンテナ
---

# std::as_bytes

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <span>`
</div>

配列やコンテナの中身を、バイト列として読みたい。ファイルに書き出す、ハッシュを計算する、ネットワークに送る。`std::as_bytes(span)` は、`std::span<T>` を、`std::span<const std::byte>` に変換します。コピーはなく、同じ領域を、バイトの単位で見るだけです。

!!! tip "ポイント"
    - `span<T>` を `span<const std::byte>` に変える
    - コピーしない。同じ領域の見え方を変えるだけ
    - 大きさは `sizeof(T) * 要素数` のバイト数
    - 書き込みたいなら `as_writable_bytes`

!!! info "このページを読む前に"
    [`std::span`](span.md) を先に読んでください。

## 関数の詳しい説明

### std::as_bytes {#as_bytes}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, std::size_t N>
std::span<const std::byte, /* N * sizeof(T) または dynamic_extent */>
as_bytes(std::span<T, N> s) noexcept;
```

`T` の中身が、パディングや、ポインターを含んでいても、その領域のバイトを読むだけなので、変換自体は安全です。ただし、バイト列を別の環境へ送ると、エンディアンやパディングが違って、意味が変わります。

`reinterpret_cast<const std::byte*>(data)` と、大きさの計算を、毎回書く代わりになります。大きさの計算ミス（`sizeof(T)` をかけ忘れる）が起きません。

## 実際に動かしてみる

```cpp
#include <array>
#include <cstddef>
#include <print>
#include <span>

int main() {
  std::array<int, 4> data = {1, 2, 3, 4};

  std::span<const std::byte> bytes = std::as_bytes(std::span(data));
  std::println("要素 {} 個 = {} バイト", data.size(), bytes.size());
  std::println("先頭のバイト: {}", std::to_integer<int>(bytes[0]));  // リトル エンディアンなら 1
}
```

```text title="実行結果"
要素 4 個 = 16 バイト
先頭のバイト: 1
```

## ゲームでの使いどころ

データをファイルに書き出す、ハッシュを計算する、ネットワークに送る、といった処理の入口で使います。

## よくあるミス

??? failure "他の環境にそのまま送る"
    エンディアンやパディングが違うと、意味が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`as_writable_bytes`](as_writable_bytes.md) | 書き込める版 |
| [`span`](span.md) | 元の型 |
| `std::bit_cast` | 値を別の型にコピーする |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::as_bytes](https://cpprefjp.github.io/reference/span/as_bytes.html)
- [cppreference: std::as_bytes](https://en.cppreference.com/w/cpp/container/span/as_bytes)
