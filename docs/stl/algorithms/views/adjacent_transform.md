---
title: std::views::adjacent_transform
summary: "隣り合う n 個に関数を適用した結果を並べる。"
order: 34
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::adjacent_transform

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::adjacent_transform<N>` は、**隣り合う N 個の要素を関数に渡し、その結果を並べる**ビューです。[`adjacent`](adjacent.md) して [`transform`](transform.md) するのを 1 つにしたものです。「前後の差」を一覧にするのに便利です。

!!! tip "ポイント"
    - 関数は N 個の引数を取る。
    - `adjacent_transform<2>(f)` なら、`f(v[0], v[1])`, `f(v[1], v[2])`, …。
    - 要素数が N 未満なら空。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::adjacent_transform {#adjacent_transform}

```cpp
r | std::views::adjacent_transform<N>(func)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `N` | テンプレート引数 | 渡す個数 |
| `func` | 関数 | N 個の引数を取り、結果を返す |

- 戻り値: 関数の結果を並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> total = {10, 25, 45, 70};  // 累計スコア

  auto gained = total
              | std::views::adjacent_transform<2>([](int a, int b) { return b - a; })
              | std::ranges::to<std::vector>();
  std::println("{}", gained);  // 各ステージで増えた点数
}
```

```text title="実行結果"
[15, 20, 25]
```

### std::ranges::adjacent_transform_view <span class="ver ver-23">C++23</span> {#adjacent_transform_view data-toc-label="std::ranges::adjacent_transform_view"}

```cpp
template <forward_range V, copy_constructible F, size_t N>
class adjacent_transform_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

隣り合う N 個の要素を関数で 1 つの値にする view。`views::adjacent_transform<N>` が作ります。

ふつうは `views::adjacent_transform` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::adjacent_transform_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 累計から、各ステージの増加量を求める | `total | adjacent_transform<2>(差)` |
| フレーム時刻から、フレーム間隔の一覧を作る | `times | adjacent_transform<2>(差)` |

## よくあるミス

??? failure "先頭の要素が出ないことを忘れる"
    最初の組は `(v[0], v[1])` からなので、結果は元より 1 つ短くなります（先頭を含む [`adjacent_difference`](../adjacent_difference.md) とは違います）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::adjacent`](adjacent.md) | 組のまま並べる |
| [`std::adjacent_difference`](../adjacent_difference.md) | 配列に書き出す従来の関数 |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣り合う N 個に関数を適用する
    - [x] 結果は元より N-1 個短い
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::adjacent_transform_view](https://cpprefjp.github.io/reference/ranges/adjacent_transform_view.html)
- [cppreference: std::ranges::adjacent_transform_view](https://en.cppreference.com/w/cpp/ranges/adjacent_transform_view)
