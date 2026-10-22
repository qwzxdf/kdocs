---
title: std::assignable_from
summary: "左辺の型に、右辺の値を代入できることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::assignable_from

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`a = b` が書ける型の組を要求します。左辺は**左辺値参照**の型で渡します（`int&`）。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::assignable_from<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::assignable_from {#assignable_from}

```cpp
template <class T, class U>
concept assignable_from = /* 左辺値参照 T に U を代入できる */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `U` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("{}", std::assignable_from<int&, int>);
  std::println("{}", std::assignable_from<int, int>);
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

??? failure "左辺に値の型を渡す"
    `assignable_from<int, int>` は `false` です。左辺は `int&` のように参照で渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copyable`](copyable.md) | コピーできる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 左辺の型に、右辺の値を代入できることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::assignable_from](https://cpprefjp.github.io/reference/concepts/assignable_from.html)
- [cppreference: std::assignable_from](https://en.cppreference.com/w/cpp/concepts/assignable_from)
