---
title: std::ranges::remove_copy
summary: "条件に合わない要素だけを、別の場所へコピーする（元は変わらない）。"
order: 45
tags:
  - アルゴリズム
---

# std::ranges::remove_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::remove_copy` は、[`remove`](remove.md) の「コピー版」です。**元の範囲は変えずに**、ある値と等しくない要素だけを別の場所へコピーします。条件を渡す `remove_copy_if` もあります。

!!! tip "ポイント"
    - 元を残して、取り除いた結果だけが欲しいときに使う。
    - 書き出し先は十分な大きさに。`std::back_inserter` が安全。
    - `copy_if` の条件を反対にしたもの、と考えてもよい。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::remove_copy_if {#remove_copy_if}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Pred>
constexpr remove_copy_if_result<borrowed_iterator_t<R>, O>
remove_copy_if(R&& r, O result, Pred pred, Proj proj = {});
```

- `pred` が `true` の要素を除いたものを `result` に書き込みます（[copy_if](copy.md#copy_if) の逆）

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 1, 3};
  std::vector<int> replaced;
  std::ranges::replace_copy(v, std::back_inserter(replaced), 1, 9);
  std::vector<int> without_one;
  std::ranges::remove_copy_if(v, std::back_inserter(without_one), [](int x) { return x == 1; });
  auto rest = std::ranges::remove(v, 3);
  std::println("{} {} / remove 後の大きさ {} / 有効 {}", replaced, without_one, v.size(),
               rest.begin() - v.begin());
}
```

```text title="実行結果"
[9, 2, 9, 3] [2, 3] / remove 後の大きさ 4 / 有効 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 死んだ敵を除いた一覧を、元は残したまま作る | `remove_copy_if(enemies, back_inserter(alive), 死んでいる)` |

## よくあるミス

??? failure "条件の向きを間違える"
    `remove_copy_if` の条件は「**取り除く**もの」です。`copy_if` と逆なので注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::copy`](copy.md) | `copy_if` は残すものを指定する |
| [`std::ranges::remove`](remove.md) | 元の範囲の中で詰める |
| [`std::ranges::replace_copy`](replace_copy.md) | 置き換えた結果をコピー |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 取り除いた結果を別の場所へ作る
    - [x] 元は変わらない
    - [x] 条件は「取り除くもの」

## 関連ページ

- [cpprefjp: std::ranges::remove_copy](https://cpprefjp.github.io/reference/algorithm/ranges_remove_copy.html)
- [cppreference: std::ranges::remove_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/remove_copy)
