---
title: std::ellint_3
summary: "第 3 種不完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ellint_3

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

特性数 `ν` を持つ第 3 種の楕円積分を、途中の角度 `φ` までの範囲で求めるのが `std::ellint_3` です。

!!! tip "ポイント"
    - `std::ellint_3(0.0, 0.0, 1.0)` は 1
    - `phi` はラジアン
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `nu = 0` なら第 1 種と同じになる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ellint_3 {#ellint_3}

<span class="ver ver-17">C++17</span>

```cpp
double ellint_3(double k, double nu, double phi);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |
| `nu` | `double` | 特性数 |
| `phi` | `double` | 振幅（ラジアン） |

第 3 種不完全楕円積分 Π(k, ν, φ) の値を返します。

`k` は離心率、`nu` は特性数、`phi` は振幅（ラジアン）です。`nu = 0` のとき、第 1 種 `F(k, φ)` と一致します。`k` も `nu` も 0 なら `φ` です。

`nu` の符号の定義は、ライブラリによって違う場合があります。他のライブラリの値と比べるときは、`nu = 0` での一致などを確かめます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double k = 0.5;
  // nu = 0 では、第 1 種 F(k, φ) と同じ
  for (double phi : {0.5, 1.0, 1.5}) {
    std::println("φ = {}: Π(k, 0, φ) = {:.4f}, F(k, φ) = {:.4f}", phi, std::ellint_3(k, 0.0, phi), std::ellint_1(k, phi));
  }
  std::println("Π(0, 0, 1) = {}", std::ellint_3(0.0, 0.0, 1.0));
}
```

```text title="実行結果"
φ = 0.5: Π(k, 0, φ) = 0.5051, F(k, φ) = 0.5051
φ = 1: Π(k, 0, φ) = 1.0374, F(k, φ) = 1.0374
φ = 1.5: Π(k, 0, φ) = 1.6040, F(k, φ) = 1.6040
Π(0, 0, 1) = 1
```

`nu = 0` では、第 1 種と同じ値になります。`k = 0` かつ `nu = 0` では、`φ` そのものです。

## ゲームでの使いどころ

楕円積分を一般化した計算で出てきます。ゲームの計算で使うことはほとんどありません。

## よくあるミス

??? failure "nu の符号を別のライブラリと同じだと思う"
    定義が違う場合があります。`nu = 0` での一致などで確かめます。

??? failure "引数の並びを間違える"
    `k`、`nu`、`phi` の順です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ellint_1`](ellint_1.md) | `nu = 0` の場合 |
| [`comp_ellint_3`](comp_ellint_3.md) | `φ = π/2` の完全積分 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ellint_3` は第 3 種不完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::ellint_3](https://cpprefjp.github.io/reference/cmath/ellint_3.html)
- [cppreference: std::ellint_3](https://en.cppreference.com/w/cpp/numeric/math/ellint_3)
