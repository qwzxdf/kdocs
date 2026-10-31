---
title: std::boyer_moore_searcher
summary: "長い列の中から部分列を速く探す検索のオブジェクト（ボイヤー・ムーア法）。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::boyer_moore_searcher

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

長い文章から短い語を何度も探すとき、素朴な検索は、文章の長さ × 語の長さだけ比べます。ボイヤー・ムーア法は、語の末尾から比べ、合わなければ語を何文字もまとめて先へずらすことで、多くの場合に、文章の長さよりも少ない比較で済ませます。`std::boyer_moore_searcher` は、それを検索オブジェクトにしたものです。

!!! tip "ポイント"
    - `std::search` の第 3 引数に渡す。ランダム アクセス イテレータが必要
    - 作るときに、パターンから「ずらす幅の表」を作る（準備のコストがかかる）
    - パターンが長いほど、1 回のずらしが大きくなり、効果が出る
    - 同じパターンで何度も探すなら、1 回作って使い回す

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::boyer_moore_searcher {#boyer_moore_searcher}

<span class="ver ver-17">C++17</span>

```cpp
template <class RandomIt, class Hash = std::hash<typename std::iterator_traits<RandomIt>::value_type>,
          class BinaryPredicate = std::equal_to<>>
class boyer_moore_searcher {
 public:
  boyer_moore_searcher(RandomIt pat_first, RandomIt pat_last, Hash hf = Hash(), BinaryPredicate pred = BinaryPredicate());

  template <class RandomIt2>
  std::pair<RandomIt2, RandomIt2> operator()(RandomIt2 first, RandomIt2 last) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pat_first`, `pat_last` | ランダム アクセス イテレータ | パターンの範囲 |
| `hf` | ハッシュ関数 | 要素から、ずらす幅の表を引くためのハッシュ。省略すると `std::hash` |
| `pred` | 二項述語 | 要素が等しいかの判定。省略すると `==` |

コンストラクターが、パターンから「悪い文字の表」と「良い接尾辞の表」という 2 つの表を作ります。この準備に、パターンの長さに比例する時間とメモリを使います。表は `Hash` を使った連想配列に入るので、メモリは、`boyer_moore_horspool_searcher` より多めです。

`operator()` は、見つかった範囲を `pair` で返します。見つからなければ `{last, last}` です。

計算量は、文章の長さを n、パターンの長さを m として、規格が保証する上限は n × m 回の比較です。典型的な文章では、n/m に近い比較回数で済みます。

パターンが短いとき（数文字）は、準備のコストのほうが大きく、`default_searcher` や `std::string::find` のほうが速いこともあります。数十文字以上のパターンを、長い文章で探すときに効果が出ます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <string>
#include <vector>

int main() {
  std::string text = "abracadabra abracadabra abra";
  std::string pat = "abra";

  // パターンから表を作る。1 度作れば何度でも使える
  std::boyer_moore_searcher searcher(pat.begin(), pat.end());

  // 見つかるたびに、その終わりから探しなおして、すべての位置を集める
  std::vector<int> positions;
  auto it = text.begin();
  while (true) {
    auto [b, e] = searcher(it, text.end());
    if (b == text.end()) break;
    positions.push_back(static_cast<int>(b - text.begin()));
    it = e;
  }
  std::println("見つかった位置: {}", positions);

  // 同じ searcher を、別の文章にも使える
  std::string other = "no match here";
  auto hit = std::search(other.begin(), other.end(), searcher);
  std::println("別の文章で見つかった: {}", hit != other.end());
}
```

```text title="実行結果"
見つかった位置: [0, 7, 12, 19, 24]
別の文章で見つかった: false
```

## ゲームでの使いどころ

大きなログ ファイルや、読み込んだテキスト全体から、決まった語を何度も探すときに使います。短い文字列を 1 回探すだけなら、準備のコストで、かえって遅くなります。

## よくあるミス

??? failure "パターンが短いのに使う"
    表を作る準備のほうが重く、素朴な検索や `find` より遅くなることがあります。

??? failure "毎回 searcher を作り直す"
    準備に時間がかかります。同じパターンなら、1 度作って使い回します。

??? failure "ランダム アクセスでないイテレータを渡す"
    `std::list` のイテレータなどでは、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_searcher`](default_searcher.md) | 素朴な検索 |
| [`boyer_moore_horspool_searcher`](boyer_moore_horspool_searcher.md) | 表が小さい簡易版 |
| [`std::search`](../../algorithms/search.md) | 検索オブジェクトを受け取る側 |

## コンパイラ対応

C++17 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::boyer_moore_searcher](https://cpprefjp.github.io/reference/functional/boyer_moore_searcher.html)
- [cppreference: std::boyer_moore_searcher](https://en.cppreference.com/w/cpp/utility/functional/boyer_moore_searcher)
