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

完全版 `comp_ellint_3` の、積分範囲 `phi` を指定できる版です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ellint_3 {#ellint_3}

```cpp
double ellint_3(double k, double nu, double phi);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | 浮動小数点 | 離心率 −1 〜 1 |
| `nu` | 浮動小数点 | 特性数 |
| `phi` | 浮動小数点 | 角度（ラジアン） |

- 戻り値: `Π(nu, k, phi)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::ellint_3(0.0, 0.0, 1.0));
}
```

```text title="実行結果"
1.0000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 物理の計算 |

## よくあるミス

??? failure "完全版と取り違える"
    `phi = π/2` のとき、`comp_ellint_3(k, nu)` と同じ値になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_3`](comp_ellint_3.md) | 完全版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 3 種不完全楕円積分を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ellint_3](https://cpprefjp.github.io/reference/cmath/ellint_3.html)
- [cppreference: std::ellint_3](https://en.cppreference.com/w/cpp/numeric/math/ellint_3)
