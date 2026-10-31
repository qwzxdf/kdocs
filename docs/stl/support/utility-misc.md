---
title: 小さな便利機能（to_underlying / byte / cmp_less など）
summary: "`to_underlying`、`cmp_less`、`byte` など細かい便利道具。"
order: 85
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

enum class の値を整数にしたい、符号付きと符号なしを安全に比べたい、生のバイトを `char` と区別したい。こうした小さな要望には、標準ライブラリが答えを用意しています。1 ページにするほどではないけれど知っておくと便利な、<strong>小さな標準機能</strong>を、このページにまとめます。enum class を整数に変える `std::to_underlying`、符号付きと符号なしを安全に比べる `std::cmp_less`、生のバイトを表す `std::byte`、「ここには絶対に来ない」を伝える `std::unreachable` などです。

!!! tip "ポイント"
    - enum class → 整数は **`std::to_underlying(e)`**（C++23）。
    - int と `size()` を比べるなら **`std::cmp_less(i, v.size())`**（警告もバグも出ない）。
    - 「この値は int に入る？」は **`std::in_range<int>(x)`**。
    - バイト列は `unsigned char` ではなく **`std::byte`**。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数一覧

| 名前 | 重要度 | 何をする | ヘッダ |
| --- | --- | --- | --- |
| [`std::to_underlying`](to_underlying.md) | <span class="rank rank-sometimes">たまに</span> | enum を中身の整数に変換 <span class="ver ver-23">C++23</span> | `<utility>` |
| [`std::cmp_less`](cmp_less.md) | <span class="rank rank-sometimes">たまに</span> | 符号の違う整数を正しく比べる（<） <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::in_range`](in_range.md) | <span class="rank rank-sometimes">たまに</span> | 値がその整数型に入るか <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::byte`](byte.md) | <span class="rank rank-sometimes">たまに</span> | 生のバイトを表す型 <span class="ver ver-17">C++17</span> | `<cstddef>` |
| [`std::unreachable`](unreachable.md) | <span class="rank rank-rare">知ってるだけ</span> | ここには来ないとコンパイラに伝える <span class="ver ver-23">C++23</span> | `<utility>` |
| [`std::cmp_equal`](cmp_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号の違う整数を正しく比べる（==） <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::as_const`](as_const.md) | <span class="rank rank-rare">知ってるだけ</span> | const 参照にする <span class="ver ver-17">C++17</span> | `<utility>` |
| [`std::to_integer`](to_integer.md) | <span class="rank rank-rare">知ってるだけ</span> | byte を整数に <span class="ver ver-17">C++17</span> | `<cstddef>` |
| [`std::initializer_list`](../containers/initializer_list.md) | <span class="rank rank-rare">知ってるだけ</span> | `{1, 2, 3}` を受け取る型 | `<initializer_list>` |
| [`std::cmp_not_equal`](cmp_not_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を安全に `!=` で比べる。 <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::cmp_greater`](cmp_greater.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を安全に `>` で比べる。 <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::cmp_less_equal`](cmp_less_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を安全に `<=` で比べる。 <span class="ver ver-20">C++20</span> | `<utility>` |
| [`std::cmp_greater_equal`](cmp_greater_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を安全に `>=` で比べる。 <span class="ver ver-20">C++20</span> | `<utility>` |

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
