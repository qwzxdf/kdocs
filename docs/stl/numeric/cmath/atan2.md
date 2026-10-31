---
title: std::atan2
summary: "x と y から、向きの角度（ラジアン）を求める。"
order: 8
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atan2

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

敵がプレイヤーのほうを向くとき、「プレイヤーへの向き」を角度で知りたくなります。2 点の差 `(dx, dy)` が分かっていれば、`atan(dy / dx)` で角度が出そうですが、`dx` が 0 のとき 0 で割ってしまいますし、左を向いているのか右を向いているのかも区別できません。`std::atan2(y, x)` はこの 2 つの問題を解決した関数で、全方向の角度を返します。

!!! tip "ポイント"
    - 引数の順番は `(y, x)`。`(x, y)` ではない。逆にすると 90 度ずれた角度になる。
    - 結果は −π から π のラジアン。度に直すなら `× 180 / π`。
    - `x` と `y` がどちらも 0 でも、例外は投げず、決まった値(ふつうは 0)を返す。ゼロベクトルの向きには意味がない。

!!! info "このページを読む前に"
    角度の単位（度とラジアン）が分かると読みやすいです。度は `度 × π / 180` でラジアンになります。

## 関数の詳しい説明

### std::atan2 {#atan2}

```cpp
float atan2(float y, float x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | 浮動小数点 | 向きの y 成分（**先に y**） |
| `x` | 浮動小数点 | 向きの x 成分 |

`y` と `x` の順番に注意します。数学では `atan(y / x)` と書くので、`y` が先、と覚えます。`std::atan2(dx, dy)` のように逆に渡すと、x 軸ではなく y 軸からの角度が返ります。

戻り値は −π から π（−180 度から 180 度）です。右向き（`x` が正、`y` が 0）が 0、上向き（`y` が正）が π/2、左向きが π（または −π）、下向きが −π/2 です。画面の y 座標が下向きに増える座標系では、上下の意味が逆になる点に注意します。

`atan(y / x)` との違いは、符号を見て象限を区別する点です。`atan(1 / 1)` と `atan(-1 / -1)` はどちらも 45 度ですが、`atan2(1, 1)` は 45 度、`atan2(-1, -1)` は −135 度です。

- 戻り値: -π〜π のラジアン。右が 0、上（y が正）が π/2
- `atan(y / x)` と違って、4 方向すべてを正しく区別でき、x が 0 でも割り算エラーになりません

#### 全方向の角度が求まる理由

`atan(y / x)` は、`y / x` という**1 つの比**にしてから角度を出すので、符号の情報が失われます。`(1, 1)` と `(-1, -1)` は、どちらも比が 1 で、同じ 45 度になります。`atan2` は、`y` と `x` を別々に受け取って、符号から、どの象限かを判断します。

| 向き | `x` | `y` | `atan2(y, x)` |
| --- | --- | --- | --- |
| 右 | 正 | 0 | 0 |
| 上(y が正) | 0 | 正 | π/2 (90 度) |
| 左 | 負 | 0 | π (180 度) |
| 下(y が負) | 0 | 負 | −π/2 (−90 度) |

#### 0 や無限大を渡したとき

`x` が 0 でも、割り算をしないので、エラーにならず π/2 か −π/2 を返します。`x` と `y` がどちらも 0 のときも、例外は投げず、`0` を返します(`x` が `-0.0` の符号つきゼロのときは、`y` の符号に従って `π` か `-π`)。

向きが定まらないゼロベクトルを渡すと、`0`(右向き)になってしまうので、敵が自分と同じ位置にいるときなどは、角度を使う前に、距離が 0 でないかを確かめます。

無限大も、規格で決まった値を返します。たとえば `atan2(y, +∞)` は 0、`atan2(+∞, x)` は π/2 です。NaN を渡すと NaN が返ります。

#### 型

`float`・`double`・`long double` の版があり、`int` を渡すと `double` 版が呼ばれます。`float` で計算を済ませたいときは、引数を `float` にします。C 言語の名前 `atan2f`・`atan2l` も、そのまま使えます。

## 実際に動かしてみる

### 向きから角度を求める

4 方向と斜め 2 方向の角度を、度で出します。

```cpp
#include <cmath>
#include <numbers>
#include <print>

// 向き (x, y) の角度を、度で返す
double AngleDegrees(double x, double y) {
  return std::atan2(y, x) * 180.0 / std::numbers::pi;   // 引数は (y, x) の順
}

int main() {
  std::println("右   (1, 0):   {:6.1f} 度", AngleDegrees(1, 0));
  std::println("上   (0, 1):   {:6.1f} 度", AngleDegrees(0, 1));
  std::println("左   (-1, 0):  {:6.1f} 度", AngleDegrees(-1, 0));
  std::println("下   (0, -1):  {:6.1f} 度", AngleDegrees(0, -1));
  std::println("右上 (1, 1):   {:6.1f} 度", AngleDegrees(1, 1));
  std::println("左下 (-1, -1): {:6.1f} 度", AngleDegrees(-1, -1));   // atan(1/1) だと 45 度になってしまう
}
```

```text title="実行結果"
右   (1, 0):      0.0 度
上   (0, 1):     90.0 度
左   (-1, 0):   180.0 度
下   (0, -1):   -90.0 度
右上 (1, 1):     45.0 度
左下 (-1, -1): -135.0 度
```

`(-1, -1)` が −135 度になるのが、`atan(y / x)` との違いです。`atan(1 / 1)` なら、どちらの向きも 45 度になってしまいます。

### 角度の差を、近い側で扱う

角度は 180 度と −180 度が同じ向きなので、差を単純に引くと、遠回りの値が出ます。差を `[-π, π]` に折り返してから使います。

```cpp
#include <algorithm>
#include <cmath>
#include <numbers>
#include <print>

constexpr float kPi = std::numbers::pi_v<float>;
constexpr float kRad = kPi / 180.0f;

// 角度を [-π, π] の範囲に折り返す
float WrapAngle(float a) {
  while (a > kPi) a -= 2 * kPi;
  while (a < -kPi) a += 2 * kPi;
  return a;
}

// current から target へ向けて、1 回に max_step だけ、近い側の回りかたで回す
float TurnToward(float current, float target, float max_step) {
  float diff = WrapAngle(target - current);   // 折り返してから比べる
  diff = std::clamp(diff, -max_step, max_step);
  return WrapAngle(current + diff);
}

int main() {
  float current = 179.0f * kRad;
  float target = -179.0f * kRad;   // 179 度の、すぐ隣

  std::println("そのまま引く: {:.1f} 度", (target - current) / kRad);        // 遠回りの値
  std::println("折り返す:     {:.1f} 度", WrapAngle(target - current) / kRad);   // 近道
  std::println("5 度ずつ回す: {:.1f} 度", TurnToward(current, target, 5.0f * kRad) / kRad);
}
```

```text title="実行結果"
そのまま引く: -358.0 度
折り返す:     2.0 度
5 度ずつ回す: -179.0 度
```

179 度から −179 度への差は、本当は 2 度ですが、そのまま引くと −358 度になります。`WrapAngle` で折り返すと 2 度になり、`TurnToward` は 5 度ずつの上限のうち、最後の 2 度で目標に届きます。

### 画面の座標で使う

ゲームの画面は、y が下に向かって増える座標系が多く、数学の座標とは上下が逆です。

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // 画面は、y が下へ増える。敵 (100, 100) から、プレイヤー (200, 50) への向き
  float enemy_x = 100, enemy_y = 100;
  float player_x = 200, player_y = 50;
  float dx = player_x - enemy_x;   //  100: 右
  float dy = player_y - enemy_y;   // -50: 画面では上
  float angle = std::atan2(dy, dx);
  std::println("角度: {:.1f} 度", angle * 180.0f / std::numbers::pi_v<float>);
  // 負の値は「画面の上方向」。画面の y が下向きなので、数学の座標とは上下が逆になる
}
```

```text title="実行結果"
角度: -26.6 度
```

プレイヤーは敵の右上にいるのに、角度は −26.6 度と負の値になります。画面の y が下向きだからです。この角度でスプライトを回転させる分には、画面の座標系で一貫しているので問題ありませんが、数学の座標(y が上向き)の式と混ぜるときは、`dy` の符号を反転させます。

## ゲームでの使いどころ

敵がプレイヤーのほうを向くとき、`float angle = std::atan2(player.y - enemy.y, player.x - enemy.x);` と書くと、向くべき角度が得られます。スプライトを回転させる、弾をその向きに撃つ、といった処理にそのまま使えます。

マウスカーソルの方向に武器を向けるときも同じです。キャラクターの中心からカーソルへの差を `atan2` に渡します。

角度の差を求めるときは、−π と π の境目に注意します。現在の角度が 179 度で目標が −179 度のとき、差は −358 度ではなく 2 度が正しいので、差を求めたあとに `[-π, π]` の範囲へ折り返します。

## よくあるミス

??? failure "引数の順番を `(x, y)` にする"
    `std::atan2(dx, dy)` と書くと、角度が 90 度ずれ、さらに回転の向きが逆になります。`atan2(y, x)` の順が正しいです。

??? failure "`atan(dy / dx)` で代用する"
    `dx` が 0 のとき 0 除算になり、左向きと右向きが区別できません。ゲームのキャラクターの向きなど、全方向に対応する場面では、必ず `atan2` を使います。

??? failure "角度の差をそのまま使って、境目で逆回りする"
    現在 `3.1` ラジアン、目標が `-3.1` ラジアンのとき、差は `-6.2` ですが、実際は `0.08` ラジアン回すだけで届きます。差を `[-π, π]` に折り返してから、回転量を決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atan`](atan.md) | 1 つの比（`y / x`）から角度を求める。象限を区別できない |
| [`acos`](acos.md) | 内積から、2 つのベクトルのなす角を求める。向き（符号）は分からない |
| SimpleMath の `Vector2` の各関数 | 回転や向きの計算をベクトルのままで済ませる |

## コンパイラ対応

C++98 から使えます。MSVC・GCC・Clang とも対応しています。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数の順番は `(y, x)`。
    - [x] 結果は −π から π。全方向の角度が求まる。
    - [x] 角度の差を求めるときは、−π と π の境目で折り返す。

## 関連ページ

- [cpprefjp: std::atan2](https://cpprefjp.github.io/reference/cmath/atan2.html)
- [cppreference: std::atan2](https://en.cppreference.com/w/cpp/numeric/math/atan2)
