---
title: std::input_iterator
summary: "要素を読みながら進められるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::input_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

一度だけ前に進みながら、`*it` で要素を読めるイテレータです。ストリームから読むイテレータも満たします。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::input_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::input_iterator {#input_iterator}

```cpp
template <class I>
concept input_iterator = /* input_or_output_iterator かつ indirectly_readable */;
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
  std::println("{}", std::input_iterator<int*>);
  std::println("{}", std::input_iterator<int>);
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

??? failure "書き込み専用を渡す"
    `back_insert_iterator` は読めないので満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_iterator`](forward_iterator.md) | 何度でも読み返せる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素を読みながら進められるイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::input_iterator](https://cpprefjp.github.io/reference/iterator/input_iterator.html)
- [cppreference: std::input_iterator](https://en.cppreference.com/w/cpp/iterator/input_iterator)
