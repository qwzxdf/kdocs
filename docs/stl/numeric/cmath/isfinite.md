---
title: std::isfinite
summary: "値が有限の数（NaN でも無限大でもない）かを調べる。"
order: 28
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isfinite

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::isfinite` は、**値が有限の数（NaN でも無限大でもない）か**を調べる関数です。計算結果が正常かを、まとめて確かめるのに便利です。

!!! tip "ポイント"
    - `isnan` と `isinf` の両方を一度に調べる。
    - デバッグで `assert(std::isfinite(v))`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isfinite {#isfinite}

```cpp
bool isfinite(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 調べる値 |

- 戻り値: 有限の数なら `true`
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  double inf = 1e308 * 10;
  std::println("{} {}", std::isfinite(1.5), std::isfinite(inf));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 座標や速度が壊れていないか、デバッグで確認する | `assert(std::isfinite(pos.x))` |

## よくあるミス

??? failure "整数に使う"
    整数は常に有限です。浮動小数点用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN か |
| [`isinf`](isinf.md) | 無限大か |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 有限の数か
    - [x] NaN と無限大を除く
    - [x] デバッグの検査に

## 関連ページ

- [cpprefjp: std::isfinite](https://cpprefjp.github.io/reference/cmath/isfinite.html)
- [cppreference: std::isfinite](https://en.cppreference.com/w/cpp/numeric/math/isfinite)
