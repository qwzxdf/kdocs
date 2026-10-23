---
title: std::llround
summary: "四捨五入して long long にする。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::llround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::lround` と同じ働きで、結果の型が `long long`（64 ビット）です。四捨五入した値が 32 ビットを超えうるときに使います。

!!! tip "ポイント"
    - `std::llround(2.5)` は 3、`std::llround(-2.5)` は −3
    - 0.5 は 0 から遠い側へ（普通の四捨五入）
    - `lround` との違いは、戻り値が `long long`
    - 結果が `long long` に収まらないと不定

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::llround {#llround}

<span class="ver ver-11">C++11</span>

```cpp
long long llround(float x);
long long llround(double x);
long long llround(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は、`x` に最も近い整数を `long long` で返した値です。小数部がちょうど 0.5 のときは、絶対値の大きい側に丸めます。丸めモードには依存しません。

`llrint` は丸めモードに従い、既定では偶数丸めなので、2.5 が 2 になります。見た目の四捨五入が欲しいときは `llround` です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("llround(2.5)  = {}", std::llround(2.5));
  std::println("llround(-2.5) = {}", std::llround(-2.5));
  std::println("llround(1e12) = {}", std::llround(1.0e12));
}
```

```text title="実行結果"
llround(2.5)  = 3
llround(-2.5) = -3
llround(1e12) = 1000000000000
```

## ゲームでの使いどころ

大きな値の四捨五入で使います。

## よくあるミス

??? failure "`llrint` と取り違えて 2.5 が 2 になる"
    四捨五入は `llround` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lround`](lround.md) | `long` を返す |
| [`llrint`](llrint.md) | 丸めモードに従う |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `llround(x)` は四捨五入して `long long` で返す
    - [x] 0.5 は遠い側へ
    - [x] 丸めモードに依存しない

## 関連ページ

- [cpprefjp: std::llround](https://cpprefjp.github.io/reference/cmath/llround.html)
- [cppreference: std::llround](https://en.cppreference.com/w/cpp/numeric/math/round)
