---
title: std::size_t
summary: "大きさや個数を表す、符号なしの整数型。"
order: 21
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::size_t

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

型の大きさや、ポインターの扱いは環境で違います。`std::size_t` は、<strong>メモリ上のサイズや添字を表す符号なし整数型</strong>です。環境に合わせた正しい幅になるので、`int` で代用するより安全です。

!!! tip "ポイント"
    - `std::size_t` はメモリ上のサイズや添字を表す符号なし整数型
    - `<cstddef>` で宣言される
    - 環境（32 ビット / 64 ビット）に応じて幅が変わる
    - `int` で代用しないのが安全

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::size_t {#size_t}

<span class="ver ver-98">C++98</span>

```cpp
using size_t = /* 実装定義 */;
```

`sizeof` の結果の型で、配列の添字や、コンテナの要素数に使われます。ポインターと同じ幅（64 ビット環境では 64 ビット）になるのが一般的です。符号なしなので、`0 - 1` が巨大な値に折り返す点に注意します。

ファイルやネットワークのデータ形式には、幅が環境で変わるこの型を使わず、`std::uint32_t` などの固定幅の型を使います。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("sizeof(size_t) == sizeof(void*) : {}", sizeof(std::size_t) == sizeof(void*));
}
```

```text title="実行結果"
sizeof(size_t) == sizeof(void*) : true
```

## ゲームでの使いどころ

配列やコンテナの添字、バイト数の計算に使います。

```cpp
for (std::size_t i = 0; i < items.size(); ++i) { /* … */ }
```

## よくあるミス

??? failure "`int` で代用して、大きなデータで桁あふれする"
    環境に合った型を使います。

??? failure "データ形式に使って、環境で互換性が崩れる"
    固定幅の型を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::int32_t`](../numeric/cstdint/int32_t.md) | 固定幅の整数 |
| [`intptr_t`](../numeric/cstdint/intptr_t.md) | ポインターを保持できる整数 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::size_t` はメモリ上のサイズや添字を表す符号なし整数型
    - [x] 環境で幅が変わる
    - [x] データ形式には固定幅の型を使う

## 関連ページ

- [cpprefjp: std::size_t](https://cpprefjp.github.io/reference/cstddef/size_t.html)
- [cppreference: std::size_t](https://en.cppreference.com/w/cpp/types/size_t)
