---
title: std::is_enum
summary: "列挙型（enum）かを調べる。"
order: 6
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_enum_v<T>` は、**型 T が列挙型（`enum` / `enum class`）か**を調べます。`std::to_underlying` を使えるかの確認や、列挙型だけを受け取るテンプレートで使います。

!!! tip "ポイント"
    - `enum class` も `true`。
    - 元の整数型は `underlying_type_t` で取れる。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_enum_v {#is_enum}

```cpp
template <class T>
inline constexpr bool is_enum_v;
```

- enum（enum class 含む）なら true

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class Color { kRed };

int main() {
  std::println("{} {}", std::is_enum_v<Color>, std::is_enum_v<int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| enum 型だけを受け取る関数 | `static_assert(std::is_enum_v<E>)` |

## よくあるミス

??? failure "整数と取り違える"
    `enum` は `is_integral` ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`underlying_type`](underlying_type.md) | 元の整数型 |
| [`std::to_underlying`](../to_underlying.md) | 整数に変換 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 列挙型かを調べる
    - [x] enum class も true
    - [x] 整数型ではない

## 関連ページ

- [cpprefjp: std::is_enum](https://cpprefjp.github.io/reference/type_traits/is_enum.html)
- [cppreference: std::is_enum](https://en.cppreference.com/w/cpp/types/is_enum)
