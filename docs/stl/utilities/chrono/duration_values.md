---
title: std::chrono::duration_values
summary: "duration の rep について、0・最小・最大を返す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::duration_values

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`duration<int>::max()` は、内部で整数の最大値を返します。この「0、最小値、最大値」を取り出す仕組みが `std::chrono::duration_values` です。標準の整数や浮動小数点数なら自動で決まるので、触る必要はありません。自作の数値型を `duration` の内部の型として使うときに、特殊化して、これらの値を教える役目です。

!!! tip "ポイント"
    - `zero()`、`min()`、`max()` の 3 つの静的関数を持つ
    - 標準の算術型では、`numeric_limits` から値が決まる。何もしなくてよい
    - `duration::zero()`、`duration::max()`、`duration::min()` が、これを使っている
    - 自作の数値型を `duration` の `Rep` に使うときだけ、特殊化する

!!! info "このページを読む前に"
    [`duration`](duration.md) と [`treat_as_floating_point`](treat_as_floating_point.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::duration_values {#duration_values}

```cpp
template <class Rep>
struct duration_values {
  static constexpr Rep zero() noexcept;
  static constexpr Rep min() noexcept;
  static constexpr Rep max() noexcept;
};
```

`zero()` は `Rep(0)`、`max()` は `numeric_limits<Rep>::max()` を返します。`min()` は `numeric_limits<Rep>::lowest()` を返します。整数なら最小値ですが、浮動小数点数では、`min()`（最小の正の値）ではなく、`lowest()`（最も小さい負の値）です。

`std::chrono::duration<Rep>::zero()` などの、`duration` 自身の静的関数が、この `duration_values<Rep>` を呼んでいます。

自作の数値型（固定小数点数、多倍長整数など）を `duration` に使うなら、`std::chrono::duration_values<MyNumber>` を特殊化して、3 つの関数を定義します。そうしないと、`duration<MyNumber>::max()` などがコンパイルできません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <limits>
#include <print>

int main() {
  using namespace std::chrono;

  using IntValues = duration_values<int>;
  std::println("zero: {}", IntValues::zero());
  std::println("max は INT_MAX: {}", IntValues::max() == std::numeric_limits<int>::max());
  std::println("min は INT_MIN: {}", IntValues::min() == std::numeric_limits<int>::min());

  // duration の静的関数は、これを使っている
  std::println("seconds::max() は rep の最大値: {}",
               seconds::max().count() == duration_values<seconds::rep>::max());
}
```

```text title="実行結果"
zero: 0
max は INT_MAX: true
min は INT_MIN: true
seconds::max() は rep の最大値: true
```

## ゲームでの使いどころ

自作の固定小数点数型で時間を表したい、という特殊な場合以外は、触りません。「無期限」を `duration::max()` で表すときに、裏で使われていることを知っておくくらいです。

## よくあるミス

??? failure "浮動小数点数の min() を、最小の負の値だと思う"
    `numeric_limits<double>::min()` は最小の正の値ですが、`duration_values<double>::min()` は `lowest()` で、最も小さい負の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | これを使って `zero()` などを提供する |
| [`treat_as_floating_point`](treat_as_floating_point.md) | もう 1 つの、`Rep` ごとの特性 |
| `std::numeric_limits` | 標準の型の最小・最大 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: duration_values](https://cpprefjp.github.io/reference/chrono/duration_values.html)
- [cppreference: std::chrono::duration_values](https://en.cppreference.com/w/cpp/chrono/duration_values)
