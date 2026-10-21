---
title: std::isnan
summary: "値が NaN（数ではない）かを調べる。"
order: 23
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isnan

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::isnan` は、**値が NaN（Not a Number：数として扱えない値）か**を調べる関数です。0 で割ったり、負の平方根を取ったりすると NaN が生まれます。NaN は自分自身とも等しくないので、`x == x` では正しく判定できず、この関数を使います。

!!! tip "ポイント"
    - NaN は伝染する。1 つ混ざると、計算結果が全部 NaN になる。
    - デバッグで `assert(!std::isnan(v))` を入れると原因を見つけやすい。
    - NaN は `==` で比べられない。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isnan {#isnan}

```cpp
bool isnan(float x);
```

- NaN（Not a Number：0/0 や sqrt(-1) の結果）か。NaN は自分自身とも等しくないので `x == x` が false になります

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::isnan(std::nan("")), std::isnan(1.0));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 座標・速度の NaN をデバッグで検出する | `assert(!std::isnan(pos.x))` |

## よくあるミス

??? failure "x == NaN で調べる"
    常に false です。`isnan` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isinf`](isinf.md) | 無限大か |
| [`isfinite`](isfinite.md) | 有限の数か |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] NaN かを調べる
    - [x] `==` では調べられない
    - [x] デバッグで検出する

## 関連ページ

- [cpprefjp: std::isnan](https://cpprefjp.github.io/reference/cmath/isnan.html)
- [cppreference: std::isnan](https://en.cppreference.com/w/cpp/numeric/math/isnan)
