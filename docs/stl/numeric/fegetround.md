---
title: std::fegetround
summary: "現在の浮動小数点の丸めモードを調べる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fegetround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

浮動小数点数の丸め方は、実は切り替えられます。普通は最も近い値に丸めますが、切り上げや切り捨てにもできます。いまどの丸め方になっているかを調べるのが `std::fegetround` です。

!!! tip "ポイント"
    - `std::fegetround()` は現在の丸めモードを返す
    - 既定は `FE_TONEAREST`（最も近い値へ）
    - 他に `FE_UPWARD`、`FE_DOWNWARD`、`FE_TOWARDZERO`
    - 変更は `fesetround`

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fegetround {#fegetround}

<span class="ver ver-11">C++11</span>

```cpp
int fegetround();
```

戻り値は、現在の丸めモードを表す定数で、`FE_TONEAREST`、`FE_UPWARD`、`FE_DOWNWARD`、`FE_TOWARDZERO` のいずれかです。丸めモードを持たない環境や、判別できない場合は負の値を返します。

丸めモードは、足し算や掛け算の結果の最後の桁の丸め方、`rint` / `nearbyint` の丸め方に影響します。既定の `FE_TONEAREST` は、ちょうど中間のとき偶数側に丸めます。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::println("既定は最も近い値へ: {}", std::fegetround() == FE_TONEAREST);
}
```

```text title="実行結果"
既定は最も近い値へ: true
```

## ゲームでの使いどころ

丸めモードを一時的に変える処理の前後で、元の値を保存・復元するために使います。

```cpp
const int saved = std::fegetround();   // 元のモードを保存
std::fesetround(FE_DOWNWARD);
// …切り捨ての計算…
std::fesetround(saved);                // 元に戻す
```

## よくあるミス

??? failure "変更したまま戻し忘れ、他の計算に影響する"
    変更の前に `fegetround` で保存し、終わったら戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |
| [`nearbyint`](cmath/nearbyint.md) | 現在の丸めモードで整数に丸める |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fegetround()` は現在の丸めモードを返す
    - [x] 既定は `FE_TONEAREST`
    - [x] 変更したら、元に戻す

## 関連ページ

- [cpprefjp: std::fegetround](https://cpprefjp.github.io/reference/cfenv/fegetround.html)
- [cppreference: std::fegetround](https://en.cppreference.com/w/cpp/numeric/fenv/fegetround)
