---
title: std::indirectly_readable
summary: "`*it` で値を読み取れる型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_readable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータやポインタのように、`*` で間接的に値を読める型です。値の型と参照の型が定義されていることが条件です。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_readable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_readable {#indirectly_readable}

```cpp
template <class In>
concept indirectly_readable = /* *it で値を読め、iter_value_t などが定義されている */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `In` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirectly_readable<int*>);
  std::println("{}", std::indirectly_readable<int>);
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

??? failure "書き込み専用の型を渡す"
    `back_insert_iterator` は `*` で読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_writable`](indirectly_writable.md) | 書き込める |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `*it` で値を読み取れる型を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_readable](https://cpprefjp.github.io/reference/iterator/indirectly_readable.html)
- [cppreference: std::indirectly_readable](https://en.cppreference.com/w/cpp/iterator/indirectly_readable)
