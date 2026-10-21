---
title: std::atan2
summary: "x と y から、向きの角度（ラジアン）を求める。"
order: 8
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atan2

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::atan2(y, x)` は、**x と y の値から、その向きの角度（ラジアン、−π〜π）を求める**関数です。キャラクターの向き、ターゲットへの方向を調べるときに使います。`atan(y / x)` と違い、**4 つの象限を区別でき、x = 0 でも安全**です。

!!! tip "ポイント"
    - 引数の順番は **`(y, x)`**。`(x, y)` ではない。
    - 結果は −π〜π（ラジアン）。
    - 度にしたいなら `× 180 / π`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atan2 {#atan2}

```cpp
float atan2(float y, float x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | 浮動小数点 | 向きの y 成分（**先に y**） |
| `x` | 浮動小数点 | 向きの x 成分 |

- 戻り値: -π〜π のラジアン。右が 0、上（y が正）が π/2
- `atan(y / x)` と違って、4 方向すべてを正しく区別でき、x が 0 でも割り算エラーになりません

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f} {:.4f}", std::atan2(1.0, 1.0), std::atan2(1.0, 0.0));  // (y, x) の順
}
```

```text title="実行結果"
0.7854 1.5708
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ターゲットの方向を向く | `angle = std::atan2(target.y - pos.y, target.x - pos.x)` |

## よくあるミス

??? failure "引数を (x, y) の順にする"
    `atan2(y, x)` です。逆にすると 90 度ずれます。

??? failure "atan(y / x) で代用する"
    x が 0 のとき割り算で壊れ、象限も区別できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sin`](sin.md) | 角度から向き |
| [`atan`](atan.md) | 傾きから角度 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 向きの角度を求める
    - [x] 引数は (y, x)
    - [x] 結果は −π〜π

## 関連ページ

- [cpprefjp: std::atan2](https://cpprefjp.github.io/reference/cmath/atan2.html)
- [cppreference: std::atan2](https://en.cppreference.com/w/cpp/numeric/math/atan2)
