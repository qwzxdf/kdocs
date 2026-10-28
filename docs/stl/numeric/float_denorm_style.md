---
title: std::float_denorm_style
summary: "非正規数を持つかを表す列挙型。"
order: 900
tags:
  - 数値
---

# std::float_denorm_style

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <limits>`
</div>

浮動小数点数が表せる最小の正規化された値より小さい値を非正規化数（サブノーマル）と呼びます。この非正規化数をサポートしているかを表す列挙型が `std::float_denorm_style` です。ただし、C++23 で非推奨になりました。

!!! tip "ポイント"
    - `std::denorm_present`（サポートあり）、`denorm_absent`（なし）、`denorm_indeterminate`（不明）の 3 値
    - `numeric_limits<T>::has_denorm` の型として登場する
    - C++23 で非推奨。`denorm_min()` で確かめる
    - 現代の環境では、ほぼ `denorm_present`

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::float_denorm_style {#float_denorm_style}

<span class="ver ver-11">C++11</span>

```cpp
enum float_denorm_style {
  denorm_indeterminate = -1,
  denorm_absent = 0,
  denorm_present = 1
};
```

`std::numeric_limits<T>::has_denorm` が返す型で、型 `T` が非正規化数をサポートしているかを表します。IEEE 754 に従う現代の環境では `denorm_present` です。

C++23 では、`has_denorm` と `has_denorm_loss`、この列挙型が非推奨になりました。値が環境で変わるのに、実際の挙動（FTZ モードの設定など）を反映しないため、信頼できなかったからです。非正規化数があるかを確かめたいときは、`std::numeric_limits<T>::denorm_min() > 0` を調べます。

ゲームでは、非正規化数が計算を遅くする場面（音声のフィルターなど）に関わりますが、このenum を直接使うことはありません。

## 実際に動かしてみる

```cpp
#include <limits>
#include <print>

int main() {
  // denorm_min() が 0 より大きければ、非正規化数がある
  std::println("非正規化数がある: {}", std::numeric_limits<float>::denorm_min() > 0.0f);
}
```

```text title="実行結果"
非正規化数がある: true
```

## ゲームでの使いどころ

新しいコードでは使いません。非正規化数の有無は `denorm_min()` で確かめます。

## よくあるミス

??? failure "C++23 で非推奨の警告が出る"
    `denorm_min() > 0` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`float_round_style`](float_round_style.md) | 丸めの方式を表す列挙型 |
| [`numeric_limits`](limits.md) | 型の性質を調べる |

## コンパイラ対応

C++11 から使えます。C++23 で非推奨になりました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `float_denorm_style` は非正規化数のサポートを表す列挙型
    - [x] C++23 で非推奨
    - [x] 代わりに `denorm_min() > 0` で確かめる

## 関連ページ

- [cpprefjp: std::float_denorm_style](https://cpprefjp.github.io/reference/limits/float_denorm_style.html)
- [cppreference: std::float_denorm_style](https://en.cppreference.com/w/cpp/types/numeric_limits/float_denorm_style)
