---
title: std::copysign
summary: "大きさは x、符号は y の値を作る。"
order: 25
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::copysign

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::copysign(x, y)` は、**x の大きさ（絶対値）に、y の符号を付けた値**を返す関数です。向きだけを引き継いで大きさを変えたい、というときに使います。

!!! tip "ポイント"
    - `copysign(5, -1)` は −5。
    - `y` が 0 でも、`-0.0` なら負の符号。
    - 符号の判定は `signbit`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::copysign {#copysign}

```cpp
float copysign(float magnitude, float sign);
```

- `magnitude` の大きさで、符号だけ `sign` から取った値

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::copysign(5.0, -1.0), std::copysign(-5.0, 1.0));
}
```

```text title="実行結果"
-5 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 速度の大きさを保ったまま、向きだけ反転する | `std::copysign(speed, dir)` |

## よくあるミス

??? failure "y = 0 の符号を期待する"
    `+0.0` は正、`-0.0` は負と扱われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](abs.md) | 絶対値 |
| [`signbit`](signbit.md) | 符号を調べる |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の大きさ、y の符号
    - [x] `signbit` は符号の判定
    - [x] 向きの引き継ぎに

## 関連ページ

- [cpprefjp: std::copysign](https://cpprefjp.github.io/reference/cmath/copysign.html)
- [cppreference: std::copysign](https://en.cppreference.com/w/cpp/numeric/math/copysign)
