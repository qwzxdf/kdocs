---
title: std::partial_sum
summary: "先頭からの累積和（途中までの合計）を求める。"
order: 28
tags:
  - アルゴリズム
---

# std::partial_sum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

`std::partial_sum` は、<strong>先頭から各位置までの合計（累積和）</strong>を作る関数です。`{1, 2, 3, 4}` から `{1, 3, 6, 10}` ができます。経験値の累計、確率の累積分布（ガチャの抽選）などに使います。

!!! tip "ポイント"
    - 出力は入力と同じ長さ。同じ範囲に書き戻すこともできる。
    - 「n 番目までの合計」を何度も求めるときに、先に作っておくと速い。
    - C++17 の [`inclusive_scan`](inclusive_scan.md) は、これの並列化できる版。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::partial_sum {#partial_sum}

```cpp
template <class InputIt, class OutputIt>
OutputIt partial_sum(InputIt first, InputIt last, OutputIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 入力の範囲 |
| `d_first` | 出力イテレータ | 書き出し先の先頭（入力と同じでもよい） |

- 戻り値: 書き出した最後の次の位置
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> drop_rate = {50, 30, 15, 5};  // ガチャの確率（%）
  std::vector<int> cumulative(drop_rate.size());

  std::partial_sum(drop_rate.begin(), drop_rate.end(), cumulative.begin());
  std::println("{}", cumulative);  // 乱数 0〜99 をこの表のどこに入るかで判定
}
```

```text title="実行結果"
[50, 80, 95, 100]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ガチャの排出率の累積表 | `partial_sum(rates, cumulative)` |
| レベルごとの必要経験値の累計 | `partial_sum(exp_per_level, total)` |

## よくあるミス

??? failure "オーバーフロー"
    累積するので、`int` が大きな値で溢れることがあります。累積の型は大きめにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::inclusive_scan`](inclusive_scan.md) | 並列化できる版 |
| [`std::adjacent_difference`](adjacent_difference.md) | 逆の操作（差分） |
| [`std::accumulate`](accumulate.md) | 最終的な合計だけ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭からの累積和を作る
    - [x] `adjacent_difference` の逆
    - [x] 累積分布の表に使える

## 関連ページ

- [cpprefjp: std::partial_sum](https://cpprefjp.github.io/reference/numeric/partial_sum.html)
- [cppreference: std::partial_sum](https://en.cppreference.com/w/cpp/algorithm/partial_sum)
