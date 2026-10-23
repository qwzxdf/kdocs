---
title: std::float_round_style
summary: "浮動小数点の丸めの方向を表す列挙型。"
order: 900
tags:
  - 数値
---

# std::float_round_style

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <limits>`
</div>

浮動小数点数の演算結果は、表せない部分を丸めます。どの向きに丸めるかを表す列挙型が `std::float_round_style` です。`std::numeric_limits<T>::round_style` が返す型として登場します。

!!! tip "ポイント"
    - `round_to_nearest`（最も近い値へ）、`round_toward_zero`（0 方向）、`round_toward_infinity`、`round_toward_neg_infinity`、`round_indeterminate` の 5 値
    - `numeric_limits<T>::round_style` の型
    - 現代の PC では `float` / `double` ともに `round_to_nearest`
    - 実際の丸めモードは `fegetround` で調べる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::float_round_style {#float_round_style}

<span class="ver ver-11">C++11</span>

```cpp
enum float_round_style {
  round_indeterminate = -1,
  round_toward_zero = 0,
  round_to_nearest = 1,
  round_toward_infinity = 2,
  round_toward_neg_infinity = 3
};
```

`std::numeric_limits<T>::round_style` が、型 `T` の演算の標準的な丸め方向を表します。IEEE 754 に従う環境の `float` / `double` は `round_to_nearest` です。整数型は `round_toward_zero` です。

注意点は、この値が「型の標準の丸め方」を表すだけで、プログラムの実行中に `fesetround` で丸めモードを変えても、`round_style` は変わらないことです。実行時の丸めモードは `std::fegetround()` で調べます。

## 実際に動かしてみる

```cpp
#include <limits>
#include <print>

int main() {
  std::println("float は最も近い値へ丸める: {}",
               std::numeric_limits<float>::round_style == std::round_to_nearest);
  std::println("int は 0 方向へ丸める: {}",
               std::numeric_limits<int>::round_style == std::round_toward_zero);
}
```

```text title="実行結果"
float は最も近い値へ丸める: true
int は 0 方向へ丸める: true
```

## ゲームでの使いどころ

型の性質を調べて、テンプレートの分岐に使う、ライブラリ作者向けの情報です。ゲームのコードで直接使う場面はほとんどありません。

## よくあるミス

??? failure "`round_style` を実行時の丸めモードと思う"
    実行時の丸めモードは `fegetround` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`float_denorm_style`](float_denorm_style.md) | 非正規化数を表す列挙型 |
| [`fegetround`](fegetround.md) | 実行時の丸めモード |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `float_round_style` は丸め方向を表す列挙型
    - [x] `numeric_limits::round_style` の型
    - [x] 実行時の丸めモードは `fegetround`

## 関連ページ

- [cpprefjp: std::float_round_style](https://cpprefjp.github.io/reference/limits/float_round_style.html)
- [cppreference: std::float_round_style](https://en.cppreference.com/w/cpp/types/numeric_limits/float_round_style)
