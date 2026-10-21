---
title: std::adjacent_difference
summary: "隣り合う要素の差を求める。"
order: 29
tags:
  - アルゴリズム
---

# std::adjacent_difference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

`std::adjacent_difference` は、**隣り合う要素の差**を求める関数です。`{1, 3, 6, 10}` から `{1, 2, 3, 4}` ができます（先頭は元のまま）。[`partial_sum`](partial_sum.md) の逆の操作で、「累積値から、毎回の増加量を取り出す」ときに使います。

!!! tip "ポイント"
    - 先頭の要素は、元のまま出力される。
    - 差ではなく、別の演算（比、和など）を指定することもできる。
    - 同じ範囲に書き戻せる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::adjacent_difference {#adjacent_difference}

```cpp
template <class InputIt, class OutputIt>
OutputIt adjacent_difference(InputIt first, InputIt last, OutputIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 入力の範囲 |
| `d_first` | 出力イテレータ | 書き出し先の先頭 |

- 戻り値: 書き出した最後の次の位置
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> total_score = {10, 25, 45, 70};  // 累計スコア
  std::vector<int> gained(total_score.size());

  std::adjacent_difference(total_score.begin(), total_score.end(), gained.begin());
  std::println("{}", gained);  // 各ステージで増えた点数
}
```

```text title="実行結果"
[10, 15, 20, 25]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 累計から、各ステージで増えた量を取り出す | `adjacent_difference(total, gained)` |
| フレーム時刻の列から、フレーム間隔を求める | `adjacent_difference(times, deltas)` |

## よくあるミス

??? failure "先頭が差ではないことを忘れる"
    先頭の要素は、元の値のままです。差としては 2 番目からを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::partial_sum`](partial_sum.md) | 逆の操作（累積和） |
| [`std::ranges::adjacent_find`](adjacent_find.md) | 隣り合う条件の場所を探す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣り合う要素の差を作る
    - [x] 先頭は元のまま
    - [x] `partial_sum` の逆

## 関連ページ

- [cpprefjp: std::adjacent_difference](https://cpprefjp.github.io/reference/numeric/adjacent_difference.html)
- [cppreference: std::adjacent_difference](https://en.cppreference.com/w/cpp/algorithm/adjacent_difference)
