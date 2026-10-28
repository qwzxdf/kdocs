---
title: std::indirect_equivalence_relation
summary: "2 つのイテレータが指す値で、同値関係を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_equivalence_relation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`unique` のように、同じ値を探すアルゴリズムの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirect_equivalence_relation<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_equivalence_relation {#indirect_equivalence_relation}

```cpp
template <class Pred, class I1, class I2>
concept indirect_equivalence_relation = /* 述語が 2 つのイテレータの値・参照で equivalence_relation */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Pred` | 型 | 調べる型 |
| `I1` | 型 | 調べる型 |
| `I2` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirect_equivalence_relation<std::equal_to<>, int*>);
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

??? failure "`<` を渡す"
    同値関係には `==` を渡します。`<` は意味が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equivalence_relation`](equivalence_relation.md) | 値の同値関係 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのイテレータが指す値で、同値関係を呼べることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirect_equivalence_relation](https://cpprefjp.github.io/reference/iterator/indirect_equivalence_relation.html)
- [cppreference: std::indirect_equivalence_relation](https://en.cppreference.com/w/cpp/iterator/indirect_equivalence_relation)
