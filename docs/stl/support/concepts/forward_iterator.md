---
title: std::forward_iterator
summary: "何度でも読み返せて、一方向に進むイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::forward_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

同じ範囲を複数回走査できるイテレータです。`forward_list` のイテレータが典型で、`vector` のものも満たします。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::forward_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::forward_iterator {#forward_iterator}

```cpp
template <class I>
concept forward_iterator = /* input_iterator かつ incrementable かつ sentinel_for<I, I> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <forward_list>
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::forward_iterator<std::forward_list<int>::iterator>);
  std::println("{}", std::forward_iterator<std::istream_iterator<int>>);
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

??? failure "入力ストリームのイテレータを渡す"
    入力ストリームは 1 回しか読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 1 回だけ |
| [`bidirectional_iterator`](bidirectional_iterator.md) | 後ろにも戻れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何度でも読み返せて、一方向に進むイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::forward_iterator](https://cpprefjp.github.io/reference/iterator/forward_iterator.html)
- [cppreference: std::forward_iterator](https://en.cppreference.com/w/cpp/iterator/forward_iterator)
