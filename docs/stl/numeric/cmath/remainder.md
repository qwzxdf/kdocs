---
title: std::remainder
summary: "小数の余り。商を四捨五入で決めるので、負になることがある。"
order: 29
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::remainder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::remainder(x, y)` は、**`x / y` の商を最も近い整数に丸めて、その余りを返す**関数です。[`fmod`](fmod.md) は商を切り捨てるので余りが 0 以上ですが、`remainder` は余りが −y/2〜y/2 の範囲になります。角度の差を「−π〜π」にそろえるのに便利です。

!!! tip "ポイント"
    - `remainder(5, 3)` は −1（商 1.667 を 2 に丸めて、5 − 3×2）。
    - 角度差の正規化: `remainder(a - b, 2π)` で −π〜π。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remainder {#remainder}

```cpp
double remainder(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 割られる数 |
| `y` | 浮動小数点 | 割る数 |

- 戻り値: `x - y * round(x / y)`（偶数丸め）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::remainder(5.0, 3.0), std::fmod(5.0, 3.0));
}
```

```text title="実行結果"
-1 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの角度の差を −π〜π に収める | `std::remainder(a - b, 2 * pi)` |

## よくあるミス

??? failure "fmod と同じと思う"
    結果が違います。`remainder` は負になりえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmod`](fmod.md) | 商を切り捨てる余り |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 商を丸めた余り
    - [x] 範囲は −y/2〜y/2
    - [x] 角度差の正規化に

## 関連ページ

- [cpprefjp: std::remainder](https://cpprefjp.github.io/reference/cmath/remainder.html)
- [cppreference: std::remainder](https://en.cppreference.com/w/cpp/numeric/math/remainder)
