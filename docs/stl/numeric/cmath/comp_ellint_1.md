---
title: std::comp_ellint_1
summary: "第 1 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_1

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

振り子の周期など、楕円の積分に登場する関数です。引数 k の範囲は −1 〜 1 です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_1 {#comp_ellint_1}

```cpp
double comp_ellint_1(double k);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | 浮動小数点 | 離心率 −1 〜 1 |

- 戻り値: `K(k)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::comp_ellint_1(0.0));
}
```

```text title="実行結果"
1.5708
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 振り子の周期の計算 |

## よくあるミス

??? failure "範囲外を渡す"
    |k| > 1 では定義されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_2`](comp_ellint_2.md) | 第 2 種 |
| [`ellint_1`](ellint_1.md) | 不完全版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 1 種完全楕円積分を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::comp_ellint_1](https://cpprefjp.github.io/reference/cmath/comp_ellint_1.html)
- [cppreference: std::comp_ellint_1](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_1)
