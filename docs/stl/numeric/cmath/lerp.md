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

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lerp(a, b, t)` は a から b へ割合 t だけ進んだ値。
    - [x] 毎フレーム同じ割合で追従するとフレームレートで変わる。`dt` から計算する。
    - [x] `t` が範囲外のときは外挿になる。必要なら `clamp` する。

## 関連ページ

- [cpprefjp: std::lerp](https://cpprefjp.github.io/reference/cmath/lerp.html)
- [cppreference: std::lerp](https://en.cppreference.com/w/cpp/numeric/math/lerp)
