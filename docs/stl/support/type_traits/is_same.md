---
title: std::is_same
summary: "2 つの型が同じかを、コンパイル時に調べる。"
order: 1
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_same

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

`std::is_same_v<A, B>` は、**2 つの型 A と B がまったく同じ型か**をコンパイル時に調べます。`const` や参照の有無も区別します。テンプレートの中で、型ごとに処理を分ける `if constexpr` と組み合わせて使います。

!!! tip "ポイント"
    - `std::is_same_v<int, int>` は `true`、`<int, const int>` は `false`。
    - `const` や参照を無視したいなら、先に `remove_cvref_t` を通す。
    - `if constexpr (std::is_same_v<T, float>)` で、型ごとの処理を書く。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_same_v {#is_same}

```cpp
template <class T, class U>
inline constexpr bool is_same_v = /* T と U が同じなら true */;
```

- 2 つの型が完全に同じか（`int` と `const int` は違う）

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<int, int>, std::is_same_v<int, const int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで float と double の処理を分ける | `if constexpr (std::is_same_v<T, float>)` |

## よくあるミス

??? failure "const や参照が付いて false になる"
    `is_same_v<const int&, int>` は `false` です。`remove_cvref_t` で外してから比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 修飾を外す |
| `std::same_as` | コンセプト版（C++20） |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ型かを調べる
    - [x] const / 参照も区別
    - [x] `if constexpr` と使う

## 関連ページ

- [cpprefjp: std::is_same](https://cpprefjp.github.io/reference/type_traits/is_same.html)
- [cppreference: std::is_same](https://en.cppreference.com/w/cpp/types/is_same)
