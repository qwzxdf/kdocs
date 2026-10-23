---
title: NAN
summary: "float の NaN（非数）を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# NAN

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

値が未設定であることを、浮動小数点数で表したい。0 だと本当の 0 と区別できません。`NAN` は、<strong>「数ではない」値（NaN）</strong>を表す `float` の定数マクロです。

!!! tip "ポイント"
    - `NAN` は `float` の quiet NaN
    - `NAN != NAN` が真（NaN は自分自身とも等しくない）
    - 判定は `std::isnan`。`== NAN` では検出できない
    - `double` の NaN が欲しいなら `std::numeric_limits<double>::quiet_NaN()`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### NAN {#nan_macro}

<span class="ver ver-11">C++11</span>

```cpp
#define NAN /* float の定数式 */
```

`NAN` は、`float` の静かな NaN（quiet NaN）を表す定数式です。計算に使っても例外は発生せず、結果も NaN になります。

「値がまだ決まっていない」ことを表す目印としても使えます。ただし、NaN は比較がすべて偽になるので、`if (x == NAN)` では検出できません。必ず `std::isnan(x)` で調べます。

NaN が意図せず混ざると、計算が壊れて原因をたどりにくくなります。目印として使う場合は、使う範囲を限り、他の計算に渡さないようにします。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  const float x = NAN;
  std::println("isnan(NAN)  = {}", std::isnan(x));
  std::println("NAN == NAN  = {}", x == x);        // 常に偽
}
```

```text title="実行結果"
isnan(NAN)  = true
NAN == NAN  = false
```

## ゲームでの使いどころ

「測定できなかった」ことを、値の中で表します。

```cpp
float measured = NAN;                 // 未測定
if (TryMeasure(&measured)) { /* measured は有効 */ }
else if (std::isnan(measured)) { /* 未測定のまま */ }
```

## よくあるミス

??? failure "`== NAN` で判定して、常に偽になる"
    `std::isnan` を使います。

??? failure "NaN が計算に混ざる"
    目印の NaN は、計算に渡す前に取り除きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nan`](nan.md) | 関数版 |
| [`isnan`](isnan.md) | NaN か |
| [`INFINITY`](infinity.md) | 無限大を表すマクロ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `NAN` は `float` の NaN を表す
    - [x] `== NAN` では検出できない。`isnan` を使う
    - [x] 計算に混ざらないよう注意

## 関連ページ

- [cpprefjp: NAN](https://cpprefjp.github.io/reference/cmath/nan.html)
- [cppreference: NAN](https://en.cppreference.com/w/cpp/numeric/math/NAN)
