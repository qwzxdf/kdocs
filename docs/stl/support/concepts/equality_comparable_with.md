---
title: std::equality_comparable_with
summary: "2 つの異なる型を `==` で比べられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equality_comparable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`int` と `long` のように、型が違う値を比べられるかを調べます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::equality_comparable_with<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::equality_comparable_with {#equality_comparable_with}

```cpp
template <class T, class U>
concept equality_comparable_with = /* T と U が == で比べられ、共通の参照型がある */;
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
  std::println("{}", std::equality_comparable_with<int, long>);
  std::println("{}", std::equality_comparable_with<int, std::string>);
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

??? failure "暗黙変換できるだけで満たすと思う"
    共通の参照型を持ち、両方向の `==` が使える必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equality_comparable`](equality_comparable.md) | 同じ型どうし |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの異なる型を `==` で比べられることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::equality_comparable_with](https://cpprefjp.github.io/reference/concepts/equality_comparable_with.html)
- [cppreference: std::equality_comparable_with](https://en.cppreference.com/w/cpp/concepts/equality_comparable_with)
