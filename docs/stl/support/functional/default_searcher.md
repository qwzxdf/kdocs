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

`std::search(first, last, searcher)` には、探し方を「検索オブジェクト」として渡せます。`default_searcher` は標準の素朴な検索（先頭から順に比べる）をそのまま包んだもので、他の検索オブジェクトと同じ書き方でそろえたいときに使います。

!!! tip "ポイント"
    - `std::search(first, last, searcher)` に渡して使う。
    - 検索結果は `search` と同じ。
    - `<functional>` にある（`<algorithm>` ではない）。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::default_searcher {#default_searcher}

```cpp
template <class ForwardIt, class Pred = equal_to<>>
class default_searcher {
 public:
  default_searcher(ForwardIt pat_first, ForwardIt pat_last, Pred pred = Pred());
  template <class It> pair<It, It> operator()(It first, It last) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pat_first, pat_last` | イテレータ | 探したいパターンの範囲 |
| `pred` | 述語 | 省略可。要素を比べる述語 |

- 戻り値: `operator()` は見つかった範囲の `pair`（見つからなければ `{last, last}`）
- 計算量: 最悪は (テキスト長) × (パターン長)


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <string>

int main() {
  std::string text = "hello world, hello cpp";
  std::string pat = "world";
  auto it = std::search(text.begin(), text.end(),
                        std::default_searcher(pat.begin(), pat.end()));
  std::println("{}", it - text.begin());
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログの長い文字列から特定のパターンを探す | `std::search(text.begin(), text.end(), std::default_searcher(pat.begin(), pat.end()));` |

## よくあるミス

??? failure "探し方を変えたいのに使う"
    素朴な検索そのものです。速くしたいなら `boyer_moore_searcher` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`search`](../../algorithms/search.md) | 検索オブジェクトを受け取る |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準の `std::search` と同じ、素朴な検索
    - [x] `std::search` の第 3 引数に渡す
    - [x] 同じパターンを何度も探すなら使い回す

## 関連ページ

- [cpprefjp: std::default_searcher](https://cpprefjp.github.io/reference/functional/default_searcher.html)
- [cppreference: std::default_searcher](https://en.cppreference.com/w/cpp/utility/functional/default_searcher)
