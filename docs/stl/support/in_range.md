---
title: std::in_range
summary: "整数の値が、ある整数型の範囲に収まるかを調べる。"
order: 4
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::in_range

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`std::in_range<T>(x)` は、**整数 x が、型 T で表せる範囲に収まっているか**を調べる関数です。`int` を `uint8_t` に変換する前に、桁あふれしないか確認するときに使います。

!!! tip "ポイント"
    - `in_range<std::uint8_t>(300)` は `false`。
    - 符号の違いも正しく扱う（`in_range<unsigned>(-1)` は `false`）。
    - 変換の前に確認して、変換する。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パケットのフィールドに収まるか確認してから代入する | `if (std::in_range<std::uint8_t>(value))` |

## よくあるミス

??? failure "変換してから確認する"
    変換後は値が壊れています。変換の前に調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::saturate_cast`](../numeric/saturate_cast.md) | 範囲に張り付ける |
| [`cmp_less`](cmp_less.md) | 正しく比べる |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型の範囲に収まるか
    - [x] 変換の前に調べる
    - [x] C++20

## 関連ページ

- [cpprefjp: std::in_range](https://cpprefjp.github.io/reference/utility/in_range.html)
- [cppreference: std::in_range](https://en.cppreference.com/w/cpp/utility/in_range)
