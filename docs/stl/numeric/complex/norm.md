---
title: std::norm
summary: "複素数の大きさの 2 乗を返す。"
order: 900
tags:
  - 数値
---

# std::norm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数の大きさ（絶対値）を求めるには、2 乗和の平方根が要ります。平方根は計算が重く、大きさを比べたいだけなら要らないことが多いです。`std::norm` は、<strong>平方根を取らない、絶対値の 2 乗</strong>を返します。

!!! tip "ポイント"
    - `std::norm(z)` は実部² + 虚部²
    - `abs(z)` の 2 乗と同じだが、平方根を取らないので速い
    - 大きさを比べるだけなら `norm` で足りる
    - 名前に反して「ノルム」そのもの（√ あり）ではない

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::norm {#norm}

```cpp
template <class T>
constexpr T norm(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

戻り値は `z` の実部と虚部の 2 乗の和です。`norm(3 + 4i)` は 25 で、`abs` は 5 です。

名前は紛らわしく、数学用語の「ノルム」（大きさそのもの）ではなく、<strong>その 2 乗</strong>を返す点に注意します。大きさそのものが欲しいなら `std::abs(z)` です。

距離の比較（近いか遠いか）には `norm` を使えば、平方根の計算を避けられます。2D の位置を複素数で持つ場合、2 点の差の `norm` を距離の 2 乗として扱えます。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  const std::complex<double> z{3.0, 4.0};
  std::println("norm(z) = {}", std::norm(z));   // 3*3 + 4*4
  std::println("abs(z)  = {}", std::abs(z));    // √25
}
```

```text title="実行結果"
norm(z) = 25
abs(z)  = 5
```

## ゲームでの使いどころ

2 点の距離の 2 乗を求めて、射程内かを判定します。

```cpp
const std::complex<float> diff = enemy - player;
const bool in_range = std::norm(diff) <= range * range;   // 平方根なしで比べる
```

## よくあるミス

??? failure "`norm` を大きさそのものと思う"
    `norm` は 2 乗です。大きさは `std::abs`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conj`](conj.md) | 共役複素数 |
| [`arg`](arg.md) | 偏角 |
| [`hypot`](../cmath/hypot.md) | 実数で長さを求める |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `norm(z)` は絶対値の 2 乗（平方根なし）
    - [x] 大きさそのものは `abs`
    - [x] 距離の比較に使える

## 関連ページ

- [cpprefjp: std::norm](https://cpprefjp.github.io/reference/complex/norm.html)
- [cppreference: std::norm](https://en.cppreference.com/w/cpp/numeric/complex/norm)
