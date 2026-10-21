---
title: std::ranges::reverse
summary: "範囲の並びを逆順にする（コピーして逆順にする版もある）。"
order: 34
tags:
  - アルゴリズム
---

# std::ranges::reverse

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::reverse` は、**範囲の要素の並びを逆順にする**アルゴリズムです。その場で並びを入れ替えます。元を残したまま、逆順のコピーを別の場所に作る `reverse_copy` もあります。

!!! tip "ポイント"
    - 元の並びを残したいなら、`reverse_copy`、または [`views::reverse`](views/reverse.md)（コピーせずに逆順で「見る」）。
    - 昇順に並べたものを降順にしたいなら、`sort` に `std::greater{}` を渡すほうが一度で済む。
    - 計算量は O(n)（要素の入れ替えが n/2 回）。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

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

<div class="anim" data-label="std::ranges::reverse(v)">
1 2 3 4 5 # v
>5 2 3 4 >1 # 両端を入れ替える
5 >4 3 >2 1 # 内側へ進む
5 4 3 2 1 # 完了
</div>

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

| 関数 | 重要度 | 意味 |
| --- | --- | --- |
| `reverse` | <span class="rank rank-sometimes">たまに</span> | その場で逆順にする |
| `reverse_copy` | <span class="rank rank-rare">知ってるだけ</span> | 逆順にしたコピーを別の場所へ書く |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 履歴（新しい順）を表示用に古い順へ並べ直す | `reverse(history)` |
| 文字列を逆順にする | `reverse(text)` |
| 描画順を前後ひっくり返す | `reverse(draw_list)` |

## よくあるミス

??? failure "逆順に「見る」だけでいいのに、並びを書き換える"
    表示のためだけなら、`std::views::reverse` で元の `vector` を変えずに逆順で走査できます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::reverse`](views/reverse.md) | コピーも書き換えもせず、逆順で「見る」 |
| [`std::ranges::rotate`](rotate.md) | 先頭の要素を末尾へ回す |
| [`std::ranges::sort`](sort.md) | 大きい順に並べ替える |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並びを逆順にする
    - [x] コピーする版は `reverse_copy`
    - [x] 見るだけなら `views::reverse`

## 関連ページ

- [cpprefjp: std::ranges::reverse](https://cpprefjp.github.io/reference/algorithm/ranges_reverse.html)
- [cppreference: std::ranges::reverse](https://en.cppreference.com/w/cpp/algorithm/ranges/reverse)
