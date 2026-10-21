---
title: std::tan
summary: "タンジェント（正接）を求める。引数はラジアン。"
order: 5
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::tan

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <cmath>`
</div>

`std::tan` は、**タンジェント（正接）を求める**関数です。`sin / cos` と同じです。視野角（FOV）から射影行列を作るときの `tan(fov / 2)` などで使います。90 度（π/2）付近では値が非常に大きくなります。

!!! tip "ポイント"
    - 射影行列の計算で `tan(fov / 2)`。
    - 90 度付近では巨大な値になる。
    - 傾きから角度を求める逆は `atan` / `atan2`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tan {#tan}

```cpp
float tan(float radians);
```

- タンジェント。カメラの視野角の計算などで使います

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  std::println("{:.1f} {:.1f}", std::tan(0.0), std::tan(std::numbers::pi / 4));
}
```

```text title="実行結果"
0.0 1.0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 視野角から射影行列を作る | `1.0f / std::tan(fov * 0.5f)` |

## よくあるミス

??? failure "90 度付近で使う"
    値が発散します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atan2`](atan2.md) | 逆関数 |
| [`sin`](sin.md) | サイン |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タンジェント
    - [x] 射影行列で使う
    - [x] 90 度付近は発散

## 関連ページ

- [cpprefjp: std::tan](https://cpprefjp.github.io/reference/cmath/tan.html)
- [cppreference: std::tan](https://en.cppreference.com/w/cpp/numeric/math/tan)
