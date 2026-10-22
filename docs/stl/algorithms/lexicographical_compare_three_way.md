---
title: std::lexicographical_compare_three_way
summary: "2 つの範囲を辞書順に比べて、順序（strong_ordering など）を返す。"
order: 900
tags:
  - アルゴリズム
---

# std::lexicographical_compare_three_way

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

辞書順の比較は `lexicographical_compare` で「小さいかどうか」が分かります。でも「等しい」「大きい」まで 1 回で知りたいときは、3 通りを返す `lexicographical_compare_three_way` が使えます。`<=>`（宇宙船演算子）の範囲版です。

!!! tip "ポイント"
    - 戻り値は `std::strong_ordering` などの順序型（`<` `==` `>` と 0 を比べて使う）。
    - 要素の比較は `<=>` が使われる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::lexicographical_compare_three_way {#lexicographical_compare_three_way}

```cpp
template <class InputIt1, class InputIt2>
auto lexicographical_compare_three_way(InputIt1 first1, InputIt1 last1, InputIt2 first2, InputIt2 last2);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first1, last1` | イテレータ | 1 つ目の範囲 |
| `first2, last2` | イテレータ | 2 つ目の範囲 |
| `comp` | 関数 | 省略可。要素を比べる関数（順序型を返す） |

- 戻り値: 順序型（`std::strong_ordering` など）。1 つ目が小さければ負、等しければ 0、大きければ正と比べられる
- 計算量: 線形（最大でも短いほうの長さの回数だけ比較）


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <compare>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3};
  std::vector<int> b = {1, 2, 4};
  auto r = std::lexicographical_compare_three_way(a.begin(), a.end(), b.begin(), b.end());
  std::println("a < b: {}", r < 0);
  std::println("a == b: {}", r == 0);
}
```

```text title="実行結果"
a < b: true
a == b: false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バージョン番号の大小を 3 通りで判定 | `std::lexicographical_compare_three_way(a.begin(), a.end(), b.begin(), b.end()) < 0` |

## よくあるミス

??? failure "順序型を整数と思う"
    戻り値は `int` ではなく `std::strong_ordering` です。`0` との比較（`== 0`、`< 0`）だけが書けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lexicographical_compare`](lexicographical_compare.md) | 小さいかどうかの `bool` だけ返す |
| [`equal`](equal.md) | 等しいかどうかだけ |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の辞書順比較を `<=>` で行う
    - [x] 戻り値は順序型
    - [x] 0 と比べて使う

## 関連ページ

- [cpprefjp: std::lexicographical_compare_three_way](https://cpprefjp.github.io/reference/algorithm/lexicographical_compare_three_way.html)
- [cppreference: std::lexicographical_compare_three_way](https://en.cppreference.com/w/cpp/algorithm/lexicographical_compare_three_way)
