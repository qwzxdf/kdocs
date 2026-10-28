---
title: std::contiguous_iterator
summary: "要素がメモリ上で連続して並ぶことを保証するイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::contiguous_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

ポインタに直せる（`std::to_address`）ことが保証されたイテレータです。`vector`・`array`・`string` のイテレータが満たします。`memcpy` などの最適化の条件になります。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::contiguous_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::contiguous_iterator {#contiguous_iterator}

```cpp
template <class I>
concept contiguous_iterator = /* random_access_iterator かつ 要素が連続している */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <deque>
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::contiguous_iterator<int*>);
  std::println("{}", std::contiguous_iterator<std::deque<int>::iterator>);
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

??? failure "`deque` を連続だと思う"
    `deque` は複数のブロックに分かれています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`random_access_iterator`](random_access_iterator.md) | 連続とは限らない |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素がメモリ上で連続して並ぶことを保証するイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::contiguous_iterator](https://cpprefjp.github.io/reference/iterator/contiguous_iterator.html)
- [cppreference: std::contiguous_iterator](https://en.cppreference.com/w/cpp/iterator/contiguous_iterator)
