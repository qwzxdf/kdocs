---
title: std::nearbyint
summary: "現在の丸めモード（既定は偶数丸め）で整数値にする。"
order: 39
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::nearbyint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::nearbyint` は、**現在の丸めモードに従って整数値にする**関数です。既定のモードでは**偶数丸め**（2.5 → 2、3.5 → 4）になります。統計的な偏りを減らしたいときに向きます。

!!! tip "ポイント"
    - 既定は偶数丸め（銀行家丸め）。`round` は半分を 0 から遠い側へ。
    - 丸めモードは `<cfenv>` で変えられる。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nearbyint {#nearbyint}

```cpp
double nearbyint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 丸める値 |

- 戻り値: 丸めた値（小数型）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::nearbyint(2.5), std::nearbyint(3.5));
}
```

```text title="実行結果"
2 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 偏りなく丸めたい統計処理 | `std::nearbyint(v)` |

## よくあるミス

??? failure "round と同じだと思う"
    半分のときの丸め方が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`round`](round.md) | 半分は 0 から遠い側へ |
| [`lround`](lround.md) | 整数型で返す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 偶数丸め
    - [x] 半分で `round` と違う
    - [x] 丸めモードに従う

## 関連ページ

- [cpprefjp: std::nearbyint](https://cpprefjp.github.io/reference/cmath/nearbyint.html)
- [cppreference: std::nearbyint](https://en.cppreference.com/w/cpp/numeric/math/nearbyint)
