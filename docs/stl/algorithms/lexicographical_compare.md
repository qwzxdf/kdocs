---
title: std::ranges::lexicographical_compare
summary: "2 つの範囲を辞書順で比べて、前のほうが小さいかを調べる。"
order: 43
tags:
  - アルゴリズム
---

# std::ranges::lexicographical_compare

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::lexicographical_compare` は、**2 つの範囲を辞書順（先頭から順に比べる）で比べて、最初の範囲のほうが小さいか**を返します。文字列の `<` と同じ規則を、`vector` など任意の範囲に使えます。

!!! tip "ポイント"
    - 先頭から比べて、最初に違った要素で大小が決まる。
    - 片方が片方の先頭部分なら、**短いほうが小さい**（`"ab"` < `"abc"`）。
    - コンテナどうしの `<` も同じ規則なので、普段は `a < b` で足りる。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 関数の詳しい説明

### std::ranges::lexicographical_compare {#lexicographical_compare}

```cpp
template <input_range R1, input_range R2, class Proj1 = identity, class Proj2 = identity,
          indirect_strict_weak_order<projected<iterator_t<R1>, Proj1>,
                                     projected<iterator_t<R2>, Proj2>> Comp = ranges::less>
constexpr bool lexicographical_compare(R1&& r1, R2&& r2, Comp comp = {},
                                       Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | 比べる 2 つ | 省略不可 |
| `comp` | 関数 | 「小さい」の判定 | `<` |
| `proj1`, `proj2` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: `r1` が `r2` より辞書順で小さければ `true`、そうでなければ `false`（等しいときも `false`）
- 計算量: 最大で `min(長さ1, 長さ2)` 回の比較

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

int main() {
  std::string a = "apple";
  std::string b = "apricot";
  // 3 文字目で 'p' < 'r' なので、a のほうが小さい
  std::println("{}", std::ranges::lexicographical_compare(a, b));

  std::vector<int> v1 = {1, 2};
  std::vector<int> v2 = {1, 2, 3};
  // v1 は v2 の先頭部分なので、短い v1 が小さい
  std::println("{}", std::ranges::lexicographical_compare(v1, v2));

  // 等しいときは false
  std::println("{}", std::ranges::lexicographical_compare(v1, v1));
}
```

```text title="実行結果"
true
true
false
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` など | 大小の決め方を変える |
| `proj1` / `proj2` | <span class="rank rank-rare">知ってるだけ</span> | `&Type::member` | 比べる前に、メンバを取り出す |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バージョン番号の比較（`{1, 2, 0}` と `{1, 10, 0}`） | `lexicographical_compare(v1, v2)` |
| 名前の並べ替えの比較関数 | `sort` の `comp` の中で使う |

## よくあるミス

??? failure "「全体の大きさ」の比較だと思ってしまう"
    辞書順は先頭の要素が優先です。`{1, 100}` は `{2, 0}` より**小さい**（先頭の 1 < 2）。合計や長さで比べたいなら、別に計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| `a < b`（コンテナ） | 同じ辞書順。普段はこれで足りる |
| [`std::ranges::equal`](equal.md) | 等しいかを調べる |
| `a <=> b` | 小さい・等しい・大きいを 1 回で調べる（三方比較） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 辞書順で「前のほうが小さいか」を返す
    - [x] 先頭部分が同じなら短いほうが小さい
    - [x] コンテナの `<` と同じ規則

## 関連ページ

- [cpprefjp: std::ranges::lexicographical_compare](https://cpprefjp.github.io/reference/algorithm/ranges_lexicographical_compare.html)
- [cppreference: std::ranges::lexicographical_compare](https://en.cppreference.com/w/cpp/algorithm/ranges/lexicographical_compare)
