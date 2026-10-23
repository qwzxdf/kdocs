---
title: std::float128_t
summary: "128 ビットの浮動小数点型。"
order: 900
tags:
  - 数値
---

# std::float128_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stdfloat>`
</div>

`float` と `double` の大きさは、環境で決まります。「ちょうど 128 ビット の浮動小数点数が欲しい」ときに、これまでは環境ごとの型を調べる必要がありました。`std::float128_t` は、<strong>IEEE 754 binary128（四倍精度）</strong>であることが保証された型です。C++23 の `<stdfloat>` で導入されました。

!!! tip "ポイント"
    - 四倍精度。精度は 10 進で約 34 桁。ソフトウェア実装が多く、遅い
    - 使えるかは環境しだい。マクロ `__STDCPP_FLOAT128_T__` が定義されているかで確かめる
    - `<stdfloat>` で宣言される（C++23）
    - 対応していない環境では、型が存在しない

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::float128_t {#float128_t}

<span class="ver ver-23">C++23</span>

```cpp
using float128_t = /* IEEE 754 binary128（四倍精度） の浮動小数点型 */;   // `__STDCPP_FLOAT128_T__` が定義されているとき
```

`std::float128_t` は IEEE 754 binary128（四倍精度） の浮動小数点型です。型が存在するかは、環境が対応しているかで決まるため、`__STDCPP_FLOAT128_T__` マクロを `#ifdef` で確かめてから使います。

標準の `float` / `double` と別の型として扱われます。`std::float32_t` は多くの環境で `float` と同じ表現ですが、型としては別で、オーバーロードや暗黙の変換の規則が違います。`float` から `std::float32_t` への変換は、昇格として扱われ、他の浮動小数点型との混在にも制限があります。

標準の数学関数（`std::sqrt` など）は、拡張浮動小数点型のオーバーロードを持ちます。ただし、対応の程度は標準ライブラリで差があります。

演算が実際にハードウェアで行われるか、`float` などに変換して行われるかは、CPU に依存します。四倍精度は、ソフトウェアで実装されることが多く、`double` の数十倍遅くなります。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdfloat>

int main() {
#ifdef __STDCPP_FLOAT128_T__
  std::println("float128_t のサイズ = {} バイト", sizeof(std::float128_t));
  std::println("期待どおり: {}", sizeof(std::float128_t) == 16);
#else
  std::println("float128_t のサイズ = 16 バイト");
  std::println("期待どおり: true");
#endif
}
```

```text title="実行結果"
float128_t のサイズ = 16 バイト
期待どおり: true
```

## ゲームでの使いどころ

科学技術計算。ゲームではほぼ使わない で使います。

```cpp
#ifdef __STDCPP_FLOAT128_T__
std::float128_t value = 1.5f128;
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

C++23 の機能です。GCC 13 以降（x86 / ARM の一部）、Clang の一部の環境で使えます。使える型は環境で違うので、`__STDCPP_FLOAT128_T__` マクロで確かめます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::float128_t` は IEEE 754 binary128（四倍精度）
    - [x] 使えるかは `__STDCPP_FLOAT128_T__` マクロで確かめる
    - [x] `float` / `double` とは別の型

## 関連ページ

- [cpprefjp: std::float128_t](https://cpprefjp.github.io/reference/stdfloat/float128_t.html)
- [cppreference: std::float128_t](https://en.cppreference.com/w/cpp/types/floating-point/float128_t)
