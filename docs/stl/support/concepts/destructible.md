---
title: std::destructible
summary: "破棄できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::destructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

デストラクタが呼べる型を要求します。`void` や、デストラクタが `private` の型は満たしません。ほぼ全ての型が満たす、最も弱いコンセプトのひとつです。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::destructible<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::destructible {#destructible}

```cpp
template <class T>
concept destructible = /* T が noexcept で破棄できる */;
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

int main() {
  std::println("{}", std::destructible<int>);
  std::println("{}", std::destructible<void>);
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

??? failure "デストラクタが投げる型"
    `noexcept(false)` のデストラクタの型は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`constructible_from`](constructible_from.md) | 作れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 破棄できる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::destructible](https://cpprefjp.github.io/reference/concepts/destructible.html)
- [cppreference: std::destructible](https://en.cppreference.com/w/cpp/concepts/destructible)
