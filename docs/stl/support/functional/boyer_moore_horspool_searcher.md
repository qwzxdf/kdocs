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

ボイヤー・ムーア法の簡略版で、前処理が軽く実装も単純です。平均的にはボイヤー・ムーア法に近い速さで、短めのパターンや前処理を軽くしたいときに向きます。

!!! tip "ポイント"
    - `std::search(first, last, searcher)` に渡して使う。
    - パターンを渡して作り、同じ検索を何度も使い回すと前処理の元が取れる。
    - `<functional>` にある（`<algorithm>` ではない）。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::boyer_moore_horspool_searcher {#boyer_moore_horspool_searcher}

```cpp
template <class ForwardIt, class Pred = equal_to<>>
class boyer_moore_horspool_searcher {
 public:
  boyer_moore_horspool_searcher(ForwardIt pat_first, ForwardIt pat_last, Pred pred = Pred());
  template <class It> pair<It, It> operator()(It first, It last) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pat_first, pat_last` | イテレータ | 探したいパターンの範囲 |
| `pred` | 述語 | 省略可。要素を比べる述語 |

- 戻り値: `operator()` は見つかった範囲の `pair`（見つからなければ `{last, last}`）
- 計算量: 平均はテキスト長より小さい（最悪は線形 × パターン長）


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
                        std::boyer_moore_horspool_searcher(pat.begin(), pat.end()));
  std::println("{}", it - text.begin());
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログの長い文字列から特定のパターンを探す | `std::search(text.begin(), text.end(), std::boyer_moore_horspool_searcher(pat.begin(), pat.end()));` |

## よくあるミス

??? failure "短いテキストで使う"
    前処理のコストがかかるので、短いテキストを 1 回探すだけなら素朴な `std::search` のほうが速いことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`search`](../../algorithms/search.md) | 検索オブジェクトを受け取る |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボイヤー・ムーア・ホースプール法（簡略版）
    - [x] `std::search` の第 3 引数に渡す
    - [x] 同じパターンを何度も探すなら使い回す

## 関連ページ

- [cpprefjp: std::boyer_moore_horspool_searcher](https://cpprefjp.github.io/reference/functional/boyer_moore_horspool_searcher.html)
- [cppreference: std::boyer_moore_horspool_searcher](https://en.cppreference.com/w/cpp/utility/functional/boyer_moore_horspool_searcher)
