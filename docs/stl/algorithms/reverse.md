---
title: std::ranges::reverse / rotate
tags:
  - アルゴリズム
---

# std::ranges::reverse / rotate

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::reverse` は、**範囲の要素を逆の順番に並べ替える**関数です。`std::ranges::rotate` は、**指定した要素が先頭に来るように全体をぐるっと回します**。どちらも元の範囲そのものを書き換えます（新しい範囲は作りません）。

!!! tip "結論"
    - 元の順番を本当に入れ替えたいなら `reverse`。**見るだけなら `std::views::reverse`** のほうが軽い。
    - `rotate` は「順番待ちの先頭を最後に回す」ような処理に使える。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::reverse`](#reverse) | <span class="rank rank-sometimes">たまに</span> | 逆順に並べ替える | O(n) |
| [`std::ranges::rotate`](#rotate) | <span class="rank rank-rare">知ってるだけ</span> | 指定した要素が先頭に来るように回す | O(n) |
| [`std::ranges::reverse_copy`](#reverse_copy) | <span class="rank rank-rare">知ってるだけ</span> | 逆順にしたコピーを別の場所に作る | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> path = {1, 2, 3, 4};  // ゴールからスタートへたどった経路
  std::ranges::reverse(path);            // スタート → ゴールの順にする
  std::println("{}", path);
}
```

```text title="実行結果"
[4, 3, 2, 1]
```

A* などの経路探索は、ゴールから親をたどって経路を作るので、最後に `reverse` するのが定番です。

## 関数の詳しい説明

### std::ranges::reverse {#reverse}

```cpp
template <bidirectional_range R>
constexpr borrowed_iterator_t<R> reverse(R&& r);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 前後に進める範囲 | 逆順にする範囲（vector、string、list など） |

- 戻り値: 範囲の終わり（ほぼ使わない）
- 計算量: O(n)（要素を半分の回数だけ交換する）

```cpp
#include <algorithm>
#include <print>
#include <string>

int main() {
  std::string word = "level";
  std::string copy = word;
  std::ranges::reverse(copy);
  std::println("回文？ {}", word == copy);
}
```

```text title="実行結果"
回文？ true
```

### std::ranges::rotate {#rotate}

```cpp
template <forward_range R>
constexpr borrowed_subrange_t<R> rotate(R&& r, iterator_t<R> middle);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 回す範囲 |
| `middle` | イテレータ | **この要素が先頭に来る**ように回す |

- 戻り値: 元の先頭の要素が移った位置から終わりまでの範囲

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> turn = {"勇者", "魔法使い", "僧侶"};
  // 先頭の人の番が終わったら最後に回す
  std::ranges::rotate(turn, turn.begin() + 1);
  std::println("{}", turn);
}
```

```text title="実行結果"
["魔法使い", "僧侶", "勇者"]
```

### std::ranges::reverse_copy {#reverse_copy}

```cpp
template <bidirectional_range R, weakly_incrementable O>
constexpr reverse_copy_result<borrowed_iterator_t<R>, O> reverse_copy(R&& r, O result);
```

- 元はそのままで、逆順にしたものを `result` に書き込みます

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::vector<int> rev;
  std::ranges::reverse_copy(v, std::back_inserter(rev));
  std::println("{} {}", v, rev);
}
```

```text title="実行結果"
[1, 2, 3] [3, 2, 1]
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 経路探索の結果をスタートからの順にする | `reverse` |
| ターン順を回す | `rotate` |
| リプレイを逆再生する | `views::reverse`（見るだけ） |

## よくあるミス

??? failure "見るだけなのに reverse して元が壊れる"
    逆順に表示したいだけなら `for (auto& x : v | std::views::reverse)` を使います。`reverse` は元の並びを変えてしまいます。

## 理解度チェック

!!! question "Q1. `{1, 2, 3, 4, 5}` を `rotate(v, v.begin() + 2)` すると？"
    <div class="spoiler" markdown>

    **答え:** `{3, 4, 5, 1, 2}`。3 が先頭に来るように回ります。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::reverse`](views.md#reverse) | 元を変えずに逆順で見る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `reverse` は元を逆順に書き換える
    - [x] 見るだけなら `views::reverse`

## 関連ページ

- [cpprefjp: std::ranges::reverse](https://cpprefjp.github.io/reference/algorithm/ranges_reverse.html)
- [cppreference: std::ranges::reverse](https://en.cppreference.com/w/cpp/algorithm/ranges/reverse)
