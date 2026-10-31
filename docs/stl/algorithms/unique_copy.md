---
title: std::ranges::unique_copy
summary: "隣り合う重複をまとめた結果を、元を残したまま別の場所に作る。"
order: 40
tags:
  - アルゴリズム
---

# std::ranges::unique_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

連続して並ぶ同じ値を 1 つにまとめたコピーを、別の配列に作りたい。`std::unique_copy` は、隣り合う同じ要素を 1 つにして、結果を出力先に書きます。元の範囲は変わりません。

!!! tip "ポイント"
    - 連続した同じ値を 1 つにまとめて、出力先へコピーする
    - 元の範囲は変わらない
    - 離れた同じ値は、まとまらない（先にソートする）
    - 戻り値は、出力の最後の次の位置

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::unique_copy {#unique_copy}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt, class OutputIt>
OutputIt unique_copy(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class BinaryPred>
OutputIt unique_copy(InputIt first, InputIt last, OutputIt d_first, BinaryPred pred);
```

`unique` が、その場で詰めて、後ろに使い終えた要素を残すのに対し、`unique_copy` は、元を残したまま、重複を除いたコピーを作ります。

「連続した」重複だけを除くので、全体の重複を除くには、先に `std::sort` します。出力に `std::back_inserter` を使えば、領域の大きさを気にしなくて済みます。

比較を変える述語を渡せます。たとえば、大文字小文字を無視して、連続した同じ文字を 1 つにまとめられます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 1, 2, 2, 2, 3, 1, 1};

  std::vector<int> out;
  std::unique_copy(v.begin(), v.end(), std::back_inserter(out));

  std::println("元: {}", v);
  std::println("結果: {}", out);  // 離れた 1 は残る
}
```

```text title="実行結果"
元: [1, 1, 2, 2, 2, 3, 1, 1]
結果: [1, 2, 3, 1]
```

## ゲームでの使いどころ

連続したキー入力の重複を除いたコピーを作る、といった処理に使います。

## よくあるミス

??? failure "離れた重複も除かれると思う"
    連続した重複だけです。先にソートします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unique`](unique.md) | その場で詰める |
| [`sort`](sort.md) | 先に並べる |
| [`adjacent_find`](adjacent_find.md) | 隣り合う等しい要素を探す |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::unique_copy](https://cpprefjp.github.io/reference/algorithm/ranges_unique_copy.html)
- [cppreference: std::ranges::unique_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/unique_copy)
