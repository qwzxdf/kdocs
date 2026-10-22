---
title: std::isnormal
summary: "正規数（0・無限大・NaN・非正規数以外）かを判定する。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isnormal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

計算が極端に小さい値（非正規数）になると、精度が落ちて遅くなります。`isnormal` は、通常の精度で扱える数かを調べます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isnormal {#isnormal}

```cpp
bool isnormal(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: 正規数なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::isnormal(1.0), std::isnormal(0.0));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 異常な値が計算に混ざっていないか検査する |

## よくあるミス

??? failure "0 を正規数と思う"
    0 は正規数ではありません。`false` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fpclassify`](fpclassify.md) | 種類を分類する |
| [`isfinite`](isfinite.md) | 有限かを判定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規数（0・無限大・NaN・非正規数以外）かを判定する
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::isnormal](https://cpprefjp.github.io/reference/cmath/isnormal.html)
- [cppreference: std::isnormal](https://en.cppreference.com/w/cpp/numeric/math/isnormal)
