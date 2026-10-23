---
title: std::polar
summary: "大きさと角度から複素数を作る。"
order: 900
tags:
  - 数値
---

# std::polar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

2D の方向と長さから位置を作りたい。極座標（長さと角度）から、直交座標（x と y）への変換です。複素数では、`std::polar` が、<strong>大きさと偏角から複素数を作ります</strong>。

!!! tip "ポイント"
    - `std::polar(r, theta)` は大きさ `r`、偏角 `theta` の複素数
    - 実部は `r * cos(theta)`、虚部は `r * sin(theta)`
    - `theta` はラジアン
    - 大きさ 1 の `polar(1, theta)` は、角度 `theta` の回転を表す

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::polar {#polar}

```cpp
template <class T>
complex<T> polar(const T& rho, const T& theta = T());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rho` | `T` | 大きさ（絶対値）。0 以上 |
| `theta` | `T` | 偏角（ラジアン）。既定は 0 |

戻り値は、大きさ `rho`、偏角 `theta` の複素数です。実部が `rho * cos(theta)`、虚部が `rho * sin(theta)` になります。

`rho` が負、または NaN の場合の動作は決まっていません（C++ 20 以前の規格では未定義）。大きさは 0 以上にします。

大きさ 1 の `polar(1, θ)` は、2D の角度 θ の回転を表します。他の複素数に掛けると、その点を θ だけ回転できます。行列を作らずに回転が書けるので、2D の簡単な処理で便利です。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  const auto z = std::polar(2.0, 0.0);              // 大きさ 2、偏角 0
  std::println("real = {}, imag = {}", z.real(), z.imag());

  // 点 (1, 0) を 90 度回転する
  const auto rotation = std::polar(1.0, 1.5707963267948966);
  const auto p = std::complex<double>{1.0, 0.0} * rotation;
  std::println("回転後: ({:.1f}, {:.1f})", p.real(), p.imag());
}
```

```text title="実行結果"
real = 2, imag = 0
回転後: (0.0, 1.0)
```

## ゲームでの使いどころ

2D の向きと速さから、速度ベクトルを作ります。

```cpp
// 向き angle、速さ speed の速度
const std::complex<float> velocity = std::polar(speed, angle);
```

## よくあるミス

??? failure "度で渡す"
    ラジアンで渡します。

??? failure "負の大きさを渡す"
    大きさは 0 以上にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`arg`](arg.md) | 偏角を取り出す |
| [`norm`](norm.md) | 絶対値の 2 乗 |
| [`conj`](conj.md) | 共役複素数 |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `polar(r, theta)` は大きさと偏角から複素数を作る
    - [x] 偏角はラジアン
    - [x] 大きさ 1 の複素数は回転を表す

## 関連ページ

- [cpprefjp: std::polar](https://cpprefjp.github.io/reference/complex/polar.html)
- [cppreference: std::polar](https://en.cppreference.com/w/cpp/numeric/complex/polar)
