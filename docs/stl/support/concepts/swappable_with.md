---
title: std::swappable_with
summary: "2 つの型の値を、たがいに `swap` できることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::swappable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

異なる型の値を入れ替えられるかを調べます。左辺値参照の型を渡します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::swappable_with<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::swappable_with {#swappable_with}

```cpp
template <class T, class U>
concept swappable_with = /* ranges::swap(a, b) と ranges::swap(b, a) が使える */;
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
  std::println("{}", std::swappable_with<int&, int&>);
  std::println("{}", std::swappable_with<int&, long&>);
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

??? failure "参照を付けずに渡す"
    `swappable_with<int, int>` は `false` です。参照で渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`swappable`](swappable.md) | 同じ型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの型の値を、たがいに `swap` できることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::swappable_with](https://cpprefjp.github.io/reference/concepts/swappable_with.html)
- [cppreference: std::swappable_with](https://en.cppreference.com/w/cpp/concepts/swappable_with)
