---
title: <cmath>（数学関数）
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
| [`std::sqrt`](#sqrt) | <span class="rank rank-must">必須</span> | 平方根 |
| [`std::abs`](#abs) | <span class="rank rank-must">必須</span> | 絶対値 |
| [`std::sin`](#sin) | <span class="rank rank-must">必須</span> | サイン |
| [`std::cos`](#cos) | <span class="rank rank-must">必須</span> | コサイン |
| [`std::atan2`](#atan2) | <span class="rank rank-must">必須</span> | (x, y) の向きの角度 |
| [`std::floor`](#floor) | <span class="rank rank-often">よく使う</span> | 切り捨て（小さいほうの整数） |
| [`std::round`](#round) | <span class="rank rank-often">よく使う</span> | 四捨五入 |
| [`std::lerp`](#lerp) | <span class="rank rank-often">よく使う</span> | 線形補間 <span class="ver ver-20">C++20</span> |
| [`std::pow`](#pow) | <span class="rank rank-often">よく使う</span> | 累乗 |
| [`std::hypot`](#hypot) | <span class="rank rank-often">よく使う</span> | ベクトルの長さ |
| [`std::ceil`](#ceil) | <span class="rank rank-often">よく使う</span> | 切り上げ |
| [`std::fmod`](#fmod) | <span class="rank rank-often">よく使う</span> | 小数の割り算の余り |
| [`std::trunc`](#trunc) | <span class="rank rank-sometimes">たまに</span> | 0 の方向へ切り捨て |
| [`std::tan`](#tan) | <span class="rank rank-sometimes">たまに</span> | タンジェント |
| [`std::asin`](#asin) | <span class="rank rank-sometimes">たまに</span> | アークサイン |
| [`std::acos`](#acos) | <span class="rank rank-sometimes">たまに</span> | アークコサイン（内積から角度） |
| [`std::exp`](#exp) | <span class="rank rank-sometimes">たまに</span> | e の累乗 |
| [`std::log`](#log) | <span class="rank rank-sometimes">たまに</span> | 自然対数 |
| [`std::isnan`](#isnan) | <span class="rank rank-sometimes">たまに</span> | NaN（壊れた数）か |
| [`std::isinf`](#isinf) | <span class="rank rank-rare">知ってるだけ</span> | 無限大か |
| [`std::copysign`](#copysign) | <span class="rank rank-rare">知ってるだけ</span> | 符号だけ別の値から取る |
| [`std::log2`](#log2) | <span class="rank rank-rare">知ってるだけ</span> | 2 を底とする対数 |
| [`std::log10`](#log10) | <span class="rank rank-rare">知ってるだけ</span> | 10 を底とする対数 |
| [`std::cbrt`](#cbrt) | <span class="rank rank-rare">知ってるだけ</span> | 立方根 |
| [`std::fma`](#fma) | <span class="rank rank-rare">知ってるだけ</span> | `a * b + c` を誤差少なく |

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

## 関数の詳しい説明

### std::sqrt {#sqrt}

```cpp
float sqrt(float x);
double sqrt(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 0 以上の値 |

- 戻り値: √x。**マイナスを渡すと NaN**

!!! note "実際は"
    「近いかどうか」を比べるだけなら、`dx * dx + dy * dy < range * range` のように 2 乗のまま比べると sqrt が要らず速くなります。

### std::abs {#abs}

```cpp
int abs(int x);
float abs(float x);
double abs(double x);
```

- 絶対値（マイナスを取った値）。整数版は `<cstdlib>`、浮動小数点版は `<cmath>` にあります

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::abs(-5), std::abs(-2.5f));
  std::println("{}", std::sqrt(16.0f));
}
```

```text title="実行結果"
5 2.5
4
```

### std::sin {#sin}

```cpp
float sin(float radians);
```

- サイン。引数は**ラジアン**（180 度 = π）。揺れ（上下にふわふわ）にも使えます

### std::cos {#cos}

```cpp
float cos(float radians);
```

- コサイン。`{cos(a), sin(a)}` が角度 a の向きの長さ 1 のベクトルです

```cpp
#include <cmath>
#include <print>

int main() {
  // 時間でふわふわ上下する（振幅 4、0.5 秒ごと）
  for (float t : {0.0f, 0.125f, 0.25f}) {
    float offset = std::sin(t * 2.0f * 3.14159265f / 0.5f) * 4.0f;
    std::println("t={} → {:.1f}", t, offset);
  }
  std::println("{:.1f}", std::cos(0.0f));
}
```

```text title="実行結果"
t=0 → 0.0
t=0.125 → 4.0
t=0.25 → -0.0
1.0
```

`-0.0` は、sin(π) が計算誤差でほんの少しマイナス（-0.0000003 くらい）になったものです。

### std::atan2 {#atan2}

```cpp
float atan2(float y, float x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | 浮動小数点 | 向きの y 成分（**先に y**） |
| `x` | 浮動小数点 | 向きの x 成分 |

- 戻り値: -π〜π のラジアン。右が 0、上（y が正）が π/2
- `atan(y / x)` と違って、4 方向すべてを正しく区別でき、x が 0 でも割り算エラーになりません

### std::floor {#floor}

```cpp
float floor(float x);
```

- x 以下で一番大きい整数（マイナスでも「小さいほう」へ）。座標からマスの番号を出すのに使います

### std::round {#round}

```cpp
float round(float x);
```

- 四捨五入（0.5 は 0 から遠いほうへ）。`std::lround` は long で返します

### std::ceil {#ceil}

```cpp
float ceil(float x);
```

- x 以上で一番小さい整数（切り上げ）

### std::trunc {#trunc}

```cpp
float trunc(float x);
```

- 小数部分を捨てる（0 の方向へ）。`static_cast<int>(x)` と同じ向き

```cpp
#include <cmath>
#include <print>

int main() {
  for (float x : {2.5f, -2.5f}) {
    std::println("{}: floor {} / ceil {} / round {} / trunc {}", x, std::floor(x),
                 std::ceil(x), std::round(x), std::trunc(x));
  }
  constexpr float kTileSize = 32.0f;
  float player_x = -10.0f;
  std::println("マス {}", static_cast<int>(std::floor(player_x / kTileSize)));
}
```

```text title="実行結果"
2.5: floor 2 / ceil 3 / round 3 / trunc 2
-2.5: floor -3 / ceil -2 / round -3 / trunc -2
マス -1
```

マイナスの座標でマスの番号を出すときは、`floor` を使わないと `-10 / 32` が 0 になってしまいます。

### std::lerp {#lerp}

<span class="ver ver-20">C++20</span>

```cpp
constexpr float lerp(float a, float b, float t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 浮動小数点 | 始まりの値（t = 0 のとき） |
| `b` | 浮動小数点 | 終わりの値（t = 1 のとき） |
| `t` | 浮動小数点 | 割合。0〜1 の外も使える |

- 戻り値: `a + t * (b - a)`

```cpp
#include <cmath>
#include <print>

int main() {
  float camera = 0.0f;
  float target = 100.0f;
  for (int i = 0; i < 3; ++i) {
    camera = std::lerp(camera, target, 0.5f);  // 毎フレーム半分ずつ近づく
    std::print("{} ", camera);
  }
  std::println("");
}
```

```text title="実行結果"
50 75 87.5 
```

### std::pow {#pow}

```cpp
float pow(float base, float exp);
```

- `base` の `exp` 乗。2 乗するだけなら `x * x` と書くほうが速くて正確です

### std::hypot {#hypot}

```cpp
float hypot(float x, float y);
float hypot(float x, float y, float z);  // C++17
```

- `sqrt(x*x + y*y)` と同じですが、とても大きい・小さい値でもあふれにくいです

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::pow(2.0f, 10.0f), std::hypot(3.0f, 4.0f),
               std::hypot(1.0f, 2.0f, 2.0f));
}
```

```text title="実行結果"
1024 5 3
```

### std::fmod {#fmod}

```cpp
float fmod(float x, float y);
```

- 小数の割り算の余り（符号は x と同じ）。角度を 0〜360 に戻す、アニメーションをループさせるのに使います

```cpp
#include <cmath>
#include <print>

int main() {
  float angle = 725.0f;
  std::println("{}", std::fmod(angle, 360.0f));
  float t = 2.3f;
  std::println("{:.1f}", std::fmod(t, 1.0f));  // 1 秒でループするアニメーションの位置
}
```

```text title="実行結果"
5
0.3
```

### std::tan {#tan}

```cpp
float tan(float radians);
```

- タンジェント。カメラの視野角の計算などで使います

### std::asin {#asin}

```cpp
float asin(float x);
```

- サインの逆。-1〜1 を渡すと -π/2〜π/2 が返ります。範囲外は NaN

### std::acos {#acos}

```cpp
float acos(float x);
```

- コサインの逆。2 つの単位ベクトルの内積から、間の角度を出すのに使います（`acos(dot)`）。誤差で 1 を少し超えると NaN になるので、`std::clamp(dot, -1.0f, 1.0f)` してから渡します

```cpp
#include <algorithm>
#include <cmath>
#include <print>

int main() {
  float dot = 1.0000001f;  // 誤差で 1 を少し超えた内積
  std::println("{}", std::isnan(std::acos(dot)));
  std::println("{}", std::acos(std::clamp(dot, -1.0f, 1.0f)));
  std::println("{:.3f} {:.3f}", std::tan(0.5f), std::asin(1.0f));
}
```

```text title="実行結果"
true
0
0.546 1.571
```

### std::exp {#exp}

```cpp
float exp(float x);
```

- e（約 2.718）の x 乗。フレームレートに依存しない減衰（`velocity *= std::exp(-damping * dt)`）に使えます

### std::log {#log}

```cpp
float log(float x);
```

- 自然対数（e を底）。0 以下を渡すと -inf や NaN

### std::isnan {#isnan}

```cpp
bool isnan(float x);
```

- NaN（Not a Number：0/0 や sqrt(-1) の結果）か。NaN は自分自身とも等しくないので `x == x` が false になります

### std::isinf {#isinf}

```cpp
bool isinf(float x);
```

- 無限大か（1.0f / 0.0f など）

```cpp
#include <cmath>
#include <print>

int main() {
  float nan = std::sqrt(-1.0f);
  float inf = std::exp(1000.0f);
  std::println("{} {} {}", std::isnan(nan), nan == nan, std::isinf(inf));
  float velocity = 10.0f;
  velocity *= std::exp(-2.0f * 0.5f);  // 0.5 秒で減衰
  std::println("{:.2f} {:.2f}", velocity, std::log(std::exp(3.0f)));
}
```

```text title="実行結果"
true false true
3.68 3.00
```

### std::copysign {#copysign}

```cpp
float copysign(float magnitude, float sign);
```

- `magnitude` の大きさで、符号だけ `sign` から取った値

### std::log2 {#log2}

```cpp
float log2(float x);
```

- 2 を底とする対数。テクスチャの mipmap の段数などに使います

### std::log10 {#log10}

```cpp
float log10(float x);
```

- 10 を底とする対数。音量（デシベル）の計算に使います

### std::cbrt {#cbrt}

```cpp
float cbrt(float x);
```

- 立方根。マイナスでも使えます

### std::fma {#fma}

```cpp
float fma(float a, float b, float c);
```

- `a * b + c` を 1 回の丸めで計算します（誤差が少ない）

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {} {} {}", std::copysign(3.0f, -1.0f), std::log2(256.0f),
               std::log10(1000.0f), std::cbrt(-27.0f), std::fma(2.0f, 3.0f, 1.0f));
}
```

```text title="実行結果"
-3 8 3 -3 7
```

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

## 理解度チェック

!!! question "Q1. 敵がプレイヤーの方を向く角度は？（プレイヤー (px, py)、敵 (ex, ey)）"
    <div class="spoiler" markdown>

    **答え:** `std::atan2(py - ey, px - ex)`。「敵から見たプレイヤーの向き」なので、プレイヤー − 敵 の差を渡します。

    </div>

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
