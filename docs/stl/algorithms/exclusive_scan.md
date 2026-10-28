---
title: std::exclusive_scan
summary: "累積和（各位置の手前までの合計、その位置を含まない）を求める。"
order: 31
tags:
  - アルゴリズム
---

# std::exclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::exclusive_scan` は、<strong>先頭から各位置の「手前」までの合計（その位置を含まない）</strong>を作る関数です。先頭には初期値が入ります。`{1, 2, 3, 4}` から、初期値 0 で `{0, 1, 3, 6}` ができます。「各要素が始まる位置（オフセット）」を求めるときに便利です。

!!! tip "ポイント"
    - 先頭は**初期値**（0 など）。結果は「自分より前の合計」。
    - メモリ配置の計算（各要素の開始位置）に向く。
    - 並列に実行できる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::exclusive_scan {#exclusive_scan}

```cpp
template <class InputIt, class OutputIt, class T>
OutputIt exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 入力の範囲 |
| `d_first` | 出力イテレータ | 書き出し先の先頭 |
| `init` | T | 先頭に入る初期値 |

- 戻り値: 書き出した最後の次の位置
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> sizes = {4, 8, 2, 6};  // 各データのバイト数
  std::vector<int> offsets(sizes.size());

  // 各データが始まる位置（オフセット）
  std::exclusive_scan(sizes.begin(), sizes.end(), offsets.begin(), 0);
  std::println("{}", offsets);
}
```

```text title="実行結果"
[0, 4, 12, 14]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 可変長のデータを 1 本のバッファに詰めるときの、各データの開始位置 | `exclusive_scan(sizes, offsets, 0)` |
| メッシュごとの頂点の開始インデックス | `exclusive_scan(vertex_counts, first_vertex, 0)` |

## よくあるミス

??? failure "初期値を忘れる"
    `exclusive_scan` には初期値が必須です。ほとんどの場合 `0` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::inclusive_scan`](inclusive_scan.md) | その位置を含む累積 |
| [`std::partial_sum`](partial_sum.md) | 従来の累積和 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] その位置を含まない累積和
    - [x] 先頭は初期値
    - [x] 開始位置の計算に便利

## 関連ページ

- [cpprefjp: std::exclusive_scan](https://cpprefjp.github.io/reference/numeric/exclusive_scan.html)
- [cppreference: std::exclusive_scan](https://en.cppreference.com/w/cpp/algorithm/exclusive_scan)
