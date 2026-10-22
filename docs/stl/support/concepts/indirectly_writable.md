---
title: std::indirectly_writable
summary: "`*it = value` で値を書き込める型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_writable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータやポインタのように、`*` を通して値を書き込める型です。書き込む値の型も指定します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_writable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_writable {#indirectly_writable}

```cpp
template <class Out, class T>
concept indirectly_writable = /* *it = value が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Out` | 型 | 調べる型 |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirectly_writable<int*, int>);
  std::println("{}", std::indirectly_writable<const int*, int>);
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
    `const int*` は書き込めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_readable`](indirectly_readable.md) | 読み取れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `*it = value` で値を書き込める型を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_writable](https://cpprefjp.github.io/reference/iterator/indirectly_writable.html)
- [cppreference: std::indirectly_writable](https://en.cppreference.com/w/cpp/iterator/indirectly_writable)
