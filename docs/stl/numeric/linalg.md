---
title: std::linalg
summary: "行列とベクトルの基本演算を、標準で提供する（C++26）。"
order: 100
tags:
  - 数値
---

# std::linalg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <linalg>`
</div>

ゲームの 3D 計算は、SimpleMath などの専用ライブラリを使うのが普通です。`<linalg>` は、BLAS という数値計算の定番の演算（内積・行列積・転置など）を、`mdspan` の上で標準として使えるようにするものです。ゲームでは、機械学習や物理シミュレーションで大きな行列を扱うときの話になります。

!!! tip "ポイント"
    - `mdspan` を引数に取る関数群。
    - `dot`・`matrix_product`・`scale`・`add` などがある。
    - ゲームの 3D 計算は SimpleMath が主役。
    - C++26 の新機能。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::linalg {#linalg}

```cpp
namespace std::linalg {
  // 例
  template <class InVec1, class InVec2, class T>
  T dot(InVec1 v1, InVec2 v2, T init);
}
```

| 引数 | 意味 |
| --- | --- |
| `v1, v2` | `mdspan` のベクトル |
| `init` | 足し込みの初期値 |

- 各関数が行列・ベクトルの演算結果を返すか、出力の `mdspan` に書き込みます

## 実際に動かしてみる

```cpp
#include <iostream>
#include <linalg>
#include <mdspan>
#include <vector>

int main() {
  std::vector<double> a = {1, 2, 3};
  std::vector<double> b = {4, 5, 6};
  std::mdspan va(a.data(), 3);
  std::mdspan vb(b.data(), 3);
  std::cout << std::linalg::dot(va, vb, 0.0) << "\n";   // 1*4 + 2*5 + 3*6
}
```

```text title="実行結果"
32
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大きな行列の積（機械学習・シミュレーション） | `std::linalg::matrix_product` |

## よくあるミス

??? failure "小さな 3D 行列に使う"
    4x4 行列などの小さな計算では、SimpleMath のほうが手軽で速いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mdspan`](../containers/mdspan.md) | 多次元の見え方 |

## コンパイラ対応

C++26 の機能です。対応する標準ライブラリは、まだ少なめです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] BLAS 相当の演算を標準で提供する。
    - [x] `mdspan` の上で動く。
    - [x] 3D の小さな計算には使わない。

## 関連ページ

- [cpprefjp: std::linalg](https://cpprefjp.github.io/reference/linalg/linalg.html)
- [cppreference: std::linalg](https://en.cppreference.com/w/cpp/numeric/linalg)
