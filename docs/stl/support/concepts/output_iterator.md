---
title: std::output_iterator
summary: "指定した型の値を書き込めるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::output_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`*it = value` で値を書き込みながら進められるイテレータです。`output_iterator<I, T>` と、書き込む値の型も指定します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::output_iterator<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::output_iterator {#output_iterator}

```cpp
template <class I, class T>
concept output_iterator = /* input_or_output_iterator かつ indirectly_writable<I, T> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::output_iterator<int*, int>);
  std::println("{}", std::output_iterator<const int*, int>);
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

??? failure "const のポインタを出力先にする"
    `const int*` には書き込めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 読み取れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した型の値を書き込めるイテレータを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::output_iterator](https://cpprefjp.github.io/reference/iterator/output_iterator.html)
- [cppreference: std::output_iterator](https://en.cppreference.com/w/cpp/iterator/output_iterator)
