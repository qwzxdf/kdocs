---
title: std::views::all
summary: "範囲を、軽いビューとして扱えるようにする。"
order: 21
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::all

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::all` は、**どんな範囲でも「ビュー」にして返す**アダプターです。`vector` に使うと、中身を参照するだけの軽い [`ref_view`](ref_view.md) になり、右辺値の `vector` に使うと、中身を引き取る [`owning_view`](owning_view.md) になります。ビューのパイプラインの内部で自動的に使われているので、普段は意識しません。

!!! tip "ポイント"
    - すでにビューなら、そのまま返す。
    - コンテナの左辺値なら `ref_view`（参照）、右辺値なら `owning_view`（所有）になる。
    - 自分で書く場面はほとんどない。型を調べたいときに登場する。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::all {#all}

```cpp
std::views::all(r)
std::views::all_t<R>   // 結果の型
```

- 戻り値: 範囲を表すビュー（`ref_view` / `owning_view` など）
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  auto a = std::views::all(v);  // v を参照するビュー（コピーしない）
  std::println("{}", std::ranges::size(a));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートの中で、受け取った範囲を「ビュー」として扱う | `std::views::all(r)` |

## よくあるミス

??? failure "all が必要だと思い込む"
    `v | std::views::filter(...)` のように、パイプでつなげば `all` は自動で挟まります。明示的に書くことはほとんどありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::ref_view`](ref_view.md) | 左辺値を参照するビュー |
| [`std::ranges::owning_view`](owning_view.md) | 右辺値を所有するビュー |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲をビューにする
    - [x] 自動で挟まるので普段は書かない
    - [x] 型を調べるときに登場

## 関連ページ

- [cpprefjp: std::ranges::all_t](https://cpprefjp.github.io/reference/ranges/all_t.html)
- [cppreference: std::ranges::all_t](https://en.cppreference.com/w/cpp/ranges/all_t)
