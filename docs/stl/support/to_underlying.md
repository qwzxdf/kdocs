---
title: std::to_underlying
summary: "列挙型の値を、元の整数型に変換する。"
order: 1
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::to_underlying

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-23">C++23</span>
`#include <utility>`
</div>

`std::to_underlying(e)` は、**列挙型（`enum class`）の値を、内部の整数型に変換する**関数です。`static_cast<int>(e)` と書くより、型の指定が要らず、`enum` の元の型が変わっても追従します。配列の添字や、ビットフラグの計算に使います。

!!! tip "ポイント"
    - `enum class` は暗黙に整数へ変換されない。そのとき使う。
    - `static_cast<int>` と違い、元の型に合わせて変換される。
    - C++23 の機能。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::to_underlying {#to_underlying}

<span class="ver ver-23">C++23</span>

```cpp
template <class Enum>
constexpr std::underlying_type_t<Enum> to_underlying(Enum e) noexcept;
```

- enum の値を、中身の整数型に変換します。`static_cast<int>(e)` と違って、中身の型を自分で書かなくていいです

```cpp
#include <array>
#include <print>
#include <utility>

enum class Direction { kUp, kRight, kDown, kLeft };

int main() {
  std::array<const char*, 4> names = {"上", "右", "下", "左"};
  Direction d = Direction::kDown;
  std::println("{} は {} 番", names[std::to_underlying(d)], std::to_underlying(d));
}
```

```text title="実行結果"
下 は 2 番
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 列挙型を配列の添字にする | `table[std::to_underlying(type)]` |
| ビットフラグの計算 | `std::to_underlying(a) | std::to_underlying(b)` |

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能です。`static_cast<std::underlying_type_t<E>>(e)` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`underlying_type`](type_traits/underlying_type.md) | 元の整数型 |
| `static_cast<int>` | 従来の書き方 |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] enum を元の整数型にする
    - [x] `static_cast` より安全
    - [x] C++23

## 関連ページ

- [cpprefjp: std::to_underlying](https://cpprefjp.github.io/reference/utility/to_underlying.html)
- [cppreference: std::to_underlying](https://en.cppreference.com/w/cpp/utility/to_underlying)
