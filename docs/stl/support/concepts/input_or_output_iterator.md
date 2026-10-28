---
title: std::input_or_output_iterator
summary: "イテレータとして最低限の操作ができることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::input_or_output_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`*it` と `++it` が使える、最も弱いイテレータの条件です。入力・出力のどちらでも満たします。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::input_or_output_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::input_or_output_iterator {#input_or_output_iterator}

```cpp
template <class I>
concept input_or_output_iterator = /* weakly_incrementable<I> かつ *i が使える */;
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
  std::println("{}", std::input_or_output_iterator<int*>);
  std::println("{}", std::input_or_output_iterator<int>);
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

??? failure "整数をイテレータとして扱う"
    `int` は `++` ができても `*` が使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 読み取れる |
| [`output_iterator`](output_iterator.md) | 書き込める |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータとして最低限の操作ができることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::input_or_output_iterator](https://cpprefjp.github.io/reference/iterator/input_or_output_iterator.html)
- [cppreference: std::input_or_output_iterator](https://en.cppreference.com/w/cpp/iterator/input_or_output_iterator)
