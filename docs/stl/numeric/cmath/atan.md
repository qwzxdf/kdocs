---
title: std::atan
summary: "アークタンジェント（逆正接）。傾きから角度を求める。"
order: 26
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atan

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::atan` は、**タンジェントの逆関数**で、傾き（y / x）から角度（ラジアン、−π/2〜π/2）を返します。象限の区別が要る向きの計算には、[`atan2`](atan2.md) を使います。

!!! tip "ポイント"
    - 向きや方向には `atan2` のほうが安全。
    - 結果は −π/2〜π/2。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atan {#atan}

```cpp
double atan(double x);
float atan(float x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 傾き（y / x） |

- 戻り値: 角度（ラジアン）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::atan(1.0));  // 傾き 1 は 45 度（π/4）
}
```

```text title="実行結果"
0.7854
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 坂道の傾きから角度を出す | `std::atan(rise / run)` |

## よくあるミス

??? failure "向きの計算に使う"
    `x = 0` で割り算が壊れ、象限も区別できません。`atan2` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atan2`](atan2.md) | 2 つの値から角度 |
| [`tan`](tan.md) | 逆関数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 傾きから角度
    - [x] 向きには atan2
    - [x] 結果はラジアン

## 関連ページ

- [cpprefjp: std::atan](https://cpprefjp.github.io/reference/cmath/atan.html)
- [cppreference: std::atan](https://en.cppreference.com/w/cpp/numeric/math/atan)
