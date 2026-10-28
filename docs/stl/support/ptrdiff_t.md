---
title: std::ptrdiff_t
summary: "2 つのポインターの差を表す、符号つきの整数型。"
order: 22
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::ptrdiff_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

型の大きさや、ポインターの扱いは環境で違います。`std::ptrdiff_t` は、<strong>ポインターどうしの差を表す符号つき整数型</strong>です。環境に合わせた正しい幅になるので、`int` で代用するより安全です。

!!! tip "ポイント"
    - `std::ptrdiff_t` はポインターどうしの差を表す符号つき整数型
    - `<cstddef>` で宣言される
    - 環境（32 ビット / 64 ビット）に応じて幅が変わる
    - `int` で代用しないのが安全

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ptrdiff_t {#ptrdiff_t}

<span class="ver ver-98">C++98</span>

```cpp
using ptrdiff_t = /* 実装定義 */;
```

ポインターの引き算の結果の型です。符号つきなので、負の差も表せます。コンテナの要素数を符号つきで扱いたいときの型にも使われます（`std::ssize` の戻り値など）。

ファイルやネットワークのデータ形式には、幅が環境で変わるこの型を使わず、`std::uint32_t` などの固定幅の型を使います。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("sizeof(ptrdiff_t) == sizeof(void*) : {}", sizeof(std::ptrdiff_t) == sizeof(void*));
}
```

```text title="実行結果"
sizeof(ptrdiff_t) == sizeof(void*) : true
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
    - [x] `std::ptrdiff_t` はポインターどうしの差を表す符号つき整数型
    - [x] 環境で幅が変わる
    - [x] データ形式には固定幅の型を使う

## 関連ページ

- [cpprefjp: std::ptrdiff_t](https://cpprefjp.github.io/reference/cstddef/ptrdiff_t.html)
- [cppreference: std::ptrdiff_t](https://en.cppreference.com/w/cpp/types/ptrdiff_t)
