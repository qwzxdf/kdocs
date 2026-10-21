---
title: std::asin
summary: "アークサイン（逆正弦）を求める。結果はラジアン。"
order: 6
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::asin

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::asin` は、**サインの逆関数**です。−1〜1 の値から、角度（ラジアン、−π/2〜π/2）を返します。範囲外の値を渡すと NaN になります。

!!! tip "ポイント"
    - 引数は −1〜1。誤差で少し超えたときは `std::clamp` してから渡す。
    - 結果はラジアン。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::asin {#asin}

```cpp
float asin(float x);
```

- サインの逆。-1〜1 を渡すと -π/2〜π/2 が返ります。範囲外は NaN

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f} {:.4f}", std::asin(1.0), std::asin(0.0));
}
```

```text title="実行結果"
1.5708 0.0000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのベクトルの角度（外積の大きさから） | `std::asin(len)` |

## よくあるミス

??? failure "範囲外の値（誤差で 1.0000001）"
    NaN になります。`std::clamp(v, -1.0f, 1.0f)` で守ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`acos`](acos.md) | コサインの逆 |
| [`atan2`](atan2.md) | 2 つの値から角度 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サインの逆関数
    - [x] 引数は −1〜1
    - [x] 誤差は clamp

## 関連ページ

- [cpprefjp: std::asin](https://cpprefjp.github.io/reference/cmath/asin.html)
- [cppreference: std::asin](https://en.cppreference.com/w/cpp/numeric/math/asin)
