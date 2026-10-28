---
title: std::lround
summary: "小数を四捨五入して、整数型（long）で返す。"
order: 38
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lround

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

小数を四捨五入して整数にしたい。`std::round` の結果を整数型に直す二段の手間を `std::lround` は 1 回で済ませます。0.5 のときは、遠いほう（絶対値の大きいほう）に丸めます。

!!! tip "ポイント"
    - `std::lround(2.5)` は 3、`std::lround(-2.5)` は −3
    - 0.5 は 0 から遠いほうへ（普通の四捨五入）
    - 戻り値は `long`。Windows では 32 ビット
    - `lrint` は偶数丸め（2.5 は 2）

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lround {#lround}

<span class="ver ver-11">C++11</span>

```cpp
long lround(float x);
long lround(double x);
long lround(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は、`x` に最も近い整数を `long` で返したものです。小数部がちょうど 0.5 のときは、絶対値の大きい側に丸めます。2.5 は 3、−2.5 は −3 です。丸めモードに依存せず、この規則で固定です。

`std::lrint` は、現在の丸めモード（既定は偶数丸め）に従うので、2.5 は 2 になります。見た目の四捨五入が欲しいなら、`lround` を使います。

結果が `long` に収まらない場合は、結果が不定です。Windows の `long` は 32 ビットなので、約 21 億を超える値は `llround`（`long long`）にします。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("lround(2.5)  = {}", std::lround(2.5));
  std::println("lround(-2.5) = {}", std::lround(-2.5));
  std::println("lround(2.4)  = {}", std::lround(2.4));
  std::println("lrint(2.5)   = {}", std::lrint(2.5));   // 偶数丸め
}
```

```text title="実行結果"
lround(2.5)  = 3
lround(-2.5) = -3
lround(2.4)  = 2
lrint(2.5)   = 2
```

## ゲームでの使いどころ

座標を最も近いピクセルに丸めるときに使います。

```cpp
const int px = static_cast<int>(std::lround(position.x));
```

## よくあるミス

??? failure "Windows の `long` は 32 ビットで、大きな値があふれる"
    `llround` を使います。

??? failure "`lrint` と取り違えて、2.5 が 2 になる"
    四捨五入は `lround` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`round`](round.md) | 浮動小数点数のまま四捨五入 |
| [`lrint`](lrint.md) | 現在の丸めモード（既定は偶数丸め） |
| [`llround`](llround.md) | `long long` を返す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lround(x)` は四捨五入して `long` で返す
    - [x] 0.5 は遠いほうへ。丸めモードに依存しない
    - [x] Windows の `long` は 32 ビット

## 関連ページ

- [cpprefjp: std::lround](https://cpprefjp.github.io/reference/cmath/lround.html)
- [cppreference: std::lround](https://en.cppreference.com/w/cpp/numeric/math/lround)
