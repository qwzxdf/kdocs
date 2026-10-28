---
title: math_errhandling
summary: "数学関数のエラーの知らせ方を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# math_errhandling

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

数学関数が失敗したときの知らせ方は、環境によって 2 通りあります。`errno` に値を設定するか、浮動小数点の例外フラグを立てるか。`math_errhandling` は、<strong>この環境がどちらの方法をとるか</strong>を教えるマクロです。

!!! tip "ポイント"
    - `math_errhandling` は `MATH_ERRNO` と `MATH_ERREXCEPT` のビットの組み合わせ
    - `MATH_ERRNO` が立っていれば `errno` を使う
    - `MATH_ERREXCEPT` が立っていれば `fetestexcept` を使う
    - 少なくとも一方は立っている

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### math_errhandling {#math_errhandling}

<span class="ver ver-11">C++11</span>

```cpp
#define math_errhandling /* int の式 */
#define MATH_ERRNO /* 定数 */
#define MATH_ERREXCEPT /* 定数 */
```

`math_errhandling` は `MATH_ERRNO`（1）と `MATH_ERREXCEPT`（2）のビットの組み合わせで、数学関数がエラーを報告する方法を表します。`MATH_ERRNO` が含まれていれば `errno` に `EDOM`（定義域のエラー）や `ERANGE`（範囲のエラー）が入り、`MATH_ERREXCEPT` が含まれていれば、`FE_INVALID` などの浮動小数点例外のフラグが立ちます。

主要な環境は異なります。GCC（glibc）は両方を持ち、MSVC は `MATH_ERRNO` だけです。移植性のあるコードは、両方に備えて、エラーを `isnan` や `isinf` といった結果の値で確かめるのが簡単です。

`math_errhandling` は、環境が決めるものです。プログラム側から変更はできません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  const bool has_errno = (math_errhandling & MATH_ERRNO) != 0;
  const bool has_except = (math_errhandling & MATH_ERREXCEPT) != 0;
  std::println("少なくとも一方の方法が使える: {}", has_errno || has_except);
}
```

```text title="実行結果"
少なくとも一方の方法が使える: true
```

## ゲームでの使いどころ

ライブラリが数学関数のエラーを報告する方法を環境に合わせて選ぶときに使います。ゲームのコードでは、結果の値（NaN や無限大）で確かめるほうが簡単です。

## よくあるミス

??? failure "`errno` だけを見て、環境によっては何も入っていない"
    結果の値でも確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fetestexcept`](../fetestexcept.md) | 例外フラグを読む |
| [`isnan`](isnan.md) | NaN か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `math_errhandling` は数学関数のエラー報告の方法を表す
    - [x] `MATH_ERRNO` と `MATH_ERREXCEPT` の組み合わせ
    - [x] 結果の値でも確かめるのが簡単

## 関連ページ

- [cpprefjp: math_errhandling](https://cpprefjp.github.io/reference/cmath/math_errhandling.html)
- [cppreference: math_errhandling](https://en.cppreference.com/w/cpp/numeric/math/math_errhandling)
