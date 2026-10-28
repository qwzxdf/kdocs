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

列挙型を `enum class` にすると、名前が衝突せず、整数との暗黙の変換もないので、安全です。その反面、配列の添え字に使いたいときや、ビットフラグを計算したいときに、`static_cast<int>(e)` と書く必要があります。`static_cast<int>` は、`enum` の元の型が `uint8_t` に変わったときに、気づかずに型が合わなくなります。C++23 の `std::to_underlying` は、`enum` の元の型に自動でそろえて、整数に変換してくれる関数です。

!!! tip "ポイント"
    - `enum class` は暗黙に整数へ変換されない。そのとき使う。
    - `static_cast<int>` と違い、元の型に合わせて変換される。
    - C++23 の機能。

!!! info "このページを読む前に"
    `enum class` の基本が分かると読みやすいです。通常の `enum` と違って、整数との暗黙の変換がありません。

## 関数の詳しい説明

### std::to_underlying {#to_underlying}

<span class="ver ver-23">C++23</span>

```cpp
template <class Enum>
constexpr std::underlying_type_t<Enum> to_underlying(Enum e) noexcept;
```

- enum の値を中身の整数型に変換します。`static_cast<int>(e)` と違って、中身の型を自分で書かなくていいです

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

配列の添え字に `enum class` を使うときに便利です。`std::array<Texture, kTextureCount> textures; textures[std::to_underlying(TextureId::kPlayer)]` と書けます。

ビットフラグでは、`enum class Flag : uint8_t { kA = 1, kB = 2 }` の値をビット演算に使いたいときに、`std::to_underlying(Flag::kA) | std::to_underlying(Flag::kB)` と書きます。演算子オーバーロードを用意して隠す書き方もよく使われます。

シリアライズでは、`enum` を整数として保存する場面で使います。保存先の型を `enum` の元の型にそろえると、バイト数がぶれません。

## よくあるミス

??? failure "通常の `enum` に使って意味がない"
    通常の `enum` は暗黙に整数へ変換されるので、`to_underlying` は不要です。`enum class` のときに使います。

??? failure "`static_cast<int>` のまま、型が合わなくなる"
    `enum class E : uint8_t` の値を `static_cast<int>` で変換すると、元の型より大きい `int` になって、保存時のバイト数がずれることがあります。`to_underlying` は元の型のままです。

??? failure "C++20 で使えなくてコンパイルエラーになる"
    `to_underlying` は C++23 の機能です。C++20 では `static_cast<std::underlying_type_t<E>>(e)` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`underlying_type`](type_traits/underlying_type.md) | 元の整数型 |
| `static_cast<int>` | 従来の書き方 |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `enum class` を元の整数型に変換する。
    - [x] `static_cast<int>` と違い、元の型に自動でそろう。
    - [x] C++23 の機能。C++20 では `underlying_type_t` と `static_cast` で書く。

## 関連ページ

- [cpprefjp: std::to_underlying](https://cpprefjp.github.io/reference/utility/to_underlying.html)
- [cppreference: std::to_underlying](https://en.cppreference.com/w/cpp/utility/to_underlying)
