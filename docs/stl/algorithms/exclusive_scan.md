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

`inclusive_scan` が、その位置の要素を含めた累計なのに対し、`std::exclusive_scan` は、<strong>その位置の要素を含めない</strong>累計です。`out[i]` は `in[0]` 〜 `in[i-1]` の合計になり、先頭は初期値です。「各要素の書き込み位置」を求めるのに、ちょうどよい形です。

!!! tip "ポイント"
    - `out[i]` は、`in[0]` 〜 `in[i-1]` の合計（その位置を含まない）
    - `out[0]` は初期値
    - 各要素のオフセット（書き込み開始位置）を求める用途に向く
    - 初期値の指定が必須

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::exclusive_scan {#exclusive_scan}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class OutputIt, class T>
OutputIt exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init);

template <class InputIt, class OutputIt, class T, class BinaryOp>
OutputIt exclusive_scan(InputIt first, InputIt last, OutputIt d_first, T init, BinaryOp op);
```

可変長のデータを 1 本の配列に詰めるとき、「各要素の長さ」の `exclusive_scan` が、各要素の開始位置になります。長さが `{3, 1, 4}` なら、開始位置は `{0, 3, 4}` で、全体の長さは `3 + 1 + 4 = 8` です。

GPU のプログラミングで、並列に詰め込む処理（ストリーム圧縮）の基本部品としても知られています。

`inclusive_scan` との違いは、`out` を 1 つずらしたものと同じですが、最後の要素の累計は出力に含まれません。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  // 各文字列の長さ
  const std::vector<int> lengths = {3, 1, 4};

  // 各文字列を詰める開始位置
  std::vector<int> offsets(lengths.size());
  std::exclusive_scan(lengths.begin(), lengths.end(), offsets.begin(), 0);
  std::println("{}", offsets);

  // 全体の長さ
  std::println("全体: {}", offsets.back() + lengths.back());
}
```

```text title="実行結果"
[0, 3, 4]
全体: 8
```

## ゲームでの使いどころ

可変長のデータ（メッシュの頂点数など）を、1 本のバッファに詰めるときの、開始位置の計算に使います。

## よくあるミス

??? failure "inclusive と取り違える"
    その位置を含まない累計です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inclusive_scan`](inclusive_scan.md) | その位置を含む累計 |
| [`transform_exclusive_scan`](transform_exclusive_scan.md) | 変換してから累計 |
| [`partial_sum`](partial_sum.md) | 従来の累計 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::exclusive_scan](https://cpprefjp.github.io/reference/numeric/exclusive_scan.html)
- [cppreference: std::exclusive_scan](https://en.cppreference.com/w/cpp/algorithm/exclusive_scan)
