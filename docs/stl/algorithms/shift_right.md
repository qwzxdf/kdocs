---
title: std::shift_right
summary: "範囲の要素を、後ろ（右）へずらす。空いた前は放置する。"
order: 70
tags:
  - アルゴリズム
---

# std::shift_right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::shift_right` は、**範囲の要素を n 個ぶん、後ろ（右）へずらす**関数です。はみ出した末尾の要素は捨てられ、先頭の空いた部分は**放置**されます（値は不定）。

!!! tip "ポイント"
    - 戻り値は、ずらした結果の有効な範囲の**先頭**。それより前は不定。
    - 先頭に新しい要素を入れたいときの準備になる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::shift_right {#shift_right}

```cpp
template <class ForwardIt>
constexpr ForwardIt shift_right(ForwardIt first, ForwardIt last,
                                typename std::iterator_traits<ForwardIt>::difference_type n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | ずらす範囲 |
| `n` | 整数 | ずらす個数 |

- 戻り値: 有効になった範囲の先頭のイテレータ
- 計算量: O(要素数)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  auto new_begin = std::shift_right(v.begin(), v.end(), 2);  // 後ろへ 2 つずらす
  v.erase(v.begin(), new_begin);                             // 先頭の不定な部分を消す
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長の履歴バッファで、古いものを後ろへ押し出す | `shift_right(history.begin(), history.end(), 1)` のあと、先頭に新しい値 |

## よくあるミス

??? failure "先頭の不定な要素を読む"
    ずらしたあとの先頭は不定です。新しい値を代入してから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shift_left`](shift_left.md) | 前へずらす |
| [`std::ranges::rotate`](rotate.md) | 回転（要素を捨てない） |

## コンパイラ対応

C++20 の機能です。ranges 版は C++26 で追加される予定です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個ぶん後ろへずらす
    - [x] 先頭は不定
    - [x] はみ出た要素は捨てられる

## 関連ページ

- [cpprefjp: std::shift_right](https://cpprefjp.github.io/reference/algorithm/shift_right.html)
- [cppreference: std::shift_right](https://en.cppreference.com/w/cpp/algorithm/shift)
