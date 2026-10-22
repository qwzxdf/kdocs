---
title: std::copy_constructible
summary: "コピーして構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

他のオブジェクトからコピーして作れる型を要求します。`unique_ptr` はコピーできないので満たしません。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::copy_constructible<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::copy_constructible {#copy_constructible}

```cpp
template <class T>
concept copy_constructible = /* move_constructible<T> かつ T がコピーで構築できる */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <memory>
#include <print>
#include <string>

int main() {
  std::println("{}", std::copy_constructible<std::string>);
  std::println("{}", std::copy_constructible<std::unique_ptr<int>>);
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

??? failure "ムーブだけの型を渡す"
    `unique_ptr` などのムーブ専用の型は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`move_constructible`](move_constructible.md) | ムーブして作れる |
| [`copyable`](copyable.md) | 代入もできる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーして構築できる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::copy_constructible](https://cpprefjp.github.io/reference/concepts/copy_constructible.html)
- [cppreference: std::copy_constructible](https://en.cppreference.com/w/cpp/concepts/copy_constructible)
