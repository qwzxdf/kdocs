---
title: <cmath>（数学関数）
summary: "`sqrt`、`sin` / `cos`、`atan2`、`lerp` など数学の関数。"
order: 70
tags:
  - 数値
---

# &lt;cmath&gt;（数学関数）

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
`#include <cmath>`
</div>

`<cmath>` は、**平方根、三角関数、累乗、丸めなどの数学の関数**をまとめたヘッダです。ゲームでは、距離の計算（`sqrt`）、向きから角度を出す（`atan2`）、角度から向きを出す（`sin` / `cos`）、なめらかな補間（`lerp`）など、毎日のように使います。引数が `float` なら `float` 版、`double` なら `double` 版が呼ばれます。

!!! tip "ポイント"
    - 距離は `std::sqrt(dx * dx + dy * dy)` か `std::hypot(dx, dy)`。**比べるだけなら 2 乗のまま**（sqrt は重い）。
    - 向き → 角度は **`std::atan2(y, x)`**（`atan` ではない）。角度は**ラジアン**。
    - 角度 → 向きは `{std::cos(a), std::sin(a)}`。
    - 補間は `std::lerp(a, b, t)`、範囲に収めるのは [`std::clamp`](../algorithms/clamp.md)。
    - float で計算するなら、引数も `1.0f` のように float にそろえる（`2.0` だと double で計算される）。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::sqrt`](cmath/sqrt.md) | <span class="rank rank-must">必須</span> | 平方根 |
| [`std::abs`](cmath/abs.md) | <span class="rank rank-must">必須</span> | 絶対値 |
| [`std::sin`](cmath/sin.md) | <span class="rank rank-must">必須</span> | サイン |
| [`std::cos`](cmath/cos.md) | <span class="rank rank-must">必須</span> | コサイン |
| [`std::atan2`](cmath/atan2.md) | <span class="rank rank-must">必須</span> | (x, y) の向きの角度 |
| [`std::floor`](cmath/floor.md) | <span class="rank rank-often">よく使う</span> | 切り捨て（小さいほうの整数） |
| [`std::round`](cmath/round.md) | <span class="rank rank-often">よく使う</span> | 四捨五入 |
| [`std::lerp`](cmath/lerp.md) | <span class="rank rank-often">よく使う</span> | 線形補間 <span class="ver ver-20">C++20</span> |
| [`std::pow`](cmath/pow.md) | <span class="rank rank-often">よく使う</span> | 累乗 |
| [`std::hypot`](cmath/hypot.md) | <span class="rank rank-often">よく使う</span> | ベクトルの長さ |
| [`std::ceil`](cmath/ceil.md) | <span class="rank rank-often">よく使う</span> | 切り上げ |
| [`std::fmod`](cmath/fmod.md) | <span class="rank rank-often">よく使う</span> | 小数の割り算の余り |
| [`std::trunc`](cmath/trunc.md) | <span class="rank rank-sometimes">たまに</span> | 0 の方向へ切り捨て |
| [`std::tan`](cmath/tan.md) | <span class="rank rank-sometimes">たまに</span> | タンジェント |
| [`std::asin`](cmath/asin.md) | <span class="rank rank-sometimes">たまに</span> | アークサイン |
| [`std::acos`](cmath/acos.md) | <span class="rank rank-sometimes">たまに</span> | アークコサイン（内積から角度） |
| [`std::exp`](cmath/exp.md) | <span class="rank rank-sometimes">たまに</span> | e の累乗 |
| [`std::log`](cmath/log.md) | <span class="rank rank-sometimes">たまに</span> | 自然対数 |
| [`std::isnan`](cmath/isnan.md) | <span class="rank rank-sometimes">たまに</span> | NaN（壊れた数）か |
| [`std::isinf`](cmath/isinf.md) | <span class="rank rank-rare">知ってるだけ</span> | 無限大か |
| [`std::copysign`](cmath/copysign.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号だけ別の値から取る |
| [`std::log2`](cmath/log2.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 を底とする対数 |
| [`std::log10`](cmath/log10.md) | <span class="rank rank-rare">知ってるだけ</span> | 10 を底とする対数 |
| [`std::cbrt`](cmath/cbrt.md) | <span class="rank rank-rare">知ってるだけ</span> | 立方根 |
| [`std::fma`](cmath/fma.md) | <span class="rank rank-rare">知ってるだけ</span> | `a * b + c` を誤差少なく |

## よくある使い方

### 1. 距離と向き

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  float px = 0.0f, py = 0.0f;  // プレイヤー
  float ex = 3.0f, ey = 4.0f;  // 敵

  float dx = ex - px;
  float dy = ey - py;
  float distance = std::sqrt(dx * dx + dy * dy);
  float angle = std::atan2(dy, dx);  // ラジアン
  float degrees = angle * 180.0f / std::numbers::pi_v<float>;

  std::println("距離 {} / 角度 {:.1f} 度", distance, degrees);
}
```

```text title="実行結果"
距離 5 / 角度 53.1 度
```

### 2. 角度の方向へ動かす

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  float angle = std::numbers::pi_v<float> / 2.0f;  // 90 度（真上）
  float speed = 10.0f;
  float vx = std::cos(angle) * speed;
  float vy = std::sin(angle) * speed;
  std::println("({:.1f}, {:.1f})", vx, vy);
}
```

```text title="実行結果"
(-0.0, 10.0)
```

`-0.0` は、計算誤差でほんの少しマイナスになった値（`-0.0000004` など）を小数 1 桁で表示したものです。

## フラグ・オプション

フラグはありません。定数（π など）は [`<numbers>`](numbers.md) にあります。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    #define PI 3.14159265f
    float t2 = a + (b - a) * t;
    float d = sqrtf(dx * dx + dy * dy);  // C の関数（float 版は f が付く）
    ```

=== "今の書き方"

    ```cpp
    float pi = std::numbers::pi_v<float>;
    float t2 = std::lerp(a, b, t);
    float d = std::hypot(dx, dy);
    ```

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 距離・当たり判定 | `sqrt`、`hypot`（比べるだけなら 2 乗） |
| 向いている角度 | `atan2` |
| 角度の方向へ移動・弾を撃つ | `cos`、`sin` |
| カメラ・UI のなめらかな追従 | `lerp` |
| 座標 → マス番号 | `floor` |
| ふわふわ揺れる | `sin(time)` |
| ループアニメーション | `fmod` |
| 減衰・慣性 | `exp` |

## よくあるミス

??? failure "度とラジアンを混ぜる"
    `std::sin(90.0f)` は 90 ラジアンのサインです。度なら `90.0f * std::numbers::pi_v<float> / 180.0f` に変換します。

??? failure "atan2 の引数の順番"
    `atan2(y, x)` です。`atan2(x, y)` にすると角度がずれます。

??? failure "float と double を混ぜて遅くなる・警告が出る"
    `std::sqrt(x * 2.0)` は double で計算されます。float のゲームなら `2.0f` と書きます。

??? failure "マイナスの座標で int にキャストしてマスを出す"
    `static_cast<int>(-0.5f)` は 0 です。マス番号には `std::floor` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<numbers>`](numbers.md) | π などの定数 |
| [`<numeric>`](numeric.md) | 最大公約数、合計など |
| [`std::clamp`](../algorithms/clamp.md) | 範囲に収める |
| GLM / DirectXMath（外部） | ベクトル・行列の計算 |

## コンパイラ対応

ほとんどが C++98 / C++11 からある関数です。`std::lerp` は C++20、3 引数の `std::hypot` は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離は sqrt / hypot、比べるだけなら 2 乗
    - [x] 角度は atan2(y, x)、向きは cos / sin。単位はラジアン
    - [x] 補間は lerp、マス番号は floor
    - [x] float なら定数も `f` 付きで

## 関連ページ

- [<numbers>](numbers.md)
- [cpprefjp: <cmath>](https://cpprefjp.github.io/reference/cmath.html)
- [cppreference: Common mathematical functions](https://en.cppreference.com/w/cpp/numeric/math)
