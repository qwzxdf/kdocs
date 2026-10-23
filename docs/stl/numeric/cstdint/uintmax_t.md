---
title: std::uintmax_t
summary: "その環境で最も大きい符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uintmax_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

ハッシュ値や、あらゆる符号なし整数を受け取りたい関数の共通の入れ物として、その環境で最大の符号なし整数型が必要になることがあります。

`std::uintmax_t` は、<strong>その環境で最大の幅を持つ符号なし整数型</strong>です。

!!! tip "ポイント"
    - 最大の符号なし整数型。少なくとも 64 ビット
    - `std::intmax_t` は符号つき版
    - `std::filesystem::file_size` の戻り値など、サイズを表す型の一部で使われる
    - 普通のゲームでは `std::uint64_t` で足りる

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uintmax_t {#uintmax_t}

<span class="ver ver-11">C++11</span>

```cpp
using uintmax_t = /* 最大幅の符号なし整数型 */;
```

`std::uintmax_t` は、環境にある符号なし整数型の中で最大のものの別名です。ほとんどの環境で 64 ビット（`unsigned long long`）です。

標準ライブラリでは、ファイルのサイズを返す `std::filesystem::file_size` の戻り値型が `std::uintmax_t` です。ファイルの大きさを 4GB 以上にも対応できる幅にするためです。

将来、環境の最大幅が増えると大きさが変わるので、ファイルや通信の形式には、固定幅の `std::uint64_t` を使います。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("少なくとも 64 ビット: {}", sizeof(std::uintmax_t) * 8 >= 64);
}
```

```text title="実行結果"
少なくとも 64 ビット: true
```

## ゲームでの使いどころ

ファイルのサイズを受け取るときに、型名として目にします。

```cpp
#include <filesystem>

std::uintmax_t size = std::filesystem::file_size("save.dat");   // バイト数
```

ゲームのコードでは、そのまま受け取って `std::uint64_t` に代入すれば足ります。

## よくあるミス

??? failure "ファイルの形式に使い、環境で大きさが変わる"
    `std::uint64_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`intmax_t`](intmax_t.md) | 符号つき版 |
| [`std::uint64_t`](uint64_t.md) | ちょうど 64 ビット |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大幅の符号なし整数型。少なくとも 64 ビット
    - [x] `file_size` の戻り値型として登場する
    - [x] データ形式には使わない

## 関連ページ

- [cpprefjp: std::uintmax_t](https://cpprefjp.github.io/reference/cstdint/uintmax_t.html)
- [cppreference: std::uintmax_t](https://en.cppreference.com/w/cpp/types/integer)
