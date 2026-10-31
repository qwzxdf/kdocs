---
title: std::ranges::find_end
summary: "範囲の中で、別の範囲の並びが最後に現れる場所を探す。"
order: 66
tags:
  - アルゴリズム
---

# std::ranges::find_end

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

文字列の中から、部分文字列が<strong>最後に</strong>現れる位置を探したい。`std::find_end(first, last, s_first, s_last)` は、`[first, last)` の中で、`[s_first, s_last)` と同じ並びが最後に現れる位置を返します。名前の「end」は、「最後の」の意味です。

!!! tip "ポイント"
    - 部分列が最後に現れる位置の先頭を返す
    - 見つからなければ `last`
    - 最初の位置なら `std::search`
    - 述語を渡して、比較を変えられる

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::find_end {#find_end}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class ForwardIt1, class ForwardIt2>
ForwardIt1 find_end(ForwardIt1 first, ForwardIt1 last, ForwardIt2 s_first, ForwardIt2 s_last);
```

探す列が空のときは、`last` を返します。

名前が紛らわしく、「終端を探す」と誤解されがちです。「最後に現れる部分列を探す」です。

`std::string` なら、`s.rfind(sub)` のほうが簡潔です。汎用のコンテナの部分列には、`find_end` を使います。

C++20 の `std::ranges::find_end` は、部分範囲を返します。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3, 1, 2, 3, 4};
  const std::vector<int> sub = {1, 2, 3};

  const auto last_pos = std::find_end(v.begin(), v.end(), sub.begin(), sub.end());
  std::println("最後に現れる位置: {}", last_pos - v.begin());

  const std::vector<int> missing = {9, 9};
  std::println("なければ end: {}",
               std::find_end(v.begin(), v.end(), missing.begin(), missing.end()) == v.end());
}
```

```text title="実行結果"
最後に現れる位置: 3
なければ end: true
```

## ゲームでの使いどころ

ログやコマンド列から、特定のパターンが最後に現れた位置を探すときに使います。

## よくあるミス

??? failure "終端を探す関数だと思う"
    最後に現れる部分列を探します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`search`](search.md) | 最初に現れる位置 |
| [`find`](find.md) | 1 要素を探す |
| `std::string::rfind` | 文字列の最後の位置 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::find_end](https://cpprefjp.github.io/reference/algorithm/ranges_find_end.html)
- [cppreference: std::ranges::find_end](https://en.cppreference.com/w/cpp/algorithm/ranges/find_end)
