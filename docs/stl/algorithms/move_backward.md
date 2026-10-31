---
title: std::ranges::move_backward
summary: "範囲の要素を、後ろから順にムーブして移す。"
order: 50
tags:
  - アルゴリズム
---

# std::ranges::move_backward

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

コンテナの途中に空きを作るために、要素を後ろへずらしたい。前から順にムーブすると、まだムーブしていない要素を、上書きしてしまいます。`std::move_backward` は、後ろから順にムーブするので、出力先が入力と重なって後ろにずれていても、正しく動きます。

!!! tip "ポイント"
    - 範囲を、後ろから順にムーブする
    - 出力先は、出力範囲の「終端」を渡す
    - 後ろへずらす（出力先が入力より後ろ）ときに使う
    - 前へずらすなら `std::move`（前から順）

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::move_backward {#move_backward}

<span class="ver ver-11">C++11</span>

```cpp
template <class BidirIt1, class BidirIt2>
BidirIt2 move_backward(BidirIt1 first, BidirIt1 last, BidirIt2 d_last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | 双方向イテレータ | ムーブ元の範囲 |
| `d_last` | 双方向イテレータ | ムーブ先の範囲の終端 |

`d_last` は終端なので、`d_last - (last - first)` から `d_last` までが、書き込み先です。

出力範囲が入力範囲と重なるとき、出力の先頭が入力の先頭より後ろなら `move_backward`、前なら `move` を使います。逆にすると、まだムーブしていない要素を壊します。

コピー版が `std::copy_backward` です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 0};  // 末尾に空きがある

  // [0, 4) を、1 つ後ろへずらす（重なっていても安全）
  std::move_backward(v.begin(), v.begin() + 4, v.end());
  v[0] = 9;  // 先頭に空いた場所へ入れる

  std::println("{}", v);
}
```

```text title="実行結果"
[9, 1, 2, 3, 4]
```

## ゲームでの使いどころ

配列の途中に要素を挿入するために、後ろの要素をずらす処理に使います。`vector::insert` の内部と同じ考え方です。

## よくあるミス

??? failure "重なっているのに std::move を使う"
    要素が壊れます。後ろへずらすときは `move_backward` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`move`](move.md) | 前から順にムーブ |
| [`copy_backward`](copy_backward.md) | コピー版 |
| [`shift_right`](shift_right.md) | 同じ効果の簡単な書き方 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::move_backward](https://cpprefjp.github.io/reference/algorithm/ranges_move_backward.html)
- [cppreference: std::ranges::move_backward](https://en.cppreference.com/w/cpp/algorithm/ranges/move_backward)
