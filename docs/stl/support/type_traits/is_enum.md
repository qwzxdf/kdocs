---
title: std::is_enum
summary: "列挙型（enum）かを調べる。"
order: 6
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

列挙型を整数に変換して保存する処理を書きたい。`std::is_enum` は、<strong>型が列挙型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_enum_v<T>` は、`T` が列挙型（`enum` または `enum class`）か
    - `enum` と `enum class` のどちらも `true`
    - `std::is_enum<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `std::byte` は `enum class` なので `true`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_enum_v {#is_enum}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_enum_v = is_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`enum` と `enum class` のどちらも `true` です。整数や、整数の別名は `false` です。`std::byte` は `enum class` なので `true` になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class Color { kRed, kBlue };
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Color                      -> {}", std::is_enum_v<Color>);
  std::println("int                        -> {}", std::is_enum_v<int>);
  std::println("Player                     -> {}", std::is_enum_v<Player>);
}
```

```text title="実行結果"
Color                      -> true
int                        -> false
Player                     -> false
```

## ゲームでの使いどころ

列挙型を、基になる整数の型で書き出す、シリアライズの入り口に使えます。

```cpp
template <class T>
void Write(std::ostream& os, T value) {
  if constexpr (std::is_enum_v<T>) {
    auto raw = std::to_underlying(value);
    os.write(reinterpret_cast<const char*>(&raw), sizeof(raw));
  } else {
    os.write(reinterpret_cast<const char*>(&value), sizeof(value));
  }
}
```

## よくあるミス

??? failure "std::byte を整数だと思う"
    `std::byte` は `enum class` なので、`is_enum_v` が `true`、`is_integral_v` が `false` です。

??? failure "定数の集まりを enum だと思う"
    `constexpr int kA = 0;` のような定数は、列挙型ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_scoped_enum`](is_scoped_enum.md) | `enum class` か（C++23） |
| [`underlying_type`](underlying_type.md) | 基になる整数の型を取り出す |
| [`is_integral`](is_integral.md) | 整数型か。列挙型は含まない |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_enum_v<T>` は、`T` が列挙型（`enum` または `enum class`）か
    - [x] 列挙型なら `true`（`enum class` も含む）
    - [x] `std::byte` も列挙型

## 関連ページ

- [cpprefjp: std::is_enum](https://cpprefjp.github.io/reference/type_traits/is_enum.html)
- [cppreference: std::is_enum](https://en.cppreference.com/w/cpp/types/is_enum)
