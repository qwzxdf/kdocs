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

`as_bytes` の、書き込み可能版です。ファイルから読み込んだバイト列をそのまま構造体の配列に流し込むときなどに使います。

!!! tip "ポイント"
    - 元の型を問わずバイト列として見られる。
    - コピーはしない（元のメモリを見る）。
    - `std::byte` は整数ではないので、計算には `std::to_integer` を使う。

!!! info "このページを読む前に"
    [`std::span`](span.md) を先に読んでください。

## 関数の詳しい説明

### std::as_writable_bytes {#as_writable_bytes}

```cpp
template <class T, std::size_t N>
std::span<byte> as_writable_bytes(std::span<T, N> s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | span | 元の span |

- 戻り値: バイト列として見た span
- 計算量: 定数

リトルエンディアンの環境での例です。バイト順は環境によって変わります。


## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <span>

int main() {
  int values[] = {1};
  auto bytes = std::as_writable_bytes(std::span(values));
  bytes[0] = std::byte{7};
  std::println("{}", values[0]);
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルに構造体の配列を書き出す | `Write(std::as_bytes(std::span(items)));` |

## よくあるミス

??? failure "バイト順を考えない"
    ファイルに書いたバイト列は、環境のバイト順（エンディアン）に依存します。別の環境で読むなら、形式を決めておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`span`](span.md) | span の本体 |
| [`as_bytes`](as_bytes.md) | もう片方 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] span をバイト列として見る
    - [x] コピーしない
    - [x] バイト順に注意

## 関連ページ

- [cpprefjp: std::as_writable_bytes](https://cpprefjp.github.io/reference/span/as_writable_bytes.html)
- [cppreference: std::as_writable_bytes](https://en.cppreference.com/w/cpp/container/span/as_writable_bytes)
