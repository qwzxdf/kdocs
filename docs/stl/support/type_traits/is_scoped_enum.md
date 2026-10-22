---
title: std::is_scoped_enum
summary: "型がスコープ付き列挙型（`enum class`）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_scoped_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <type_traits>`
</div>

`enum class` で宣言した型かを判定します。暗黙に整数へ変換されない列挙型です。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_scoped_enum {#is_scoped_enum}

```cpp
template <class T>
struct is_scoped_enum;
template <class T>
inline constexpr bool is_scoped_enum_v = is_scoped_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class E {};
enum Old {};

int main() {
  std::println("{}", std::is_scoped_enum_v<E>);
  std::println("{}", std::is_scoped_enum_v<Old>);
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
    `is_scoped_enum` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型がスコープ付き列挙型（`enum class`）かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_scoped_enum](https://cpprefjp.github.io/reference/type_traits/is_scoped_enum.html)
- [cppreference: std::is_scoped_enum](https://en.cppreference.com/w/cpp/types/is_scoped_enum)
