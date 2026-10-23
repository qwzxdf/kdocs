---
title: std::saturate_cast
summary: "整数を別の整数型に変換する。範囲を超えたら張り付く。"
order: 14
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::saturate_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

`int` の値を `uint8_t` に入れると、範囲外なら値が折り返されます。300 を `uint8_t` に入れると 44 になります。画像の色や音声のサンプルを小さな型に詰めるとき、範囲外は「端で止めたい」場面が多いはずです。

`std::saturate_cast` は、<strong>型を変換するとき、範囲を超えたら最大値か最小値に止める</strong>キャストです。

!!! tip "ポイント"
    - `std::saturate_cast<std::uint8_t>(300)` は 255
    - `std::saturate_cast<std::uint8_t>(-5)` は 0
    - 範囲内の値はそのまま変換される
    - C++26 で追加

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::saturate_cast {#saturate_cast}

<span class="ver ver-26">C++26</span>

```cpp
template <class R, class T>
constexpr R saturate_cast(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 整数型 | 変換先の型（テンプレート引数） |
| `x` | 整数型 | 変換する値 |

戻り値は、`x` を `R` に変換した値です。`x` が `R` の範囲を超えていれば `R` の最大値、下回っていれば最小値を返します。範囲内なら、値は変わりません。

普通の `static_cast` は、範囲外の値を折り返す（符号なしへ）か、処理系に任せます（符号つきへ）。結果を信用できないため、範囲の端で止めたい場合に、自分で `std::clamp` を使って書いていました。`saturate_cast` は、その定型を標準にしたものです。

整数型どうしの変換に使います。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  std::println("saturate_cast<uint8_t>(300)  = {}", std::saturate_cast<std::uint8_t>(300));
  std::println("saturate_cast<uint8_t>(-5)   = {}", std::saturate_cast<std::uint8_t>(-5));
  std::println("saturate_cast<uint8_t>(100)  = {}", std::saturate_cast<std::uint8_t>(100));
}
```

```text title="実行結果"
saturate_cast<uint8_t>(300)  = 255
saturate_cast<uint8_t>(-5)   = 0
saturate_cast<uint8_t>(100)  = 100
```

## ゲームでの使いどころ

計算した色を 8 ビットに詰めるときに使います。

```cpp
// 明るさを 1.5 倍にして、0〜255 に収めて保存する
const int boosted = static_cast<int>(pixel * 1.5f);
const std::uint8_t out = std::saturate_cast<std::uint8_t>(boosted);
```

## よくあるミス

??? failure "`static_cast` で折り返して、白が黒になる"
    `saturate_cast` を使います。

??? failure "浮動小数点数を渡す"
    整数型どうしが対象です。浮動小数点数は先に丸めて整数にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_sat`](add_sat.md) | 飽和する足し算 |
| [`clamp`](../algorithms/clamp.md) | 範囲に収める（型は変えない） |

## コンパイラ対応

C++26 の機能です。GCC と Clang の新しい版で使えます。対応状況はコンパイラのバージョンで確かめてください。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `saturate_cast<R>(x)` は範囲を超えたら端で止める変換
    - [x] `static_cast` と違い、折り返さない
    - [x] 色や音声の詰め込みに使う（C++26）

## 関連ページ

- [cpprefjp: std::saturate_cast](https://cpprefjp.github.io/reference/numeric/saturate_cast.html)
- [cppreference: std::saturate_cast](https://en.cppreference.com/w/cpp/numeric/saturate_cast)
