---
title: std::weakly_incrementable
summary: "`++` で進めるイテレータの最低限の条件を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::weakly_incrementable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`++it` と `it++` が使えて、差の型（`difference_type`）が定義されている型です。`int` も満たします（`views::iota` が `int` を数えるときに使われます）。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::weakly_incrementable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::weakly_incrementable {#weakly_incrementable}

```cpp
template <class I>
concept weakly_incrementable = /* default_initializable かつ movable かつ ++i が使える */;
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
  std::println("{}", std::weakly_incrementable<int>);
  std::println("{}", std::weakly_incrementable<void*>);
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

??? failure "ポインタを何でも満たすと思う"
    `void*` は演算できないので満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`incrementable`](incrementable.md) | さらに等価性がある |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `++` で進めるイテレータの最低限の条件を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::weakly_incrementable](https://cpprefjp.github.io/reference/iterator/weakly_incrementable.html)
- [cppreference: std::weakly_incrementable](https://en.cppreference.com/w/cpp/iterator/weakly_incrementable)
