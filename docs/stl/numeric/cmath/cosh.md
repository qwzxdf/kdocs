---
title: std::cosh
summary: "双曲線余弦（cosh）を求める。"
order: 31
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cosh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

吊り橋のケーブルや電線のように、両端をつるして自然に垂れ下がる曲線は、放物線ではなく懸垂線（カテナリー）です。その式は `a * cosh(x / a)` で、`std::cosh` はこの双曲線余弦を計算します。

!!! tip "ポイント"
    - `std::cosh(0.0)` は 1、`std::cosh(1.0)` は約 1.5431
    - 偶関数: `cosh(-x) = cosh(x)`。常に 1 以上
    - `x` が大きいと急激に増え、オーバーフローする
    - 懸垂線を描くときに使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cosh {#cosh}

```cpp
float cosh(float x);
double cosh(double x);
long double cosh(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力 |

戻り値は `(exp(x) + exp(-x)) / 2` です。`x` が 0 のとき最小値 1 で、そこから左右対称に増えます。戻り値が 1 未満になることはありません。

`cos` とは似て非なる関数で、周期を持たず、指数的に増えます。`cosh(x)^2 - sinh(x)^2 = 1` という関係があり、これが双曲線関数の名前の由来です。

`double` では `x` の絶対値が約 710 を超えると、無限大を返します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("cosh(0)  = {}", std::cosh(0.0));
  std::println("cosh(1)  = {}", std::cosh(1.0));
  std::println("cosh(-1) = {}", std::cosh(-1.0));    // 偶関数なので cosh(1) と同じ
}
```

```text title="実行結果"
cosh(0)  = 1
cosh(1)  = 1.5430806348152437
cosh(-1) = 1.5430806348152437
```

## ゲームでの使いどころ

つり橋のケーブルを描く場合、両端を結ぶ曲線の高さを `a * cosh(x / a)` で計算します。`a` が大きいほど張りが強く、小さいほど深く垂れます。

```cpp
// x = 0 を最下点とする、懸垂線の高さ
const float y = a * std::cosh(x / a) - a;
```

## よくあるミス

??? failure "`cos` の代わりに使って、振動しないことに驚く"
    `cosh` は周期関数ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sinh`](sinh.md) | 双曲線正弦 |
| [`tanh`](tanh.md) | 双曲線正接 |
| [`cos`](cos.md) | 三角関数の余弦 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cosh(x)` は `(exp(x) + exp(-x)) / 2`
    - [x] 偶関数で、最小値は `cosh(0) = 1`
    - [x] 懸垂線を描くときに使う

## 関連ページ

- [`std::sinh`](sinh.md)
- [cpprefjp: std::cosh](https://cpprefjp.github.io/reference/cmath/cosh.html)
- [cppreference: std::cosh](https://en.cppreference.com/w/cpp/numeric/math/cosh)
