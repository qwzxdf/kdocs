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

円を描く、角度をラジアンに変換する、自然対数を使う。数学の計算では、π や e といった定数が必要です。以前は、`#define PI 3.14159f` と自分で書いたり、環境によって使えない `M_PI` に頼ったりしていました。C++20 の `<numbers>` は、π、e、√2 などの数学定数を、正確な値で用意しています。どの環境でも、同じ値が手に入ります。

!!! tip "ポイント"
    - π は **`std::numbers::pi`<strong>（double）、float なら </strong>`std::numbers::pi_v<float>`**。
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
| [`inv_sqrtpi`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 0.56418… | 1/√π |
| [`inv_sqrt3`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 0.57735… | 1/√3 |
| [`ln2`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 0.69314… | log(2) |
| [`ln10`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 2.30258… | log(10) |
| [`log2e`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 1.44269… | log₂(e) |
| [`log10e`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 0.43429… | log₁₀(e) |
| [`egamma`](#others) | <span class="rank rank-rare">知ってるだけ</span> | 0.57721… | オイラーの定数 |

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

### pi {#pi}

```cpp
template <class T> inline constexpr T pi_v = /* π */;
inline constexpr double pi = pi_v<double>;
```

- 円周率。角度の変換、円の計算、三角関数の周期（2π）に使います

### sqrt2 {#sqrt2}

```cpp
template <class T> inline constexpr T sqrt2_v = /* √2 */;
inline constexpr double sqrt2 = sqrt2_v<double>;
```

- √2。斜め入力のとき、縦と横を両方押すと速さが √2 倍になるのを補正するのに使えます

```cpp
#include <numbers>
#include <print>

int main() {
  float speed = 100.0f;
  float diagonal = speed / std::numbers::sqrt2_v<float>;  // 斜めでも同じ速さに
  std::println("{:.1f}", diagonal);
}
```

```text title="実行結果"
70.7
```

### inv_pi {#inv_pi}

```cpp
inline constexpr double inv_pi = /* 1/π */;
```

- 1/π。割り算を掛け算にしたいときに使います

### e {#e}

```cpp
inline constexpr double e = /* 2.71828... */;
```

- ネイピア数。指数関数の底です（`std::exp(1.0)` と同じ値）

### phi {#phi}

```cpp
inline constexpr double phi = /* 1.61803... */;
```

- 黄金比。点を均等にばらまく（ゴールデンアングル）などに使えます

### sqrt3 {#sqrt3}

```cpp
inline constexpr double sqrt3 = /* 1.73205... */;
```

- √3。六角形のマス（ヘックス）の座標計算でよく出てきます

### その他の定数 {#others}

`inv_sqrtpi`、`inv_sqrt3`、`ln2`、`ln10`、`log2e`、`log10e`、`egamma` は、数学・統計の計算で使う定数です。ゲームではほぼ使いません。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.5f} {:.5f} {:.5f}", std::numbers::e, std::numbers::phi, std::numbers::sqrt3);
}
```

```text title="実行結果"
2.71828 1.61803 1.73205
```

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

### std::numbers::log2e <span class="ver ver-20">C++20</span> {#log2e data-toc-label="std::numbers::log2e"}

```cpp
template <class T> inline constexpr T log2e_v = /* log₂(e)（自然対数の底 e の、2 を底とした対数） */;
inline constexpr double log2e = log2e_v<double>;
```

- 戻り値: log₂(e)（自然対数の底 e の、2 を底とした対数）（約 1.442695）
- 計算量: コンパイル時

log₂(e)（自然対数の底 e の、2 を底とした対数）の定数です。`float` 用は `std::numbers::log2e_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::log2e);
}
```

```text title="実行結果"
1.442695
```

### std::numbers::log10e <span class="ver ver-20">C++20</span> {#log10e data-toc-label="std::numbers::log10e"}

```cpp
template <class T> inline constexpr T log10e_v = /* log₁₀(e)（e の常用対数） */;
inline constexpr double log10e = log10e_v<double>;
```

- 戻り値: log₁₀(e)（e の常用対数）（約 0.434294）
- 計算量: コンパイル時

log₁₀(e)（e の常用対数）の定数です。`float` 用は `std::numbers::log10e_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::log10e);
}
```

```text title="実行結果"
0.434294
```

### std::numbers::inv_sqrtpi <span class="ver ver-20">C++20</span> {#inv_sqrtpi data-toc-label="std::numbers::inv_sqrtpi"}

```cpp
template <class T> inline constexpr T inv_sqrtpi_v = /* 1/√π */;
inline constexpr double inv_sqrtpi = inv_sqrtpi_v<double>;
```

- 戻り値: 1/√π（約 0.564189）
- 計算量: コンパイル時

1/√πの定数です。`float` 用は `std::numbers::inv_sqrtpi_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::inv_sqrtpi);
}
```

```text title="実行結果"
0.564190
```

### std::numbers::ln2 <span class="ver ver-20">C++20</span> {#ln2 data-toc-label="std::numbers::ln2"}

```cpp
template <class T> inline constexpr T ln2_v = /* ln(2)（2 の自然対数） */;
inline constexpr double ln2 = ln2_v<double>;
```

- 戻り値: ln(2)（2 の自然対数）（約 0.693147）
- 計算量: コンパイル時

ln(2)（2 の自然対数）の定数です。`float` 用は `std::numbers::ln2_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::ln2);
}
```

```text title="実行結果"
0.693147
```

### std::numbers::ln10 <span class="ver ver-20">C++20</span> {#ln10 data-toc-label="std::numbers::ln10"}

```cpp
template <class T> inline constexpr T ln10_v = /* ln(10)（10 の自然対数） */;
inline constexpr double ln10 = ln10_v<double>;
```

- 戻り値: ln(10)（10 の自然対数）（約 2.302585）
- 計算量: コンパイル時

ln(10)（10 の自然対数）の定数です。`float` 用は `std::numbers::ln10_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::ln10);
}
```

```text title="実行結果"
2.302585
```

### std::numbers::inv_sqrt3 <span class="ver ver-20">C++20</span> {#inv_sqrt3 data-toc-label="std::numbers::inv_sqrt3"}

```cpp
template <class T> inline constexpr T inv_sqrt3_v = /* 1/√3 */;
inline constexpr double inv_sqrt3 = inv_sqrt3_v<double>;
```

- 戻り値: 1/√3（約 0.577350）
- 計算量: コンパイル時

1/√3の定数です。`float` 用は `std::numbers::inv_sqrt3_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::inv_sqrt3);
}
```

```text title="実行結果"
0.577350
```

### std::numbers::egamma <span class="ver ver-20">C++20</span> {#egamma data-toc-label="std::numbers::egamma"}

```cpp
template <class T> inline constexpr T egamma_v = /* オイラー・マスケローニ定数 γ */;
inline constexpr double egamma = egamma_v<double>;
```

- 戻り値: オイラー・マスケローニ定数 γ（約 0.577215）
- 計算量: コンパイル時

オイラー・マスケローニ定数 γの定数です。`float` 用は `std::numbers::egamma_v<float>` です。

```cpp
#include <numbers>
#include <print>

int main() {
  std::println("{:.6f}", std::numbers::egamma);
}
```

```text title="実行結果"
0.577216
```

## ゲームでの使いどころ

角度の変換が、いちばん多い使い方です。度からラジアンへは `deg * std::numbers::pi_v<float> / 180.0f`、ラジアンから度へは `rad * 180.0f / std::numbers::pi_v<float>` と書きます。何度も使うので、`kDegToRad` のような定数や小さな関数にしておくと便利です。

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
