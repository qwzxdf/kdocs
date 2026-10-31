---
title: std::default_searcher
summary: "`std::search` に渡せる、素朴な部分列検索のオブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::default_searcher

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::search(first, last, searcher)` は、探し方を「検索オブジェクト」として第 3 引数に渡せます。ほかの検索（`boyer_moore_searcher` など）と同じ書き方でそろえたいとき、標準の素朴な検索も同じ形の部品として用意されています。それが `std::default_searcher` です。先頭から 1 要素ずつ比べるだけの検索を、検索オブジェクトに包みます。

!!! tip "ポイント"
    - `std::search(first, last, searcher)` の第 3 引数に渡す
    - `searcher(first, last)` と直接呼ぶと、見つかった範囲の `pair` が返る
    - パターンを 1 度渡しておけば、いくつもの文章に使い回せる
    - `<algorithm>` ではなく `<functional>` にある

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::default_searcher {#default_searcher}

<span class="ver ver-17">C++17</span>

```cpp
template <class ForwardIt, class BinaryPredicate = std::equal_to<>>
class default_searcher {
 public:
  default_searcher(ForwardIt pat_first, ForwardIt pat_last, BinaryPredicate pred = BinaryPredicate());

  template <class ForwardIt2>
  std::pair<ForwardIt2, ForwardIt2> operator()(ForwardIt2 first, ForwardIt2 last) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pat_first`, `pat_last` | 前方イテレータ | 探したいパターンの範囲 |
| `pred` | 二項述語 | 2 つの要素を等しいとみなす条件。省略すると `==` |

`pat_first` と `pat_last` が指す範囲は、`default_searcher` が参照するだけで、コピーしません。そのため、検索を終えるまで、パターンの元の文字列を生かしておく必要があります。

`pred` を渡すと、比べ方を変えられます。たとえば大文字小文字を無視して探したいときは、`tolower` で比べるラムダを渡します。

`operator()` の戻り値は、見つかった範囲の `pair` です。パターンが見つからなければ、`{last, last}` が返ります。パターンが空のときは、`{first, first}` です。

`std::search` にそのまま渡した場合は、`pair` の `first`（見つかった位置）だけが返ります。

計算量は最悪で、（文章の長さ）×（パターンの長さ）です。長い文章を何度も探すなら、[`boyer_moore_searcher`](boyer_moore_searcher.md) のほうが速くなります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <cctype>
#include <functional>
#include <print>
#include <string>

int main() {
  std::string text = "hello world, hello cpp";
  std::string pat = "hello";
  std::default_searcher searcher(pat.begin(), pat.end());

  // searcher を直接呼ぶと、見つかった範囲の pair が返る
  auto [b1, e1] = searcher(text.begin(), text.end());
  std::println("1 つ目: {} から {}", b1 - text.begin(), e1 - text.begin());

  // 1 つ目の終わりから探しなおすと、2 つ目が見つかる
  auto [b2, e2] = searcher(e1, text.end());
  std::println("2 つ目: {} から {}", b2 - text.begin(), e2 - text.begin());

  // 見つからないとき
  std::string other = "abc";
  auto [nb, ne] = searcher(other.begin(), other.end());
  std::println("見つからない: {}", nb == other.end());

  // 大文字小文字を無視する述語
  std::string title = "Hello World";
  std::string key = "WORLD";
  auto ci = [](char a, char b) {
    return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b));
  };
  auto it = std::search(title.begin(), title.end(), std::default_searcher(key.begin(), key.end(), ci));
  std::println("大文字小文字を無視: {}", it - title.begin());
}
```

```text title="実行結果"
1 つ目: 0 から 5
2 つ目: 13 から 18
見つからない: true
大文字小文字を無視: 6
```

## ゲームでの使いどころ

ログやチャットの文字列から、特定の語を探すときに使います。大文字小文字を無視した検索のように、比べ方を変えたいときも、述語を 1 つ渡すだけで済みます。

## よくあるミス

??? failure "パターンの元の文字列を先に消す"
    `default_searcher` は、パターンの範囲を参照するだけです。元の文字列が消えると、検索が壊れます。

??? failure "速くなると思って使う"
    素朴な検索そのものなので、`std::search` を普通に呼ぶのと同じ速さです。速くしたいときは `boyer_moore_searcher` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`boyer_moore_searcher`](boyer_moore_searcher.md) | 長い文章向けの速い検索 |
| [`boyer_moore_horspool_searcher`](boyer_moore_horspool_searcher.md) | 準備が軽い速い検索 |
| [`std::search`](../../algorithms/search.md) | 検索オブジェクトを受け取る側 |

## コンパイラ対応

C++17 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::default_searcher](https://cpprefjp.github.io/reference/functional/default_searcher.html)
- [cppreference: std::default_searcher](https://en.cppreference.com/w/cpp/utility/functional/default_searcher)
