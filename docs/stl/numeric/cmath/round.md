---
title: std::round
summary: "小数を四捨五入する（半分は 0 から遠いほうへ）。"
order: 10
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::round

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <cmath>`
</div>

`std::round` は、**小数を最も近い整数にする**関数です。ちょうど半分のときは、**0 から遠いほうへ**丸めます（2.5 → 3、−2.5 → −3）。

!!! tip "ポイント"
    - ちょうど半分は 0 から遠い側へ（**偶数丸めではない**。`chrono::round` とは違う）。
    - 戻り値は小数型。
    - `std::lround` なら、整数型で返る。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::round {#round}

```cpp
float round(float x);
```

- 四捨五入（0.5 は 0 から遠いほうへ）。`std::lround` は long で返します

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::round(2.5), std::round(-2.5), std::round(2.4));
}
```

```text title="実行結果"
3 -3 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ピクセル位置を整数にそろえる | `std::round(x)` |

## よくあるミス

??? failure "偶数丸めだと思う"
    `std::round(2.5)` は 3 です（銀行家丸めではない）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨て |
| [`ceil`](ceil.md) | 切り上げ |
| [`std::chrono::round`](../../utilities/chrono/floor.md) | 時間の丸め（偶数へ） |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 四捨五入
    - [x] 半分は 0 から遠いほうへ
    - [x] 戻り値は小数型

## 関連ページ

- [cpprefjp: std::round](https://cpprefjp.github.io/reference/cmath/round.html)
- [cppreference: std::round](https://en.cppreference.com/w/cpp/numeric/math/round)
