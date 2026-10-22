---
title: std::expint
summary: "指数積分 Ei(x) を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::expint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

指数と逆数が組み合わさった積分の関数です。放射や熱の計算に出てきます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::expint {#expint}

```cpp
double expint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `Ei(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::expint(1.0));
}
```

```text title="実行結果"
1.8951
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 光の減衰の積分 |

## よくあるミス

??? failure "x = 0 を渡す"
    x = 0 では −∞ になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exp`](exp.md) | 指数関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指数積分 Ei(x) を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::expint](https://cpprefjp.github.io/reference/cmath/expint.html)
- [cppreference: std::expint](https://en.cppreference.com/w/cpp/numeric/math/expint)
