---
title: std::swappable
summary: "`swap` で入れ替えられる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::swap` が使える型だけを受け付けます。`const` の値は入れ替えられないので満たしません。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::swappable<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::swappable {#swappable}

```cpp
template <class T>
concept swappable = /* ranges::swap(a, a) が使える */;
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
  std::println("{}", std::swappable<int>);
  std::println("{}", std::swappable<const int>);
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

??? failure "const な型を渡す"
    `const` の値は書き換えられないので、入れ替えられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`swappable_with`](swappable_with.md) | 2 つの型を入れ替える |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `swap` で入れ替えられる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::swappable](https://cpprefjp.github.io/reference/concepts/swappable.html)
- [cppreference: std::swappable](https://en.cppreference.com/w/cpp/concepts/swappable)
