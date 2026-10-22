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

3D の描画で、カメラの視野角（FOV）から射影行列を作るとき、`tan(fov / 2)` の逆数が出てきます。タンジェントは「斜辺ではなく、底辺に対する高さの比」で、角度から傾きを求める関数です。ゲームの 3D 計算では、射影行列のほかに、ゲーム画面の座標から視線の方向を計算するときにも使います。

!!! tip "ポイント"
    - 射影行列の計算で `tan(fov / 2)` が出てくる。
    - 90 度（π/2）の近くでは、値が非常に大きくなる。90 度ちょうどは使わない。
    - 傾きから角度を求めるなら、逆関数の `atan` か `atan2` を使う。

!!! info "このページを読む前に"
    角度の単位（度とラジアン）が分かると読みやすいです。度は `度 × π / 180` でラジアンになります。

## 関数の詳しい説明

### std::tan {#tan}

```cpp
float tan(float radians);
```

`x` はラジアンです。`tan(0)` が 0、`tan(π/4)` が 1 です。`tan(π/2)` は理論上は無限大ですが、`π/2` を浮動小数点で正確に表せないので、実際には約 `1.6e16` のような巨大な有限の値が返ります。この値が後続の計算に使われると、画面が壊れたような表示になることがあります。

`tan(x)` は `sin(x) / cos(x)` と同じです。`cos` が 0 に近いほど値が大きくなります。

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

射影行列を自分で作るとき、`float f = 1.0f / std::tan(fov * 0.5f);` と書いて、`f` を行列の要素に入れます。視野角が広いほど `tan` が大きくなり、`f` が小さくなって、画面に映る範囲が広がります。DirectX Tool Kit の `Matrix::CreatePerspectiveFieldOfView` を使うなら、内部で同じ計算をしてくれるので、直接呼ぶ必要はありません。

斜面の傾きから登れるかを判断するときも使います。傾きの角度 `a` に対して、`tan(a)` が高さ÷水平距離になります。

## よくあるミス

??? failure "度の値を渡す"
    `std::tan(45.0f)` は 45 ラジアンのタンジェントです。ラジアンに変換してから渡します。

??? failure "90 度付近の値をそのまま使う"
    FOV が 180 度に近い値になると、`tan(fov / 2)` が巨大になり、行列がつぶれて何も映らなくなります。FOV は 120 度程度までにします。

??? failure "`tan` の逆を `1 / tan` で求める"
    角度を求めたいなら `atan` です。`1 / tan(x)` は余接（コタンジェント）で、角度ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sin`](sin.md) | 高さの成分 |
| [`cos`](cos.md) | 底辺の成分 |
| [`atan2`](atan2.md) | x と y の値から角度を求める。傾きから角度を出すときの定番 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `tan(x) = sin(x) / cos(x)`。
    - [x] 90 度付近は巨大な値になる。
    - [x] 射影行列の `tan(fov / 2)` で使う。

## 関連ページ

- [cpprefjp: std::tan](https://cpprefjp.github.io/reference/cmath/tan.html)
- [cppreference: std::tan](https://en.cppreference.com/w/cpp/numeric/math/tan)
