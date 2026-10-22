---
title: std::views::all_t
summary: "views::all が返す view の型。"
order: 900
tags:
  - 型・言語サポート
---

# std::views::all_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`views::all(r)` は、範囲 `r` を view として包みます。包んだ後の型を知りたいときは、`all_t<R>` が使えます。左辺値のコンテナなら `ref_view<R>`、右辺値のコンテナなら `owning_view<R>` になります。

!!! tip "ポイント"
    - `views::all_t<R>` = `decltype(views::all(declval<R>()))`。
    - 左辺値の範囲は `ref_view`、右辺値の範囲は `owning_view`、view はそのまま。
    - テンプレートで、view の型を持つメンバを作るときに使う。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::views::all_t {#all_t}

```cpp
template <viewable_range R>
using views::all_t = decltype(views::all(declval<R>()));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 包む範囲の型 |

- 戻り値: 包んだ view の型
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  using V = std::views::all_t<std::vector<int>&>;
  std::println("{}", std::is_same_v<V, std::ranges::ref_view<std::vector<int>>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | view をメンバ変数に持つクラスを書く |

## よくあるミス

??? failure "右辺値を渡して `ref_view` になると思う"
    右辺値のコンテナは `owning_view` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::all`](../../algorithms/views/all.md) | view に包む関数 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] views::all が返す view の型
    - [x] `views::all_t<R>` = `decltype(views::all(declval<R>()))`
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::views::all_t](https://cpprefjp.github.io/reference/ranges/all_t.html)
- [cppreference: std::views::all_t](https://en.cppreference.com/w/cpp/ranges/all_view)
