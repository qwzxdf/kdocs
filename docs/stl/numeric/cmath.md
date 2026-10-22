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
| [`std::fabs`](cmath/fabs.md) | <span class="rank rank-sometimes">たまに</span> | 浮動小数点の絶対値を返す。 |
| [`std::remquo`](cmath/remquo.md) | <span class="rank rank-rare">知ってるだけ</span> | 割り算の余りと、商の下位ビットをいっしょに返す。 <span class="ver ver-11">C++11</span> |
| [`std::fdim`](cmath/fdim.md) | <span class="rank rank-rare">知ってるだけ</span> | x − y が正ならその値、そうでなければ 0 を返す。 <span class="ver ver-11">C++11</span> |
| [`std::nan`](cmath/nan.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字列に対応する NaN（非数）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::asinh`](cmath/asinh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆正弦（sinh の逆関数）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::acosh`](cmath/acosh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆余弦（cosh の逆関数）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::atanh`](cmath/atanh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆正接（tanh の逆関数）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::erf`](cmath/erf.md) | <span class="rank rank-rare">知ってるだけ</span> | 誤差関数（正規分布の積分に関係する関数）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::erfc`](cmath/erfc.md) | <span class="rank rank-rare">知ってるだけ</span> | 相補誤差関数（1 − erf）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::tgamma`](cmath/tgamma.md) | <span class="rank rank-rare">知ってるだけ</span> | ガンマ関数（階乗の一般化）を返す。 <span class="ver ver-11">C++11</span> |
| [`std::lgamma`](cmath/lgamma.md) | <span class="rank rank-rare">知ってるだけ</span> | ガンマ関数の自然対数を返す。 <span class="ver ver-11">C++11</span> |
| [`std::llround`](cmath/llround.md) | <span class="rank rank-rare">知ってるだけ</span> | 四捨五入して long long にする。 <span class="ver ver-11">C++11</span> |
| [`std::rint`](cmath/rint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（結果は小数）。 <span class="ver ver-11">C++11</span> |
| [`std::lrint`](cmath/lrint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（long で返す）。 <span class="ver ver-11">C++11</span> |
| [`std::llrint`](cmath/llrint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（long long で返す）。 <span class="ver ver-11">C++11</span> |
| [`std::scalbn`](cmath/scalbn.md) | <span class="rank rank-rare">知ってるだけ</span> | x × 2ⁿ を、乗算を使わずに計算する。 <span class="ver ver-11">C++11</span> |
| [`std::scalbln`](cmath/scalbln.md) | <span class="rank rank-rare">知ってるだけ</span> | x × 2ⁿ を計算する（指数が long）。 <span class="ver ver-11">C++11</span> |
| [`std::ilogb`](cmath/ilogb.md) | <span class="rank rank-rare">知ってるだけ</span> | x の指数部（2 を底とした対数の整数部分）を int で返す。 <span class="ver ver-11">C++11</span> |
| [`std::logb`](cmath/logb.md) | <span class="rank rank-rare">知ってるだけ</span> | x の指数部を、浮動小数点で返す。 <span class="ver ver-11">C++11</span> |
| [`std::nextafter`](cmath/nextafter.md) | <span class="rank rank-rare">知ってるだけ</span> | x の次に表せる浮動小数点数を返す（y の方向へ）。 <span class="ver ver-11">C++11</span> |
| [`std::nexttoward`](cmath/nexttoward.md) | <span class="rank rank-rare">知ってるだけ</span> | x の次に表せる値を返す（向かう先が long double）。 <span class="ver ver-11">C++11</span> |
| [`std::fpclassify`](cmath/fpclassify.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点数の種類（0・正規数・NaN など）を判定する。 <span class="ver ver-11">C++11</span> |
| [`std::isnormal`](cmath/isnormal.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規数（0・無限大・NaN・非正規数以外）かを判定する。 <span class="ver ver-11">C++11</span> |
| [`std::isgreater`](cmath/isgreater.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より大きいか）。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::isgreaterequal`](cmath/isgreaterequal.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y 以上か）。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::isless`](cmath/isless.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より小さいか）。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::islessequal`](cmath/islessequal.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y 以下か）。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::islessgreater`](cmath/islessgreater.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より小さいか大きいか（等しくも非順序でもない））。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::isunordered`](cmath/isunordered.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（どちらかが NaN で、大小を比べられないか）。NaN でも例外を出さない。 <span class="ver ver-11">C++11</span> |
| [`std::assoc_laguerre`](cmath/assoc_laguerre.md) | <span class="rank rank-rare">知ってるだけ</span> | ラゲール陪多項式を求める。 <span class="ver ver-17">C++17</span> |
| [`std::assoc_legendre`](cmath/assoc_legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | ルジャンドル陪関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::beta`](cmath/beta.md) | <span class="rank rank-rare">知ってるだけ</span> | ベータ関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::comp_ellint_1`](cmath/comp_ellint_1.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::comp_ellint_2`](cmath/comp_ellint_2.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::comp_ellint_3`](cmath/comp_ellint_3.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 3 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::cyl_bessel_i`](cmath/cyl_bessel_i.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種変形ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::cyl_bessel_j`](cmath/cyl_bessel_j.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::cyl_bessel_k`](cmath/cyl_bessel_k.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種変形ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::cyl_neumann`](cmath/cyl_neumann.md) | <span class="rank rank-rare">知ってるだけ</span> | ノイマン関数（第 2 種ベッセル関数）を求める。 <span class="ver ver-17">C++17</span> |
| [`std::ellint_1`](cmath/ellint_1.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::ellint_2`](cmath/ellint_2.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::ellint_3`](cmath/ellint_3.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 3 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::expint`](cmath/expint.md) | <span class="rank rank-rare">知ってるだけ</span> | 指数積分 Ei(x) を求める。 <span class="ver ver-17">C++17</span> |
| [`std::hermite`](cmath/hermite.md) | <span class="rank rank-rare">知ってるだけ</span> | エルミート多項式を求める。 <span class="ver ver-17">C++17</span> |
| [`std::laguerre`](cmath/laguerre.md) | <span class="rank rank-rare">知ってるだけ</span> | ラゲール多項式を求める。 <span class="ver ver-17">C++17</span> |
| [`std::legendre`](cmath/legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | ルジャンドル多項式を求める。 <span class="ver ver-17">C++17</span> |
| [`std::riemann_zeta`](cmath/riemann_zeta.md) | <span class="rank rank-rare">知ってるだけ</span> | リーマンのゼータ関数を求める。 <span class="ver ver-17">C++17</span> |
| [`std::sph_bessel`](cmath/sph_bessel.md) | <span class="rank rank-rare">知ってるだけ</span> | 球ベッセル関数（第 1 種）を求める。 <span class="ver ver-17">C++17</span> |
| [`std::sph_legendre`](cmath/sph_legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | 球面調和関数の θ 部分を求める。 <span class="ver ver-17">C++17</span> |
| [`std::sph_neumann`](cmath/sph_neumann.md) | <span class="rank rank-rare">知ってるだけ</span> | 球ノイマン関数を求める。 <span class="ver ver-17">C++17</span> |
| [`HUGE_VAL`](cmath/huge_val.md) | <span class="rank rank-rare">知ってるだけ</span> | double の無限大を表すマクロ。 |
| [`INFINITY`](cmath/infinity.md) | <span class="rank rank-rare">知ってるだけ</span> | float の無限大を表すマクロ。 |
| [`math_errhandling`](cmath/math_errhandling.md) | <span class="rank rank-rare">知ってるだけ</span> | 数学関数のエラーの知らせ方を表すマクロ。 |
| [`NAN`](cmath/nan_macro.md) | <span class="rank rank-rare">知ってるだけ</span> | float の NaN（非数）を表すマクロ。 |

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
