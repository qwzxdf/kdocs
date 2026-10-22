---
title: std::transform_exclusive_scan
summary: "各要素を変換してから、先頭からの累積を作る（その位置を含まない）。"
order: 900
tags:
  - アルゴリズム
---

# std::transform_exclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`transform_inclusive_scan` の、「その位置を含まない」版です。出力の先頭は初期値になり、そこから 1 つ前までの変換後の値の累積が並びます。

!!! tip "ポイント"
    - 初期値が必須。出力の最初の要素は初期値そのもの。
    - 含むのは [`transform_inclusive_scan`](transform_inclusive_scan.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::transform_exclusive_scan {#transform_exclusive_scan}

```cpp
template <class InputIt, class OutputIt, class T, class BinaryOp, class UnaryOp>
OutputIt transform_exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init, BinaryOp binary_op, UnaryOp unary_op);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 入力の範囲 |
| `d_first` | イテレータ | 出力の先頭 |
| `init` | T | 初期値 |
| `binary_op` | 関数 | 累積に使う 2 項演算 |
| `unary_op` | 関数 | 各要素に先に適用する変換 |

- 戻り値: 出力の最後の次のイテレータ
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::vector<int> out(v.size());
  std::transform_exclusive_scan(v.begin(), v.end(), out.begin(), 0, std::plus<>{},
                                [](int x) { return x * x; });
  std::println("{}", out);
}
```

```text title="実行結果"
[0, 1, 5, 14]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 各オブジェクトが配列のどこから始まるかを求める（サイズ列の累積） | `std::transform_exclusive_scan(sizes.begin(), sizes.end(), offs.begin(), 0, std::plus<>{}, [](int s){ return s; });` |

## よくあるミス

??? failure "初期値を忘れる"
    exclusive 系は初期値が必須です。`inclusive` と違い省略できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exclusive_scan`](exclusive_scan.md) | 変換なしの版 |
| [`transform_inclusive_scan`](transform_inclusive_scan.md) | その位置を含む版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変換しながら累積を作る
    - [x] その位置を含まない
    - [x] 初期値が必須

## 関連ページ

- [cpprefjp: std::transform_exclusive_scan](https://cpprefjp.github.io/reference/numeric/transform_exclusive_scan.html)
- [cppreference: std::transform_exclusive_scan](https://en.cppreference.com/w/cpp/algorithm/transform_exclusive_scan)
