---
title: std::valarray
summary: "要素ごとの計算（足し算、掛け算）を、配列全体にまとめて書ける数値用の配列。"
order: 26
tags:
  - コンテナ
---

# std::valarray

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++98〜</span>
`#include <valarray>`
</div>

`std::valarray` は、**数値の配列に対して、`a + b` や `a * 2` と書くだけで、全要素の計算ができる**配列です。数値計算のために作られましたが、機能が中途半端で、現在はほとんど使われません。ゲームでは、ベクトル型（SimpleMath の `Vector3` など）や SIMD を使います。

!!! tip "ポイント"
    - <strong>知っておくだけでよい。</strong> 3D の計算には、SimpleMath の `Vector3` / `Matrix` を使う。
    - `+` `-` `*` `/` がそのまま全要素に効く。
    - `sum()`、`min()`、`max()` で集計できる。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 宣言

```cpp
template <class T>
class valarray;
```

## 関数の詳しい説明

### 算術演算（+ - * /） {#operators}

```cpp
valarray<T> operator+(const valarray<T>& lhs, const valarray<T>& rhs);
valarray<T> operator*(const valarray<T>& lhs, const T& rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs, rhs` | `valarray<T>` | 同じ長さの 2 つの配列、または配列とスカラー |

- 戻り値: 要素ごとに計算した新しい `valarray`
- 計算量: O(n)

```cpp
#include <print>
#include <valarray>

int main() {
  std::valarray<double> a = {1.0, 2.0, 3.0};
  std::valarray<double> b = {4.0, 5.0, 6.0};

  std::valarray<double> c = a + b;  // 要素ごとの足し算
  std::valarray<double> d = a * 2;  // 全要素を 2 倍
  std::println("{} {} {} / 合計 {}", c[0], c[1], c[2], c.sum());
  std::println("{} {} {}", d[0], d[1], d[2]);
}
```

```text title="実行結果"
5 7 9 / 合計 21
2 4 6
```

### sum, min, max {#sum}

```cpp
T sum() const;
T min() const;
T max() const;
```

- 戻り値: 合計、最小値、最大値
- 計算量: O(n)

### apply {#apply}

```cpp
valarray apply(T func(T)) const;
```

- 計算量: O(要素数)

全要素に関数を適用した、新しい `valarray` を返します。

### shift {#shift}

```cpp
valarray shift(int count) const;
```

- 計算量: O(要素数)

要素を `count` だけずらします。あいた場所は 0 で埋めます（正で左、負で右）。

### cshift {#cshift}

```cpp
valarray cshift(int count) const;
```

- 計算量: O(要素数)

要素を `count` だけ循環させてずらします（あふれた要素が反対側に回る）。

### resize {#resize}

```cpp
void resize(size_t n, T c = T());
```

- 計算量: O(n)

要素数を `n` にします。中身は `c` で埋められます（元の値は失われます）。

### swap {#swap}

```cpp
void swap(valarray& v) noexcept;
```

- 計算量: 定数

2 つの `valarray` を入れ替えます。

### size {#size}

```cpp
size_t size() const;
```

- 計算量: 定数

要素の数。

### operator[] {#op_index}

```cpp
T& operator[](size_t n);
slice_array<T> operator[](slice s);
mask_array<T> operator[](const valarray<bool>& m);
```

- 計算量: 定数

n 番目の要素を返します。`slice`・マスク・添字の配列を渡すと、その部分への参照が返ります。

### operator= {#op_assign}

```cpp
valarray& operator=(const valarray& v);
valarray& operator=(const T& v);
```

- 計算量: O(要素数)

別の `valarray` を代入します。スカラーを代入すると、全要素がその値になります。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パーティクルの数値配列をまとめて計算（ただし、ふつうは SIMD や専用ライブラリ） | `pos += vel * dt` |

## よくあるミス

??? failure "3D の計算に使う"
    ゲームでの 3D ベクトルの計算には向きません。SimpleMath（`Vector3`、`Matrix`）か、DirectXMath を使ってください。

??? failure "長さの違う配列を計算する"
    長さが違う `valarray` 同士の計算は未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::vector`](vector.md) | 汎用の配列。算術演算はない |
| [`<numeric>`](../numeric/numeric.md) | `accumulate` などで集計 |
| [`std::mdspan`](mdspan.md) | 多次元の添字を扱う |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全要素の計算を `a + b` と書ける数値配列
    - [x] ほとんど使われない
    - [x] 3D には SimpleMath

## 関連ページ

- [cpprefjp: std::valarray](https://cpprefjp.github.io/reference/valarray/valarray.html)
- [cppreference: std::valarray](https://en.cppreference.com/w/cpp/numeric/valarray)
