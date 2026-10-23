---
title: std::partial_ordering
summary: "「比べられない」場合がある比較結果（NaN を含む小数）。"
order: 4
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::partial_ordering

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

2 つの値を比べた結果は、「小さい」「等しい」「大きい」のどれかです。C++20 の三方比較演算子 `<=>` は、その結果を 1 つの値で返します。`std::partial_ordering` は、<strong>その結果を表す型</strong>で、`less`、`equivalent`、`greater`、`unordered` の 4 値 を持ちます。

!!! tip "ポイント"
    - `std::partial_ordering` の 4 つの値: `less`、`equivalent`、`greater`、`unordered`
    - `unordered` は、NaN のように比べられない場合
    - `float` / `double` の `<=>` の結果
    - `unordered` では、`<`・`>`・`==` がすべて偽になる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::partial_ordering {#partial_ordering}

<span class="ver ver-20">C++20</span>

```cpp
class partial_ordering {
 public:
  static const partial_ordering less;
  static const partial_ordering equivalent;
  static const partial_ordering greater;
  static const partial_ordering unordered;
};
```

浮動小数点数に NaN が含まれると、どちらが大きいとも小さいとも言えません。それを表すのが `unordered` です。`unordered` のとき、`r < 0`、`r > 0`、`r == 0` はすべて `false` になります。

3 つの順序型のうち、最も弱い（制約が少ない）型です。

型の強さは、`strong_ordering` > `weak_ordering` > `partial_ordering` の順です。強い型から弱い型へは暗黙に変換できます。比較した結果は、`0` との比較演算子（`r < 0`、`r == 0`）で判定でき、`std::is_lt(r)` のような名前つきの関数でも判定できます。

## 実際に動かしてみる

```cpp
#include <compare>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("1.0 <=> 2.0 は less     : {}", (1.0 <=> 2.0) == std::partial_ordering::less);
  std::println("1.0 <=> NaN は unordered: {}", (1.0 <=> nan) == std::partial_ordering::unordered);
}
```

```text title="実行結果"
1.0 <=> 2.0 は less     : true
1.0 <=> NaN は unordered: true
```

## ゲームでの使いどころ

自作のクラスに比較演算子をまとめて定義します。

```cpp
struct Version {
  int major, minor;
  auto operator<=>(const Version&) const = default;   // すべての比較演算子が自動で揃う
};
```

## よくあるミス

??? failure "`unordered` を考えず、NaN の比較で誤る"
    `partial_ordering` では、`unordered` のとき `<` も `>` も `==` も偽です。

??? failure "弱い型から強い型へ代入する"
    強い型から弱い型への変換だけが許されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_lt`](is_lt.md) | 結果を `bool` で判定する |
| [`three_way_comparable`](three_way_comparable.md) | `<=>` が使えるか |
| [`compare_three_way`](compare_three_way.md) | `<=>` の関数オブジェクト |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `partial_ordering` は`<=>` の結果を表す型
    - [x] 強い型から弱い型へ暗黙に変換できる
    - [x] `0` との比較か `is_lt` などで判定する

## 関連ページ

- [cpprefjp: std::partial_ordering](https://cpprefjp.github.io/reference/compare/partial_ordering.html)
- [cppreference: std::partial_ordering](https://en.cppreference.com/w/cpp/utility/compare/partial_ordering)
