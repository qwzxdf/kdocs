---
title: std::copysign
summary: "大きさは x、符号は y の値を作る。"
order: 25
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::copysign

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

「大きさはこの値で、向きはあの値と同じにしたい」という場面があります。たとえば、反動の大きさ（常に正の値）に弾が飛んだ向きの符号を付けたい。`if (y < 0) x = -x;` と書くこともできますが、`-0.0` の扱いなど細かい例外がついてきます。

`std::copysign` は、<strong>1 つ目の引数の大きさに、2 つ目の引数の符号を付けて</strong>返します。

!!! tip "ポイント"
    - `std::copysign(3.0, -1.0)` は −3。大きさは 3、符号は −1 のもの
    - 符号は `-0.0` や NaN の符号ビットまで見る
    - 符号の取り出しは `signbit`、大きさの取り出しは `fabs`
    - 分岐なしで符号を移せるので、シェーダー風の計算で便利

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::copysign {#copysign}

<span class="ver ver-11">C++11</span>

```cpp
float copysign(float x, float y);
double copysign(double x, double y);
long double copysign(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 大きさを取る値 |
| `y` | 浮動小数点数 | 符号を取る値 |

戻り値は、`x` の絶対値に `y` の符号を付けた値です。`y` が 0 以上（`+0.0` を含む）なら正、`y` が負（`-0.0` を含む）なら負になります。

`y < 0` と比べる書き方との違いは、`-0.0` と NaN の扱いです。`-0.0 < 0` は偽ですが、`copysign(1.0, -0.0)` は −1 を返します。計算の結果で符号つきゼロが現れる場面（例えば `atan2` の結果の方向）では、この違いが意味を持ちます。

`x` が NaN のときでも、符号は `y` のものに変わります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("copysign(3, -1)    = {}", std::copysign(3.0, -1.0));
  std::println("copysign(-3, 1)    = {}", std::copysign(-3.0, 1.0));
  std::println("copysign(1, -0.0)  = {}", std::copysign(1.0, -0.0));  // -0.0 の符号も反映
}
```

```text title="実行結果"
copysign(3, -1)    = -3
copysign(-3, 1)    = 3
copysign(1, -0.0)  = -1
```

## ゲームでの使いどころ

「大きさ」と「向き」を別々に計算して、あとで合体するときに使います。

```cpp
// 反動の大きさ kick は常に正。向きは弾の飛んだ方向 direction.x の符号に従う
const float recoil_x = std::copysign(kick, direction.x);
```

符号を取り出して反転させる場面でも便利です。`signbit` で分岐するより、符号の移し替えが短く書けます。

## よくあるミス

??? failure "引数の順序を逆にして、大きさと符号が入れ替わる"
    1 つ目が大きさ、2 つ目が符号です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`signbit`](signbit.md) | 符号ビットを真偽で返す |
| [`fabs`](fabs.md) | 絶対値（符号を正にする） |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `copysign(x, y)` は `x` の大きさに `y` の符号を付ける
    - [x] `-0.0` の符号ビットも反映される
    - [x] 大きさと向きを別々に計算するときに使う

## 関連ページ

- [`std::signbit`](signbit.md)
- [cpprefjp: std::copysign](https://cpprefjp.github.io/reference/cmath/copysign.html)
- [cppreference: std::copysign](https://en.cppreference.com/w/cpp/numeric/math/copysign)
