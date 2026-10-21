---
title: std::piecewise_constant_distribution
summary: "区間ごとに重みを決めた、連続値の乱数。"
order: 28
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::piecewise_constant_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::piecewise_constant_distribution` は、**範囲をいくつかの区間に分けて、区間ごとの重みで出やすさを決める**連続値の乱数です。`discrete_distribution` が「何番目か」を選ぶのに対し、こちらは区間の**中の小数**を出します。「0〜10 は 1、10〜20 は 3 の重み」のような階段状の確率になります。

!!! tip "ポイント"
    - 区間の境界 `b0, b1, b2, …` と、区間ごとの重み `w0, w1, …` を渡す。
    - 同じ区間の中では、どの値も同じ確率。
    - 連続的に変化する重みなら [`piecewise_linear_distribution`](piecewise_linear_distribution.md)。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::piecewise_constant_distribution {#piecewise_constant_distribution}

```cpp
template <class InputIt1, class InputIt2>
piecewise_constant_distribution(InputIt1 first_b, InputIt1 last_b, InputIt2 first_w);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first_b, last_b` | イテレータ | 区間の境界の並び |
| `first_w` | イテレータ | 区間ごとの重みの並び（境界の数 − 1 個） |

- 戻り値: `operator()` で小数を 1 つ返す
- 計算量: O(log n)

```cpp
#include <print>
#include <random>
#include <vector>

int main() {
  std::vector<double> bounds = {0.0, 10.0, 20.0};
  std::vector<double> weights = {1.0, 3.0};  // 10〜20 が 3 倍出やすい

  std::piecewise_constant_distribution<double> d(bounds.begin(), bounds.end(), weights.begin());
  std::println("{}", d.intervals());
}
```

```text title="実行結果"
[0, 10, 20]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ステージの難易度に応じた、敵の強さの分布 | 区間ごとの重みで階段状に |
| 時間帯ごとの出現頻度 | 区間 = 時間帯、重み = 頻度 |

## よくあるミス

??? failure "重みの数を間違える"
    重みは「境界の数 − 1」個です。同じ数を渡すと範囲外を読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`discrete_distribution`](discrete_distribution.md) | 添字を選ぶ |
| [`piecewise_linear_distribution`](piecewise_linear_distribution.md) | 区間の中で重みが直線的に変わる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 区間ごとの重みで連続値を出す
    - [x] 階段状の確率
    - [x] 重みは境界より 1 つ少ない

## 関連ページ

- [cpprefjp: std::piecewise_constant_distribution](https://cpprefjp.github.io/reference/random/piecewise_constant_distribution.html)
- [cppreference: std::piecewise_constant_distribution](https://en.cppreference.com/w/cpp/numeric/random/piecewise_constant_distribution)
