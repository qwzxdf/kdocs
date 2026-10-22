---
title: std::float_round_style
summary: "浮動小数点の丸めの方向を表す列挙型。"
order: 900
tags:
  - 数値
---

# std::float_round_style

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <limits>`
</div>

浮動小数点の演算が、結果を丸めるときの方向を表す列挙型です。`std::numeric_limits<T>::round_style` の型で、多くの環境は `round_to_nearest`（最も近い値へ）です。

!!! tip "ポイント"
    - `numeric_limits` のメンバが返す型。
    - 値: round_indeterminate / round_toward_zero / round_to_nearest / round_toward_infinity / round_toward_neg_infinity。
    - ふつうは `numeric_limits` 経由で比べる。

!!! info "このページを読む前に"
    [`std::numeric_limits`](limits.md) を先に読んでください。

## 関数の詳しい説明

### std::float_round_style {#float_round_style}

```cpp
enum float_round_style {
  /* round_indeterminate / round_toward_zero / round_to_nearest / round_toward_infinity / round_toward_neg_infinity */
};
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <limits>
#include <print>

int main() {
  std::println("{}", std::numeric_limits<float>::round_style == std::round_to_nearest);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 環境の浮動小数点の性質を調べる | `std::numeric_limits<float>::round_style` |

## よくあるミス

??? failure "実行時に変わると思う"
    この値は型の性質で、`fesetround` で変えた丸めは反映されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型の性質 |
| [`fesetround`](fesetround.md) | 実行時の丸めモード |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 丸めの方向を表す列挙型
    - [x] numeric_limits のメンバが返す
    - [x] ふつうは意識しない

## 関連ページ

- [cpprefjp: std::float_round_style](https://cpprefjp.github.io/reference/limits/float_round_style.html)
- [cppreference: std::float_round_style](https://en.cppreference.com/w/cpp/types/numeric_limits/float_round_style)
