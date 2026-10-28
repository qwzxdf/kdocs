---
title: std::is_pointer_interconvertible_base_of
summary: "基底クラスのポインタと派生クラスのポインタを、相互に変換できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pointer_interconvertible_base_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

派生クラスのオブジェクトの先頭が基底クラスと一致し、ポインタを `reinterpret_cast` で行き来しても安全かを判定します。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_pointer_interconvertible_base_of {#is_pointer_interconvertible_base_of}

```cpp
template <class Base, class Derived>
struct is_pointer_interconvertible_base_of;
template <class Base, class Derived>
inline constexpr bool is_pointer_interconvertible_base_of_v = is_pointer_interconvertible_base_of<Base, Derived>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Base` | 型 | 調べる型 |
| `Derived` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("{}", std::is_pointer_interconvertible_base_of_v<Base, Derived>);
  std::println("{}", std::is_pointer_interconvertible_base_of_v<Derived, Base>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "値と型を取り違える"
    `is_pointer_interconvertible_base_of` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基底クラスのポインタと派生クラスのポインタを相互に変換できるかを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_pointer_interconvertible_base_of](https://cpprefjp.github.io/reference/type_traits/is_pointer_interconvertible_base_of.html)
- [cppreference: std::is_pointer_interconvertible_base_of](https://en.cppreference.com/w/cpp/types/is_pointer_interconvertible_base_of)
