---
title: std::complex
summary: "複素数（実部 + 虚部）。回転・波・フーリエ変換に。"
order: 40
tags:
  - 数値
---

# std::complex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <complex>`
</div>

`std::complex<T>` は、**複素数（実部と虚部を持つ数）**を表すクラスです。`+`、`-`、`*`、`/` がそのまま使え、`std::abs`（大きさ）や `std::arg`（角度）で極座標に直せます。2D の回転を「複素数のかけ算」で表す、フーリエ変換（波形の分析）を作る、といった場面で使います。

!!! tip "ポイント"
    - 2D の回転は `std::polar(1.0, angle)` をかけるだけ。
    - `std::abs(z)` が大きさ、`std::arg(z)` が角度。
    - ゲームの 3D 回転には、複素数を拡張した「クォータニオン」（SimpleMath の `Quaternion`）を使う。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::complex {#complex}

```cpp
template <class T>
class complex {
 public:
  complex(T re = T(), T im = T());
  T real() const;
  T imag() const;
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `re` | T | 実部 | 0 |
| `im` | T | 虚部 | 0 |

- 戻り値: （クラス）。四則演算、`abs`、`arg`、`polar` などが使える
- 計算量: O(1)

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> a(1.0, 2.0);   // 1 + 2i
  std::complex<double> b(3.0, 4.0);   // 3 + 4i

  auto c = a * b;                      // (1+2i)(3+4i) = -5 + 10i
  std::println("{} {}", c.real(), c.imag());
  std::println("{}", std::abs(b));     // |3+4i| = 5
}
```

```text title="実行結果"
-5 10
5
```

## 複素数の関数

| 名前 | 何をする |
| --- | --- |
| [`std::arg`](complex/arg.md) | 複素数の偏角（実軸からの角度）をラジアンで返す。 |
| [`std::conj`](complex/conj.md) | 共役複素数（虚部の符号を反転したもの）を返す。 |
| [`std::imag`](complex/imag.md) | 複素数の虚部を取り出す。 |
| [`std::norm`](complex/norm.md) | 複素数の大きさの 2 乗を返す。 |
| [`std::polar`](complex/polar.md) | 大きさと角度から複素数を作る。 |
| [`std::proj`](complex/proj.md) | 複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）。 |
| [`std::real`](complex/real.md) | 複素数の実部を取り出す。 |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の回転を複素数のかけ算で表す | `pos *= std::polar(1.0f, angle)` |

## よくあるミス

??? failure "3D の回転に使う"
    3D の回転には複素数は足りません。クォータニオンを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hypot`](cmath/hypot.md) | 大きさだけなら |
| [`std::valarray`](../containers/valarray.md) | 数値配列 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複素数
    - [x] 回転は polar のかけ算
    - [x] 3D はクォータニオン

## 関連ページ

- [cpprefjp: std::complex](https://cpprefjp.github.io/reference/complex/complex.html)
- [cppreference: std::complex](https://en.cppreference.com/w/cpp/numeric/complex)
