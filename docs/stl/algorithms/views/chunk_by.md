---
title: std::views::chunk_by
summary: "隣り合う要素の条件で、範囲を塊に区切って見る。"
order: 37
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::chunk_by

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::chunk_by(pred)` は、**隣り合う 2 つの要素が条件を満たす間を 1 つの塊として、塊に区切る**ビューです。「連続した数字をまとめる」「同じ種類が続く間をまとめる」のように、**条件が崩れた所で区切る**使い方ができます。

!!! tip "ポイント"
    - 条件は `pred(前, 後)` の形。`true` の間は同じ塊。
    - 塊は元の順序のまま、連続した範囲になる。
    - `chunk` は個数で区切るが、`chunk_by` は条件で区切る。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::chunk_by {#chunk_by}

```cpp
r | std::views::chunk_by(pred)
std::views::chunk_by(r, pred)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pred` | 関数 | 隣り合う 2 つの要素（前, 後）を受け取り、同じ塊なら `true` |

- 戻り値: 塊（部分範囲）を並べたビュー
- 計算量: O(1) 償却（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 4, 5, 7, 8};

  // 連続した数字（前+1 == 後）をまとめる
  auto groups = v
              | std::views::chunk_by([](int a, int b) { return b == a + 1; })
              | std::ranges::to<std::vector<std::vector<int>>>();
  std::println("{}", groups);
}
```

```text title="実行結果"
[[1, 2], [4, 5], [7, 8]]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 連続した入力フレームをグループにまとめる | `frames | chunk_by(連続している)` |
| 整列済みのスコアを、同じ値ごとにまとめる | `scores | chunk_by(等しい)` |

## よくあるミス

??? failure "条件の向きを逆にする"
    条件は「**同じ塊に入れる**」とき `true` です。区切りたいときに `true` ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::chunk`](chunk.md) | 個数で区切る |
| [`std::views::split`](split.md) | 区切りの値で分ける |
| [`std::ranges::adjacent_find`](../adjacent_find.md) | 条件に合う隣り合いを探す |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件が崩れた所で区切る
    - [x] `pred(前, 後)` が真の間は同じ塊
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::chunk_by_view](https://cpprefjp.github.io/reference/ranges/chunk_by_view.html)
- [cppreference: std::ranges::chunk_by_view](https://en.cppreference.com/w/cpp/ranges/chunk_by_view)
