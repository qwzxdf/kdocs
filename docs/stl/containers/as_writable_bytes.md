---
title: std::as_writable_bytes
summary: "span を、書き込み可能のバイト列（span<std::byte>）として見る。"
order: 900
tags:
  - コンテナ
---

# std::as_writable_bytes

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <span>`
</div>

`std::as_bytes` が読み取り専用なのに対し、`std::as_writable_bytes(span)` は、書き込める `std::span<std::byte>` に変換します。ファイルから読んだバイト列を、そのまま配列に流し込む、といった用途に使います。

!!! tip "ポイント"
    - `span<T>` を `span<std::byte>` に変える（`T` が非 const のとき）
    - コピーしない
    - `T` が const だとコンパイル エラー
    - バイトを書き込んでも安全な型（トリビアルにコピー可能）にだけ使う

!!! info "このページを読む前に"
    [`std::as_bytes`](as_bytes.md) を先に読んでください。

## 関数の詳しい説明

### std::as_writable_bytes {#as_writable_bytes}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, std::size_t N>
std::span<std::byte, /* N * sizeof(T) または dynamic_extent */>
as_writable_bytes(std::span<T, N> s) noexcept;
```

`T` が `const` だと、書き込めないので、コンパイルできません。

バイトを直接書き込むと、`T` の値の規則（不変条件）を壊すことがあります。`std::string` や `std::vector` のように、内部にポインターを持つ型のバイトを書き換えると、動作が壊れます。`int` や `float`、トリビアルな構造体など、どんなビット列でも有効な値になる型に使います。

## 実際に動かしてみる

```cpp
#include <array>
#include <cstddef>
#include <cstring>
#include <print>
#include <span>

int main() {
  std::array<int, 2> data = {0, 0};

  // バイト列として書き込む
  const int src[2] = {7, 9};
  std::span<std::byte> bytes = std::as_writable_bytes(std::span(data));
  std::memcpy(bytes.data(), src, bytes.size());

  std::println("{} {}", data[0], data[1]);
}
```

```text title="実行結果"
7 9
```

## ゲームでの使いどころ

ファイルやネットワークから読んだバイト列を、そのまま配列に流し込むときに使います。

## よくあるミス

??? failure "std::string のような型に使う"
    内部のポインターを壊します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`as_bytes`](as_bytes.md) | 読み取り専用 |
| [`span`](span.md) | 元の型 |
| `std::memcpy` | バイト単位のコピー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::as_writable_bytes](https://cpprefjp.github.io/reference/span/as_writable_bytes.html)
- [cppreference: std::as_writable_bytes](https://en.cppreference.com/w/cpp/container/span/as_writable_bytes)
