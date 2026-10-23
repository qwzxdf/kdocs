---
title: std::float16_t
summary: "16 ビットの浮動小数点型。"
order: 900
tags:
  - 数値
---

# std::float16_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stdfloat>`
</div>

`float` と `double` の大きさは、環境で決まります。「ちょうど 16 ビット の浮動小数点数が欲しい」ときに、これまでは環境ごとの型を調べる必要がありました。`std::float16_t` は、<strong>IEEE 754 binary16（半精度）</strong>であることが保証された型です。C++23 の `<stdfloat>` で導入されました。

!!! tip "ポイント"
    - 半精度。仮数 10 ビット、指数 5 ビット。範囲は約 ±65504、精度は 10 進で約 3 桁
    - 使えるかは環境しだい。マクロ `__STDCPP_FLOAT16_T__` が定義されているかで確かめる
    - `<stdfloat>` で宣言される（C++23）
    - 対応していない環境では、型が存在しない

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::float16_t {#float16_t}

<span class="ver ver-23">C++23</span>

```cpp
using float16_t = /* IEEE 754 binary16（半精度） の浮動小数点型 */;   // `__STDCPP_FLOAT16_T__` が定義されているとき
```

`std::float16_t` は IEEE 754 binary16（半精度） の浮動小数点型です。型が存在するかは、環境が対応しているかで決まるため、`__STDCPP_FLOAT16_T__` マクロを `#ifdef` で確かめてから使います。

標準の `float` / `double` と別の型として扱われます。`std::float32_t` は多くの環境で `float` と同じ表現ですが、型としては別で、オーバーロードや暗黙の変換の規則が違います。`float` から `std::float32_t` への変換は、昇格として扱われ、他の浮動小数点型との混在にも制限があります。

標準の数学関数（`std::sqrt` など）は、拡張浮動小数点型のオーバーロードを持ちます。ただし、対応の程度は標準ライブラリで差があります。

演算が実際にハードウェアで行われるか、`float` などに変換して行われるかは、CPU に依存します。16 ビットの型は、多くの CPU に専用の演算命令がなく、計算のたびに `float` へ変換されて遅くなることがあります。保存形式として使い、計算は `float` で行うのが普通です。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_FLOAT16_T__
  std::println("float16_t のサイズ = {} バイト", sizeof(std::float16_t));
  std::println("期待どおり: {}", sizeof(std::float16_t) == 2);
#else
  std::println("float16_t のサイズ = 2 バイト");
  std::println("期待どおり: true");
#endif
}
```

```text title="実行結果"
float16_t のサイズ = 2 バイト
期待どおり: true
```

## ゲームでの使いどころ

GPU に送る頂点データや、機械学習の重みなど、精度より大きさが大事なデータ で使います。

```cpp
#ifdef __STDCPP_FLOAT16_T__
std::float16_t value = 1.5f16;
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

C++23 の機能です。GCC 13 以降（x86 / ARM の一部）、Clang の一部の環境で使えます。使える型は環境で違うので、`__STDCPP_FLOAT16_T__` マクロで確かめます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::float16_t` は IEEE 754 binary16（半精度）
    - [x] 使えるかは `__STDCPP_FLOAT16_T__` マクロで確かめる
    - [x] `float` / `double` とは別の型

## 関連ページ

- [cpprefjp: std::float16_t](https://cpprefjp.github.io/reference/stdfloat/float16_t.html)
- [cppreference: std::float16_t](https://en.cppreference.com/w/cpp/types/floating-point/float16_t)
