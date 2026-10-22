---
title: std::indirect_strict_weak_order
summary: "2 つのイテレータが指す値で、厳密な弱順序を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_strict_weak_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`sort` や `lower_bound` のように、要素の順序を比べるアルゴリズムの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirect_strict_weak_order<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_strict_weak_order {#indirect_strict_weak_order}

```cpp
template <class Comp, class I>
concept indirect_strict_weak_order = /* 述語が 2 つのイテレータの値・参照で strict_weak_order */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Comp` | 型 | 調べる型 |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirect_strict_weak_order<std::less<>, int*>);
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

??? failure "`<=` を渡す"
    `<=` は厳密な弱順序ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strict_weak_order`](strict_weak_order.md) | 値の弱順序 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのイテレータが指す値で、厳密な弱順序を呼べることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirect_strict_weak_order](https://cpprefjp.github.io/reference/iterator/indirect_strict_weak_order.html)
- [cppreference: std::indirect_strict_weak_order](https://en.cppreference.com/w/cpp/iterator/indirect_strict_weak_order)
