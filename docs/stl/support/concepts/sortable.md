---
title: std::sortable
summary: "並べ替えられるイテレータ（ランダムアクセスと入れ替えと比較）を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sortable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`ranges::sort` が使える条件です。ランダムアクセスで、要素を入れ替えられ、比較できる必要があります。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::sortable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sortable {#sortable}

```cpp
template <class I>
concept sortable = /* permutable かつ indirect_strict_weak_order */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <list>
#include <print>
#include <vector>

int main() {
  std::println("{}", std::sortable<std::vector<int>::iterator>);
  std::println("{}", std::sortable<std::list<int>::iterator>);
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

??? failure "`list` に sort を使う"
    `list` はランダムアクセスできないので、`ranges::sort` できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permutable`](permutable.md) | 並べ替えの前提 |
| [`mergeable`](mergeable.md) | 併合の前提 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並べ替えられるイテレータ（ランダムアクセスと入れ替えと比較）を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sortable](https://cpprefjp.github.io/reference/iterator/sortable.html)
- [cppreference: std::sortable](https://en.cppreference.com/w/cpp/iterator/sortable)
