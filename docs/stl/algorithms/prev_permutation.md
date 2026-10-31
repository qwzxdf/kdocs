---
title: std::ranges::prev_permutation
summary: "要素の並びを、辞書順で前の並べ方にする。"
order: 68
tags:
  - アルゴリズム
---

# std::ranges::prev_permutation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

並べ方の全パターンを、順に試したい。`std::next_permutation` が、辞書順で次の並べ方に進めるのに対し、`std::prev_permutation` は、<strong>前</strong>の並べ方に戻します。降順から始めれば、全パターンを逆の順に作れます。

!!! tip "ポイント"
    - 辞書順で「前」の並べ方に変える
    - 前があれば `true`、なければ（最初の並び）`false` を返し、最後の並び（降順）に戻る
    - 降順から始めると、全部の並べ方を巡れる
    - 重複する要素があると、同じ並べ方は 1 回だけ

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::prev_permutation {#prev_permutation}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class BidirIt>
bool prev_permutation(BidirIt first, BidirIt last);

template <class BidirIt, class Compare>
bool prev_permutation(BidirIt first, BidirIt last, Compare comp);
```

`next_permutation` と逆向きに、同じアルゴリズムで動きます。計算量は、1 回あたり O(n) です。

`do { ... } while (std::prev_permutation(v.begin(), v.end()));` の形で、全パターンを処理できます。

要素の数が増えると、パターン数が階乗で増えます（10 個で約 360 万、13 個で約 62 億）。試せるのは 10 個程度までです。

C++20 の `std::ranges::prev_permutation` は、範囲を直接渡せます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 3, 2};
  std::prev_permutation(v.begin(), v.end());
  std::println("{}", v);  // 1 つ前の並び

  // 降順から始めて、全パターンを数える
  std::vector<int> w = {3, 2, 1};
  int count = 0;
  do {
    ++count;
  } while (std::prev_permutation(w.begin(), w.end()));
  std::println("パターン数: {}", count);
  std::println("最後は降順に戻る: {}", w);
}
```

```text title="実行結果"
[1, 2, 3]
パターン数: 6
最後は降順に戻る: [3, 2, 1]
```

## ゲームでの使いどころ

小さな問題の全探索（パズルの総当たり）で使います。

## よくあるミス

??? failure "ソートせずに始める"
    途中の並びから始まり、全パターンを巡れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next_permutation`](next_permutation.md) | 次の並べ方に進める |
| [`is_permutation`](is_permutation.md) | 並べ替えの関係を調べる |
| [`sort`](sort.md) | 最初の並びを作る |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::prev_permutation](https://cpprefjp.github.io/reference/algorithm/ranges_prev_permutation.html)
- [cppreference: std::ranges::prev_permutation](https://en.cppreference.com/w/cpp/algorithm/ranges/prev_permutation)
