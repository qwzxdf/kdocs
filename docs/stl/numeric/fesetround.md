---
title: std::fesetround
summary: "浮動小数点の丸め方（最近接・切り上げ・切り捨てなど）を切り替える。"
order: 50
tags:
  - 数値
---

# std::fesetround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

`std::fesetround` は、**浮動小数点の計算の丸め方（最も近い値、切り上げ、切り捨て、0 に向かう）を切り替える**関数です。区間演算（誤差の上限・下限を求める）のように、丸めの向きが結果に影響する数値計算で使います。ゲームではほとんど使いません。

!!! tip "ポイント"
    - 丸めは `FE_TONEAREST`（既定）、`FE_UPWARD`、`FE_DOWNWARD`、`FE_TOWARDZERO`。
    - `<cfenv>` を include し、`#pragma STDC FENV_ACCESS ON` が本来必要。
    - `nearbyint` などの丸めの結果にも影響する。

## 関数の詳しい説明

### std::fesetround {#fesetround}

```cpp
int fesetround(int mode);
int fegetround();
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mode` | `int` | `FE_TONEAREST` など |

- 戻り値: 成功なら 0
- 計算量: O(1)

```cpp
#include <cfenv>
#include <cmath>
#include <print>

int main() {
  std::fesetround(FE_TOWARDZERO);   // 0 に向かって丸める
  std::println("{}", std::nearbyint(2.7));
  std::fesetround(FE_TONEAREST);    // 元に戻す
  std::println("{}", std::nearbyint(2.7));
}
```

```text title="実行結果"
2
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 区間演算で、誤差の上限・下限を計算する | `FE_UPWARD` と `FE_DOWNWARD` |

## よくあるミス

??? failure "丸めモードを戻し忘れる"
    以降のすべての計算に影響します。必ず戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nearbyint`](cmath/nearbyint.md) | 丸めモードに従う丸め |
| [`round`](cmath/round.md) | 固定の丸め |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 丸め方を切り替える
    - [x] 戻し忘れに注意
    - [x] ゲームではほぼ使わない

## 関連ページ

- [cpprefjp: std::fesetround](https://cpprefjp.github.io/reference/cfenv/fesetround.html)
- [cppreference: std::fesetround](https://en.cppreference.com/w/cpp/numeric/fenv/feround)
