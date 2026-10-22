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

巨大なテキストの中から長いパターンを探すとき、先頭から 1 文字ずつ比べると遅くなります。`boyer_moore_searcher` は、パターンを前処理して「ずらせる幅」を大きくとることで、速く探します。

!!! tip "ポイント"
    - `std::search(first, last, searcher)` に渡して使う。
    - パターンを渡して作り、同じ検索を何度も使い回すと前処理の元が取れる。
    - `<functional>` にある（`<algorithm>` ではない）。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::boyer_moore_searcher {#boyer_moore_searcher}

```cpp
template <class ForwardIt, class Pred = equal_to<>>
class boyer_moore_searcher {
 public:
  boyer_moore_searcher(ForwardIt pat_first, ForwardIt pat_last, Pred pred = Pred());
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
                        std::boyer_moore_searcher(pat.begin(), pat.end()));
  std::println("{}", it - text.begin());
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログの長い文字列から特定のパターンを探す | `std::search(text.begin(), text.end(), std::boyer_moore_searcher(pat.begin(), pat.end()));` |

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
    - [x] ボイヤー・ムーア法（長いパターン向き）
    - [x] `std::search` の第 3 引数に渡す
    - [x] 同じパターンを何度も探すなら使い回す

## 関連ページ

- [cpprefjp: std::boyer_moore_searcher](https://cpprefjp.github.io/reference/functional/boyer_moore_searcher.html)
- [cppreference: std::boyer_moore_searcher](https://en.cppreference.com/w/cpp/utility/functional/boyer_moore_searcher)
