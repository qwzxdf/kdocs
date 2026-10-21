---
title: std::underlying_type
summary: "列挙型が内部で使っている整数型を調べる。"
order: 15
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::underlying_type

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::underlying_type_t<E>` は、**列挙型 E が内部で使っている整数型**を返します。`enum class Color : uint8_t` なら `uint8_t` です。`std::to_underlying` の戻り値の型です。

!!! tip "ポイント"
    - 列挙型にだけ使える。
    - `enum class E : uint8_t` と書くと、型が明示される。
    - 値の取り出しは [`std::to_underlying`](../to_underlying.md)。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::underlying_type_t {#underlying_type}

```cpp
template <class E>
using underlying_type_t = /* enum E の中身の整数型 */;
```

- enum class を整数に変換するときの型。C++23 なら [`std::to_underlying`](../to_underlying.md#to_underlying) が簡単です

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <type_traits>

enum class Color : std::uint8_t { kRed, kBlue };

int main() {
  std::println("{} {}", std::is_same_v<std::underlying_type_t<Color>, std::uint8_t>, sizeof(Color));
}
```

```text title="実行結果"
true 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| enum のビットフラグを、元の整数型で扱う | `std::underlying_type_t<Flags>` |

## よくあるミス

??? failure "列挙型でない型に使う"
    コンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::to_underlying`](../to_underlying.md) | 値を取り出す |
| [`is_enum`](is_enum.md) | 列挙型か |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 列挙型の元の整数型
    - [x] 列挙型だけ
    - [x] to_underlying の戻り値型

## 関連ページ

- [cpprefjp: std::underlying_type](https://cpprefjp.github.io/reference/type_traits/underlying_type.html)
- [cppreference: std::underlying_type](https://en.cppreference.com/w/cpp/types/underlying_type)
