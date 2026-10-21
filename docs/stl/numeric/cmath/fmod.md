---
title: std::fmod
summary: "小数の割り算の余りを求める。"
order: 16
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmod

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::fmod(x, y)` は、**小数の割り算の余り**を求める関数です。角度を 0〜2π に収める、時間をループさせる、といった「周期で巻き戻す」処理に使います。**結果の符号は x と同じ**です（負の x では負の余り）。

!!! tip "ポイント"
    - `%` は整数用。小数には `fmod`。
    - 結果の符号は x に従う。負を 0〜y に収めたいなら加工が必要。
    - 角度の正規化に使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmod {#fmod}

```cpp
float fmod(float x, float y);
```

- 小数の割り算の余り（符号は x と同じ）。角度を 0〜360 に戻す、アニメーションをループさせるのに使います

```cpp
#include <cmath>
#include <print>

int main() {
  float angle = 725.0f;
  std::println("{}", std::fmod(angle, 360.0f));
  float t = 2.3f;
  std::println("{:.1f}", std::fmod(t, 1.0f));  // 1 秒でループするアニメーションの位置
}
```

```text title="実行結果"
5
0.3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 角度を 0〜360 に収める | `std::fmod(angle, 360.0f)` |
| 時間をループさせる | `std::fmod(time, period)` |

## よくあるミス

??? failure "負の値で正の余りを期待する"
    `fmod(-1, 3)` は −1 です。0〜y にするには `r < 0 ? r + y : r`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remainder`](remainder.md) | 符号が違う余り |
| `operator%` | 整数用 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数の余り
    - [x] 符号は x と同じ
    - [x] 周期の巻き戻しに

## 関連ページ

- [cpprefjp: std::fmod](https://cpprefjp.github.io/reference/cmath/fmod.html)
- [cppreference: std::fmod](https://en.cppreference.com/w/cpp/numeric/math/fmod)
