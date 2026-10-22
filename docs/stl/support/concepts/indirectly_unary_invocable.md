---
title: std::indirectly_unary_invocable
summary: "イテレータが指す値で、1 引数の関数を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_unary_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`for_each` のように、要素を 1 つずつ関数に渡すアルゴリズムの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_unary_invocable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_unary_invocable {#indirectly_unary_invocable}

```cpp
template <class F, class I>
concept indirectly_unary_invocable = /* 関数 F が iter_value_t と iter_reference_t で呼べる */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `F` | 型 | 調べる型 |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  auto f = [](int x) { return x; };
  std::println("{}", std::indirectly_unary_invocable<decltype(f), int*>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のアルゴリズムの引数を制約する |

## よくあるミス

??? failure "引数の型が合わない関数"
    要素の型を受けられない関数は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_regular_unary_invocable`](indirectly_regular_unary_invocable.md) | 副作用なしの条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータが指す値で、1 引数の関数を呼べることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_unary_invocable](https://cpprefjp.github.io/reference/iterator/indirectly_unary_invocable.html)
- [cppreference: std::indirectly_unary_invocable](https://en.cppreference.com/w/cpp/iterator/indirectly_unary_invocable)
