---
title: std::ranges::sized_range
summary: "要素数を定数時間で返せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::sized_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`size()` を呼べる範囲です。`list` は `size()` が定数時間なので満たし、`forward_list` は `size()` がないので満たしません。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::sized_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::sized_range {#sized_range}

```cpp
template <class T>
concept sized_range = /* ranges::size(r) が使える */;
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
    std::println("{}", std::ranges::sized_range<std::list<int>>);
    std::println("{}", std::ranges::sized_range<std::forward_list<int>>);
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

??? failure "`size()` が速いと思い込む"
    `sized_range` は定数時間を求めます。距離を数える必要がある範囲は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::size`](size.md) | 要素数を返す |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数を定数時間で返せる範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::sized_range](https://cpprefjp.github.io/reference/ranges/sized_range.html)
- [cppreference: std::ranges::sized_range](https://en.cppreference.com/w/cpp/ranges/sized_range)
