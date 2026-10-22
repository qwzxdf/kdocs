---
title: std::sentinel_for
summary: "あるイテレータの終端として使える型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sentinel_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

範囲の終わりを表す型が、イテレータとは別の型のことがあります。`sentinel_for<S, I>` は、`S` が `I` と `==` で比べられる、終端として使える型かを調べます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::sentinel_for<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが、引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sentinel_for {#sentinel_for}

```cpp
template <class S, class I>
concept sentinel_for = /* semiregular<S> かつ I と S が == で比べられる */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `S` | 型 | 調べる型 |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::sentinel_for<int*, int*>);
  std::println("{}", std::sentinel_for<int, int*>);
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

??? failure "異なる種類のイテレータを組み合わせる"
    比べられない組み合わせは満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sized_sentinel_for`](sized_sentinel_for.md) | 差を求められる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] あるイテレータの終端として使える型を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sentinel_for](https://cpprefjp.github.io/reference/iterator/sentinel_for.html)
- [cppreference: std::sentinel_for](https://en.cppreference.com/w/cpp/iterator/sentinel_for)
