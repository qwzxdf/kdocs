---
title: std::ranges::output_range
summary: "書き込める範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::output_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::copy` の出力先には、書き込める範囲が必要です。`std::ranges::output_range<R, T>` は、<strong>範囲 `R` に、型 `T` の値を書き込めること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::output_range<R, T>`: `R` に `T` の値を書き込めるか
    - `const` のコンテナは満たさない
    - 要素の型に `T` が代入できること
    - 出力先の範囲を受け取るアルゴリズムの制約

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::output_range {#output_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class R, class T>
concept output_range = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 範囲 | 書き込み先の範囲 |
| `T` | 型 | 書き込む値の型 |

`R` の要素を書き換えられて、`T` が代入できる型なら満たします。`const std::vector<int>` は書き換えられないので満たしません。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("vector<int> に int         : {}", std::ranges::output_range<std::vector<int>, int>);
  std::println("const vector<int> に int   : {}", std::ranges::output_range<const std::vector<int>, int>);
}
```

```text title="実行結果"
vector<int> に int         : true
const vector<int> に int   : false
```

## ゲームでの使いどころ

出力先を引数に取る自作のアルゴリズムに使います。

## よくあるミス

??? failure "`const` の範囲に書こうとする"
    書き込み先は `const` でない範囲です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_range`](input_range.md) | 読める範囲 |
| [`range`](range.md) | 基本の範囲 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `output_range<R, T>` は `R` に `T` を書き込めるか
    - [x] `const` のコンテナは満たさない
    - [x] 出力先の制約に使う

## 関連ページ

- [cpprefjp: std::ranges::output_range](https://cpprefjp.github.io/reference/ranges/output_range.html)
- [cppreference: std::ranges::output_range](https://en.cppreference.com/w/cpp/ranges/output_range)
