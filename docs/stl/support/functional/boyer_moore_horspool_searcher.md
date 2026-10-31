---
title: std::boyer_moore_horspool_searcher
summary: "ボイヤー・ムーア・ホースプール法で部分列を探す検索のオブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::boyer_moore_horspool_searcher

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

ボイヤー・ムーア法は速い反面、表が 2 つ要り、準備の手間もかかります。ボイヤー・ムーア・ホースプール法は、そのうち「悪い文字の表」だけを使う簡略版で、実装が軽く、準備も早く済みます。それを検索オブジェクトにしたのが `std::boyer_moore_horspool_searcher` です。

!!! tip "ポイント"
    - `boyer_moore_searcher` と同じ使い方
    - 表が 1 つだけなので、準備とメモリが軽い
    - 典型的な文章では、`boyer_moore_searcher` と同じくらい速い
    - 最悪の場合の遅さは、`boyer_moore_searcher` より劣る

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::boyer_moore_horspool_searcher {#boyer_moore_horspool_searcher}

<span class="ver ver-17">C++17</span>

```cpp
template <class RandomIt, class Hash = std::hash<typename std::iterator_traits<RandomIt>::value_type>,
          class BinaryPredicate = std::equal_to<>>
class boyer_moore_horspool_searcher {
 public:
  boyer_moore_horspool_searcher(RandomIt pat_first, RandomIt pat_last, Hash hf = Hash(), BinaryPredicate pred = BinaryPredicate());

  template <class RandomIt2>
  std::pair<RandomIt2, RandomIt2> operator()(RandomIt2 first, RandomIt2 last) const;
};
```

引数は [`boyer_moore_searcher`](boyer_moore_searcher.md) と同じです。ランダム アクセス イテレータのパターン範囲 `pat_first`・`pat_last`、ハッシュ関数 `hf`、等しさの述語 `pred` を渡します。

ボイヤー・ムーア法との違いは、準備する表の数です。ホースプール法は「悪い文字の表」しか作りません。表を作る時間が短く、メモリも少なくて済みます。そのかわり、「良い接尾辞の表」で大きく飛べる場面がないぶん、パターンが繰り返しの多い形だと、最悪の計算量が悪くなります。

規格が決めているのは、ボイヤー・ムーア法と同じく、見つからないときの時間が文章の長さに比例することと、典型的にはパターンの長さの分だけ、飛ぶことです。どちらを選ぶかは、測ってから決めます。

文字列だけでなく、バイト列（`std::vector<unsigned char>`）のような、ランダム アクセスできる任意の列でも探せます。ハッシュ関数 `std::hash<unsigned char>` が使われるため、特別な準備は要りません。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  // バイナリ データの中から、バイト列のパターンを探す
  std::vector<unsigned char> data = {0x00, 0xFF, 0x10, 0x20, 0x30, 0xFF, 0x10, 0x20, 0x30, 0x40};
  std::vector<unsigned char> pat = {0xFF, 0x10, 0x20, 0x30, 0x40};

  std::boyer_moore_horspool_searcher searcher(pat.begin(), pat.end());
  auto [b, e] = searcher(data.begin(), data.end());
  std::println("位置: {} から {}", b - data.begin(), e - data.begin());

  // std::search に渡しても同じ
  auto it = std::search(data.begin(), data.end(), searcher);
  std::println("std::search の結果: {}", it - data.begin());

  // 見つからない場合
  std::vector<unsigned char> missing = {0xAA, 0xBB};
  auto [mb, me] = std::boyer_moore_horspool_searcher(missing.begin(), missing.end())(data.begin(), data.end());
  std::println("見つからない: {}", mb == data.end());
}
```

```text title="実行結果"
位置: 5 から 10
std::search の結果: 5
見つからない: true
```

## ゲームでの使いどころ

セーブ データやパケットのような、バイト列の中から、決まった並びの目印（ヘッダーなど）を探すときに使えます。

## よくあるミス

??? failure "最悪のパターンで遅くなる"
    繰り返しの多いパターン（`aaaa…b` など）では、ボイヤー・ムーア法より遅くなることがあります。

??? failure "ランダム アクセスでないイテレータを渡す"
    コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`boyer_moore_searcher`](boyer_moore_searcher.md) | 良い接尾辞の表も使う版 |
| [`default_searcher`](default_searcher.md) | 素朴な検索 |
| [`std::search`](../../algorithms/search.md) | 検索オブジェクトを受け取る側 |

## コンパイラ対応

C++17 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::boyer_moore_horspool_searcher](https://cpprefjp.github.io/reference/functional/boyer_moore_horspool_searcher.html)
- [cppreference: std::boyer_moore_horspool_searcher](https://en.cppreference.com/w/cpp/utility/functional/boyer_moore_horspool_searcher)
