---
title: std::indirectly_regular_unary_invocable
summary: "イテレータが指す値で、副作用なく 1 引数の関数を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_regular_unary_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`indirectly_unary_invocable` に、「同じ入力なら同じ出力」の意味が付きます。プロジェクションなどに使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_regular_unary_invocable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_regular_unary_invocable {#indirectly_regular_unary_invocable}

```cpp
template <class F, class I>
concept indirectly_regular_unary_invocable = /* 関数 F が値・参照の両方で regular_invocable */;
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
  std::println("{}", std::indirectly_regular_unary_invocable<decltype(f), int*>);
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

??? failure "状態を持つ関数"
    コンパイラは意味を検査しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_unary_invocable`](indirectly_unary_invocable.md) | 構文だけの条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータが指す値で、副作用なく 1 引数の関数を呼べることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_regular_unary_invocable](https://cpprefjp.github.io/reference/iterator/indirectly_regular_unary_invocable.html)
- [cppreference: std::indirectly_regular_unary_invocable](https://en.cppreference.com/w/cpp/iterator/indirectly_regular_unary_invocable)
