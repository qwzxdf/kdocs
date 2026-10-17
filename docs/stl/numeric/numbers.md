---
title: <numbers>（数学定数）
tags:
  - 数値
---

# &lt;numbers&gt;（数学定数）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <numbers>`
</div>

`<numbers>` は、**円周率 π やネイピア数 e などの数学の定数**を、正確な値で用意してくれるヘッダです。C++20 より前は `#define PI 3.14159f` のように自分で書いたり、`M_PI`（環境によっては使えない）を使ったりしていましたが、今は `std::numbers::pi` を使えば、どの環境でも同じ正確な値が手に入ります。

!!! tip "ポイント"
    - π は **`std::numbers::pi`<strong>（double）、float なら </strong>`std::numbers::pi_v<float>`**。
    - 度 → ラジアンは `deg * std::numbers::pi_v<float> / 180.0f`。
    - 自分で `#define PI` を書かない。

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

## よくあるミス

??? failure "float の計算に double の pi を使う"
    `std::numbers::pi` は double なので、`float a = deg * std::numbers::pi / 180;` は double で計算されます。float なら `pi_v<float>` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] π は `std::numbers::pi` / `pi_v<float>`
    - [x] `#define PI` は書かない

## 関連ページ

- [<cmath>](cmath.md)
- [cppreference: Mathematical constants](https://en.cppreference.com/w/cpp/numeric/constants)
