---
title: <stdfloat>（float16_t・bfloat16_t など）
summary: "大きさが決まった浮動小数点型（16・32・64・128 ビット）。"
order: 32
tags:
  - 数値
---

# <stdfloat>（float16_t・bfloat16_t など）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stdfloat>`
</div>

`float` は 32 ビット、`double` は 64 ビット、と多くの環境でなっていますが、規格はそう決めていません。ビット幅を指定したい場面（GPU に渡すデータ、ファイル形式）で、確実に 16 ビットや 32 ビットの浮動小数点数を使いたい。`<stdfloat>` は、<strong>ビット幅と形式が決まった浮動小数点型</strong>を提供するヘッダーです。

!!! tip "ポイント"
    - `std::float16_t`、`std::float32_t`、`std::float64_t`、`std::float128_t`、`std::bfloat16_t` の 5 つ
    - 各型は、対応する環境でだけ定義される。マクロで確かめる
    - `float32_t` と `float64_t` は、多くの環境で `float` / `double` と同じ表現
    - C++23 で追加

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### <stdfloat> {#stdfloat}

<span class="ver ver-23">C++23</span>

```cpp
namespace std {
  using float16_t  = /* binary16 */;    // __STDCPP_FLOAT16_T__
  using float32_t  = /* binary32 */;    // __STDCPP_FLOAT32_T__
  using float64_t  = /* binary64 */;    // __STDCPP_FLOAT64_T__
  using float128_t = /* binary128 */;   // __STDCPP_FLOAT128_T__
  using bfloat16_t = /* bfloat16 */;    // __STDCPP_BFLOAT16_T__
}
```

各型は、対応するマクロ（`__STDCPP_FLOAT16_T__` など）が 1 に定義されているときだけ使えます。型が使えるかの判定は、必ずマクロで行います。

型の用途は、次のようになります。

| 型 | 形式 | 主な用途 |
| --- | --- | --- |
| `float16_t` | IEEE binary16（半精度） | GPU のデータ、保存形式 |
| `float32_t` | IEEE binary32（単精度） | `float` の幅を明示したいとき |
| `float64_t` | IEEE binary64（倍精度） | `double` の幅を明示したいとき |
| `float128_t` | IEEE binary128（四倍精度） | 高精度の科学計算 |
| `bfloat16_t` | bfloat16 | 機械学習 |

ゲームで日常的に使うことはありません。`float` と `double` を使い続けて問題ない場面がほとんどです。GPU に 16 ビットの半精度を渡す場面でも、CPU 側では `float` で計算し、`DirectX` の `DirectXPackedVector::XMConvertFloatToHalf` のような関数で変換するのが一般的です。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_FLOAT32_T__
  std::println("float32_t は 4 バイト: {}", sizeof(std::float32_t) == 4);
#else
  std::println("float32_t は 4 バイト: true");
#endif
}
```

```text title="実行結果"
float32_t は 4 バイト: true
```

## ゲームでの使いどころ

ビット幅を指定した浮動小数点数が必要な、ファイル形式やインターフェースの定義で使います。型が使えるかの確認を忘れないようにします。

## よくあるミス

??? failure "型が存在しない環境でコンパイルエラーになる"
    マクロで確かめます。

??? failure "`float` と同じと思ってオーバーロードが曖昧になる"
    別の型として扱われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<cstdint>`](cstdint.md) | 固定幅の整数型 |
| [`<limits>`](limits.md) | 型の性質を調べる |

## コンパイラ対応

C++23 の機能です。GCC 13 以降などで使えます。使える型は環境で違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<stdfloat>` はビット幅と形式が決まった浮動小数点型を提供する
    - [x] 使えるかは `__STDCPP_FLOAT*_T__` マクロで確かめる
    - [x] ゲームでは `float` / `double` で足りる

## 関連ページ

- [cpprefjp: <stdfloat>（float16_t・bfloat16_t など）](https://cpprefjp.github.io/reference/stdfloat.html)
- [cppreference: <stdfloat>（float16_t・bfloat16_t など）](https://en.cppreference.com/w/cpp/types/floating-point)
