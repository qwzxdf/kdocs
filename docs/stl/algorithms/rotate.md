---
title: std::ranges::rotate
summary: "範囲の要素を回転させる（指定した要素が先頭に来る）。"
order: 35
tags:
  - アルゴリズム
---

# std::ranges::rotate

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::rotate` は、**範囲の要素を巡回させて、指定した要素が先頭に来るようにする**アルゴリズムです。`{1, 2, 3, 4, 5}` を「3 が先頭」にすると `{3, 4, 5, 1, 2}` になります。ターン制ゲームの順番の回し方、メニューの項目の巡回に向いています。

!!! tip "ポイント"
    - 第 2 引数は「**新しく先頭になる要素の位置**」。何個ずらすか、ではない。
    - 先頭を末尾へ 1 つ回すなら、`rotate(v, v.begin() + 1)`。
    - 値のコピーを作らず、要素の並びだけを O(n) で入れ替える。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

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

<div class="anim" data-label="std::rotate(b, b + 2, e)">
1 2 3 4 5 # v
1 2 3 4 5 # 2 番目の要素（3）を先頭にしたい
>3 >4 >5 >1 >2 # 前後を入れ替えるように回転する
</div>

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


### rotate_copy の使い方

回転した結果を、元を残したまま別の場所に書く `rotate_copy` もあります。

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};
  std::vector<int> out;

  // 3（v.begin() + 2）が先頭になるように回した結果を、out に作る
  std::ranges::rotate_copy(v, v.begin() + 2, std::back_inserter(out));
  std::println("{} → {}", v, out);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5] → [3, 4, 5, 1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ターン制の行動順を 1 人ぶん進める | `rotate(order, order.begin() + 1)` |
| メニューの選択肢を巡回させる | `rotate(items, 新しい先頭)` |
| リングバッファ風の並びを、先頭から読めるように整える | `rotate(buffer, buffer.begin() + head)` |

## よくあるミス

??? failure "「何個ずらすか」を渡してしまう"
    第 2 引数は個数ではなくイテレータです。2 個ずらしたいなら `v.begin() + 2`。

??? failure "end() を渡す"
    `end()` を渡しても何も起きません（全部が前の部分になるだけ）。新しい先頭は `[begin, end)` の中を指します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::reverse`](reverse.md) | 並びを逆にする |
| [`std::ranges::shift_left`](shift_left.md) | ずらして、空いた所は放置する（回転しない） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 新しい先頭の位置を渡す
    - [x] 先頭を末尾へ回すなら `begin() + 1`
    - [x] 結果を残したままなら `rotate_copy`

## 関連ページ

- [cpprefjp: std::ranges::rotate](https://cpprefjp.github.io/reference/algorithm/ranges_rotate.html)
- [cppreference: std::ranges::rotate](https://en.cppreference.com/w/cpp/algorithm/ranges/rotate)
