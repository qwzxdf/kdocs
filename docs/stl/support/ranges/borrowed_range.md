---
title: std::ranges::borrowed_range
summary: "元の範囲より長生きするイテレータを返せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::borrowed_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`find` が返したイテレータを、一時オブジェクトの範囲に対して使うと、そのまま壊れた参照になります。`borrowed_range` は、「イテレータが範囲の寿命に依存しない」範囲です。左辺値の範囲や `string_view`・`span` は満たします。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::borrowed_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::borrowed_range {#borrowed_range}

```cpp
template <class T>
concept borrowed_range = /* 左辺値、または enable_borrowed_range が true */;
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
    std::println("{}", std::ranges::borrowed_range<std::vector<int>&>);
    std::println("{}", std::ranges::borrowed_range<std::vector<int>>);
    std::println("{}", std::ranges::borrowed_range<std::string_view>);
}
```

```text title="実行結果"
true
false
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数を制約して、使える範囲だけを受け付ける |

## よくあるミス

??? failure "一時オブジェクトの `find` の結果を使う"
    `borrowed_range` でない一時オブジェクトに `ranges::find` を使うと、`dangling` が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dangling`](dangling.md) | 壊れたイテレータの代わり |
| [`enable_borrowed_range`](enable_borrowed_range.md) | 借りられると宣言する |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 元の範囲より長生きするイテレータを返せる範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::borrowed_range](https://cpprefjp.github.io/reference/ranges/borrowed_range.html)
- [cppreference: std::ranges::borrowed_range](https://en.cppreference.com/w/cpp/ranges/borrowed_range)
