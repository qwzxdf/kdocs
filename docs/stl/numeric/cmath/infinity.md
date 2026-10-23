---
title: INFINITY
summary: "float の無限大を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# INFINITY

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

無限大の値を書きたい。式の中で `1.0 / 0.0` と書くのは、見た目がよくありません。`INFINITY` は、<strong>`float` の正の無限大</strong>を表すマクロです。

!!! tip "ポイント"
    - `INFINITY` は `float` の正の無限大
    - 負の無限大は `-INFINITY`
    - どんな有限の値よりも大きい
    - `double` の無限大が欲しいなら `std::numeric_limits<double>::infinity()`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### INFINITY {#infinity}

<span class="ver ver-11">C++11</span>

```cpp
#define INFINITY /* float の定数式 */
```

`INFINITY` は、`float` 型の正の無限大を表す定数式です。浮動小数点が無限大を持たない環境では、コンパイル時にエラーになります（そのような環境はまれです）。

比較の初期値として、「見つかった中の最小値」を探すときに使うと便利です。最小値を探す変数を `INFINITY` で初期化すると、最初の比較で必ず更新されます。

型を明示したいときは、`std::numeric_limits<float>::infinity()` のように書けます。`double` で使うなら、`INFINITY` は `double` に変換されますが、型を揃えたほうが意図が明確です。

## 実際に動かしてみる

```cpp
#include <cfloat>
#include <cmath>
#include <print>

int main() {
  std::println("INFINITY は FLT_MAX より大きい: {}", INFINITY > FLT_MAX);
  std::println("-INFINITY は負: {}", -INFINITY < 0.0f);
}
```

```text title="実行結果"
INFINITY は FLT_MAX より大きい: true
-INFINITY は負: true
```

## ゲームでの使いどころ

最近接の敵を探す処理で、距離の初期値に使います。

```cpp
float nearest = INFINITY;                      // どんな距離よりも大きい
for (const auto& e : enemies) {
  nearest = std::min(nearest, Distance(player, e));
}
```

## よくあるミス

??? failure "`FLT_MAX` と取り違える"
    `FLT_MAX` は有限の最大値、`INFINITY` は無限大です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`NAN`](nan_macro.md) | 非数を表すマクロ |
| [`HUGE_VAL`](huge_val.md) | オーバーフローの戻り値 |
| [`isinf`](isinf.md) | 無限大か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `INFINITY` は `float` の正の無限大
    - [x] 最小値探索の初期値に便利
    - [x] `double` なら `numeric_limits<double>::infinity()`

## 関連ページ

- [cpprefjp: INFINITY](https://cpprefjp.github.io/reference/cmath/infinity.html)
- [cppreference: INFINITY](https://en.cppreference.com/w/cpp/numeric/math/INFINITY)
