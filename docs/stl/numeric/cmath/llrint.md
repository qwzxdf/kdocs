---
title: std::llrint
summary: "現在の丸めモードで整数に丸める（long long で返す）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::llrint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::lrint` と同じ働きで、結果の型が `long long`（64 ビット）です。Windows の `long` は 32 ビットなので、大きな値を丸めるときは `llrint` を使います。

!!! tip "ポイント"
    - `std::llrint(2.5)` は 2（偶数丸め、`long long`）
    - 現在の丸めモードに従う
    - `lrint` との違いは、戻り値が `long long`
    - 結果が `long long` に収まらないと不定

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::llrint {#llrint}

<span class="ver ver-11">C++11</span>

```cpp
long long llrint(float x);
long long llrint(double x);
long long llrint(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は、`x` を現在の丸めモードで整数に丸めた `long long` の値です。既定の最近接偶数では、2.5 は 2、3.5 は 4 です。

64 ビットの整数で受けるので、約 ±9.2×10¹⁸ までの値を扱えます。範囲を超える値、NaN、無限大を渡すと、結果は不定です。

四捨五入が欲しいなら、`llround` を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("llrint(2.5)  = {}", std::llrint(2.5));
  std::println("llrint(3.5)  = {}", std::llrint(3.5));
  std::println("llrint(1e12) = {}", std::llrint(1.0e12));    // 32 ビットを超える値
}
```

```text title="実行結果"
llrint(2.5)  = 2
llrint(3.5)  = 4
llrint(1e12) = 1000000000000
```

## ゲームでの使いどころ

時刻（ミリ秒）や大きな座標のような、32 ビットに収まらない値を整数に丸めるときに使います。

## よくあるミス

??? failure "`lrint` で Windows の 32 ビットを超えてしまう"
    `llrint` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lrint`](lrint.md) | `long` を返す |
| [`llround`](llround.md) | 四捨五入で `long long` |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `llrint(x)` は丸めて `long long` で返す
    - [x] 既定では偶数丸め
    - [x] 大きな値は `lrint` でなくこちら

## 関連ページ

- [cpprefjp: std::llrint](https://cpprefjp.github.io/reference/cmath/llrint.html)
- [cppreference: std::llrint](https://en.cppreference.com/w/cpp/numeric/math/rint)
