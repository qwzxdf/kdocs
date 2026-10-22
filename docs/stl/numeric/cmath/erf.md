---
title: std::erf
summary: "誤差関数（正規分布の積分に関係する関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::erf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

正規分布の累積確率を求めるときに出てくる関数です。`erf(x)` は 0 から x までの積分を使った値で、-1 〜 1 の範囲を取ります。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::erf {#erf}

```cpp
double erf(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `erf(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::erf(1.0));
}
```

```text title="実行結果"
0.8427
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ガチャの確率や正規分布の累積を求める |

## よくあるミス

??? failure "相補誤差関数と取り違える"
    `1 - erf(x)` は `erfc(x)` と等しいですが、x が大きいと `erfc` のほうが精度が高くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`erfc`](erfc.md) | 相補誤差関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 誤差関数（正規分布の積分に関係する関数）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::erf](https://cpprefjp.github.io/reference/cmath/erf.html)
- [cppreference: std::erf](https://en.cppreference.com/w/cpp/numeric/math/erf)
