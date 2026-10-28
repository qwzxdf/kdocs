---
title: std::permutable
summary: "要素を並べ替えられるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::permutable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

要素を入れ替えたり、動かしたりできる前方イテレータです。`rotate` や `unique` などの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::permutable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::permutable {#permutable}

```cpp
template <class I>
concept permutable = /* forward_iterator かつ indirectly_movable_storable かつ indirectly_swappable */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::permutable<int*>);
  std::println("{}", std::permutable<const int*>);
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

??? failure "const のポインタを渡す"
    書き込めないので、並べ替えられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sortable`](sortable.md) | 並べ替えられる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素を並べ替えられるイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::permutable](https://cpprefjp.github.io/reference/iterator/permutable.html)
- [cppreference: std::permutable](https://en.cppreference.com/w/cpp/iterator/permutable)
