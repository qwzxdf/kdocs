---
title: std::equality_comparable
summary: "`==` と `!=` で比べられる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equality_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`a == b` が書ける型を要求します。`==` のほかに `!=` も使えることが条件です。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::equality_comparable<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::equality_comparable {#equality_comparable}

```cpp
template <class T>
concept equality_comparable = /* T 同士で == と != が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

struct NoEq {};

int main() {
  std::println("{}", std::equality_comparable<int>);
  std::println("{}", std::equality_comparable<NoEq>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数に条件をつけて、使える型を制限する |

## よくあるミス

??? failure "`==` を定義していない構造体"
    `struct` は、`operator==` を書くか `= default` するまで比べられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equality_comparable_with`](equality_comparable_with.md) | 異なる型どうし |
| [`totally_ordered`](totally_ordered.md) | 大小も比べられる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `==` と `!=` で比べられる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::equality_comparable](https://cpprefjp.github.io/reference/concepts/equality_comparable.html)
- [cppreference: std::equality_comparable](https://en.cppreference.com/w/cpp/concepts/equality_comparable)
