---
title: std::fesetround
summary: "浮動小数点の丸め方（最近接・切り上げ・切り捨てなど）を切り替える。"
order: 50
tags:
  - 数値
---

# std::fesetround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

区間演算のように、わざと切り上げや切り捨てで丸めて、結果の範囲を押さえたい計算があります。丸めモードを切り替えるのが `std::fesetround` です。

!!! tip "ポイント"
    - `std::fesetround(FE_UPWARD)` で切り上げに変える
    - 成功すれば 0 を返す。指定できないモードなら 0 以外
    - 影響は、そのスレッドの以降の計算全部
    - 終わったら元のモードに戻す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fesetround {#fesetround}

<span class="ver ver-11">C++11</span>

```cpp
int fesetround(int mode);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mode` | `int` | `FE_TONEAREST`、`FE_UPWARD`、`FE_DOWNWARD`、`FE_TOWARDZERO` のいずれか |

丸めモードを `mode` に変えます。成功すれば 0、環境が対応していないモードなら 0 以外を返します。変更はスレッドごとで、以降の浮動小数点の演算と `nearbyint` などの結果に影響します。

`FE_UPWARD` は正の無限大方向、`FE_DOWNWARD` は負の無限大方向、`FE_TOWARDZERO` は 0 方向への丸めです。`FE_TONEAREST` が既定の「最も近い値へ（中間は偶数へ）」です。

見えにくいバグの原因になるので、変更は短い区間に限り、必ず元に戻します。ライブラリの内部が丸めモードを前提にしている場合、変更したままだと、そのライブラリの結果が変わります。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <cmath>
#include <print>

int main() {
  volatile double x = 2.1;                       // 定数に畳み込まれないよう volatile
  std::println("既定        : {}", std::nearbyint(x));

  const int saved = std::fegetround();
  std::fesetround(FE_UPWARD);
  std::println("切り上げ    : {}", std::nearbyint(x));
  std::fesetround(FE_DOWNWARD);
  std::println("切り捨て    : {}", std::nearbyint(x));
  std::fesetround(saved);                        // 元に戻す
}
```

```text title="実行結果"
既定        : 2
切り上げ    : 3
切り捨て    : 2
```

## ゲームでの使いどころ

丸めの誤差がどちら向きにずれるかを調べたいときに使います。同じ計算を切り上げと切り捨ての両方で行い、結果の差から誤差の大きさを見積もります。

```cpp
std::fesetround(FE_UPWARD);
const double upper = Compute();
std::fesetround(FE_DOWNWARD);
const double lower = Compute();
std::fesetround(FE_TONEAREST);
// lower <= 真の値 <= upper
```

## よくあるミス

??? failure "元に戻さず、他の計算の結果が変わる"
    `fegetround` で保存して、終わったら戻します。

??? failure "最適化でモードの変更が効かない"
    コンパイラのオプションや `volatile` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fegetround`](fegetround.md) | 現在のモードを調べる |
| [`nearbyint`](cmath/nearbyint.md) | 現在のモードで丸める |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fesetround(mode)` は丸めモードを変える
    - [x] 成功で 0。影響はスレッド内の以降の計算全部
    - [x] 必ず元に戻す

## 関連ページ

- [cpprefjp: std::fesetround](https://cpprefjp.github.io/reference/cfenv/fesetround.html)
- [cppreference: std::fesetround](https://en.cppreference.com/w/cpp/numeric/fenv/feround)
