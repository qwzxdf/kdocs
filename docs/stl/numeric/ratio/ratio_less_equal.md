---
title: std::ratio_less_equal
summary: "2 つの `ratio` を `<=` で比べる（コンパイル時）。"
order: 900
tags:
  - 数値
---

# std::ratio_less_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

単位の大きさを比べたいとき、分数の通分をして比べる必要はありません。`ratio_less_equal<R1, R2>::value` が、`R1 <= R2` をコンパイル時に計算します。`static_assert` と組み合わせると、単位の前提をコンパイル時に確認できます。

!!! tip "ポイント"
    - `::value` が `bool` の定数。
    - 約分されていなくても、値として比べられる（`1/2` と `2/4` は等しい）。
    - `_v` 版（C++17）もある。

!!! info "このページを読む前に"
    [`std::ratio`](../ratio.md) を先に読んでください。

## 関数の詳しい説明

### std::ratio_less_equal {#ratio_less_equal}

```cpp
template <class R1, class R2>
struct ratio_less_equal : bool_constant</* R1 <= R2 */> {};
template <class R1, class R2>
inline constexpr bool ratio_less_equal_v = ratio_less_equal<R1, R2>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R1, R2` | ratio | 比べる 2 つの `ratio` |

- 戻り値: `R1 <= R2` なら `true`（以下か）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  std::println("{}", std::ratio_less_equal<std::ratio<1, 2>, std::ratio<1, 2>>::value);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 単位の前提をコンパイル時に確認 | `static_assert(std::ratio_less_equal_v<A, B>);` |

## よくあるミス

??? failure "文字列として比べたつもりになる"
    約分前の形が違っても、値が同じなら等しいと判定されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数の型 |
| [`ratio_add`](ratio_add.md) | 足し算 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ratio を <= で比べる（コンパイル時）
    - [x] ::value が bool
    - [x] static_assert に使える

## 関連ページ

- [cpprefjp: std::ratio_less_equal](https://cpprefjp.github.io/reference/ratio/ratio_less_equal.html)
- [cppreference: std::ratio_less_equal](https://en.cppreference.com/w/cpp/numeric/ratio/ratio_equal)
