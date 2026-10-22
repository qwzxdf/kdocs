---
title: std::relation
summary: "2 つの値を比べる二項関係（真偽を返す関数）を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::relation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`less` や `equal_to` のように、2 つの値を受け取って `bool` を返す関数を要求します。`sort` の比較関数などの制約に使われます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::relation<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::relation {#relation}

```cpp
template <class R, class T, class U>
concept relation = /* predicate<R, T, T> かつ predicate<R, T, U> など（4 つの組み合わせ） */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 調べる型 |
| `T` | 型 | 調べる型 |
| `U` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <functional>
#include <print>
#include <string>

int main() {
  std::println("{}", std::relation<std::less<>, int, int>);
  std::println("{}", std::relation<std::less<>, int, std::string>);
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

??? failure "1 引数の関数を渡す"
    2 つの値を受け取る関数だけが対象です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equivalence_relation`](equivalence_relation.md) | 同値関係 |
| [`strict_weak_order`](strict_weak_order.md) | 整列に使える |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの値を比べる二項関係（真偽を返す関数）を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::relation](https://cpprefjp.github.io/reference/concepts/relation.html)
- [cppreference: std::relation](https://en.cppreference.com/w/cpp/concepts/relation)
