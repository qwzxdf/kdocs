---
title: std::is_integral
summary: "整数型かを調べる。"
order: 2
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_integral

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

整数だけを受け取るテンプレート関数を書きたい。`int`、`unsigned`、`char`、`bool` などはすべて整数型です。`std::is_integral` は、<strong>型が整数型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_integral_v<T>` は、`T` が整数型（`bool`、`char` 系、`int` 系）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_integral<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_integral_v {#is_integral}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_integral_v = is_integral<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`bool`、`char`、`signed char`、`unsigned char`、`wchar_t`、`char8_t`、`char16_t`、`char32_t`、`short`、`int`、`long`、`long long` と、それぞれの符号なし版（`const` や `volatile` 付きを含む）が `true` です。`float` や `double`、ポインタは `false` です。

列挙型は、整数に変換できますが、`is_integral` では `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int                        -> {}", std::is_integral_v<int>);
  std::println("bool                       -> {}", std::is_integral_v<bool>);
  std::println("char                       -> {}", std::is_integral_v<char>);
  std::println("float                      -> {}", std::is_integral_v<float>);
  std::println("int*                       -> {}", std::is_integral_v<int*>);
}
```

```text title="実行結果"
int                        -> true
bool                       -> true
char                       -> true
float                      -> false
int*                       -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_integral_v<T>) {
    // T が条件に当てはまる型のときの処理
  } else {
    // それ以外の型の処理
  }
}
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_integral_v<T>` は、`T` が整数型（`bool`、`char` 系、`int` 系）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_integral](https://cpprefjp.github.io/reference/type_traits/is_integral.html)
- [cppreference: std::is_integral](https://en.cppreference.com/w/cpp/types/is_integral)
