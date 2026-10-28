---
title: std::weak_ordering
summary: "「等しいが、区別はできる」場合を含む比較結果（大文字小文字を無視した比較など）。"
order: 3
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::weak_ordering

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

2 つの値を比べた結果は、「小さい」「等しい」「大きい」のどれかです。C++20 の三方比較演算子 `<=>` は、その結果を 1 つの値で返します。`std::weak_ordering` は、<strong>その結果を表す型</strong>で、`less`、`equivalent`、`greater` の 3 値 を持ちます。

!!! tip "ポイント"
    - `std::weak_ordering::less`、`equivalent`、`greater` の 3 つの値
    - 「等価」な値でも、区別がつくことがある（大文字小文字を無視した比較など）
    - `partial_ordering` に暗黙に変換できる
    - `strong_ordering` からは変換できない（弱くなるだけ）

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::weak_ordering {#weak_ordering}

<span class="ver ver-20">C++20</span>

```cpp
class weak_ordering {
 public:
  static const weak_ordering less;
  static const weak_ordering equivalent;
  static const weak_ordering greater;
};
```

等価（`equivalent`）な値を置き換え可能とは限りません。たとえば、大文字小文字を区別しない文字列比較で、"Abc" と "abc" は等価ですが、同じ文字列ではありません。

並べ替えのアルゴリズムが要求する「厳密な弱順序」に対応する型です。

型の強さは、`strong_ordering` > `weak_ordering` > `partial_ordering` の順です。強い型から弱い型へは暗黙に変換できます。比較した結果は、`0` との比較演算子（`r < 0`、`r == 0`）で判定でき、`std::is_lt(r)` のような名前つきの関数でも判定できます。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  std::weak_ordering r = std::weak_ordering::equivalent;
  std::println("equivalent は等しい扱い : {}", r == 0);
  std::println("strong から変換できる  : {}", std::weak_ordering(std::strong_ordering::less) == std::weak_ordering::less);
}
```

```text title="実行結果"
equivalent は等しい扱い : true
strong から変換できる  : true
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
    - [x] `weak_ordering` は`<=>` の結果を表す型
    - [x] 強い型から弱い型へ暗黙に変換できる
    - [x] `0` との比較か `is_lt` などで判定する

## 関連ページ

- [cpprefjp: std::weak_ordering](https://cpprefjp.github.io/reference/compare/weak_ordering.html)
- [cppreference: std::weak_ordering](https://en.cppreference.com/w/cpp/utility/compare/weak_ordering)
