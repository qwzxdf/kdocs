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

`<stdfloat>` は、**ビット数が決まった浮動小数点型**（`std::float16_t`、`std::float32_t`、`std::float64_t`、`std::float128_t`、`std::bfloat16_t`）を定義するヘッダーです。GPU との間でやりとりする半精度（16 ビット）の小数を、型として表せます。**環境が対応していない型は定義されない**ので、`#ifdef __STDCPP_FLOAT16_T__` で確認します。

!!! tip "ポイント"
    - `float32_t` は多くの環境で `float` と同じ。
    - `float16_t`（半精度）と `bfloat16_t`（脳用の精度）は、対応環境が限られる。
    - GPU のバッファに半精度を使う、機械学習の重みを持つ、といった用途。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### <stdfloat> {#stdfloat}

```cpp
using float16_t = /* 実装定義 */;   // __STDCPP_FLOAT16_T__ が定義されていれば使える
```

- 戻り値: （型）
- 計算量: O(1)

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_FLOAT16_T__
  std::println("{} {}", sizeof(std::float16_t), sizeof(std::bfloat16_t));
#else
  std::println("float16_t は未対応");
#endif
}
```

```text title="実行結果"
2 2（対応した環境の場合）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| GPU と共有するバッファに半精度を使う | `std::float16_t` |

## よくあるミス

??? failure "MSVC で使えると思う"
    MSVC は半精度をまだサポートしていません。`#ifdef` で確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型の性質を調べる |
| [`cstdint`](cstdint.md) | 整数の大きさが決まった型 |

## コンパイラ対応

C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビット数が決まった小数型
    - [x] 対応していない環境がある
    - [x] GPU の半精度に

## 関連ページ

- [cpprefjp: <stdfloat>（float16_t・bfloat16_t など）](https://cpprefjp.github.io/reference/stdfloat.html)
- [cppreference: <stdfloat>（float16_t・bfloat16_t など）](https://en.cppreference.com/w/cpp/types/floating-point)
