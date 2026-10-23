---
title: std::ranges::minmax_element
summary: "範囲の中で、最小と最大の要素の位置を、1 回の走査で両方返す。"
order: 30
tags:
  - アルゴリズム
---

# std::ranges::minmax_element

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`minmax_element` は、**最小の要素と最大の要素の位置を、1 回の走査で両方返す**関数です。[`min_element`](min_element.md) と [`max_element`](max_element.md) を別々に呼ぶより、範囲を 1 回なめるだけで済みます。

!!! tip "ポイント"
    - 戻り値は `.min` と `.max` を持つ構造体（どちらもイテレータ）。
    - 最小は**最初の**もの、最大は**最後の**ものを返す（`max_element` とは違う）。
    - 空の範囲なら、どちらも `end()`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 関数の詳しい説明

### std::ranges::minmax_element {#minmax_element}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr minmax_element_result<borrowed_iterator_t<R>> minmax_element(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: `.min` と `.max` を持つ構造体（どちらもイテレータ）。最大は同じ値なら**最後の**もの

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 9, 1, 9};
  auto [lo, hi] = std::ranges::minmax_element(v);
  std::println("最小 {}番目 / 最大 {}番目", lo - v.begin(), hi - v.begin());
}
```

```text title="実行結果"
最小 2番目 / 最大 3番目
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで比べる |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` | 大小を逆にする |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スコアの最高・最低の人を一度に探す | `minmax_element(players, {}, &Player::score)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲の結果を読む | 未定義動作 |

## よくあるミス

??? failure "最大が「最初」だと思い込む"
    `minmax_element` の最大は、同じ値が複数あれば**最後**のものです。`max_element` とは結果が変わることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::minmax`](minmax.md) | 値のコピーを返す |
| [`std::ranges::min_element`](min_element.md) | 最小の位置だけ |
| [`std::ranges::max_element`](max_element.md) | 最大の位置だけ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最小と最大の位置を 1 回で取る
    - [x] 最大は最後のもの
    - [x] 空なら `end()`

## 関連ページ

- [cpprefjp: std::ranges::minmax_element](https://cpprefjp.github.io/reference/algorithm/ranges_minmax_element.html)
- [cppreference: std::ranges::minmax_element](https://en.cppreference.com/w/cpp/algorithm/ranges/minmax_element)
