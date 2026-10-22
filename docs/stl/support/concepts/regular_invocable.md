---
title: std::regular_invocable
summary: "同じ引数で何度呼んでも、同じ結果になる呼び出し可能な型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::regular_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`invocable` より厳しく、「関数の副作用がなく、同じ入力に同じ出力」という意味が付きます。ただし、コンパイラが意味まで検査するわけではなく、構文上は `invocable` と同じです。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::regular_invocable<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::regular_invocable {#regular_invocable}

```cpp
template <class F, class Args...>
concept regular_invocable = /* invocable<F, Args...>（意味の上で等価性を保つ） */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `F` | 型 | 調べる型 |
| `Args...` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  auto f = [](int x) { return x; };
  std::println("{}", std::regular_invocable<decltype(f), int>);
  std::println("{}", std::regular_invocable<decltype(f), std::string>);
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

??? failure "乱数やカウンタを返す関数に使う"
    意味の上では、呼ぶたびに結果が変わる関数は対象外です。コンパイラは検査しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invocable`](invocable.md) | 構文だけの条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ引数で何度呼んでも、同じ結果になる呼び出し可能な型を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regular_invocable](https://cpprefjp.github.io/reference/concepts/regular_invocable.html)
- [cppreference: std::regular_invocable](https://en.cppreference.com/w/cpp/concepts/regular_invocable)
