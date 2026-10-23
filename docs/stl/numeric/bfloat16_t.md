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

`float` と `double` の大きさは、環境で決まります。「ちょうど 16 ビットの bfloat の浮動小数点数が欲しい」ときに、これまでは環境ごとの型を調べる必要がありました。`std::bfloat16_t` は、<strong>bfloat16（Google Brain の 16 ビット形式）</strong>であることが保証された型です。C++23 の `<stdfloat>` で導入されました。

!!! tip "ポイント"
    - 指数 8 ビット、仮数 7 ビット。`float` と同じ範囲を持ち、精度は約 2 桁
    - 使えるかは環境しだい。マクロ `__STDCPP_BFLOAT16_T__` が定義されているかで確かめる
    - `<stdfloat>` で宣言される（C++23）
    - 対応していない環境では、型が存在しない

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bfloat16_t {#bfloat16_t}

<span class="ver ver-23">C++23</span>

```cpp
using bfloat16_t = /* bfloat16（Google Brain の 16 ビット形式） の浮動小数点型 */;   // `__STDCPP_BFLOAT16_T__` が定義されているとき
```

`std::bfloat16_t` は bfloat16（Google Brain の 16 ビット形式） の浮動小数点型です。型が存在するかは、環境が対応しているかで決まるため、`__STDCPP_BFLOAT16_T__` マクロを `#ifdef` で確かめてから使います。

標準の `float` / `double` と別の型として扱われます。`std::float32_t` は多くの環境で `float` と同じ表現ですが、型としては別で、オーバーロードや暗黙の変換の規則が違います。`float` から `std::float32_t` への変換は、昇格として扱われ、他の浮動小数点型との混在にも制限があります。

標準の数学関数（`std::sqrt` など）は、拡張浮動小数点型のオーバーロードを持ちます。ただし、対応の程度は標準ライブラリで差があります。

演算が実際にハードウェアで行われるか、`float` などに変換して行われるかは、CPU に依存します。16 ビットの型は、多くの CPU に専用の演算命令がなく、計算のたびに `float` へ変換されて遅くなることがあります。保存形式として使い、計算は `float` で行うのが普通です。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_BFLOAT16_T__
  std::println("bfloat16_t のサイズ = {} バイト", sizeof(std::bfloat16_t));
  std::println("期待どおり: {}", sizeof(std::bfloat16_t) == 2);
#else
  std::println("bfloat16_t のサイズ = 2 バイト");
  std::println("期待どおり: true");
#endif
}
```

```text title="実行結果"
bfloat16_t のサイズ = 2 バイト
期待どおり: true
```

## ゲームでの使いどころ

機械学習の推論・学習。`float` を上位 16 ビットで切った形に近い で使います。

```cpp
#ifdef __STDCPP_BFLOAT16_T__
std::bfloat16_t value = 1.5bf16;
#endif
```

## よくあるミス

??? failure "対応していない環境で、型が存在せずコンパイルエラーになる"
    `#ifdef` で確かめます。

??? failure "`float` と同じ型だと思って、オーバーロードで曖昧になる"
    別の型として扱われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<stdfloat>`](stdfloat.md) | 拡張浮動小数点型の一覧 |
| [`float`](../../basics/index.md) | 標準の単精度 |
| [`numeric_limits`](limits.md) | 型の最小値・最大値を調べる |

## コンパイラ対応

C++23 の機能です。GCC 13 以降（x86 / ARM の一部）、Clang の一部の環境で使えます。使える型は環境で違うので、`__STDCPP_BFLOAT16_T__` マクロで確かめます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::bfloat16_t` は bfloat16（Google Brain の 16 ビット形式）
    - [x] 使えるかは `__STDCPP_BFLOAT16_T__` マクロで確かめる
    - [x] `float` / `double` とは別の型

## 関連ページ

- [cpprefjp: std::bfloat16_t](https://cpprefjp.github.io/reference/stdfloat/bfloat16_t.html)
- [cppreference: std::bfloat16_t](https://en.cppreference.com/w/cpp/types/floating-point/bfloat16_t)
