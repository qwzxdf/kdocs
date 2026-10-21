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

`std::ranges::prev_permutation` は、[`next_permutation`](next_permutation.md) の逆で、**要素の並びを辞書順で「前の並べ方」に変える**アルゴリズムです。降順から始めると、全部の並べ方が逆の順番で作れます。

!!! tip "ポイント"
    - **降順の状態**から始めると、全部の並べ方を作れる。
    - 最初の並べ方まで来ると `false` を返し、並びは最後（降順）に戻る。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::prev_permutation {#prev_permutation}

```cpp
template <bidirectional_range R, class Comp = ranges::less, class Proj = identity>
constexpr prev_permutation_result<borrowed_iterator_t<R>> prev_permutation(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 並べ替える範囲 |  |
| `comp` | 関数 | 辞書順を決める比較 | `<` |

- 戻り値: `in` と `found`（前の並べ方があれば `true`）
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 3, 2};
  std::ranges::prev_permutation(v);
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 降順から全パターンを試す | `do { ... } while (prev_permutation(order).found)` |

## よくあるミス

??? failure "昇順から始めて、すぐ終わる"
    昇順は「最初の並べ方」なので、`found` が `false` になります。降順から始めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::next_permutation`](next_permutation.md) | 辞書順で次の並べ方 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 辞書順で前の並べ方にする
    - [x] 降順から始める
    - [x] `next_permutation` の逆

## 関連ページ

- [cpprefjp: std::ranges::prev_permutation](https://cpprefjp.github.io/reference/algorithm/ranges_prev_permutation.html)
- [cppreference: std::ranges::prev_permutation](https://en.cppreference.com/w/cpp/algorithm/ranges/prev_permutation)
