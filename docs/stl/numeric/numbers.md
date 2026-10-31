---
title: <numbers>（数学定数）
summary: "π などの数学の定数。"
order: 73
tags:
  - 数値
---

# &lt;numbers&gt;（数学定数）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <numbers>`
</div>

円を描く、角度をラジアンに変換する、自然対数を使う。数学の計算では、π や e といった定数が必要です。以前は、`#define PI 3.14159f` と自分で書いたり、環境によって使えない `M_PI` に頼ったりしていました。C++20 の `<numbers>` は、π、e、√2 などの数学定数を正確な値で用意しています。どの環境でも、同じ値が手に入ります。

!!! tip "ポイント"
    - π は `std::numbers::pi`(`double`)。`float` なら `std::numbers::pi_v<float>`。
    - 度 → ラジアンは `deg * std::numbers::pi_v<float> / 180.0f`。
    - 自分で `#define PI` を書かない。

!!! info "このページを読む前に"
    三角関数で使う角度の単位（度とラジアン）が分かると読みやすいです。度は `度 × π / 180` でラジアンになります。

## 定数一覧

よく使う順です。それぞれ `名前` が double 版、`名前_v<float>` のように型を指定する版があります。

| 定数 | 重要度 | 値 | 意味 |
| --- | --- | --- | --- |
| [`pi`](#pi) | <span class="rank rank-must">必須</span> | 3.14159… | 円周率 π |
| [`sqrt2`](#sqrt2) | <span class="rank rank-sometimes">たまに</span> | 1.41421… | √2（斜め移動の補正など） |
| [`inv_pi`](#inv_pi) | <span class="rank rank-rare">知ってるだけ</span> | 0.31830… | 1/π |
| [`e`](#e) | <span class="rank rank-rare">知ってるだけ</span> | 2.71828… | ネイピア数 |
| [`phi`](#phi) | <span class="rank rank-rare">知ってるだけ</span> | 1.61803… | 黄金比 |
| [`sqrt3`](#sqrt3) | <span class="rank rank-rare">知ってるだけ</span> | 1.73205… | √3（正三角形・六角形のマス） |
| [`inv_sqrtpi`](#inv_sqrtpi) | <span class="rank rank-rare">知ってるだけ</span> | 0.56418… | 1/√π |
| [`inv_sqrt3`](#inv_sqrt3) | <span class="rank rank-rare">知ってるだけ</span> | 0.57735… | 1/√3 |
| [`ln2`](#ln2) | <span class="rank rank-rare">知ってるだけ</span> | 0.69314… | log(2) |
| [`ln10`](#ln10) | <span class="rank rank-rare">知ってるだけ</span> | 2.30258… | log(10) |
| [`log2e`](#log2e) | <span class="rank rank-rare">知ってるだけ</span> | 1.44269… | log₂(e) |
| [`log10e`](#log10e) | <span class="rank rank-rare">知ってるだけ</span> | 0.43429… | log₁₀(e) |
| [`egamma`](#egamma) | <span class="rank rank-rare">知ってるだけ</span> | 0.57721… | オイラーの定数 |

## よくある使い方

```cpp
#include <cmath>
#include <numbers>
#include <print>

constexpr float kPi = std::numbers::pi_v<float>;

constexpr float ToRadians(float degrees) { return degrees * kPi / 180.0f; }
constexpr float ToDegrees(float radians) { return radians * 180.0f / kPi; }

int main() {
  std::println("{:.4f}", ToRadians(180.0f));
  std::println("{:.1f}", ToDegrees(std::atan2(1.0f, 1.0f)));

  float radius = 2.0f;
  std::println("円の面積 {:.2f}", kPi * radius * radius);
}
```

```text title="実行結果"
3.1416
45.0
円の面積 12.57
```

## 定数の詳しい説明

どの定数にも、`double` 版(`std::numbers::pi`)と、型を指定する変数テンプレート版(`std::numbers::pi_v<float>`)があります。`_v<T>` の `T` に使えるのは浮動小数点数の型だけで、整数の型を渡すとコンパイルエラーです。値はコンパイル時の定数(`constexpr`)なので、定数式の中や `static_assert` でも使えます。

### pi {#pi}

```cpp
template <class T> inline constexpr T pi_v = /* π */;
inline constexpr double pi = pi_v<double>;
```

円周率 π(3.14159…)です。ラジアンと度の変換、円周と面積の計算、三角関数の周期(2π)など、使う場面がいちばん多い定数です。

`float` の計算なら `pi_v<float>`、`double` の計算なら `pi` を使います。`float` の式に `double` の `pi` を混ぜると、式全体が `double` になり、`float` へ代入するたびに警告が出ます。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  double r = 3.0;
  std::println("円周: {:.4f}", 2 * kPi * r);        // 2πr
  std::println("面積: {:.4f}", kPi * r * r);        // πr²
  std::println("90 度は {:.4f} ラジアン", 90.0 * kPi / 180.0);
  std::println("sin(π/6) = {:.4f}", std::sin(kPi / 6));   // 30 度
}
```

```text title="実行結果"
円周: 18.8496
面積: 28.2743
90 度は 1.5708 ラジアン
sin(π/6) = 0.5000
```

`2 * kPi * r` が円周、`kPi * r * r` が面積です。三角関数に角度を渡すときは、度ではなくラジアンに直します(`度 × π / 180`)。

### sqrt2 {#sqrt2}

```cpp
template <class T> inline constexpr T sqrt2_v = /* √2 */;
inline constexpr double sqrt2 = sqrt2_v<double>;
```

√2(1.41421…)です。1 辺が 1 の正方形の対角線の長さです。

ゲームでよく出てくるのは、斜め移動の補正です。キーボードで「右」と「上」を同時に押すと、入力は `(1, 1)` で、その長さは √2 です。そのまま速さを掛けると、斜めに進むときだけ約 1.41 倍速くなります。`√2` で割ると、どの向きでも同じ速さになります。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  float speed = 100.0f;
  // 斜めの入力 (1, 1) の長さは √2。そのまま掛けると、斜めだけ速くなる
  float wrong_x = speed * 1.0f;
  float wrong_y = speed * 1.0f;
  std::println("補正なし: 長さ {:.1f}", std::sqrt(wrong_x * wrong_x + wrong_y * wrong_y));

  // √2 で割ると、斜めでも同じ速さ
  float fixed_x = wrong_x / std::numbers::sqrt2_v<float>;
  float fixed_y = wrong_y / std::numbers::sqrt2_v<float>;
  std::println("補正あり: 長さ {:.1f} (各軸 {:.1f})", std::sqrt(fixed_x * fixed_x + fixed_y * fixed_y), fixed_x);
}
```

```text title="実行結果"
補正なし: 長さ 141.4
補正あり: 長さ 100.0 (各軸 70.7)
```

補正なしだと、速さ 100 のつもりが約 141 になります。補正ありなら、各軸は約 70.7 になり、合成した長さが 100 に戻ります。入力が (1, 0) か (0, 1) のときは補正が要らないので、実際には、入力ベクトルの長さで割る(正規化する)書き方のほうが一般的です。

### inv_pi {#inv_pi}

```cpp
template <class T> inline constexpr T inv_pi_v = /* 1/π */;
inline constexpr double inv_pi = inv_pi_v<double>;
```

1/π(0.31830…)です。`x / pi` と書く代わりに `x * inv_pi` と書くと、割り算を掛け算にできます。ふつうは、コンパイラが定数の割り算を掛け算に直してくれるので、速さのためというより、式の見通しをよくするために使います。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  double area = 100.0;
  // 面積から半径: r = √(A / π)。割り算の代わりに、1/π を掛ける
  double radius = std::sqrt(area * std::numbers::inv_pi);
  std::println("面積 100 の円の半径: {:.3f}", radius);
}
```

```text title="実行結果"
面積 100 の円の半径: 5.642
```

円の面積 `A` から半径を求める式 `r = √(A / π)` は、`√(A × inv_pi)` と書けます。

### e {#e}

```cpp
template <class T> inline constexpr T e_v = /* e */;
inline constexpr double e = e_v<double>;
```

ネイピア数 e(2.71828…)で、自然対数の底です。`std::exp(1.0)` と同じ値です。

数式で e を単独で使うことは多くなく、減衰や成長の式 `exp(-k * t)` のように、`std::exp` を通して使います。`std::pow(std::numbers::e, x)` は `std::exp(x)` より遅く、精度も劣るので、使いません。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // exp(1) は e そのもの
  std::println("exp(1) と e の差が小さい: {}", std::abs(std::exp(1.0) - std::numbers::e) < 1e-15);

  // 時間とともに減る値: value = exp(-k * t)。t = 1/k のとき、1/e (約 37%) に減る
  double k = 0.5;
  double t = 1.0 / k;
  std::println("1/k 秒後の残り: {:.4f} (1/e = {:.4f})", std::exp(-k * t), 1.0 / std::numbers::e);
}
```

```text title="実行結果"
exp(1) と e の差が小さい: true
1/k 秒後の残り: 0.3679 (1/e = 0.3679)
```

`exp(-k * t)` は、時間 `t` とともに指数関数で減る値です。`t = 1/k` のとき、ちょうど `1/e`(約 36.8%)まで減ります。

### phi {#phi}

```cpp
template <class T> inline constexpr T phi_v = /* 黄金比 */;
inline constexpr double phi = phi_v<double>;
```

黄金比 φ(1.61803…)で、`(1 + √5) / 2` です。

ゲームでは、点を均等にばらまくための「黄金角」に使います。円を黄金比で分けた角度(約 137.5 度)ごとに点を 1 つずつ置くと、ひまわりの種のように、隙間も重なりもない並びになります。木や草の配置を、規則正しすぎず、偏らないように散らしたいときに便利です。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  // 黄金角: 円を黄金比で分けた角度。約 137.5 度
  double golden_angle = 2 * kPi * (1.0 - 1.0 / std::numbers::phi);
  std::println("黄金角: {:.3f} ラジアン = {:.3f} 度", golden_angle, golden_angle * 180.0 / kPi);

  // 黄金角ごとに 1 つずつ点を置くと、隙間なく均等に広がる(ひまわりの種の並び)
  for (int i = 1; i <= 3; ++i) {
    double radius = std::sqrt(static_cast<double>(i));
    double angle = i * golden_angle;
    std::println("{} 個目: ({:.3f}, {:.3f})", i, radius * std::cos(angle), radius * std::sin(angle));
  }
}
```

```text title="実行結果"
黄金角: 2.400 ラジアン = 137.508 度
1 個目: (-0.737, 0.675)
2 個目: (0.124, -1.409)
3 個目: (1.054, 1.375)
```

`i` 個目の点を、半径 `√i`、角度 `i × 黄金角` に置くのが、この並びの作り方です。

### sqrt3 {#sqrt3}

```cpp
template <class T> inline constexpr T sqrt3_v = /* √3 */;
inline constexpr double sqrt3 = sqrt3_v<double>;
```

√3(1.73205…)です。1 辺が 2 の正三角形の高さです。

六角形のマス(ヘックス)を並べるときに必ず出てきます。頂点が上を向く六角形は、幅が `√3 × 大きさ`、隣の段へは `1.5 × 大きさ` ずつ下がります。

```cpp
#include <numbers>
#include <print>
#include <utility>

int main() {
  // 頂点が上を向くヘックス(六角形のマス)の中心を、軸座標 (q, r) から求める
  constexpr double kSize = 10.0;   // 中心から頂点までの長さ
  constexpr double kSqrt3 = std::numbers::sqrt3;
  for (auto [q, r] : {std::pair{0, 0}, std::pair{1, 0}, std::pair{0, 1}, std::pair{1, 1}}) {
    double x = kSize * (kSqrt3 * q + kSqrt3 / 2 * r);
    double y = kSize * (1.5 * r);
    std::println("({}, {}) -> ({:.1f}, {:.1f})", q, r, x, y);
  }
}
```

```text title="実行結果"
(0, 0) -> (0.0, 0.0)
(1, 0) -> (17.3, 0.0)
(0, 1) -> (8.7, 15.0)
(1, 1) -> (26.0, 15.0)
```

軸座標 `(q, r)` のマスの中心は、`x = 大きさ × (√3 × q + √3/2 × r)`、`y = 大きさ × 1.5 × r` です。`r` が 1 増えるごとに、`x` が `√3/2` ずつ右にずれるのは、六角形の段が互い違いに並ぶためです。

### inv_sqrtpi {#inv_sqrtpi data-toc-label="std::numbers::inv_sqrtpi"}

```cpp
template <class T> inline constexpr T inv_sqrtpi_v = /* 1/√π */;
```

1/√π(0.56418…)です。正規分布(ガウス分布)の山の高さや、誤差関数 `erf` の係数に現れます。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 標準正規分布(平均 0、標準偏差 1)の山の高さ = 1/√(2π) = (1/√π) / √2
  double peak = std::numbers::inv_sqrtpi / std::numbers::sqrt2;
  std::println("山の高さ: {:.5f}", peak);
  std::println("定義どおりに計算: {:.5f}", 1.0 / std::sqrt(2 * std::numbers::pi));
}
```

```text title="実行結果"
山の高さ: 0.39894
定義どおりに計算: 0.39894
```

標準正規分布の山の高さ `1/√(2π)` を、`inv_sqrtpi / sqrt2` で作れます。ゲームでは、ガウスぼかしの重みの計算で使うぐらいです。

### inv_sqrt3 {#inv_sqrt3 data-toc-label="std::numbers::inv_sqrt3"}

```cpp
template <class T> inline constexpr T inv_sqrt3_v = /* 1/√3 */;
```

1/√3(0.57735…)です。`tan(30°)` と同じ値で、3D の `(1, 1, 1)` 方向の単位ベクトルの 1 成分でもあります。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 3D で (1, 1, 1) の向きの単位ベクトルは、各成分が 1/√3
  std::println("各成分: {:.5f}", std::numbers::inv_sqrt3);

  // 1/√3 = tan(30 度)
  double tan30 = std::tan(std::numbers::pi / 6);
  std::println("tan(30 度) との差が小さい: {}", std::abs(tan30 - std::numbers::inv_sqrt3) < 1e-12);
}
```

```text title="実行結果"
各成分: 0.57735
tan(30 度) との差が小さい: true
```

立方体の対角線の向き `(1, 1, 1)` を正規化すると、各成分が `1/√3` になります。

### ln2 {#ln2 data-toc-label="std::numbers::ln2"}

```cpp
template <class T> inline constexpr T ln2_v = /* log(2) */;
```

2 の自然対数 `ln 2`(0.69314…)です。指数関数で減る値の**半減期**の計算に使います。`exp(-k × t)` が半分になる時間は `ln2 / k` です。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // exp(-k * t) で減る値の半減期は ln2 / k
  double k = 0.5;
  double half_life = std::numbers::ln2 / k;
  std::println("半減期: {:.4f} 秒", half_life);
  std::println("その時間後の残り: {:.4f}", std::exp(-k * half_life));
}
```

```text title="実行結果"
半減期: 1.3863 秒
その時間後の残り: 0.5000
```

体力が自然に回復する速さ、エフェクトが消えていく速さなどを、「何秒で半分になるか」で指定したいとき、`k = ln2 / 半減期` で、内部の係数に直せます。

### ln10 {#ln10 data-toc-label="std::numbers::ln10"}

```cpp
template <class T> inline constexpr T ln10_v = /* log(10) */;
```

10 の自然対数 `ln 10`(2.30258…)です。自然対数から常用対数への換算に使います。`log10(x) = log(x) / ln10` です。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 自然対数 log から、常用対数 log10 を求める: log10(x) = log(x) / ln10
  double x = 100.0;
  std::println("log(100) / ln10 = {:.6f}", std::log(x) / std::numbers::ln10);
  std::println("log10(100) = {:.6f}", std::log10(x));
}
```

```text title="実行結果"
log(100) / ln10 = 2.000000
log10(100) = 2.000000
```

`std::log10` が使えるなら、それを使えば足ります。底の変換の式を自分で書くときに必要になる定数です。

### log2e {#log2e data-toc-label="std::numbers::log2e"}

```cpp
template <class T> inline constexpr T log2e_v = /* log2(e) */;
```

`log₂(e)`(1.44269…)です。自然対数の底 e を、2 を底にした対数で表したものです。`exp(x) = exp2(x × log2e)` のように、底を 2 に直して計算するときに使います。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // exp(x) = exp2(x * log2e): 底を 2 に直して計算する
  double x = 1.0;
  std::println("exp2(1 * log2e) = {:.5f}", std::exp2(x * std::numbers::log2e));
  std::println("exp(1) = {:.5f}", std::exp(x));
}
```

```text title="実行結果"
exp2(1 * log2e) = 2.71828
exp(1) = 2.71828
```

2 を底にした計算は、2 進数のコンピューターで速く済むことがあります。

### log10e {#log10e data-toc-label="std::numbers::log10e"}

```cpp
template <class T> inline constexpr T log10e_v = /* log10(e) */;
```

`log₁₀(e)`(0.43429…)です。`ln10` の逆数で、自然対数の値に掛けると、常用対数になります。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 音量(振幅)を dB に直す: dB = 20 * log10(振幅)。自然対数 log と log10e でも書ける
  double amplitude = 0.5;
  double db = 20.0 * std::log(amplitude) * std::numbers::log10e;
  std::println("振幅 0.5 は {:.2f} dB", db);
}
```

```text title="実行結果"
振幅 0.5 は -6.02 dB
```

音量(振幅)をデシベルに直す式 `20 × log10(振幅)` を、自然対数 `log` と `log10e` で書き直した例です。

### egamma {#egamma data-toc-label="std::numbers::egamma"}

```cpp
template <class T> inline constexpr T egamma_v = /* オイラーの定数 */;
```

オイラー・マスケロニ定数 γ(0.57721…)です。調和数 `1 + 1/2 + … + 1/n` が、大きな `n` で `ln(n) + γ` にほぼ等しくなる、という関係に出てきます。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 調和数 H(n) = 1 + 1/2 + ... + 1/n は、大きな n で ln(n) + γ にほぼ等しい
  int n = 1000;
  double h = 0.0;
  for (int k = 1; k <= n; ++k) h += 1.0 / k;
  std::println("H(1000) = {:.4f}", h);
  std::println("ln(1000) + γ = {:.4f}", std::log(static_cast<double>(n)) + std::numbers::egamma);
}
```

```text title="実行結果"
H(1000) = 7.4855
ln(1000) + γ = 7.4850
```

ゲームの計算では、ほとんど使いません。確率や乱数の期待値を解析する計算で出てくる定数です。

## フラグ・オプション

フラグはありません。型を指定するときは `_v<float>`、`_v<double>` のように書きます。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    #define PI 3.14159f            // 桁が足りない・人によって値が違う
    #define _USE_MATH_DEFINES      // MSVC で M_PI を使うための呪文
    #include <cmath>
    double x = M_PI;
    ```

=== "今の書き方（C++20）"

    ```cpp
    #include <numbers>
    float x = std::numbers::pi_v<float>;
    ```

## ゲームでの使いどころ

角度の変換がいちばん多い使い方です。度からラジアンへは `deg * std::numbers::pi_v<float> / 180.0f`、ラジアンから度へは `rad * 180.0f / std::numbers::pi_v<float>` と書きます。何度も使うので、`kDegToRad` のような定数や小さな関数にしておくと便利です。

円周上の点を求める、回転の角度を決める、ふわふわの周期を決める、といった場面では、`2 * pi` が登場します。ゲームでは `float` で計算することが多いので、`pi_v<float>` を使います。`std::numbers::pi` は `double` です。

e は、減衰や成長の計算（`exp(-k * t)`）で、直接は書かず、`exp` 関数を通して使います。

## よくあるミス

??? failure "`float` の計算に `double` の `pi` を混ぜる"
    `std::numbers::pi` は `double` です。`float` の変数と掛けると、計算が `double` になり、代入のたびに精度が落ちる警告が出ます。`float` の計算には `pi_v<float>` を使います。

??? failure "度のまま三角関数に渡す"
    `std::sin(90.0f)` は、90 度ではなく 90 ラジアンです。`pi` を使って、ラジアンに変換してから渡します。

??? failure "`M_PI` を使ってコンパイルエラーになる"
    `M_PI` は標準ではなく、Visual Studio では `#define _USE_MATH_DEFINES` が必要です。`std::numbers::pi` は標準で、どの環境でも同じように使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] π は `std::numbers::pi`（double）、`float` なら `pi_v<float>`。
    - [x] 度からラジアンは `度 × π / 180`。
    - [x] 自分で `#define PI` を書かない。

## 関連ページ

- [<cmath>](cmath.md)
- [cppreference: Mathematical constants](https://en.cppreference.com/w/cpp/numeric/constants)
