---
title: std::bfloat16_t
summary: "16 ビットの浮動小数点型。"
order: 900
tags:
  - 数値
---

# std::bfloat16_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stdfloat>`
</div>

`float` や `double` の大きさは環境で違うことがあります。`std::bfloat16_t` は、16 ビットの浮動小数点型です。ブレイン浮動小数点（16 ビット）。指数部が `float` と同じ 8 ビットで、範囲は広く精度は低い形式です。機械学習で使われます。実装が対応していない場合は定義されないので、`__STDCPP_BFLOAT16_T__` マクロで確かめて使います。

!!! tip "ポイント"
    - 実装が対応していない型は定義されない。
    - `__STDCPP_BFLOAT16_T__` で対応を確かめる。
    - リテラルは接尾辞（`f16`・`bf16`・`f32`・`f64`・`f128`）。

!!! info "このページを読む前に"
    [`<stdfloat>`](stdfloat.md) を先に読んでください。

## 関数の詳しい説明

### std::bfloat16_t {#bfloat16_t}

```cpp
using bfloat16_t = /* 実装定義の 16 ビット浮動小数点型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_BFLOAT16_T__
  std::println("{}", sizeof(std::bfloat16_t));
#endif
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| GPU に渡す大量の値の形式 | `std::bfloat16_t` |

## よくあるミス

??? failure "対応を確かめずに使う"
    対応していないコンパイラでは、型が存在せずコンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<stdfloat>`](stdfloat.md) | 概要 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 16 ビットの浮動小数点型
    - [x] 対応はマクロで確かめる
    - [x] C++23

## 関連ページ

- [cpprefjp: std::bfloat16_t](https://cpprefjp.github.io/reference/stdfloat/bfloat16_t.html)
- [cppreference: std::bfloat16_t](https://en.cppreference.com/w/cpp/types/floating-point/bfloat16_t)
