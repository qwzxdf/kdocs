---
title: std::ranges::viewable_range
summary: "view に変換できる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::viewable_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

パイプ（`|`）で view に渡せる範囲かを表します。左辺値の範囲や、ムーブできる右辺値の範囲が満たします。`views::all` で包めるかが条件です。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::viewable_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::viewable_range {#viewable_range}

```cpp
template <class T>
concept viewable_range = /* views::all が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>

int main() {
    std::println("{}", std::ranges::viewable_range<std::vector<int>&>);
    std::println("{}", std::ranges::viewable_range<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数を制約して、使える範囲だけを受け付ける |

## よくあるミス

??? failure "コピーできない範囲を左辺値の const で渡す"
    view に包めない範囲は、パイプに渡せません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::all`](../../algorithms/views/all.md) | view に包む |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] view に変換できる範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::viewable_range](https://cpprefjp.github.io/reference/ranges/viewable_range.html)
- [cppreference: std::ranges::viewable_range](https://en.cppreference.com/w/cpp/ranges/viewable_range)
