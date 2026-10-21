---
title: std::views::adjacent
summary: "隣り合う n 個を、1 つの組にして順にずらしながら見る。"
order: 33
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::adjacent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::adjacent<N>` は、**隣り合う N 個の要素を 1 つの組にして、1 つずつずらしながら並べる**ビューです。`adjacent<2>` なら、`(1,2)`, `(2,3)`, `(3,4)` …と、前後の組になります。折れ線の各線分、フレームごとの変化量を調べるのに便利です。

!!! tip "ポイント"
    - `adjacent<2>` が最もよく使う（前後の 2 つ）。
    - [`slide`](slide.md) と似ているが、`adjacent` は**組（tuple）**、`slide` は**範囲**として返す。N がコンパイル時に決まる場合は `adjacent` が速い。
    - 要素数が N 未満なら、空になる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::adjacent {#adjacent}

```cpp
r | std::views::adjacent<N>
std::views::adjacent<N>(r)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `N` | テンプレート引数 | 組にする個数（コンパイル時に決まる値） |

- 戻り値: 隣り合う N 個の組を並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> points = {1, 4, 9, 16};

  for (auto [a, b] : points | std::views::adjacent<2>) {
    std::println("{} -> {}", a, b);
  }
}
```

```text title="実行結果"
1 -> 4
4 -> 9
9 -> 16
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 折れ線（点の並び）を、線分のペアにして描画する | `points | adjacent<2>` |
| 隣り合うフレームの値の差を調べる | `values | adjacent<2>` |

## よくあるミス

??? failure "要素 1 つのときに空になるのを忘れる"
    `adjacent<2>` は要素が 1 つ以下だと、何も出ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::slide`](slide.md) | 範囲として返す（N が実行時に決まる） |
| [`std::views::adjacent_transform`](adjacent_transform.md) | 組に関数を適用する |
| [`std::ranges::adjacent_find`](../adjacent_find.md) | 条件に合う隣り合いを探す |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣り合う N 個の組
    - [x] `adjacent<2>` が定番
    - [x] 構造化束縛で受ける

## 関連ページ

- [cpprefjp: std::ranges::adjacent_view](https://cpprefjp.github.io/reference/ranges/adjacent_view.html)
- [cppreference: std::ranges::adjacent_view](https://en.cppreference.com/w/cpp/ranges/adjacent_view)
