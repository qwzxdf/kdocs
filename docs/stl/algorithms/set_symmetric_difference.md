---
title: std::ranges::set_symmetric_difference
summary: "整列済みの 2 つの範囲の、どちらか片方にだけある要素を作る。"
order: 83
tags:
  - アルゴリズム
---

# std::ranges::set_symmetric_difference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::set_symmetric_difference` は、**2 つの範囲の、どちらか片方にだけ入っている要素**（対称差）を作ります。「共通部分を除いた全部」です。2 つのリストの違いを調べるときに使います。

!!! tip "ポイント"
    - `(A - B) と (B - A)` を合わせたもの。
    - 入力の 2 つは**整列済み**であること。
    - 結果の書き出し先は十分な大きさに。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::set_symmetric_difference {#set_symmetric_difference}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr set_symmetric_difference_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_symmetric_difference(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
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

  std::ranges::set_symmetric_difference(a, b, std::back_inserter(out));
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2, 6, 7]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのセーブデータの違いをすべて挙げる | `set_symmetric_difference(a, b, out)` |
| 2 つのフレンドリストで、共通でない人 | `set_symmetric_difference(...)` |

## よくあるミス

??? failure "整列していない範囲に使う"
    整列済みでないと、結果は不正です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::set_difference`](set_difference.md) | 片方向の差 |
| [`std::ranges::set_union`](set_union.md) | 和集合 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] どちらか片方だけにある要素
    - [x] 差集合を両方向にしたもの
    - [x] 入力は整列済み

## 関連ページ

- [cpprefjp: std::ranges::set_symmetric_difference](https://cpprefjp.github.io/reference/algorithm/ranges_set_symmetric_difference.html)
- [cppreference: std::ranges::set_symmetric_difference](https://en.cppreference.com/w/cpp/algorithm/ranges/set_symmetric_difference)
