---
title: std::same_as
summary: "2 つの型が同じであることを要求するコンセプト。"
order: 1
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::same_as

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::same_as<T, U>` は、**T と U がまったく同じ型であること**を要求するコンセプトです。`is_same_v` のコンセプト版で、関数テンプレートの引数に直接書けます。

!!! tip "ポイント"
    - `template <std::same_as<int> T>` や、`std::same_as<int> auto x` と書ける。
    - `const` や参照も区別する。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::same_as {#same_as}

```cpp
template <class T>
concept same_as = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("{} {}", std::same_as<int, int>, std::same_as<int, long>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 特定の型だけを受け取るテンプレート | `template <std::same_as<float> T>` |

## よくあるミス

??? failure "const や参照が付いて false"
    `same_as<const int&, int>` は `false` です。必要なら `remove_cvref_t` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](../type_traits/is_same.md) | 変数テンプレート版 |
| [`derived_from`](derived_from.md) | 派生クラスか |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ型であることを要求
    - [x] `is_same_v` のコンセプト版
    - [x] const / 参照も区別

## 関連ページ

- [cpprefjp: std::same_as](https://cpprefjp.github.io/reference/concepts/same_as.html)
- [cppreference: std::same_as](https://en.cppreference.com/w/cpp/concepts/same_as)
