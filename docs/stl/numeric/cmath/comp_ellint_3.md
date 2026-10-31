---
title: std::comp_ellint_3
summary: "第 3 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_3

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

第 1 種・第 2 種の楕円積分では表せない問題のために、特性数 `ν` を加えた第 3 種があります。`std::comp_ellint_3` は、その完全積分の値を返します。

!!! tip "ポイント"
    - `std::comp_ellint_3(0.0, 0.0)` は π/2 ≈ 1.5708
    - `|k|` は 1 以下
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `nu = 0` なら第 1 種と同じになる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_3 {#comp_ellint_3}

<span class="ver ver-17">C++17</span>

```cpp
double comp_ellint_3(double k, double nu);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |
| `nu` | `double` | 特性数 |

第 3 種完全楕円積分 Π(ν, k) の値を返します。

`k` は −1 から 1 の範囲の離心率、`nu` は特性数です。第 3 種完全楕円積分は、`nu = 0` のとき、第 1 種 `K(k)` と一致します。`k` と `nu` が両方 0 なら `π/2` です。

`nu` の符号の取り方は、数学のライブラリごとに違うことがあります。他のライブラリの値と比べるときは、定義を確かめます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // nu = 0 のとき、第 1 種完全楕円積分 K(k) と一致する
  for (double k : {0.0, 0.5, 0.9}) {
    std::println("k = {}: Π(k, 0) = {:.4f}, K(k) = {:.4f}", k, std::comp_ellint_3(k, 0.0), std::comp_ellint_1(k));
  }
  std::println("Π(0, 0) = {:.4f}", std::comp_ellint_3(0.0, 0.0));
}
```

```text title="実行結果"
k = 0: Π(k, 0) = 1.5708, K(k) = 1.5708
k = 0.5: Π(k, 0) = 1.6858, K(k) = 1.6858
k = 0.9: Π(k, 0) = 2.2805, K(k) = 2.2805
Π(0, 0) = 1.5708
```

`nu = 0` では、第 3 種が第 1 種と一致します。`k = 0.9` では、`K(k)` が約 2.28 まで増えます。

## ゲームでの使いどころ

振り子や楕円の問題を、さらに一般化した形の積分で出てきます。ゲームの計算で、直接使うことはありません。必要になったら、まず第 1 種・第 2 種で足りないかを確かめてください。

## よくあるミス

??? failure "nu の符号を別のライブラリと同じだと思う"
    定義が違う場合があります。`nu = 0` で一致を確かめるなど、小さな検査をします。

??? failure "k の範囲を超える値を渡す"
    絶対値が 1 以上だと、結果は定まりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_1`](comp_ellint_1.md) | `nu = 0` の場合 |
| [`ellint_3`](ellint_3.md) | 積分範囲を φ までにした版 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::comp_ellint_3` は第 3 種完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::comp_ellint_3](https://cpprefjp.github.io/reference/cmath/comp_ellint_3.html)
- [cppreference: std::comp_ellint_3](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_3)
