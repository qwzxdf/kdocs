---
title: std::common_type
summary: "複数の型に共通する型（どちらにも変換できる型）を調べる。"
order: 18
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::common_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::common_type_t<A, B>` は、**型 A と B の両方を無理なく表せる共通の型**を返します。`int` と `double` なら `double` です。`std::min` / `max` の引数の型や、`std::chrono::duration` の足し算の結果の型を決めるのに使われています。

!!! tip "ポイント"
    - 算術演算の結果の型と同じ（`int + double` は `double`）。
    - `std::chrono` の単位の合成にも使われる。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::common_type_t {#common_type}

- 両方の型を表せる型（`int` と `double` なら `double`）

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::common_type_t<int, double>, double>, std::is_same_v<std::common_type_t<int, long>, long>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの値を足すテンプレートの戻り値型 | `std::common_type_t<A, B>` |

## よくあるミス

??? failure "符号の違う整数の組み合わせ"
    `int` と `unsigned` は `unsigned` になり、負の値が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cmp_less`](../cmp_less.md) | 符号の混ざった比較を安全にする |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 共通の型を調べる
    - [x] int と double は double
    - [x] chrono の単位合成に使われる

## 関連ページ

- [cpprefjp: std::common_type](https://cpprefjp.github.io/reference/type_traits/common_type.html)
- [cppreference: std::common_type](https://en.cppreference.com/w/cpp/types/common_type)
