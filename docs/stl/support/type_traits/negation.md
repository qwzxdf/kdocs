---
title: std::negation
summary: "型特性の結果を反転する。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::negation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

`!is_void<T>::value` のように書く代わりに、`negation<is_void<T>>` と書くと、型特性として他の組み合わせ（`conjunction` など）に渡せます。

!!! tip "ポイント"
    - `_v` 版で `bool` の定数が取れる。
    - 型特性を組み合わせる道具（メタ関数）。
    - C++20 では `requires` の `&&` `||` `!` が読みやすい。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::negation {#negation}

```cpp
template <class B>
struct negation;
template <class B>
inline constexpr bool negation_v = negation<B>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B...` | 型特性 | 組み合わせる型特性（`::value` をもつ型） |

- 戻り値: 結果の `bool`（`::value`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::negation_v<std::is_void<int>>);
  std::println("{}", std::negation_v<std::is_void<void>>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの条件を、複数の型特性で組み合わせる |

## よくあるミス

??? failure "`::value` を持たない型を渡す"
    型特性（`::value` を持つ型）を渡します。値の `bool` ではなく型です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conjunction`](conjunction.md) | すべてが真か |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型特性の結果を反転する
    - [x] `_v` 版で `bool` の定数が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::negation](https://cpprefjp.github.io/reference/type_traits/negation.html)
- [cppreference: std::negation](https://en.cppreference.com/w/cpp/types/negation)
