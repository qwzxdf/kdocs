---
title: std::atan
summary: "アークタンジェント（逆正接）。傾きから角度を求める。"
order: 26
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atan

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

斜面の傾きの割合（上がる高さ ÷ 進む距離）が分かっているとき、その斜面は何度でしょうか。割合から角度を求めるのが逆正接、`std::atan` です。

ただし `atan` は、割合（1 つの数）しか受け取らないので、「右にも左にも同じ割合」の区別がつきません。向きを含めた角度が欲しいときは、x と y を別々に渡せる [`atan2`](atan2.md) を使います。

!!! tip "ポイント"
    - `std::atan(1.0)` は π/4（約 0.785）。戻り値はラジアン
    - 戻り値の範囲は −π/2 〜 +π/2。象限の区別はできない
    - 2D の向き（x と y から角度）は `atan2(y, x)` を使う
    - 度に直すときは、180 / π を掛ける

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atan {#atan}

```cpp
float atan(float x);
double atan(double x);
long double atan(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 傾き（高さ ÷ 距離）。どんな実数でもよい |

戻り値は、正接が `x` になる角度で、単位はラジアンです。範囲は −π/2 〜 +π/2 で、`x` が大きくなるほど π/2 に近づきます（無限大の入力では、ちょうど π/2）。

`x` にはどんな値でも渡せるので、定義域のエラーはありません。`atan(0)` は 0、`atan(1)` は π/4 です。整数を渡すと `double` に変換されます。

落とし穴は、傾きを計算した時点で情報が失われることです。`y / x` を渡すと、`x` が負の場合に符号が打ち消し合い、(1, 1) と (−1, −1) が同じ角度になります。`x` が 0 の場合は 0 で割ることにもなります。位置ベクトルから向きを求めるなら、必ず `atan2` を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  const double rad = std::atan(1.0);                          // 傾き 1（45 度）
  const double deg = rad * 180.0 / std::numbers::pi;          // 度に直す
  std::println("atan(1) = {} ラジアン", rad);
  std::println("      = {} 度", deg);
  std::println("atan(0) = {}", std::atan(0.0));
}
```

```text title="実行結果"
atan(1) = 0.7853981633974483 ラジアン
      = 45 度
atan(0) = 0
```

## ゲームでの使いどころ

斜面の傾斜角を求める用途が代表的です。高さの差と水平距離から、坂道の角度を出します。

```cpp
// 高さ rise、水平距離 run の坂道の角度（ラジアン）
const float slope_angle = std::atan(rise / run);
```

この角度が一定以上なら「急すぎて登れない」と判定する、といった使い方ができます。`run` が 0（垂直）のときは割り算が危険なので、`atan2(rise, run)` にすれば解決します。

## よくあるミス

??? failure "向きの角度に使って、左右が逆になる"
    `atan(y / x)` は `x` の符号を区別できません。`atan2(y, x)` を使います。

??? failure "度とラジアンを取り違える"
    戻り値はラジアンです。度が必要なら 180 / π を掛けます（`std::numbers::pi` を使う）。

??? failure "`x` が 0 のときの割り算で NaN や無限大になる"
    `y / x` の割り算を避けるため、`atan2` に切り替えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atan2`](atan2.md) | x と y を別々に受け取り、象限まで区別する |
| [`asin`](asin.md) | 逆正弦。正弦から角度を求める |
| [`tan`](tan.md) | 正接。`atan` の逆 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atan(x)` は正接が `x` になる角度（ラジアン、−π/2 〜 π/2）
    - [x] 象限は区別できない。向きは `atan2(y, x)`
    - [x] 度に直すには 180 / π を掛ける

## 関連ページ

- [`std::atan2`](atan2.md)
- [cpprefjp: std::atan](https://cpprefjp.github.io/reference/cmath/atan.html)
- [cppreference: std::atan](https://en.cppreference.com/w/cpp/numeric/math/atan)
