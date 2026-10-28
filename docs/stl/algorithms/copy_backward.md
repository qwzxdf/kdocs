---
title: std::ranges::copy_backward
summary: "範囲を、後ろの要素から順にコピーする（コピー先が後ろに重なるとき）。"
order: 48
tags:
  - アルゴリズム
---

# std::ranges::copy_backward

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::copy_backward` は、**範囲を後ろの要素から順にコピーする**アルゴリズムです。コピー元とコピー先が**重なっていて、コピー先が後ろ**にあるとき、[`copy`](copy.md) の代わりに使います。配列の途中に空きを作る（要素を 1 つずつ後ろへずらす）ときの定番です。

!!! tip "ポイント"
    - コピー先は**終わりの位置**を渡す（`copy` は先頭の位置）。
    - 前へずらす（コピー先が前）なら `copy`、後ろへずらす（コピー先が後ろ）なら `copy_backward`。
    - コンテナの途中に挿入するなら、`vector::insert` が内部でこれをやってくれる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::copy_backward {#copy_backward}

```cpp
template <bidirectional_range R, bidirectional_iterator I>
constexpr copy_backward_result<borrowed_iterator_t<R>, I> copy_backward(R&& r, I result);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | コピー元 |
| `result` | イテレータ | コピー先の**終わりの位置**（最後にコピーされる要素の次） |

- 戻り値: `in`（コピー元の終わり）と `out`（コピー先で最後に書いた位置）の組
- 計算量: 要素数 n に対して、ちょうど n 回の代入

```cpp
#include <algorithm>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 0};  // 末尾に空きが 1 つある

  // 先頭の 5 個を 1 つ後ろへずらす（v の終わりをコピー先の終わりにする）
  std::ranges::copy_backward(std::ranges::subrange(v.begin(), v.begin() + 5), v.end());
  v[0] = 99;  // 空いた先頭に新しい値を入れる
  std::println("{}", v);
}
```

```text title="実行結果"
[99, 1, 2, 3, 4, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パーティの並びの途中にメンバーを割り込ませる | 後ろへずらしてから、空いた所に入れる |
| 固定長の配列で、挿入のための場所を空ける | `copy_backward(range, end)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| コピー先がコピー元の範囲の内側に入る（`result` が `r` の (begin, end] にある） | 未定義動作 |

## よくあるミス

??? failure "コピー先に「先頭」を渡してしまう"
    `copy_backward` のコピー先は**終わりの位置**です。先頭を渡すと、先頭より前の範囲外に書き込みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::copy`](copy.md) | 前から順にコピー（コピー先が前に重なるとき） |
| [`std::ranges::move_backward`](move_backward.md) | 後ろからコピーせず移す |
| `std::vector::insert` | 途中への挿入。内部でこの処理をしてくれる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 後ろの要素から順にコピーする
    - [x] コピー先は**終わりの位置**を渡す
    - [x] 後ろへずらすときの定番

## 関連ページ

- [cpprefjp: std::ranges::copy_backward](https://cpprefjp.github.io/reference/algorithm/ranges_copy_backward.html)
- [cppreference: std::ranges::copy_backward](https://en.cppreference.com/w/cpp/algorithm/ranges/copy_backward)
