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

`std::is_floating_point_v<T>` は、**型 T が小数型（`float`、`double`、`long double`）か**を調べます。テンプレートで、整数と小数の処理を切り替えるときに使います。

!!! tip "ポイント"
    - `half` などの拡張型は含まれない（`std::float16_t` は C++23 で含まれる）。
    - コンセプト版は `std::floating_point`。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_floating_point_v {#is_floating_point}

```cpp
template <class T>
inline constexpr bool is_floating_point_v;
```

- float、double、long double なら true

```cpp
#include <print>
#include <string>
#include <type_traits>

template <class T>
std::string Describe(T value) {
  if constexpr (std::is_integral_v<T>) {
    return "整数 " + std::to_string(value);
  } else if constexpr (std::is_floating_point_v<T>) {
    return "小数 " + std::to_string(value);
  } else {
    return "その他";
  }
}

int main() {
  std::println("{} / {} / {}", Describe(3), Describe(1.5f), Describe("x"));
  std::println("{} {}", std::is_same_v<int, int>, std::is_same_v<int, const int>);
}
```

```text title="実行結果"
整数 3 / 小数 1.500000 / その他
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小数だけを受け取る数学関数のテンプレート | `static_assert(std::is_floating_point_v<T>)` |

## よくあるミス

??? failure "整数に小数の関数を使う"
    `std::sqrt(int)` は double に変換されます。意図に合わせて型を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_integral`](is_integral.md) | 整数型 |
| [`is_arithmetic`](is_arithmetic.md) | 整数または小数 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数型かを調べる
    - [x] float / double / long double
    - [x] コンセプト版もある

## 関連ページ

- [cpprefjp: std::is_floating_point](https://cpprefjp.github.io/reference/type_traits/is_floating_point.html)
- [cppreference: std::is_floating_point](https://en.cppreference.com/w/cpp/types/is_floating_point)
