---
title: std::totally_ordered_with
summary: "2 つの異なる型を `<` などで比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::totally_ordered_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`totally_ordered` の、型が異なる版です。`int` と `long` のように、混ぜて大小を比べられるかを調べます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::totally_ordered_with<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::totally_ordered_with {#totally_ordered_with}

```cpp
template <class T, class U>
concept totally_ordered_with = /* T と U が <, >, <=, >= で比べられ、共通の参照型がある */;
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
#include <string>

int main() {
  std::println("{}", std::totally_ordered_with<int, long>);
  std::println("{}", std::totally_ordered_with<int, std::string>);
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

??? failure "符号付きと符号なしを混ぜる"
    満たしても、比較の結果が直感と違うことがあります。`std::cmp_less` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`totally_ordered`](totally_ordered.md) | 同じ型どうし |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの異なる型を `<` などで比べられることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::totally_ordered_with](https://cpprefjp.github.io/reference/concepts/totally_ordered_with.html)
- [cppreference: std::totally_ordered_with](https://en.cppreference.com/w/cpp/concepts/totally_ordered_with)
