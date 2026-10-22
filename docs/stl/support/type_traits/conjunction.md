---
title: std::conjunction
summary: "複数の条件がすべて真かを調べる（短絡評価）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::conjunction

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

`is_integral<T> && is_signed<T>` のような条件を、型特性のまま組み合わせます。先に偽になった時点で、残りの型を調べずに止まります。

!!! tip "ポイント"
    - `_v` 版で `bool` の定数が取れる。
    - 型特性を組み合わせる道具（メタ関数）。
    - C++20 では `requires` の `&&` `||` `!` が読みやすい。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::conjunction {#conjunction}

```cpp
template <class... B>
struct conjunction;
template <class... B>
inline constexpr bool conjunction_v = conjunction<B...>::value;
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
  std::println("{}", std::conjunction_v<std::is_integral<int>, std::is_signed<int>>);
  std::println("{}", std::conjunction_v<std::is_integral<int>, std::is_unsigned<int>>);
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
| [`disjunction`](disjunction.md) | どれかが真か |
| [`negation`](negation.md) | 否定 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の条件がすべて真かを調べる（短絡評価）
    - [x] `_v` 版で `bool` の定数が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::conjunction](https://cpprefjp.github.io/reference/type_traits/conjunction.html)
- [cppreference: std::conjunction](https://en.cppreference.com/w/cpp/types/conjunction)
