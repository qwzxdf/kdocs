---
title: std::ranges::next_permutation
summary: "要素の並びを、辞書順で次の並べ方にする。"
order: 67
tags:
  - アルゴリズム
---

# std::ranges::next_permutation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::next_permutation` は、**要素の並びを、辞書順で「次の並べ方」に変える**アルゴリズムです。繰り返し呼ぶと、すべての並べ方（順列）を 1 つずつ作れます。パズルの全探索や、組み合わせのテストに使います。

!!! tip "ポイント"
    - **整列した状態**から始めると、全部の並べ方を 1 回ずつ作れる。
    - 最後の並べ方まで来ると `false` を返し、並びは最初（昇順）に戻る。
    - 要素数 n の全順列は n! 通り。10 個を超えると爆発的に増える。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::next_permutation {#next_permutation}

```cpp
template <bidirectional_range R, class Comp = ranges::less, class Proj = identity>
constexpr next_permutation_result<borrowed_iterator_t<R>> next_permutation(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 並べ替える範囲 |  |
| `comp` | 関数 | 辞書順を決める比較 | `<` |

- 戻り値: `in`（範囲の終わり）と `found`（次の並べ方があれば `true`）を持つ構造体
- 計算量: O(n)（1 回の呼び出し）

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};  // 昇順から始める

  do {
    std::println("{}", v);
  } while (std::ranges::next_permutation(v).found);
}
```

```text title="実行結果"
[1, 2, 3]
[1, 3, 2]
[2, 1, 3]
[2, 3, 1]
[3, 1, 2]
[3, 2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 3〜8 人の出撃順の全パターンを試す | `do { 評価 } while (next_permutation(order).found)` |
| パズルの全探索 | 全部の並べ方を試す |

## よくあるミス

??? failure "整列せずに始めて、全部が出ない"
    `{3, 1, 2}` から始めると、そこより後の並べ方しか出ません。全部を出したいなら先に `sort` します。

??? failure "要素数が大きい"
    10 個で 362 万通り、13 個で 62 億通りです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::prev_permutation`](prev_permutation.md) | 辞書順で前の並べ方 |
| [`std::ranges::is_permutation`](is_permutation.md) | 並べ替えで一致するか |
| [`std::ranges::shuffle`](shuffle.md) | ランダムな並べ方を 1 つ作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 辞書順で次の並べ方にする
    - [x] 昇順から始めて `found` が false になるまで
    - [x] 要素数は 10 以下に

## 関連ページ

- [cpprefjp: std::ranges::next_permutation](https://cpprefjp.github.io/reference/algorithm/ranges_next_permutation.html)
- [cppreference: std::ranges::next_permutation](https://en.cppreference.com/w/cpp/algorithm/ranges/next_permutation)
