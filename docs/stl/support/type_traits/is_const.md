---
title: std::is_const
summary: "`const` が付いた型かを調べる。"
order: 9
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_const_v<T>` は、**型 T に最上位の `const` が付いているか**を調べます。参照やポインターの指す先の `const` は見ません。

!!! tip "ポイント"
    - `const int` は `true`、`const int&` は `false`（参照自体は const にならない）。
    - `const int*` は `false`（指す先が const なだけ）。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_const_v {#is_const}

- `const` が付いていれば true（`const int&` は参照なので false。`std::remove_reference_t` してから調べる）

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {} {}", std::is_const_v<const int>, std::is_const_v<int>, std::is_const_v<const int&>);
}
```

```text title="実行結果"
true false false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、const のときだけ別の処理 | `std::is_const_v<T>` |

## よくあるミス

??? failure "参照型で調べて false"
    `remove_reference_t` を先に通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 修飾を外す |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最上位の const か
    - [x] 参照・ポインター先は見ない
    - [x] `const int*` は false

## 関連ページ

- [cpprefjp: std::is_const](https://cpprefjp.github.io/reference/type_traits/is_const.html)
- [cppreference: std::is_const](https://en.cppreference.com/w/cpp/types/is_const)
