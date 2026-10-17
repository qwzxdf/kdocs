---
title: 小さな便利機能（to_underlying / byte / cmp_less など）
tags:
  - 型・言語サポート
---

# 小さな便利機能（to_underlying / byte / cmp_less など）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
<span class="ver ver-23">C++23</span>
`#include <utility>` / `#include <cstddef>`
</div>

このページでは、1 ページにするほどではないけれど知っておくと便利な、**小さな標準機能**をまとめます。enum class を整数に変える `std::to_underlying`、符号付きと符号なしを安全に比べる `std::cmp_less`、生のバイトを表す `std::byte`、「ここには絶対に来ない」を伝える `std::unreachable` などです。

!!! tip "ポイント"
    - enum class → 整数は **`std::to_underlying(e)`**（C++23）。
    - int と `size()` を比べるなら **`std::cmp_less(i, v.size())`**（警告もバグも出ない）。
    - 「この値は int に入る？」は **`std::in_range<int>(x)`**。
    - バイト列は `unsigned char` ではなく **`std::byte`**。

## 関数一覧

| 名前 | 重要度 | 何をする | ヘッダ |
| --- | --- | --- | --- |
| [`std::to_underlying`](#to_underlying) | <span class="rank rank-sometimes">たまに</span> | enum を中身の整数に変換 <span class="ver ver-23">C++23</span> | `<utility>` |
| [`std::cmp_less`](#cmp_less) | <span class="rank rank-sometimes">たまに</span> | 符号の違う整数を正しく比べる（<） <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::in_range`](#in_range) | <span class="rank rank-sometimes">たまに</span> | 値がその整数型に入るか <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::byte`](#byte) | <span class="rank rank-sometimes">たまに</span> | 生のバイトを表す型 <span class="ver ver-17">C++17</span> | `<cstddef>` |
| [`std::unreachable`](#unreachable) | <span class="rank rank-rare">知ってるだけ</span> | ここには来ないとコンパイラに伝える <span class="ver ver-23">C++23</span> | `<utility>` |
| [`std::cmp_equal`](#cmp_equal) | <span class="rank rank-rare">知ってるだけ</span> | 符号の違う整数を正しく比べる（==） <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::as_const`](#as_const) | <span class="rank rank-rare">知ってるだけ</span> | const 参照にする <span class="ver ver-17">C++17</span> | `<utility>` |
| [`std::to_integer`](#to_integer) | <span class="rank rank-rare">知ってるだけ</span> | byte を整数に <span class="ver ver-17">C++17</span> | `<cstddef>` |
| [`std::initializer_list`](#initializer_list) | <span class="rank rank-rare">知ってるだけ</span> | `{1, 2, 3}` を受け取る型 | `<initializer_list>` |

## 詳しい説明

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

### std::cmp_less {#cmp_less}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
constexpr bool cmp_less(T t, U u) noexcept;
```

- 符号付きと符号なしの整数を、**数学的に正しく**比べます。普通の `<` では、`-1 < 3u` が false になります（-1 が巨大な符号なし数に変換されるため）
- ほかに `cmp_greater`、`cmp_less_equal`、`cmp_greater_equal`、`cmp_not_equal` があります

```cpp
#include <print>
#include <utility>
#include <vector>

int main() {
  int index = -1;
  std::vector<int> v = {1, 2, 3};
  std::println("< の結果: {}", index < static_cast<long long>(v.size()));
  std::println("普通の比較だと -1 < 3u は {}", -1 < 3u);  // 警告も出る
  std::println("cmp_less(-1, 3u) は {}", std::cmp_less(index, v.size()));
}
```

```text title="実行結果"
< の結果: true
普通の比較だと -1 < 3u は false
cmp_less(-1, 3u) は true
```

### std::in_range {#in_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class R, class T>
constexpr bool in_range(T t) noexcept;
```

- `t` の値が、整数型 `R` で表せる範囲に入っていれば true。大きい型から小さい型へキャストする前の確認に使います

```cpp
#include <cstdint>
#include <print>
#include <utility>

int main() {
  long long big = 3'000'000'000;
  std::println("{} {} {}", std::in_range<int>(big), std::in_range<std::uint8_t>(200),
               std::in_range<std::uint8_t>(-1));
}
```

```text title="実行結果"
false true false
```

### std::byte {#byte}

<span class="ver ver-17">C++17</span>

```cpp
enum class byte : unsigned char {};
```

- 「数値でも文字でもない、ただのバイト」を表す型。足し算などはできず、ビット演算（`&`、`|`、`<<`）だけできます。ファイルやネットワークの生データに使うと、うっかり文字や数値として扱う間違いを防げます

### std::to_integer {#to_integer}

<span class="ver ver-17">C++17</span>

```cpp
template <class IntType>
constexpr IntType to_integer(std::byte b) noexcept;
```

- byte を整数に変換します

```cpp
#include <cstddef>
#include <print>
#include <vector>

int main() {
  std::vector<std::byte> data = {std::byte{0x12}, std::byte{0xF0}};
  std::byte masked = data[1] & std::byte{0x0F};
  std::println("{:#x} {:#x}", std::to_integer<int>(data[0]), std::to_integer<int>(masked));
}
```

```text title="実行結果"
0x12 0x0
```

### std::unreachable {#unreachable}

<span class="ver ver-23">C++23</span>

```cpp
[[noreturn]] void unreachable();
```

- 「ここには絶対に来ない」とコンパイラに伝えます。最適化に使われますが、**本当に来てしまうと未定義動作**です。switch で全部の enum を扱ったあとの最後などに使います

```cpp
#include <print>
#include <utility>

enum class Shape { kCircle, kSquare };

const char* Name(Shape s) {
  switch (s) {
    case Shape::kCircle:
      return "円";
    case Shape::kSquare:
      return "四角";
  }
  std::unreachable();  // 全部の case を書いたので、ここには来ない
}

int main() { std::println("{}", Name(Shape::kSquare)); }
```

```text title="実行結果"
四角
```

!!! warning
    デバッグ中は `assert(false)` のほうが、来てしまったときに気づけて安全です。

### std::cmp_equal {#cmp_equal}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
constexpr bool cmp_equal(T t, U u) noexcept;
```

- 符号の違う整数を正しく `==` で比べます（`-1 == 0xFFFFFFFFu` は普通の `==` だと true になる）

### std::as_const {#as_const}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
constexpr const T& as_const(T& t) noexcept;
```

- const 参照にします。const 版の関数を呼びたいときや、範囲 for で書き換えないことを保証したいときに使います

### std::initializer_list {#initializer_list}

```cpp
template <class E>
class initializer_list;
```

- `{1, 2, 3}` のような波かっこのリストを受け取る型。自作の関数やクラスで `{...}` を受け取れるようにします

```cpp
#include <initializer_list>
#include <print>
#include <utility>
#include <vector>

int Sum(std::initializer_list<int> values) {
  int total = 0;
  for (int v : values) {
    total += v;
  }
  return total;
}

int main() {
  std::vector<int> v = {1, 2};
  for (const int& x : std::as_const(v)) {
    std::print("{} ", x);
  }
  std::println("/ {} {}", Sum({1, 2, 3}), std::cmp_equal(-1, 0xFFFFFFFFu));
}
```

```text title="実行結果"
1 2 / 6 false
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 機能 |
| --- | --- |
| enum を配列の添字に | `to_underlying` |
| int の添字と size() の比較 | `cmp_less` |
| 読み込んだ数値が型に収まるか | `in_range` |
| ファイル・通信のバイト列 | `std::byte` |

## これだけ覚える

!!! abstract "まとめ"
    - [x] enum → 整数は to_underlying
    - [x] 符号の違う比較は cmp_less
    - [x] バイト列は std::byte

## 関連ページ

- [<type_traits>](type_traits.md)
- [cppreference: Utility library](https://en.cppreference.com/w/cpp/utility)
