---
title: std::random_access_iterator
summary: "添字で好きな位置へ飛べるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::random_access_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`it + n` や `it[n]` で一気に飛べるイテレータです。`vector`・`deque`・配列のイテレータが満たします。`sort` などが要求します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::random_access_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::random_access_iterator {#random_access_iterator}

```cpp
template <class I>
concept random_access_iterator = /* bidirectional_iterator かつ +, -, [], < などが使える */;
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
  std::println("{}", std::random_access_iterator<std::vector<int>::iterator>);
  std::println("{}", std::random_access_iterator<std::list<int>::iterator>);
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
    `list` は飛べないので、`sort` できません。`list::sort` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bidirectional_iterator`](bidirectional_iterator.md) | 1 つずつ |
| [`contiguous_iterator`](contiguous_iterator.md) | さらにメモリが連続 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 添字で好きな位置へ飛べるイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::random_access_iterator](https://cpprefjp.github.io/reference/iterator/random_access_iterator.html)
- [cppreference: std::random_access_iterator](https://en.cppreference.com/w/cpp/iterator/random_access_iterator)
