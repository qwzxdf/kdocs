---
title: std::lerp
summary: "2 つの値の間を、割合で補間する（線形補間）。"
order: 13
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lerp

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <cmath>`
</div>

カメラを目標の位置へなめらかに近づけたい、HP バーの色を赤から緑へ変えたい、フェードアウトをしたい。ゲームの「なめらかな変化」の大半は、2 つの値の間を割合で進む処理で書けます。`std::lerp(a, b, t)` は、a から b までの道のりのうち、割合 `t` だけ進んだ位置の値を返します。

!!! tip "ポイント"
    - `t` が 0 のとき `a`、1 のとき `b`、0.5 のとき真ん中を返す。
    - `t` は 0〜1 に収める必要はない。超えると、`b` を越えた延長線上の値になる。
    - 毎フレーム `lerp(現在, 目標, 0.1f)` と書く追従は、フレームレートによって速さが変わる。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の一覧を先に見ると、ほかの数学関数との関係が分かります。

## 関数の詳しい説明

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

`a` は `t = 0` のときの値、`b` は `t = 1` のときの値です。型は同じ浮動小数点でそろえます。`float` と `double` を混ぜると、`double` の版が選ばれます。

`t` は割合です。0〜1 の範囲なら、`a` と `b` の間の値になります。範囲を越えて `t = 2` を渡すと、`b` よりさらに先の値（外挿）になります。範囲内に収めたいときは、渡す前に [`clamp`](../../algorithms/clamp.md) で 0〜1 に制限します。

`a + (b - a) * t` と書いても同じ結果ですが、`std::lerp` は `t = 1` のとき必ず `b` を返し、`a` と `b` が同じなら必ずその値を返します。自分で書いた式は、誤差で `b` にぴったり届かないことがあります。

- 戻り値: `a + t * (b - a)`

#### 外挿と、収める必要

`t` は 0〜1 に制限されません。`t = 1.5` なら `b` を越えた先の値、`t = -0.5` なら `a` より手前の値になります。外挿は、予測や、行き過ぎる演出(はねる動き)で役に立ちますが、アニメーションの進行率として使うときは、終点を越えないように `t` を収めておきます。

#### a + (b - a) * t との違い

`std::lerp` は、次の性質を保証します。

- `t = 0` なら必ず `a`、`t = 1` なら必ず `b` を返す
- `a` と `b` が等しければ、どんな `t` でもその値を返す
- `t` が 0〜1 のとき、結果は `a` と `b` の間に収まり、`t` が大きくなるにつれて、減ることがない(単調)
- `b - a` が桁あふれしても、結果は有限になる(正しく計算される)

自分で `a + (b - a) * t` と書くと、`b - a` の丸め誤差のために、`t = 1` でも `b` に届かないことがあります。

#### 型

`float`・`double`・`long double` の版があり、整数を渡すと `double` 版が呼ばれます。`constexpr` なので、コンパイル時の計算にも使えます。

## 実際に動かしてみる

### t の動きと外挿

```cpp
#include <cmath>
#include <print>

int main() {
  float a = 0.0f;
  float b = 100.0f;

  std::println("t = 0.0  -> {}", std::lerp(a, b, 0.0f));
  std::println("t = 0.25 -> {}", std::lerp(a, b, 0.25f));
  std::println("t = 1.0  -> {}", std::lerp(a, b, 1.0f));

  // 範囲の外は、外挿になる
  std::println("t = 1.5  -> {}", std::lerp(a, b, 1.5f));
  std::println("t = -0.5 -> {}", std::lerp(a, b, -0.5f));

  // 止めたいときは、渡す前に t を 0〜1 に収める
  float t = 1.5f;
  t = t < 0.0f ? 0.0f : (t > 1.0f ? 1.0f : t);
  std::println("収めたあと -> {}", std::lerp(a, b, t));
}
```

```text title="実行結果"
t = 0.0  -> 0
t = 0.25 -> 25
t = 1.0  -> 100
t = 1.5  -> 150
t = -0.5 -> -50
収めたあと -> 100
```

`t = 1.5` で 150、`t = -0.5` で −50 になります。最後の例のように `t` を収めておけば、150 ではなく 100 で止まります。C++17 以降なら、`std::clamp(t, 0.0f, 1.0f)` が使えます。

### 終点にぴったり届く

```cpp
#include <cmath>
#include <print>

int main() {
  // 自分で a + (b - a) * t と書くと、t = 1 でも b に届かないことがある
  float a = 1.0f;
  float b = 1e-8f;
  float naive = a + (b - a) * 1.0f;
  std::println("自分で書いた式: {}", naive);
  std::println("std::lerp:      {}", std::lerp(a, b, 1.0f));
  std::println("lerp は b に一致する: {}", std::lerp(a, b, 1.0f) == b);
}
```

```text title="実行結果"
自分で書いた式: 0
std::lerp:      1e-08
lerp は b に一致する: true
```

`b - a` は `1e-8 - 1.0` ですが、`float` では `-1.0` に丸められます。`1.0 + (-1.0 * 1.0)` が 0 になり、`b` の 1e-8 には届きません。`std::lerp` は、このような場合でも `b` を返します。

### フレームレートによらない追従

毎フレーム「一定の割合だけ近づく」書き方は、フレームレートに依存します。1 秒間の追従を、60 fps と 144 fps で比べます。

```cpp
#include <cmath>
#include <print>

// 1 秒間、目標 100 に追従したときの位置
float FollowNaive(float rate, int fps) {
  float pos = 0.0f;
  for (int i = 0; i < fps; ++i) pos = std::lerp(pos, 100.0f, rate);   // 毎フレーム rate だけ近づく
  return pos;
}

float FollowByTime(float speed, int fps) {
  float pos = 0.0f;
  float dt = 1.0f / fps;
  float t = 1.0f - std::exp(-speed * dt);   // 経過時間から t を作る
  for (int i = 0; i < fps; ++i) pos = std::lerp(pos, 100.0f, t);
  return pos;
}

int main() {
  std::println("毎フレーム 2% 近づく:  60fps {:.1f} / 144fps {:.1f}", FollowNaive(0.02f, 60), FollowNaive(0.02f, 144));
  std::println("経過時間から t を計算:  60fps {:.1f} / 144fps {:.1f}", FollowByTime(2.0f, 60), FollowByTime(2.0f, 144));
}
```

```text title="実行結果"
毎フレーム 2% 近づく:  60fps 70.2 / 144fps 94.5
経過時間から t を計算:  60fps 86.5 / 144fps 86.5
```

上の行は、毎フレーム 2% 近づく書き方です。フレームが多い 144 fps のほうが、1 秒で目標にずっと近づきます。下の行は、経過時間 `dt` から `t = 1 - exp(-speed × dt)` を計算した書き方です。どちらのフレームレートでも、ほぼ同じ位置になります。

## ゲームでの使いどころ

カメラの追従は代表例です。毎フレーム `cam = std::lerp(cam, target, 0.1f)` と書くと、目標に近づくほど動きがゆっくりになる、滑らかな追従になります。ただしこの書き方は、1 フレームの長さに依存します。60 フレームの機械と 144 フレームの機械では、追いつく速さが変わります。`t` を `1 - std::exp(-k * dt)` として、経過時間 `dt` から計算すると、フレームレートによらず同じ速さになります。

色や透明度の変化にも使います。赤 `(1, 0, 0)` と緑 `(0, 1, 0)` の間を HP の割合で補間すると、HP バーの色が連続的に変わります。成分ごとに `lerp` を呼びます。

アニメーションの進行にも使います。時刻から `t = (now - start) / duration` を求め、それを `lerp` に渡すと、一定の速さで移動します。`t` をイージング関数に通してから渡すと、加速や減速が付きます。

## よくあるミス

??? failure "フレームレートに依存した追従を書く"
    `cam = lerp(cam, target, 0.1f)` は、1 フレームごとに 10% 近づくので、フレームが多い機械ほど速く追いつきます。時間の長さを使った `t = 1 - exp(-k * dt)` を使います。

??? failure "`t` が範囲外になって、行き過ぎる"
    `t = (now - start) / duration` は、`now` が `start + duration` を越えると 1 を超えて、目標を通り過ぎます。`std::clamp(t, 0.0f, 1.0f)` で 0〜1 に収めてから渡します。

??? failure "角度に `lerp` を使って、遠回りする"
    角度 `350` 度と `10` 度の間を `lerp` で補間すると、20 度の近道ではなく 340 度の遠回りをします。角度は、折り返しを考えた補間（差を `[-180, 180]` に収めてから足す）を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| SimpleMath の `Vector3::Lerp` | ベクトルの補間。成分ごとに `lerp` を呼ぶのと同じ |
| [`clamp`](../../algorithms/clamp.md) | `t` を 0〜1 に収める |
| `std::midpoint` | 2 つの値の真ん中（`t = 0.5` の `lerp`）。桁あふれに安全 |

## コンパイラ対応

C++20 から使えます。`<cmath>` にあります。MSVC・GCC・Clang とも対応しています。C++17 以前では、`a + (b - a) * t` と自分で書く必要があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lerp(a, b, t)` は a から b へ割合 t だけ進んだ値。
    - [x] 毎フレーム同じ割合で追従するとフレームレートで変わる。`dt` から計算する。
    - [x] `t` が範囲外のときは外挿になる。必要なら `clamp` する。

## 関連ページ

- [cpprefjp: std::lerp](https://cpprefjp.github.io/reference/cmath/lerp.html)
- [cppreference: std::lerp](https://en.cppreference.com/w/cpp/numeric/math/lerp)
