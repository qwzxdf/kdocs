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

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

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

## ratio の計算・比較・SI 接頭辞

| 名前 | 何をする |
| --- | --- |
| [`std::centi`](ratio/centi.md) | SI 接頭辞「centi」（100 分の 1）を表す `ratio` の別名。 |
| [`std::deca`](ratio/deca.md) | SI 接頭辞「deca」（10 倍）を表す `ratio` の別名。 |
| [`std::deci`](ratio/deci.md) | SI 接頭辞「deci」（10 分の 1）を表す `ratio` の別名。 |
| [`std::exa`](ratio/exa.md) | SI 接頭辞「exa」（100 京倍）を表す `ratio` の別名。 |
| [`std::giga`](ratio/giga.md) | SI 接頭辞「giga」（10 億倍）を表す `ratio` の別名。 |
| [`std::hecto`](ratio/hecto.md) | SI 接頭辞「hecto」（100 倍）を表す `ratio` の別名。 |
| [`std::kilo`](ratio/kilo.md) | SI 接頭辞「kilo」（1000 倍）を表す `ratio` の別名。 |
| [`std::mega`](ratio/mega.md) | SI 接頭辞「mega」（100 万倍）を表す `ratio` の別名。 |
| [`std::micro`](ratio/micro.md) | SI 接頭辞「micro」（100 万分の 1）を表す `ratio` の別名。 |
| [`std::milli`](ratio/milli.md) | SI 接頭辞「milli」（1000 分の 1）を表す `ratio` の別名。 |
| [`std::nano`](ratio/nano.md) | SI 接頭辞「nano」（10 億分の 1）を表す `ratio` の別名。 |
| [`std::peta`](ratio/peta.md) | SI 接頭辞「peta」（1000 兆倍）を表す `ratio` の別名。 |
| [`std::ratio_add`](ratio/ratio_add.md) | 2 つの `ratio` の足し算を、コンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_divide`](ratio/ratio_divide.md) | 2 つの `ratio` の割り算を、コンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_equal`](ratio/ratio_equal.md) | 2 つの `ratio` を `==` で比べる（コンパイル時）。 |
| [`std::ratio_greater`](ratio/ratio_greater.md) | 2 つの `ratio` を `>` で比べる（コンパイル時）。 |
| [`std::ratio_greater_equal`](ratio/ratio_greater_equal.md) | 2 つの `ratio` を `>=` で比べる（コンパイル時）。 |
| [`std::ratio_less`](ratio/ratio_less.md) | 2 つの `ratio` を `<` で比べる（コンパイル時）。 |
| [`std::ratio_less_equal`](ratio/ratio_less_equal.md) | 2 つの `ratio` を `<=` で比べる（コンパイル時）。 |
| [`std::ratio_multiply`](ratio/ratio_multiply.md) | 2 つの `ratio` のかけ算を、コンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_not_equal`](ratio/ratio_not_equal.md) | 2 つの `ratio` を `!=` で比べる（コンパイル時）。 |
| [`std::ratio_subtract`](ratio/ratio_subtract.md) | 2 つの `ratio` の引き算を、コンパイル時に計算して `ratio` で返す。 |
| [`std::tera`](ratio/tera.md) | SI 接頭辞「tera」（1 兆倍）を表す `ratio` の別名。 |

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
