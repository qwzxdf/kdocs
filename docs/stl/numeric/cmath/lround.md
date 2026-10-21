---
title: std::lround
summary: "小数を四捨五入して、整数型（long）で返す。"
order: 38
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lround

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::lround` は、**小数を四捨五入して、`long` の整数として返す**関数です。[`round`](round.md) は小数型で返しますが、こちらは最初から整数型なので、ピクセル座標やインデックスにそのまま使えます。半分は 0 から遠いほうへ丸めます。

!!! tip "ポイント"
    - `std::lround(x)` で `long`、`std::llround(x)` で `long long`。
    - `int` に代入するときは範囲に注意。
    - 半分は 0 から遠いほうへ。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lround {#lround}

```cpp
long lround(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 丸める値 |

- 戻り値: 四捨五入した整数
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::lround(2.5), std::lround(-2.5), std::lround(2.4));
}
```

```text title="実行結果"
3 -3 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワールド座標を、整数のピクセル位置にする | `int px = static_cast<int>(std::lround(x));` |

## よくあるミス

??? failure "値が long に収まらない"
    範囲外は未定義の結果です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`round`](round.md) | 小数型で返す |
| [`nearbyint`](nearbyint.md) | 偶数丸め |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 四捨五入して整数型で返す
    - [x] ピクセル位置に便利
    - [x] 半分は 0 から遠い側

## 関連ページ

- [cpprefjp: std::lround](https://cpprefjp.github.io/reference/cmath/lround.html)
- [cppreference: std::lround](https://en.cppreference.com/w/cpp/numeric/math/lround)
