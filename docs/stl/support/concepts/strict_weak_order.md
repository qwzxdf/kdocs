---
title: std::strict_weak_order
summary: "厳密な弱順序（`sort` に使える比較）となる二項関係を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::strict_weak_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`<` のように、`sort` が使える比較関数が満たすべき条件です。「A<A は偽」「推移的」「等価も推移的」が成り立つことを要求します。構文上は `relation` と同じです。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::strict_weak_order<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::strict_weak_order {#strict_weak_order}

```cpp
template <class R, class T, class U>
concept strict_weak_order = /* relation<R, T, U>（意味の上で厳密な弱順序） */;
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

int main() {
  std::println("{}", std::strict_weak_order<std::less<>, int, int>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数に条件をつけて、使える型を制限する |

## よくあるミス

??? failure "`<=` を渡す"
    `<=` は「A<=A が真」になり、厳密な弱順序ではありません。`sort` で未定義動作になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`relation`](relation.md) | 構文だけの条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 厳密な弱順序（`sort` に使える比較）となる二項関係を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strict_weak_order](https://cpprefjp.github.io/reference/concepts/strict_weak_order.html)
- [cppreference: std::strict_weak_order](https://en.cppreference.com/w/cpp/concepts/strict_weak_order)
