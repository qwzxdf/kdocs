---
title: std::strong_ordering
summary: "「等しいものは区別できない」比較結果（整数など）。less / equal / greater の 3 値。"
order: 2
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::strong_ordering

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

2 つの値を比べた結果は、「小さい」「等しい」「大きい」のどれかです。C++20 の三方比較演算子 `<=>` は、その結果を 1 つの値で返します。`std::strong_ordering` は、<strong>その結果を表す型</strong>で、`less`、`equal`、`greater` の 3 値 を持ちます。

!!! tip "ポイント"
    - `std::strong_ordering::less`、`equal`、`greater` の 3 つの値
    - 等しい値は、完全に区別できない（置き換えられる）
    - 整数、文字列、`std::string` などの `<=>` の結果
    - `weak_ordering` と `partial_ordering` に暗黙に変換できる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strong_ordering {#strong_ordering}

<span class="ver ver-20">C++20</span>

```cpp
class strong_ordering {
 public:
  static const strong_ordering less;
  static const strong_ordering equal;
  static const strong_ordering greater;
};
```

値が等しい（`equal`）とき、それらを区別できません。どちらを使っても結果が変わらない、置き換え可能な関係です。整数や文字列がこれにあたります。

自作のクラスで `auto operator<=>(const T&) const = default;` と書くと、メンバー変数の型の `<=>` に応じて、`strong_ordering` などの型が決まります。

型の強さは、`strong_ordering` > `weak_ordering` > `partial_ordering` の順です。強い型から弱い型へは暗黙に変換できます。比較した結果は、`0` との比較演算子（`r < 0`、`r == 0`）で判定でき、`std::is_lt(r)` のような名前つきの関数でも判定できます。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  auto r = 1 <=> 2;
  std::println("1 <=> 2 は less    : {}", r == std::strong_ordering::less);
  std::println("2 <=> 2 は equal   : {}", (2 <=> 2) == std::strong_ordering::equal);
  std::println("3 <=> 2 は greater : {}", (3 <=> 2) == std::strong_ordering::greater);
}
```

```text title="実行結果"
1 <=> 2 は less    : true
2 <=> 2 は equal   : true
3 <=> 2 は greater : true
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
    - [x] `strong_ordering` は`<=>` の結果を表す型
    - [x] 強い型から弱い型へ暗黙に変換できる
    - [x] `0` との比較か `is_lt` などで判定する

## 関連ページ

- [cpprefjp: std::strong_ordering](https://cpprefjp.github.io/reference/compare/strong_ordering.html)
- [cppreference: std::strong_ordering](https://en.cppreference.com/w/cpp/utility/compare/strong_ordering)
