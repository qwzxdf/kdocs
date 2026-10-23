---
title: std::fdim
summary: "x − y が正ならその値、そうでなければ 0 を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fdim

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

「体力から受けたダメージを引く。ただし 0 未満にはしない」。ゲームではよく書く処理です。`std::max(0.0, a - b)` と書くところですが、`std::fdim` は、まさにその意味の関数です。

!!! tip "ポイント"
    - `std::fdim(5.0, 3.0)` は 2、`std::fdim(3.0, 5.0)` は 0
    - `max(x - y, 0)` と同じ意味
    - 引き算の結果を 0 以上に切り上げる
    - `fabs` のような「差の絶対値」ではない

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fdim {#fdim}

<span class="ver ver-11">C++11</span>

```cpp
float fdim(float x, float y);
double fdim(double x, double y);
long double fdim(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 引かれる数 |
| `y` | 浮動小数点数 | 引く数 |

戻り値は、`x` が `y` より大きければ `x - y`、そうでなければ 0 です（正の差）。`max(x - y, 0)` と同じです。

差の絶対値（`fabs(x - y)`）ではありません。`fdim(3.0, 5.0)` は 0 で、2 にはなりません。名前から「距離」を連想して取り違えやすい点に注意します。

片方が NaN なら NaN を返します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("fdim(5, 3) = {}", std::fdim(5.0, 3.0));
  std::println("fdim(3, 5) = {}", std::fdim(3.0, 5.0));   // 負にならず 0
  // 体力 30 にダメージ 50: 0 で止まる
  std::println("残り体力 = {}", std::fdim(30.0, 50.0));
}
```

```text title="実行結果"
fdim(5, 3) = 2
fdim(3, 5) = 0
残り体力 = 0
```

## ゲームでの使いどころ

体力、弾薬、所持金のように、0 を下回ってはいけない値の減算に使えます。

```cpp
health = std::fdim(health, damage);   // 0 未満にならない
```

`std::max(0.0f, health - damage)` と書いても同じです。意図が読み取りやすいほうを選びます。

## よくあるミス

??? failure "「差の絶対値」だと思って使う"
    `fdim` は正の差のみ。絶対値の差は `fabs(x - y)`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fabs`](fabs.md) | 絶対値 |
| [`fmax`](fmax.md) | 大きいほうを返す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fdim(x, y)` は `max(x - y, 0)`
    - [x] 差の絶対値ではない
    - [x] 0 未満にしたくない減算に

## 関連ページ

- [`std::fmax`](fmax.md)
- [cpprefjp: std::fdim](https://cpprefjp.github.io/reference/cmath/fdim.html)
- [cppreference: std::fdim](https://en.cppreference.com/w/cpp/numeric/math/fdim)
