---
title: std::constructible_from
summary: "指定した引数から構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::constructible_from

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`T(args...)` と書ける型を要求します。ジェネリックなコンテナの `emplace` などの制約に使います。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::constructible_from<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::constructible_from {#constructible_from}

```cpp
template <class T, class Args...>
concept constructible_from = /* destructible<T> かつ is_constructible_v<T, Args...> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `Args...` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  std::println("{}", std::constructible_from<std::string, const char*>);
  std::println("{}", std::constructible_from<std::string, int>);
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

??? failure "暗黙変換と混同する"
    コンストラクタが `explicit` でも `constructible_from` は満たします。暗黙変換は `convertible_to` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`convertible_to`](convertible_to.md) | 暗黙の変換 |
| [`default_initializable`](default_initializable.md) | 引数なしで作れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した引数から構築できる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::constructible_from](https://cpprefjp.github.io/reference/concepts/constructible_from.html)
- [cppreference: std::constructible_from](https://en.cppreference.com/w/cpp/concepts/constructible_from)
