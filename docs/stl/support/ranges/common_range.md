---
title: std::ranges::common_range
summary: "begin と end が同じ型の範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::common_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

従来のアルゴリズムは、`begin` と `end` が同じ型であることを前提にしていました。`common_range` は、その性質を要求します。`views::iota(1)`（終わりなし）のような範囲は満たしません。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::common_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::common_range {#common_range}

```cpp
template <class T>
concept common_range = /* begin と end が同じ型 */;
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
    std::println("{}", std::ranges::common_range<std::vector<int>>);
    std::println("{}", std::ranges::common_range<std::ranges::iota_view<int>>);
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

??? failure "古いアルゴリズムに view を直接渡す"
    `common_range` でない view は、従来の `std::sort` などに渡せません。`views::common` で包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::common`](../../algorithms/views/common.md) | common_range に変える |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] begin と end が同じ型の範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::common_range](https://cpprefjp.github.io/reference/ranges/common_range.html)
- [cppreference: std::ranges::common_range](https://en.cppreference.com/w/cpp/ranges/common_range)
