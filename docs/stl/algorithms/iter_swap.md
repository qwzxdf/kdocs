---
title: std::iter_swap
summary: "2 つのイテレータが指す要素を入れ替える。"
order: 71
tags:
  - アルゴリズム
---

# std::iter_swap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <algorithm>`
</div>

2 つのイテレータが指す要素を、入れ替えたい。`std::iter_swap(a, b)` は、`std::swap(*a, *b)` と同じ働きです。ソートなどのアルゴリズムの内部で、要素の入れ替えに使われています。

!!! tip "ポイント"
    - 2 つのイテレータが指す要素を入れ替える
    - `std::swap(*a, *b)` と同じ
    - 値を返さない
    - 特殊なイテレータ（プロキシを返すもの）でも正しく動くよう、アルゴリズムが使う

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::iter_swap {#iter_swap}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class ForwardIt1, class ForwardIt2>
void iter_swap(ForwardIt1 a, ForwardIt2 b);
```

`std::vector<bool>` のように、要素への参照が本物の参照でない（プロキシ）コンテナで、`std::swap(*a, *b)` が正しく動かない場合があります。`iter_swap` は、そうしたイテレータ向けに特殊化されることがあり、より安全です。

`a == b` でも安全です（同じ要素どうしの入れ替えで、何も変わらない）。

自作のアルゴリズムで要素を入れ替えるときは、`iter_swap` を使うと、イテレータの種類に対応しやすくなります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <list>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::iter_swap(v.begin(), v.end() - 1);  // 先頭と末尾
  std::println("{}", v);

  // list のようなイテレータでも使える
  std::list<int> l = {10, 20, 30};
  std::iter_swap(l.begin(), std::next(l.begin(), 2));
  std::println("{}", l);
}
```

```text title="実行結果"
[4, 2, 3, 1]
[30, 20, 10]
```

## ゲームでの使いどころ

自作のソートやシャッフルで、イテレータの位置の要素を入れ替えるときに使います。

## よくあるミス

??? failure "swap(a, b) と書く"
    イテレータ自身が入れ替わります。要素を入れ替えるのは `iter_swap` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`swap_ranges`](swap_ranges.md) | 範囲を入れ替える |
| `std::swap` | 値を入れ替える |
| [`reverse`](reverse.md) | 並びを逆にする |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::iter_swap](https://cpprefjp.github.io/reference/algorithm/iter_swap.html)
- [cppreference: std::iter_swap](https://en.cppreference.com/w/cpp/algorithm/iter_swap)
