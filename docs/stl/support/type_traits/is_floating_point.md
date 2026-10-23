---
title: std::is_floating_point
summary: "小数型（float・double・long double）かを調べる。"
order: 3
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_floating_point

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

数値を受け取るテンプレートで、整数と小数で処理を分けたい。`std::is_floating_point` は、<strong>型が浮動小数点型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_floating_point_v<T>` は、`T` が浮動小数点型（`float`、`double`、`long double`）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_floating_point<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_floating_point_v {#is_floating_point}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_floating_point_v = is_floating_point<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`float`、`double`、`long double`（`const` や `volatile` 付きを含む）が `true` です。C++23 の拡張浮動小数点型（`std::float32_t` など）も、`true` になります。整数型は `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("float                      -> {}", std::is_floating_point_v<float>);
  std::println("double                     -> {}", std::is_floating_point_v<double>);
  std::println("int                        -> {}", std::is_floating_point_v<int>);
  std::println("float*                     -> {}", std::is_floating_point_v<float*>);
}
```

```text title="実行結果"
float                      -> true
double                     -> true
int                        -> false
float*                     -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_floating_point_v<T>) {
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
    - [x] `std::is_floating_point_v<T>` は、`T` が浮動小数点型（`float`、`double`、`long double`）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_floating_point](https://cpprefjp.github.io/reference/type_traits/is_floating_point.html)
- [cppreference: std::is_floating_point](https://en.cppreference.com/w/cpp/types/is_floating_point)
