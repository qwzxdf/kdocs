---
title: std::indirectly_comparable
summary: "2 つのイテレータが指す要素を、比較関数で比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`equal` や `find` などの制約に使われます。比較関数と、それぞれのイテレータを指定します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_comparable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_comparable {#indirectly_comparable}

```cpp
template <class I1, class I2, class Comp>
concept indirectly_comparable = /* indirect_binary_predicate<Comp, projected<I1, P1>, projected<I2, P2>> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I1` | 型 | 調べる型 |
| `I2` | 型 | 調べる型 |
| `Comp` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <iterator>
#include <print>
#include <ranges>

int main() {
  std::println("{}", std::indirectly_comparable<int*, int*, std::ranges::equal_to>);
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

??? failure "比較できない型の組"
    要素どうしが比較関数に渡せない組み合わせは満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_binary_predicate`](indirect_binary_predicate.md) | 二項述語 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのイテレータが指す要素を比較関数で比べられることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_comparable](https://cpprefjp.github.io/reference/iterator/indirectly_comparable.html)
- [cppreference: std::indirectly_comparable](https://en.cppreference.com/w/cpp/iterator/indirectly_comparable)
