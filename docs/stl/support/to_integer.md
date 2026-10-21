---
title: std::to_integer
summary: "`std::byte` を整数に変換する。"
order: 6
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::to_integer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cstddef>`
</div>

`std::to_integer<T>(b)` は、**`std::byte` を整数型 T に変換する**関数です。`std::byte` は整数として扱えないので、値を調べたり表示したりするときに使います。

!!! tip "ポイント"
    - `std::to_integer<int>(b)` のように、変換先の型を指定する。
    - `static_cast<int>(b)` ではなく、こちらを使う（意図が分かりやすい）。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリの中身を 16 進数で表示する | `std::println("{:02x}", std::to_integer<int>(b))` |

## よくあるミス

??? failure "型を省略する"
    変換先の型を `<int>` のように指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`byte`](byte.md) | 元の型 |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] byte を整数にする
    - [x] 変換先の型を指定
    - [x] 算術のときに使う

## 関連ページ

- [cpprefjp: std::to_integer](https://cpprefjp.github.io/reference/utility/to_integer.html)
- [cppreference: std::to_integer](https://en.cppreference.com/w/cpp/utility/to_integer)
