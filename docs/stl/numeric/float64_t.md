---
title: std::float64_t
summary: "64 ビットの浮動小数点型。"
order: 900
tags:
  - 数値
---

# std::float64_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stdfloat>`
</div>

`float` や `double` の大きさは環境で違うことがあります。`std::float64_t` は、64 ビットの浮動小数点型です。倍精度（64 ビット）。`double` と同じ大きさで、IEEE 754 の形式であることが保証されます。実装が対応していない場合は定義されないので、`__STDCPP_FLOAT64_T__` マクロで確かめて使います。

!!! tip "ポイント"
    - 実装が対応していない型は定義されない。
    - `__STDCPP_FLOAT64_T__` で対応を確かめる。
    - リテラルは接尾辞（`f16`・`bf16`・`f32`・`f64`・`f128`）。

!!! info "このページを読む前に"
    [`<stdfloat>`](stdfloat.md) を先に読んでください。

## 関数の詳しい説明

### std::float64_t {#float64_t}

```cpp
using float64_t = /* 実装定義の 64 ビット浮動小数点型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_FLOAT64_T__
  std::println("{}", sizeof(std::float64_t));
#endif
}
```

```text title="実行結果"
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| GPU に渡す大量の値の形式 | `std::float64_t` |

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
    - [x] 64 ビットの浮動小数点型
    - [x] 対応はマクロで確かめる
    - [x] C++23

## 関連ページ

- [cpprefjp: std::float64_t](https://cpprefjp.github.io/reference/stdfloat/float64_t.html)
- [cppreference: std::float64_t](https://en.cppreference.com/w/cpp/types/floating-point/float64_t)
