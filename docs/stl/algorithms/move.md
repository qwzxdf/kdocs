---
title: std::ranges::move
summary: "範囲の要素を、コピーせずに別の場所へ「移す」。"
order: 49
tags:
  - アルゴリズム
---

# std::ranges::move

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::move`（アルゴリズムのほう）は、**範囲の要素を 1 つずつムーブして、別の場所に移す**関数です。[`std::move`](../utilities/move.md)（1 つの値を右辺値にする関数）とは別のものです。`std::string` や `std::unique_ptr` のような、**コピーが重い・できない**要素の受け渡しに使います。

!!! tip "ポイント"
    - `copy` と同じ形で、中身を**コピーする代わりにムーブ**する。
    - 移したあとの元の要素は「有効だが中身は不定」。**読まずに、代入し直すか捨てる**。
    - `unique_ptr` の `vector` を別の `vector` に渡すときは、`copy` ができないので、これを使う。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::move {#move}

```cpp
template <input_range R, weakly_incrementable O>
constexpr move_result<borrowed_iterator_t<R>, O> move(R&& r, O result);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 移す元 |
| `result` | イテレータ | 移し先の先頭 |

- 戻り値: `in`（移す元の終わり）と `out`（移し先で最後に書いた位置の次）の組
- 計算量: 要素数 n に対して、n 回のムーブ代入

```cpp
#include <algorithm>
#include <memory>
#include <print>
#include <vector>

int main() {
  std::vector<std::unique_ptr<int>> src;
  src.push_back(std::make_unique<int>(10));
  src.push_back(std::make_unique<int>(20));

  std::vector<std::unique_ptr<int>> dst(2);
  // unique_ptr はコピーできないので、copy ではなく move を使う
  std::ranges::move(src, dst.begin());

  std::println("{} {}", *dst[0], *dst[1]);
  std::println("元は空になった？ {}", src[0] == nullptr);
}
```

```text title="実行結果"
10 20
元は空になった？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `unique_ptr` で持つオブジェクトのリストを、別のリストに渡す | `move(src, dst.begin())` |
| 巨大な文字列の配列を、コピーせずに別のコンテナへ移す | `move(strings, back_inserter(other))` |

## よくあるミス

??? failure "ムーブしたあとの元の要素を使う"
    移したあとの要素は「有効だが中身は不定」です。上の `unique_ptr` のように `nullptr` になるものもあれば、`int` のようにそのまま残るものもあります。移したあとは読まないようにします。

??? failure "`std::move`（1 値）と混同する"
    `std::move(x)` は 1 つの値を右辺値にするキャストです。`std::ranges::move(range, out)` は範囲の要素をまとめて移すアルゴリズムです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::copy`](copy.md) | コピーする |
| [`std::ranges::move_backward`](move_backward.md) | 後ろからムーブする |
| [`std::move`](../utilities/move.md) | 1 つの値を右辺値にする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の要素をムーブして移す
    - [x] 元の要素は不定になる
    - [x] `unique_ptr` の受け渡しに使える

## 関連ページ

- [cpprefjp: std::ranges::move](https://cpprefjp.github.io/reference/algorithm/ranges_move.html)
- [cppreference: std::ranges::move](https://en.cppreference.com/w/cpp/algorithm/ranges/move)
