---
title: std::projected
summary: "プロジェクション（変換）を通した値を、アルゴリズムに見せるための型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::projected

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`ranges::sort(v, comp, proj)` のように、アルゴリズムは「比較の前に値を変換するプロジェクション」を受け取ります。`projected<It, Proj>` は、その変換後の値を、コンセプトの制約で使うための型です。自分で書くことはほとんどなく、自作のアルゴリズムの制約に登場します。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::projected {#projected}

```cpp
template <indirectly_readable It, indirectly_regular_unary_invocable<It> Proj>
struct projected;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | 元のイテレータ |
| `Proj` | 型 | プロジェクション |

- 戻り値: プロジェクション後の値の型を表す型
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <ranges>

int main() {
  // 自作アルゴリズムの制約の例
  // template <std::input_iterator I, class Proj = std::identity,
  //           std::indirect_strict_weak_order<std::projected<I, Proj>> Comp = std::ranges::less>
  // void MySort(I first, I last, Comp comp = {}, Proj proj = {});
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の ranges アルゴリズムを書くとき |

## よくあるミス

??? failure "制約を手で書く"
    標準のアルゴリズムと同じ制約は、`projected` を使うとまとめて書けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::identity`](../functional/identity.md) | 何もしないプロジェクション |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プロジェクション（変換）を通した値を、アルゴリズムに見せるための型
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::projected](https://cpprefjp.github.io/reference/iterator/projected.html)
- [cppreference: std::projected](https://en.cppreference.com/w/cpp/iterator/projected)
