---
title: std::ratio
summary: "分数（1/3 など）を、型としてコンパイル時に表す。chrono の単位の土台。"
order: 41
tags:
  - 数値
---

# std::ratio

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

`std::ratio<分子, 分母>` は、**分数をコンパイル時の型として表す**クラスです。`std::chrono::duration` の単位（ミリ秒は `ratio<1, 1000>`）の土台になっています。分数の計算は `std::ratio_add` などの型の演算で行い、結果の分子・分母は `num` と `den` で取れます。`std::milli`、`std::kilo` などの別名もあります。

!!! tip "ポイント"
    - 計算は**コンパイル時**。実行時の分数には使えない。
    - 約分された形で保存される（`ratio<2, 4>` は `1/2`）。
    - `std::milli` は `ratio<1, 1000>`、`std::kilo` は `ratio<1000>`。

## 関数の詳しい説明

### std::ratio {#ratio}

```cpp
template <std::intmax_t Num, std::intmax_t Denom = 1>
struct ratio {
  static constexpr std::intmax_t num;
  static constexpr std::intmax_t den;
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `Num` | 整数 | 分子 |  |
| `Denom` | 整数 | 分母 | 1 |

- 戻り値: （型）。`num` と `den` が約分後の分子・分母
- 計算量: コンパイル時

```cpp
#include <print>
#include <ratio>

int main() {
  using Sum = std::ratio_add<std::ratio<1, 3>, std::ratio<1, 6>>;  // 1/3 + 1/6
  std::println("{}/{}", Sum::num, Sum::den);                        // 約分されて 1/2
}
```

```text title="実行結果"
1/2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| chrono の単位の仕組みを理解する | `std::chrono::duration<double, std::ratio<1, 1000>>` は ms |

## よくあるミス

??? failure "実行時の分数に使う"
    型なのでコンパイル時に決まった値だけです。実行時なら、自作の分数クラスを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::duration`](../utilities/chrono/duration.md) | 単位に使っている |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 分数をコンパイル時の型にする
    - [x] 約分される
    - [x] chrono の単位の土台

## 関連ページ

- [cpprefjp: std::ratio](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::ratio](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
