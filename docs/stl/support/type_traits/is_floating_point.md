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

テンプレートの数値計算で、整数と小数の処理を分けたいとき、型をコンパイラーに聞くのが `std::is_floating_point_v<T>` です。型 `T` が小数型（`float`、`double`、`long double`）なら `true` を返します。`if constexpr` と組み合わせて、小数のときだけ誤差を考えた比較にする、などの分岐に使います。

!!! tip "ポイント"
    - `half` などの拡張型は含まれない（`std::float16_t` は C++23 で含まれる）。
    - コンセプト版は `std::floating_point`。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

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

## しくみ

`is_floating_point_v<T>` は、`T` が `float`、`double`、`long double` のどれか（`const` や `volatile` は無視）なら `true` です。C++23 の `std::float16_t`、`std::float32_t` なども、含まれます。

整数型は `false`、参照とポインターも `false` です。テンプレートが参照で型を受けているなら、`remove_cvref_t` を通してから調べます。

C++20 のコンセプト `std::floating_point` は、同じ判定を `template <std::floating_point T>` と書ける形にしたものです。

## ゲームでの使いどころ

数値の比較関数で、整数と小数を分けるのが代表例です。小数なら `std::abs(a - b) < epsilon`、整数なら `a == b` と書き分けます。

```cpp
template <class T>
bool NearlyEqual(T a, T b) {
  if constexpr (std::is_floating_point_v<T>) {
    return std::abs(a - b) < static_cast<T>(1e-5);
  } else {
    return a == b;
  }
}
```

ベクトルや行列のテンプレートで、要素の型が小数であることを制約するときにも使います。`static_assert(std::is_floating_point_v<T>)` と書いておけば、整数の行列を作ったときに、早めに気づけます。

## よくあるミス

??? failure "整数を小数として扱うつもりで `true` を期待する"
    `is_floating_point_v<int>` は `false` です。整数と小数をまとめて「数値」とするなら `std::is_arithmetic_v` を使います。

??? failure "参照型で `false` になる"
    `is_floating_point_v<float&>` は `false` です。`std::remove_cvref_t<T>` を通してから調べます。

??? failure "`half` などの拡張型を期待する"
    GPU 向けの `half` のような独自の型は、`is_floating_point_v` が `false` です。標準の拡張型（`std::float16_t`）は、C++23 で含まれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::is_integral`](is_integral.md) | 整数型かを調べる |
| `std::is_arithmetic` | 整数または小数のどちらかか |
| `std::floating_point` | コンセプト版。関数の制約に使う |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `is_floating_point_v<T>` で小数型かを調べる。
    - [x] 参照型には `remove_cvref_t` を通してから使う。
    - [x] C++20 では `std::floating_point` コンセプトでも書ける。

## 関連ページ

- [cpprefjp: std::is_floating_point](https://cpprefjp.github.io/reference/type_traits/is_floating_point.html)
- [cppreference: std::is_floating_point](https://en.cppreference.com/w/cpp/types/is_floating_point)
