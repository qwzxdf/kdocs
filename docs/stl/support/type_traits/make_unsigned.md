---
title: std::make_unsigned
summary: "符号つき整数の型を、符号なしの同じ大きさの型にする。"
order: 19
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::make_unsigned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::make_unsigned_t<T>` は、**符号つき整数型 T を、同じ大きさの符号なし整数型にする**型です。`int` なら `unsigned int`、`int64_t` なら `uint64_t` です。符号つきの値を、ビットのまま符号なしで扱いたいときに使います。

!!! tip "ポイント"
    - `make_signed_t` は逆。
    - `bool` と浮動小数点には使えない。
    - ビット演算の前に使うと安全。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::make_unsigned_t {#make_unsigned}

- `int` → `unsigned int` のように符号なし版にします

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::make_unsigned_t<int>, unsigned int>, std::is_same_v<std::make_unsigned_t<long>, unsigned long>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ハッシュ計算で、符号つきの値を符号なしにして扱う | `static_cast<std::make_unsigned_t<T>>(value)` |

## よくあるミス

??? failure "負の値のキャストの結果"
    元のビット列がそのまま大きな値として見えます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::make_signed` | 逆 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号つき → 符号なし（同じ大きさ）
    - [x] `make_signed` は逆
    - [x] ビット演算の前に使う

## 関連ページ

- [cpprefjp: std::make_unsigned](https://cpprefjp.github.io/reference/type_traits/make_unsigned.html)
- [cppreference: std::make_unsigned](https://en.cppreference.com/w/cpp/types/make_unsigned)
