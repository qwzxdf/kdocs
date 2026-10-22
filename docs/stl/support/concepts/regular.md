---
title: std::regular
summary: "値のように扱える型（コピー・既定構築・比較）を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::regular

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`int` のように「コピーでき、引数なしで作れ、`==` で比べられる」型を要求します。標準の多くのアルゴリズムが、この条件を前提にします。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::regular<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::regular {#regular}

```cpp
template <class T>
concept regular = /* semiregular<T> かつ equality_comparable<T> */;
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

int main() {
  std::println("{}", std::regular<int>);
  std::println("{}", std::regular<std::unique_ptr<int>>);
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

??? failure "`==` の無い型"
    比較できない型は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`semiregular`](semiregular.md) | 比較は不要 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値のように扱える型（コピー・既定構築・比較）を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regular](https://cpprefjp.github.io/reference/concepts/regular.html)
- [cppreference: std::regular](https://en.cppreference.com/w/cpp/concepts/regular)
