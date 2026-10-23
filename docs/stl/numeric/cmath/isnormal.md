---
title: std::isnormal
summary: "正規数（0・無限大・NaN・非正規数以外）かを判定する。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isnormal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

浮動小数点数が 0 に近づきすぎると、通常の精度で表せない「非正規化数」になり、計算が遅くなったり、精度が落ちたりします。`std::isnormal` は、値が<strong>通常の数（ゼロでも非正規化数でも無限大でも NaN でもない）</strong>かを調べます。

!!! tip "ポイント"
    - `std::isnormal(1.0)` は `true`、`std::isnormal(0.0)` は `false`
    - ゼロ・非正規化数・無限大・NaN はすべて `false`
    - 有限かどうかだけなら `isfinite`
    - 非正規化数の混入の検出に使える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isnormal {#isnormal}

<span class="ver ver-11">C++11</span>

```cpp
bool isnormal(float x);
bool isnormal(double x);
bool isnormal(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 調べたい値 |

戻り値は、`x` が通常の（正規化された）数なら `true` です。ゼロは通常の数ではないので `false` です。ここが `isfinite`（ゼロも `true`）との違いです。

非正規化数は、0 にとても近い値で、一部の CPU では計算が数十倍遅くなります。音声のフィルターなどで、フィードバックの値が 0 に向かって減衰していくと、この遅さが突然現れます。`isnormal` で検出するか、小さな値を 0 に丸める（FTZ / DAZ の設定）対策をとります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double tiny = std::numeric_limits<double>::denorm_min();   // 最小の非正規化数
  std::println("1.0 : {}", std::isnormal(1.0));
  std::println("0.0 : {}", std::isnormal(0.0));
  std::println("tiny: {}", std::isnormal(tiny));
}
```

```text title="実行結果"
1.0 : true
0.0 : false
tiny: false
```

## ゲームでの使いどころ

フィルターや減衰の計算で、非正規化数が出て重くならないかを検出します。

```cpp
if (!std::isnormal(state) && state != 0.0f) {
  state = 0.0f;   // 非正規化数は 0 に丸める
}
```

## よくあるミス

??? failure "ゼロを `true` と期待する"
    `isnormal(0.0)` は `false` です。ゼロを含めて有限かを調べるなら `isfinite`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isfinite`](isfinite.md) | 有限の値か（ゼロも含む） |
| [`fpclassify`](fpclassify.md) | 値の種類を分類 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isnormal(x)` は通常の数のとき `true`
    - [x] ゼロと非正規化数は `false`
    - [x] 非正規化数による遅さの検出に使える

## 関連ページ

- [cpprefjp: std::isnormal](https://cpprefjp.github.io/reference/cmath/isnormal.html)
- [cppreference: std::isnormal](https://en.cppreference.com/w/cpp/numeric/math/isnormal)
