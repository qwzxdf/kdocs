---
title: std::ranges::is_permutation
summary: "2 つの範囲が、並べ替えれば同じになる（要素の種類と数が同じ）かを調べる。"
order: 44
tags:
  - アルゴリズム
---

# std::ranges::is_permutation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::is_permutation` は、**片方を並べ替えればもう片方と同じになるか**（要素の種類と個数が同じか）を調べます。並び順は気にしません。

!!! tip "ポイント"
    - `{1, 2, 3}` と `{3, 1, 2}` は `true`、`{1, 2, 3}` と `{1, 2, 2}` は `false`。
    - 並べ替えて比べるのではなく、元の範囲を変えずに調べる（その代わり計算量は最悪 O(n²)）。
    - 「ピースが全部そろっているか」「手札が同じ組み合わせか」の判定に向く。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 関数の詳しい説明

### std::ranges::is_permutation {#is_permutation}

```cpp
template <forward_range R1, forward_range R2, class Proj1 = identity, class Proj2 = identity,
          class Pred = ranges::equal_to>
constexpr bool is_permutation(R1&& r1, R2&& r2, Pred pred = {},
                              Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | 比べる 2 つ | 省略不可 |
| `pred` | 関数 | 「等しい」の判定 | `==` |
| `proj1`, `proj2` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 要素の種類と個数が同じなら `true`。長さが違えば `false`
- 計算量: 長さが同じで中身も同じ並び順なら O(n)、最悪 O(n²)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> goal = {1, 2, 3};
  std::vector<int> shuffled = {3, 1, 2};
  std::vector<int> broken = {1, 2, 2};

  std::println("{}", std::ranges::is_permutation(goal, shuffled));
  std::println("{}", std::ranges::is_permutation(goal, broken));
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パズルのピースが全部そろっているか | `is_permutation(pieces, all_pieces)` |
| 手札が同じ組み合わせか | `is_permutation(hand, expected)` |
| テストで、順序が決まっていない結果の確認 | `is_permutation(result, expected)` |

## よくあるミス

??? failure "大きな範囲に何度も使う"
    最悪 O(n²) です。要素が数千を超えるなら、どちらも `sort` してから [`equal`](equal.md) で比べるほうが速くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::equal`](equal.md) | 並び順まで同じかを調べる |
| [`std::next_permutation`](next_permutation.md) | 次の並べ替えの順列を作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並べ替えれば同じになるか、を調べる
    - [x] 並び順は無視、種類と個数を見る
    - [x] 最悪 O(n²)

## 関連ページ

- [cpprefjp: std::ranges::is_permutation](https://cpprefjp.github.io/reference/algorithm/ranges_is_permutation.html)
- [cppreference: std::ranges::is_permutation](https://en.cppreference.com/w/cpp/algorithm/ranges/is_permutation)
