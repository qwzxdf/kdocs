---
title: std::indirectly_swappable
summary: "2 つのイテレータが指す要素を、入れ替えられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`swap_ranges` などの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_swappable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_swappable {#indirectly_swappable}

```cpp
template <class I1, class I2>
concept indirectly_swappable = /* iter_swap(i1, i2) が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I1` | 型 | 調べる型 |
| `I2` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirectly_swappable<int*, int*>);
  std::println("{}", std::indirectly_swappable<const int*, const int*>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のアルゴリズムの引数を制約する |

## よくあるミス

??? failure "const な要素"
    書き込めない要素は入れ替えられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`swappable`](swappable.md) | 値の入れ替え |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのイテレータが指す要素を、入れ替えられることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_swappable](https://cpprefjp.github.io/reference/iterator/indirectly_swappable.html)
- [cppreference: std::indirectly_swappable](https://en.cppreference.com/w/cpp/iterator/indirectly_swappable)
