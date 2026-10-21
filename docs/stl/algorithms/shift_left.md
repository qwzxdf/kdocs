---
title: std::shift_left
summary: "範囲の要素を、前（左）へずらす。空いた後ろは放置する。"
order: 69
tags:
  - アルゴリズム
---

# std::shift_left

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::shift_left` は、**範囲の要素を n 個ぶん、前（左）へずらす**関数です。回転（[`rotate`](rotate.md)）と違い、はみ出した先頭の要素は捨てられ、後ろの空いた部分は**放置**されます（値は不定）。`std::ranges::shift_left` はありません（C++23 時点）。

!!! tip "ポイント"
    - 戻り値は、ずらした結果の有効な範囲。その後ろは不定。
    - 後ろを消すなら、戻り値の終わりから `erase` する。
    - `rotate` と違って、はみ出た要素は戻ってこない。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::shift_left {#shift_left}

```cpp
template <class ForwardIt>
constexpr ForwardIt shift_left(ForwardIt first, ForwardIt last,
                               typename std::iterator_traits<ForwardIt>::difference_type n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | ずらす範囲 |
| `n` | 整数 | ずらす個数（0 以下は何もしない） |

- 戻り値: 有効になった範囲の終わりのイテレータ（`n` が大きいと `first`）
- 計算量: O(要素数)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  auto new_end = std::shift_left(v.begin(), v.end(), 2);  // 前へ 2 つずらす
  v.erase(new_end, v.end());                              // 後ろの不定な部分を消す
  std::println("{}", v);
}
```

```text title="実行結果"
[3, 4, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| タイムラインの先頭の古いデータを捨てる | `shift_left(buf.begin(), buf.end(), n)` |
| スクロールするログ表示 | 先頭の n 行を捨てる |

## よくあるミス

??? failure "後ろの不定な要素を読む"
    ずらしたあとの末尾は不定です。`erase` するか、戻り値までしか読まないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shift_right`](shift_right.md) | 後ろへずらす |
| [`std::ranges::rotate`](rotate.md) | 回転（要素を捨てない） |
| `std::vector::erase` | 先頭の要素を消す。ずらしは内部で行われる |

## コンパイラ対応

C++20 の機能です。ranges 版（`std::ranges::shift_left`）は C++26 で追加される予定です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個ぶん前へずらす
    - [x] 後ろは不定
    - [x] はみ出た要素は捨てられる

## 関連ページ

- [cpprefjp: std::shift_left](https://cpprefjp.github.io/reference/algorithm/shift_left.html)
- [cppreference: std::shift_left](https://en.cppreference.com/w/cpp/algorithm/shift)
