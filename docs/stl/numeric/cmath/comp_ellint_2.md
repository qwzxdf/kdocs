---
title: std::comp_ellint_2
summary: "第 2 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

楕円の周の長さの計算に登場する関数です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_2 {#comp_ellint_2}

```cpp
double comp_ellint_2(double k);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | 浮動小数点 | 離心率 −1 〜 1 |

- 戻り値: `E(k)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::comp_ellint_2(0.0));
}
```

```text title="実行結果"
1.5708
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 楕円の周の長さ |

## よくあるミス

??? failure "範囲外を渡す"
    |k| > 1 では定義されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_1`](comp_ellint_1.md) | 第 1 種 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 2 種完全楕円積分を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::comp_ellint_2](https://cpprefjp.github.io/reference/cmath/comp_ellint_2.html)
- [cppreference: std::comp_ellint_2](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_2)
