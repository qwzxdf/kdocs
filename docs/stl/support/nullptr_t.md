---
title: std::nullptr_t
summary: "`nullptr` の型。"
order: 20
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::nullptr_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstddef>`
</div>

型の大きさや、ポインターの扱いは環境で違います。`std::nullptr_t` は、<strong>`nullptr` の型</strong>です。環境に合わせた正しい幅になるので、`int` で代用するより安全です。

!!! tip "ポイント"
    - `std::nullptr_t` は`nullptr` の型
    - `<cstddef>` で宣言される
    - 環境（32 ビット / 64 ビット）に応じて幅が変わる
    - `int` で代用しないのが安全

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nullptr_t {#nullptr_t}

<span class="ver ver-11">C++11</span>

```cpp
using nullptr_t = /* 実装定義 */;
```

`nullptr` リテラルの型です。どのポインター型にも暗黙に変換できます。オーバーロードで `nullptr` を受け取る関数を書くときに使います。

ファイルやネットワークのデータ形式には、幅が環境で変わるこの型を使わず、`std::uint32_t` などの固定幅の型を使います。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("is_same_v<decltype(nullptr), nullptr_t> : {}", std::is_same_v<decltype(nullptr), std::nullptr_t>);
}
```

```text title="実行結果"
is_same_v<decltype(nullptr), nullptr_t> : true
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

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::nullptr_t` は`nullptr` の型
    - [x] 環境で幅が変わる
    - [x] データ形式には固定幅の型を使う

## 関連ページ

- [cpprefjp: std::nullptr_t](https://cpprefjp.github.io/reference/cstddef/nullptr_t.html)
- [cppreference: std::nullptr_t](https://en.cppreference.com/w/cpp/types/nullptr_t)
