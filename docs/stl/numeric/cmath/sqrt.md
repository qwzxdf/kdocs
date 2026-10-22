---
title: std::sqrt
summary: "平方根（ルート）を求める。"
order: 1
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sqrt

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

敵がプレイヤーの近くにいるかを調べたいとき、2 点の距離が必要になります。距離は、x の差と y の差を 2 乗して足し、その平方根を取ると求まります。この「平方根を取る」処理が `std::sqrt` です。ベクトルの長さ、正規化、円と円の当たり判定でも、ほぼ毎回登場します。

!!! tip "ポイント"
    - 距離を比べるだけなら、平方根を取らずに 2 乗のまま比べる。`sqrt` を呼ぶ回数が減る。
    - 負の数を渡すと NaN（数ではない値）が返る。例外は投げられない。
    - `float` を渡せば `float` 版が呼ばれる。`double` に変換されて遅くなることはない。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の一覧を先に見ると、ほかの数学関数との関係が分かります。

## 関数の詳しい説明

### std::sqrt {#sqrt}

```cpp
float sqrt(float x);
double sqrt(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 0 以上の値 |

`x` が負の数のときは、NaN が返ります。エラー表示も例外も出ないので、NaN が次の計算に流れ込んで、画面上のキャラクターが消える、という形で気づくことが多くなります。距離の 2 乗を計算した値は 0 以上のはずですが、浮動小数点の誤差で `-0.0000001` のような値になる式（たとえば 1 から何かを引いた値）では、`std::max(0.0f, x)` を通してから渡すと安全です。

`x` が 0 のときは 0 が返ります。無限大を渡すと無限大が返ります。

- 戻り値: √x。**マイナスを渡すと NaN**

!!! note "実際は"
    「近いかどうか」を比べるだけなら、`dx * dx + dy * dy < range * range` のように 2 乗のまま比べると sqrt が要らず速くなります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::sqrt(16.0), std::isnan(std::sqrt(-1.0)));
}
```

```text title="実行結果"
4 true
```

## ゲームでの使いどころ

最も多い使いどころは、2 点間の距離です。`std::sqrt(dx * dx + dy * dy)` で、敵とプレイヤーの距離が求まります。ただし「射程 5 メートル以内か」だけを知りたいなら、`dx * dx + dy * dy < 5.0f * 5.0f` と 2 乗のまま比べます。大小関係は 2 乗しても変わらないので、毎フレーム何百体もの敵を調べる場面では、この差が効きます。

ベクトルの正規化（長さを 1 にそろえる）にも使います。`length = std::sqrt(x*x + y*y + z*z)` を求めて、各成分を `length` で割ります。このとき `length` が 0 だと 0 で割ってしまうので、割る前に 0 に近くないかを確かめます。SimpleMath の `Vector3::Normalize` は、この処理を内部でやってくれます。

## よくあるミス

??? failure "距離の比較で毎回 sqrt を呼ぶ"
    `if (std::sqrt(dx*dx + dy*dy) < range)` と書くと、比較のたびに平方根を計算します。`dx*dx + dy*dy < range * range` と書けば、`sqrt` が要りません。結果は同じで、速くなります。

??? failure "誤差で負になった値を渡す"
    `std::sqrt(1.0f - dot * dot)` のように、「理論上は 0 以上」の式でも、誤差で `-1e-8` のような値になることがあります。結果は NaN になり、その NaN が座標や色に広がります。`std::sqrt(std::max(0.0f, v))` と書いて、負の値を 0 に直してから渡します。

??? failure "`int` を渡して精度を落とす"
    `std::sqrt(int)` は `double` 版が呼ばれて `double` が返ります。`float` の変数に代入すると精度が落ちる警告が出ます。ゲームでは最初から `float` で計算するのが普通です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hypot`](hypot.md) | `sqrt(x*x + y*y)` と同じ値を、途中の 2 乗で桁あふれしないように計算する。値が極端に大きい場合に使う |
| [`cbrt`](cbrt.md) | 立方根。体積から一辺の長さを求めるときなど |
| SimpleMath の `Vector3::Length` | ベクトルの長さ。内部で `sqrt` を使っている。3D の計算ではこちらを使う |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離を比べるだけなら、2 乗のまま比べる。
    - [x] 負の数を渡すと NaN になる。誤差で負になる式には `std::max(0, v)` を通す。
    - [x] `float` を渡せば `float` 版が呼ばれる。

## 関連ページ

- [cpprefjp: std::sqrt](https://cpprefjp.github.io/reference/cmath/sqrt.html)
- [cppreference: std::sqrt](https://en.cppreference.com/w/cpp/numeric/math/sqrt)
