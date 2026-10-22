---
title: std::bidirectional_iterator
summary: "前後どちらにも進めるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::bidirectional_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`--it` で後ろに戻れるイテレータです。`list` や `map` のイテレータが満たします。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::bidirectional_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::bidirectional_iterator {#bidirectional_iterator}

```cpp
template <class I>
concept bidirectional_iterator = /* forward_iterator かつ --i が使える */;
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
#include <list>
#include <print>

int main() {
  std::println("{}", std::bidirectional_iterator<std::list<int>::iterator>);
  std::println("{}", std::bidirectional_iterator<std::forward_list<int>::iterator>);
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

??? failure "`forward_list` に使う"
    `forward_list` は後ろに戻れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_iterator`](forward_iterator.md) | 一方向 |
| [`random_access_iterator`](random_access_iterator.md) | 添字で飛べる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前後どちらにも進めるイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bidirectional_iterator](https://cpprefjp.github.io/reference/iterator/bidirectional_iterator.html)
- [cppreference: std::bidirectional_iterator](https://en.cppreference.com/w/cpp/iterator/bidirectional_iterator)
