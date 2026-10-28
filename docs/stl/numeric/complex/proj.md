---
title: std::proj
summary: "複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）。"
order: 900
tags:
  - 数値
---

# std::proj

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数には、実部か虚部のどちらかが無限大の値が含まれることがあります。数学的には、無限大の点は「リーマン球面」上の 1 点にまとめられます。`std::proj` は、複素数をこの<strong>無限遠点を 1 通りの表現にそろえる</strong>関数です。

!!! tip "ポイント"
    - `std::proj(z)` は、有限の値はそのまま返す
    - 無限大を含む値は `(inf, ±0)` に統一される
    - 普通のゲームのコードでは使わない
    - 数値計算ライブラリの実装で使われる

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::proj {#proj}

```cpp
template <class T>
complex<T> proj(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

`z` の実部か虚部のどちらかが無限大なら、`(+inf, ±0)` の形の無限遠点を返します。虚部の符号は、元の虚部の符号に従います。それ以外（有限の値）は、`z` をそのまま返します。

無限大を含む複素数は、実部と虚部の組み合わせがいくつもあり、同じ無限遠点として扱うべき値が別々の表現になります。`proj` はそれを 1 通りにそろえて、比較などを簡単にします。

数値計算ライブラリの内部で使う関数で、ゲームのコードで直接呼ぶ場面はまずありません。

## 実際に動かしてみる

```cpp
#include <complex>
#include <limits>
#include <print>

int main() {
  const double inf = std::numeric_limits<double>::infinity();
  const std::complex<double> finite{3.0, 4.0};
  std::println("有限の値はそのまま: {}", std::proj(finite) == finite);

  const auto p = std::proj(std::complex<double>{inf, 5.0});
  std::println("無限遠点の虚部 = {}", p.imag());
}
```

```text title="実行結果"
有限の値はそのまま: true
無限遠点の虚部 = 0
```

## ゲームでの使いどころ

複素数の無限大を比較しやすい形にそろえます。ゲームのコードでは使う場面がありません。

## よくあるミス

??? failure "有限の値に変化を期待する"
    有限の値はそのまま返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`norm`](norm.md) | 絶対値の 2 乗 |
| [`isinf`](../cmath/isinf.md) | 実数が無限大か |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `proj(z)` は無限遠点を 1 通りの表現にそろえる
    - [x] 有限の値はそのまま返る
    - [x] ゲームではほぼ使わない

## 関連ページ

- [cpprefjp: std::proj](https://cpprefjp.github.io/reference/complex/proj.html)
- [cppreference: std::proj](https://en.cppreference.com/w/cpp/numeric/complex/proj)
