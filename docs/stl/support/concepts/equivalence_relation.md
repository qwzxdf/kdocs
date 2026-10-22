---
title: std::equivalence_relation
summary: "同値関係（反射・対称・推移）となる二項関係を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equivalence_relation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`==` のように、「A と A は同じ」「A と B が同じなら B と A も同じ」「A=B, B=C なら A=C」が成り立つ関係を要求します。構文上は `relation` と同じで、意味の条件は人間が守ります。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::equivalence_relation<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::equivalence_relation {#equivalence_relation}

```cpp
template <class R, class T, class U>
concept equivalence_relation = /* relation<R, T, U>（意味の上で同値関係） */;
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
  std::println("{}", std::equivalence_relation<std::equal_to<>, int, int>);
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

??? failure "成り立たない関係を渡す"
    コンパイラは意味を検査しません。たとえば `<` を渡しても通りますが、結果は保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`relation`](relation.md) | 構文だけの条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同値関係（反射・対称・推移）となる二項関係を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::equivalence_relation](https://cpprefjp.github.io/reference/concepts/equivalence_relation.html)
- [cppreference: std::equivalence_relation](https://en.cppreference.com/w/cpp/concepts/equivalence_relation)
