---
title: std::inclusive_scan
summary: "累積和（各位置までの合計、その位置を含む）を求める。並列化できる。"
order: 30
tags:
  - アルゴリズム
---

# std::inclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::inclusive_scan` は、**先頭から各位置までの合計（その位置を含む）**を作る関数で、[`partial_sum`](partial_sum.md) の C++17 版です。足し算の順序を問わないので、並列に実行できます。実行ポリシーを渡すと並列になります。

!!! tip "ポイント"
    - 結果は `partial_sum` と同じ。`{1, 2, 3, 4}` → `{1, 3, 6, 10}`。
    - 各位置を「含む」のが `inclusive`。含まないのは [`exclusive_scan`](exclusive_scan.md)。
    - 関数は結合法則を満たす必要がある。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::inclusive_scan {#inclusive_scan}

```cpp
template <class InputIt, class OutputIt>
OutputIt inclusive_scan(InputIt first, InputIt last, OutputIt d_first);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `first`, `last` | イテレータ | 入力の範囲 |  |
| `d_first` | 出力イテレータ | 書き出し先の先頭 |  |
| `op` | 関数 | 演算（省略時は `+`） | `std::plus` |

- 戻り値: 書き出した最後の次の位置
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::vector<int> out(v.size());

  std::inclusive_scan(v.begin(), v.end(), out.begin());
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 3, 6, 10]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大量のデータの累積和を並列に求める | `inclusive_scan(std::execution::par, ...)` |

## よくあるミス

??? failure "exclusive と取り違える"
    `inclusive_scan` は各位置を**含む**合計、`exclusive_scan` は**含まない**合計です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::exclusive_scan`](exclusive_scan.md) | その位置を含まない累積 |
| [`std::partial_sum`](partial_sum.md) | 従来の累積和（順序固定） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 各位置を含む累積和
    - [x] 並列化できる
    - [x] `partial_sum` の後継

## 関連ページ

- [cpprefjp: std::inclusive_scan](https://cpprefjp.github.io/reference/numeric/inclusive_scan.html)
- [cppreference: std::inclusive_scan](https://en.cppreference.com/w/cpp/algorithm/inclusive_scan)
