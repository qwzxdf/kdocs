---
title: std::div_sat
summary: "割り算。範囲を超える唯一の場合（最小値 ÷ −1）で張り付く。"
order: 13
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::div_sat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

体力に回復量を足すとき、最大値を超えて 0 に折り返してしまったら大変です。符号なしの 8 ビットの体力 250 に 10 を足すと、普通は 260 ではなく、折り返して 4 になります。

`std::div_sat` は、<strong>結果が型の範囲を超えたら、最大値（または最小値）で止める</strong>、飽和演算の割り算です。

!!! tip "ポイント"
    - `std::div_sat<std::int8_t>` は、結果が範囲を超えたら最大値か最小値に止める
    - 桁あふれによる折り返し（符号なし）や未定義動作（符号つき）が起きない
    - 引数は両方とも同じ型。型を明示して呼ぶことが多い
    - C++26 で追加

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::div_sat {#div_sat}

<span class="ver ver-26">C++26</span>

```cpp
template <class T>
constexpr T div_sat(T x, T y) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 整数型 | 1 つ目の値 |
| `y` | `x` と同じ型 | 2 つ目の値 |

戻り値は、`x` と `y` の割り算の結果です。ただし、結果が `T` の範囲を超える場合、最大値または最小値に止めて返します（飽和）。

通常の整数演算では、符号なし整数は折り返し、符号つき整数の桁あふれは未定義動作になります。飽和演算は、そのどちらも起こさず、範囲の端で止まります。画像処理の色の計算（0〜255 に収める）、音声の振幅の加算、体力・弾薬の増減のように、「範囲を超えたら端で止める」処理に適しています。

型は、引数から決まります。`int` のリテラルを渡すと `int` の演算になるので、8 ビットなどの小さい型で演算したい場合は、`div_sat<int8_t>` のようにテンプレート引数で型を指定します。

`INT_MIN / -1` のような、結果が表せない割り算は、飽和して端の値になります。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  // `INT_MIN / -1` のような、結果が表せない割り算
  std::println("std::div_sat<std::int8_t>(-128, -1) = {}", std::div_sat<std::int8_t>(-128, -1));
}
```

```text title="実行結果"
std::div_sat<std::int8_t>(-128, -1) = 127
```

## ゲームでの使いどころ

8 ビットの色や、小さい整数型の体力など、範囲が狭い値の増減に使います。

```cpp
// 体力 (0〜255) に回復を足す。255 を超えたら 255 で止まる
health = std::add_sat(health, heal);
```

範囲の確認を `if` で書く手間が省けて、折り返しのバグが起きません。

## よくあるミス

??? failure "`int` の演算になってしまい、8 ビットの範囲で飽和しない"
    `std::div_sat<std::uint8_t>(...)` のように型を指定するか、引数の型を合わせます。

??? failure "C++23 以前のコンパイラで使えない"
    C++26 の機能です。古い環境では `std::clamp` などで書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_sat`](add_sat.md) | 飽和演算 |
| [`sub_sat`](sub_sat.md) | 飽和演算 |
| [`saturate_cast`](saturate_cast.md) | 型を変えるときに範囲で止める |

## コンパイラ対応

C++26 の機能です。GCC と Clang の新しい版で使えます。対応状況はコンパイラのバージョンで確かめてください。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `div_sat` は結果が範囲を超えたら端の値で止める
    - [x] 折り返しも未定義動作も起きない
    - [x] 色や体力など、範囲の狭い値の増減に使う（C++26）

## 関連ページ

- [cpprefjp: std::div_sat](https://cpprefjp.github.io/reference/numeric/div_sat.html)
- [cppreference: std::div_sat](https://en.cppreference.com/w/cpp/numeric/div_sat)
