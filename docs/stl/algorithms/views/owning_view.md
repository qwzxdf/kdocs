---
title: std::ranges::owning_view
summary: "右辺値の範囲を引き取って、所有するビュー。"
order: 23
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::ranges::owning_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::owning_view` は、**一時的な範囲（右辺値の `vector` など）を引き取って、ビューの中に持つ**型です。元の変数が無くても、ビュー自身が中身を保持するので、安全に返せます。`views::all` が、コンテナの右辺値に対して返す型です。

!!! tip "ポイント"
    - ムーブだけでき、**コピーはできない**（所有しているため）。
    - 一時的な `vector` をパイプラインにそのまま流せるのは、これのおかげ（C++20 の仕様修正で追加）。
    - `ref_view` との違いは、参照か所有か。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::owning_view {#owning_view}

```cpp
template <range R>
  requires movable<R> && (!is_array_v<R>)
class std::ranges::owning_view;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲の右辺値 | 引き取る範囲 |

- 戻り値: `r` を所有するビュー
- 計算量: ムーブは O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  // 一時的な vector を所有するビュー
  std::ranges::owning_view view(std::vector<int>{1, 2, 3, 4});
  std::println("{}", view.size());
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 関数が、加工した結果の範囲を返す（元の `vector` を中に持たせる） | `return std::views::all(std::move(v)) | ...;` |

## よくあるミス

??? failure "ビューをコピーしようとする"
    `owning_view` はコピーできません（`std::move` で移動します）。パイプラインの途中で使うと、全体がムーブ専用の型になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::ref_view`](ref_view.md) | 左辺値を参照するだけ |
| [`std::views::all`](all.md) | 状況に応じてどちらかを選ぶ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 右辺値の範囲を所有する
    - [x] コピーできない（ムーブのみ）
    - [x] 一時的な `vector` をパイプに流せる

## 関連ページ

- [cpprefjp: std::ranges::owning_view](https://cpprefjp.github.io/reference/ranges/owning_view.html)
- [cppreference: std::ranges::owning_view](https://en.cppreference.com/w/cpp/ranges/owning_view)
