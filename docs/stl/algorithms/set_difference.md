---
title: std::ranges::set_difference
summary: "整列済みの 2 つの範囲の「差集合」（前にだけある要素）を作る。"
order: 82
tags:
  - アルゴリズム
---

# std::ranges::set_difference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::set_difference` は、**最初の範囲にあって、2 番目の範囲にない要素**（差集合）を作ります。「新しいセーブデータで増えたアイテム」「まだ解放していないステージ」を求めるときに使います。

!!! tip "ポイント"
    - 順番が大事: `A - B` と `B - A` は違う。
    - 入力の 2 つは**整列済み**であること。
    - 結果の書き出し先は十分な大きさに。`std::back_inserter` が安全。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::set_difference {#set_difference}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr set_difference_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_difference(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | **整列済み**の 2 つの範囲 |  |
| `result` | 出力イテレータ | 結果の書き出し先。`std::back_inserter(out)` が安全 |  |
| `comp` | 関数 | 整列した順の比較 | `<` |

- 戻り値: `in1`、`in2`、`out`（結果の書き出しの終わり）を持つ構造体
- 計算量: O(n + m)

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3, 4, 5};
  std::vector<int> b = {3, 4, 5, 6, 7};
  std::vector<int> out;

  std::ranges::set_difference(a, b, std::back_inserter(out));  // a にあって b にない
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| まだ解放していないステージの一覧 | `set_difference(all_stages, unlocked, out)` |
| 更新前後の差分（消えた ID） | `set_difference(old_ids, new_ids, out)` |

## よくあるミス

??? failure "引数の順番を取り違える"
    `set_difference(a, b)` は「a にあって b にない」です。逆にしたいなら `set_difference(b, a)`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::set_symmetric_difference`](set_symmetric_difference.md) | どちらか片方だけにある要素 |
| [`std::ranges::set_intersection`](set_intersection.md) | 共通部分 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前にだけある要素を作る
    - [x] 順番が大事（`A - B`）
    - [x] 入力は整列済み

## 関連ページ

- [cpprefjp: std::ranges::set_difference](https://cpprefjp.github.io/reference/algorithm/ranges_set_difference.html)
- [cppreference: std::ranges::set_difference](https://en.cppreference.com/w/cpp/algorithm/ranges/set_difference)
