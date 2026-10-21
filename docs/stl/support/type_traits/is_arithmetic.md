---
title: std::is_arithmetic
summary: "算術型（整数または小数）かを調べる。"
order: 4
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_arithmetic

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::is_arithmetic_v<T>` は、**型 T が数として計算できる基本型（整数または小数）か**を調べます。数値だけを受け取るテンプレートの制約に使います。

!!! tip "ポイント"
    - `is_integral || is_floating_point` と同じ。
    - `enum` やポインターは含まれない。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_arithmetic_v {#is_arithmetic}

- 整数か浮動小数点なら true（数値として計算できる型）

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("{} {} {}", std::is_arithmetic_v<int>, std::is_arithmetic_v<double>, std::is_arithmetic_v<std::string>);
}
```

```text title="実行結果"
true true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 数値型だけを受け取る関数テンプレート | `static_assert(std::is_arithmetic_v<T>)` |

## よくあるミス

??? failure "ベクトル型を数値とみなす"
    `Vector3` は算術型ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_integral`](is_integral.md) | 整数 |
| [`is_floating_point`](is_floating_point.md) | 小数 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数または小数
    - [x] `enum` やポインターは含まれない
    - [x] コンセプトは `std::integral` / `floating_point`

## 関連ページ

- [cpprefjp: std::is_arithmetic](https://cpprefjp.github.io/reference/type_traits/is_arithmetic.html)
- [cppreference: std::is_arithmetic](https://en.cppreference.com/w/cpp/types/is_arithmetic)
