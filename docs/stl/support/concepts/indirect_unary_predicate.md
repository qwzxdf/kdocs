---
title: std::indirect_unary_predicate
summary: "イテレータが指す値で、1 引数の述語を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_unary_predicate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`find_if` や `count_if` のように、要素を条件で判定するアルゴリズムの制約に使われます。述語は `bool` に変換できる値を返す必要があります。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirect_unary_predicate<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_unary_predicate {#indirect_unary_predicate}

```cpp
template <class Pred, class I>
concept indirect_unary_predicate = /* 述語 Pred が値・参照で predicate */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Pred` | 型 | 調べる型 |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  auto p = [](int x) { return x > 0; };
  std::println("{}", std::indirect_unary_predicate<decltype(p), int*>);
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

??? failure "`bool` に変換できない戻り値"
    戻り値が `bool` に変換できない関数は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`predicate`](predicate.md) | 値の述語 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータが指す値で、1 引数の述語を呼べることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirect_unary_predicate](https://cpprefjp.github.io/reference/iterator/indirect_unary_predicate.html)
- [cppreference: std::indirect_unary_predicate](https://en.cppreference.com/w/cpp/iterator/indirect_unary_predicate)
