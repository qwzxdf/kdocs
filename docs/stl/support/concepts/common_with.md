---
title: std::common_with
summary: "2 つの型が、共通の型を持つことを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::common_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

2 つの型を混ぜた計算（`int` と `double` の足し算など）ができるかを調べます。`common_type_t<T, U>` が存在し、両方から変換できることが条件です。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::common_with<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::common_with {#common_with}

```cpp
template <class T, class U>
concept common_with = /* common_type_t<T, U> が存在し、両方から変換できる */;
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
  std::println("{}", std::common_with<int, double>);
  std::println("{}", std::common_with<int, std::string>);
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

??? failure "見かけだけで判断する"
    `int` と `std::string` は、同じ「何か」に変換できないので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`common_reference_with`](common_reference_with.md) | 共通の参照型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの型が共通の型を持つことを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::common_with](https://cpprefjp.github.io/reference/concepts/common_with.html)
- [cppreference: std::common_with](https://en.cppreference.com/w/cpp/concepts/common_with)
