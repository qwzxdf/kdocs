---
title: std::ranges::find_first_of
summary: "範囲の中で、候補のどれかと等しい最初の要素を探す。"
order: 65
tags:
  - アルゴリズム
---

# std::ranges::find_first_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::find_first_of` は、**範囲の中から、候補のうちどれかと等しい要素を、先頭から順に探して最初のものを返す**関数です。「この文字のどれかが最初に出てくる所」を探すときに使います。

!!! tip "ポイント"
    - 候補を **1 つずつ** [`find`](find.md) で探すより、まとめて探せる。
    - 戻り値は `r1` 側のイテレータ。見つからなければ `end()`。
    - 計算量は O(n·m)（n は `r1`、m は候補の数）。候補が多いなら `set` で調べるほうが速い。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::find_first_of {#find_first_of}

```cpp
template <input_range R1, forward_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr borrowed_iterator_t<R1> find_first_of(R1&& r1, R2&& r2, Pred pred = {},
                                               Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1` | 範囲 | 探す場所 |  |
| `r2` | 範囲 | 候補の集まり |  |
| `pred` | 関数 | 「等しい」の判定 | `==` |

- 戻り値: `r1` の中で、`r2` のどれかと等しい最初の要素のイテレータ。無ければ `end()`
- 計算量: O(n·m)

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 5, 3, 4};
  std::array targets = {7, 3, 5};

  auto it = std::ranges::find_first_of(v, targets);
  if (it != v.end()) {
    std::println("最初にヒットしたのは {}（{} 番目）", *it, it - v.begin() + 1);
  }
}
```

```text title="実行結果"
最初にヒットしたのは 5（3 番目）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 倒すべき敵 ID のどれかが最初に出た位置 | `find_first_of(enemy_ids, targets)` |
| 区切り文字のどれかが最初に出る位置 | `find_first_of(text, " ,;")` |

## よくあるミス

??? failure "候補の順番で「最初」だと思う"
    「最初」は `r1`（探す側）の順番です。`r2` の先頭の候補が優先されるわけではありません。上の例でも、`targets` の先頭は 7 ですが、結果は `v` で先に出てくる 5 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](find.md) | 1 つの値を探す |
| `std::string::find_first_of` | 文字列専用のメンバ関数 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 候補のどれかが最初に出る位置を探す
    - [x] 「最初」は探す側の順番
    - [x] O(n·m)

## 関連ページ

- [cpprefjp: std::ranges::find_first_of](https://cpprefjp.github.io/reference/algorithm/find_first_of.html)
- [cppreference: std::find_first_of](https://en.cppreference.com/w/cpp/algorithm/find_first_of)
