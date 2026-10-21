---
title: std::ceil
summary: "小数を切り上げる（大きいほうの整数にする）。"
order: 11
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ceil

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <cmath>`
</div>

`std::ceil` は、**小数を正の無限大の方向へ切り上げて、整数値にする**関数です。必要なページ数、グリッドの分割数など、「足りない分を 1 つ増やす」計算に使います。

!!! tip "ポイント"
    - `ceil(a / b)` で「割り切れなければ 1 つ増やす」。
    - 整数どうしの切り上げ割り算は `(a + b - 1) / b`。
    - 戻り値は小数型。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ceil {#ceil}

```cpp
float ceil(float x);
```

- x 以上で一番小さい整数（切り上げ）

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::ceil(1.2), std::ceil(-1.2));
}
```

```text title="実行結果"
2 -1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ページ数・グリッド数の計算 | `std::ceil(count / static_cast<float>(per_page))` |

## よくあるミス

??? failure "整数どうしの割り算に ceil を使う"
    整数の割り算は先に切り捨てられるので、`ceil` に届く前に失われます。`(a + b - 1) / b` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨て |
| [`round`](round.md) | 四捨五入 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きいほうへ切り上げ
    - [x] 足りない分を増やす計算
    - [x] 整数の割り算は別の書き方

## 関連ページ

- [cpprefjp: std::ceil](https://cpprefjp.github.io/reference/cmath/ceil.html)
- [cppreference: std::ceil](https://en.cppreference.com/w/cpp/numeric/math/ceil)
