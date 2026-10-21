---
title: std::conditional
summary: "条件によって、2 つの型のどちらかを選ぶ。"
order: 17
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::conditional

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::conditional_t<B, T, F>` は、**条件 B が `true` なら型 T、`false` なら型 F を選ぶ**型です。テンプレートの中で、型を条件で切り替えるときに使います。

!!! tip "ポイント"
    - `conditional_t<(sizeof(T) > 4), double, float>` のように、条件を型に反映する。
    - 実行時の条件ではなく、**コンパイル時の定数**で決まる。
    - `if constexpr` で足りることも多い。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::conditional_t {#conditional}

```cpp
template <bool B, class T, class F>
using conditional_t = /* B ? T : F */;
```

- コンパイル時の条件で型を選びます

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::conditional_t<true, int, double>, int>, std::is_same_v<std::conditional_t<false, int, double>, double>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大きさによって保存用の型を切り替える | `std::conditional_t<(N > 255), std::uint16_t, std::uint8_t>` |

## よくあるミス

??? failure "実行時の値を条件にする"
    コンパイル時の定数だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 条件に使う |
| `if constexpr` | 処理を切り替える |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件で型を選ぶ
    - [x] 条件はコンパイル時の定数
    - [x] 処理の切り替えは if constexpr

## 関連ページ

- [cpprefjp: std::conditional](https://cpprefjp.github.io/reference/type_traits/conditional.html)
- [cppreference: std::conditional](https://en.cppreference.com/w/cpp/types/conditional)
