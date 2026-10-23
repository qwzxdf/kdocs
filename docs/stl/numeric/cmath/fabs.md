---
title: std::fabs
summary: "浮動小数点の絶対値を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fabs

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

2 つの位置の差は、前後どちらが大きいかで正にも負にもなります。「どれだけ離れているか」だけが欲しいとき、符号を捨てた大きさ（絶対値）を使います。

`std::fabs` は、浮動小数点数の絶対値を返します。C++ では `std::abs` も同じ働きをするので、普段はどちらを使っても構いません。

!!! tip "ポイント"
    - `std::fabs(-3.5)` は 3.5。符号を取り除いた大きさを返す
    - 浮動小数点数用。整数の絶対値には `std::abs`（`<cstdlib>`）を使う
    - `std::abs` を浮動小数点数に使っても同じ結果になる（`<cmath>` のオーバーロード）
    - `-0.0` の絶対値は `+0.0`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fabs {#fabs}

```cpp
float fabs(float x);
double fabs(double x);
long double fabs(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 絶対値を取りたい値 |

戻り値は `x` の絶対値で、常に 0 以上（NaN の場合を除く）です。`fabs(-0.0)` は `+0.0` になります。無限大は無限大のままです。

名前が C 言語由来の `fabs` なのは、C では整数の `abs` と区別する必要があったためです。C++ の `<cmath>` には、`float` と `double` を受け取る `std::abs` が用意されていて、型に応じて正しい版が選ばれます。そのため、C++ では `std::abs` を使うのが一般的です。

落とし穴は、整数の `abs` と取り違えることです。`<cstdlib>` の `std::abs(int)` に `float` を渡すと、古い環境では小数部が切り捨てられることがありました。`<cmath>` を取り込めば浮動小数点数用が選ばれますが、不安なら `fabs` を使います。

`fabs` は、ビットの符号部分を 0 にするだけの軽い処理で、コンパイラが命令 1 つに置き換えます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("fabs(-3.5) = {}", std::fabs(-3.5));
  std::println("fabs(2.0)  = {}", std::fabs(2.0));
  std::println("fabs(-0.0) = {}", std::fabs(-0.0));     // 正のゼロになる

  // 値がほぼ等しいか調べる（誤差の許容つき比較）
  const double a = 0.1 + 0.2;
  std::println("ほぼ等しい: {}", std::fabs(a - 0.3) < 1e-9);
}
```

```text title="実行結果"
fabs(-3.5) = 3.5
fabs(2.0)  = 2
fabs(-0.0) = 0
ほぼ等しい: true
```

## ゲームでの使いどころ

浮動小数点数を比べるときは、`==` ではなく、差の絶対値が小さいかを調べます。0.1 + 0.2 のような計算は、誤差で 0.3 とぴったり一致しないためです。

```cpp
// 到着判定: 目標との距離が許容範囲以内か
if (std::fabs(target.x - position.x) < 0.01f) {
  arrived = true;
}
```

2 つの位置の差の大きさ（どちらが前か気にしない）が欲しいときも、同様に使います。

## よくあるミス

??? failure "浮動小数点数を `==` で比べて、一致しない"
    `fabs(a - b) < 許容値` の形で比べます。

??? failure "整数用の `abs` に浮動小数点数を渡して、小数が切り捨てられる"
    `<cmath>` を取り込む、または `fabs` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](abs.md) | 型に応じて整数・浮動小数点数の両方を扱う |
| [`copysign`](copysign.md) | 符号を別の値からコピーする |
| [`signbit`](signbit.md) | 符号ビットを調べる |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fabs(x)` は浮動小数点数の絶対値。`-0.0` は `+0.0` になる
    - [x] C++ では `std::abs` でも同じ
    - [x] 浮動小数点数の比較は、差に `fabs` をかけて許容値と比べる

## 関連ページ

- [`std::abs`](abs.md)
- [cpprefjp: std::fabs](https://cpprefjp.github.io/reference/cmath/fabs.html)
- [cppreference: std::fabs](https://en.cppreference.com/w/cpp/numeric/math/fabs)
