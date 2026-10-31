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

`enum class` は、内部で整数として保存されます。その整数の型を知りたいことがあります。たとえば、`enum class` の値をファイルに書くときです。`std::underlying_type` は、<strong>列挙型の基底の整数型</strong>を返します。

!!! tip "ポイント"
    - `std::underlying_type_t<Color>` は列挙型の基底の整数型
    - `enum class` の既定は `int`
    - 列挙型以外には使えない
    - 値の変換は C++23 の `to_underlying` が簡単

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::underlying_type_t {#underlying_type}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using underlying_type_t = typename underlying_type<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が列挙型のとき、その基底型（`enum class Color : std::uint8_t` なら `std::uint8_t`）を返します。基底型を指定しなかった `enum class` では `int` です。列挙型でない型を渡すと、C++20 より前は未定義、C++20 以降は不適格です。

C++23 の `std::to_underlying(value)` を使えば、値を基底型に変換する処理も簡単に書けます。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::underlying_type<T>::type` と書いても同じ型ですが、C++14 以降の `std::underlying_type_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <type_traits>

enum class Color : std::uint8_t { kRed, kBlue };
enum class Shape { kCircle, kSquare };

int main() {
  std::println("std::underlying_type_t<Color> は std::uint8_t : {}", std::is_same_v<std::underlying_type_t<Color>, std::uint8_t>);
  std::println("std::underlying_type_t<Shape> は int : {}", std::is_same_v<std::underlying_type_t<Shape>, int>);
}
```

```text title="実行結果"
std::underlying_type_t<Color> は std::uint8_t : true
std::underlying_type_t<Shape> は int : true
```

## ゲームでの使いどころ

列挙型の基になっている整数型を取り出します。列挙型を、環境に依存しない大きさで保存するときに使います。値を取り出すだけなら、C++23 の `std::to_underlying` が短く書けます。

```cpp
enum class Layer : std::uint8_t { kGround = 1, kAir = 2 };

template <class E>
void Save(std::ostream& os, E value) {
  auto raw = static_cast<std::underlying_type_t<E>>(value);   // Layer なら std::uint8_t
  os.write(reinterpret_cast<const char*>(&raw), sizeof(raw));
}
```

## よくあるミス

??? failure "列挙型以外に使う"
    列挙型でない型に使うと、コンパイルエラー（または未定義動作）です。`std::is_enum_v` で確かめてから使います。

??? failure "基になる型を省略した enum で大きさを決めつける"
    基の型を書かない `enum` は、環境によって大きさが変わります。保存に使うなら、`enum class Layer : std::uint8_t` のように明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_underlying`](../to_underlying.md) | 値を基底型に変換する（C++23） |
| [`is_enum`](is_enum.md) | 列挙型か調べる |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::underlying_type_t<Color>` は列挙型の基底の整数型
    - [x] `enum class` の既定は `int`
    - [x] 列挙型以外には使えない

## 関連ページ

- [cpprefjp: std::underlying_type](https://cpprefjp.github.io/reference/type_traits/underlying_type.html)
- [cppreference: std::underlying_type](https://en.cppreference.com/w/cpp/types/underlying_type)
