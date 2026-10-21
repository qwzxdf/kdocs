---
title: std::derived_from
summary: "別のクラスの派生クラスであることを要求するコンセプト。"
order: 5
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::derived_from

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::derived_from<Derived, Base>` は、**`Derived` が `Base` の（公開）派生クラスであること**を要求するコンセプトです。「`Component` の派生だけ受け取る」という制約を、読みやすく書けます。

!!! tip "ポイント"
    - `is_base_of` と違い、**public 継承**であることが条件。
    - 引数の順番は **派生が先、基底が後**（`is_base_of` と逆）。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::derived_from {#derived_from}

```cpp
template <class T>
concept derived_from = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

struct Component {};
struct Mesh : Component {};

int main() {
  std::println("{} {}", std::derived_from<Mesh, Component>, std::derived_from<Component, Mesh>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Component の派生だけを受け取る AddComponent | `template <std::derived_from<Component> T>` |

## よくあるミス

??? failure "引数の順番を is_base_of と同じにする"
    `is_base_of<Base, Derived>` とは逆順です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_base_of`](../type_traits/is_base_of.md) | 基底が先の変数テンプレート版 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 派生クラスであることを要求
    - [x] 派生が先、基底が後
    - [x] public 継承が条件

## 関連ページ

- [cpprefjp: std::derived_from](https://cpprefjp.github.io/reference/concepts/derived_from.html)
- [cppreference: std::derived_from](https://en.cppreference.com/w/cpp/concepts/derived_from)
